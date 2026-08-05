"""Tests for Phase 4 platform scaffolding."""

import pytest

from ai_assistant.domain.errors import InvalidToolCallError
from ai_assistant.platform.domain import (
    ExecutionBudget,
    Objective,
    Plan,
    PlatformTask,
)
from ai_assistant.platform.ports import (
    CapabilityRegistry,
    Evaluator,
    ExecutionStore,
    Planner,
)


pytestmark = pytest.mark.unit


def test_phase4_domain_models_are_importable() -> None:
    objective = Objective("obj-1", "Prepare Phase 4")
    task = PlatformTask("task-1", objective.objective_id, "Create structure")
    plan = Plan("plan-1", objective.objective_id, (task,))
    budget = ExecutionBudget(max_steps=1, max_tool_calls=0, max_seconds=1.0)

    assert plan.tasks == (task,)
    assert budget.max_tool_calls == 0


def test_phase4_domain_models_fail_explicitly() -> None:
    with pytest.raises(InvalidToolCallError, match="objective_id"):
        Objective("", "missing id")


def test_phase4_ports_are_abstract() -> None:
    for port in (CapabilityRegistry, Evaluator, ExecutionStore, Planner):
        with pytest.raises(TypeError):
            port()
