"""Model provider adapters."""

from ai_assistant.application.ports.models import ModelProvider
from ai_assistant.infrastructure.models.adapter import ModelAdapter, ModelAdapterConfig
from ai_assistant.infrastructure.models.dummy import DummyModel
from ai_assistant.infrastructure.models.ollama import OllamaModelProvider
from ai_assistant.infrastructure.models.openai_compatible import OpenAICompatibleModel

__all__ = [
    "DummyModel",
    "ModelAdapter",
    "ModelAdapterConfig",
    "ModelProvider",
    "OllamaModelProvider",
    "OpenAICompatibleModel",
]
