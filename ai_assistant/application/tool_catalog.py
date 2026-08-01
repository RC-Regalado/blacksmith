"""Static read-only tool catalog."""

from ai_assistant.application.ports.tools import ToolCatalog
from ai_assistant.domain.errors import InvalidToolCallError
from ai_assistant.domain.tools import ToolDefinition, ToolPermission


LIST_DIRECTORY = "list_directory"
READ_FILE = "read_file"


class StaticToolCatalog(ToolCatalog):
    def __init__(
        self,
        tool_timeout: float = 5.0,
        max_read_bytes: int = 16384,
        max_directory_entries: int = 200,
        max_directory_depth: int = 0,
    ) -> None:
        self._tools = _definitions(
            min(tool_timeout, 30.0),
            min(max_read_bytes, 65536),
            min(max_directory_entries, 1000),
            min(max_directory_depth, 3),
        )

    def definition_for(self, tool_name: str) -> ToolDefinition:
        try:
            return self._tools[tool_name]
        except KeyError as exc:
            raise InvalidToolCallError(f"Unknown tool: {tool_name}") from exc

    def definitions(self) -> tuple[ToolDefinition, ...]:
        return tuple(self._tools.values())


def _definitions(
    tool_timeout: float,
    max_read_bytes: int,
    max_directory_entries: int,
    max_directory_depth: int,
) -> dict[str, ToolDefinition]:
    return {
        LIST_DIRECTORY: ToolDefinition(
            name=LIST_DIRECTORY,
            description="List entries in a workspace directory.",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "recursive": {"type": "boolean"},
                    "include_hidden": {"type": "boolean"},
                    "max_entries": {"type": "integer"},
                    "max_depth": {"type": "integer"},
                },
                "required": ["path"],
            },
            permission=ToolPermission.READ_ONLY,
            defaults={
                "recursive": False,
                "include_hidden": False,
                "max_entries": max_directory_entries,
                "max_depth": max_directory_depth,
                "timeout_seconds": tool_timeout,
            },
            limits={
                "max_entries": 1000,
                "max_depth": 3,
                "max_path_length": 4096,
                "timeout_seconds": 30.0,
            },
        ),
        READ_FILE: ToolDefinition(
            name=READ_FILE,
            description="Read a bounded byte range from a workspace file.",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "offset": {"type": "integer"},
                    "max_bytes": {"type": "integer"},
                },
                "required": ["path"],
            },
            permission=ToolPermission.READ_ONLY,
            defaults={
                "offset": 0,
                "max_bytes": max_read_bytes,
                "timeout_seconds": tool_timeout,
            },
            limits={
                "max_bytes": 65536,
                "max_path_length": 4096,
                "timeout_seconds": 30.0,
            },
        ),
    }
