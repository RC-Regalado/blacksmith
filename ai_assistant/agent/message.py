"""Message abstraction used across the agent runtime."""

from dataclasses import dataclass
from typing import Literal


Role = Literal["system", "user", "assistant", "tool"]


@dataclass(frozen=True, slots=True)
class Message:
    role: Role
    content: str
    session_id: str | None = None
    tool_name: str | None = None
    tool_call_id: str | None = None

    def __post_init__(self) -> None:
        if not self.content:
            raise ValueError("Message content cannot be empty.")
