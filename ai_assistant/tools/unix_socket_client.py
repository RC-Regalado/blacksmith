"""Unix domain socket client for framed protobuf messages."""

import socket
from dataclasses import dataclass
from pathlib import Path

from ai_assistant.tools.framing import FRAME_HEADER_SIZE, decode_frame_header, encode_frame
from ai_assistant.tools.protobuf import SerializableProto


class UnixSocketClientError(RuntimeError):
    """Raised when communication with the Unix socket server fails."""

    def __init__(self, message: str, code: str = "socket_error") -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True, slots=True)
class UnixSocketProtobufClient:
    socket_path: Path
    timeout_seconds: float = 5.0

    def send(self, message: SerializableProto) -> None:
        payload = self._serialize(message)
        with self._connect() as connection:
            connection.sendall(encode_frame(payload))

    def request(self, message: SerializableProto) -> bytes:
        payload = self._serialize(message)
        with self._connect() as connection:
            connection.sendall(encode_frame(payload))
            return self._read_frame(connection)

    def _connect(self) -> socket.socket:
        if not self.socket_path.exists():
            raise UnixSocketClientError(
                f"Socket does not exist: {self.socket_path}",
                "missing_socket",
            )

        connection = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        connection.settimeout(self.timeout_seconds)
        try:
            connection.connect(str(self.socket_path))
        except ConnectionRefusedError as exc:
            connection.close()
            raise UnixSocketClientError(
                "Cannot connect to socket: connection refused",
                "connection_refused",
            ) from exc
        except OSError as exc:
            connection.close()
            raise UnixSocketClientError(
                f"Cannot connect to socket: {exc}",
                "socket_unavailable",
            ) from exc
        return connection

    def _serialize(self, message: SerializableProto) -> bytes:
        try:
            payload = message.SerializeToString()
        except AttributeError as exc:
            raise TypeError("Message must implement SerializeToString().") from exc

        if not isinstance(payload, bytes):
            raise TypeError("SerializeToString() must return bytes.")
        return payload

    def _read_frame(self, connection: socket.socket) -> bytes:
        header = self._read_exact(connection, FRAME_HEADER_SIZE)
        length = decode_frame_header(header)
        return self._read_exact(connection, length)

    def _read_exact(self, connection: socket.socket, size: int) -> bytes:
        chunks: list[bytes] = []
        remaining = size
        while remaining:
            chunk = connection.recv(remaining)
            if not chunk:
                raise UnixSocketClientError(
                    "Socket closed before frame was complete.",
                    "incomplete_response",
                )
            chunks.append(chunk)
            remaining -= len(chunk)
        return b"".join(chunks)
