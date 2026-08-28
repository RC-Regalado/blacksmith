"""Coordinator-level tests for automatic case-only path recovery.

Covers the mandatory cases from the "avoid wasting LLM tool rounds on
trivial path resolution errors" fix: exact match (no recovery), case-only
recovery, missing file, ambiguous match, traversal, sensitive path,
external symlink, write exclusion and the recovery budget/metrics, plus an
end-to-end reproduction of the reported "Agents.md" -> "AGENTS.md" prompt
at the AgentRuntime level.
"""

from pathlib import Path

import pytest

from ai_assistant.agent.context import ContextBuilder
from ai_assistant.agent.message import FinishReason, Message, ModelResponse
from ai_assistant.agent.planner import ToolCallDetector
from ai_assistant.agent.runtime import AgentRuntime
from ai_assistant.application.confirmation import ConfirmationService
from ai_assistant.application.path_policy import WorkspacePathPolicy
from ai_assistant.application.path_recovery import PathRecoveryPolicy
from ai_assistant.application.ports.memory import ConversationMemory
from ai_assistant.application.ports.models import ModelProvider
from ai_assistant.application.ports.tools import (
    AuditRecorder,
    ConfirmationPrompter,
    ToolDiagnosticLogger,
)
from ai_assistant.application.tool_catalog import StaticToolCatalog
from ai_assistant.application.tool_coordinator import ToolExecutionCoordinator
from ai_assistant.application.tool_policy import DenyByDefaultToolPolicy
from ai_assistant.domain.tools import (
    ToolAuditEvent,
    ToolCallLogEvent,
    ToolExecutionRequest,
    ToolExecutionStatus,
    ToolPermission,
)
from ai_assistant.infrastructure.tools.local_read_only import LocalReadOnlyToolExecutor


pytestmark = pytest.mark.unit


# --- Caso 1: case-only difference is recovered -----------------------------


def test_case_only_mismatch_is_recovered(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("Follow the house style.", encoding="utf-8")
    coordinator, diagnostics = _coordinator(tmp_path)

    result = coordinator.execute(_request("read_file", "Agents.md"))

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.content is not None
    assert result.content["content"] == "Follow the house style."
    assert result.content["path"] == "AGENTS.md"
    stages = _recovery_stages(diagnostics)
    assert stages == [
        "recovery_started",
        "recovery_candidate",
        "recovery_retry",
        "recovery_success",
    ]


# --- Caso 2: exact match never triggers recovery ----------------------------


def test_exact_match_does_not_trigger_recovery(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("hello", encoding="utf-8")
    coordinator, diagnostics = _coordinator(tmp_path)

    result = coordinator.execute(_request("read_file", "README.md"))

    assert result.status == ToolExecutionStatus.SUCCESS
    assert _recovery_stages(diagnostics) == []


# --- Caso 3: genuinely missing path stays PATH_NOT_FOUND --------------------


def test_missing_file_falls_back_to_path_denied(tmp_path: Path) -> None:
    coordinator, diagnostics = _coordinator(tmp_path)

    result = coordinator.execute(_request("read_file", "missing.md"))

    assert result.status == ToolExecutionStatus.DENIED
    assert result.error is not None
    assert result.error.code == "path_denied"
    stages = _recovery_stages(diagnostics)
    assert stages == ["recovery_started", "recovery_failed"]
    assert _last_recovery_error_code(diagnostics) == "path_not_found"


# --- Caso 4: ambiguous case-insensitive matches are denied, not guessed ----


def test_ambiguous_case_variants_are_denied_without_guessing(tmp_path: Path) -> None:
    (tmp_path / "Agents.md").write_text("a", encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text("b", encoding="utf-8")
    coordinator, diagnostics = _coordinator(tmp_path)

    result = coordinator.execute(_request("read_file", "agents.md"))

    assert result.status == ToolExecutionStatus.DENIED
    assert result.error is not None
    assert result.error.code == "path_denied"
    assert _last_recovery_error_code(diagnostics) == "ambiguous_path"


# --- Caso 5: traversal is denied before recovery can run -------------------


def test_traversal_is_denied_before_recovery(tmp_path: Path) -> None:
    coordinator, diagnostics = _coordinator(tmp_path)

    result = coordinator.execute(_request("read_file", "../../etc/passwd"))

    assert result.status == ToolExecutionStatus.DENIED
    assert result.error is not None
    assert result.error.code == "path_denied"
    assert _recovery_stages(diagnostics) == []


# --- Caso 6: sensitive paths are denied, never offered as a candidate ------


def test_sensitive_path_is_denied_without_recovery(tmp_path: Path) -> None:
    (tmp_path / "secret.pem").write_text("key", encoding="utf-8")
    coordinator, diagnostics = _coordinator(tmp_path)

    result = coordinator.execute(_request("read_file", "secret.pem"))

    assert result.status == ToolExecutionStatus.DENIED
    assert result.error is not None
    assert result.error.code == "path_denied"
    assert _recovery_stages(diagnostics) == []


def test_case_variant_of_sensitive_path_is_still_denied(tmp_path: Path) -> None:
    (tmp_path / "secret.pem").write_text("key", encoding="utf-8")
    coordinator, diagnostics = _coordinator(tmp_path)

    result = coordinator.execute(_request("read_file", "Secret.PEM"))

    assert result.status == ToolExecutionStatus.DENIED
    assert result.error is not None
    assert result.error.code == "path_denied"
    # Recovery is attempted (the raw lookup looks like a plain miss) but the
    # sensitive candidate must never be offered, so it still falls back.
    assert _recovery_stages(diagnostics) == ["recovery_started", "recovery_failed"]
    assert _last_recovery_error_code(diagnostics) == "path_not_found"


# --- Caso 7: external symlink is denied, even after a corrected retry -----


def test_external_symlink_is_denied(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside-secret.txt"
    outside.write_text("secret", encoding="utf-8")
    (tmp_path / "link.txt").symlink_to(outside)
    coordinator, diagnostics = _coordinator(tmp_path)

    result = coordinator.execute(_request("read_file", "link.txt"))

    assert result.status == ToolExecutionStatus.DENIED
    assert result.error is not None
    assert result.error.code == "path_denied"
    assert _recovery_stages(diagnostics) == []
    outside.unlink()


def test_case_variant_of_external_symlink_is_denied_after_retry(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside-secret-2.txt"
    outside.write_text("secret", encoding="utf-8")
    (tmp_path / "link.txt").symlink_to(outside)
    coordinator, diagnostics = _coordinator(tmp_path)

    result = coordinator.execute(_request("read_file", "Link.txt"))

    assert result.status == ToolExecutionStatus.DENIED
    assert result.error is not None
    assert result.error.code == "path_denied"
    # The corrected candidate is found, but the full re-validation pipeline
    # still catches the workspace escape on retry.
    assert _recovery_stages(diagnostics) == [
        "recovery_started",
        "recovery_candidate",
        "recovery_retry",
        "recovery_failed",
    ]
    assert _last_recovery_error_code(diagnostics) == "path_outside_workspace"
    outside.unlink()


# --- Caso 8: write never enters the recovery mechanism ---------------------


def test_write_wrong_case_is_denied_without_recovery(tmp_path: Path) -> None:
    (tmp_path / "notes.txt").write_text("old", encoding="utf-8")
    coordinator, diagnostics = _coordinator(tmp_path)

    result = coordinator.execute(
        ToolExecutionRequest(
            request_id="req-write",
            session_id="default",
            tool_name="write",
            arguments={"path": "Notes.txt", "content": "new", "mode": "replace"},
            permission=ToolPermission.WRITE_WORKSPACE,
        )
    )

    assert result.status == ToolExecutionStatus.DENIED
    assert _recovery_stages(diagnostics) == []


# --- Caso 9: budget/metrics for a successful recovery -----------------------


def test_successful_recovery_reports_metrics_without_extra_round(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("guidelines", encoding="utf-8")
    coordinator, diagnostics = _coordinator(tmp_path)

    result = coordinator.execute(_request("read_file", "Agents.md"))

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.executor_operations == 3
    success = _events_by_stage(diagnostics)["recovery_success"]
    assert len(success) == 1
    payload = success[0].result
    assert payload is not None
    assert payload["model_tool_requests"] == 1
    assert payload["executor_operations"] > 1
    assert payload["recovery_operations"] == 1
    assert payload["requested_path"] == "Agents.md"
    assert payload["resolved_path"] == "AGENTS.md"


def test_executor_operations_is_one_for_a_direct_success(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("guidelines", encoding="utf-8")
    coordinator, _ = _coordinator(tmp_path)

    result = coordinator.execute(_request("read_file", "AGENTS.md"))

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.executor_operations == 1


def test_executor_operations_is_zero_for_an_unknown_tool(tmp_path: Path) -> None:
    coordinator, _ = _coordinator(tmp_path)

    result = coordinator.execute(_request("not_a_real_tool", "AGENTS.md"))

    assert result.status == ToolExecutionStatus.DENIED
    assert result.executor_operations == 0


def test_recovery_attempt_is_capped_at_one(tmp_path: Path) -> None:
    coordinator, diagnostics = _coordinator(tmp_path)

    result = coordinator.execute(_request("read_file", "missing.md"))

    assert result.status == ToolExecutionStatus.DENIED
    failed = _events_by_stage(diagnostics)["recovery_failed"]
    assert len(failed) == 1
    assert failed[0].result is not None
    assert failed[0].result["recovery_operations"] == 1


# --- Caso "Validación funcional": end-to-end runtime reproduction ----------


def test_runtime_recovers_agents_md_without_hitting_round_limit(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text(
        "This project follows hexagonal architecture.", encoding="utf-8"
    )
    coordinator, _ = _coordinator(tmp_path)
    model = SequenceModel(
        [
            '{"tool_call":{"id":"call-1","name":"read_file","arguments":{"path":"Agents.md"}}}',
            "The AGENTS.md file describes the hexagonal architecture rules.",
        ]
    )
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="system"),
        memory=Memory(),
        model=model,
        tool_detector=ToolCallDetector(),
        tool_coordinator=coordinator,
        session_id="alpha",
    )

    response = runtime.respond("Explícame el archivo Agents.md")

    assert model.responses == []  # both scripted turns were consumed, no third round
    assert "Tool round limit reached" not in response.content
    assert "hexagonal architecture" in response.content


# --- fixtures / fakes -------------------------------------------------------


def _coordinator(
    workspace: Path,
) -> tuple[ToolExecutionCoordinator, "RecordingDiagnostics"]:
    diagnostics = RecordingDiagnostics()
    audit = RecordingAudit()
    coordinator = ToolExecutionCoordinator(
        StaticToolCatalog(),
        DenyByDefaultToolPolicy(),
        WorkspacePathPolicy(str(workspace)),
        audit,
        LocalReadOnlyToolExecutor(),
        confirmation=ConfirmationService(AlwaysApprove(), audit),
        path_recovery=PathRecoveryPolicy(str(workspace)),
        diagnostics=diagnostics,
        model_provider_name="ollama",
        model_name="qwen3.5:4b",
    )
    return coordinator, diagnostics


def _request(tool_name: str, path: str) -> ToolExecutionRequest:
    return ToolExecutionRequest(
        request_id="req-1",
        session_id="default",
        tool_name=tool_name,
        arguments={"path": path},
    )


def _recovery_stages(diagnostics: "RecordingDiagnostics") -> list[str]:
    return [
        event.status.value
        for event in diagnostics.events
        if event.status.value.startswith("recovery_")
    ]


def _events_by_stage(
    diagnostics: "RecordingDiagnostics",
) -> dict[str, list[ToolCallLogEvent]]:
    grouped: dict[str, list[ToolCallLogEvent]] = {}
    for event in diagnostics.events:
        grouped.setdefault(event.status.value, []).append(event)
    return grouped


def _last_recovery_error_code(diagnostics: "RecordingDiagnostics") -> str | None:
    for event in reversed(diagnostics.events):
        if event.status.value == "recovery_failed":
            assert event.error is not None
            return str(event.error["code"])
    return None


class RecordingDiagnostics(ToolDiagnosticLogger):
    def __init__(self) -> None:
        self.events: list[ToolCallLogEvent] = []

    def record(self, event: ToolCallLogEvent) -> None:
        self.events.append(event)


class RecordingAudit(AuditRecorder):
    def __init__(self) -> None:
        self.events: list[ToolAuditEvent] = []

    def record(self, event: ToolAuditEvent) -> None:
        self.events.append(event)


class AlwaysApprove(ConfirmationPrompter):
    def confirm(self, session_id: str, workspace_id: str, permission: str) -> bool:
        return True


class Memory(ConversationMemory):
    def __init__(self) -> None:
        self.messages: list[Message] = []

    def append(self, session_id: str, message: Message) -> None:
        self.append_many(session_id, [message])

    def append_many(self, session_id: str, messages: list[Message]) -> None:
        self.messages.extend(messages)

    def history(self, session_id: str) -> list[Message]:
        return list(self.messages)


class SequenceModel(ModelProvider):
    def __init__(self, responses: list[str]) -> None:
        self.responses = responses

    def chat(self, messages: list[Message]) -> ModelResponse:
        return ModelResponse(
            message=Message(role="assistant", content=self.responses.pop(0)),
            finish_reason=FinishReason.STOP,
        )
