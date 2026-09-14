"""Provider-neutral model response metadata (ADR-068)."""

from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Mapping

from ai_assistant.domain.message import Message


class FinishReason(StrEnum):
    STOP = "stop"
    LENGTH = "length"
    TOOL_CALL = "tool_call"
    ERROR = "error"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class ModelResponse:
    message: Message
    finish_reason: FinishReason = FinishReason.UNKNOWN
    prompt_tokens: int | None = None
    output_tokens: int | None = None
    duration_ms: float | None = None
    truncated: bool = False
    metadata: Mapping[str, object] = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if not isinstance(self.metadata, MappingProxyType):
            object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))
