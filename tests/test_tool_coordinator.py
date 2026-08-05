"""Unit tests for tool execution coordinator."""

import pytest

from ai_assistant.application.ports.tools import (
    AuditRecorder,
    PathPolicy,
    ToolCatalog,
    ToolExecutor,
    ToolPolicy,
)
from ai_assistant.application.tool_coordinator import ToolExecutionCoordinator
from ai_assistant.domain.errors import InvalidToolCallError
from ai_assistant.domain.tools import (
    PolicyDecisionKind,
    ToolAuditEvent,
    ToolDefinition,
    ToolExecutionContext,
    ToolExecutionRequest,
    ToolExecutionResult,
    ToolExecutionStatus,
    ToolPolicyDecision,
    ToolPermission,
)


pytestmark = pytest.mark.unit


def test_coordinator_execution_order_is_deterministic() -> None:
    calls: list[str] = []
    audit = RecordingAudit(calls)
    coordinator = ToolExecutionCoordinator(
        Catalog(calls),
        Policy(calls),
        Path(calls),
        audit,
        Executor(calls),
    )

    result = coordinator.execute(_request())

    assert result.status == ToolExecutionStatus.SUCCESS
    assert calls == ["catalog", "policy", "path", "audit", "executor", "audit"]
    assert [event.status for event in audit.events] == [
        ToolExecutionStatus.ALLOWED,
        ToolExecutionStatus.SUCCESS,
    ]


def test_denied_request_is_audited_and_does_not_reach_executor() -> None:
    calls: list[str] = []
    audit = RecordingAudit(calls)
    coordinator = ToolExecutionCoordinator(
        Catalog(calls),
        Policy(calls, ToolPolicyDecision(PolicyDecisionKind.DENY, "blocked")),
        Path(calls),
        audit,
        Executor(calls),
    )

    result = coordinator.execute(_request())

    assert result.status == ToolExecutionStatus.DENIED
    assert result.error is not None
    assert result.error.code == "blocked"
    assert calls == ["catalog", "policy", "audit"]
    assert audit.events[0].denial_reason == "blocked"


def test_unknown_tool_is_audited_and_denied() -> None:
    calls: list[str] = []
    audit = RecordingAudit(calls)
    coordinator = ToolExecutionCoordinator(
        MissingCatalog(calls),
        Policy(calls),
        Path(calls),
        audit,
        Executor(calls),
    )

    result = coordinator.execute(_request(tool_name="unknown"))

    assert result.status == ToolExecutionStatus.DENIED
    assert result.error is not None
    assert result.error.code == "unknown_tool"
    assert calls == ["catalog", "audit"]


def test_path_denial_is_audited_and_does_not_reach_executor() -> None:
    calls: list[str] = []
    coordinator = ToolExecutionCoordinator(
        Catalog(calls),
        Policy(calls),
        DenyingPath(calls),
        RecordingAudit(calls),
        Executor(calls),
    )

    result = coordinator.execute(_request())

    assert result.status == ToolExecutionStatus.DENIED
    assert result.error is not None
    assert result.error.code == "path_denied"
    assert calls == ["catalog", "policy", "path", "audit"]


def test_executor_exception_becomes_normalized_error_result() -> None:
    calls: list[str] = []
    audit = RecordingAudit(calls)
    coordinator = ToolExecutionCoordinator(
        Catalog(calls),
        Policy(calls),
        Path(calls),
        audit,
        RaisingExecutor(calls),
    )

    result = coordinator.execute(_request())

    assert result.status == ToolExecutionStatus.ERROR
    assert result.error is not None
    assert result.error.code == "executor_error"
    assert [event.status for event in audit.events] == [
        ToolExecutionStatus.ALLOWED,
        ToolExecutionStatus.ERROR,
    ]


def test_execute_project_requires_confirmation_service() -> None:
    calls: list[str] = []
    coordinator = ToolExecutionCoordinator(
        Catalog(calls),
        Policy(calls),
        Path(calls),
        RecordingAudit(calls),
        Executor(calls),
    )

    result = coordinator.execute(_request(permission=ToolPermission.EXECUTE_PROJECT))

    assert result.status == ToolExecutionStatus.DENIED
    assert result.error is not None
    assert result.error.code == "confirmation_required"
    assert calls == ["catalog", "policy", "path", "audit"]


def test_write_workspace_requires_confirmation_service() -> None:
    calls: list[str] = []
    coordinator = ToolExecutionCoordinator(
        Catalog(calls),
        Policy(calls),
        Path(calls),
        RecordingAudit(calls),
        Executor(calls),
    )

    result = coordinator.execute(_request(permission=ToolPermission.WRITE_WORKSPACE))

    assert result.status == ToolExecutionStatus.DENIED
    assert result.error is not None
    assert result.error.code == "confirmation_required"
    assert calls == ["catalog", "policy", "path", "audit"]


def test_execute_project_confirmation_allows_execution() -> None:
    calls: list[str] = []
    confirmation = Confirmation(calls, approved=True)
    coordinator = ToolExecutionCoordinator(
        Catalog(calls),
        Policy(calls),
        Path(calls),
        RecordingAudit(calls),
        Executor(calls),
        confirmation=confirmation,
    )

    result = coordinator.execute(_request(permission=ToolPermission.EXECUTE_PROJECT))

    assert result.status == ToolExecutionStatus.SUCCESS
    assert calls == [
        "catalog",
        "policy",
        "path",
        "confirmation",
        "audit",
        "executor",
        "audit",
    ]


def test_write_workspace_confirmation_allows_execution() -> None:
    calls: list[str] = []
    coordinator = ToolExecutionCoordinator(
        Catalog(calls),
        Policy(calls),
        Path(calls),
        RecordingAudit(calls),
        Executor(calls),
        confirmation=Confirmation(calls, approved=True),
    )

    result = coordinator.execute(_request(permission=ToolPermission.WRITE_WORKSPACE))

    assert result.status == ToolExecutionStatus.SUCCESS
    assert "confirmation" in calls


class Catalog(ToolCatalog):
    def __init__(self, calls: list[str]) -> None:
        self.calls = calls

    def definition_for(self, tool_name: str) -> ToolDefinition:
        self.calls.append("catalog")
        return ToolDefinition(
            name=tool_name,
            description="test",
            input_schema={"type": "object"},
        )


class MissingCatalog(Catalog):
    def definition_for(self, tool_name: str) -> ToolDefinition:
        self.calls.append("catalog")
        raise InvalidToolCallError("Unknown tool")


class Policy(ToolPolicy):
    def __init__(
        self,
        calls: list[str],
        decision: ToolPolicyDecision | None = None,
    ) -> None:
        self.calls = calls
        self.decision = decision or ToolPolicyDecision(PolicyDecisionKind.ALLOW)

    def decide(
        self, request: ToolExecutionRequest, definition: ToolDefinition
    ) -> ToolPolicyDecision:
        self.calls.append("policy")
        return self.decision


class Path(PathPolicy):
    def __init__(self, calls: list[str]) -> None:
        self.calls = calls

    def validate(
        self, request: ToolExecutionRequest, definition: ToolDefinition
    ) -> ToolExecutionContext:
        self.calls.append("path")
        return ToolExecutionContext(
            request=request,
            workspace_id="workspace",
            resolved_path="/workspace/file.txt",
            relative_path="file.txt",
        )


class DenyingPath(Path):
    def validate(
        self, request: ToolExecutionRequest, definition: ToolDefinition
    ) -> ToolExecutionContext:
        self.calls.append("path")
        raise InvalidToolCallError("path denied")


class RecordingAudit(AuditRecorder):
    def __init__(self, calls: list[str]) -> None:
        self.calls = calls
        self.events: list[ToolAuditEvent] = []

    def record(self, event: ToolAuditEvent) -> None:
        self.calls.append("audit")
        self.events.append(event)


class Executor(ToolExecutor):
    def __init__(self, calls: list[str]) -> None:
        self.calls = calls

    def execute(self, context: ToolExecutionContext) -> ToolExecutionResult:
        self.calls.append("executor")
        return ToolExecutionResult(
            request_id=context.request.request_id,
            tool_name=context.request.tool_name,
            status=ToolExecutionStatus.SUCCESS,
            content={"ok": True},
        )


class RaisingExecutor(Executor):
    def execute(self, context: ToolExecutionContext) -> ToolExecutionResult:
        self.calls.append("executor")
        raise RuntimeError("boom")


class Confirmation:
    def __init__(self, calls: list[str], approved: bool) -> None:
        self.calls = calls
        self.approved = approved

    def ensure_confirmed(
        self,
        session_id: str,
        workspace_id: str,
        permission: ToolPermission,
        request_id: str,
    ) -> bool:
        self.calls.append("confirmation")
        return self.approved


def _request(
    tool_name: str = "read_file",
    permission: ToolPermission = ToolPermission.READ_ONLY,
) -> ToolExecutionRequest:
    return ToolExecutionRequest(
        request_id="req-1",
        session_id="default",
        tool_name=tool_name,
        arguments={"path": "file.txt"},
        permission=permission,
    )
