"""Integration tests for coordinator with local executor and SQLite audit."""

import sqlite3
from pathlib import Path

import pytest

from ai_assistant.application.path_policy import WorkspacePathPolicy
from ai_assistant.application.tool_catalog import StaticToolCatalog
from ai_assistant.application.tool_coordinator import ToolExecutionCoordinator
from ai_assistant.application.tool_policy import DenyByDefaultToolPolicy
from ai_assistant.domain.tools import ToolExecutionRequest, ToolExecutionStatus
from ai_assistant.infrastructure.storage.sqlite_audit import SQLiteAuditRecorder
from ai_assistant.infrastructure.tools.local_read_only import LocalReadOnlyToolExecutor


pytestmark = pytest.mark.integration


def test_coordinator_uses_local_executor_and_sqlite_audit(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "notes.txt").write_text("hello", encoding="utf-8")
    audit_db = tmp_path / "audit.sqlite3"
    coordinator = ToolExecutionCoordinator(
        StaticToolCatalog(),
        DenyByDefaultToolPolicy(),
        WorkspacePathPolicy(str(workspace)),
        SQLiteAuditRecorder(audit_db),
        LocalReadOnlyToolExecutor(),
    )

    result = coordinator.execute(
        ToolExecutionRequest(
            request_id="req-1",
            session_id="default",
            tool_name="read_file",
            arguments={"path": "notes.txt"},
        )
    )

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.content is not None
    assert result.content["content"] == "hello"
    assert _audit_statuses(audit_db) == ["allowed", "success"]


def _audit_statuses(database: Path) -> list[str]:
    with sqlite3.connect(database) as connection:
        return [
            row[0]
            for row in connection.execute(
                "SELECT status FROM tool_audit_events ORDER BY id"
            )
        ]
