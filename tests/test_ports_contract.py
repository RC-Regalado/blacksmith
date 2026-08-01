"""Basic contract tests for application ports."""

from datetime import datetime, timezone

import pytest

from ai_assistant.application.ports.memory import ConversationMemory, SessionId
from ai_assistant.application.ports.models import ModelProvider
from ai_assistant.application.ports.tools import (
    AuditRecorder,
    PathPolicy,
    ToolCatalog,
    ToolExecutor,
    ToolPolicy,
)
from ai_assistant.agent.message import Message
from ai_assistant.domain.tools import (
    PolicyDecisionKind,
    ToolAuditEvent,
    ToolDefinition,
    ToolExecutionContext,
    ToolExecutionRequest,
    ToolExecutionResult,
    ToolExecutionStatus,
    ToolPermission,
    ToolPolicyDecision,
)


pytestmark = pytest.mark.contract


def test_model_provider_contract_returns_message() -> None:
    provider: ModelProvider = ContractModel()

    response = provider.chat([Message(role="user", content="Hello")])

    assert response == Message(role="assistant", content="ok")


def test_conversation_memory_contract_preserves_messages() -> None:
    memory: ConversationMemory = ContractMemory()

    memory.append_many(
        "default",
        [
            Message(role="user", content="Hello"),
            Message(role="assistant", content="ok"),
        ],
    )

    assert memory.history("default") == [
        Message(role="user", content="Hello", session_id="default"),
        Message(role="assistant", content="ok", session_id="default"),
    ]


def test_tool_execution_ports_can_be_implemented_by_fakes() -> None:
    catalog: ToolCatalog = ContractToolCatalog()
    policy: ToolPolicy = ContractToolPolicy()
    path_policy: PathPolicy = ContractPathPolicy()
    executor: ToolExecutor = ContractToolExecutor()
    audit: AuditRecorder = ContractAuditRecorder()
    request = ToolExecutionRequest(
        request_id="req-1",
        session_id="default",
        tool_name="read_file",
        arguments={"path": "notes.txt"},
    )

    definition = catalog.definition_for(request.tool_name)
    decision = policy.decide(request, definition)
    context = path_policy.validate(request, definition)
    result = executor.execute(context)
    audit.record(_audit_event(request, decision, result))

    assert decision == ToolPolicyDecision(kind=PolicyDecisionKind.ALLOW)
    assert isinstance(context, ToolExecutionContext)
    assert result == ToolExecutionResult(
        request_id="req-1",
        tool_name="read_file",
        status=ToolExecutionStatus.SUCCESS,
        content={"ok": True},
    )
    assert len(audit.events) == 1
    assert audit.events[0].request_id == "req-1"


def test_tool_executor_contract_receives_authorized_context() -> None:
    executor: ToolExecutor = ContractToolExecutor()
    request = ToolExecutionRequest(
        request_id="req-2",
        session_id="default",
        tool_name="list_dir",
        arguments={"path": "."},
    )
    context = ToolExecutionContext(request=request, workspace_id="workspace")

    result = executor.execute(context)

    assert result.status == ToolExecutionStatus.SUCCESS


class ContractModel(ModelProvider):
    def chat(self, messages: list[Message]) -> Message:
        return Message(role="assistant", content="ok")


class ContractMemory(ConversationMemory):
    def __init__(self) -> None:
        self._messages: list[Message] = []

    def append(self, session_id: SessionId, message: Message) -> None:
        self.append_many(session_id, [message])

    def append_many(self, session_id: SessionId, messages: list[Message]) -> None:
        self._messages.extend(
            Message(role=message.role, content=message.content, session_id=session_id)
            for message in messages
        )

    def history(self, session_id: SessionId) -> list[Message]:
        return [
            message for message in self._messages if message.session_id == session_id
        ]


class ContractToolCatalog(ToolCatalog):
    def definition_for(self, tool_name: str) -> ToolDefinition:
        return ToolDefinition(
            name=tool_name,
            description="Read-only test tool.",
            input_schema={"type": "object"},
        )


class ContractToolPolicy(ToolPolicy):
    def decide(
        self, request: ToolExecutionRequest, definition: ToolDefinition
    ) -> ToolPolicyDecision:
        return ToolPolicyDecision(kind=PolicyDecisionKind.ALLOW)


class ContractPathPolicy(PathPolicy):
    def validate(
        self, request: ToolExecutionRequest, definition: ToolDefinition
    ) -> ToolExecutionContext:
        return ToolExecutionContext(request=request, workspace_id="workspace")


class ContractToolExecutor(ToolExecutor):
    def execute(self, context: ToolExecutionContext) -> ToolExecutionResult:
        return ToolExecutionResult(
            request_id=context.request.request_id,
            tool_name=context.request.tool_name,
            status=ToolExecutionStatus.SUCCESS,
            content={"ok": True},
        )


class ContractAuditRecorder(AuditRecorder):
    def __init__(self) -> None:
        self.events: list[ToolAuditEvent] = []

    def record(self, event: ToolAuditEvent) -> None:
        self.events.append(event)


def _audit_event(
    request: ToolExecutionRequest,
    decision: ToolPolicyDecision,
    result: ToolExecutionResult,
) -> ToolAuditEvent:
    now = datetime.now(timezone.utc)
    return ToolAuditEvent(
        request_id=request.request_id,
        session_id=request.session_id,
        tool_name=request.tool_name,
        permission=ToolPermission.READ_ONLY,
        decision=decision.kind,
        status=result.status,
        workspace_id="workspace",
        argument_summary={"path": "notes.txt"},
        started_at=now,
        ended_at=now,
        duration_ms=0,
    )
