"""Tests for the dedicated SQLite execution store."""

import sqlite3
from datetime import UTC, datetime

import pytest

from ai_assistant.domain.errors import ExecutionStoreError
from ai_assistant.infrastructure.storage.sqlite_execution import SQLiteExecutionStore
from ai_assistant.platform.domain import (
    CapabilityName,
    Checkpoint,
    ExecutionRecord,
    ExecutionStatus,
    Objective,
    ObjectiveStatus,
    Plan,
    PlatformTask,
    PlatformTaskStatus,
)


pytestmark = pytest.mark.unit


def test_sqlite_execution_store_reloads_execution_state(tmp_path) -> None:
    database = tmp_path / "execution.sqlite3"
    store = SQLiteExecutionStore(database)
    objective = Objective("obj-1", "Inspect", ObjectiveStatus.PLANNED, ("listed",))
    plan = Plan("plan-1", "obj-1", (_task("task-1"),))
    execution = ExecutionRecord(
        "exec-1",
        "obj-1",
        "plan-1",
        ExecutionStatus.RUNNING,
        datetime(2026, 8, 10, tzinfo=UTC),
    )

    store.save_objective(objective)
    store.save_plan(plan)
    store.save_execution(execution)

    restored = SQLiteExecutionStore(database)

    assert restored.load_objective("obj-1") == objective
    assert restored.load_plan("plan-1") == plan
    assert restored.load_execution("exec-1") == execution


def test_sqlite_execution_store_persists_task_status_and_checkpoint(tmp_path) -> None:
    store = SQLiteExecutionStore(tmp_path / "execution.sqlite3")
    checkpoint = Checkpoint(
        "chk-1",
        "exec-1",
        "task-1",
        {"status": "ok"},
        datetime(2026, 8, 10, tzinfo=UTC),
    )

    store.save_plan(Plan("plan-1", "obj-1", (_task("task-1"),)))
    store.update_task_status("plan-1", "task-1", PlatformTaskStatus.SUCCEEDED)
    store.save_checkpoint(checkpoint)

    assert store.load_task_status("plan-1", "task-1") == PlatformTaskStatus.SUCCEEDED
    assert store.checkpoints_for_execution("exec-1") == (checkpoint,)


def test_sqlite_execution_store_rolls_back_failed_plan_replace(tmp_path) -> None:
    store = SQLiteExecutionStore(tmp_path / "execution.sqlite3")
    original = Plan("plan-1", "obj-1", (_task("task-1"),))
    duplicate = _task("task-2")
    tampered = Plan("plan-1", "obj-1", (duplicate,))
    object.__setattr__(tampered, "tasks", (duplicate, duplicate))

    store.save_plan(original)

    with pytest.raises(ExecutionStoreError):
        store.save_plan(tampered)

    assert store.load_plan("plan-1") == original


def test_sqlite_execution_store_uses_dedicated_tables(tmp_path) -> None:
    database = tmp_path / "execution.sqlite3"
    SQLiteExecutionStore(database)

    with sqlite3.connect(database) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }

    assert "messages" not in tables
    assert "tool_audit" not in tables
    assert {
        "execution_objectives",
        "execution_plans",
        "execution_tasks",
        "executions",
        "execution_checkpoints",
    }.issubset(tables)


def _task(task_id: str) -> PlatformTask:
    return PlatformTask(
        task_id,
        "obj-1",
        task_id,
        CapabilityName.READ_FILE,
        {"path": "README.md"},
    )
