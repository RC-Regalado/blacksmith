"""Tests for fake and dry-run tool executors."""

import pytest

from ai_assistant.application.tool_executors import DryRunToolExecutor, FakeToolExecutor
from ai_assistant.domain.tools import (
    PolicyDecisionKind,
    ToolExecutionContext,
    ToolExecutionRequest,
    ToolExecutionResult,
    ToolExecutionStatus,
)


pytestmark = pytest.mark.unit


def test_allowed_request_reaches_fake_executor() -> None:
    executor = FakeToolExecutor()
    context = _context()

    result = _execute_if_allowed(PolicyDecisionKind.ALLOW, executor, context)

    assert result is not None
    assert result.status == ToolExecutionStatus.SUCCESS
    assert executor.calls == [context]


def test_denied_request_does_not_reach_fake_executor() -> None:
    executor = FakeToolExecutor()

    result = _execute_if_allowed(PolicyDecisionKind.DENY, executor, _context())

    assert result is None
    assert executor.calls == []


@pytest.mark.parametrize(
    "status",
    [
        ToolExecutionStatus.SUCCESS,
        ToolExecutionStatus.TIMEOUT,
        ToolExecutionStatus.ERROR,
    ],
)
def test_fake_executor_reproduces_success_timeout_and_failure(
    status: ToolExecutionStatus,
) -> None:
    result = FakeToolExecutor(status=status).execute(_context())

    assert result.status == status
    if status == ToolExecutionStatus.SUCCESS:
        assert result.content == {"ok": True}
        assert result.error is None
    else:
        assert result.content is None
        assert result.error is not None
        assert result.error.code == "fake_error"


def test_dry_run_executor_produces_no_external_effect() -> None:
    context = _context(arguments={"path": "README.md", "max_bytes": 10})

    result = DryRunToolExecutor().execute(context)

    assert result == ToolExecutionResult(
        request_id="req-1",
        tool_name="read_file",
        status=ToolExecutionStatus.SUCCESS,
        content={
            "dry_run": True,
            "tool_name": "read_file",
            "arguments": {"path": "README.md", "max_bytes": 10},
        },
    )


def _context(arguments: dict[str, object] | None = None) -> ToolExecutionContext:
    return ToolExecutionContext(
        request=ToolExecutionRequest(
            request_id="req-1",
            session_id="default",
            tool_name="read_file",
            arguments=arguments or {"path": "README.md"},
        ),
        workspace_id="workspace",
        resolved_path="/workspace/README.md",
        relative_path="README.md",
    )


def _execute_if_allowed(
    decision: PolicyDecisionKind,
    executor: FakeToolExecutor,
    context: ToolExecutionContext,
) -> ToolExecutionResult | None:
    if decision != PolicyDecisionKind.ALLOW:
        return None
    return executor.execute(context)
