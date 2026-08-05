"""Tests for workspace path policy."""

import os
import socket
import stat
from pathlib import Path

import pytest

from ai_assistant.application.errors import ConfigurationError, InvalidToolCallError
from ai_assistant.application.path_policy import WorkspacePathPolicy
from ai_assistant.application.tool_catalog import StaticToolCatalog
from ai_assistant.domain.tools import ToolExecutionRequest


pytestmark = pytest.mark.unit


def test_internal_valid_file_path_is_allowed(tmp_path: Path) -> None:
    target = tmp_path / "notes.txt"
    target.write_text("ok", encoding="utf-8")

    context = _validate(tmp_path, "read_file", "notes.txt")

    assert context.resolved_path == str(target.resolve())
    assert context.relative_path == "notes.txt"


def test_internal_valid_directory_path_is_allowed(tmp_path: Path) -> None:
    directory = tmp_path / "src"
    directory.mkdir()

    context = _validate(tmp_path, "list_directory", "src")

    assert context.resolved_path == str(directory.resolve())
    assert context.relative_path == "src"


def test_file_metadata_allows_file_or_directory(tmp_path: Path) -> None:
    (tmp_path / "notes.txt").write_text("ok", encoding="utf-8")
    (tmp_path / "src").mkdir()

    assert _validate(tmp_path, "file_metadata", "notes.txt").relative_path == "notes.txt"
    assert _validate(tmp_path, "file_metadata", "src").relative_path == "src"


def test_search_text_allows_file_or_directory_root(tmp_path: Path) -> None:
    (tmp_path / "notes.txt").write_text("ok", encoding="utf-8")
    (tmp_path / "src").mkdir()

    assert _validate(tmp_path, "search_text", "notes.txt").relative_path == "notes.txt"
    assert _validate(tmp_path, "search_text", "src").relative_path == "src"


def test_git_status_allows_directory_root_only(tmp_path: Path) -> None:
    (tmp_path / "notes.txt").write_text("ok", encoding="utf-8")
    (tmp_path / "repo").mkdir()

    assert _validate(tmp_path, "git_status", "repo").relative_path == "repo"
    with pytest.raises(InvalidToolCallError, match="directory"):
        _validate(tmp_path, "git_status", "notes.txt")


def test_git_diff_allows_directory_root_only(tmp_path: Path) -> None:
    (tmp_path / "notes.txt").write_text("ok", encoding="utf-8")
    (tmp_path / "repo").mkdir()

    assert _validate(tmp_path, "git_diff", "repo").relative_path == "repo"
    with pytest.raises(InvalidToolCallError, match="directory"):
        _validate(tmp_path, "git_diff", "notes.txt")


def test_run_tests_allows_directory_root_only(tmp_path: Path) -> None:
    (tmp_path / "notes.txt").write_text("ok", encoding="utf-8")
    (tmp_path / "repo").mkdir()

    assert _validate(tmp_path, "run_tests", "repo").relative_path == "repo"
    with pytest.raises(InvalidToolCallError, match="directory"):
        _validate(tmp_path, "run_tests", "notes.txt")


def test_build_project_allows_directory_root_only(tmp_path: Path) -> None:
    (tmp_path / "notes.txt").write_text("ok", encoding="utf-8")
    (tmp_path / "repo").mkdir()

    assert _validate(tmp_path, "build_project", "repo").relative_path == "repo"
    with pytest.raises(InvalidToolCallError, match="directory"):
        _validate(tmp_path, "build_project", "notes.txt")


def test_write_create_allows_new_workspace_file(tmp_path: Path) -> None:
    context = _validate_write(tmp_path, "new.txt", "create")

    assert context.resolved_path == str(tmp_path / "new.txt")
    assert context.relative_path == "new.txt"


def test_write_replace_allows_existing_regular_file(tmp_path: Path) -> None:
    target = tmp_path / "notes.txt"
    target.write_text("old", encoding="utf-8")

    context = _validate_write(tmp_path, "notes.txt", "replace")

    assert context.resolved_path == str(target.resolve())


def test_write_create_rejects_existing_file(tmp_path: Path) -> None:
    (tmp_path / "notes.txt").write_text("old", encoding="utf-8")

    with pytest.raises(InvalidToolCallError, match="already exists"):
        _validate_write(tmp_path, "notes.txt", "create")


def test_write_replace_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(InvalidToolCallError, match="does not exist"):
        _validate_write(tmp_path, "missing.txt", "replace")


def test_write_rejects_external_symlink(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside.txt"
    outside.write_text("secret", encoding="utf-8")
    (tmp_path / "link.txt").symlink_to(outside)

    with pytest.raises(InvalidToolCallError, match="escapes workspace"):
        _validate_write(tmp_path, "link.txt", "replace")


@pytest.mark.parametrize("path", [".env", "nested/.hidden/file.txt", "secret.pem"])
def test_write_rejects_hidden_and_sensitive_paths(tmp_path: Path, path: str) -> None:
    with pytest.raises(InvalidToolCallError, match="hidden|sensitive"):
        _validate_write(tmp_path, path, "create")


@pytest.mark.parametrize("path", ["../outside.txt", "nested/../../outside.txt"])
def test_traversal_escape_is_denied(tmp_path: Path, path: str) -> None:
    with pytest.raises(InvalidToolCallError, match="traversal"):
        _validate(tmp_path, "read_file", path)


def test_absolute_path_is_denied(tmp_path: Path) -> None:
    with pytest.raises(InvalidToolCallError, match="absolute"):
        _validate(tmp_path, "read_file", str(tmp_path / "notes.txt"))


def test_external_symlink_is_denied(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside.txt"
    outside.write_text("secret", encoding="utf-8")
    (tmp_path / "link.txt").symlink_to(outside)

    with pytest.raises(InvalidToolCallError, match="escapes workspace"):
        _validate(tmp_path, "read_file", "link.txt")


@pytest.mark.parametrize("path", [".env", "nested/.hidden/file.txt"])
def test_hidden_paths_are_denied(tmp_path: Path, path: str) -> None:
    _touch(tmp_path / path)

    with pytest.raises(InvalidToolCallError, match="hidden"):
        _validate(tmp_path, "read_file", path)


@pytest.mark.parametrize(
    "path",
    [
        "secret.pem",
        "secret.key",
        "secret.p12",
        "secret.pfx",
        "id_rsa",
        "id_ed25519",
        "credentials.json",
        "secrets.local",
        "config.kubeconfig",
    ],
)
def test_sensitive_paths_are_denied(tmp_path: Path, path: str) -> None:
    _touch(tmp_path / path)

    with pytest.raises(InvalidToolCallError, match="sensitive"):
        _validate(tmp_path, "read_file", path)


def test_special_file_is_denied(tmp_path: Path) -> None:
    fifo = tmp_path / "pipe"
    os.mkfifo(fifo)

    with pytest.raises(InvalidToolCallError, match="regular file"):
        _validate(tmp_path, "read_file", "pipe")


def test_socket_path_is_denied_for_directory_tool(tmp_path: Path) -> None:
    sock_path = tmp_path / "sock"
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        sock.bind(str(sock_path))
        assert stat.S_ISSOCK(sock_path.stat().st_mode)
        with pytest.raises(InvalidToolCallError, match="directory"):
            _validate(tmp_path, "list_directory", "sock")
    finally:
        sock.close()


def test_too_long_path_is_denied(tmp_path: Path) -> None:
    path = "a" * 4097

    with pytest.raises(InvalidToolCallError, match="maximum length"):
        _validate(tmp_path, "read_file", path)


@pytest.mark.parametrize("workspace", [None, ""])
def test_missing_workspace_produces_typed_error(workspace: str | None) -> None:
    with pytest.raises(ConfigurationError, match="AI_ASSISTANT_WORKSPACE"):
        WorkspacePathPolicy(workspace)


def _validate(workspace: Path, tool_name: str, path: str):
    catalog = StaticToolCatalog()
    definition = catalog.definition_for(tool_name)
    request = ToolExecutionRequest(
        request_id="req-1",
        session_id="default",
        tool_name=tool_name,
        arguments={"path": path},
    )
    return WorkspacePathPolicy(str(workspace)).validate(request, definition)


def _validate_write(workspace: Path, path: str, mode: str):
    catalog = StaticToolCatalog()
    definition = catalog.definition_for("write")
    request = ToolExecutionRequest(
        request_id="req-1",
        session_id="default",
        tool_name="write",
        arguments={"path": path, "content": "ok", "mode": mode},
    )
    return WorkspacePathPolicy(str(workspace)).validate(request, definition)


def _touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("x", encoding="utf-8")
