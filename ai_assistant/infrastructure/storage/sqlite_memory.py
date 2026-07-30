"""SQLite-backed conversation memory."""

import sqlite3
from pathlib import Path

from ai_assistant.application.ports.memory import ConversationMemory
from ai_assistant.domain.errors import ConversationStoreError
from ai_assistant.domain.message import Message, Role
from ai_assistant.domain.session import DEFAULT_SESSION_ID, SessionId, validate_session_id


class SQLiteConversationStore(ConversationMemory):
    def __init__(self, database_path: str | Path) -> None:
        self._database_path = Path(database_path)
        self._initialize()

    def append(self, session_id: SessionId, message: Message) -> None:
        self.append_many(session_id, [message])

    def append_many(self, session_id: SessionId, messages: list[Message]) -> None:
        session_id = validate_session_id(session_id)
        try:
            with self._connect() as connection:
                connection.executemany(
                    """
                    INSERT INTO messages (session_id, role, content)
                    VALUES (?, ?, ?)
                    """,
                    [(session_id, message.role, message.content) for message in messages],
                )
        except sqlite3.Error as exc:
            raise ConversationStoreError("Failed to persist conversation turn.") from exc

    def history(self, session_id: SessionId) -> list[Message]:
        session_id = validate_session_id(session_id)
        try:
            with self._connect() as connection:
                rows = connection.execute(
                    """
                    SELECT session_id, role, content
                    FROM messages
                    WHERE session_id = ?
                    ORDER BY id ASC
                    """,
                    (session_id,),
                ).fetchall()
        except sqlite3.Error as exc:
            raise ConversationStoreError("Failed to load conversation history.") from exc
        return [
            Message(session_id=row[0], role=self._role(row[1]), content=row[2])
            for row in rows
        ]

    def _initialize(self) -> None:
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with self._connect() as connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL DEFAULT 'default',
                        role TEXT NOT NULL
                            CHECK (role IN ('system', 'user', 'assistant', 'tool')),
                        content TEXT NOT NULL,
                        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                self._ensure_session_column(connection)
                connection.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_messages_session_id_id
                    ON messages (session_id, id)
                    """
                )
        except sqlite3.Error as exc:
            raise ConversationStoreError("Failed to initialize conversation store.") from exc

    def _ensure_session_column(self, connection: sqlite3.Connection) -> None:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(messages)")}
        if "session_id" not in columns:
            connection.execute(
                "ALTER TABLE messages ADD COLUMN session_id TEXT "
                f"NOT NULL DEFAULT '{DEFAULT_SESSION_ID}'"
            )

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._database_path)

    def _role(self, value: str) -> Role:
        if value not in {"system", "user", "assistant", "tool"}:
            raise ConversationStoreError(f"Invalid role stored in SQLite: {value}")
        return value  # type: ignore[return-value]
