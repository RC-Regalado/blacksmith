"""Tests for structured tool-loop diagnostic logging."""

from datetime import UTC, datetime
import json

import pytest

from ai_assistant.agent.context import ContextBuilder
from ai_assistant.agent.message import Message
from ai_assistant.agent.planner import ToolCallDetector
from ai_assistant.agent.runtime import AgentRuntime
from ai_assistant.application.ports.memory import ConversationMemory
from ai_assistant.application.ports.models import ModelProvider
from ai_assistant.domain.tools import (
    SanitizedToolError,
    ToolCallLogEvent,
    ToolDiagnosticStatus,
    ToolExecutionRequest,
    ToolExecutionResult,
    ToolExecutionStatus,
)
from ai_assistant.infrastructure.tool_diagnostics import JsonlToolDiagnosticLogger


pytestmark = pytest.mark.unit


def test_jsonl_logger_creates_sanitized_filename_and_payload(tmp_path) -> None:
    logger = JsonlToolDiagnosticLogger(tmp_path)

    logger.record(
        ToolCallLogEvent(
            timestamp=datetime(2026, 8, 20, tzinfo=UTC),
            session_id="../default/session",
            provider="ollama",
            model="qwen3.5:4b",
            tool_name="read_file",
            capability_name="ReadFile",
            tool_call_id="call-1",
            round_index=1,
            tool_call_count=1,
            status=ToolDiagnosticStatus.EXECUTED,
            arguments={"path": ".env", "api_key": "secret", "query": "token=abc"},
            result={"status": "success", "content": {"content": "secret file"}},
            duration_ms=1.25,
        )
    )

    files = list(tmp_path.iterdir())
    assert [item.name for item in files] == ["log-qwen3.5-4b-default-session-2026-08-20.log"]
    row = json.loads(files[0].read_text(encoding="utf-8"))
    assert row["timestamp"] == "2026-08-20T00:00:00+00:00"
    assert row["session_id"] == "../default/session"
    assert row["capability_name"] == "ReadFile"
    assert row["arguments"] == {
        "path": "[redacted]",
        "api_key": "[redacted]",
        "query": "token=[REDACTED]",
    }
    assert row["result"]["content"] == "[redacted]"


def test_runtime_logs_successful_tool_round(tmp_path) -> None:
    runtime = _runtime(
        tmp_path,
        SequenceModel(
            [
                '{"tool_call":{"id":"call-1","name":"read_file","arguments":{"path":"README.md"}}}',
                "done",
            ]
        ),
        _coordinator(
            ToolExecutionResult(
                "call-1",
                "read_file",
                ToolExecutionStatus.SUCCESS,
                {"bytes_read": 1},
            )
        ),
    )

    runtime.respond("read")

    rows = _rows(tmp_path)
    assert [row["status"] for row in rows] == ["requested", "executed"]
    assert rows[0]["tool_call_count"] == 1
    assert rows[1]["round_index"] == 1
    assert rows[1]["result"]["status"] == "success"


def test_runtime_logs_denied_error_timeout_and_round_limit(tmp_path) -> None:
    for status, expected in (
        (ToolExecutionStatus.DENIED, "rejected"),
        (ToolExecutionStatus.ERROR, "failed"),
        (ToolExecutionStatus.TIMEOUT, "timeout"),
    ):
        runtime = _runtime(
            tmp_path / expected,
            SequenceModel(
                [
                    '{"tool_call":{"name":"read_file","arguments":{"path":"secret.pem"}}}',
                    "done",
                ]
            ),
            _coordinator(
                ToolExecutionResult(
                    "alpha:read_file",
                    "read_file",
                    status,
                    error=SanitizedToolError("x", "sanitized"),
                )
            ),
        )

        runtime.respond("read")

        rows = _rows(tmp_path / expected)
        assert rows[-1]["status"] == expected
        assert rows[-1]["error"] == {"code": "x", "message": "sanitized"}
        assert rows[-1]["arguments"]["path"] == "[redacted]"

    runtime = _runtime(
        tmp_path / "limit",
        SequenceModel(
            [
                '{"tool_call":{"name":"read_file","arguments":{"path":"README.md"}}}',
                '{"tool_call":{"name":"list_directory","arguments":{"path":"."}}}',
            ]
        ),
        _coordinator(ToolExecutionResult("alpha:read_file", "read_file", ToolExecutionStatus.SUCCESS)),
    )

    runtime.respond("read")

    rows = _rows(tmp_path / "limit")
    assert [row["status"] for row in rows] == ["requested", "executed", "requested", "rejected"]
    assert rows[-1]["round_index"] == 2
    assert rows[-1]["tool_call_count"] == 2
    assert rows[-1]["error"]["code"] == "tool_round_limit_reached"


def test_runtime_continues_when_diagnostic_logger_fails() -> None:
    runtime = AgentRuntime(
        context_builder=ContextBuilder("system"),
        memory=Memory(),
        model=SequenceModel(
            [
                '{"tool_call":{"name":"read_file","arguments":{"path":"README.md"}}}',
                "done",
            ]
        ),
        tool_detector=ToolCallDetector(),
        tool_coordinator=_coordinator(
            ToolExecutionResult("alpha:read_file", "read_file", ToolExecutionStatus.SUCCESS)
        ),
        tool_diagnostics=FailingLogger(),
        session_id="alpha",
    )

    assert runtime.respond("read").content == "done"


def _runtime(tmp_path, model, coordinator) -> AgentRuntime:
    return AgentRuntime(
        context_builder=ContextBuilder("system"),
        memory=Memory(),
        model=model,
        tool_detector=ToolCallDetector(),
        tool_coordinator=coordinator,
        tool_diagnostics=JsonlToolDiagnosticLogger(tmp_path),
        model_provider_name="ollama",
        model_name="qwen3.5:4b",
        session_id="alpha",
    )


def _coordinator(result: ToolExecutionResult):
    class Coordinator:
        def execute(self, request: ToolExecutionRequest) -> ToolExecutionResult:
            return result

    return Coordinator()


def _rows(tmp_path) -> list[dict[str, object]]:
    files = list(tmp_path.iterdir())
    assert len(files) == 1
    return [json.loads(line) for line in files[0].read_text(encoding="utf-8").splitlines()]


class Memory(ConversationMemory):
    def __init__(self) -> None:
        self.messages: list[Message] = []

    def append(self, session_id: str, message: Message) -> None:
        self.append_many(session_id, [message])

    def append_many(self, session_id: str, messages: list[Message]) -> None:
        self.messages.extend(messages)

    def history(self, session_id: str) -> list[Message]:
        return self.messages


class SequenceModel(ModelProvider):
    def __init__(self, responses: list[str]) -> None:
        self._responses = responses

    def chat(self, messages: list[Message]) -> Message:
        return Message(role="assistant", content=self._responses.pop(0))


class FailingLogger:
    def record(self, event: ToolCallLogEvent) -> None:
        raise OSError("disk full")
