"""Tests for Phase 4 platform domain models."""

from datetime import UTC, datetime
from pathlib import Path

import pytest

from ai_assistant.domain.errors import InvalidToolCallError
from ai_assistant.platform.domain import (
    BudgetUsage,
    CapabilityName,
    Checkpoint,
    EvaluationResult,
    EvaluationStatus,
    ExecutionBudget,
    Objective,
    ObjectiveStatus,
    Plan,
    PlanStatus,
    PlatformTask,
    PlatformTaskStatus,
)


pytestmark = pytest.mark.unit


def test_objective_task_plan_and_execution_transitions_are_validated() -> None:
    objective = Objective("obj-1", "Inspect repo")
    assert objective.transition(ObjectiveStatus.PLANNING).status == ObjectiveStatus.PLANNING

    task = PlatformTask("task-1", "obj-1", "List files", CapabilityName.INSPECT_DIRECTORY)
    ready = task.transition(PlatformTaskStatus.READY)
    assert ready.transition(PlatformTaskStatus.RUNNING).status == PlatformTaskStatus.RUNNING

    plan = Plan("plan-1", "obj-1", (task,))
    assert plan.transition(PlanStatus.VALIDATED).status == PlanStatus.VALIDATED

    with pytest.raises(InvalidToolCallError, match="invalid objective transition"):
        objective.transition(ObjectiveStatus.COMPLETED)
    with pytest.raises(InvalidToolCallError, match="invalid task transition"):
        task.transition(PlatformTaskStatus.SUCCEEDED)
    with pytest.raises(InvalidToolCallError, match="invalid plan transition"):
        plan.transition(PlanStatus.COMPLETED)


def test_domain_rejects_write_budget_and_write_capability() -> None:
    budget = ExecutionBudget()
    assert budget.max_tasks == 5
    assert budget.max_writes == 0
    assert budget.max_replans == 0
    assert BudgetUsage().writes == 0
    assert "write" not in {capability.value.lower() for capability in CapabilityName}

    with pytest.raises(InvalidToolCallError, match="max_writes"):
        ExecutionBudget(max_writes=1)
    with pytest.raises(InvalidToolCallError, match="max_replans"):
        ExecutionBudget(max_replans=1)
    with pytest.raises(InvalidToolCallError, match="unknown task capability"):
        PlatformTask("task-1", "obj-1", "Write", "write")


def test_plan_checkpoint_and_evaluation_guard_domain_invariants() -> None:
    task = PlatformTask("task-1", "obj-1", "Read", CapabilityName.READ_FILE)
    with pytest.raises(InvalidToolCallError, match="unique"):
        Plan("plan-1", "obj-1", (task, task))

    created_at = datetime(2026, 8, 5, tzinfo=UTC)
    with pytest.raises(InvalidToolCallError, match="filesystem state"):
        Checkpoint("chk-1", "exec-1", "task-1", {"file_contents": "secret"}, created_at)

    with pytest.raises(InvalidToolCallError, match="evidence"):
        EvaluationResult("obj-1", EvaluationStatus.PASSED, (), "looks done")


def test_platform_domain_has_no_infrastructure_dependency_leaks() -> None:
    forbidden = ("sqlite", "ollama", "protobuf", "toolserver")
    for path in Path("ai_assistant/platform/domain").glob("*.py"):
        text = path.read_text(encoding="utf-8").lower()
        assert not any(term in text for term in forbidden), path
