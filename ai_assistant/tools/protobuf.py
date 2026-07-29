"""Small protobuf protocol types without depending on generated classes."""

from typing import Protocol


class SerializableProto(Protocol):
    def SerializeToString(self) -> bytes:
        """Return the protobuf wire-format payload."""

