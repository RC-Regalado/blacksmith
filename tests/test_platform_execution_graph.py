"""Tests for Phase 4 execution graph."""

import pytest

from ai_assistant.domain.errors import InvalidToolCallError
from ai_assistant.platform.application import ExecutionGraph
from ai_assistant.platform.domain import CapabilityName, Plan, PlatformTask, PlatformTaskStatus


pytestmark = pytest.mark.unit


def test_execution_graph_selects_ready_tasks_in_plan_order() -> None:
    first = _task("task-1")
    second = _task("task-2")
    third = _task("task-3", ("task-1",))
    graph = ExecutionGraph.from_plan(Plan("plan-1", "obj-1", (first, second, third)))

    assert graph.task_ids == ("task-1", "task-2", "task-3")
    assert graph.ready_tasks({}) == (first, second)
    assert graph.ready_tasks({"task-1": PlatformTaskStatus.SUCCEEDED}) == (second, third)


def test_execution_graph_blocks_dependents_after_failed_dependency() -> None:
    first = _task("task-1")
    second = _task("task-2", ("task-1",))
    graph = ExecutionGraph.from_plan(Plan("plan-1", "obj-1", (first, second)))

    states = {"task-1": PlatformTaskStatus.FAILED}

    assert graph.ready_tasks(states) == ()
    assert graph.blocked_tasks(states) == (second,)


def test_execution_graph_rejects_tampered_invalid_plan() -> None:
    first = _task("task-1", ("task-2",))
    second = _task("task-2", ("task-1",))
    plan = Plan("plan-1", "obj-1", (first,))
    object.__setattr__(plan, "tasks", (first, second))

    with pytest.raises(InvalidToolCallError, match="cycle"):
        ExecutionGraph.from_plan(plan)


def _task(task_id: str, dependencies: tuple[str, ...] = ()) -> PlatformTask:
    return PlatformTask(
        task_id,
        "obj-1",
        task_id,
        CapabilityName.READ_FILE,
        {"path": "README.md"},
        dependencies,
    )
