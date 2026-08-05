"""Static read-only tool catalog."""

from ai_assistant.application.ports.tools import ToolCatalog
from ai_assistant.domain.errors import InvalidToolCallError
from ai_assistant.domain.tools import ToolDefinition, ToolPermission


LIST_DIRECTORY = "list_directory"
READ_FILE = "read_file"
BUILD_PROJECT = "build_project"
FILE_METADATA = "file_metadata"
SEARCH_TEXT = "search_text"
GIT_STATUS = "git_status"
GIT_DIFF = "git_diff"
RUN_TESTS = "run_tests"
WRITE = "write"


class StaticToolCatalog(ToolCatalog):
    def __init__(
        self,
        tool_timeout: float = 5.0,
        max_read_bytes: int = 16384,
        max_directory_entries: int = 200,
        max_directory_depth: int = 0,
        max_search_matches: int = 20,
        max_search_files: int = 50,
        max_search_preview_chars: int = 160,
        max_search_bytes_per_file: int = 262144,
        max_git_status_entries: int = 200,
        max_git_diff_bytes: int = 16384,
        max_process_output_bytes: int = 131072,
        max_write_bytes: int = 65536,
    ) -> None:
        self._tools = _definitions(
            min(tool_timeout, 30.0),
            min(max_read_bytes, 65536),
            min(max_directory_entries, 1000),
            min(max_directory_depth, 3),
            min(max_search_matches, 100),
            min(max_search_files, 200),
            min(max_search_preview_chars, 500),
            min(max_search_bytes_per_file, 1048576),
            min(max_git_status_entries, 1000),
            min(max_git_diff_bytes, 65536),
            min(max_process_output_bytes, 2097152),
            min(max_write_bytes, 65536),
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
    max_search_matches: int,
    max_search_files: int,
    max_search_preview_chars: int,
    max_search_bytes_per_file: int,
    max_git_status_entries: int,
    max_git_diff_bytes: int,
    max_process_output_bytes: int,
    max_write_bytes: int,
) -> dict[str, ToolDefinition]:
    return {
        FILE_METADATA: ToolDefinition(
            name=FILE_METADATA,
            description="Return bounded metadata for a workspace file or directory.",
            input_schema={
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
            permission=ToolPermission.READ_METADATA,
            defaults={"timeout_seconds": tool_timeout},
            limits={
                "max_path_length": 4096,
                "timeout_seconds": 30.0,
            },
        ),
        SEARCH_TEXT: ToolDefinition(
            name=SEARCH_TEXT,
            description="Search literal text in bounded workspace files.",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "query": {"type": "string"},
                    "max_matches": {"type": "integer"},
                    "max_files": {"type": "integer"},
                    "max_preview_chars": {"type": "integer"},
                    "max_bytes_per_file": {"type": "integer"},
                },
                "required": ["path", "query"],
            },
            permission=ToolPermission.READ_CONTENT,
            defaults={
                "max_matches": max_search_matches,
                "max_files": max_search_files,
                "max_preview_chars": max_search_preview_chars,
                "max_bytes_per_file": max_search_bytes_per_file,
                "timeout_seconds": tool_timeout,
            },
            limits={
                "max_matches": 100,
                "max_files": 200,
                "max_preview_chars": 500,
                "max_bytes_per_file": 1048576,
                "max_path_length": 4096,
                "max_query_length": 256,
                "timeout_seconds": 30.0,
            },
        ),
        GIT_STATUS: ToolDefinition(
            name=GIT_STATUS,
            description="Return bounded structured Git repository status.",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "max_entries": {"type": "integer"},
                },
                "required": ["path"],
            },
            permission=ToolPermission.READ_REPOSITORY,
            defaults={
                "max_entries": max_git_status_entries,
                "timeout_seconds": tool_timeout,
            },
            limits={
                "max_entries": 1000,
                "max_path_length": 4096,
                "timeout_seconds": 30.0,
            },
        ),
        GIT_DIFF: ToolDefinition(
            name=GIT_DIFF,
            description="Return bounded read-only Git diff for staged or worktree changes.",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "scope": {"type": "string", "enum": ["worktree", "staged"]},
                    "max_bytes": {"type": "integer"},
                },
                "required": ["path", "scope"],
            },
            permission=ToolPermission.READ_REPOSITORY,
            defaults={
                "max_bytes": max_git_diff_bytes,
                "timeout_seconds": tool_timeout,
            },
            limits={
                "max_bytes": 65536,
                "max_path_length": 4096,
                "timeout_seconds": 30.0,
            },
        ),
        RUN_TESTS: ToolDefinition(
            name=RUN_TESTS,
            description="Run an approved fixed test profile.",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "profile_id": {"type": "string"},
                    "stdout_limit_bytes": {"type": "integer"},
                    "stderr_limit_bytes": {"type": "integer"},
                },
                "required": ["path", "profile_id"],
            },
            permission=ToolPermission.EXECUTE_PROJECT,
            defaults={
                "stdout_limit_bytes": max_process_output_bytes,
                "stderr_limit_bytes": max_process_output_bytes,
                "timeout_seconds": 120.0,
            },
            limits={
                "stdout_limit_bytes": 2097152,
                "stderr_limit_bytes": 2097152,
                "max_path_length": 4096,
                "timeout_seconds": 900.0,
            },
        ),
        BUILD_PROJECT: ToolDefinition(
            name=BUILD_PROJECT,
            description="Run an approved fixed build profile.",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "profile_id": {"type": "string"},
                    "stdout_limit_bytes": {"type": "integer"},
                    "stderr_limit_bytes": {"type": "integer"},
                },
                "required": ["path", "profile_id"],
            },
            permission=ToolPermission.EXECUTE_PROJECT,
            defaults={
                "stdout_limit_bytes": max_process_output_bytes,
                "stderr_limit_bytes": max_process_output_bytes,
                "timeout_seconds": 180.0,
            },
            limits={
                "stdout_limit_bytes": 2097152,
                "stderr_limit_bytes": 2097152,
                "max_path_length": 4096,
                "timeout_seconds": 1200.0,
            },
        ),
        WRITE: ToolDefinition(
            name=WRITE,
            description="Validate a bounded workspace file create or replace request.",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                    "mode": {"type": "string", "enum": ["create", "replace"]},
                    "expected_sha256": {"type": "string"},
                },
                "required": ["path", "content", "mode"],
            },
            permission=ToolPermission.WRITE_WORKSPACE,
            defaults={
                "max_bytes": max_write_bytes,
                "timeout_seconds": 30.0,
            },
            limits={
                "max_bytes": 65536,
                "max_path_length": 4096,
                "timeout_seconds": 30.0,
            },
        ),
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
