"""Integration tests for local read-only tool executor."""

from pathlib import Path

import pytest

from ai_assistant.domain.tools import (
    ToolExecutionContext,
    ToolExecutionRequest,
    ToolExecutionStatus,
    ToolPermission,
)
from ai_assistant.infrastructure.tools.local_read_only import LocalReadOnlyToolExecutor


pytestmark = pytest.mark.integration


def test_list_directory_returns_structured_entries(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "README.md").write_text("hello", encoding="utf-8")
    (tmp_path / ".env").write_text("secret", encoding="utf-8")

    result = LocalReadOnlyToolExecutor().execute(_context(tmp_path, "list_directory", "."))

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.content == {
        "path": ".",
        "entries": [
            {"name": "README.md", "type": "file", "size": 5},
            {"name": "src", "type": "directory", "size": None},
        ],
        "truncated": False,
    }


def test_read_file_is_bounded_and_reports_truncation(tmp_path: Path) -> None:
    (tmp_path / "notes.txt").write_text("abcdef", encoding="utf-8")

    result = LocalReadOnlyToolExecutor().execute(
        _context(tmp_path, "read_file", "notes.txt", {"max_bytes": 3})
    )

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.truncated is True
    assert result.content == {
        "path": "notes.txt",
        "content": "abc",
        "bytes_read": 3,
        "truncated": True,
    }


def test_file_metadata_returns_no_file_content(tmp_path: Path) -> None:
    (tmp_path / "notes.txt").write_text("abcdef", encoding="utf-8")

    result = LocalReadOnlyToolExecutor().execute(
        _context(tmp_path, "file_metadata", "notes.txt", permission=ToolPermission.READ_METADATA)
    )

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.content is not None
    assert result.content["path"] == "notes.txt"
    assert result.content["type"] == "file"
    assert result.content["size"] == 6
    assert "content" not in result.content


def test_executor_repeats_path_validation_before_access(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside.txt"
    outside.write_text("secret", encoding="utf-8")

    result = LocalReadOnlyToolExecutor().execute(
        _context(tmp_path, "read_file", "../outside.txt")
    )

    assert result.status == ToolExecutionStatus.ERROR
    assert result.error is not None
    assert result.error.code == "local_executor_error"


def test_binary_file_is_decoded_with_replacement(tmp_path: Path) -> None:
    (tmp_path / "binary.bin").write_bytes(b"a\xffb")

    result = LocalReadOnlyToolExecutor().execute(
        _context(tmp_path, "read_file", "binary.bin")
    )

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.content is not None
    assert result.content["content"] == "a\ufffdb"
    assert result.content["bytes_read"] == 3


def test_executor_enforces_read_limit_independently(tmp_path: Path) -> None:
    (tmp_path / "big.txt").write_bytes(b"x" * 70000)

    result = LocalReadOnlyToolExecutor().execute(
        _context(tmp_path, "read_file", "big.txt", {"max_bytes": 70000})
    )

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.content is not None
    assert result.content["bytes_read"] == 65536
    assert result.truncated is True


def test_executor_enforces_directory_entry_limit_independently(tmp_path: Path) -> None:
    for index in range(1002):
        (tmp_path / f"{index:04}.txt").write_text("x", encoding="utf-8")

    result = LocalReadOnlyToolExecutor().execute(
        _context(tmp_path, "list_directory", ".", {"max_entries": 2000})
    )

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.content is not None
    assert len(result.content["entries"]) == 1000
    assert result.truncated is True


def _context(
    workspace: Path,
    tool_name: str,
    path: str,
    arguments: dict[str, object] | None = None,
    permission: ToolPermission = ToolPermission.READ_ONLY,
) -> ToolExecutionContext:
    args = {"path": path, **(arguments or {})}
    return ToolExecutionContext(
        request=ToolExecutionRequest(
            request_id="req-1",
            session_id="default",
            tool_name=tool_name,
            arguments=args,
            permission=permission,
        ),
        workspace_id=str(workspace),
        resolved_path=str((workspace / path).resolve()),
        relative_path=path,
    )
