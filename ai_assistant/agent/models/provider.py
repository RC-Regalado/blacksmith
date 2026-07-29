"""Model provider interface."""

from abc import ABC, abstractmethod

from ai_assistant.agent.message import Message


class ModelProvider(ABC):
    @abstractmethod
    def chat(self, messages: list[Message]) -> Message:
        raise NotImplementedError

