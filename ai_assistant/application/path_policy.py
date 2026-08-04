"""Workspace path policy for read-only tools."""

from fnmatch import fnmatchcase
from pathlib import Path

from ai_assistant.application.errors import ConfigurationError, InvalidToolCallError
from ai_assistant.application.ports.tools import PathPolicy
from ai_assistant.application.tool_catalog import FILE_METADATA, LIST_DIRECTORY, READ_FILE
from ai_assistant.domain.tools import (
    ToolDefinition,
    ToolExecutionContext,
    ToolExecutionRequest,
)

_SENSITIVE_PATTERNS = (
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
)


class WorkspacePathPolicy(PathPolicy):
    def __init__(self, workspace: str | None) -> None:
        if not workspace:
            raise ConfigurationError("AI_ASSISTANT_WORKSPACE is required")
        self._workspace = Path(workspace).resolve(strict=True)
        if not self._workspace.is_dir():
            raise ConfigurationError("AI_ASSISTANT_WORKSPACE must be a directory")

    def validate(
        self, request: ToolExecutionRequest, definition: ToolDefinition
    ) -> ToolExecutionContext:
        relative = _relative_path(request, definition)
        try:
            resolved = (self._workspace / relative).resolve(strict=True)
        except OSError as exc:
            raise InvalidToolCallError("path does not exist") from exc
        _require_inside_workspace(resolved, self._workspace)
        _require_allowed_components(relative)
        _require_allowed_components(resolved.relative_to(self._workspace))
        _require_expected_type(resolved, definition)
        return ToolExecutionContext(
            request=request,
            workspace_id=str(self._workspace),
            resolved_path=str(resolved),
            relative_path=relative.as_posix(),
        )


def _relative_path(
    request: ToolExecutionRequest, definition: ToolDefinition
) -> Path:
    value = request.arguments.get("path")
    if not isinstance(value, str) or not value:
        raise InvalidToolCallError("path must be a non-empty string")
    limit = int(definition.limits.get("max_path_length", 4096))
    if len(value) > limit:
        raise InvalidToolCallError("path exceeds maximum length")
    path = Path(value)
    if path.is_absolute():
        raise InvalidToolCallError("absolute paths are denied")
    if ".." in path.parts:
        raise InvalidToolCallError("path traversal is denied")
    return path


def _require_inside_workspace(path: Path, workspace: Path) -> None:
    try:
        path.relative_to(workspace)
    except ValueError as exc:
        raise InvalidToolCallError("path escapes workspace") from exc


def _require_allowed_components(path: Path) -> None:
    for part in path.parts:
        if part in {"", "."}:
            continue
        if part.startswith("."):
            raise InvalidToolCallError("hidden paths are denied")
        if any(fnmatchcase(part, pattern) for pattern in _SENSITIVE_PATTERNS):
            raise InvalidToolCallError("sensitive paths are denied")


def _require_expected_type(path: Path, definition: ToolDefinition) -> None:
    if definition.name == READ_FILE and not path.is_file():
        raise InvalidToolCallError("path must be a regular file")
    if definition.name == LIST_DIRECTORY and not path.is_dir():
        raise InvalidToolCallError("path must be a directory")
    if definition.name == FILE_METADATA and not (path.is_file() or path.is_dir()):
        raise InvalidToolCallError("path must be a regular file or directory")
