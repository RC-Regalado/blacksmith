"""Length-prefixed framing helpers for socket transports."""

import struct


FRAME_HEADER_SIZE = 4
MAX_FRAME_LENGTH = 64 * 1024 * 1024


class FrameError(RuntimeError):
    """Raised when a framed message is malformed."""


def encode_frame(payload: bytes) -> bytes:
    if not payload:
        raise FrameError("Payload cannot be empty.")
    if len(payload) > MAX_FRAME_LENGTH:
        raise FrameError("Payload exceeds maximum frame length.")

    return struct.pack(">I", len(payload)) + payload


def decode_frame_header(header: bytes) -> int:
    if len(header) != FRAME_HEADER_SIZE:
        raise FrameError("Frame header must be exactly 4 bytes.")

    length = struct.unpack(">I", header)[0]
    if length == 0:
        raise FrameError("Frame payload length cannot be zero.")
    if length > MAX_FRAME_LENGTH:
        raise FrameError("Frame payload exceeds maximum length.")
    return length

