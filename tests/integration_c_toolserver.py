"""Integration check for Python framed client and C tool server."""

import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ai_assistant.tools.unix_socket_client import UnixSocketProtobufClient


class RawProto:
    def __init__(self, payload: bytes) -> None:
        self._payload = payload

    def SerializeToString(self) -> bytes:
        return self._payload


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


def build_tool_request() -> bytes:
    return b"".join(
        [
            encode_string(1, "integration-1"),
            encode_string(2, "echo"),
            encode_varint_field(5, 1),
            encode_map_entry("message", "hello from python"),
        ]
    )


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


def main() -> None:
    binary = Path("c_toolserver/build/toolserver")
    with tempfile.TemporaryDirectory() as directory:
        socket_path = Path(directory) / "toolserver.sock"
        process = subprocess.Popen([str(binary), "--socket", str(socket_path)])
        try:
            wait_for_socket(socket_path)
            client = UnixSocketProtobufClient(socket_path)
            payload = client.request(RawProto(build_tool_request()))
            response = decode_response(payload)
        finally:
            process.terminate()
            process.wait(timeout=2)

    assert response[2] == 1
    assert response[3] == b"echo completed"
    assert response[4] == b"hello from python"


if __name__ == "__main__":
    main()
