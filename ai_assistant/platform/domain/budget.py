"""Execution budget domain model."""

from dataclasses import dataclass

from ai_assistant.domain.errors import InvalidToolCallError


@dataclass(frozen=True, slots=True)
class ExecutionBudget:
    max_steps: int = 1
    max_tool_calls: int = 1
    max_seconds: float = 30.0

    def __post_init__(self) -> None:
        if self.max_steps < 1:
            raise InvalidToolCallError("max_steps must be positive.")
        if self.max_tool_calls < 0:
            raise InvalidToolCallError("max_tool_calls cannot be negative.")
        if self.max_seconds <= 0:
            raise InvalidToolCallError("max_seconds must be positive.")

