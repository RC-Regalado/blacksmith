"""Tests for the Phase 1 agent runtime and memory stores."""

import tempfile
import unittest
from pathlib import Path

from ai_assistant.agent.context import ContextBuilder
from ai_assistant.agent.memory import InMemoryConversationStore
from ai_assistant.agent.message import Message
from ai_assistant.agent.models.dummy import DummyModel
from ai_assistant.agent.planner import ToolCallDetector
from ai_assistant.agent.runtime import AgentRuntime
from ai_assistant.storage.sqlite_memory import SQLiteConversationStore


class AgentRuntimeTests(unittest.TestCase):
    def test_runtime_persists_user_and_assistant_turn(self) -> None:
        memory = InMemoryConversationStore()
        runtime = AgentRuntime(
            context_builder=ContextBuilder(system_prompt="System prompt"),
            memory=memory,
            model=DummyModel(),
            tool_detector=ToolCallDetector(),
        )

        response = runtime.respond("Hello")

        self.assertEqual(response, Message(role="assistant", content="Echo: Hello"))
        self.assertEqual(
            memory.history(),
            [
                Message(role="user", content="Hello"),
                Message(role="assistant", content="Echo: Hello"),
            ],
        )

    def test_context_builder_merges_system_history_and_user_input(self) -> None:
        builder = ContextBuilder(system_prompt="System prompt")
        history = [Message(role="assistant", content="Prior response")]

        context = builder.build(history=history, user_input="Next")

        self.assertEqual(
            context,
            [
                Message(role="system", content="System prompt"),
                Message(role="assistant", content="Prior response"),
                Message(role="user", content="Next"),
            ],
        )


class SQLiteConversationStoreTests(unittest.TestCase):
    def test_sqlite_store_persists_messages_in_order(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "assistant.sqlite3"
            store = SQLiteConversationStore(database_path)
            store.append(Message(role="user", content="Hello"))
            store.append(Message(role="assistant", content="Echo: Hello"))

            restored = SQLiteConversationStore(database_path)
            self.assertEqual(
                restored.history(),
                [
                    Message(role="user", content="Hello"),
                    Message(role="assistant", content="Echo: Hello"),
                ],
            )


if __name__ == "__main__":
    unittest.main()
