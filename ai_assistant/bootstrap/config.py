"""Application configuration loaded at bootstrap."""

import os
from collections.abc import Mapping
from dataclasses import dataclass, field

from ai_assistant.application.errors import ConfigurationError

SUPPORTED_PROVIDERS = frozenset({"dummy", "ollama", "openai", "chatgpt"})
SUPPORTED_TOOL_EXECUTORS = frozenset({"unix_socket", "local"})


@dataclass(frozen=True, slots=True)
class AppConfig:
    provider: str = "dummy"
    model: str = ""
    base_url: str = "https://api.openai.com/v1"
    database: str = "assistant.sqlite3"
    session: str = "default"
    system_prompt: str = "You are a local AI assistant."
    log_level: str = "INFO"
    request_timeout: float = 60.0
    context_limit: int = 4096
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
    api_key: str | None = field(default=None, repr=False)


def load_app_config(env: Mapping[str, str] | None = None) -> AppConfig:
    source = os.environ if env is None else env
    provider = _provider(source.get("AI_ASSISTANT_PROVIDER", "dummy"))
    return AppConfig(
        provider=provider,
        model=source.get("AI_ASSISTANT_MODEL", ""),
        base_url=source.get("AI_ASSISTANT_BASE_URL", _default_base_url(provider)),
        database=source.get("AI_ASSISTANT_DATABASE", "assistant.sqlite3"),
        session=source.get("AI_ASSISTANT_SESSION", "default"),
        system_prompt=source.get(
            "AI_ASSISTANT_SYSTEM_PROMPT", "You are a local AI assistant."
        ),
        log_level=source.get("AI_ASSISTANT_LOG_LEVEL", "INFO").upper(),
        request_timeout=_positive_float(
            source.get("AI_ASSISTANT_REQUEST_TIMEOUT", "60"),
            "AI_ASSISTANT_REQUEST_TIMEOUT",
        ),
        context_limit=_positive_int(
            source.get("AI_ASSISTANT_CONTEXT_LIMIT", "4096"),
            "AI_ASSISTANT_CONTEXT_LIMIT",
        ),
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
