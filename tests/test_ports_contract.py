"""Basic contract tests for application ports."""

import pytest

from ai_assistant.application.ports.memory import ConversationMemory, SessionId
from ai_assistant.application.ports.models import ModelProvider
from ai_assistant.agent.message import Message


pytestmark = pytest.mark.contract


def test_model_provider_contract_returns_message() -> None:
    provider: ModelProvider = ContractModel()

    response = provider.chat([Message(role="user", content="Hello")])

    assert response == Message(role="assistant", content="ok")


def test_conversation_memory_contract_preserves_messages() -> None:
    memory: ConversationMemory = ContractMemory()

    memory.append_many(
        "default",
        [
            Message(role="user", content="Hello"),
            Message(role="assistant", content="ok"),
        ],
    )

    assert memory.history("default") == [
        Message(role="user", content="Hello", session_id="default"),
        Message(role="assistant", content="ok", session_id="default"),
    ]


class ContractModel(ModelProvider):
    def chat(self, messages: list[Message]) -> Message:
        return Message(role="assistant", content="ok")


class ContractMemory(ConversationMemory):
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
