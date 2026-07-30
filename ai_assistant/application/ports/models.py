"""Model provider port."""

from abc import ABC, abstractmethod

from ai_assistant.domain.message import Message


class ModelProvider(ABC):
    @abstractmethod
    def chat(self, messages: list[Message]) -> Message:
        raise NotImplementedError
