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
            "AI_ASSISTANT_EXECUTION_DATABASE": "execution.sqlite3",
            "AI_ASSISTANT_KNOWLEDGE_DATABASE": "knowledge.sqlite3",
            "AI_ASSISTANT_SESSION": "test-session",
            "AI_ASSISTANT_SYSTEM_PROMPT": "system",
            "AI_ASSISTANT_LOG_LEVEL": "debug",
            "AI_ASSISTANT_REQUEST_TIMEOUT": "2.5",
            "AI_ASSISTANT_CONTEXT_LIMIT": "128",
            "AI_ASSISTANT_WORKSPACE": " /tmp/workspace ",
            "AI_ASSISTANT_TOOL_EXECUTION": "yes",
            "AI_ASSISTANT_TOOL_TIMEOUT": "4.5",
            "AI_ASSISTANT_MAX_READ_BYTES": "2048",
            "AI_ASSISTANT_MAX_DIRECTORY_ENTRIES": "25",
            "AI_ASSISTANT_MAX_DIRECTORY_DEPTH": "2",
            "AI_ASSISTANT_AUDIT_DATABASE": "audit.sqlite3",
            "AI_ASSISTANT_AUDIT_AUTO_PURGE": "true",
            "AI_ASSISTANT_TOOL_EXECUTOR": "local",
            "AI_ASSISTANT_TOOL_SOCKET": "/tmp/tool.sock",
            "OPENAI_API_KEY": "secret",
        }
    )

    assert config.provider == "openai"
    assert config.model == "test-model"
    assert config.base_url == "http://example.test/v1"
    assert config.database == "test.sqlite3"
    assert config.execution_database == "execution.sqlite3"
    assert config.knowledge_database == "knowledge.sqlite3"
    assert config.session == "test-session"
    assert config.system_prompt == "system"
    assert config.log_level == "DEBUG"
    assert config.request_timeout == 2.5
    assert config.context_limit == 128
    assert config.workspace == "/tmp/workspace"
    assert config.tool_execution is True
    assert config.tool_timeout == 4.5
    assert config.max_read_bytes == 2048
    assert config.max_directory_entries == 25
    assert config.max_directory_depth == 2
    assert config.audit_database == "audit.sqlite3"
    assert config.audit_auto_purge is True
    assert config.tool_executor == "local"
    assert config.tool_socket == "/tmp/tool.sock"
    assert config.api_key == "secret"


def test_ollama_provider_defaults_to_local_base_url() -> None:
    config = load_app_config({"AI_ASSISTANT_PROVIDER": "ollama"})

    assert config.provider == "ollama"
    assert config.base_url == "http://localhost:11434"


def test_context_limit_allows_8192() -> None:
    config = load_app_config({"AI_ASSISTANT_CONTEXT_LIMIT": "8192"})

    assert config.context_limit == 8192


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


def test_invalid_tool_execution_flag_fails_clearly() -> None:
    with pytest.raises(ConfigurationError, match="AI_ASSISTANT_TOOL_EXECUTION"):
        load_app_config({"AI_ASSISTANT_TOOL_EXECUTION": "maybe"})


def test_invalid_tool_executor_fails_clearly() -> None:
    with pytest.raises(ConfigurationError, match="AI_ASSISTANT_TOOL_EXECUTOR"):
        load_app_config({"AI_ASSISTANT_TOOL_EXECUTOR": "python_fallback"})


def test_invalid_tool_limits_fail_clearly() -> None:
    with pytest.raises(ConfigurationError, match="AI_ASSISTANT_MAX_DIRECTORY_DEPTH"):
        load_app_config({"AI_ASSISTANT_MAX_DIRECTORY_DEPTH": "-1"})
