"""Tests for UnixSocketToolExecutor."""

import socket
import threading
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
from ai_assistant.tools.framing import decode_frame_header, encode_frame


pytestmark = pytest.mark.integration


def test_executor_transmits_authorized_context(tmp_path: Path) -> None:
    received: list[bytes] = []
    thread = _server(tmp_path / "tool.sock", received, _response("req-1", 1, b"{}"))

    result = UnixSocketToolExecutor(tmp_path / "tool.sock").execute(_context(tmp_path))

    thread.join(timeout=2)
    request = _decode_message(received[0])
    assert result.status == ToolExecutionStatus.SUCCESS
    assert request[1] == b"req-1"
    assert request[2] == b"read_file"
    assert request[3] == str(tmp_path).encode()
    assert request[5] == 1
    assert _request_args(received[0])["path"] == "safe.txt"


def test_executor_maps_read_metadata_to_read_only_transport(tmp_path: Path) -> None:
    received: list[bytes] = []
    thread = _server(tmp_path / "tool.sock", received, _response("req-1", 1, b"{}"))

    result = UnixSocketToolExecutor(tmp_path / "tool.sock").execute(
        _context(tmp_path, permission=ToolPermission.READ_METADATA)
    )

    thread.join(timeout=2)
    request = _decode_message(received[0])
    assert result.status == ToolExecutionStatus.SUCCESS
    assert request[5] == 1


def test_executor_maps_write_workspace_to_write_transport(tmp_path: Path) -> None:
    received: list[bytes] = []
    thread = _server(tmp_path / "tool.sock", received, _response("req-1", 1, b"{}"))

    result = UnixSocketToolExecutor(tmp_path / "tool.sock").execute(
        _context(tmp_path, tool_name="write", permission=ToolPermission.WRITE_WORKSPACE)
    )

    thread.join(timeout=2)
    request = _decode_message(received[0])
    assert result.status == ToolExecutionStatus.SUCCESS
    assert request[5] == 2


def test_executor_maps_execute_project_to_process_transport(tmp_path: Path) -> None:
    received: list[bytes] = []
    thread = _server(tmp_path / "tool.sock", received, _response("req-1", 1, b"{}"))

    result = UnixSocketToolExecutor(tmp_path / "tool.sock").execute(
        _context(tmp_path, tool_name="run_tests", permission=ToolPermission.EXECUTE_PROJECT)
    )

    thread.join(timeout=2)
    request = _decode_message(received[0])
    assert result.status == ToolExecutionStatus.SUCCESS
    assert request[5] == 3


def test_missing_socket_becomes_typed_error(tmp_path: Path) -> None:
    result = UnixSocketToolExecutor(tmp_path / "missing.sock").execute(_context())

    assert result.status == ToolExecutionStatus.ERROR
    assert result.error is not None
    assert result.error.code == "missing_socket"


def test_stale_socket_becomes_connection_refused(tmp_path: Path) -> None:
    socket_path = tmp_path / "stale.sock"
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server:
        server.bind(str(socket_path))

    result = UnixSocketToolExecutor(socket_path).execute(_context())

    assert result.status == ToolExecutionStatus.ERROR
    assert result.error is not None
    assert result.error.code == "connection_refused"


def test_timeout_becomes_typed_error(tmp_path: Path) -> None:
    thread = _server(tmp_path / "tool.sock", [], None, delay=0.2)

    result = UnixSocketToolExecutor(tmp_path / "tool.sock").execute(
        _context(timeout_seconds=0.01)
    )

    thread.join(timeout=1)
    assert result.status == ToolExecutionStatus.TIMEOUT
    assert result.error is not None
    assert result.error.code == "timeout"


def test_malformed_response_becomes_typed_error(tmp_path: Path) -> None:
    thread = _server(tmp_path / "tool.sock", [], b"\xff")

    result = UnixSocketToolExecutor(tmp_path / "tool.sock").execute(_context())

    thread.join(timeout=2)
    assert result.status == ToolExecutionStatus.ERROR
    assert result.error is not None
    assert result.error.code == "malformed_response"


def test_socket_disconnect_becomes_typed_error(tmp_path: Path) -> None:
    thread = _server(tmp_path / "tool.sock", [], None)

    result = UnixSocketToolExecutor(tmp_path / "tool.sock").execute(_context())

    thread.join(timeout=2)
    assert result.status == ToolExecutionStatus.ERROR
    assert result.error is not None
    assert result.error.code == "incomplete_response"


def test_success_response_requires_json_object_content(tmp_path: Path) -> None:
    thread = _server(tmp_path / "tool.sock", [], _response("req-1", 1, b"[]"))

    result = UnixSocketToolExecutor(tmp_path / "tool.sock").execute(_context())

    thread.join(timeout=2)
    assert result.status == ToolExecutionStatus.ERROR
    assert result.error is not None
    assert result.error.code == "invalid_response_schema"


def test_oversized_response_becomes_typed_error(tmp_path: Path) -> None:
    thread = _server(tmp_path / "tool.sock", [], _response("req-1", 1, b"{}"))

    result = UnixSocketToolExecutor(tmp_path / "tool.sock", max_response_bytes=1).execute(
        _context()
    )

    thread.join(timeout=2)
    assert result.status == ToolExecutionStatus.ERROR
    assert result.error is not None
    assert result.error.code == "oversized_response"


def test_response_id_mismatch_becomes_typed_error(tmp_path: Path) -> None:
    thread = _server(tmp_path / "tool.sock", [], _response("other", 1, b"{}"))

    result = UnixSocketToolExecutor(tmp_path / "tool.sock").execute(_context())

    thread.join(timeout=2)
    assert result.status == ToolExecutionStatus.ERROR
    assert result.error is not None
    assert result.error.code == "response_id_mismatch"


def _context(
    workspace: Path | None = None,
    timeout_seconds: float = 5.0,
    permission: ToolPermission = ToolPermission.READ_ONLY,
    tool_name: str = "read_file",
) -> ToolExecutionContext:
    root = workspace or Path.cwd()
    return ToolExecutionContext(
        request=ToolExecutionRequest(
            request_id="req-1",
            session_id="default",
            tool_name=tool_name,
            arguments={"path": "../unsafe.txt", "max_bytes": 8},
            timeout_seconds=timeout_seconds,
            permission=permission,
        ),
        workspace_id=str(root),
        resolved_path=str(root / "safe.txt"),
        relative_path="safe.txt",
    )


def _server(
    socket_path: Path,
    received: list[bytes],
    response: bytes | None,
    delay: float = 0,
) -> threading.Thread:
    ready = threading.Event()

    def run() -> None:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server:
            server.bind(str(socket_path))
            server.listen(1)
            ready.set()
            connection, _ = server.accept()
            with connection:
                header = connection.recv(4)
                length = decode_frame_header(header)
                received.append(connection.recv(length))
                if delay:
                    time.sleep(delay)
                if response is not None:
                    connection.sendall(encode_frame(response))

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    ready.wait(timeout=2)
    return thread


def _response(request_id: str, status: int, stdout_data: bytes) -> bytes:
    return _string(1, request_id) + _varint_field(2, status) + _bytes(4, stdout_data)


def _request_args(payload: bytes) -> dict[str, str]:
    args: dict[str, str] = {}
    offset = 0
    while offset < len(payload):
        tag, offset = _read_varint(payload, offset)
        field_number = tag >> 3
        wire_type = tag & 0x07
        if wire_type == 0:
            _, offset = _read_varint(payload, offset)
        elif wire_type == 2:
            data, offset = _read_bytes(payload, offset)
            if field_number == 6:
                entry = _decode_message(data)
                args[entry[1].decode()] = entry[2].decode()
        else:
            raise ValueError("unsupported wire type")
    return args


def _decode_message(payload: bytes) -> dict[int, bytes | int]:
    fields: dict[int, bytes | int] = {}
    offset = 0
    while offset < len(payload):
        tag, offset = _read_varint(payload, offset)
        field_number = tag >> 3
        wire_type = tag & 0x07
        if wire_type == 0:
            fields[field_number], offset = _read_varint(payload, offset)
        elif wire_type == 2:
            fields[field_number], offset = _read_bytes(payload, offset)
        else:
            raise ValueError("unsupported wire type")
    return fields


def _read_bytes(payload: bytes, offset: int) -> tuple[bytes, int]:
    size, offset = _read_varint(payload, offset)
    return payload[offset : offset + size], offset + size


def _read_varint(payload: bytes, offset: int) -> tuple[int, int]:
    shift = 0
    value = 0
    while True:
        byte = payload[offset]
        offset += 1
        value |= (byte & 0x7F) << shift
        if byte < 0x80:
            return value, offset
        shift += 7


def _varint(value: int) -> bytes:
    chunks: list[int] = []
    while value >= 0x80:
        chunks.append((value & 0x7F) | 0x80)
        value >>= 7
    chunks.append(value)
    return bytes(chunks)


def _field(field_number: int, wire_type: int) -> bytes:
    return _varint((field_number << 3) | wire_type)


def _string(field_number: int, value: str) -> bytes:
    data = value.encode()
    return _field(field_number, 2) + _varint(len(data)) + data


def _bytes(field_number: int, value: bytes) -> bytes:
    return _field(field_number, 2) + _varint(len(value)) + value


def _varint_field(field_number: int, value: int) -> bytes:
    return _field(field_number, 0) + _varint(value)
