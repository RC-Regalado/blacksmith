"""Execution domain model."""

from dataclasses import dataclass, replace
from datetime import datetime
from enum import StrEnum

from ai_assistant.domain.errors import InvalidToolCallError


class ExecutionStatus(StrEnum):
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    BUDGET_EXCEEDED = "budget_exceeded"


_TERMINAL_EXECUTION_STATUSES = frozenset(
    {
        ExecutionStatus.COMPLETED,
        ExecutionStatus.FAILED,
        ExecutionStatus.CANCELLED,
        ExecutionStatus.BUDGET_EXCEEDED,
    }
)

_EXECUTION_TRANSITIONS = {
    ExecutionStatus.CREATED: frozenset({ExecutionStatus.RUNNING, ExecutionStatus.CANCELLED}),
    ExecutionStatus.RUNNING: frozenset(
        {
            ExecutionStatus.PAUSED,
            ExecutionStatus.COMPLETED,
            ExecutionStatus.FAILED,
            ExecutionStatus.CANCELLED,
            ExecutionStatus.BUDGET_EXCEEDED,
        }
    ),
    ExecutionStatus.PAUSED: frozenset({ExecutionStatus.RUNNING, ExecutionStatus.CANCELLED}),
    **{status: frozenset() for status in _TERMINAL_EXECUTION_STATUSES},
}


@dataclass(frozen=True, slots=True)
class ExecutionRecord:
    execution_id: str
    objective_id: str
    plan_id: str
    status: ExecutionStatus = ExecutionStatus.CREATED
    started_at: datetime | None = None
    ended_at: datetime | None = None
    error_code: str | None = None

    def __post_init__(self) -> None:
        _require_text(self.execution_id, "execution_id")
        _require_text(self.objective_id, "objective_id")
        _require_text(self.plan_id, "plan_id")
        if self.ended_at and not self.started_at:
            raise InvalidToolCallError("started_at is required when ended_at is set.")

    def transition(self, status: ExecutionStatus) -> "ExecutionRecord":
        if status == self.status:
            return self
        if status not in _EXECUTION_TRANSITIONS[self.status]:
            raise InvalidToolCallError(
                f"invalid execution transition {self.status.value}->{status.value}"
            )
        return replace(self, status=status)


@dataclass(frozen=True, slots=True)
class ExecutionResult:
    execution_id: str
    status: ExecutionStatus
    evidence: tuple[str, ...] = ()
    error_code: str | None = None
    observations: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require_text(self.execution_id, "execution_id")
        object.__setattr__(self, "evidence", tuple(self.evidence))
        object.__setattr__(self, "observations", tuple(self.observations))


def _require_text(value: str, name: str) -> None:
    if not isinstance(value, str) or not value:
        raise InvalidToolCallError(f"{name} must be a non-empty string.")
