"""Tests for Phase 4 logical checkpoint service."""

from datetime import UTC, datetime

import pytest

from ai_assistant.domain.errors import InvalidToolCallError
from ai_assistant.infrastructure.storage.sqlite_execution import SQLiteExecutionStore
from ai_assistant.platform.application import CheckpointService
from ai_assistant.platform.domain import PlatformTaskStatus


pytestmark = pytest.mark.unit


def test_checkpoint_service_persists_successful_task_metadata(tmp_path) -> None:
    store = SQLiteExecutionStore(tmp_path / "execution.sqlite3")
    service = CheckpointService(
        store,
        id_factory=lambda: "chk-1",
        clock=lambda: datetime(2026, 8, 16, tzinfo=UTC),
    )

    checkpoint = service.checkpoint_task(
        "exec-1",
        "task-1",
        PlatformTaskStatus.SUCCEEDED,
        {"task_status": "succeeded", "cursor": "task-1"},
    )

    assert checkpoint.checkpoint_id == "chk-1"
    assert dict(service.restore_metadata("exec-1")) == {
        "task_status": "succeeded",
        "cursor": "task-1",
    }


def test_checkpoint_service_rejects_unsuccessful_task() -> None:
    service = CheckpointService(_FakeStore())

    with pytest.raises(InvalidToolCallError, match="successful tasks"):
        service.checkpoint_task("exec-1", "task-1", PlatformTaskStatus.FAILED, {})


def test_checkpoint_service_rejects_filesystem_snapshot_metadata() -> None:
    service = CheckpointService(_FakeStore())

    with pytest.raises(InvalidToolCallError, match="filesystem state"):
        service.checkpoint_task(
            "exec-1",
            "task-1",
            PlatformTaskStatus.SUCCEEDED,
            {"rollback_path": "/tmp/snapshot"},
        )


def test_checkpoint_service_restores_empty_metadata_without_checkpoint() -> None:
    assert dict(CheckpointService(_FakeStore()).restore_metadata("exec-1")) == {}


class _FakeStore:
    def save_checkpoint(self, checkpoint):
        self.checkpoint = checkpoint

    def checkpoints_for_execution(self, execution_id):
        return ()
