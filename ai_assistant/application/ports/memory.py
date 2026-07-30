"""Conversation memory port."""

from abc import ABC, abstractmethod

from ai_assistant.domain.message import Message
from ai_assistant.domain.session import DEFAULT_SESSION_ID, SessionId, validate_session_id


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
