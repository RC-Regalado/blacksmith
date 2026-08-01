"""SQLite-backed tool audit recorder."""

import json
import sqlite3
from collections.abc import Mapping
from pathlib import Path

from ai_assistant.application.ports.tools import AuditRecorder
from ai_assistant.domain.errors import ToolAuditStoreError
from ai_assistant.domain.tools import ToolAuditEvent

_REDACTED = "[redacted]"
_SENSITIVE_KEYS = {
    "api_key",
    "auth",
    "authorization",
    "content",
    "file_content",
    "password",
    "prompt",
    "response",
    "secret",
    "token",
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
        json.dumps(_redact(event.argument_summary), sort_keys=True),
        event.started_at.isoformat(),
        event.ended_at.isoformat(),
        event.duration_ms,
        int(event.dry_run),
        event.denial_reason,
        event.error_code,
        json.dumps(list(event.artifact_ids), sort_keys=True),
    )


def _redact(value: object) -> object:
    if isinstance(value, Mapping):
        return {
            str(key): _REDACTED if _is_sensitive(str(key)) else _redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list | tuple):
        return [_redact(item) for item in value]
    return value


def _is_sensitive(key: str) -> bool:
    normalized = key.lower()
    return any(part in normalized for part in _SENSITIVE_KEYS)
