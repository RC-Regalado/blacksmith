"""Conversation memory interfaces and implementations."""

from dataclasses import replace

from ai_assistant.application.ports.memory import (
    DEFAULT_SESSION_ID,
    ConversationMemory,
    SessionId,
    validate_session_id,
)
from ai_assistant.agent.message import Message


class InMemoryConversationStore(ConversationMemory):
    def __init__(self) -> None:
        self._messages: list[Message] = []

    def append(self, session_id: SessionId, message: Message) -> None:
        self.append_many(session_id, [message])

    def append_many(self, session_id: SessionId, messages: list[Message]) -> None:
        session_id = validate_session_id(session_id)
        staged = [replace(message, session_id=session_id) for message in messages]
        self._messages.extend(staged)

    def history(self, session_id: SessionId) -> list[Message]:
        session_id = validate_session_id(session_id)
        return [
            message for message in self._messages if message.session_id == session_id
        ]
