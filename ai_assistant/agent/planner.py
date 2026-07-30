"""Tool-call planning placeholders."""

from dataclasses import dataclass
import json
from typing import Any, Mapping

from ai_assistant.agent.message import Message
from ai_assistant.application.errors import InvalidToolCallError


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


class ToolCallInterpreter:
    def interpret(self, message: Message) -> ToolCallPlan:
        if message.role != "assistant":
            return ToolCallPlan(has_tool_call=False)

        content = self._json_object(message.content)
        if not content or "tool_call" not in content:
            return ToolCallPlan(has_tool_call=False)
        return ToolCallPlan(
            has_tool_call=True,
            tool_call=self._tool_call(content["tool_call"]),
        )

    def _json_object(self, content: str) -> dict[str, Any] | None:
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            return None
        if not isinstance(data, dict):
            return None
        return data

    def _tool_call(self, data: Any) -> ToolCall:
        if not isinstance(data, dict):
            raise InvalidToolCallError("tool_call must be an object.")
        name = data.get("name")
        arguments = data.get("arguments", {})
        tool_call_id = data.get("id")
        if not isinstance(name, str) or not name:
            raise InvalidToolCallError("tool_call.name must be a non-empty string.")
        if not isinstance(arguments, dict):
            raise InvalidToolCallError("tool_call.arguments must be an object.")
        if tool_call_id is not None and not isinstance(tool_call_id, str):
            raise InvalidToolCallError("tool_call.id must be a string.")
        return ToolCall(
            name=name,
            arguments=arguments,
            tool_call_id=tool_call_id,
        )


class ToolCallDetector:
    def __init__(self, interpreter: ToolCallInterpreter | None = None) -> None:
        self._interpreter = interpreter or ToolCallInterpreter()

    def detect(self, message: Message) -> ToolCallPlan:
        return self._interpreter.interpret(message)
