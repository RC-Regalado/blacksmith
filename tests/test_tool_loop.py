"""Unit tests for the deterministic tool-loop budget and guards (ADR-069)."""

import pytest

from ai_assistant.application.tool_loop import (
    DuplicateCallGuard,
    ProgressGuard,
    ToolCallAttempt,
    ToolLoopBudget,
    fingerprint,
)
from ai_assistant.domain.tools import ToolExecutionStatus


pytestmark = pytest.mark.unit


def test_fingerprint_is_stable_regardless_of_argument_order() -> None:
    first = fingerprint("read_file", {"path": "a.txt", "max_bytes": 10})
    second = fingerprint("read_file", {"max_bytes": 10, "path": "a.txt"})

    assert first == second


def test_fingerprint_differs_for_different_arguments() -> None:
    first = fingerprint("read_file", {"path": "a.txt"})
    second = fingerprint("read_file", {"path": "b.txt"})

    assert first != second


def test_duplicate_guard_flags_exact_repeat_of_a_success() -> None:
    guard = DuplicateCallGuard()
    fp = fingerprint("read_file", {"path": "a.txt"})
    history = [ToolCallAttempt(fp, "read_file", ToolExecutionStatus.SUCCESS)]

    assert guard.is_duplicate(history, fp) is True


def test_duplicate_guard_flags_exact_repeat_of_a_failure() -> None:
    guard = DuplicateCallGuard()
    fp = fingerprint("read_file", {"path": "missing.txt"})
    history = [ToolCallAttempt(fp, "read_file", ToolExecutionStatus.DENIED)]

    assert guard.is_duplicate(history, fp) is True


def test_duplicate_guard_allows_a_changed_strategy() -> None:
    guard = DuplicateCallGuard()
    history = [
        ToolCallAttempt(
            fingerprint("read_file", {"path": "missing.txt"}),
            "read_file",
            ToolExecutionStatus.DENIED,
        )
    ]

    assert guard.is_duplicate(history, fingerprint("read_file", {"path": "corrected.txt"})) is False


def test_progress_guard_allows_a_single_failure() -> None:
    guard = ProgressGuard(max_consecutive_failures=2)
    history = [
        ToolCallAttempt(fingerprint("read_file", {"path": "a.txt"}), "read_file", ToolExecutionStatus.DENIED)
    ]

    assert guard.is_stalled(history) is False


def test_progress_guard_stops_after_repeated_failures_with_no_success() -> None:
    guard = ProgressGuard(max_consecutive_failures=2)
    history = [
        ToolCallAttempt(fingerprint("read_file", {"path": "a.txt"}), "read_file", ToolExecutionStatus.DENIED),
        ToolCallAttempt(fingerprint("read_file", {"path": "b.txt"}), "read_file", ToolExecutionStatus.ERROR),
    ]

    assert guard.is_stalled(history) is True


def test_progress_guard_allows_continuation_after_a_success() -> None:
    guard = ProgressGuard(max_consecutive_failures=2)
    history = [
        ToolCallAttempt(fingerprint("list_directory", {"path": "."}), "list_directory", ToolExecutionStatus.SUCCESS),
        ToolCallAttempt(fingerprint("read_file", {"path": "a.txt"}), "read_file", ToolExecutionStatus.DENIED),
    ]

    assert guard.is_stalled(history) is False


def test_tool_loop_budget_rejects_non_positive_limits() -> None:
    with pytest.raises(ValueError, match="max_model_tool_rounds"):
        ToolLoopBudget(max_model_tool_rounds=0)
    with pytest.raises(ValueError, match="max_tool_requests"):
        ToolLoopBudget(max_tool_requests=0)
    with pytest.raises(ValueError, match="max_executor_operations"):
        ToolLoopBudget(max_executor_operations=0)
