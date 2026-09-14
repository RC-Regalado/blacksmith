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


def test_sqlite_audit_persists_interaction_id(tmp_path: Path) -> None:
    database = tmp_path / "audit.sqlite3"

    SQLiteAuditRecorder(database).record(_event(interaction_id="turn-abc123"))

    assert _rows(database)[0]["interaction_id"] == "turn-abc123"


def test_sqlite_audit_allows_missing_interaction_id(tmp_path: Path) -> None:
    database = tmp_path / "audit.sqlite3"

    SQLiteAuditRecorder(database).record(_event())

    assert _rows(database)[0]["interaction_id"] is None


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


def test_audit_purge_dry_run_reports_without_deleting(tmp_path: Path) -> None:
    database = tmp_path / "audit.sqlite3"
    recorder = SQLiteAuditRecorder(database)
    now = datetime(2026, 8, 1, tzinfo=UTC)
    recorder.record(_event(started=now - timedelta(days=31), tool_name="search_text"))

    result = recorder.purge_expired(dry_run=True, now=now)

    assert result.deleted_count == 1
    assert len(_rows(database)) == 1


def test_real_audit_purge_requires_confirmation(tmp_path: Path) -> None:
    recorder = SQLiteAuditRecorder(tmp_path / "audit.sqlite3")

    with pytest.raises(ToolAuditStoreError, match="confirmation"):
        recorder.purge_expired(dry_run=False, confirm=False)


def test_audit_purge_enforces_minimum_retention_by_class(tmp_path: Path) -> None:
    database = tmp_path / "audit.sqlite3"
    recorder = SQLiteAuditRecorder(database)
    now = datetime(2026, 8, 1, tzinfo=UTC)
    recorder.record(_event(started=now - timedelta(days=31), tool_name="search_text"))
    recorder.record(_event(started=now - timedelta(days=89), tool_name="git_status"))
    recorder.record(_event(started=now - timedelta(days=90), tool_name="run_tests"))
    recorder.record(_event(started=now - timedelta(days=364), tool_name="write"))
    recorder.record(
        _event(
            started=now - timedelta(days=365),
            tool_name="read_file",
            decision=PolicyDecisionKind.DENY,
            status=ToolExecutionStatus.DENIED,
        )
    )

    result = recorder.purge_expired(dry_run=False, confirm=True, now=now)

    remaining = [row["tool_name"] for row in _rows(database)]
    assert result.deleted_count == 3
    assert remaining == ["git_status", "write", "audit_purge"]


def test_audit_purge_records_purge_event(tmp_path: Path) -> None:
    database = tmp_path / "audit.sqlite3"
    recorder = SQLiteAuditRecorder(database)
    now = datetime(2026, 8, 1, tzinfo=UTC)
    recorder.record(_event(started=now - timedelta(days=31), tool_name="file_metadata"))

    recorder.purge_expired(dry_run=False, confirm=True, now=now)

    purge = _rows(database)[0]
    assert purge["tool_name"] == "audit_purge"
    assert json.loads(purge["argument_summary"])["deleted_count"] == 1


def _event(
    decision: PolicyDecisionKind = PolicyDecisionKind.ALLOW,
    status: ToolExecutionStatus = ToolExecutionStatus.SUCCESS,
    argument_summary: dict[str, object] | None = None,
    started: datetime | None = None,
    tool_name: str = "read_file",
    interaction_id: str | None = None,
) -> ToolAuditEvent:
    event_started = started or datetime(2026, 8, 1, tzinfo=UTC)
    return ToolAuditEvent(
        request_id="req-1",
        session_id="default",
        tool_name=tool_name,
        permission=ToolPermission.READ_ONLY,
        decision=decision,
        status=status,
        workspace_id="workspace",
        argument_summary=argument_summary or {"path": "notes.txt"},
        started_at=event_started,
        ended_at=event_started + timedelta(milliseconds=5),
        duration_ms=5,
        denial_reason="denied" if decision == PolicyDecisionKind.DENY else None,
        error_code="error" if status == ToolExecutionStatus.ERROR else None,
        artifact_ids=("artifact-1",),
        interaction_id=interaction_id,
    )


def _rows(database: Path) -> list[sqlite3.Row]:
    with sqlite3.connect(database) as connection:
        connection.row_factory = sqlite3.Row
        return list(connection.execute("SELECT * FROM tool_audit_events"))
