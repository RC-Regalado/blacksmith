"""Tests for Phase 4 budget manager."""

import pytest

from ai_assistant.platform.application import (
    BudgetExceededCode,
    BudgetExceededError,
    BudgetManager,
)
from ai_assistant.platform.domain import BudgetUsage, ExecutionBudget


pytestmark = pytest.mark.unit


def test_budget_manager_records_usage_until_limit() -> None:
    manager = BudgetManager()
    budget = ExecutionBudget(max_tasks=1, max_model_calls=1, max_tool_calls=1)
    usage = BudgetUsage()

    usage = manager.record_task(budget, usage)
    usage = manager.record_model_call(budget, usage)
    usage = manager.record_tool_call(budget, usage)

    assert usage.tasks == 1
    assert usage.model_calls == 1
    assert usage.tool_calls == 1


@pytest.mark.parametrize(
    ("record", "code"),
    (
        (lambda manager, budget, usage: manager.record_task(budget, usage), BudgetExceededCode.TASK_LIMIT_EXCEEDED),
        (
            lambda manager, budget, usage: manager.record_model_call(budget, usage),
            BudgetExceededCode.MODEL_CALL_LIMIT_EXCEEDED,
        ),
        (
            lambda manager, budget, usage: manager.record_tool_call(budget, usage),
            BudgetExceededCode.TOOL_CALL_LIMIT_EXCEEDED,
        ),
        (
            lambda manager, budget, usage: manager.record_duration(budget, usage, 1),
            BudgetExceededCode.DURATION_LIMIT_EXCEEDED,
        ),
        (
            lambda manager, budget, usage: manager.record_output(budget, usage, 1),
            BudgetExceededCode.OUTPUT_LIMIT_EXCEEDED,
        ),
        (lambda manager, budget, usage: manager.record_write(budget, usage), BudgetExceededCode.WRITE_LIMIT_EXCEEDED),
        (lambda manager, budget, usage: manager.record_replan(budget, usage), BudgetExceededCode.REPLAN_LIMIT_EXCEEDED),
    ),
)
def test_budget_manager_rejects_before_next_forbidden_call(record, code) -> None:
    budget = ExecutionBudget(
        max_tasks=1,
        max_model_calls=1,
        max_tool_calls=1,
        max_duration_seconds=1,
        max_output_bytes=1,
    )
    usage = BudgetUsage(
        tasks=1,
        model_calls=1,
        tool_calls=1,
        duration_seconds=1,
        output_bytes=1,
    )

    with pytest.raises(BudgetExceededError) as exc_info:
        record(BudgetManager(), budget, usage)

    assert exc_info.value.code == code
    assert str(exc_info.value) == code.value
