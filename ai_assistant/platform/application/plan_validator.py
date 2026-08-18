"""Plan validation service."""

from enum import StrEnum

from ai_assistant.domain.errors import InvalidToolCallError
from ai_assistant.platform.domain.budget import ExecutionBudget
from ai_assistant.platform.domain.plan import Plan
from ai_assistant.platform.domain.task import CapabilityName, PlatformTask
from ai_assistant.platform.ports.capability_registry import CapabilityRegistry


class PlanValidationCode(StrEnum):
    MALFORMED_PLAN = "malformed_plan"
    DUPLICATE_TASK_ID = "duplicate_task_id"
    MISSING_DEPENDENCY = "missing_dependency"
    GRAPH_CYCLE = "graph_cycle"
    UNKNOWN_CAPABILITY = "unknown_capability"
    INVALID_ARGUMENTS = "invalid_arguments"
    TASK_LIMIT_EXCEEDED = "task_limit_exceeded"


class PlanValidationError(InvalidToolCallError):
    def __init__(self, code: PlanValidationCode) -> None:
        self.code = code
        super().__init__(code.value)


class PlanValidator:
    def __init__(self, registry: CapabilityRegistry) -> None:
        self._registry = registry

    def validate(self, plan: Plan, budget: ExecutionBudget) -> Plan:
        if not isinstance(plan, Plan):
            raise PlanValidationError(PlanValidationCode.MALFORMED_PLAN)
        if len(plan.tasks) > budget.max_tasks:
            raise PlanValidationError(PlanValidationCode.TASK_LIMIT_EXCEEDED)
        task_ids = [task.task_id for task in plan.tasks if isinstance(task, PlatformTask)]
        if len(task_ids) != len(set(task_ids)):
            raise PlanValidationError(PlanValidationCode.DUPLICATE_TASK_ID)
        if len(task_ids) != len(plan.tasks):
            raise PlanValidationError(PlanValidationCode.MALFORMED_PLAN)
        self._validate_tasks(plan.tasks, set(task_ids))
        self._reject_cycles(plan.tasks)
        return plan

    def _validate_tasks(self, tasks: tuple[PlatformTask, ...], task_ids: set[str]) -> None:
        for task in tasks:
            if not isinstance(task.capability, CapabilityName):
                raise PlanValidationError(PlanValidationCode.UNKNOWN_CAPABILITY)
            try:
                definition = self._registry.definition_for(task.capability)
            except InvalidToolCallError as exc:
                raise PlanValidationError(PlanValidationCode.UNKNOWN_CAPABILITY) from exc
            required = set(definition.input_schema.get("required", ()))
            if not required.issubset(task.arguments):
                raise PlanValidationError(PlanValidationCode.INVALID_ARGUMENTS)
            if any(dependency not in task_ids for dependency in task.dependencies):
                raise PlanValidationError(PlanValidationCode.MISSING_DEPENDENCY)

    def _reject_cycles(self, tasks: tuple[PlatformTask, ...]) -> None:
        graph = {task.task_id: set(task.dependencies) for task in tasks}
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(task_id: str) -> None:
            if task_id in visiting:
                raise PlanValidationError(PlanValidationCode.GRAPH_CYCLE)
            if task_id in visited:
                return
            visiting.add(task_id)
            for dependency in graph[task_id]:
                visit(dependency)
            visiting.remove(task_id)
            visited.add(task_id)

        for task_id in graph:
            visit(task_id)
