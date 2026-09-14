"""Tests for interaction-level diagnostics (ADR-070 end-to-end correlation)."""

from datetime import UTC, datetime
import json

import pytest

from ai_assistant.application.tool_diagnostics import (
    InteractionDiagnostics,
    NullInteractionDiagnosticLogger,
)
from ai_assistant.domain.errors import InvalidToolCallError
from ai_assistant.domain.tools import (
    InteractionLogEvent,
    InteractionStage,
    ToolCallLogEvent,
    ToolDiagnosticStatus,
)
from ai_assistant.infrastructure.tool_diagnostics import (
    JsonlInteractionDiagnosticLogger,
    JsonlToolDiagnosticLogger,
)


pytestmark = pytest.mark.unit


def test_interaction_log_event_requires_non_blank_interaction_id() -> None:
    with pytest.raises(InvalidToolCallError):
        InteractionLogEvent(
            timestamp=datetime(2026, 8, 28, tzinfo=UTC),
            interaction_id="",
            session_id="alpha",
            provider="ollama",
            model="qwen3.5:4b",
            stage=InteractionStage.MODEL_REQUEST,
            payload={},
        )


def test_null_interaction_diagnostic_logger_is_a_no_op() -> None:
    NullInteractionDiagnosticLogger().record(
        InteractionLogEvent(
            timestamp=datetime(2026, 8, 28, tzinfo=UTC),
            interaction_id="abc",
            session_id="alpha",
            provider="ollama",
            model="qwen3.5:4b",
            stage=InteractionStage.MODEL_REQUEST,
            payload={},
        )
    )


def test_interaction_diagnostics_helper_is_noop_without_interaction_id() -> None:
    sink = RecordingSink()
    diagnostics = InteractionDiagnostics(sink, "ollama", "qwen3.5:4b")

    diagnostics.record(
        InteractionStage.MODEL_REQUEST,
        session_id="alpha",
        interaction_id=None,
        payload={"round_index": 1},
    )

    assert sink.events == []


def test_interaction_diagnostics_helper_swallows_sink_errors() -> None:
    diagnostics = InteractionDiagnostics(FailingSink(), "ollama", "qwen3.5:4b")

    diagnostics.record(
        InteractionStage.MODEL_REQUEST,
        session_id="alpha",
        interaction_id="abc-123",
        payload={"round_index": 1},
    )


def test_jsonl_interaction_logger_shares_the_tool_logger_file_and_sanitizes_payload(
    tmp_path,
) -> None:
    tool_logger = JsonlToolDiagnosticLogger(tmp_path)
    interaction_logger = JsonlInteractionDiagnosticLogger(tmp_path)
    timestamp = datetime(2026, 8, 28, tzinfo=UTC)

    tool_logger.record(
        ToolCallLogEvent(
            timestamp=timestamp,
            session_id="alpha",
            provider="ollama",
            model="qwen3.5:4b",
            tool_name="read_file",
            tool_call_id="call-1",
            round_index=1,
            tool_call_count=1,
            status=ToolDiagnosticStatus.EXECUTED,
            arguments={"path": "README.md"},
            interaction_id="interaction-1",
        )
    )
    interaction_logger.record(
        InteractionLogEvent(
            timestamp=timestamp,
            interaction_id="interaction-1",
            session_id="alpha",
            provider="ollama",
            model="qwen3.5:4b",
            stage=InteractionStage.MODEL_RESPONSE,
            payload={"finish_reason": "stop", "api_key": "should be redacted"},
        )
    )

    files = list(tmp_path.iterdir())
    assert len(files) == 1
    rows = [json.loads(line) for line in files[0].read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 2
    assert rows[0]["tool_name"] == "read_file"
    assert rows[0]["interaction_id"] == "interaction-1"
    assert rows[1]["stage"] == "model_response"
    assert rows[1]["kind"] == "interaction"
    assert rows[1]["interaction_id"] == "interaction-1"
    assert rows[1]["payload"]["api_key"] == "[redacted]"
    assert rows[1]["payload"]["finish_reason"] == "stop"


class RecordingSink:
    def __init__(self) -> None:
        self.events: list[InteractionLogEvent] = []

    def record(self, event: InteractionLogEvent) -> None:
        self.events.append(event)


class FailingSink:
    def record(self, event: InteractionLogEvent) -> None:
        raise OSError("disk full")
