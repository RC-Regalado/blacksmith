"""Application configuration loaded at bootstrap."""

import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from ai_assistant.application.errors import ConfigurationError

SUPPORTED_PROVIDERS = frozenset({"dummy", "ollama", "openai", "chatgpt"})
SUPPORTED_TOOL_EXECUTORS = frozenset({"unix_socket", "local"})
DEFAULT_MODEL_CONTEXT_WINDOW = 4096
DEFAULT_MODEL_MAX_OUTPUT_TOKENS = 2048
DEFAULT_MODEL_CONTEXT_SAFETY_MARGIN = 0


@dataclass(frozen=True, slots=True)
class AppConfig:
    provider: str = "dummy"
    model: str = ""
    base_url: str = "https://api.openai.com/v1"
    database: str = "assistant.sqlite3"
    execution_database: str = "assistant_execution.sqlite3"
    knowledge_database: str = "assistant_knowledge.sqlite3"
    session: str = "default"
    system_prompt: str = "You are a local AI assistant."
    log_level: str = "INFO"
    request_timeout: float = 60.0
    model_context_window: int = DEFAULT_MODEL_CONTEXT_WINDOW
    model_max_output_tokens: int = DEFAULT_MODEL_MAX_OUTPUT_TOKENS
    model_context_safety_margin: int = DEFAULT_MODEL_CONTEXT_SAFETY_MARGIN
    workspace: str | None = None
    tool_execution: bool = False
    tool_timeout: float = 5.0
    max_read_bytes: int = 16384
    max_directory_entries: int = 200
    max_directory_depth: int = 0
    audit_database: str = "assistant_audit.sqlite3"
    audit_auto_purge: bool = False
    tool_executor: str = "unix_socket"
    tool_socket: str = "c_toolserver/build/toolserver.sock"
    tool_log_dir: str = "logs/tools"
    context_engine: bool = False
    show_metrics: bool = False
    api_key: str | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if self.model_context_window <= 0:
            raise ConfigurationError("model_context_window must be positive.")
        if self.model_max_output_tokens <= 0:
            raise ConfigurationError("model_max_output_tokens must be positive.")
        if self.model_context_safety_margin < 0:
            raise ConfigurationError("model_context_safety_margin cannot be negative.")
        reserved = self.model_max_output_tokens + self.model_context_safety_margin
        if reserved >= self.model_context_window:
            raise ConfigurationError(
                "model_max_output_tokens plus model_context_safety_margin must be less than model_context_window."
            )
        if self.provider == "ollama":
            _validate_ollama_budget(self)

    @property
    def context_limit(self) -> int:
        return self.model_context_window

    @property
    def reserved_output_tokens(self) -> int:
        return self.model_max_output_tokens

    @property
    def model_input_budget(self) -> int:
        return (
            self.model_context_window
            - self.model_max_output_tokens
            - self.model_context_safety_margin
        )


def load_app_config(
    env: Mapping[str, str] | None = None,
    env_file: str | Path | None = None,
) -> AppConfig:
    file_path = Path(".env") if env is None and env_file is None else env_file
    source = {**_load_env_file(file_path), **dict(os.environ if env is None else env)}
    provider = _provider(source.get("AI_ASSISTANT_PROVIDER", "dummy"))
    model_context_window = _positive_int(
        source.get(
            "AI_ASSISTANT_MODEL_CONTEXT_WINDOW",
            str(DEFAULT_MODEL_CONTEXT_WINDOW),
        ),
        "AI_ASSISTANT_MODEL_CONTEXT_WINDOW",
    )
    model_max_output_tokens = _positive_int(
        source.get(
            "AI_ASSISTANT_MODEL_MAX_OUTPUT_TOKENS",
            str(_default_max_output_tokens(model_context_window)),
        ),
        "AI_ASSISTANT_MODEL_MAX_OUTPUT_TOKENS",
    )
    model_context_safety_margin = _non_negative_int(
        source.get(
            "AI_ASSISTANT_MODEL_CONTEXT_SAFETY_MARGIN",
            str(DEFAULT_MODEL_CONTEXT_SAFETY_MARGIN),
        ),
        "AI_ASSISTANT_MODEL_CONTEXT_SAFETY_MARGIN",
    )
    return AppConfig(
        provider=provider,
        model=source.get("AI_ASSISTANT_MODEL", ""),
        base_url=source.get("AI_ASSISTANT_BASE_URL", _default_base_url(provider)),
        database=source.get("AI_ASSISTANT_DATABASE", "assistant.sqlite3"),
        execution_database=source.get(
            "AI_ASSISTANT_EXECUTION_DATABASE",
            "assistant_execution.sqlite3",
        ),
        knowledge_database=source.get(
            "AI_ASSISTANT_KNOWLEDGE_DATABASE",
            "assistant_knowledge.sqlite3",
        ),
        session=source.get("AI_ASSISTANT_SESSION", "default"),
        system_prompt=source.get(
            "AI_ASSISTANT_SYSTEM_PROMPT", "You are a local AI assistant."
        ),
        log_level=source.get("AI_ASSISTANT_LOG_LEVEL", "INFO").upper(),
        request_timeout=_positive_float(
            source.get("AI_ASSISTANT_REQUEST_TIMEOUT", "60"),
            "AI_ASSISTANT_REQUEST_TIMEOUT",
        ),
        model_context_window=model_context_window,
        model_max_output_tokens=model_max_output_tokens,
        model_context_safety_margin=model_context_safety_margin,
        workspace=_optional_text(source.get("AI_ASSISTANT_WORKSPACE")),
        tool_execution=_bool(
            source.get("AI_ASSISTANT_TOOL_EXECUTION", "false"),
            "AI_ASSISTANT_TOOL_EXECUTION",
        ),
        tool_timeout=_positive_float(
            source.get("AI_ASSISTANT_TOOL_TIMEOUT", "5"),
            "AI_ASSISTANT_TOOL_TIMEOUT",
        ),
        max_read_bytes=_positive_int(
            source.get("AI_ASSISTANT_MAX_READ_BYTES", "16384"),
            "AI_ASSISTANT_MAX_READ_BYTES",
        ),
        max_directory_entries=_positive_int(
            source.get("AI_ASSISTANT_MAX_DIRECTORY_ENTRIES", "200"),
            "AI_ASSISTANT_MAX_DIRECTORY_ENTRIES",
        ),
        max_directory_depth=_non_negative_int(
            source.get("AI_ASSISTANT_MAX_DIRECTORY_DEPTH", "0"),
            "AI_ASSISTANT_MAX_DIRECTORY_DEPTH",
        ),
        audit_database=source.get(
            "AI_ASSISTANT_AUDIT_DATABASE",
            "assistant_audit.sqlite3",
        ),
        audit_auto_purge=_bool(
            source.get("AI_ASSISTANT_AUDIT_AUTO_PURGE", "false"),
            "AI_ASSISTANT_AUDIT_AUTO_PURGE",
        ),
        tool_executor=_tool_executor(
            source.get("AI_ASSISTANT_TOOL_EXECUTOR", "unix_socket")
        ),
        tool_socket=source.get(
            "AI_ASSISTANT_TOOL_SOCKET",
            "c_toolserver/build/toolserver.sock",
        ),
        tool_log_dir=source.get("AI_ASSISTANT_TOOL_LOG_DIR", "logs/tools"),
        context_engine=_bool(
            source.get("AI_ASSISTANT_CONTEXT_ENGINE", "false"),
            "AI_ASSISTANT_CONTEXT_ENGINE",
        ),
        show_metrics=_bool(
            source.get("AI_ASSISTANT_SHOW_METRICS", "false"),
            "AI_ASSISTANT_SHOW_METRICS",
        ),
        api_key=source.get("OPENAI_API_KEY"),
    )


def _provider(value: str) -> str:
    provider = value.strip().lower()
    if provider not in SUPPORTED_PROVIDERS:
        supported = ", ".join(sorted(SUPPORTED_PROVIDERS))
        raise ConfigurationError(
            f"Unsupported AI_ASSISTANT_PROVIDER: {value!r}; use {supported}"
        )
    return provider


def _tool_executor(value: str) -> str:
    executor = value.strip().lower()
    if executor not in SUPPORTED_TOOL_EXECUTORS:
        supported = ", ".join(sorted(SUPPORTED_TOOL_EXECUTORS))
        raise ConfigurationError(
            f"Unsupported AI_ASSISTANT_TOOL_EXECUTOR: {value!r}; use {supported}"
        )
    return executor


def _default_base_url(provider: str) -> str:
    if provider == "ollama":
        return "http://localhost:11434"
    return "https://api.openai.com/v1"


def _default_max_output_tokens(context_window: int) -> int:
    return min(DEFAULT_MODEL_MAX_OUTPUT_TOKENS, max(1, context_window // 2))


def _validate_ollama_budget(config: AppConfig) -> None:
    if config.model_max_output_tokens <= 0:
        raise ConfigurationError("model_max_output_tokens must be positive for Ollama.")


def _load_env_file(env_file: str | Path | None) -> dict[str, str]:
    if env_file is None:
        return {}
    path = Path(env_file)
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        parsed = _parse_env_line(line)
        if parsed is not None:
            key, value = parsed
            values[key] = value
    return values


def _parse_env_line(line: str) -> tuple[str, str] | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#") or "=" not in stripped:
        return None
    if stripped.startswith("export "):
        stripped = stripped[7:].lstrip()
    key, value = stripped.split("=", 1)
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        value = value[1:-1]
    return key.strip(), value


def _positive_float(value: str, name: str) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise ConfigurationError(f"{name} must be a positive number") from exc
    if parsed <= 0:
        raise ConfigurationError(f"{name} must be a positive number")
    return parsed


def _positive_int(value: str, name: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ConfigurationError(f"{name} must be a positive integer") from exc
    if parsed <= 0:
        raise ConfigurationError(f"{name} must be a positive integer")
    return parsed


def _non_negative_int(value: str, name: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ConfigurationError(f"{name} must be a non-negative integer") from exc
    if parsed < 0:
        raise ConfigurationError(f"{name} must be a non-negative integer")
    return parsed


def _bool(value: str, name: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ConfigurationError(f"{name} must be true or false")


def _optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _optional_positive_int(value: str | None, name: str) -> int | None:
    if value is None or not value.strip():
        return None
    return _positive_int(value, name)
