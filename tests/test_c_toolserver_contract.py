"""Contract tests for C toolserver actions."""

import hashlib
import json
import subprocess
import tempfile
import time
from pathlib import Path

import pytest

from ai_assistant.domain.tools import (
    ToolExecutionContext,
    ToolExecutionRequest,
    ToolExecutionStatus,
    ToolPermission,
)
from ai_assistant.infrastructure.tools import UnixSocketToolExecutor
from ai_assistant.tools.unix_socket_client import UnixSocketProtobufClient


pytestmark = pytest.mark.toolserver


class RawProto:
    def __init__(self, payload: bytes) -> None:
        self._payload = payload

    def SerializeToString(self) -> bytes:
        return self._payload


def test_c_toolserver_reads_bounded_file(tmp_path: Path) -> None:
    binary = build_toolserver_or_skip()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "notes.txt").write_text("abcdef", encoding="utf-8")

    response = run_toolserver_request(
        build_tool_request(
            request_id="read-1",
            tool_name="read_file",
            workspace_id=str(workspace),
            args={"path": "notes.txt", "max_bytes": "3"},
        ),
        binary,
    )

    assert response[1] == b"read-1"
    assert response[2] == 1
    assert response[3] == b"file read"
    assert b'"bytes_read":3' in response[4]
    assert b'"truncated":true' in response[4]


def test_c_toolserver_returns_file_metadata_without_content(tmp_path: Path) -> None:
    binary = build_toolserver_or_skip()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "notes.txt").write_text("abcdef", encoding="utf-8")

    response = run_toolserver_request(
        build_tool_request(
            request_id="metadata-1",
            tool_name="file_metadata",
            workspace_id=str(workspace),
            args={"path": "notes.txt"},
        ),
        binary,
    )

    assert response[1] == b"metadata-1"
    assert response[2] == 1
    assert response[3] == b"file metadata"
    assert b'"type":"file"' in response[4]
    assert b'"size":6' in response[4]
    assert b"abcdef" not in response[4]


def test_unix_socket_executor_reads_from_c_toolserver(tmp_path: Path) -> None:
    binary = build_toolserver_or_skip()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    target = workspace / "notes.txt"
    target.write_text("abcdef", encoding="utf-8")

    with tempfile.TemporaryDirectory() as directory:
        socket_path = Path(directory) / "toolserver.sock"
        process = subprocess.Popen([str(binary), "--socket", str(socket_path)])
        try:
            wait_for_socket(socket_path)
            result = UnixSocketToolExecutor(socket_path).execute(
                ToolExecutionContext(
                    request=ToolExecutionRequest(
                        request_id="exec-1",
                        session_id="default",
                        tool_name="read_file",
                        arguments={"path": "notes.txt", "max_bytes": 3},
                    ),
                    workspace_id=str(workspace),
                    resolved_path=str(target),
                    relative_path="notes.txt",
                )
            )
        finally:
            process.terminate()
            process.wait(timeout=2)

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.content is not None
    assert result.content["content"] == "abc"
    assert result.content["bytes_read"] == 3
    assert result.truncated is True


def test_unix_socket_executor_gets_metadata_from_c_toolserver(tmp_path: Path) -> None:
    binary = build_toolserver_or_skip()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    target = workspace / "notes.txt"
    target.write_text("abcdef", encoding="utf-8")

    with tempfile.TemporaryDirectory() as directory:
        socket_path = Path(directory) / "toolserver.sock"
        process = subprocess.Popen([str(binary), "--socket", str(socket_path)])
        try:
            wait_for_socket(socket_path)
            result = UnixSocketToolExecutor(socket_path).execute(
                ToolExecutionContext(
                    request=ToolExecutionRequest(
                        request_id="metadata-exec-1",
                        session_id="default",
                        tool_name="file_metadata",
                        arguments={"path": "notes.txt"},
                        permission=ToolPermission.READ_METADATA,
                    ),
                    workspace_id=str(workspace),
                    resolved_path=str(target),
                    relative_path="notes.txt",
                )
            )
        finally:
            process.terminate()
            process.wait(timeout=2)

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.content is not None
    assert result.content["type"] == "file"
    assert result.content["size"] == 6
    assert "content" not in result.content


def test_c_toolserver_lists_directory_without_hidden_entries(tmp_path: Path) -> None:
    binary = build_toolserver_or_skip()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "visible.txt").write_text("x", encoding="utf-8")
    (workspace / ".env").write_text("secret", encoding="utf-8")

    response = run_toolserver_request(
        build_tool_request(
            request_id="list-1",
            tool_name="list_directory",
            workspace_id=str(workspace),
            args={"path": "."},
        ),
        binary,
    )

    assert response[2] == 1
    assert b"visible.txt" in response[4]
    assert b".env" not in response[4]


def test_c_toolserver_rejects_traversal_and_external_symlink(tmp_path: Path) -> None:
    binary = build_toolserver_or_skip()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("secret", encoding="utf-8")
    (workspace / "link.txt").symlink_to(outside)

    traversal = run_toolserver_request(
        build_tool_request(
            request_id="deny-1",
            tool_name="read_file",
            workspace_id=str(workspace),
            args={"path": "../outside.txt"},
        ),
        binary,
    )
    symlink = run_toolserver_request(
        build_tool_request(
            request_id="deny-2",
            tool_name="read_file",
            workspace_id=str(workspace),
            args={"path": "link.txt"},
        ),
        binary,
    )

    assert traversal[2] == 3
    assert symlink[2] == 3


def test_c_toolserver_creates_file_atomically_without_echoing_content(tmp_path: Path) -> None:
    binary = build_toolserver_or_skip()
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    response = run_toolserver_request(
        build_tool_request(
            request_id="write-1",
            tool_name="write",
            workspace_id=str(workspace),
            permission=2,
            args={"path": "notes.txt", "mode": "create", "content": "hello"},
        ),
        binary,
    )

    body = json.loads(response[4].decode())
    assert response[2] == 1
    assert (workspace / "notes.txt").read_text(encoding="utf-8") == "hello"
    assert body["before_sha256"] is None
    assert body["after_sha256"] == hashlib.sha256(b"hello").hexdigest()
    assert "hello" not in body.values()


def test_c_toolserver_replaces_file_with_expected_hash(tmp_path: Path) -> None:
    binary = build_toolserver_or_skip()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    target = workspace / "notes.txt"
    target.write_text("old", encoding="utf-8")
    before_hash = hashlib.sha256(b"old").hexdigest()

    response = run_toolserver_request(
        build_tool_request(
            request_id="write-2",
            tool_name="write",
            workspace_id=str(workspace),
            permission=2,
            args={
                "path": "notes.txt",
                "mode": "replace",
                "content": "new",
                "expected_sha256": before_hash,
            },
        ),
        binary,
    )

    body = json.loads(response[4].decode())
    assert response[2] == 1
    assert target.read_text(encoding="utf-8") == "new"
    assert body["before_sha256"] == before_hash
    assert body["after_sha256"] == hashlib.sha256(b"new").hexdigest()


def test_c_toolserver_hash_mismatch_fails_without_replacing_or_temp(tmp_path: Path) -> None:
    binary = build_toolserver_or_skip()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    target = workspace / "notes.txt"
    target.write_text("old", encoding="utf-8")

    response = run_toolserver_request(
        build_tool_request(
            request_id="write-3",
            tool_name="write",
            workspace_id=str(workspace),
            permission=2,
            args={
                "path": "notes.txt",
                "mode": "replace",
                "content": "new",
                "expected_sha256": "0" * 64,
            },
        ),
        binary,
    )

    assert response[2] == 3
    assert target.read_text(encoding="utf-8") == "old"
    assert not list(workspace.glob(".blacksmith-write.*"))


def test_c_toolserver_rejects_external_symlink_write(tmp_path: Path) -> None:
    binary = build_toolserver_or_skip()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("secret", encoding="utf-8")
    (workspace / "link.txt").symlink_to(outside)

    response = run_toolserver_request(
        build_tool_request(
            request_id="write-4",
            tool_name="write",
            workspace_id=str(workspace),
            permission=2,
            args={"path": "link.txt", "mode": "replace", "content": "new"},
        ),
        binary,
    )

    assert response[2] == 3
    assert outside.read_text(encoding="utf-8") == "secret"


def test_c_toolserver_searches_text(tmp_path: Path) -> None:
    binary = build_toolserver_or_skip()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "notes.txt").write_text("alpha\nneedle here\n", encoding="utf-8")

    response = run_toolserver_request(
        build_tool_request(
            request_id="search-1",
            tool_name="search_text",
            workspace_id=str(workspace),
            args={"path": ".", "query": "needle"},
        ),
        binary,
    )

    body = json.loads(response[4].decode())
    assert response[2] == 1
    assert body["matches"][0]["path"] == "notes.txt"
    assert body["matches"][0]["line"] == 2


def test_c_toolserver_reports_git_status_and_diff(tmp_path: Path) -> None:
    binary = build_toolserver_or_skip()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    subprocess.run(["git", "init"], cwd=workspace, check=True, capture_output=True)
    (workspace / "tracked.txt").write_text("old\n", encoding="utf-8")
    subprocess.run(["git", "add", "tracked.txt"], cwd=workspace, check=True)
    subprocess.run(
        ["git", "-c", "user.name=test", "-c", "user.email=test@example.com", "commit", "-m", "init"],
        cwd=workspace,
        check=True,
        capture_output=True,
    )
    (workspace / "tracked.txt").write_text("new\n", encoding="utf-8")

    status = run_toolserver_request(
        build_tool_request(
            request_id="git-status-1",
            tool_name="git_status",
            workspace_id=str(workspace),
            args={"path": "."},
        ),
        binary,
    )
    diff = run_toolserver_request(
        build_tool_request(
            request_id="git-diff-1",
            tool_name="git_diff",
            workspace_id=str(workspace),
            args={"path": ".", "scope": "worktree"},
        ),
        binary,
    )

    assert status[2] == 1
    assert b"tracked.txt" in status[4]
    assert diff[2] == 1
    assert b"+new" in diff[4]


def test_c_toolserver_runs_build_profile_from_repo_root() -> None:
    binary = build_toolserver_or_skip()

    response = run_toolserver_request(
        build_tool_request(
            request_id="build-1",
            tool_name="build_project",
            workspace_id=str(Path.cwd()),
            permission=3,
            args={"path": ".", "profile_id": "python-compile"},
        ),
        binary,
    )

    body = json.loads(response[4].decode())
    assert response[2] == 1
    assert body["profile_id"] == "python-compile"
    assert body["exit_code"] == 0


def test_c_toolserver_runs_test_profile_from_repo_root() -> None:
    binary = build_toolserver_or_skip()

    response = run_toolserver_request(
        build_tool_request(
            request_id="run-tests-1",
            tool_name="run_tests",
            workspace_id=str(Path.cwd()),
            permission=3,
            args={"path": ".", "profile_id": "core-tests"},
        ),
        binary,
    )

    body = json.loads(response[4].decode())
    assert response[2] == 1
    assert body["profile_id"] == "core-tests"
    assert isinstance(body["exit_code"], int)
    assert "stdout" in body


def test_c_toolserver_only_allows_read_only_actions(tmp_path: Path) -> None:
    binary = build_toolserver_or_skip()
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    response = run_toolserver_request(
        build_tool_request(
            request_id="unknown-1",
            tool_name="echo",
            workspace_id=str(workspace),
            args={"message": "hello"},
        ),
        binary,
    )

    assert response[2] == 4


def test_c_toolserver_malformed_protobuf_fails_safely() -> None:
    binary = build_toolserver_or_skip()

    response = run_toolserver_request(b"\xff\xff\xff", binary)

    assert response[2] == 5
    assert response[3] == b"invalid protobuf"


def build_toolserver_or_skip() -> Path:
    result = subprocess.run(
        ["make", "-C", "c_toolserver"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        pytest.skip(f"C toolserver build unavailable: {result.stderr or result.stdout}")
    return Path("c_toolserver/build/toolserver")


def run_toolserver_request(payload: bytes, binary: Path | None = None) -> dict[int, bytes | int]:
    executable = binary or Path("c_toolserver/build/toolserver")
    with tempfile.TemporaryDirectory() as directory:
        socket_path = Path(directory) / "toolserver.sock"
        process = subprocess.Popen([str(executable), "--socket", str(socket_path)])
        try:
            wait_for_socket(socket_path)
            response = UnixSocketProtobufClient(socket_path).request(RawProto(payload))
            return decode_response(response)
        finally:
            process.terminate()
            process.wait(timeout=2)


def build_tool_request(
    request_id: str,
    tool_name: str,
    workspace_id: str,
    args: dict[str, str],
    permission: int = 1,
) -> bytes:
    chunks = [
        encode_string(1, request_id),
        encode_string(2, tool_name),
        encode_string(3, workspace_id),
        encode_varint_field(5, permission),
    ]
    chunks.extend(encode_map_entry(key, value) for key, value in args.items())
    return b"".join(chunks)


def encode_varint(value: int) -> bytes:
    chunks: list[int] = []
    while value >= 0x80:
        chunks.append((value & 0x7F) | 0x80)
        value >>= 7
    chunks.append(value)
    return bytes(chunks)


def encode_field(field_number: int, wire_type: int) -> bytes:
    return encode_varint((field_number << 3) | wire_type)


def encode_string(field_number: int, value: str) -> bytes:
    data = value.encode()
    return encode_field(field_number, 2) + encode_varint(len(data)) + data


def encode_varint_field(field_number: int, value: int) -> bytes:
    return encode_field(field_number, 0) + encode_varint(value)


def encode_map_entry(key: str, value: str) -> bytes:
    entry = encode_string(1, key) + encode_string(2, value)
    return encode_field(6, 2) + encode_varint(len(entry)) + entry


def read_varint(payload: bytes, offset: int) -> tuple[int, int]:
    shift = 0
    value = 0
    while True:
        byte = payload[offset]
        offset += 1
        value |= (byte & 0x7F) << shift
        if byte < 0x80:
            return value, offset
        shift += 7


def decode_length_delimited(payload: bytes, offset: int) -> tuple[bytes, int]:
    size, offset = read_varint(payload, offset)
    return payload[offset : offset + size], offset + size


def decode_response(payload: bytes) -> dict[int, bytes | int]:
    fields: dict[int, bytes | int] = {}
    offset = 0
    while offset < len(payload):
        tag, offset = read_varint(payload, offset)
        field_number = tag >> 3
        wire_type = tag & 0x07
        if wire_type == 0:
            fields[field_number], offset = read_varint(payload, offset)
        elif wire_type == 2:
            fields[field_number], offset = decode_length_delimited(payload, offset)
        else:
            raise ValueError(f"Unsupported wire type: {wire_type}")
    return fields


def wait_for_socket(socket_path: Path) -> None:
    for _ in range(50):
        if socket_path.exists():
            return
        time.sleep(0.02)
    raise TimeoutError(f"Socket was not created: {socket_path}")
