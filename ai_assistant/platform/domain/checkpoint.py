"""Logical checkpoint domain model."""

from dataclasses import dataclass
from datetime import datetime
from types import MappingProxyType
from typing import Mapping

from ai_assistant.domain.errors import InvalidToolCallError


_FORBIDDEN_METADATA_KEYS = frozenset(
    {"filesystem_snapshot", "file_contents", "rollback_path"}
)


@dataclass(frozen=True, slots=True)
class Checkpoint:
    checkpoint_id: str
    execution_id: str
    task_id: str
    metadata: Mapping[str, object]
    created_at: datetime

    def __post_init__(self) -> None:
        _require_text(self.checkpoint_id, "checkpoint_id")
        _require_text(self.execution_id, "execution_id")
        _require_text(self.task_id, "task_id")
        keys = set(self.metadata)
        if keys & _FORBIDDEN_METADATA_KEYS:
            raise InvalidToolCallError("checkpoint metadata must not store filesystem state.")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


def _require_text(value: str, name: str) -> None:
    if not isinstance(value, str) or not value:
        raise InvalidToolCallError(f"{name} must be a non-empty string.")
