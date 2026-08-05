"""Task domain model."""

from dataclasses import dataclass
from enum import StrEnum

from ai_assistant.domain.errors import InvalidToolCallError


class PlatformTaskStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class PlatformTask:
    task_id: str
    objective_id: str
    description: str
    dependencies: tuple[str, ...] = ()
    status: PlatformTaskStatus = PlatformTaskStatus.PENDING

    def __post_init__(self) -> None:
        _require_text(self.task_id, "task_id")
        _require_text(self.objective_id, "objective_id")
        _require_text(self.description, "description")
        if not isinstance(self.dependencies, tuple):
            object.__setattr__(self, "dependencies", tuple(self.dependencies))


def _require_text(value: str, name: str) -> None:
    if not isinstance(value, str) or not value:
        raise InvalidToolCallError(f"{name} must be a non-empty string.")

