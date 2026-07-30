"""Tests for bootstrap configuration."""

from dataclasses import FrozenInstanceError

import pytest

from ai_assistant.application.errors import ConfigurationError
from ai_assistant.bootstrap.config import AppConfig, load_app_config


pytestmark = pytest.mark.unit


def test_app_config_defaults_are_explicit() -> None:
    config = load_app_config({})

    assert config == AppConfig()


def test_app_config_is_immutable() -> None:
    config = AppConfig()

    with pytest.raises(FrozenInstanceError):
        config.provider = "openai"  # type: ignore[misc]


def test_load_app_config_reads_supported_environment_values() -> None:
    config = load_app_config(
        {
            "AI_ASSISTANT_PROVIDER": "OPENAI",
            "AI_ASSISTANT_MODEL": "test-model",
            "AI_ASSISTANT_BASE_URL": "http://example.test/v1",
            "AI_ASSISTANT_DATABASE": "test.sqlite3",
            "AI_ASSISTANT_SESSION": "test-session",
            "AI_ASSISTANT_SYSTEM_PROMPT": "system",
            "AI_ASSISTANT_LOG_LEVEL": "debug",
            "AI_ASSISTANT_REQUEST_TIMEOUT": "2.5",
            "AI_ASSISTANT_CONTEXT_LIMIT": "128",
            "OPENAI_API_KEY": "secret",
        }
    )

    assert config.provider == "openai"
    assert config.model == "test-model"
    assert config.base_url == "http://example.test/v1"
    assert config.database == "test.sqlite3"
    assert config.session == "test-session"
    assert config.system_prompt == "system"
    assert config.log_level == "DEBUG"
    assert config.request_timeout == 2.5
    assert config.context_limit == 128
    assert config.api_key == "secret"


def test_ollama_provider_defaults_to_local_base_url() -> None:
    config = load_app_config({"AI_ASSISTANT_PROVIDER": "ollama"})

    assert config.provider == "ollama"
    assert config.base_url == "http://localhost:11434"


def test_app_config_repr_hides_api_key() -> None:
    assert "secret" not in repr(AppConfig(api_key="secret"))


def test_invalid_provider_fails_clearly() -> None:
    with pytest.raises(ConfigurationError, match="Unsupported AI_ASSISTANT_PROVIDER"):
        load_app_config({"AI_ASSISTANT_PROVIDER": "bad"})


def test_invalid_timeout_fails_clearly() -> None:
    with pytest.raises(ConfigurationError, match="AI_ASSISTANT_REQUEST_TIMEOUT"):
        load_app_config({"AI_ASSISTANT_REQUEST_TIMEOUT": "0"})


def test_invalid_context_limit_fails_clearly() -> None:
    with pytest.raises(ConfigurationError, match="AI_ASSISTANT_CONTEXT_LIMIT"):
        load_app_config({"AI_ASSISTANT_CONTEXT_LIMIT": "nope"})
