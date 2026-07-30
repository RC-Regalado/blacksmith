"""Tests for model adapter provider selection."""

import pytest

from ai_assistant.application.errors import ConfigurationError
from ai_assistant.agent.message import Message
from ai_assistant.agent.models.adapter import ModelAdapter, ModelAdapterConfig
from ai_assistant.agent.models.ollama import OllamaModelProvider
from ai_assistant.agent.models.openai_compatible import OpenAICompatibleModel


pytestmark = pytest.mark.unit


def test_dummy_provider_delegates_to_dummy_model() -> None:
    adapter = ModelAdapter.from_config(ModelAdapterConfig(provider="dummy"))

    response = adapter.chat([Message(role="user", content="hola")])

    assert adapter.provider_name == "dummy"
    assert response == Message(role="assistant", content="Echo: hola")


def test_openai_provider_can_be_constructed_without_api_key() -> None:
    adapter = ModelAdapter.from_config(ModelAdapterConfig(provider="openai"))

    assert adapter.provider_name == "openai"


def test_chatgpt_alias_uses_openai_compatible_provider() -> None:
    adapter = ModelAdapter.from_config(ModelAdapterConfig(provider="chatgpt"))

    assert adapter.provider_name == "chatgpt"
    assert isinstance(adapter._provider, OpenAICompatibleModel)


def test_ollama_provider_can_be_constructed() -> None:
    adapter = ModelAdapter.from_config(ModelAdapterConfig(provider="ollama"))

    assert adapter.provider_name == "ollama"
    assert isinstance(adapter._provider, OllamaModelProvider)


def test_unknown_provider_fails_explicitly() -> None:
    with pytest.raises(ConfigurationError, match="Unsupported model provider"):
        ModelAdapter.from_config(ModelAdapterConfig(provider="unknown"))


def test_build_payload_separates_system_instructions() -> None:
    model = OpenAICompatibleModel(model="gpt-5", api_key="test-key")

    payload = model._build_payload(
        [
            Message(role="system", content="Sistema"),
            Message(role="user", content="Hola"),
        ]
    )

    assert payload["instructions"] == "Sistema"
    assert payload["input"][0]["role"] == "user"
    assert payload["input"][0]["content"] == "Hola"


def test_extract_text_reads_responses_output() -> None:
    model = OpenAICompatibleModel(model="gpt-5", api_key="test-key")

    text = model._extract_text(
        {
            "output": [
                {
                    "type": "message",
                    "content": [{"type": "output_text", "text": "Listo"}],
                }
            ]
        }
    )

    assert text == "Listo"
