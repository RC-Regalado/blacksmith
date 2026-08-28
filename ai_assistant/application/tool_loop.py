"""Deterministic tool-loop budget and guards (ADR-069).

Supersedes the previous hard single-round cap (ADR-024) with a small,
platform-owned, fully deterministic budget plus duplicate/no-progress guards.
Nothing here is LLM-mediated: every decision is a pure function of the
current turn's own recorded tool-call history. `AgentRuntime` owns the loop
control flow; this module owns the numeric limits and the guard rules so no
threshold is hardcoded inline in the runtime.
"""

from dataclasses import dataclass
from collections.abc import Mapping
import json

from ai_assistant.domain.tools import ToolExecutionStatus


@dataclass(frozen=True, slots=True)
class ToolLoopBudget:
    max_model_tool_rounds: int = 3
    max_tool_requests: int = 5
    max_executor_operations: int = 8

    def __post_init__(self) -> None:
        if self.max_model_tool_rounds <= 0:
            raise ValueError("max_model_tool_rounds must be positive.")
        if self.max_tool_requests <= 0:
            raise ValueError("max_tool_requests must be positive.")
        if self.max_executor_operations <= 0:
            raise ValueError("max_executor_operations must be positive.")


@dataclass(frozen=True, slots=True)
class ToolCallAttempt:
    fingerprint: str
    tool_name: str
    status: ToolExecutionStatus


_FAILURE_STATUSES = frozenset(
    {ToolExecutionStatus.DENIED, ToolExecutionStatus.ERROR, ToolExecutionStatus.TIMEOUT}
)


def fingerprint(tool_name: str, arguments: Mapping[str, object]) -> str:
    return f"{tool_name}:{json.dumps(arguments, sort_keys=True, default=str)}"


class DuplicateCallGuard:
    """Rejects an exact repeat of any tool call already attempted this turn.

    A repeat cannot add new evidence regardless of whether the earlier
    attempt succeeded or failed, so it is blocked without spending another
    executor operation.
    """

    def is_duplicate(self, history: list[ToolCallAttempt], candidate: str) -> bool:
        return any(attempt.fingerprint == candidate for attempt in history)


class ProgressGuard:
    """Stops the loop once the turn has made no progress at all.

    A changed strategy (different fingerprint) after a failure remains
    allowed — only a streak of consecutive failures with zero success
    triggers a stop, and only once that streak reaches the configured
    threshold. This is a count over outcomes already recorded, never a
    judgment about *which* strategy the model chose.
    """

    def __init__(self, max_consecutive_failures: int = 2) -> None:
        if max_consecutive_failures <= 0:
            raise ValueError("max_consecutive_failures must be positive.")
        self._max_consecutive_failures = max_consecutive_failures

    def is_stalled(self, history: list[ToolCallAttempt]) -> bool:
        if len(history) < self._max_consecutive_failures:
            return False
        recent = history[-self._max_consecutive_failures :]
        return all(attempt.status in _FAILURE_STATUSES for attempt in recent)
