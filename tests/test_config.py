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
            "AI_ASSISTANT_MODEL_CONTEXT_WINDOW": "128",
            "AI_ASSISTANT_MODEL_MAX_OUTPUT_TOKENS": "32",
            "AI_ASSISTANT_MODEL_CONTEXT_SAFETY_MARGIN": "8",
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
            "AI_ASSISTANT_TOOL_LOG_DIR": "/tmp/tool-logs",
            "AI_ASSISTANT_CONTEXT_ENGINE": "true",
            "AI_ASSISTANT_SHOW_METRICS": "true",
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
    assert config.model_context_window == 128
    assert config.model_max_output_tokens == 32
    assert config.model_context_safety_margin == 8
    assert config.model_input_budget == 88
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
    assert config.tool_log_dir == "/tmp/tool-logs"
    assert config.context_engine is True
    assert config.show_metrics is True
    assert config.api_key == "secret"


def test_ollama_provider_defaults_to_local_base_url() -> None:
    config = load_app_config({"AI_ASSISTANT_PROVIDER": "ollama"})

    assert config.provider == "ollama"
    assert config.base_url == "http://localhost:11434"
    assert config.model_context_window == 4096
    assert config.model_max_output_tokens == 2048
    assert config.model_context_safety_margin == 0


def test_ollama_budget_is_derived_from_provider_neutral_context_config() -> None:
    config = load_app_config(
        {
            "AI_ASSISTANT_PROVIDER": "ollama",
            "AI_ASSISTANT_MODEL_CONTEXT_WINDOW": "3072",
            "AI_ASSISTANT_MODEL_MAX_OUTPUT_TOKENS": "768",
        }
    )

    assert config.model_context_window == 3072
    assert config.model_max_output_tokens == 768


def test_default_reserved_output_budget_fits_small_context_window() -> None:
    config = load_app_config(
        {
            "AI_ASSISTANT_PROVIDER": "ollama",
            "AI_ASSISTANT_MODEL_CONTEXT_WINDOW": "128",
        }
    )

    assert config.model_max_output_tokens == 64
    assert config.model_input_budget == 64


def test_model_budget_uses_environment_over_dotenv(tmp_path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "AI_ASSISTANT_PROVIDER=ollama\n"
        "AI_ASSISTANT_MODEL_CONTEXT_WINDOW=1024\n"
        "AI_ASSISTANT_MODEL_MAX_OUTPUT_TOKENS=128\n",
        encoding="utf-8",
    )

    config = load_app_config(
        {"AI_ASSISTANT_MODEL_CONTEXT_WINDOW": "2048"},
        env_file=env_file,
    )

    assert config.provider == "ollama"
    assert config.model_context_window == 2048
    assert config.model_max_output_tokens == 128


def test_model_budget_loads_dotenv_when_no_process_override(tmp_path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "AI_ASSISTANT_PROVIDER=ollama\n"
        "AI_ASSISTANT_MODEL_CONTEXT_WINDOW=1536\n"
        "AI_ASSISTANT_MODEL_MAX_OUTPUT_TOKENS=256\n"
        "AI_ASSISTANT_MODEL_CONTEXT_SAFETY_MARGIN=32\n",
        encoding="utf-8",
    )

    config = load_app_config({}, env_file=env_file)

    assert config.model_context_window == 1536
    assert config.model_max_output_tokens == 256
    assert config.model_context_safety_margin == 32
    assert config.model_input_budget == 1248


def test_ollama_budget_rejects_impossible_generation_reserve() -> None:
    with pytest.raises(ConfigurationError, match="model_max_output_tokens"):
        AppConfig(provider="ollama", model_context_window=1024, model_max_output_tokens=1024)

    with pytest.raises(ConfigurationError, match="positive"):
        AppConfig(provider="ollama", model_context_window=1024, model_max_output_tokens=0)


def test_model_budget_rejects_impossible_safety_margin() -> None:
    with pytest.raises(ConfigurationError, match="safety_margin"):
        load_app_config(
            {
                "AI_ASSISTANT_MODEL_CONTEXT_WINDOW": "1024",
                "AI_ASSISTANT_MODEL_MAX_OUTPUT_TOKENS": "768",
                "AI_ASSISTANT_MODEL_CONTEXT_SAFETY_MARGIN": "256",
            }
        )


def test_context_limit_allows_8192() -> None:
    config = load_app_config({"AI_ASSISTANT_MODEL_CONTEXT_WINDOW": "8192"})

    assert config.model_context_window == 8192


def test_app_config_repr_hides_api_key() -> None:
    assert "secret" not in repr(AppConfig(api_key="secret"))


def test_invalid_provider_fails_clearly() -> None:
    with pytest.raises(ConfigurationError, match="Unsupported AI_ASSISTANT_PROVIDER"):
        load_app_config({"AI_ASSISTANT_PROVIDER": "bad"})


def test_invalid_timeout_fails_clearly() -> None:
    with pytest.raises(ConfigurationError, match="AI_ASSISTANT_REQUEST_TIMEOUT"):
        load_app_config({"AI_ASSISTANT_REQUEST_TIMEOUT": "0"})


def test_invalid_context_limit_fails_clearly() -> None:
    with pytest.raises(ConfigurationError, match="AI_ASSISTANT_MODEL_CONTEXT_WINDOW"):
        load_app_config({"AI_ASSISTANT_MODEL_CONTEXT_WINDOW": "nope"})


def test_invalid_tool_execution_flag_fails_clearly() -> None:
    with pytest.raises(ConfigurationError, match="AI_ASSISTANT_TOOL_EXECUTION"):
        load_app_config({"AI_ASSISTANT_TOOL_EXECUTION": "maybe"})


def test_invalid_tool_executor_fails_clearly() -> None:
    with pytest.raises(ConfigurationError, match="AI_ASSISTANT_TOOL_EXECUTOR"):
        load_app_config({"AI_ASSISTANT_TOOL_EXECUTOR": "python_fallback"})


def test_invalid_tool_limits_fail_clearly() -> None:
    with pytest.raises(ConfigurationError, match="AI_ASSISTANT_MAX_DIRECTORY_DEPTH"):
        load_app_config({"AI_ASSISTANT_MAX_DIRECTORY_DEPTH": "-1"})
