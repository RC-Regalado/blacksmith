"""Tests for length-prefixed framing helpers."""

import struct
import unittest

from ai_assistant.tools.framing import decode_frame_header, encode_frame


class FramingTests(unittest.TestCase):
    def test_encode_frame_uses_big_endian_length_header(self) -> None:
        frame = encode_frame(b"abc")

        self.assertEqual(frame, struct.pack(">I", 3) + b"abc")

    def test_decode_frame_header_reads_big_endian_length(self) -> None:
        self.assertEqual(decode_frame_header(b"\x00\x00\x00\x03"), 3)


if __name__ == "__main__":
    unittest.main()

