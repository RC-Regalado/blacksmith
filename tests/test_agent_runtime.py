"""Tests for the Phase 1 agent runtime."""

import pytest

from ai_assistant.agent.context import ContextBuilder
from ai_assistant.application.ports.memory import (
    ConversationMemory,
    SessionId,
)
from ai_assistant.application.ports.models import ModelProvider
from ai_assistant.agent.message import Message
from ai_assistant.agent.planner import ToolCallDetector
from ai_assistant.agent.runtime import AgentRuntime


pytestmark = pytest.mark.unit


def test_runtime_persists_user_and_assistant_turn() -> None:
    memory = FakeConversationStore()
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="System prompt"),
        memory=memory,
        model=FakeModel("Echo: Hello"),
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


def test_runtime_persists_complete_turn_atomically() -> None:
    memory = FailingTurnStore()
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="System prompt"),
        memory=memory,
        model=FakeModel("Echo: Hello"),
        tool_detector=ToolCallDetector(),
        session_id="alpha",
    )

    with pytest.raises(RuntimeError, match="store failed"):
        runtime.respond("Hello")

    assert memory.history("alpha") == []


def test_context_builder_merges_system_history_and_user_input() -> None:
    builder = ContextBuilder(system_prompt="System prompt")
    history = [Message(role="assistant", content="Prior response")]

    context = builder.build(history=history, user_input="Next")

    assert context == [
        Message(role="system", content="System prompt"),
        Message(role="assistant", content="Prior response"),
        Message(role="user", content="Next"),
    ]


def test_context_builder_prefers_recent_history_within_budget() -> None:
    builder = ContextBuilder(system_prompt="S", context_limit=9)
    history = [
        Message(role="user", content="old"),
        Message(role="assistant", content="mid"),
        Message(role="assistant", content="new"),
    ]

    context = builder.build(history=history, user_input="U")

    assert context == [
        Message(role="system", content="S"),
        Message(role="assistant", content="mid"),
        Message(role="assistant", content="new"),
        Message(role="user", content="U"),
    ]


def test_context_builder_preserves_system_and_current_input_when_over_budget() -> None:
    builder = ContextBuilder(system_prompt="system", context_limit=1)

    context = builder.build(
        history=[Message(role="assistant", content="history")],
        user_input="current",
    )

    assert context == [
        Message(role="system", content="system"),
        Message(role="user", content="current"),
    ]


def test_runtime_stores_tool_call_plan_without_execution() -> None:
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="System prompt"),
        memory=FakeConversationStore(),
        model=FakeModel('{"tool_call":{"name":"search","arguments":{"q":"x"}}}'),
        tool_detector=ToolCallDetector(),
        session_id="alpha",
    )

    runtime.respond("Hello")

    assert runtime.last_tool_plan.has_tool_call is True
    assert runtime.last_tool_plan.tool_name == "search"


class FailingTurnStore(ConversationMemory):
    def __init__(self) -> None:
        self._messages: list[Message] = []

    def append(self, session_id: SessionId, message: Message) -> None:
        self.append_many(session_id, [message])

    def append_many(self, session_id: SessionId, messages: list[Message]) -> None:
        raise RuntimeError("store failed")

    def history(self, session_id: SessionId) -> list[Message]:
        return list(self._messages)


class FakeConversationStore(ConversationMemory):
    def __init__(self) -> None:
        self._messages: list[Message] = []

    def append(self, session_id: SessionId, message: Message) -> None:
        self.append_many(session_id, [message])

    def append_many(self, session_id: SessionId, messages: list[Message]) -> None:
        self._messages.extend(
            Message(role=message.role, content=message.content, session_id=session_id)
            for message in messages
        )

    def history(self, session_id: SessionId) -> list[Message]:
        return [
            message for message in self._messages if message.session_id == session_id
        ]


class FakeModel(ModelProvider):
    def __init__(self, response: str) -> None:
        self._response = response

    def chat(self, messages: list[Message]) -> Message:
        return Message(role="assistant", content=self._response)
