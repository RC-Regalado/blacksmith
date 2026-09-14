"""Tests for Phase 4 execution engine."""

from ai_assistant.application.tool_coordinator import ToolExecutionCoordinator
from ai_assistant.domain.tools import (
    SanitizedToolError,
    ToolCallLogEvent,
    ToolExecutionRequest,
    ToolExecutionResult,
    ToolExecutionStatus,
    ToolPermission,
)
from ai_assistant.platform.application import (
    BudgetManager,
    CheckpointService,
    DeterministicPlanner,
    ExecutionEngine,
    ObjectiveEvaluator,
    PlanValidator,
    StaticCapabilityRegistry,
    TaskScheduler,
)
from ai_assistant.platform.domain import (
    CapabilityName,
    ExecutionBudget,
    ExecutionStatus,
    EvaluationStatus,
    Objective,
    Plan,
    PlatformTask,
    PlatformTaskStatus,
)
from ai_assistant.platform.ports.capability_registry import CapabilityDefinition


def test_execution_engine_runs_read_only_plan_through_tool_coordinator() -> None:
    objective = Objective("obj-1", "Inspect", success_criteria=("task-1:list_directory:success",))
    plan = Plan(
        "plan-1",
        "obj-1",
        (_task("task-1", CapabilityName.INSPECT_DIRECTORY, {"path": "."}),),
    )
    store = _Store()
    tools = _Coordinator(ToolExecutionStatus.SUCCESS)
    engine = _engine(plan, store, tools)

    outcome = engine.run(objective, "session-1", ExecutionBudget())

    assert outcome.result.status == ExecutionStatus.COMPLETED
    assert outcome.evaluation.status == EvaluationStatus.PASSED
    assert tools.requests[0].tool_name == "list_directory"
    assert tools.requests[0].permission == ToolPermission.READ_ONLY
    assert store.checkpoints == [("exec-obj-1", "task-1")]


def test_execution_engine_logs_capability_tool_diagnostics() -> None:
    objective = Objective("obj-1", "Inspect")
    plan = Plan(
        "plan-1",
        "obj-1",
        (_task("task-1", CapabilityName.INSPECT_DIRECTORY, {"path": "."}),),
    )
    diagnostics = _Diagnostics()

    _engine(plan, _Store(), _Coordinator(ToolExecutionStatus.SUCCESS), diagnostics).run(
        objective,
        "session-1",
        ExecutionBudget(),
    )

    assert [event.status.value for event in diagnostics.events] == ["requested", "executed"]
    assert diagnostics.events[0].capability_name == "InspectDirectory"
    assert diagnostics.events[1].tool_name == "list_directory"


def test_execution_engine_summarizes_makefile_usage() -> None:
    objective = Objective("obj-1", "Determine how to use Makefile")
    plan = Plan(
        "plan-1",
        "obj-1",
        (_task("task-1", CapabilityName.READ_FILE, {"path": "native_tools/Makefile"}),),
    )
    content = {
        "path": "native_tools/Makefile",
        "content": "all: check-deps $(TARGET)\nclean:\n\trm -rf build\nprotoc-gen-c\n",
        "bytes_read": 64,
    }

    outcome = _engine(plan, _Store(), _Coordinator(ToolExecutionStatus.SUCCESS, content)).run(
        objective,
        "session-1",
        ExecutionBudget(),
    )

    assert "Build with `make -C native_tools` from the workspace root." in outcome.result.observations
    assert "Clean with `make -C native_tools clean`." in outcome.result.observations
    assert (
        "The Makefile validates required build dependencies before building."
        in outcome.result.observations
    )


def test_execution_engine_summarizes_cmake_usage() -> None:
    objective = Objective("obj-1", "Determine how to use CMake")
    plan = Plan(
        "plan-1",
        "obj-1",
        (_task("task-1", CapabilityName.READ_FILE, {"path": "native_tools/CMakeLists.txt"}),),
    )
    content = {
        "path": "native_tools/CMakeLists.txt",
        "content": "project(native_tools C)\nfind_package(PkgConfig REQUIRED)\nfind_program(CC cc)\n",
        "bytes_read": 76,
    }

    outcome = _engine(plan, _Store(), _Coordinator(ToolExecutionStatus.SUCCESS, content)).run(
        objective,
        "session-1",
        ExecutionBudget(),
    )

    assert "Configure with `cmake -S native_tools -B native_tools/build`." in outcome.result.observations
    assert "Build with `cmake --build native_tools/build`." in outcome.result.observations
    assert "The CMake project validates required build dependencies." in outcome.result.observations


def test_execution_engine_fails_without_retry_on_tool_error() -> None:
    objective = Objective("obj-1", "Inspect", success_criteria=("never",))
    plan = Plan(
        "plan-1",
        "obj-1",
        (_task("task-1", CapabilityName.READ_FILE, {"path": "README.md"}),),
    )
    tools = _Coordinator(ToolExecutionStatus.ERROR)

    outcome = _engine(plan, _Store(), tools).run(objective, "session-1", ExecutionBudget())

    assert outcome.result.status == ExecutionStatus.FAILED
    assert outcome.execution.status == ExecutionStatus.FAILED
    assert outcome.result.error_code == "tool_error"
    assert len(tools.requests) == 1


def test_execution_engine_blocks_dependents_after_failed_dependency() -> None:
    objective = Objective("obj-1", "Inspect", success_criteria=("never",))
    plan = Plan(
        "plan-1",
        "obj-1",
        (
            _task("task-1", CapabilityName.READ_FILE, {"path": "missing.md"}),
            _task("task-2", CapabilityName.READ_FILE, {"path": "README.md"}, ("task-1",)),
        ),
    )
    store = _Store()

    outcome = _engine(plan, store, _Coordinator(ToolExecutionStatus.ERROR)).run(
        objective,
        "session-1",
        ExecutionBudget(),
    )

    assert outcome.result.status == ExecutionStatus.FAILED
    assert store.task_statuses[("plan-1", "task-1")] == PlatformTaskStatus.FAILED
    assert store.task_statuses[("plan-1", "task-2")] == PlatformTaskStatus.BLOCKED


def test_execution_engine_stops_before_excessive_tool_call() -> None:
    objective = Objective("obj-1", "Inspect", success_criteria=("never",))
    plan = Plan(
        "plan-1",
        "obj-1",
        (_task("task-1", CapabilityName.READ_FILE, {"path": "README.md"}),),
    )
    tools = _Coordinator(ToolExecutionStatus.SUCCESS)

    outcome = _engine(plan, _Store(), tools).run(
        objective,
        "session-1",
        ExecutionBudget(max_tool_calls=0),
    )

    assert outcome.result.status == ExecutionStatus.BUDGET_EXCEEDED
    assert outcome.result.error_code == "tool_call_limit_exceeded"
    assert tools.requests == []


def test_execution_engine_does_not_expose_write_permission() -> None:
    plan = Plan(
        "plan-1",
        "obj-1",
        (_task("task-1", CapabilityName.BUILD_PROJECT, {"path": ".", "profile_id": "default"}),),
    )
    tools = _Coordinator(ToolExecutionStatus.SUCCESS)

    _engine(plan, _Store(), tools).run(Objective("obj-1", "Build"), "session-1")

    assert {request.permission for request in tools.requests} == {ToolPermission.EXECUTE_PROJECT}
    assert ToolPermission.WRITE_WORKSPACE not in {request.permission for request in tools.requests}


def test_execution_engine_logs_metadata_without_content(caplog) -> None:
    objective = Objective("obj-1", "secret prompt", success_criteria=("task-1:read_file:success",))
    plan = Plan(
        "plan-1",
        "obj-1",
        (_task("task-1", CapabilityName.READ_FILE, {"path": "README.md"}),),
    )
    tools = _Coordinator(
        ToolExecutionStatus.SUCCESS,
        {"path": "README.md", "content": "secret file content"},
    )
    caplog.set_level("INFO")

    _engine(plan, _Store(), tools).run(objective, "session-1", ExecutionBudget())

    logs = caplog.text
    assert "objective accepted objective_id=obj-1" in logs
    assert "plan validated objective_id=obj-1 plan_id=plan-1 task_count=1" in logs
    assert "task transition plan_id=plan-1 task_id=task-1 status=running" in logs
    assert "budget usage event=tool_call" in logs
    assert "checkpoint saved execution_id=exec-obj-1 task_id=task-1" in logs
    assert "execution finished objective_id=obj-1 execution_id=exec-obj-1" in logs
    assert "secret prompt" not in logs
    assert "secret file content" not in logs
    assert "README.md" not in logs


def test_execution_engine_has_no_concrete_adapter_imports() -> None:
    text = open("ai_assistant/platform/application/engine.py", encoding="utf-8").read().lower()
    assert not any(term in text for term in ("ollama", "sqlite", "protobuf", "toolserver"))


def _engine(plan: Plan, store, tools, diagnostics=None) -> ExecutionEngine:
    registry = _Registry()
    return ExecutionEngine(
        DeterministicPlanner({"obj-1": plan}),
        PlanValidator(registry),
        registry,
        TaskScheduler(store),
        BudgetManager(),
        store,
        CheckpointService(store, id_factory=lambda: "chk-1"),
        ObjectiveEvaluator(),
        tools,
        tool_diagnostics=diagnostics,
        model_provider_name="dummy",
        model_name="dummy-model",
    )


def _task(
    task_id: str,
    capability: CapabilityName,
    arguments: dict[str, object],
    dependencies: tuple[str, ...] = (),
) -> PlatformTask:
    return PlatformTask(task_id, "obj-1", task_id, capability, arguments, dependencies)


class _Registry(StaticCapabilityRegistry):
    def __init__(self) -> None:
        pass

    def definition_for(self, capability: CapabilityName) -> CapabilityDefinition:
        return CapabilityDefinition(capability, "", {"required": ["path"]})

    def tool_name_for(self, capability: CapabilityName) -> str:
        return {
            CapabilityName.INSPECT_DIRECTORY: "list_directory",
            CapabilityName.READ_FILE: "read_file",
            CapabilityName.BUILD_PROJECT: "build_project",
        }[capability]


class _Coordinator(ToolExecutionCoordinator):
    def __init__(self, status: ToolExecutionStatus, content=None) -> None:
        self._status = status
        self._content = {} if content is None else content
        self.requests: list[ToolExecutionRequest] = []

    def execute(self, request: ToolExecutionRequest) -> ToolExecutionResult:
        self.requests.append(request)
        error = None
        if self._status == ToolExecutionStatus.ERROR:
            error = SanitizedToolError("tool_error", "failed")
        return ToolExecutionResult(
            request.request_id,
            request.tool_name,
            self._status,
            self._content,
            error,
        )


class _Diagnostics:
    def __init__(self) -> None:
        self.events: list[ToolCallLogEvent] = []

    def record(self, event: ToolCallLogEvent) -> None:
        self.events.append(event)


class _Store:
    def __init__(self) -> None:
        self.task_statuses: dict[tuple[str, str], PlatformTaskStatus] = {}
        self.checkpoints: list[tuple[str, str]] = []

    def save_objective(self, objective):
        self.objective = objective

    def save_plan(self, plan):
        self.plan = plan

    def save_execution(self, execution):
        self.execution = execution

    def load_task_status(self, plan_id, task_id):
        return self.task_statuses.get((plan_id, task_id))

    def update_task_status(self, plan_id, task_id, status):
        self.task_statuses[(plan_id, task_id)] = status

    def save_checkpoint(self, checkpoint):
        self.checkpoints.append((checkpoint.execution_id, checkpoint.task_id))

    def checkpoints_for_execution(self, execution_id):
        return ()
