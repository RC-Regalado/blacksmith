"""Application configuration loaded at bootstrap."""

import os
from collections.abc import Mapping
from dataclasses import dataclass, field

from ai_assistant.application.errors import ConfigurationError

SUPPORTED_PROVIDERS = frozenset({"dummy", "ollama", "openai", "chatgpt"})


@dataclass(frozen=True, slots=True)
class AppConfig:
    provider: str = "dummy"
    model: str = "gpt-5"
    base_url: str = "https://api.openai.com/v1"
    database: str = "assistant.sqlite3"
    session: str = "default"
    system_prompt: str = "You are a local AI assistant."
    log_level: str = "INFO"
    request_timeout: float = 60.0
    context_limit: int = 4096
    api_key: str | None = field(default=None, repr=False)


def load_app_config(env: Mapping[str, str] | None = None) -> AppConfig:
    source = os.environ if env is None else env
    provider = _provider(source.get("AI_ASSISTANT_PROVIDER", "dummy"))
    return AppConfig(
        provider=provider,
        model=source.get("AI_ASSISTANT_MODEL", "gpt-5"),
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
