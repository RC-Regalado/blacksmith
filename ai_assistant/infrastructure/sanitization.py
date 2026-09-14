"""Shared metadata redaction helpers."""

from collections.abc import Mapping
from fnmatch import fnmatchcase
import re

_REDACTED = "[redacted]"
_SECRET_RE = re.compile(r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*\S+")
_SENSITIVE_KEYS = {
    "api_key",
    "auth",
    "authorization",
    "content",
    "file_content",
    "password",
    "prompt",
    "response",
    "secret",
    "token",
}
_PATH_KEYS = {"path", "file", "filename", "source_uri"}
_SENSITIVE_PATTERNS = {
    ".env",
    ".env.*",
    "*.pem",
    "*.key",
    "*.p12",
    "*.pfx",
    "id_rsa",
    "id_ed25519",
    "credentials.json",
    "secrets.*",
    "*.kubeconfig",
}


def redact_sensitive(value: object, key: str | None = None) -> object:
    if key and _is_sensitive_key(key):
        return _REDACTED
    if key and _is_path_key(key) and isinstance(value, str) and _is_sensitive_path(value):
        return _REDACTED
    if isinstance(value, Mapping):
        return {str(k): redact_sensitive(item, str(k)) for k, item in value.items()}
    if isinstance(value, list | tuple):
        return [redact_sensitive(item) for item in value]
    if isinstance(value, str):
        return _SECRET_RE.sub(r"\1=[REDACTED]", value)
    return value


def _is_sensitive_key(key: str) -> bool:
    normalized = key.lower()
    return any(part in normalized for part in _SENSITIVE_KEYS)


def _is_path_key(key: str) -> bool:
    return key.lower() in _PATH_KEYS


def _is_sensitive_path(value: str) -> bool:
    parts = [part for part in value.replace("\\", "/").split("/") if part]
    return any(part.startswith(".") or any(fnmatchcase(part, pattern) for pattern in _SENSITIVE_PATTERNS) for part in parts)
