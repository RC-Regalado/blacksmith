"""Test-oriented tool executors without external effects."""

from collections.abc import Mapping

from ai_assistant.application.ports.tools import ToolExecutor
from ai_assistant.domain.tools import (
    SanitizedToolError,
    ToolExecutionContext,
    ToolExecutionResult,
    ToolExecutionStatus,
)


class FakeToolExecutor(ToolExecutor):
    def __init__(
        self,
        status: ToolExecutionStatus = ToolExecutionStatus.SUCCESS,
        content: Mapping[str, object] | None = None,
        error_code: str = "fake_error",
    ) -> None:
        self.calls: list[ToolExecutionContext] = []
        self._status = status
        self._content = dict(content or {"ok": True})
        self._error_code = error_code

    def execute(self, context: ToolExecutionContext) -> ToolExecutionResult:
        self.calls.append(context)
        error = None
        if self._status in {ToolExecutionStatus.ERROR, ToolExecutionStatus.TIMEOUT}:
            error = SanitizedToolError(
                code=self._error_code,
                message="Fake tool execution failed.",
            )
        return ToolExecutionResult(
            request_id=context.request.request_id,
            tool_name=context.request.tool_name,
            status=self._status,
            content=None if error else self._content,
            error=error,
        )


class DryRunToolExecutor(ToolExecutor):
    def execute(self, context: ToolExecutionContext) -> ToolExecutionResult:
        return ToolExecutionResult(
            request_id=context.request.request_id,
            tool_name=context.request.tool_name,
            status=ToolExecutionStatus.SUCCESS,
            content={
                "dry_run": True,
                "tool_name": context.request.tool_name,
                "arguments": dict(context.request.arguments),
            },
        )
