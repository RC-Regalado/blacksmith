"""Tool execution coordinator."""

from datetime import UTC, datetime

from ai_assistant.application.ports.tools import (
    AuditRecorder,
    PathPolicy,
    ToolCatalog,
    ToolExecutor,
    ToolPolicy,
)
from ai_assistant.application.confirmation import ConfirmationService
from ai_assistant.application.tool_policy import REASON_PATH_DENIED, REASON_UNKNOWN_TOOL
from ai_assistant.domain.errors import InvalidToolCallError
from ai_assistant.domain.tools import (
    PolicyDecisionKind,
    SanitizedToolError,
    ToolAuditEvent,
    ToolExecutionContext,
    ToolExecutionRequest,
    ToolExecutionResult,
    ToolExecutionStatus,
    ToolPolicyDecision,
    ToolPermission,
)

_CONFIRMATION_REQUIRED = {
    ToolPermission.EXECUTE_PROJECT,
    ToolPermission.WRITE_WORKSPACE,
}


class ToolExecutionCoordinator:
    def __init__(
        self,
        catalog: ToolCatalog,
        policy: ToolPolicy,
        path_policy: PathPolicy,
        audit: AuditRecorder,
        executor: ToolExecutor,
        confirmation: ConfirmationService | None = None,
    ) -> None:
        self._catalog = catalog
        self._policy = policy
        self._path_policy = path_policy
        self._audit = audit
        self._executor = executor
        self._confirmation = confirmation

    def execute(self, request: ToolExecutionRequest) -> ToolExecutionResult:
        try:
            definition = self._catalog.definition_for(request.tool_name)
        except InvalidToolCallError:
            return self._deny(request, REASON_UNKNOWN_TOOL)
        decision = self._policy.decide(request, definition)
        if decision.kind != PolicyDecisionKind.ALLOW:
            return self._deny(request, decision.reason_code or "denied")
        try:
            context = self._path_policy.validate(request, definition)
        except InvalidToolCallError:
            return self._deny(request, REASON_PATH_DENIED)
        if request.permission in _CONFIRMATION_REQUIRED:
            if self._confirmation is None:
                return self._deny_context(context, "confirmation_required")
            if not self._confirmation.ensure_confirmed(
                request.session_id,
                context.workspace_id,
                request.permission,
                request.request_id,
            ):
                return self._deny_context(context, "confirmation_denied")
        self._audit.record(_event(context, decision, ToolExecutionStatus.ALLOWED))
        result = self._execute(context)
        self._audit.record(_event(context, decision, result.status, result))
        return result

    def _deny(self, request: ToolExecutionRequest, reason_code: str) -> ToolExecutionResult:
        decision = ToolPolicyDecision(
            kind=PolicyDecisionKind.DENY,
            reason_code=reason_code,
        )
        context = ToolExecutionContext(request=request, workspace_id="unresolved")
        result = ToolExecutionResult(
            request_id=request.request_id,
            tool_name=request.tool_name,
            status=ToolExecutionStatus.DENIED,
            error=SanitizedToolError(code=reason_code, message="Tool request denied."),
        )
        self._audit.record(_event(context, decision, ToolExecutionStatus.DENIED, result))
        return result

    def _deny_context(
        self, context: ToolExecutionContext, reason_code: str
    ) -> ToolExecutionResult:
        decision = ToolPolicyDecision(
            kind=PolicyDecisionKind.DENY,
            reason_code=reason_code,
        )
        result = ToolExecutionResult(
            request_id=context.request.request_id,
            tool_name=context.request.tool_name,
            status=ToolExecutionStatus.DENIED,
            error=SanitizedToolError(code=reason_code, message="Tool request denied."),
        )
        self._audit.record(_event(context, decision, ToolExecutionStatus.DENIED, result))
        return result

    def _execute(self, context: ToolExecutionContext) -> ToolExecutionResult:
        try:
            return self._executor.execute(context)
        except Exception as exc:  # noqa: BLE001 - model-facing result must be sanitized.
            return ToolExecutionResult(
                request_id=context.request.request_id,
                tool_name=context.request.tool_name,
                status=ToolExecutionStatus.ERROR,
                error=SanitizedToolError(
                    code="executor_error",
                    message=str(exc) or "Tool executor failed.",
                ),
            )


def _event(
    context: ToolExecutionContext,
    decision: ToolPolicyDecision,
    status: ToolExecutionStatus,
    result: ToolExecutionResult | None = None,
) -> ToolAuditEvent:
    now = datetime.now(UTC)
    return ToolAuditEvent(
        request_id=context.request.request_id,
        session_id=context.request.session_id,
        tool_name=context.request.tool_name,
        permission=context.request.permission,
        decision=decision.kind,
        status=status,
        workspace_id=context.workspace_id,
        argument_summary=dict(context.request.arguments),
        started_at=now,
        ended_at=now,
        duration_ms=0,
        dry_run=context.request.dry_run,
        denial_reason=decision.reason_code,
        error_code=result.error.code if result and result.error else None,
    )
