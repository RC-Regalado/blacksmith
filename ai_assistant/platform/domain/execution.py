"""Execution domain model."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from ai_assistant.domain.errors import InvalidToolCallError


class ExecutionStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class ExecutionRecord:
    execution_id: str
    task_id: str
    status: ExecutionStatus = ExecutionStatus.PENDING
    started_at: datetime | None = None
    ended_at: datetime | None = None
    error_code: str | None = None

    def __post_init__(self) -> None:
        _require_text(self.execution_id, "execution_id")
        _require_text(self.task_id, "task_id")
        if self.ended_at and not self.started_at:
            raise InvalidToolCallError("started_at is required when ended_at is set.")


def _require_text(value: str, name: str) -> None:
    if not isinstance(value, str) or not value:
        raise InvalidToolCallError(f"{name} must be a non-empty string.")

