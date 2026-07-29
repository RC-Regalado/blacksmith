"""Model provider adapters."""

from ai_assistant.agent.models.adapter import ModelAdapter, ModelAdapterConfig
from ai_assistant.agent.models.dummy import DummyModel
from ai_assistant.agent.models.openai_compatible import OpenAICompatibleModel
from ai_assistant.agent.models.provider import ModelProvider

__all__ = [
    "DummyModel",
    "ModelAdapter",
    "ModelAdapterConfig",
    "ModelProvider",
    "OpenAICompatibleModel",
]
