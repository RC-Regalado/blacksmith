"""Tests for length-prefixed framing helpers."""

import struct

import pytest

from ai_assistant.tools.framing import decode_frame_header, encode_frame


pytestmark = pytest.mark.unit


def test_encode_frame_uses_big_endian_length_header() -> None:
    frame = encode_frame(b"abc")

    assert frame == struct.pack(">I", 3) + b"abc"


def test_decode_frame_header_reads_big_endian_length() -> None:
    assert decode_frame_header(b"\x00\x00\x00\x03") == 3
