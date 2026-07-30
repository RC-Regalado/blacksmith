"""Model adapter service for selecting concrete model providers."""

import os
from collections.abc import Callable, Mapping
from dataclasses import dataclass

from ai_assistant.application.ports.models import ModelProvider
from ai_assistant.agent.message import Message
from ai_assistant.agent.models.dummy import DummyModel
from ai_assistant.agent.models.openai_compatible import OpenAICompatibleModel


ProviderFactory = Callable[["ModelAdapterConfig"], ModelProvider]


@dataclass(frozen=True, slots=True)
class ModelAdapterConfig:
    provider: str = "dummy"
    model: str = "gpt-5"
    base_url: str = "https://api.openai.com/v1"
    api_key: str | None = None
    timeout_seconds: float = 60.0


class ModelAdapter(ModelProvider):
    def __init__(self, provider_name: str, provider: ModelProvider) -> None:
        self.provider_name = provider_name
        self._provider = provider

    @classmethod
    def from_env(cls) -> "ModelAdapter":
        config = ModelAdapterConfig(
            provider=os.getenv("AI_ASSISTANT_MODEL_PROVIDER", "dummy"),
            model=os.getenv("AI_ASSISTANT_MODEL", "gpt-5"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        return cls.from_config(config)

    @classmethod
    def from_config(
        cls,
        config: ModelAdapterConfig,
        factories: Mapping[str, ProviderFactory] | None = None,
    ) -> "ModelAdapter":
        provider_key = config.provider.strip().lower()
        available_factories = factories or cls._default_factories()
        if provider_key not in available_factories:
            raise ValueError(f"Unsupported model provider: {config.provider}")
        provider = available_factories[provider_key](config)
        return cls(provider_name=provider_key, provider=provider)

    def chat(self, messages: list[Message]) -> Message:
        return self._provider.chat(messages)

    @staticmethod
    def _default_factories() -> dict[str, ProviderFactory]:
        return {
            "dummy": lambda _config: DummyModel(),
            "openai": _build_openai_provider,
            "chatgpt": _build_openai_provider,
        }


def _build_openai_provider(config: ModelAdapterConfig) -> ModelProvider:
    return OpenAICompatibleModel(
        model=config.model,
        api_key=config.api_key,
        base_url=config.base_url,
        timeout_seconds=config.timeout_seconds,
    )
