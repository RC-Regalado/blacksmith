"""Tests for the Unix socket protobuf client."""

import socket
import threading
from pathlib import Path

import pytest

from ai_assistant.tools.framing import decode_frame_header, encode_frame
from ai_assistant.tools.unix_socket_client import UnixSocketProtobufClient


pytestmark = pytest.mark.integration


class FakeProto:
    def __init__(self, payload: bytes) -> None:
        self._payload = payload

    def SerializeToString(self) -> bytes:
        return self._payload


def test_send_writes_length_prefixed_payload(tmp_path: Path) -> None:
    socket_path = tmp_path / "toolserver.sock"
    received: list[bytes] = []
    thread = start_server(socket_path, received)

    client = UnixSocketProtobufClient(socket_path)
    client.send(FakeProto(b"payload"))

    thread.join(timeout=2)
    assert received == [b"payload"]


def test_request_returns_framed_response_payload(tmp_path: Path) -> None:
    socket_path = tmp_path / "toolserver.sock"
    received: list[bytes] = []
    thread = start_server(socket_path, received, b"ok")

    client = UnixSocketProtobufClient(socket_path)
    response = client.request(FakeProto(b"payload"))

    thread.join(timeout=2)
    assert received == [b"payload"]
    assert response == b"ok"


def start_server(
    socket_path: Path,
    received: list[bytes],
    response: bytes | None = None,
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
                if response is not None:
                    connection.sendall(encode_frame(response))

    thread = threading.Thread(target=run)
    thread.start()
    ready.wait(timeout=2)
    return thread
