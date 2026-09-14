"""Tests for Phase 4 objective evaluator."""

import pytest

from ai_assistant.platform.application import ObjectiveEvaluator
from ai_assistant.platform.domain import (
    EvaluationStatus,
    ExecutionResult,
    ExecutionStatus,
    Objective,
    PlatformTaskStatus,
)


pytestmark = pytest.mark.unit


def test_objective_evaluator_requires_execution_success() -> None:
    result = ObjectiveEvaluator().evaluate(
        Objective("obj-1", "Inspect", success_criteria=("listed files",)),
        ExecutionResult("exec-1", ExecutionStatus.FAILED, ("listed files",)),
    )

    assert result.status == EvaluationStatus.FAILED
    assert result.reason == "execution failed"


def test_objective_evaluator_requires_all_task_states_to_succeed() -> None:
    result = ObjectiveEvaluator().evaluate(
        Objective("obj-1", "Inspect", success_criteria=("listed files",)),
        ExecutionResult("exec-1", ExecutionStatus.COMPLETED, ("listed files",)),
        {"task-1": PlatformTaskStatus.SUCCEEDED, "task-2": PlatformTaskStatus.FAILED},
    )

    assert result.status == EvaluationStatus.FAILED
    assert "task-2" in result.reason


def test_objective_evaluator_cannot_be_overridden_by_model_success_text() -> None:
    result = ObjectiveEvaluator().evaluate(
        Objective("obj-1", "Inspect", success_criteria=("listed files",)),
        ExecutionResult("exec-1", ExecutionStatus.COMPLETED, ("model says success",)),
        {"task-1": PlatformTaskStatus.SUCCEEDED},
    )

    assert result.status == EvaluationStatus.FAILED
    assert "listed files" in result.reason


def test_objective_evaluator_passes_with_task_success_and_evidence() -> None:
    result = ObjectiveEvaluator().evaluate(
        Objective("obj-1", "Inspect", success_criteria=("listed files",)),
        ExecutionResult(
            "exec-1",
            ExecutionStatus.COMPLETED,
            ("listed files in workspace",),
        ),
        {"task-1": PlatformTaskStatus.SUCCEEDED},
    )

    assert result.status == EvaluationStatus.PASSED
