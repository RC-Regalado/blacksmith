"""Plan domain model."""

from dataclasses import dataclass
from enum import StrEnum

from ai_assistant.domain.errors import InvalidToolCallError
from ai_assistant.platform.domain.task import PlatformTask


class PlanStatus(StrEnum):
    DRAFT = "draft"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    BLOCKED = "blocked"


@dataclass(frozen=True, slots=True)
class Plan:
    plan_id: str
    objective_id: str
    tasks: tuple[PlatformTask, ...] = ()
    status: PlanStatus = PlanStatus.DRAFT

    def __post_init__(self) -> None:
        _require_text(self.plan_id, "plan_id")
        _require_text(self.objective_id, "objective_id")


def _require_text(value: str, name: str) -> None:
    if not isinstance(value, str) or not value:
        raise InvalidToolCallError(f"{name} must be a non-empty string.")

