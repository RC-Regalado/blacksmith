"""Tests for declarative tool-call planning."""

import pytest

from ai_assistant.agent.message import Message
from ai_assistant.agent.planner import (
    ToolCall,
    ToolCallDetector,
    ToolCallInterpreter,
    ToolDefinition,
)
from ai_assistant.application.errors import InvalidToolCallError


pytestmark = pytest.mark.unit


def test_tool_definition_is_declarative() -> None:
    definition = ToolDefinition(
        name="search",
        description="Search documents",
        input_schema={"type": "object"},
    )

    assert definition.input_schema == {"type": "object"}


def test_interpreter_detects_explicit_tool_call() -> None:
    message = Message(
        role="assistant",
        content='{"tool_call":{"id":"call-1","name":"search","arguments":{"q":"x"}}}',
    )

    plan = ToolCallInterpreter().interpret(message)

    assert plan.has_tool_call is True
    assert plan.tool_call == ToolCall(
        name="search",
        arguments={"q": "x"},
        tool_call_id="call-1",
    )
    assert plan.tool_name == "search"


def test_interpreter_ignores_plain_assistant_text() -> None:
    message = Message(role="assistant", content="no tools")

    plan = ToolCallInterpreter().interpret(message)

    assert plan.has_tool_call is False
    assert plan.tool_call is None


def test_interpreter_ignores_non_assistant_messages() -> None:
    message = Message(role="user", content='{"tool_call":{"name":"search"}}')

    assert ToolCallInterpreter().interpret(message).has_tool_call is False


def test_interpreter_rejects_invalid_explicit_tool_call() -> None:
    message = Message(role="assistant", content='{"tool_call":{"arguments":[]}}')

    with pytest.raises(InvalidToolCallError, match="name"):
        ToolCallInterpreter().interpret(message)


def test_detector_returns_typed_plan_without_execution() -> None:
    detector = ToolCallDetector()

    plan = detector.detect(
        Message(role="assistant", content='{"tool_call":{"name":"search"}}')
    )

    assert plan.has_tool_call is True
    assert plan.tool_call == ToolCall(name="search", arguments={})
