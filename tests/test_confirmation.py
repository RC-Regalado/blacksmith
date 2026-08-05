"""Tests for in-memory confirmation grants."""

from dataclasses import dataclass

import pytest

from ai_assistant.application.confirmation import ConfirmationService
from ai_assistant.application.ports.tools import AuditRecorder, ConfirmationPrompter
from ai_assistant.domain.tools import (
    PolicyDecisionKind,
    ToolAuditEvent,
    ToolExecutionStatus,
    ToolPermission,
)


pytestmark = pytest.mark.unit


def test_same_scope_reuses_confirmation_without_reprompt() -> None:
    prompter = Prompt([True])
    audit = RecordingAudit()
    service = ConfirmationService(prompter, audit)

    assert service.ensure_confirmed(
        "session-1", "workspace-1", ToolPermission.WRITE_WORKSPACE, "req-1"
    )
    assert service.ensure_confirmed(
        "session-1", "workspace-1", ToolPermission.WRITE_WORKSPACE, "req-2"
    )

    assert prompter.calls == [
        ("session-1", "workspace-1", ToolPermission.WRITE_WORKSPACE.value)
    ]
    assert [event.status for event in audit.events] == [ToolExecutionStatus.ALLOWED]


@pytest.mark.parametrize(
    ("session_id", "workspace_id", "permission"),
    [
        ("session-2", "workspace-1", ToolPermission.WRITE_WORKSPACE),
        ("session-1", "workspace-2", ToolPermission.WRITE_WORKSPACE),
        ("session-1", "workspace-1", ToolPermission.EXECUTE_PROJECT),
    ],
)
def test_new_scope_prompts_again(
    session_id: str,
    workspace_id: str,
    permission: ToolPermission,
) -> None:
    prompter = Prompt([True, True])
    service = ConfirmationService(prompter, RecordingAudit())
    assert service.ensure_confirmed(
        "session-1", "workspace-1", ToolPermission.WRITE_WORKSPACE, "req-1"
    )

    assert service.ensure_confirmed(session_id, workspace_id, permission, "req-2")

    assert len(prompter.calls) == 2


def test_denial_is_audited_and_does_not_create_grant() -> None:
    prompter = Prompt([False, True])
    audit = RecordingAudit()
    service = ConfirmationService(prompter, audit)

    assert not service.ensure_confirmed(
        "session-1", "workspace-1", ToolPermission.EXECUTE_PROJECT, "req-1"
    )
    assert service.ensure_confirmed(
        "session-1", "workspace-1", ToolPermission.EXECUTE_PROJECT, "req-2"
    )

    assert len(prompter.calls) == 2
    assert [event.decision for event in audit.events] == [
        PolicyDecisionKind.DENY,
        PolicyDecisionKind.ALLOW,
    ]
    assert audit.events[0].denial_reason == "confirmation_denied"


@pytest.mark.parametrize("error", [EOFError(), TimeoutError(), ValueError()])
def test_prompt_errors_deny_by_default(error: Exception) -> None:
    audit = RecordingAudit()

    service = ConfirmationService(RaisingPrompt(error), audit)

    assert not service.ensure_confirmed(
        "session-1", "workspace-1", ToolPermission.WRITE_WORKSPACE, "req-1"
    )
    assert audit.events[0].status == ToolExecutionStatus.DENIED


def test_revoke_requires_confirmation_again() -> None:
    prompter = Prompt([True, True])
    service = ConfirmationService(prompter, RecordingAudit())

    assert service.ensure_confirmed(
        "session-1", "workspace-1", ToolPermission.WRITE_WORKSPACE, "req-1"
    )
    service.revoke("session-1", "workspace-1", ToolPermission.WRITE_WORKSPACE)
    assert service.ensure_confirmed(
        "session-1", "workspace-1", ToolPermission.WRITE_WORKSPACE, "req-2"
    )

    assert len(prompter.calls) == 2


def test_read_permissions_do_not_prompt() -> None:
    prompter = Prompt([])

    assert ConfirmationService(prompter, RecordingAudit()).ensure_confirmed(
        "session-1", "workspace-1", ToolPermission.READ_CONTENT, "req-1"
    )
    assert prompter.calls == []


@dataclass
class Prompt(ConfirmationPrompter):
    responses: list[bool]

    def __post_init__(self) -> None:
        self.calls: list[tuple[str, str, str]] = []

    def confirm(self, session_id: str, workspace_id: str, permission: str) -> bool:
        self.calls.append((session_id, workspace_id, permission))
        return self.responses.pop(0)


@dataclass
class RaisingPrompt(ConfirmationPrompter):
    error: Exception

    def confirm(self, session_id: str, workspace_id: str, permission: str) -> bool:
        raise self.error


class RecordingAudit(AuditRecorder):
    def __init__(self) -> None:
        self.events: list[ToolAuditEvent] = []

    def record(self, event: ToolAuditEvent) -> None:
        self.events.append(event)
