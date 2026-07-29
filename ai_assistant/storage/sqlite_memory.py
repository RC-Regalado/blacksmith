"""SQLite-backed conversation memory."""

import sqlite3
from pathlib import Path

from ai_assistant.agent.memory import ConversationMemory
from ai_assistant.agent.message import Message, Role


class SQLiteConversationStore(ConversationMemory):
    def __init__(self, database_path: str | Path) -> None:
        self._database_path = Path(database_path)
        self._initialize()

    def append(self, message: Message) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO messages (role, content) VALUES (?, ?)",
                (message.role, message.content),
            )

    def history(self) -> list[Message]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT role, content FROM messages ORDER BY id ASC"
            ).fetchall()
        return [Message(role=self._role(row[0]), content=row[1]) for row in rows]

    def _initialize(self) -> None:
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._database_path)

    def _role(self, value: str) -> Role:
        if value not in {"system", "user", "assistant", "tool"}:
            raise ValueError(f"Invalid role stored in SQLite: {value}")
        return value  # type: ignore[return-value]

