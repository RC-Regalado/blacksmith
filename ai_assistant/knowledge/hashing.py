"""Content hashing helpers for derived knowledge."""

from hashlib import sha256


def hash_bytes(content: bytes) -> str:
    return sha256(content).hexdigest()


def hash_text(content: str) -> str:
    return hash_bytes(content.encode("utf-8"))
