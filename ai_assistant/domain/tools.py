"""Declarative tool-call domain models."""

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True, slots=True)
class ToolDefinition:
    name: str
    description: str
    input_schema: Mapping[str, object]


@dataclass(frozen=True, slots=True)
class ToolCall:
    name: str
    arguments: Mapping[str, object]
    tool_call_id: str | None = None


@dataclass(frozen=True, slots=True)
class ToolCallPlan:
    has_tool_call: bool
    tool_call: ToolCall | None = None

    @property
    def tool_name(self) -> str | None:
        return self.tool_call.name if self.tool_call else None
