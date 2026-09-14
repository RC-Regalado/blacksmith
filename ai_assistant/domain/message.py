"""Provider-neutral message model."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Literal

from ai_assistant.domain.errors import InvalidMessageError


Role = Literal["system", "user", "assistant", "tool"]


class MessageProvenance(StrEnum):
    SYSTEM_POLICY = "system_policy"
    OPERATOR_INPUT = "operator_input"
    MODEL_OUTPUT = "model_output"
    RETRIEVED_KNOWLEDGE = "retrieved_knowledge"
    TOOL_RESULT = "tool_result"
    RUNTIME_DIAGNOSTIC = "runtime_diagnostic"


@dataclass(frozen=True, slots=True)
class Message:
    role: Role
    content: str
    session_id: str | None = None
    tool_name: str | None = None
    tool_call_id: str | None = None
    provenance: MessageProvenance | str | None = None

    def __post_init__(self) -> None:
        if not self.content:
            raise InvalidMessageError("Message content cannot be empty.")
        provenance = (
            _default_provenance(self.role)
            if self.provenance is None
            else MessageProvenance(self.provenance)
        )
        object.__setattr__(self, "provenance", provenance)


def _default_provenance(role: Role) -> MessageProvenance:
    if role == "user":
        return MessageProvenance.OPERATOR_INPUT
    if role == "assistant":
        return MessageProvenance.MODEL_OUTPUT
    if role == "tool":
        return MessageProvenance.TOOL_RESULT
    return MessageProvenance.RUNTIME_DIAGNOSTIC
