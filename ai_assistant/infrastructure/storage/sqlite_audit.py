"""SQLite-backed tool audit recorder."""

import json
import sqlite3
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

from ai_assistant.application.ports.tools import AuditRecorder
from ai_assistant.domain.errors import ToolAuditStoreError
from ai_assistant.domain.tools import ToolAuditEvent
from ai_assistant.infrastructure.sanitization import redact_sensitive

@dataclass(frozen=True, slots=True)
class AuditPurgeResult:
    deleted_count: int
    oldest_started_at: str | None
    newest_started_at: str | None
    dry_run: bool


_RETENTION_DAYS = {
    "metadata_search": 30,
    "git_inspection": 90,
    "test_build": 90,
    "write": 365,
    "security_denial": 365,
    "critical_error": 365,
}


class SQLiteAuditRecorder(AuditRecorder):
    def __init__(self, database_path: str | Path) -> None:
        self._database_path = Path(database_path)
        self._initialize()

    def record(self, event: ToolAuditEvent) -> None:
        try:
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT INTO tool_audit_events (
                        request_id, session_id, tool_name, permission, decision,
                        status, workspace_id, argument_summary, started_at, ended_at,
                        duration_ms, dry_run, denial_reason, error_code, artifact_ids
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    _row(event),
                )
        except sqlite3.Error as exc:
            raise ToolAuditStoreError("Failed to persist tool audit event.") from exc

    def purge_expired(
        self,
        *,
        dry_run: bool = True,
        confirm: bool = False,
        now: datetime | None = None,
    ) -> AuditPurgeResult:
        if not dry_run and not confirm:
            raise ToolAuditStoreError("Audit purge requires explicit confirmation.")
        current = now or datetime.now(UTC)
        try:
            with self._connect() as connection:
                rows = list(
                    connection.execute(
                        """
                        SELECT id, tool_name, decision, status, started_at
                        FROM tool_audit_events
                        WHERE tool_name != 'audit_purge'
                        """
                    )
                )
                expired = _expired_rows(rows, current)
                result = _purge_result(expired, dry_run)
                if not dry_run:
                    if expired:
                        connection.executemany(
                            "DELETE FROM tool_audit_events WHERE id = ?",
                            [(row[0],) for row in expired],
                        )
                    connection.execute(
                        """
                        INSERT INTO tool_audit_events (
                            request_id, session_id, tool_name, permission, decision,
                            status, workspace_id, argument_summary, started_at, ended_at,
                            duration_ms, dry_run, denial_reason, error_code, artifact_ids
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        _purge_row(result, current),
                    )
                return result
        except sqlite3.Error as exc:
            raise ToolAuditStoreError("Failed to purge audit events.") from exc

    def _initialize(self) -> None:
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with self._connect() as connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS tool_audit_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        request_id TEXT NOT NULL,
                        session_id TEXT NOT NULL,
                        tool_name TEXT NOT NULL,
                        permission TEXT NOT NULL,
                        decision TEXT NOT NULL,
                        status TEXT NOT NULL,
                        workspace_id TEXT NOT NULL,
                        argument_summary TEXT NOT NULL,
                        started_at TEXT NOT NULL,
                        ended_at TEXT NOT NULL,
                        duration_ms REAL NOT NULL,
                        dry_run INTEGER NOT NULL,
                        denial_reason TEXT,
                        error_code TEXT,
                        artifact_ids TEXT NOT NULL,
                        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
        except sqlite3.Error as exc:
            raise ToolAuditStoreError("Failed to initialize tool audit store.") from exc

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._database_path)


def _row(event: ToolAuditEvent) -> tuple[object, ...]:
    return (
        event.request_id,
        event.session_id,
        event.tool_name,
        event.permission.value,
        event.decision.value,
        event.status.value,
        event.workspace_id,
        json.dumps(redact_sensitive(event.argument_summary), sort_keys=True),
        event.started_at.isoformat(),
        event.ended_at.isoformat(),
        event.duration_ms,
        int(event.dry_run),
        event.denial_reason,
        event.error_code,
        json.dumps(list(event.artifact_ids), sort_keys=True),
    )

def _expired_rows(
    rows: list[sqlite3.Row | tuple[object, ...]],
    now: datetime,
) -> list[sqlite3.Row | tuple[object, ...]]:
    expired: list[sqlite3.Row | tuple[object, ...]] = []
    for row in rows:
        started = datetime.fromisoformat(str(row[4]))
        retention = _retention_days(str(row[1]), str(row[2]), str(row[3]))
        if now - started >= timedelta(days=retention):
            expired.append(row)
    return expired


def _retention_days(tool_name: str, decision: str, status: str) -> int:
    if status == "error":
        return _RETENTION_DAYS["critical_error"]
    if decision == "deny" or status == "denied":
        return _RETENTION_DAYS["security_denial"]
    if tool_name in {"git_status", "git_diff"}:
        return _RETENTION_DAYS["git_inspection"]
    if tool_name in {"run_tests", "build_project"}:
        return _RETENTION_DAYS["test_build"]
    if tool_name == "write":
        return _RETENTION_DAYS["write"]
    return _RETENTION_DAYS["metadata_search"]


def _purge_result(
    rows: list[sqlite3.Row | tuple[object, ...]],
    dry_run: bool,
) -> AuditPurgeResult:
    dates = [str(row[4]) for row in rows]
    return AuditPurgeResult(
        deleted_count=len(rows),
        oldest_started_at=min(dates) if dates else None,
        newest_started_at=max(dates) if dates else None,
        dry_run=dry_run,
    )


def _purge_row(result: AuditPurgeResult, now: datetime) -> tuple[object, ...]:
    return (
        "audit-purge",
        "operator",
        "audit_purge",
        "read_only",
        "allow",
        "success",
        "audit",
        json.dumps(
            {
                "deleted_count": result.deleted_count,
                "oldest_started_at": result.oldest_started_at,
                "newest_started_at": result.newest_started_at,
            },
            sort_keys=True,
        ),
        now.isoformat(),
        now.isoformat(),
        0,
        0,
        None,
        None,
        "[]",
    )
