"""Tool-loop diagnostic event helpers."""

from collections.abc import Mapping
from datetime import UTC, datetime
import logging

from ai_assistant.application.ports.tools import (
    InteractionDiagnosticLogger,
    ToolDiagnosticLogger,
)
from ai_assistant.domain.tools import (
    InteractionLogEvent,
    InteractionStage,
    SanitizedToolError,
    ToolCallLogEvent,
    ToolDiagnosticStatus,
    ToolExecutionRequest,
    ToolExecutionResult,
    ToolExecutionStatus,
)

logger = logging.getLogger(__name__)


class NullToolDiagnosticLogger(ToolDiagnosticLogger):
    def record(self, event: ToolCallLogEvent) -> None:
        return None


class NullInteractionDiagnosticLogger(InteractionDiagnosticLogger):
    def record(self, event: InteractionLogEvent) -> None:
        return None


class InteractionDiagnostics:
    """Emits `InteractionLogEvent`s for the non-tool stages of one turn (ADR-070).

    Every event carries the turn's `interaction_id`, so a reader can
    reconstruct one complete interaction (context/retrieval, model
    request/response, tool activity, final synthesis, completion) by
    grouping the shared JSONL stream on that ID alone.
    """

    def __init__(
        self,
        sink: InteractionDiagnosticLogger | None,
        provider: str,
        model: str,
    ) -> None:
        self._sink = sink or NullInteractionDiagnosticLogger()
        self._provider = provider or "unknown"
        self._model = model or "unknown"

    def record(
        self,
        stage: InteractionStage,
        *,
        session_id: str,
        interaction_id: str | None,
        payload: Mapping[str, object],
        duration_ms: float = 0.0,
    ) -> None:
        if interaction_id is None:
            return
        try:
            self._sink.record(
                InteractionLogEvent(
                    timestamp=datetime.now(UTC),
                    interaction_id=interaction_id,
                    session_id=session_id,
                    provider=self._provider,
                    model=self._model,
                    stage=stage,
                    payload=payload,
                    duration_ms=duration_ms,
                )
            )
        except Exception:  # noqa: BLE001 - diagnostics must not affect the turn.
            logger.warning("interaction diagnostic logging failed", exc_info=True)


class ToolLoopDiagnostics:
    def __init__(
        self,
        sink: ToolDiagnosticLogger | None,
        provider: str,
        model: str,
    ) -> None:
        self._sink = sink or NullToolDiagnosticLogger()
        self._provider = provider or "unknown"
        self._model = model or "unknown"

    def requested(
        self,
        request: ToolExecutionRequest,
        *,
        round_index: int,
        tool_call_count: int,
        capability_name: str | None = None,
    ) -> None:
        self._record(
            request,
            ToolDiagnosticStatus.REQUESTED,
            round_index,
            tool_call_count,
            capability_name=capability_name,
        )

    def completed(
        self,
        request: ToolExecutionRequest,
        result: ToolExecutionResult,
        *,
        round_index: int,
        tool_call_count: int,
        duration_ms: float,
        capability_name: str | None = None,
    ) -> None:
        self._record(
            request,
            _status(result.status),
            round_index,
            tool_call_count,
            result=_result_payload(result),
            error=_error_payload(result.error),
            duration_ms=duration_ms,
            capability_name=capability_name,
        )

    def rejected(
        self,
        request: ToolExecutionRequest,
        *,
        round_index: int,
        tool_call_count: int,
        code: str,
        message: str,
        capability_name: str | None = None,
    ) -> None:
        self._record(
            request,
            ToolDiagnosticStatus.REJECTED,
            round_index,
            tool_call_count,
            error={"code": code, "message": message},
            capability_name=capability_name,
        )

    def recovery(
        self,
        request: ToolExecutionRequest,
        *,
        stage: ToolDiagnosticStatus,
        round_index: int,
        tool_call_count: int,
        requested_path: str | None,
        resolved_path: str | None,
        executor_operations: int,
        recovery_operations: int,
        code: str | None = None,
        message: str | None = None,
        capability_name: str | None = None,
    ) -> None:
        self._record(
            request,
            stage,
            round_index,
            tool_call_count,
            result={
                "requested_path": requested_path,
                "resolved_path": resolved_path,
                "model_tool_requests": 1,
                "executor_operations": executor_operations,
                "recovery_operations": recovery_operations,
            },
            error={"code": code, "message": message} if code else None,
            capability_name=capability_name,
        )

    def _record(
        self,
        request: ToolExecutionRequest,
        status: ToolDiagnosticStatus,
        round_index: int,
        tool_call_count: int,
        *,
        result: Mapping[str, object] | None = None,
        error: Mapping[str, object] | None = None,
        duration_ms: float = 0.0,
        capability_name: str | None = None,
    ) -> None:
        try:
            self._sink.record(
                ToolCallLogEvent(
                    timestamp=datetime.now(UTC),
                    session_id=request.session_id,
                    provider=self._provider,
                    model=self._model,
                    tool_name=request.tool_name,
                    capability_name=capability_name,
                    tool_call_id=request.request_id,
                    round_index=round_index,
                    tool_call_count=tool_call_count,
                    status=status,
                    arguments=request.arguments,
                    result=result,
                    error=error,
                    duration_ms=duration_ms,
                    interaction_id=request.interaction_id,
                )
            )
        except Exception:  # noqa: BLE001 - diagnostics must not affect tool execution.
            logger.warning("tool diagnostic logging failed", exc_info=True)


def _status(status: ToolExecutionStatus) -> ToolDiagnosticStatus:
    return {
        ToolExecutionStatus.SUCCESS: ToolDiagnosticStatus.EXECUTED,
        ToolExecutionStatus.DENIED: ToolDiagnosticStatus.REJECTED,
        ToolExecutionStatus.TIMEOUT: ToolDiagnosticStatus.TIMEOUT,
        ToolExecutionStatus.ERROR: ToolDiagnosticStatus.FAILED,
        ToolExecutionStatus.ALLOWED: ToolDiagnosticStatus.REQUESTED,
    }[status]


def _result_payload(result: ToolExecutionResult) -> Mapping[str, object]:
    payload: dict[str, object] = {
        "status": result.status.value,
        "truncated": result.truncated,
    }
    if result.content is not None:
        payload["content"] = dict(result.content)
    return payload


def _error_payload(error: SanitizedToolError | None) -> Mapping[str, object] | None:
    if error is None:
        return None
    return {"code": error.code, "message": error.message}
