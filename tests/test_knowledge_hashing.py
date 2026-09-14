"""Tests for knowledge content hashing."""

import pytest

from ai_assistant.knowledge import hash_bytes, hash_text


pytestmark = pytest.mark.unit


def test_hash_text_matches_utf8_bytes() -> None:
    assert hash_text("hello") == hash_bytes(b"hello")


def test_hash_text_changes_when_content_changes() -> None:
    assert hash_text("hello") != hash_text("hello!")
