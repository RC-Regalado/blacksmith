"""Deny-by-default tool policy."""

from collections.abc import Mapping

from ai_assistant.application.ports.tools import ToolPolicy
from ai_assistant.application.tool_catalog import (
    FILE_METADATA,
    GIT_STATUS,
    LIST_DIRECTORY,
    READ_FILE,
    SEARCH_TEXT,
)
from ai_assistant.domain.tools import (
    PolicyDecisionKind,
    ToolDefinition,
    ToolExecutionRequest,
    ToolPolicyDecision,
)

REASON_TOOL_DISABLED = "tool_disabled"
REASON_UNKNOWN_TOOL = "unknown_tool"
REASON_INVALID_ARGUMENTS = "invalid_arguments"
REASON_PERMISSION_DENIED = "permission_denied"
REASON_TIMEOUT_EXCEEDED = "timeout_exceeded"
REASON_LIMIT_EXCEEDED = "limit_exceeded"
REASON_PATH_DENIED = "path_denied"


class DenyByDefaultToolPolicy(ToolPolicy):
    def __init__(self, enabled: bool = True) -> None:
        self._enabled = enabled

    def decide(
        self, request: ToolExecutionRequest, definition: ToolDefinition
    ) -> ToolPolicyDecision:
        if not self._enabled:
            return _deny(REASON_TOOL_DISABLED)
        if request.tool_name != definition.name:
            return _deny(REASON_UNKNOWN_TOOL)
        if request.permission != definition.permission:
            return _deny(REASON_PERMISSION_DENIED)
        if request.timeout_seconds > float(definition.limits["timeout_seconds"]):
            return _deny(REASON_TIMEOUT_EXCEEDED)
        if not _valid_arguments(request.arguments, definition):
            return _deny(REASON_INVALID_ARGUMENTS)
        if _exceeds_limits(request.arguments, definition):
            return _deny(REASON_LIMIT_EXCEEDED)
        return ToolPolicyDecision(kind=PolicyDecisionKind.ALLOW)

    def deny_unknown_tool(self) -> ToolPolicyDecision:
        return _deny(REASON_UNKNOWN_TOOL)

    def deny_path_result(self) -> ToolPolicyDecision:
        return _deny(REASON_PATH_DENIED)


def _valid_arguments(arguments: Mapping[str, object], definition: ToolDefinition) -> bool:
    path = arguments.get("path")
    if not isinstance(path, str) or not path:
        return False
    if definition.name == FILE_METADATA:
        return set(arguments) == {"path"}
    if definition.name == SEARCH_TEXT:
        query = arguments.get("query")
        return (
            isinstance(query, str)
            and bool(query)
            and _optional_int(arguments, "max_matches")
            and _optional_int(arguments, "max_files")
            and _optional_int(arguments, "max_preview_chars")
            and _optional_int(arguments, "max_bytes_per_file")
            and set(arguments)
            <= {
                "path",
                "query",
                "max_matches",
                "max_files",
                "max_preview_chars",
                "max_bytes_per_file",
            }
        )
    if definition.name == GIT_STATUS:
        return _optional_int(arguments, "max_entries") and set(arguments) <= {
            "path",
            "max_entries",
        }
    if definition.name == READ_FILE:
        return _optional_int(arguments, "offset") and _optional_int(
            arguments, "max_bytes"
        )
    if definition.name == LIST_DIRECTORY:
        return (
            _optional_bool(arguments, "recursive")
            and _optional_bool(arguments, "include_hidden")
            and _optional_int(arguments, "max_entries")
            and _optional_int(arguments, "max_depth")
        )
    return False


def _exceeds_limits(arguments: Mapping[str, object], definition: ToolDefinition) -> bool:
    if len(str(arguments["path"])) > int(definition.limits["max_path_length"]):
        return True
    if definition.name == FILE_METADATA:
        return False
    if definition.name == SEARCH_TEXT:
        query = str(arguments["query"])
        max_matches = int(
            arguments.get("max_matches", definition.defaults["max_matches"])
        )
        max_files = int(arguments.get("max_files", definition.defaults["max_files"]))
        max_preview = int(
            arguments.get("max_preview_chars", definition.defaults["max_preview_chars"])
        )
        max_bytes = int(
            arguments.get(
                "max_bytes_per_file", definition.defaults["max_bytes_per_file"]
            )
        )
        return (
            len(query) > int(definition.limits["max_query_length"])
            or max_matches < 1
            or max_matches > int(definition.limits["max_matches"])
            or max_files < 1
            or max_files > int(definition.limits["max_files"])
            or max_preview < 1
            or max_preview > int(definition.limits["max_preview_chars"])
            or max_bytes < 1
            or max_bytes > int(definition.limits["max_bytes_per_file"])
        )
    if definition.name == GIT_STATUS:
        max_entries = int(
            arguments.get("max_entries", definition.defaults["max_entries"])
        )
        return (
            max_entries < 1
            or max_entries > int(definition.limits["max_entries"])
        )
    if definition.name == READ_FILE:
        offset = int(arguments.get("offset", definition.defaults["offset"]))
        max_bytes = int(arguments.get("max_bytes", definition.defaults["max_bytes"]))
        return (
            offset < 0
            or max_bytes < 1
            or max_bytes > int(definition.limits["max_bytes"])
        )
    max_entries = int(arguments.get("max_entries", definition.defaults["max_entries"]))
    max_depth = int(arguments.get("max_depth", definition.defaults["max_depth"]))
    return (
        max_entries < 1
        or max_entries > int(definition.limits["max_entries"])
        or max_depth < 0
        or max_depth > int(definition.limits["max_depth"])
    )


def _optional_int(arguments: Mapping[str, object], name: str) -> bool:
    value = arguments.get(name)
    return value is None or type(value) is int


def _optional_bool(arguments: Mapping[str, object], name: str) -> bool:
    value = arguments.get(name)
    return value is None or isinstance(value, bool)


def _deny(reason_code: str) -> ToolPolicyDecision:
    return ToolPolicyDecision(kind=PolicyDecisionKind.DENY, reason_code=reason_code)
