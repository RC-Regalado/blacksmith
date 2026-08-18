"""Execution budget domain model."""

from dataclasses import dataclass, fields

from ai_assistant.domain.errors import InvalidToolCallError


@dataclass(frozen=True, slots=True)
class ExecutionBudget:
    max_tasks: int = 5
    max_model_calls: int = 4
    max_tool_calls: int = 4
    max_duration_seconds: float = 120.0
    max_output_bytes: int = 262_144
    max_writes: int = 0
    max_replans: int = 0

    def __post_init__(self) -> None:
        _require_positive(self.max_tasks, "max_tasks")
        _require_non_negative(self.max_model_calls, "max_model_calls")
        _require_non_negative(self.max_tool_calls, "max_tool_calls")
        _require_positive(self.max_duration_seconds, "max_duration_seconds")
        _require_positive(self.max_output_bytes, "max_output_bytes")
        if self.max_writes != 0:
            raise InvalidToolCallError("max_writes must be 0 in Phase 4.")
        if self.max_replans != 0:
            raise InvalidToolCallError("max_replans must be 0 in Phase 4.")


@dataclass(frozen=True, slots=True)
class BudgetUsage:
    tasks: int = 0
    model_calls: int = 0
    tool_calls: int = 0
    duration_seconds: float = 0.0
    output_bytes: int = 0
    writes: int = 0
    replans: int = 0

    def __post_init__(self) -> None:
        for field in fields(self):
            name = field.name
            value = getattr(self, name)
            _require_non_negative(value, name)


def _require_positive(value: int | float, name: str) -> None:
    if value <= 0:
        raise InvalidToolCallError(f"{name} must be positive.")


def _require_non_negative(value: int | float, name: str) -> None:
    if value < 0:
        raise InvalidToolCallError(f"{name} cannot be negative.")
