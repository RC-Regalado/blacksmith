"""Tests for Phase 4 plan validation."""

import pytest

from ai_assistant.application.tool_catalog import StaticToolCatalog
from ai_assistant.platform.application import (
    PlanValidationCode,
    PlanValidationError,
    PlanValidator,
    StaticCapabilityRegistry,
)
from ai_assistant.platform.domain import CapabilityName, ExecutionBudget, Plan, PlatformTask


pytestmark = pytest.mark.unit


def test_plan_validator_accepts_valid_plan() -> None:
    validator = _validator()
    plan = Plan(
        "plan-1",
        "obj-1",
        (
            _task("task-1", CapabilityName.INSPECT_DIRECTORY, {"path": "."}),
            _task("task-2", CapabilityName.READ_FILE, {"path": "README.md"}, ("task-1",)),
        ),
    )

    assert validator.validate(plan, ExecutionBudget()) == plan


def test_plan_validator_rejects_invalid_plans() -> None:
    cases = (
        (
            Plan("plan-1", "obj-1", (_task("task-1", CapabilityName.READ_FILE, {}),)),
            PlanValidationCode.INVALID_ARGUMENTS,
        ),
        (
            Plan(
                "plan-1",
                "obj-1",
                (_task("task-1", CapabilityName.READ_FILE, {"path": "README.md"}, ("missing",)),),
            ),
            PlanValidationCode.MISSING_DEPENDENCY,
        ),
        (
            Plan(
                "plan-1",
                "obj-1",
                (
                    _task("task-1", CapabilityName.READ_FILE, {"path": "a"}, ("task-2",)),
                    _task("task-2", CapabilityName.READ_FILE, {"path": "b"}, ("task-1",)),
                ),
            ),
            PlanValidationCode.GRAPH_CYCLE,
        ),
        (
            Plan(
                "plan-1",
                "obj-1",
                tuple(
                    _task(f"task-{index}", CapabilityName.READ_FILE, {"path": "README.md"})
                    for index in range(6)
                ),
            ),
            PlanValidationCode.TASK_LIMIT_EXCEEDED,
        ),
    )

    for plan, code in cases:
        with pytest.raises(PlanValidationError) as exc_info:
            _validator().validate(plan, ExecutionBudget(max_tasks=5))

        assert exc_info.value.code == code
        assert str(exc_info.value) == code.value


def test_plan_validator_rejects_malformed_plan() -> None:
    with pytest.raises(PlanValidationError) as exc_info:
        _validator().validate(object(), ExecutionBudget())  # type: ignore[arg-type]

    assert exc_info.value.code == PlanValidationCode.MALFORMED_PLAN


def test_plan_validator_rejects_duplicate_task_ids_from_tampered_plan() -> None:
    task = _task("task-1", CapabilityName.READ_FILE, {"path": "README.md"})
    plan = Plan("plan-1", "obj-1", (task,))
    object.__setattr__(plan, "tasks", (task, task))

    with pytest.raises(PlanValidationError) as exc_info:
        _validator().validate(plan, ExecutionBudget())

    assert exc_info.value.code == PlanValidationCode.DUPLICATE_TASK_ID


def test_plan_validator_rejects_unknown_capability_from_tampered_task() -> None:
    task = _task("task-1", CapabilityName.READ_FILE, {"path": "README.md"})
    object.__setattr__(task, "capability", "write")
    plan = Plan("plan-1", "obj-1", (task,))

    with pytest.raises(PlanValidationError) as exc_info:
        _validator().validate(plan, ExecutionBudget())

    assert exc_info.value.code == PlanValidationCode.UNKNOWN_CAPABILITY


def _validator() -> PlanValidator:
    return PlanValidator(StaticCapabilityRegistry(StaticToolCatalog()))


def _task(
    task_id: str,
    capability: CapabilityName,
    arguments: dict[str, object],
    dependencies: tuple[str, ...] = (),
) -> PlatformTask:
    return PlatformTask(task_id, "obj-1", task_id, capability, arguments, dependencies)
