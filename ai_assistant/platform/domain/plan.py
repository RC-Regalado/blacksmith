"""Plan domain model."""

from dataclasses import dataclass, replace
from enum import StrEnum

from ai_assistant.domain.errors import InvalidToolCallError
from ai_assistant.platform.domain.task import PlatformTask


class PlanStatus(StrEnum):
    DRAFT = "draft"
    VALIDATED = "validated"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


_TERMINAL_PLAN_STATUSES = frozenset(
    {
        PlanStatus.COMPLETED,
        PlanStatus.FAILED,
        PlanStatus.BLOCKED,
        PlanStatus.CANCELLED,
    }
)

_PLAN_TRANSITIONS = {
    PlanStatus.DRAFT: frozenset({PlanStatus.VALIDATED, PlanStatus.FAILED}),
    PlanStatus.VALIDATED: frozenset({PlanStatus.RUNNING, PlanStatus.CANCELLED}),
    PlanStatus.RUNNING: frozenset(
        {PlanStatus.COMPLETED, PlanStatus.FAILED, PlanStatus.BLOCKED}
    ),
    **{status: frozenset() for status in _TERMINAL_PLAN_STATUSES},
}


@dataclass(frozen=True, slots=True)
class Plan:
    plan_id: str
    objective_id: str
    tasks: tuple[PlatformTask, ...] = ()
    status: PlanStatus = PlanStatus.DRAFT

    def __post_init__(self) -> None:
        _require_text(self.plan_id, "plan_id")
        _require_text(self.objective_id, "objective_id")
        object.__setattr__(self, "tasks", tuple(self.tasks))
        if any(not isinstance(task, PlatformTask) for task in self.tasks):
            raise InvalidToolCallError("plan tasks must be PlatformTask instances.")
        task_ids = [task.task_id for task in self.tasks]
        if len(task_ids) != len(set(task_ids)):
            raise InvalidToolCallError("plan task IDs must be unique.")
        if any(task.objective_id != self.objective_id for task in self.tasks):
            raise InvalidToolCallError("plan tasks must belong to the same objective.")

    def transition(self, status: PlanStatus) -> "Plan":
        if status == self.status:
            return self
        if status not in _PLAN_TRANSITIONS[self.status]:
            raise InvalidToolCallError(
                f"invalid plan transition {self.status.value}->{status.value}"
            )
        return replace(self, status=status)


def _require_text(value: str, name: str) -> None:
    if not isinstance(value, str) or not value:
        raise InvalidToolCallError(f"{name} must be a non-empty string.")
