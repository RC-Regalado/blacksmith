"""Model provider port."""

from abc import ABC, abstractmethod

from ai_assistant.domain.message import Message
from ai_assistant.domain.model_response import ModelResponse


class ModelProvider(ABC):
    @abstractmethod
    def chat(self, messages: list[Message]) -> ModelResponse:
        raise NotImplementedError
