"""Tool-call planning placeholders."""

from dataclasses import dataclass

from ai_assistant.agent.message import Message


@dataclass(frozen=True, slots=True)
class ToolCallPlan:
    has_tool_call: bool
    tool_name: str | None = None


class ToolCallDetector:
    def detect(self, message: Message) -> ToolCallPlan:
        if message.role != "assistant":
            return ToolCallPlan(has_tool_call=False)

        return ToolCallPlan(has_tool_call=False)

