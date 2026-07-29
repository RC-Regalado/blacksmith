"""Conversation memory interfaces and implementations."""

from abc import ABC, abstractmethod
from dataclasses import replace

from ai_assistant.agent.message import Message


SessionId = str
DEFAULT_SESSION_ID: SessionId = "default"


def validate_session_id(session_id: SessionId) -> SessionId:
    if not session_id.strip():
        raise ValueError("Session ID cannot be empty.")
    return session_id


class ConversationMemory(ABC):
    @abstractmethod
    def append(self, session_id: SessionId, message: Message) -> None:
        raise NotImplementedError

    @abstractmethod
    def history(self, session_id: SessionId) -> list[Message]:
        raise NotImplementedError


class InMemoryConversationStore(ConversationMemory):
    def __init__(self) -> None:
        self._messages: list[Message] = []

    def append(self, session_id: SessionId, message: Message) -> None:
        session_id = validate_session_id(session_id)
        self._messages.append(replace(message, session_id=session_id))

    def history(self, session_id: SessionId) -> list[Message]:
        session_id = validate_session_id(session_id)
        return [
            message for message in self._messages if message.session_id == session_id
        ]
