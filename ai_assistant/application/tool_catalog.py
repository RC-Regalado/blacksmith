"""Static read-only tool catalog."""

from types import MappingProxyType

from ai_assistant.application.ports.tools import ToolCatalog
from ai_assistant.domain.errors import InvalidToolCallError
from ai_assistant.domain.tools import ToolDefinition, ToolPermission


LIST_DIRECTORY = "list_directory"
READ_FILE = "read_file"

_TOOLS = MappingProxyType(
    {
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
                },
                "required": ["path"],
            },
            permission=ToolPermission.READ_ONLY,
            defaults={
                "recursive": False,
                "include_hidden": False,
                "max_entries": 200,
                "timeout_seconds": 5.0,
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
                "max_bytes": 16384,
                "timeout_seconds": 5.0,
            },
            limits={
                "max_bytes": 65536,
                "max_path_length": 4096,
                "timeout_seconds": 30.0,
            },
        ),
    }
)


class StaticToolCatalog(ToolCatalog):
    def definition_for(self, tool_name: str) -> ToolDefinition:
        try:
            return _TOOLS[tool_name]
        except KeyError as exc:
            raise InvalidToolCallError(f"Unknown tool: {tool_name}") from exc

    def definitions(self) -> tuple[ToolDefinition, ...]:
        return tuple(_TOOLS.values())
