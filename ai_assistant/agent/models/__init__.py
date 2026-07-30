"""Compatibility exports for model provider adapters."""

from ai_assistant.infrastructure.models import (
    DummyModel,
    ModelAdapter,
    ModelAdapterConfig,
    ModelProvider,
    OllamaModelProvider,
    OpenAICompatibleModel,
)

__all__ = [
    "DummyModel",
    "ModelAdapter",
    "ModelAdapterConfig",
    "ModelProvider",
    "OllamaModelProvider",
    "OpenAICompatibleModel",
]
