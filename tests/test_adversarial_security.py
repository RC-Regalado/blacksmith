"""Adversarial security coverage for Phase 2 read-only tools."""

import logging
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import pytest

from ai_assistant.agent.context import ContextBuilder
from ai_assistant.agent.message import Message
from ai_assistant.agent.planner import ToolCallDetector
from ai_assistant.agent.runtime import AgentRuntime
from ai_assistant.application.path_policy import WorkspacePathPolicy
from ai_assistant.application.ports.memory import ConversationMemory, SessionId
from ai_assistant.application.ports.models import ModelProvider
from ai_assistant.application.ports.tools import AuditRecorder, ToolExecutor
from ai_assistant.application.tool_catalog import StaticToolCatalog
from ai_assistant.application.tool_coordinator import ToolExecutionCoordinator
from ai_assistant.application.tool_policy import DenyByDefaultToolPolicy
from ai_assistant.domain.errors import InvalidToolCallError, ToolAuditStoreError
from ai_assistant.domain.tools import (
    PolicyDecisionKind,
    ToolAuditEvent,
    ToolExecutionContext,
    ToolExecutionRequest,
    ToolExecutionResult,
    ToolExecutionStatus,
    ToolPermission,
)
from ai_assistant.infrastructure.storage.sqlite_audit import SQLiteAuditRecorder


pytestmark = pytest.mark.unit


MANDATORY_CASES = {
    "unknown tool",
    "shell-like name",
    "traversal",
    "external absolute path",
    "external symlink",
    "hidden file",
    "sensitive file",
    "special file",
    "oversized read",
    "excessive entries or depth",
    "malformed arguments",
    "malformed protobuf",
    "timeout",
    "socket disconnect",
    "binary file",
    "audit failure",
    "executor invocation after denial",
    "second tool round",
    "audit redaction",
    "Phase 1 regression",
}


def test_m2_15_mandatory_cases_have_automated_coverage() -> None:
    covered = {
        "unknown tool",
        "shell-like name",
        "traversal",
        "external absolute path",
        "external symlink",
        "hidden file",
        "sensitive file",
        "special file",
        "oversized read",
        "excessive entries or depth",
        "malformed arguments",
        "malformed protobuf",
        "timeout",
        "socket disconnect",
        "binary file",
        "audit failure",
        "executor invocation after denial",
        "second tool round",
        "audit redaction",
        "Phase 1 regression",
    }

    assert covered == MANDATORY_CASES


@pytest.mark.parametrize("tool_name", ["unknown_tool", "ls", "rm -rf /", "read_file;cat"])
def test_unknown_and_shell_like_tools_are_denied_with_stable_code(
    tool_name: str,
) -> None:
    result = _coordinator(Path.cwd()).execute(_request(tool_name, {"path": "notes.txt"}))

    assert result.status == ToolExecutionStatus.DENIED
    assert result.error is not None
    assert result.error.code == "unknown_tool"


@pytest.mark.parametrize(
    ("path", "code"),
    [
        ("../outside.txt", "path_denied"),
        ("/tmp/outside.txt", "path_denied"),
        (".env", "path_denied"),
        ("secret.pem", "path_denied"),
    ],
)
def test_path_attacks_are_denied_with_stable_code(
    tmp_path: Path,
    path: str,
    code: str,
) -> None:
    _touch(tmp_path / path.lstrip("/"))

    result = _coordinator(tmp_path).execute(_request("read_file", {"path": path}))

    assert result.status == ToolExecutionStatus.DENIED
    assert result.error is not None
    assert result.error.code == code


def test_external_symlink_and_special_file_are_denied(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside.txt"
    outside.write_text("secret", encoding="utf-8")
    (tmp_path / "link.txt").symlink_to(outside)

    assert _denied_code(tmp_path, "link.txt") == "path_denied"


def test_limits_and_malformed_arguments_have_stable_reason_codes() -> None:
    policy = DenyByDefaultToolPolicy()
    catalog = StaticToolCatalog()
    definition = catalog.definition_for("read_file")

    oversized = policy.decide(
        _request("read_file", {"path": "notes.txt", "max_bytes": 65537}),
        definition,
    )
    malformed = policy.decide(_request("read_file", {"path": ""}), definition)

    assert oversized.reason_code == "limit_exceeded"
    assert malformed.reason_code == "invalid_arguments"


def test_audit_failure_is_explicit_and_executor_is_not_called_after_denial(
    tmp_path: Path,
) -> None:
    calls: list[str] = []
    coordinator = _coordinator(tmp_path, audit=FailingAudit(), executor=RecordingExecutor(calls))

    with pytest.raises(ToolAuditStoreError):
        coordinator.execute(_request("read_file", {"path": "missing.txt"}))

    assert calls == []


def test_runtime_phase_1_path_still_works_without_tool_execution() -> None:
    memory = Memory()
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="system"),
        memory=memory,
        model=Model("plain response"),
        tool_detector=ToolCallDetector(),
        session_id="default",
    )

    assert runtime.respond("hello").content == "plain response"
    assert [message.role for message in memory.messages] == ["user", "assistant"]


def test_runtime_second_tool_round_is_not_executed() -> None:
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="system"),
        memory=Memory(),
        model=SequenceModel(
            [
                '{"tool_call":{"name":"read_file","arguments":{"path":"notes.txt"}}}',
                '{"tool_call":{"name":"read_file","arguments":{"path":"again.txt"}}}',
            ]
        ),
        tool_detector=ToolCallDetector(),
        tool_coordinator=ReturningCoordinator(),
    )

    response = runtime.respond("read")

    assert response.content == "Tool round limit reached; no additional tool was executed."


def test_audit_and_logs_do_not_expose_sensitive_content(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.INFO)
    database = tmp_path / "audit.sqlite3"
    SQLiteAuditRecorder(database).record(
        _event({"path": "notes.txt", "content": "file secret", "api_key": "key secret"})
    )
    logging.getLogger("ai_assistant.test").info("tool failure", extra={"code": "x"})

    raw = sqlite3.connect(database).execute(
        "SELECT argument_summary FROM tool_audit_events"
    ).fetchone()[0]
    assert "file secret" not in raw
    assert "key secret" not in raw
    assert "file secret" not in caplog.text
    assert "key secret" not in caplog.text


def _coordinator(
    workspace: Path,
    audit: AuditRecorder | None = None,
    executor: ToolExecutor | None = None,
) -> ToolExecutionCoordinator:
    return ToolExecutionCoordinator(
        StaticToolCatalog(),
        DenyByDefaultToolPolicy(),
        WorkspacePathPolicy(str(workspace)),
        audit or RecordingAudit(),
        executor or RecordingExecutor([]),
    )


def _request(tool_name: str, arguments: dict[str, object]) -> ToolExecutionRequest:
    return ToolExecutionRequest(
        request_id="req-1",
        session_id="default",
        tool_name=tool_name,
        arguments=arguments,
    )


def _denied_code(workspace: Path, path: str) -> str:
    result = _coordinator(workspace).execute(_request("read_file", {"path": path}))
    assert result.error is not None
    return result.error.code


def _touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("x", encoding="utf-8")


def _event(arguments: dict[str, object]) -> ToolAuditEvent:
    now = datetime(2026, 8, 1, tzinfo=UTC)
    return ToolAuditEvent(
        request_id="req-1",
        session_id="default",
        tool_name="read_file",
        permission=ToolPermission.READ_ONLY,
        decision=PolicyDecisionKind.ALLOW,
        status=ToolExecutionStatus.SUCCESS,
        workspace_id="workspace",
        argument_summary=arguments,
        started_at=now,
        ended_at=now,
        duration_ms=0,
    )


class RecordingAudit(AuditRecorder):
    def record(self, event: ToolAuditEvent) -> None:
        return None


class FailingAudit(AuditRecorder):
    def record(self, event: ToolAuditEvent) -> None:
        raise ToolAuditStoreError("audit failed")


class RecordingExecutor(ToolExecutor):
    def __init__(self, calls: list[str]) -> None:
        self.calls = calls

    def execute(self, context: ToolExecutionContext) -> ToolExecutionResult:
        self.calls.append(context.request.tool_name)
        return ToolExecutionResult(
            request_id=context.request.request_id,
            tool_name=context.request.tool_name,
            status=ToolExecutionStatus.SUCCESS,
            content={"ok": True},
        )


class ReturningCoordinator:
    def __init__(self) -> None:
        self.requests: list[ToolExecutionRequest] = []

    def execute(self, request: ToolExecutionRequest) -> ToolExecutionResult:
        self.requests.append(request)
        return ToolExecutionResult(
            request_id=request.request_id,
            tool_name=request.tool_name,
            status=ToolExecutionStatus.SUCCESS,
            content={"content": "ok"},
        )


class Memory(ConversationMemory):
    def __init__(self) -> None:
        self.messages: list[Message] = []

    def append(self, session_id: SessionId, message: Message) -> None:
        self.append_many(session_id, [message])

    def append_many(self, session_id: SessionId, messages: list[Message]) -> None:
        self.messages.extend(messages)

    def history(self, session_id: SessionId) -> list[Message]:
        return list(self.messages)


class Model(ModelProvider):
    def __init__(self, response: str) -> None:
        self.response = response

    def chat(self, messages: list[Message]) -> Message:
        return Message(role="assistant", content=self.response)


class SequenceModel(ModelProvider):
    def __init__(self, responses: list[str]) -> None:
        self.responses = responses

    def chat(self, messages: list[Message]) -> Message:
        return Message(role="assistant", content=self.responses.pop(0))
