"""Objective evaluation domain model."""

from dataclasses import dataclass
from enum import StrEnum

from ai_assistant.domain.errors import InvalidToolCallError


class EvaluationStatus(StrEnum):
    PASSED = "passed"
    FAILED = "failed"
    INCONCLUSIVE = "inconclusive"


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    objective_id: str
    status: EvaluationStatus
    evidence: tuple[str, ...]
    reason: str

    def __post_init__(self) -> None:
        _require_text(self.objective_id, "objective_id")
        _require_text(self.reason, "reason")
        object.__setattr__(self, "evidence", tuple(self.evidence))
        if self.status == EvaluationStatus.PASSED and not self.evidence:
            raise InvalidToolCallError("passed evaluation requires objective evidence.")


def _require_text(value: str, name: str) -> None:
    if not isinstance(value, str) or not value:
        raise InvalidToolCallError(f"{name} must be a non-empty string.")
