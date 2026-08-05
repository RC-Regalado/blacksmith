"""Unix socket tool executor adapter."""

import json
import socket
from dataclasses import dataclass
from pathlib import Path

from ai_assistant.application.ports.tools import ToolExecutor
from ai_assistant.domain.tools import (
    SanitizedToolError,
    ToolExecutionContext,
    ToolExecutionResult,
    ToolExecutionStatus,
    ToolPermission,
)
from ai_assistant.tools.framing import FrameError
from ai_assistant.tools.unix_socket_client import (
    UnixSocketClientError,
    UnixSocketProtobufClient,
)

_OK = 1
_ERROR = 2
_DENIED = 3
_TIMEOUT = 6
_READ_ONLY = 1
_WRITE_WORKSPACE = 2
_PROCESS_EXEC = 3


@dataclass(frozen=True, slots=True)
class _RawProto:
    payload: bytes

    def SerializeToString(self) -> bytes:
        return self.payload


@dataclass(frozen=True, slots=True)
class UnixSocketToolExecutor(ToolExecutor):
    socket_path: Path
    max_response_bytes: int = 1_048_576

    def execute(self, context: ToolExecutionContext) -> ToolExecutionResult:
        if not self.socket_path.exists():
            return _failure(context, ToolExecutionStatus.ERROR, "missing_socket")
        try:
            payload = UnixSocketProtobufClient(
                self.socket_path,
                context.request.timeout_seconds,
            ).request(_RawProto(_encode_request(context)))
            if len(payload) > self.max_response_bytes:
                return _failure(context, ToolExecutionStatus.ERROR, "oversized_response")
            return _decode_result(context, payload)
        except FileNotFoundError:
            return _failure(context, ToolExecutionStatus.ERROR, "missing_socket")
        except TimeoutError:
            return _failure(context, ToolExecutionStatus.TIMEOUT, "timeout")
        except socket.timeout:
            return _failure(context, ToolExecutionStatus.TIMEOUT, "timeout")
        except (FrameError, UnixSocketClientError, OSError, ValueError, json.JSONDecodeError):
            return _failure(context, ToolExecutionStatus.ERROR, "malformed_response")


def _encode_request(context: ToolExecutionContext) -> bytes:
    request = context.request
    args = {key: str(value) for key, value in request.arguments.items()}
    if context.relative_path:
        args["path"] = context.relative_path
    parts = [
        _string(1, request.request_id),
        _string(2, request.tool_name),
        _string(3, context.workspace_id),
        _string(4, request.session_id),
        _varint_field(5, _permission(request.permission)),
        _varint_field(7, int(request.timeout_seconds * 1000)),
        _varint_field(8, int(request.dry_run)),
    ]
    parts.extend(_map_entry(key, value) for key, value in args.items())
    return b"".join(parts)


def _decode_result(context: ToolExecutionContext, payload: bytes) -> ToolExecutionResult:
    fields = _decode_message(payload)
    request_id = _text(fields.get(1, b""))
    if request_id != context.request.request_id:
        return _failure(context, ToolExecutionStatus.ERROR, "response_id_mismatch")
    status = int(fields.get(2, 0))
    if status == _OK:
        content = json.loads(bytes(fields.get(4, b"{}")).decode("utf-8"))
        content.setdefault("path", context.relative_path)
        return ToolExecutionResult(
            request_id=request_id,
            tool_name=context.request.tool_name,
            status=ToolExecutionStatus.SUCCESS,
            content=content,
            truncated=bool(content.get("truncated", False)),
        )
    return _failure(context, _status(status), _error_code(fields, status))


def _failure(
    context: ToolExecutionContext,
    status: ToolExecutionStatus,
    code: str,
) -> ToolExecutionResult:
    return ToolExecutionResult(
        request_id=context.request.request_id,
        tool_name=context.request.tool_name,
        status=status,
        error=SanitizedToolError(code=code, message="Tool execution failed."),
    )


def _status(value: int) -> ToolExecutionStatus:
    if value == _TIMEOUT:
        return ToolExecutionStatus.TIMEOUT
    if value == _DENIED:
        return ToolExecutionStatus.DENIED
    return ToolExecutionStatus.ERROR


def _error_code(fields: dict[int, bytes | int], status: int) -> str:
    error = fields.get(8)
    if isinstance(error, bytes):
        nested = _decode_message(error)
        code = _text(nested.get(1, b""))
        if code:
            return code
    return {
        _ERROR: "tool_error",
        _DENIED: "tool_denied",
        _TIMEOUT: "timeout",
    }.get(status, "tool_error")


def _permission(permission: ToolPermission) -> int:
    if permission in {
        ToolPermission.READ_ONLY,
        ToolPermission.READ_METADATA,
        ToolPermission.READ_CONTENT,
        ToolPermission.READ_REPOSITORY,
    }:
        return _READ_ONLY
    if permission == ToolPermission.WRITE_WORKSPACE:
        return _WRITE_WORKSPACE
    if permission == ToolPermission.EXECUTE_PROJECT:
        return _PROCESS_EXEC
    return 0


def _text(value: bytes | int | object) -> str:
    return value.decode("utf-8") if isinstance(value, bytes) else ""


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
            raise ValueError("unsupported protobuf wire type")
    return fields


def _read_bytes(payload: bytes, offset: int) -> tuple[bytes, int]:
    size, offset = _read_varint(payload, offset)
    end = offset + size
    if end > len(payload):
        raise ValueError("truncated protobuf field")
    return payload[offset:end], end


def _read_varint(payload: bytes, offset: int) -> tuple[int, int]:
    shift = 0
    value = 0
    while offset < len(payload) and shift < 64:
        byte = payload[offset]
        offset += 1
        value |= (byte & 0x7F) << shift
        if byte < 0x80:
            return value, offset
        shift += 7
    raise ValueError("invalid protobuf varint")


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
    data = value.encode("utf-8")
    return _field(field_number, 2) + _varint(len(data)) + data


def _varint_field(field_number: int, value: int) -> bytes:
    return _field(field_number, 0) + _varint(value)


def _map_entry(key: str, value: str) -> bytes:
    entry = _string(1, key) + _string(2, value)
    return _field(6, 2) + _varint(len(entry)) + entry
