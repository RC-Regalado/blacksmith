"""Tests for declarative tool-call planning."""

from datetime import UTC, datetime

import pytest

from ai_assistant.agent.message import Message
from ai_assistant.agent.planner import (
    PolicyDecisionKind,
    SanitizedToolError,
    ToolCall,
    ToolAuditEvent,
    ToolCallDetector,
    ToolCallInterpreter,
    ToolDefinition,
    ToolExecutionContext,
    ToolExecutionRequest,
    ToolExecutionResult,
    ToolExecutionStatus,
    ToolPermission,
    ToolPolicyDecision,
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


def test_interpreter_detects_json_markdown_fenced_tool_call() -> None:
    message = Message(
        role="assistant",
        content='```json\n{"tool_call":{"name":"list_directory","arguments":{"path":"."}}}\n```',
    )

    plan = ToolCallInterpreter().interpret(message)

    assert plan.has_tool_call is True
    assert plan.tool_call == ToolCall(
        name="list_directory",
        arguments={"path": "."},
    )


def test_interpreter_detects_fenced_tool_call_with_trailing_garbage() -> None:
    message = Message(
        role="assistant",
        content='```json\n{"tool_call":{"name":"list_directory","arguments":{"path":"."}}}\n}\n```',
    )

    plan = ToolCallInterpreter().interpret(message)

    assert plan.has_tool_call is True
    assert plan.tool_call == ToolCall(
        name="list_directory",
        arguments={"path": "."},
    )


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


def test_tool_execution_request_requires_explicit_ids() -> None:
    with pytest.raises(InvalidToolCallError, match="request_id"):
        ToolExecutionRequest(
            request_id="",
            session_id="default",
            tool_name="read_file",
            arguments={"path": "README.md"},
        )


def test_tool_execution_request_is_provider_neutral() -> None:
    request = ToolExecutionRequest(
        request_id="req-1",
        session_id="default",
        tool_name="read_file",
        arguments={"path": "README.md", "max_bytes": 1024},
    )

    assert request.permission == ToolPermission.READ_ONLY
    assert request.timeout_seconds == 5.0
    assert request.dry_run is False


def test_policy_denial_requires_reason_code() -> None:
    with pytest.raises(InvalidToolCallError, match="reason_code"):
        ToolPolicyDecision(kind=PolicyDecisionKind.DENY)


def test_execution_result_requires_error_for_failures() -> None:
    with pytest.raises(InvalidToolCallError, match="error"):
        ToolExecutionResult(
            request_id="req-1",
            tool_name="read_file",
            status=ToolExecutionStatus.ERROR,
        )


def test_execution_result_includes_truncation_metadata() -> None:
    result = ToolExecutionResult(
        request_id="req-1",
        tool_name="read_file",
        status=ToolExecutionStatus.SUCCESS,
        content={"bytes_read": 1024},
        truncated=True,
    )

    assert result.truncated is True
    assert result.content == {"bytes_read": 1024}


def test_audit_event_uses_sanitized_metadata() -> None:
    started = datetime(2026, 7, 30, tzinfo=UTC)
    ended = datetime(2026, 7, 30, 0, 0, 1, tzinfo=UTC)

    event = ToolAuditEvent(
        request_id="req-1",
        session_id="default",
        tool_name="read_file",
        permission=ToolPermission.READ_ONLY,
        decision=PolicyDecisionKind.ALLOW,
        status=ToolExecutionStatus.SUCCESS,
        workspace_id="workspace",
        argument_summary={"path": "README.md"},
        started_at=started,
        ended_at=ended,
        duration_ms=1000.0,
    )

    assert event.argument_summary == {"path": "README.md"}
    assert event.artifact_ids == ()


def test_audit_event_rejects_invalid_time_order() -> None:
    started = datetime(2026, 7, 30, 0, 0, 1, tzinfo=UTC)
    ended = datetime(2026, 7, 30, tzinfo=UTC)

    with pytest.raises(InvalidToolCallError, match="ended_at"):
        ToolAuditEvent(
            request_id="req-1",
            session_id="default",
            tool_name="read_file",
            permission=ToolPermission.READ_ONLY,
            decision=PolicyDecisionKind.ALLOW,
            status=ToolExecutionStatus.SUCCESS,
            workspace_id="workspace",
            argument_summary={},
            started_at=started,
            ended_at=ended,
            duration_ms=1.0,
        )


def test_execution_context_requires_workspace_id() -> None:
    request = ToolExecutionRequest(
        request_id="req-1",
        session_id="default",
        tool_name="list_directory",
        arguments={"path": "."},
    )

    with pytest.raises(InvalidToolCallError, match="workspace_id"):
        ToolExecutionContext(request=request, workspace_id="")


def test_execution_context_accepts_resolved_path_metadata() -> None:
    request = ToolExecutionRequest(
        request_id="req-1",
        session_id="default",
        tool_name="read_file",
        arguments={"path": "README.md"},
    )

    context = ToolExecutionContext(
        request=request,
        workspace_id="workspace",
        resolved_path="/workspace/README.md",
        relative_path="README.md",
    )

    assert context.resolved_path == "/workspace/README.md"
    assert context.relative_path == "README.md"


def test_sanitized_tool_error_requires_code_and_message() -> None:
    error = SanitizedToolError(code="path_denied", message="Path denied.")

    assert error.code == "path_denied"
    assert error.message == "Path denied."
