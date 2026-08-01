"""Integration tests for SQLite tool audit recorder."""

import json
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from ai_assistant.application.errors import ToolAuditStoreError
from ai_assistant.domain.tools import (
    PolicyDecisionKind,
    ToolAuditEvent,
    ToolExecutionStatus,
    ToolPermission,
)
from ai_assistant.infrastructure.storage.sqlite_audit import SQLiteAuditRecorder


pytestmark = pytest.mark.integration


@pytest.mark.parametrize(
    ("decision", "status"),
    [
        (PolicyDecisionKind.ALLOW, ToolExecutionStatus.SUCCESS),
        (PolicyDecisionKind.DENY, ToolExecutionStatus.DENIED),
        (PolicyDecisionKind.ALLOW, ToolExecutionStatus.TIMEOUT),
        (PolicyDecisionKind.ALLOW, ToolExecutionStatus.ERROR),
    ],
)
def test_sqlite_audit_records_all_outcomes(
    tmp_path: Path,
    decision: PolicyDecisionKind,
    status: ToolExecutionStatus,
) -> None:
    database = tmp_path / "audit.sqlite3"

    SQLiteAuditRecorder(database).record(_event(decision=decision, status=status))

    row = _rows(database)[0]
    assert row["decision"] == decision.value
    assert row["status"] == status.value
    assert row["request_id"] == "req-1"
    assert row["artifact_ids"] == '["artifact-1"]'


def test_sqlite_audit_does_not_persist_file_contents_or_sensitive_values(
    tmp_path: Path,
) -> None:
    database = tmp_path / "audit.sqlite3"
    event = _event(
        argument_summary={
            "path": "notes.txt",
            "content": "file body",
            "nested": {"api_key": "secret", "safe": "ok"},
        }
    )

    SQLiteAuditRecorder(database).record(event)

    raw = _rows(database)[0]["argument_summary"]
    assert "file body" not in raw
    assert "secret" not in raw
    assert json.loads(raw) == {
        "path": "notes.txt",
        "content": "[redacted]",
        "nested": {"api_key": "[redacted]", "safe": "ok"},
    }


def test_sqlite_audit_failure_is_explicit(tmp_path: Path) -> None:
    database = tmp_path / "audit.sqlite3"
    recorder = SQLiteAuditRecorder(database)
    with sqlite3.connect(database) as connection:
        connection.execute("DROP TABLE tool_audit_events")

    with pytest.raises(ToolAuditStoreError, match="persist tool audit"):
        recorder.record(_event())


def _event(
    decision: PolicyDecisionKind = PolicyDecisionKind.ALLOW,
    status: ToolExecutionStatus = ToolExecutionStatus.SUCCESS,
    argument_summary: dict[str, object] | None = None,
) -> ToolAuditEvent:
    started = datetime(2026, 8, 1, tzinfo=UTC)
    return ToolAuditEvent(
        request_id="req-1",
        session_id="default",
        tool_name="read_file",
        permission=ToolPermission.READ_ONLY,
        decision=decision,
        status=status,
        workspace_id="workspace",
        argument_summary=argument_summary or {"path": "notes.txt"},
        started_at=started,
        ended_at=started + timedelta(milliseconds=5),
        duration_ms=5,
        denial_reason="denied" if decision == PolicyDecisionKind.DENY else None,
        error_code="error" if status == ToolExecutionStatus.ERROR else None,
        artifact_ids=("artifact-1",),
    )


def _rows(database: Path) -> list[sqlite3.Row]:
    with sqlite3.connect(database) as connection:
        connection.row_factory = sqlite3.Row
        return list(connection.execute("SELECT * FROM tool_audit_events"))
