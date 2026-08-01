"""Declarative tool-call interpretation without execution."""

import json
from typing import Any

from ai_assistant.domain.errors import InvalidToolCallError
from ai_assistant.domain.message import Message
from ai_assistant.domain.tools import ToolCall, ToolCallPlan


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
        source, fenced = _strip_json_fence(content)
        try:
            data = json.loads(source)
        except json.JSONDecodeError:
            if not fenced:
                return None
            candidate = _first_json_object(source)
            if candidate is None:
                return None
            data = json.loads(candidate)
        return data if isinstance(data, dict) else None

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
        return ToolCall(name=name, arguments=arguments, tool_call_id=tool_call_id)


class ToolCallDetector:
    def __init__(self, interpreter: ToolCallInterpreter | None = None) -> None:
        self._interpreter = interpreter or ToolCallInterpreter()

    def detect(self, message: Message) -> ToolCallPlan:
        return self._interpreter.interpret(message)


def _strip_json_fence(content: str) -> tuple[str, bool]:
    stripped = content.strip()
    if not stripped.startswith("```") or not stripped.endswith("```"):
        return content, False
    first_line, _, rest = stripped.partition("\n")
    if first_line not in {"```", "```json"}:
        return content, False
    return rest.removesuffix("```").strip(), True


def _first_json_object(content: str) -> str | None:
    depth = 0
    start = None
    in_string = False
    escaped = False
    for index, char in enumerate(content):
        if in_string:
            escaped = char == "\\" and not escaped
            if char == '"' and not escaped:
                in_string = False
            elif char != "\\":
                escaped = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            start = index if start is None else start
            depth += 1
        elif char == "}" and depth:
            depth -= 1
            if depth == 0 and start is not None:
                return content[start : index + 1]
    return None
