"""Model adapter service for selecting concrete model providers."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass
import logging

from ai_assistant.application.ports.models import ModelProvider
from ai_assistant.domain.errors import ConfigurationError
from ai_assistant.domain.message import Message
from ai_assistant.domain.model_response import ModelResponse
from ai_assistant.infrastructure.models.dummy import DummyModel
from ai_assistant.infrastructure.models.ollama import OllamaModelProvider
from ai_assistant.infrastructure.models.openai_compatible import OpenAICompatibleModel


ProviderFactory = Callable[["ModelAdapterConfig"], ModelProvider]
logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ModelAdapterConfig:
    provider: str = "dummy"
    model: str = ""
    base_url: str = "https://api.openai.com/v1"
    api_key: str | None = None
    timeout_seconds: float = 60.0
    ollama_num_ctx: int | None = None
    ollama_num_predict: int | None = None


class ModelAdapter(ModelProvider):
    def __init__(self, provider_name: str, provider: ModelProvider) -> None:
        self.provider_name = provider_name
        self._provider = provider

    @classmethod
    def from_config(
        cls,
        config: ModelAdapterConfig,
        factories: Mapping[str, ProviderFactory] | None = None,
    ) -> "ModelAdapter":
        provider_key = config.provider.strip().lower()
        available_factories = factories or cls._default_factories()
        if provider_key not in available_factories:
            raise ConfigurationError(f"Unsupported model provider: {config.provider}")
        provider = available_factories[provider_key](config)
        logger.info(
            "model provider selected provider=%s model=%s",
            provider_key,
            config.model,
        )
        return cls(provider_name=provider_key, provider=provider)

    def chat(self, messages: list[Message]) -> ModelResponse:
        return self._provider.chat(messages)

    @staticmethod
    def _default_factories() -> dict[str, ProviderFactory]:
        return {
            "dummy": lambda _config: DummyModel(),
            "ollama": _build_ollama_provider,
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


def _build_ollama_provider(config: ModelAdapterConfig) -> ModelProvider:
    return OllamaModelProvider(
        model=config.model,
        base_url=config.base_url,
        timeout_seconds=config.timeout_seconds,
        num_ctx=config.ollama_num_ctx,
        num_predict=config.ollama_num_predict,
    )
