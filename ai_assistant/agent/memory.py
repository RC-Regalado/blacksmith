"""Conversation memory interfaces and implementations."""

from abc import ABC, abstractmethod

from ai_assistant.agent.message import Message


class ConversationMemory(ABC):
    @abstractmethod
    def append(self, message: Message) -> None:
        raise NotImplementedError

    @abstractmethod
    def history(self) -> list[Message]:
        raise NotImplementedError


class InMemoryConversationStore(ConversationMemory):
    def __init__(self) -> None:
        self._messages: list[Message] = []

    def append(self, message: Message) -> None:
        self._messages.append(message)

    def history(self) -> list[Message]:
        return list(self._messages)

