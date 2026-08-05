"""In-memory confirmation grants for side-effecting tool permissions."""

from dataclasses import dataclass, field
from datetime import UTC, datetime

from ai_assistant.application.ports.tools import AuditRecorder, ConfirmationPrompter
from ai_assistant.domain.tools import (
    ConfirmationGrant,
    PolicyDecisionKind,
    ToolAuditEvent,
    ToolExecutionStatus,
    ToolPermission,
)

_CONFIRMATION_TOOL_NAME = "confirmation"
_CONFIRMATION_DENIED = "confirmation_denied"
_CONFIRMATION_ERROR = "confirmation_error"
_CONFIRMATION_NOT_REQUIRED = {
    ToolPermission.READ_ONLY,
    ToolPermission.READ_METADATA,
    ToolPermission.READ_CONTENT,
    ToolPermission.READ_REPOSITORY,
}
_CONFIRMATION_REQUIRED = {
    ToolPermission.EXECUTE_PROJECT,
    ToolPermission.WRITE_WORKSPACE,
}


@dataclass(slots=True)
class ConfirmationService:
    prompter: ConfirmationPrompter
    audit: AuditRecorder
    policy_version: str = "phase3-v1"
    _grants: dict[tuple[str, str, ToolPermission], ConfirmationGrant] = field(
        default_factory=dict,
        init=False,
    )

    def ensure_confirmed(
        self,
        session_id: str,
        workspace_id: str,
        permission: ToolPermission,
        request_id: str,
    ) -> bool:
        if permission in _CONFIRMATION_NOT_REQUIRED:
            return True
        if permission not in _CONFIRMATION_REQUIRED:
            self._record(request_id, session_id, workspace_id, permission, False)
            return False
        scope = (session_id, workspace_id, permission)
        if scope in self._grants:
            return True
        approved = self._prompt(session_id, workspace_id, permission)
        self._record(request_id, session_id, workspace_id, permission, approved)
        if approved:
            self._grants[scope] = ConfirmationGrant(
                session_id=session_id,
                workspace_id=workspace_id,
                permission=permission,
                granted_at=datetime.now(UTC),
                policy_version=self.policy_version,
            )
        return approved

    def revoke(
        self,
        session_id: str,
        workspace_id: str,
        permission: ToolPermission,
    ) -> None:
        self._grants.pop((session_id, workspace_id, permission), None)

    def revoke_all(self) -> None:
        self._grants.clear()

    def _prompt(
        self,
        session_id: str,
        workspace_id: str,
        permission: ToolPermission,
    ) -> bool:
        try:
            return bool(self.prompter.confirm(session_id, workspace_id, permission.value))
        except (EOFError, TimeoutError, ValueError):
            return False

    def _record(
        self,
        request_id: str,
        session_id: str,
        workspace_id: str,
        permission: ToolPermission,
        approved: bool,
    ) -> None:
        now = datetime.now(UTC)
        self.audit.record(
            ToolAuditEvent(
                request_id=request_id,
                session_id=session_id,
                tool_name=_CONFIRMATION_TOOL_NAME,
                permission=permission,
                decision=(
                    PolicyDecisionKind.ALLOW
                    if approved
                    else PolicyDecisionKind.DENY
                ),
                status=(
                    ToolExecutionStatus.ALLOWED
                    if approved
                    else ToolExecutionStatus.DENIED
                ),
                workspace_id=workspace_id,
                argument_summary={"permission": permission.value},
                started_at=now,
                ended_at=now,
                duration_ms=0,
                denial_reason=None if approved else _CONFIRMATION_DENIED,
                error_code=None if approved else _CONFIRMATION_ERROR,
            )
        )
