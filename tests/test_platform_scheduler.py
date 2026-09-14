"""Tests for Phase 4 sequential scheduler."""

import pytest

from ai_assistant.domain.errors import InvalidToolCallError
from ai_assistant.platform.application import ExecutionGraph, TaskScheduler
from ai_assistant.platform.domain import CapabilityName, Plan, PlatformTask, PlatformTaskStatus


pytestmark = pytest.mark.unit


def test_scheduler_starts_one_ready_task_and_persists_transitions() -> None:
    store = _Store()
    graph = ExecutionGraph.from_plan(Plan("plan-1", "obj-1", (_task("task-1"), _task("task-2"))))

    task = TaskScheduler(store).start_next("plan-1", graph)

    assert task is not None
    assert task.task_id == "task-1"
    assert task.status == PlatformTaskStatus.RUNNING
    assert store.events == [
        ("task-1", PlatformTaskStatus.READY),
        ("task-1", PlatformTaskStatus.RUNNING),
    ]


def test_scheduler_rejects_parallel_running_task() -> None:
    store = _Store({"task-1": PlatformTaskStatus.RUNNING})
    graph = ExecutionGraph.from_plan(Plan("plan-1", "obj-1", (_task("task-1"), _task("task-2"))))

    with pytest.raises(InvalidToolCallError, match="running task"):
        TaskScheduler(store).start_next("plan-1", graph)


def test_scheduler_unblocks_after_success_and_blocks_after_failure() -> None:
    store = _Store()
    graph = ExecutionGraph.from_plan(
        Plan("plan-1", "obj-1", (_task("task-1"), _task("task-2", ("task-1",))))
    )
    scheduler = TaskScheduler(store)

    scheduler.start_next("plan-1", graph)
    scheduler.mark_succeeded("plan-1", "task-1")

    assert scheduler.start_next("plan-1", graph).task_id == "task-2"  # type: ignore[union-attr]

    store = _Store({"task-1": PlatformTaskStatus.FAILED})
    assert TaskScheduler(store).start_next("plan-1", graph) is None
    assert store.statuses["task-2"] == PlatformTaskStatus.BLOCKED


def _task(task_id: str, dependencies: tuple[str, ...] = ()) -> PlatformTask:
    return PlatformTask(
        task_id,
        "obj-1",
        task_id,
        CapabilityName.READ_FILE,
        {"path": "README.md"},
        dependencies,
    )


class _Store:
    def __init__(self, statuses: dict[str, PlatformTaskStatus] | None = None) -> None:
        self.statuses = statuses or {}
        self.events: list[tuple[str, PlatformTaskStatus]] = []

    def load_task_status(self, plan_id: str, task_id: str) -> PlatformTaskStatus | None:
        return self.statuses.get(task_id)

    def update_task_status(
        self,
        plan_id: str,
        task_id: str,
        status: PlatformTaskStatus,
    ) -> None:
        self.statuses[task_id] = status
        self.events.append((task_id, status))
