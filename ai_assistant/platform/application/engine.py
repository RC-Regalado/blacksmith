"""Bounded autonomous execution engine."""

from dataclasses import dataclass
from datetime import UTC, datetime
import logging
from pathlib import PurePosixPath

from ai_assistant.application.tool_coordinator import ToolExecutionCoordinator
from ai_assistant.domain.tools import (
    ToolExecutionRequest,
    ToolExecutionResult,
    ToolExecutionStatus,
    ToolPermission,
)
from ai_assistant.platform.application.budget import BudgetExceededError, BudgetManager
from ai_assistant.platform.application.checkpoint import CheckpointService
from ai_assistant.platform.application.execution_graph import ExecutionGraph
from ai_assistant.platform.application.plan_validator import PlanValidator
from ai_assistant.platform.application.scheduler import TaskScheduler
from ai_assistant.platform.domain.budget import BudgetUsage, ExecutionBudget
from ai_assistant.platform.domain.evaluation import EvaluationResult
from ai_assistant.platform.domain.execution import (
    ExecutionRecord,
    ExecutionResult,
    ExecutionStatus,
)
from ai_assistant.platform.domain.objective import Objective
from ai_assistant.platform.domain.plan import Plan
from ai_assistant.platform.domain.task import CapabilityName, PlatformTaskStatus
from ai_assistant.platform.ports.capability_registry import CapabilityRegistry
from ai_assistant.platform.ports.evaluator import Evaluator
from ai_assistant.platform.ports.execution_store import ExecutionStore
from ai_assistant.platform.ports.planner import Planner


logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ExecutionOutcome:
    objective: Objective
    plan: Plan
    execution: ExecutionRecord
    result: ExecutionResult
    evaluation: EvaluationResult
    usage: BudgetUsage


class ExecutionEngine:
    def __init__(
        self,
        planner: Planner,
        validator: PlanValidator,
        registry: CapabilityRegistry,
        scheduler: TaskScheduler,
        budget_manager: BudgetManager,
        store: ExecutionStore,
        checkpoints: CheckpointService,
        evaluator: Evaluator,
        tools: ToolExecutionCoordinator,
    ) -> None:
        self._planner = planner
        self._validator = validator
        self._registry = registry
        self._scheduler = scheduler
        self._budget_manager = budget_manager
        self._store = store
        self._checkpoints = checkpoints
        self._evaluator = evaluator
        self._tools = tools

    @property
    def last_planner_response(self) -> str | None:
        value = getattr(self._planner, "last_response_content", None)
        return value if isinstance(value, str) else None

    def run(
        self,
        objective: Objective,
        session_id: str,
        budget: ExecutionBudget | None = None,
    ) -> ExecutionOutcome:
        budget = budget or ExecutionBudget()
        usage = self._budget_manager.record_model_call(budget, BudgetUsage())
        _log_budget("model_call", usage)
        logger.info("objective accepted objective_id=%s", objective.objective_id)
        self._store.save_objective(objective)
        plan = self._validator.validate(self._planner.create_plan(objective), budget)
        _log_plan(objective, plan)
        self._store.save_plan(plan)
        execution = ExecutionRecord(f"exec-{objective.objective_id}", objective.objective_id, plan.plan_id)
        execution = execution.transition(ExecutionStatus.RUNNING)
        _log_execution(execution)
        self._store.save_execution(execution)
        try:
            result, usage = self._run_tasks(plan, execution.execution_id, session_id, budget, usage)
        except BudgetExceededError as error:
            result = ExecutionResult(
                execution.execution_id,
                ExecutionStatus.BUDGET_EXCEEDED,
                (),
                error.code.value,
            )
        execution = execution.transition(result.status)
        _log_execution(execution)
        self._store.save_execution(execution)
        evaluation = self._evaluator.evaluate(objective, result, _task_states(self._store, plan))
        _log_final(objective, execution, result, evaluation)
        return ExecutionOutcome(objective, plan, execution, result, evaluation, usage)

    def _run_tasks(
        self,
        plan: Plan,
        execution_id: str,
        session_id: str,
        budget: ExecutionBudget,
        usage: BudgetUsage,
    ) -> tuple[ExecutionResult, BudgetUsage]:
        graph = ExecutionGraph.from_plan(plan)
        evidence: list[str] = []
        observations: list[str] = []
        while task := self._scheduler.start_next(plan.plan_id, graph):
            usage = self._budget_manager.record_task(budget, usage)
            _log_budget("task", usage)
            usage = self._budget_manager.record_tool_call(budget, usage)
            _log_budget("tool_call", usage)
            logger.info(
                "task executing execution_id=%s task_id=%s capability=%s",
                execution_id,
                task.task_id,
                task.capability.value,
            )
            result = self._execute_tool(execution_id, session_id, task)
            usage = self._budget_manager.record_output(budget, usage, _output_bytes(result))
            _log_budget("output", usage)
            if result.status != ToolExecutionStatus.SUCCESS:
                self._scheduler.mark_failed(plan.plan_id, task.task_id)
                _block_failed_dependents(self._store, plan, graph)
                logger.info(
                    "task failed execution_id=%s task_id=%s status=%s",
                    execution_id,
                    task.task_id,
                    result.status.value,
                )
                return _result(execution_id, ExecutionStatus.FAILED, evidence, result), usage
            self._scheduler.mark_succeeded(plan.plan_id, task.task_id)
            logger.info("task succeeded execution_id=%s task_id=%s", execution_id, task.task_id)
            evidence.append(f"{task.task_id}:{result.tool_name}:{result.status.value}")
            observations.extend(_observations(task, result))
            self._checkpoints.checkpoint_task(
                execution_id,
                task.task_id,
                PlatformTaskStatus.SUCCEEDED,
                {"task_id": task.task_id, "tool_name": result.tool_name},
            )
        status = _final_status(self._store, plan)
        return ExecutionResult(execution_id, status, tuple(evidence), observations=tuple(observations)), usage

    def _execute_tool(
        self,
        execution_id: str,
        session_id: str,
        task,
    ) -> ToolExecutionResult:
        tool_name = self._registry.tool_name_for(task.capability)
        request = ToolExecutionRequest(
            request_id=f"{execution_id}:{task.task_id}",
            session_id=session_id,
            tool_name=tool_name,
            arguments=task.arguments,
            permission=_permission(task.capability),
        )
        return self._tools.execute(request)


def _permission(capability: CapabilityName) -> ToolPermission:
    if capability in {CapabilityName.RUN_TESTS, CapabilityName.BUILD_PROJECT}:
        return ToolPermission.EXECUTE_PROJECT
    if capability in {CapabilityName.INSPECT_GIT_STATUS, CapabilityName.INSPECT_GIT_DIFF}:
        return ToolPermission.READ_REPOSITORY
    if capability == CapabilityName.INSPECT_FILE_METADATA:
        return ToolPermission.READ_METADATA
    if capability == CapabilityName.SEARCH_TEXT:
        return ToolPermission.READ_CONTENT
    return ToolPermission.READ_ONLY


def _task_states(store: ExecutionStore, plan: Plan) -> dict[str, PlatformTaskStatus]:
    return {
        task.task_id: store.load_task_status(plan.plan_id, task.task_id) or task.status
        for task in plan.tasks
    }


def _final_status(store: ExecutionStore, plan: Plan) -> ExecutionStatus:
    states = set(_task_states(store, plan).values())
    if states <= {PlatformTaskStatus.SUCCEEDED}:
        return ExecutionStatus.COMPLETED
    return ExecutionStatus.FAILED


def _block_failed_dependents(
    store: ExecutionStore,
    plan: Plan,
    graph: ExecutionGraph,
) -> None:
    for task in graph.blocked_tasks(_task_states(store, plan)):
        store.update_task_status(plan.plan_id, task.task_id, PlatformTaskStatus.BLOCKED)


def _result(
    execution_id: str,
    status: ExecutionStatus,
    evidence: list[str],
    tool_result: ToolExecutionResult,
) -> ExecutionResult:
    error_code = tool_result.error.code if tool_result.error else tool_result.status.value
    return ExecutionResult(execution_id, status, tuple(evidence), error_code)


def _output_bytes(result: ToolExecutionResult) -> int:
    return len(str(result.content or result.error or "").encode("utf-8"))


def _observations(task, result: ToolExecutionResult) -> tuple[str, ...]:
    content = result.content or {}
    if result.tool_name == "read_file":
        return _read_file_observations(content)
    if result.tool_name == "list_directory":
        entries = content.get("entries", ())
        return (f"Listed {content.get('path', '.')} ({len(entries)} entries).",)
    if result.tool_name in {"run_tests", "build_project"}:
        return (f"{result.tool_name} exited with code {content.get('exit_code')}.",)
    return (f"{task.task_id} completed {result.tool_name}.",)


def _read_file_observations(content: object) -> tuple[str, ...]:
    if not isinstance(content, dict):
        return ()
    path = str(content.get("path", "file"))
    notes = [f"Read {path} ({content.get('bytes_read', 0)} bytes)."]
    filename = PurePosixPath(path).name
    if filename == "Makefile":
        notes.extend(_makefile_notes(path, str(content.get("content", ""))))
    if filename == "CMakeLists.txt":
        notes.extend(_cmake_notes(path, str(content.get("content", ""))))
    return tuple(notes)


def _makefile_notes(path: str, content: str) -> tuple[str, ...]:
    directory = PurePosixPath(path).parent.as_posix()
    command = "make" if directory == "." else f"make -C {directory}"
    notes = [f"Build with `{command}` from the workspace root."]
    if "clean:" in content:
        notes.append(f"Clean with `{command} clean`.")
    if "check-deps" in content:
        notes.append("The Makefile validates required build dependencies before building.")
    return tuple(notes)


def _cmake_notes(path: str, content: str) -> tuple[str, ...]:
    directory = PurePosixPath(path).parent.as_posix()
    build_dir = "." if directory == "." else f"{directory}/build"
    notes = [
        f"Configure with `cmake -S {directory} -B {build_dir}`.",
        f"Build with `cmake --build {build_dir}`.",
    ]
    if "find_package" in content or "find_program" in content:
        notes.append("The CMake project validates required build dependencies.")
    return tuple(notes)


def _log_plan(objective: Objective, plan: Plan) -> None:
    logger.info(
        "plan validated objective_id=%s plan_id=%s task_count=%s",
        objective.objective_id,
        plan.plan_id,
        len(plan.tasks),
    )


def _log_execution(execution: ExecutionRecord) -> None:
    logger.info(
        "execution transition execution_id=%s status=%s",
        execution.execution_id,
        execution.status.value,
    )


def _log_budget(event: str, usage: BudgetUsage) -> None:
    logger.info(
        "budget usage event=%s tasks=%s model_calls=%s tool_calls=%s output_bytes=%s",
        event,
        usage.tasks,
        usage.model_calls,
        usage.tool_calls,
        usage.output_bytes,
    )


def _log_final(
    objective: Objective,
    execution: ExecutionRecord,
    result: ExecutionResult,
    evaluation: EvaluationResult,
) -> None:
    logger.info(
        "execution finished objective_id=%s execution_id=%s status=%s evaluation=%s",
        objective.objective_id,
        execution.execution_id,
        result.status.value,
        evaluation.status.value,
    )
