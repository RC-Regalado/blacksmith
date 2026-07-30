"""Compatibility exports for model adapter selection."""

from ai_assistant.infrastructure.models.adapter import (
    ModelAdapter,
    ModelAdapterConfig,
    ProviderFactory,
)

__all__ = ["ModelAdapter", "ModelAdapterConfig", "ProviderFactory"]
