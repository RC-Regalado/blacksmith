"""Local read-only tool executor.

Binary reads are returned as UTF-8 text with replacement characters. `bytes_read`
always reports raw bytes, not decoded character count.
"""

import json
import stat
from pathlib import Path

from ai_assistant.application.path_policy import WorkspacePathPolicy
from ai_assistant.application.ports.tools import ToolExecutor
from ai_assistant.application.tool_catalog import (
    LIST_DIRECTORY,
    READ_FILE,
    StaticToolCatalog,
)
from ai_assistant.domain.tools import (
    SanitizedToolError,
    ToolExecutionContext,
    ToolExecutionResult,
    ToolExecutionStatus,
)

_MAX_RESPONSE_BYTES = 1_048_576


class LocalReadOnlyToolExecutor(ToolExecutor):
    def __init__(self) -> None:
        self._catalog = StaticToolCatalog()

    def execute(self, context: ToolExecutionContext) -> ToolExecutionResult:
        try:
            checked = self._validate_again(context)
            if checked.request.tool_name == READ_FILE:
                return _read_file(checked)
            if checked.request.tool_name == LIST_DIRECTORY:
                return _list_directory(checked)
            return _error(checked, "unknown_tool", "Unknown tool.")
        except Exception as exc:  # noqa: BLE001 - executor returns sanitized errors.
            return ToolExecutionResult(
                request_id=context.request.request_id,
                tool_name=context.request.tool_name,
                status=ToolExecutionStatus.ERROR,
                error=SanitizedToolError(
                    code="local_executor_error",
                    message=str(exc) or "Local tool execution failed.",
                ),
            )

    def _validate_again(self, context: ToolExecutionContext) -> ToolExecutionContext:
        definition = self._catalog.definition_for(context.request.tool_name)
        return WorkspacePathPolicy(context.workspace_id).validate(
            context.request,
            definition,
        )


def _read_file(context: ToolExecutionContext) -> ToolExecutionResult:
    path = _resolved_path(context)
    offset = int(context.request.arguments.get("offset", 0))
    max_bytes = min(int(context.request.arguments.get("max_bytes", 16384)), 65536)
    with path.open("rb") as handle:
        handle.seek(max(offset, 0))
        data = handle.read(max_bytes + 1)
    truncated = len(data) > max_bytes
    data = data[:max_bytes]
    return ToolExecutionResult(
        request_id=context.request.request_id,
        tool_name=context.request.tool_name,
        status=ToolExecutionStatus.SUCCESS,
        content={
            "path": context.relative_path,
            "content": data.decode("utf-8", errors="replace"),
            "bytes_read": len(data),
            "truncated": truncated,
        },
        truncated=truncated,
    )


def _list_directory(context: ToolExecutionContext) -> ToolExecutionResult:
    path = _resolved_path(context)
    max_entries = min(int(context.request.arguments.get("max_entries", 200)), 1000)
    max_depth = min(int(context.request.arguments.get("max_depth", 0)), 3)
    recursive = bool(context.request.arguments.get("recursive", False))
    entries = list(_entries(path, recursive, max_depth))
    limited = _fit_response(entries[:max_entries])
    return ToolExecutionResult(
        request_id=context.request.request_id,
        tool_name=context.request.tool_name,
        status=ToolExecutionStatus.SUCCESS,
        content={
            "path": context.relative_path,
            "entries": limited,
            "truncated": len(limited) < len(entries) or len(entries) > max_entries,
        },
        truncated=len(limited) < len(entries) or len(entries) > max_entries,
    )


def _entries(path: Path, recursive: bool, max_depth: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for child in sorted(path.iterdir(), key=lambda item: item.name):
        if child.name.startswith("."):
            continue
        rows.append(_entry(child, child.name))
        if recursive and max_depth > 0 and _is_directory(child):
            for entry in _entries(child, True, max_depth - 1):
                rows.append({**entry, "name": f"{child.name}/{entry['name']}"})
    return rows


def _entry(path: Path, name: str) -> dict[str, object]:
    mode = path.lstat().st_mode
    if stat.S_ISDIR(mode):
        return {"name": name, "type": "directory", "size": None}
    if stat.S_ISREG(mode):
        return {"name": name, "type": "file", "size": path.stat().st_size}
    return {"name": name, "type": "other", "size": None}


def _is_directory(path: Path) -> bool:
    return stat.S_ISDIR(path.lstat().st_mode)


def _fit_response(entries: list[dict[str, object]]) -> list[dict[str, object]]:
    kept: list[dict[str, object]] = []
    for entry in entries:
        candidate = [*kept, entry]
        if len(json.dumps(candidate).encode("utf-8")) > _MAX_RESPONSE_BYTES:
            break
        kept = candidate
    return kept


def _resolved_path(context: ToolExecutionContext) -> Path:
    if not context.resolved_path:
        raise ValueError("resolved_path is required")
    return Path(context.resolved_path)


def _error(
    context: ToolExecutionContext,
    code: str,
    message: str,
) -> ToolExecutionResult:
    return ToolExecutionResult(
        request_id=context.request.request_id,
        tool_name=context.request.tool_name,
        status=ToolExecutionStatus.ERROR,
        error=SanitizedToolError(code=code, message=message),
    )
