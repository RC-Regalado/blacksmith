"""Tests for Phase 4 planner and evaluator ports."""

from pathlib import Path

import pytest

from ai_assistant.domain.errors import InvalidToolCallError
from ai_assistant.platform.application import DeterministicEvaluator, DeterministicPlanner
from ai_assistant.platform.domain import (
    CapabilityName,
    EvaluationStatus,
    ExecutionResult,
    ExecutionStatus,
    Objective,
    Plan,
    PlatformTask,
)
from ai_assistant.platform.ports import Evaluator, Planner


pytestmark = pytest.mark.unit


def test_planner_fake_returns_structured_plan_through_port() -> None:
    objective = Objective("obj-1", "Inspect", success_criteria=("listed files",))
    task = PlatformTask("task-1", "obj-1", "List", CapabilityName.INSPECT_DIRECTORY)
    plan = Plan("plan-1", "obj-1", (task,))
    planner: Planner = DeterministicPlanner({"obj-1": plan})

    assert planner.create_plan(objective) == plan


def test_planner_fake_rejects_malformed_results() -> None:
    planner: Planner = DeterministicPlanner({"obj-1": object()})  # type: ignore[arg-type]

    with pytest.raises(InvalidToolCallError, match="malformed plan"):
        planner.create_plan(Objective("obj-1", "Inspect"))


def test_planner_fake_rejects_wrong_objective() -> None:
    plan = Plan("plan-1", "other", ())
    planner: Planner = DeterministicPlanner({"obj-1": plan})

    with pytest.raises(InvalidToolCallError, match="different objective"):
        planner.create_plan(Objective("obj-1", "Inspect"))


def test_evaluator_fake_uses_evidence_not_summary() -> None:
    evaluator: Evaluator = DeterministicEvaluator()
    objective = Objective("obj-1", "Inspect", success_criteria=("listed files",))
    result = ExecutionResult(
        "exec-1",
        ExecutionStatus.COMPLETED,
        ("model says success",),
    )

    evaluation = evaluator.evaluate(objective, result)

    assert evaluation.status == EvaluationStatus.FAILED
    assert "listed files" in evaluation.reason


def test_evaluator_fake_passes_when_evidence_matches_criteria() -> None:
    evaluator: Evaluator = DeterministicEvaluator()
    objective = Objective("obj-1", "Inspect", success_criteria=("listed files",))
    result = ExecutionResult(
        "exec-1",
        ExecutionStatus.COMPLETED,
        ("listed files in workspace",),
    )

    assert evaluator.evaluate(objective, result).status == EvaluationStatus.PASSED


def test_planner_and_evaluator_contracts_do_not_import_infrastructure() -> None:
    forbidden = ("ollama", "sqlite", "protobuf", "toolserver", "unix_socket")
    for path in (
        Path("ai_assistant/platform/ports/planner.py"),
        Path("ai_assistant/platform/ports/evaluator.py"),
        Path("ai_assistant/platform/application/planner.py"),
        Path("ai_assistant/platform/application/evaluator.py"),
    ):
        text = path.read_text(encoding="utf-8").lower()
        assert not any(term in text for term in forbidden), path
