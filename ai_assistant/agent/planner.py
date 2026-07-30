"""Compatibility exports for declarative tool-call planning."""

from ai_assistant.application.tool_calls import ToolCallDetector, ToolCallInterpreter
from ai_assistant.domain.tools import ToolCall, ToolCallPlan, ToolDefinition

__all__ = [
    "ToolCall",
    "ToolCallDetector",
    "ToolCallInterpreter",
    "ToolCallPlan",
    "ToolDefinition",
]
