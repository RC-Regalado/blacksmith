"""Tool execution coordinator."""

from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

from ai_assistant.application.ports.tools import (
    AuditRecorder,
    PathPolicy,
    ToolCatalog,
    ToolDiagnosticLogger,
    ToolExecutor,
    ToolPolicy,
)
from ai_assistant.application.confirmation import ConfirmationService
from ai_assistant.application.path_recovery import PathRecoveryPolicy
from ai_assistant.application.tool_catalog import FILE_METADATA, READ_FILE
from ai_assistant.application.tool_diagnostics import ToolLoopDiagnostics
from ai_assistant.application.tool_policy import REASON_PATH_DENIED, REASON_UNKNOWN_TOOL
from ai_assistant.domain.errors import InvalidToolCallError
from ai_assistant.domain.tools import (
    PolicyDecisionKind,
    SanitizedToolError,
    ToolAuditEvent,
    ToolDefinition,
    ToolDiagnosticStatus,
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

# Tools eligible for automatic case-only path recovery. Deliberately narrow:
# read-only, single-path tools where re-reading under a corrected name has no
# side effects. `write` must never appear here (ADR-030 controlled write
# semantics; a write must never silently retarget itself).
_RECOVERABLE_TOOLS = {READ_FILE, FILE_METADATA}

_ROUND_INDEX = 1
_TOOL_CALL_COUNT = 1


class ToolExecutionCoordinator:
    def __init__(
        self,
        catalog: ToolCatalog,
        policy: ToolPolicy,
        path_policy: PathPolicy,
        audit: AuditRecorder,
        executor: ToolExecutor,
        confirmation: ConfirmationService | None = None,
        path_recovery: PathRecoveryPolicy | None = None,
        diagnostics: ToolDiagnosticLogger | None = None,
        model_provider_name: str = "unknown",
        model_name: str = "unknown",
    ) -> None:
        self._catalog = catalog
        self._policy = policy
        self._path_policy = path_policy
        self._audit = audit
        self._executor = executor
        self._confirmation = confirmation
        self._path_recovery = path_recovery
        self._diagnostics = ToolLoopDiagnostics(diagnostics, model_provider_name, model_name)

    def execute(self, request: ToolExecutionRequest) -> ToolExecutionResult:
        try:
            definition = self._catalog.definition_for(request.tool_name)
        except InvalidToolCallError:
            return self._deny(request, REASON_UNKNOWN_TOOL)
        decision = self._policy.decide(request, definition)
        if decision.kind != PolicyDecisionKind.ALLOW:
            return self._deny(request, decision.reason_code or "denied")
        context, executor_operations = self._resolve_path(request, definition)
        if context is None:
            return self._deny(request, REASON_PATH_DENIED, executor_operations=executor_operations)
        active_request = context.request
        if active_request.permission in _CONFIRMATION_REQUIRED:
            if self._confirmation is None:
                return self._deny_context(
                    context, "confirmation_required", executor_operations=executor_operations
                )
            if not self._confirmation.ensure_confirmed(
                active_request.session_id,
                context.workspace_id,
                active_request.permission,
                active_request.request_id,
            ):
                return self._deny_context(
                    context, "confirmation_denied", executor_operations=executor_operations
                )
        self._audit.record(_event(context, decision, ToolExecutionStatus.ALLOWED))
        result = replace(self._execute(context), executor_operations=executor_operations)
        self._audit.record(_event(context, decision, result.status, result))
        return result

    def _resolve_path(
        self, request: ToolExecutionRequest, definition: ToolDefinition
    ) -> tuple[ToolExecutionContext | None, int]:
        """Validate the request's path, attempting one bounded recovery.

        A single internal retry (case-only path correction) may run here
        without consuming an additional model tool round: this method is
        invoked exactly once per `execute()` call, which is itself exactly
        one model tool request (ADR-024/ADR-069 loop round accounting is the
        caller's responsibility). Any internal retry is invisible above this
        layer. Returns the resolved context (or `None` on denial) alongside
        how many executor operations the resolution attempt spent, so the
        caller can enforce a platform-owned `max_executor_operations` budget.
        """
        try:
            return self._path_policy.validate(request, definition), 1
        except InvalidToolCallError as exc:
            if not self._recovery_eligible(exc, definition):
                return None, 1
            return self._attempt_recovery(request, definition, exc)

    def _recovery_eligible(
        self, exc: InvalidToolCallError, definition: ToolDefinition
    ) -> bool:
        if self._path_recovery is None:
            return False
        if definition.name not in _RECOVERABLE_TOOLS:
            return False
        return bool(getattr(exc, "recoverable", False))

    def _attempt_recovery(
        self,
        request: ToolExecutionRequest,
        definition: ToolDefinition,
        original_exc: InvalidToolCallError,
    ) -> tuple[ToolExecutionContext | None, int]:
        requested_path = str(request.arguments.get("path", ""))
        # Operation 1 is the failed attempt already made by `_resolve_path`.
        executor_operations = 1
        recovery_operations = 1
        self._recovery_event(
            request,
            ToolDiagnosticStatus.RECOVERY_STARTED,
            requested_path,
            None,
            executor_operations,
            recovery_operations,
        )
        try:
            executor_operations += 1  # parent-directory lookup
            corrected_relative = self._path_recovery.resolve(Path(requested_path))
        except InvalidToolCallError as exc:
            self._recovery_event(
                request,
                ToolDiagnosticStatus.RECOVERY_FAILED,
                requested_path,
                None,
                executor_operations,
                recovery_operations,
                code=getattr(exc, "code", REASON_PATH_DENIED),
                message=str(exc) or "Recovery lookup failed.",
            )
            return None, executor_operations

        resolved_path = corrected_relative.as_posix()
        self._recovery_event(
            request,
            ToolDiagnosticStatus.RECOVERY_CANDIDATE,
            requested_path,
            resolved_path,
            executor_operations,
            recovery_operations,
        )
        corrected_request = _with_path(request, resolved_path)
        self._recovery_event(
            corrected_request,
            ToolDiagnosticStatus.RECOVERY_RETRY,
            requested_path,
            resolved_path,
            executor_operations,
            recovery_operations,
        )
        executor_operations += 1  # the retried validate + read as one unit
        try:
            context = self._path_policy.validate(corrected_request, definition)
        except InvalidToolCallError as exc:
            self._recovery_event(
                corrected_request,
                ToolDiagnosticStatus.RECOVERY_FAILED,
                requested_path,
                resolved_path,
                executor_operations,
                recovery_operations,
                code=getattr(exc, "code", REASON_PATH_DENIED),
                message=str(exc) or "Recovery retry failed.",
            )
            return None, executor_operations

        self._recovery_event(
            corrected_request,
            ToolDiagnosticStatus.RECOVERY_SUCCESS,
            requested_path,
            resolved_path,
            executor_operations,
            recovery_operations,
        )
        return context, executor_operations

    def _recovery_event(
        self,
        request: ToolExecutionRequest,
        stage: ToolDiagnosticStatus,
        requested_path: str,
        resolved_path: str | None,
        executor_operations: int,
        recovery_operations: int,
        *,
        code: str | None = None,
        message: str | None = None,
    ) -> None:
        self._diagnostics.recovery(
            request,
            stage=stage,
            round_index=_ROUND_INDEX,
            tool_call_count=_TOOL_CALL_COUNT,
            requested_path=requested_path,
            resolved_path=resolved_path,
            executor_operations=executor_operations,
            recovery_operations=recovery_operations,
            code=code,
            message=message,
        )

    def _deny(
        self, request: ToolExecutionRequest, reason_code: str, *, executor_operations: int = 0
    ) -> ToolExecutionResult:
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
            executor_operations=executor_operations,
        )
        self._audit.record(_event(context, decision, ToolExecutionStatus.DENIED, result))
        return result

    def _deny_context(
        self, context: ToolExecutionContext, reason_code: str, *, executor_operations: int = 1
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
            executor_operations=executor_operations,
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


def _with_path(request: ToolExecutionRequest, path: str) -> ToolExecutionRequest:
    arguments = dict(request.arguments)
    arguments["path"] = path
    return ToolExecutionRequest(
        request_id=request.request_id,
        session_id=request.session_id,
        tool_name=request.tool_name,
        arguments=arguments,
        permission=request.permission,
        timeout_seconds=request.timeout_seconds,
        dry_run=request.dry_run,
        interaction_id=request.interaction_id,
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
        interaction_id=context.request.interaction_id,
    )
