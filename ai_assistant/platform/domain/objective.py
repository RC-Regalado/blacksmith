"""Objective domain model."""

from dataclasses import dataclass
from enum import StrEnum

from ai_assistant.domain.errors import InvalidToolCallError


class ObjectiveStatus(StrEnum):
    PROPOSED = "proposed"
    ACTIVE = "active"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class Objective:
    objective_id: str
    description: str
    status: ObjectiveStatus = ObjectiveStatus.PROPOSED

    def __post_init__(self) -> None:
        _require_text(self.objective_id, "objective_id")
        _require_text(self.description, "description")


def _require_text(value: str, name: str) -> None:
    if not isinstance(value, str) or not value:
        raise InvalidToolCallError(f"{name} must be a non-empty string.")

