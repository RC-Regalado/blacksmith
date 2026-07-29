"""Tests for the Phase 1 agent runtime and memory stores."""

import sqlite3
from pathlib import Path

import pytest

from ai_assistant.agent.context import ContextBuilder
from ai_assistant.agent.memory import DEFAULT_SESSION_ID, InMemoryConversationStore
from ai_assistant.agent.message import Message
from ai_assistant.agent.models.dummy import DummyModel
from ai_assistant.agent.planner import ToolCallDetector
from ai_assistant.agent.runtime import AgentRuntime
from ai_assistant.storage.sqlite_memory import SQLiteConversationStore


pytestmark = pytest.mark.unit


def test_runtime_persists_user_and_assistant_turn() -> None:
    memory = InMemoryConversationStore()
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="System prompt"),
        memory=memory,
        model=DummyModel(),
        tool_detector=ToolCallDetector(),
        session_id="alpha",
    )

    response = runtime.respond("Hello")

    assert response == Message(role="assistant", content="Echo: Hello")
    assert memory.history("alpha") == [
        Message(role="user", content="Hello", session_id="alpha"),
        Message(role="assistant", content="Echo: Hello", session_id="alpha"),
    ]
    assert memory.history("beta") == []


def test_in_memory_store_isolates_sessions() -> None:
    memory = InMemoryConversationStore()

    memory.append("alpha", Message(role="user", content="A"))
    memory.append("beta", Message(role="user", content="B"))

    assert memory.history("alpha") == [
        Message(role="user", content="A", session_id="alpha")
    ]
    assert memory.history("beta") == [
        Message(role="user", content="B", session_id="beta")
    ]


def test_context_builder_merges_system_history_and_user_input() -> None:
    builder = ContextBuilder(system_prompt="System prompt")
    history = [Message(role="assistant", content="Prior response")]

    context = builder.build(history=history, user_input="Next")

    assert context == [
        Message(role="system", content="System prompt"),
        Message(role="assistant", content="Prior response"),
        Message(role="user", content="Next"),
    ]


def test_sqlite_store_persists_messages_in_order(tmp_path: Path) -> None:
    database_path = tmp_path / "assistant.sqlite3"
    store = SQLiteConversationStore(database_path)
    store.append("alpha", Message(role="user", content="Hello"))
    store.append("alpha", Message(role="assistant", content="Echo: Hello"))

    restored = SQLiteConversationStore(database_path)

    assert restored.history("alpha") == [
        Message(role="user", content="Hello", session_id="alpha"),
        Message(role="assistant", content="Echo: Hello", session_id="alpha"),
    ]


def test_sqlite_store_isolates_sessions(tmp_path: Path) -> None:
    store = SQLiteConversationStore(tmp_path / "assistant.sqlite3")

    store.append("alpha", Message(role="user", content="A"))
    store.append("beta", Message(role="user", content="B"))

    assert store.history("alpha") == [
        Message(role="user", content="A", session_id="alpha")
    ]
    assert store.history("beta") == [
        Message(role="user", content="B", session_id="beta")
    ]


def test_sqlite_store_migrates_existing_rows_to_default_session(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "assistant.sqlite3"
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            "INSERT INTO messages (role, content) VALUES (?, ?)",
            ("user", "Legacy"),
        )

    store = SQLiteConversationStore(database_path)

    assert store.history(DEFAULT_SESSION_ID) == [
        Message(role="user", content="Legacy", session_id=DEFAULT_SESSION_ID)
    ]
