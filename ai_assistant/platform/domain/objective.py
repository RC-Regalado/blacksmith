"""Objective domain model."""

from dataclasses import dataclass, replace
from enum import StrEnum

from ai_assistant.domain.errors import InvalidToolCallError


class ObjectiveStatus(StrEnum):
    CREATED = "created"
    PLANNING = "planning"
    PLANNED = "planned"
    EXECUTING = "executing"
    EVALUATING = "evaluating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"


_TERMINAL_OBJECTIVE_STATUSES = frozenset(
    {
        ObjectiveStatus.COMPLETED,
        ObjectiveStatus.FAILED,
        ObjectiveStatus.CANCELLED,
        ObjectiveStatus.BLOCKED,
    }
)

_OBJECTIVE_TRANSITIONS = {
    ObjectiveStatus.CREATED: frozenset(
        {ObjectiveStatus.PLANNING, ObjectiveStatus.CANCELLED, ObjectiveStatus.BLOCKED}
    ),
    ObjectiveStatus.PLANNING: frozenset(
        {ObjectiveStatus.PLANNED, ObjectiveStatus.FAILED, ObjectiveStatus.CANCELLED}
    ),
    ObjectiveStatus.PLANNED: frozenset(
        {ObjectiveStatus.EXECUTING, ObjectiveStatus.FAILED, ObjectiveStatus.CANCELLED}
    ),
    ObjectiveStatus.EXECUTING: frozenset(
        {
            ObjectiveStatus.EVALUATING,
            ObjectiveStatus.FAILED,
            ObjectiveStatus.CANCELLED,
            ObjectiveStatus.BLOCKED,
        }
    ),
    ObjectiveStatus.EVALUATING: frozenset(
        {ObjectiveStatus.COMPLETED, ObjectiveStatus.FAILED, ObjectiveStatus.BLOCKED}
    ),
    **{status: frozenset() for status in _TERMINAL_OBJECTIVE_STATUSES},
}


@dataclass(frozen=True, slots=True)
class Objective:
    objective_id: str
    description: str
    status: ObjectiveStatus = ObjectiveStatus.CREATED
    success_criteria: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require_text(self.objective_id, "objective_id")
        _require_text(self.description, "description")
        object.__setattr__(self, "success_criteria", tuple(self.success_criteria))

    def transition(self, status: ObjectiveStatus) -> "Objective":
        if status == self.status:
            return self
        if status not in _OBJECTIVE_TRANSITIONS[self.status]:
            raise InvalidToolCallError(
                f"invalid objective transition {self.status.value}->{status.value}"
            )
        return replace(self, status=status)


def _require_text(value: str, name: str) -> None:
    if not isinstance(value, str) or not value:
        raise InvalidToolCallError(f"{name} must be a non-empty string.")
