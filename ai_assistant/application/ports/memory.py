"""Conversation memory port."""

from abc import ABC, abstractmethod

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
    def append_many(self, session_id: SessionId, messages: list[Message]) -> None:
        raise NotImplementedError

    @abstractmethod
    def history(self, session_id: SessionId) -> list[Message]:
        raise NotImplementedError
