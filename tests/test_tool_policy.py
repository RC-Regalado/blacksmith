"""Tests for deny-by-default tool policy."""

import pytest

from ai_assistant.application.tool_catalog import StaticToolCatalog
from ai_assistant.application.tool_policy import (
    REASON_INVALID_ARGUMENTS,
    REASON_LIMIT_EXCEEDED,
    REASON_PATH_DENIED,
    REASON_PERMISSION_DENIED,
    REASON_TIMEOUT_EXCEEDED,
    REASON_TOOL_DISABLED,
    REASON_UNKNOWN_TOOL,
    DenyByDefaultToolPolicy,
)
from ai_assistant.domain.tools import (
    PolicyDecisionKind,
    ToolExecutionContext,
    ToolExecutionRequest,
    ToolExecutionResult,
    ToolExecutionStatus,
)


pytestmark = pytest.mark.unit


def test_allowed_read_file_request_is_allowed() -> None:
    decision = _decide("read_file", {"path": "notes.txt", "max_bytes": 1024})

    assert decision.kind == PolicyDecisionKind.ALLOW
    assert decision.reason_code is None


def test_unknown_tool_is_denied_with_stable_reason() -> None:
    decision = DenyByDefaultToolPolicy().deny_unknown_tool()

    assert decision.reason_code == REASON_UNKNOWN_TOOL


@pytest.mark.parametrize(
    ("tool_name", "arguments"),
    [
        ("read_file", {}),
        ("read_file", {"path": ""}),
        ("read_file", {"path": "notes.txt", "offset": "0"}),
        ("read_file", {"path": "notes.txt", "max_bytes": True}),
        ("list_directory", {"path": ".", "recursive": "yes"}),
        ("list_directory", {"path": ".", "include_hidden": 1}),
    ],
)
def test_malformed_arguments_are_denied(tool_name: str, arguments: dict[str, object]) -> None:
    decision = _decide(tool_name, arguments)

    assert decision.reason_code == REASON_INVALID_ARGUMENTS


@pytest.mark.parametrize(
    ("tool_name", "arguments"),
    [
        ("read_file", {"path": "notes.txt", "max_bytes": 65537}),
        ("read_file", {"path": "notes.txt", "offset": -1}),
        ("list_directory", {"path": ".", "max_entries": 1001}),
        ("list_directory", {"path": ".", "max_depth": 4}),
    ],
)
def test_values_above_hard_maximum_are_denied(
    tool_name: str, arguments: dict[str, object]
) -> None:
    decision = _decide(tool_name, arguments)

    assert decision.reason_code == REASON_LIMIT_EXCEEDED


def test_timeout_above_hard_maximum_is_denied() -> None:
    decision = _decide(
        "read_file",
        {"path": "notes.txt"},
        timeout_seconds=31.0,
    )

    assert decision.reason_code == REASON_TIMEOUT_EXCEEDED


def test_permission_above_static_permission_is_denied() -> None:
    decision = _decide("read_file", {"path": "notes.txt"}, permission="write")

    assert decision.reason_code == REASON_PERMISSION_DENIED


def test_disabled_policy_denies_with_stable_reason() -> None:
    catalog = StaticToolCatalog()
    request = _request("read_file", {"path": "notes.txt"})

    decision = DenyByDefaultToolPolicy(enabled=False).decide(
        request,
        catalog.definition_for("read_file"),
    )

    assert decision.reason_code == REASON_TOOL_DISABLED


def test_path_policy_failure_maps_to_stable_reason() -> None:
    decision = DenyByDefaultToolPolicy().deny_path_result()

    assert decision.reason_code == REASON_PATH_DENIED


def test_denied_request_does_not_reach_executor() -> None:
    executor = RecordingExecutor()
    decision = _decide("read_file", {"path": "notes.txt", "max_bytes": 65537})
    request = _request("read_file", {"path": "notes.txt"})

    result = _execute_if_allowed(decision.kind, executor, request)

    assert result is None
    assert executor.calls == 0


class RecordingExecutor:
    def __init__(self) -> None:
        self.calls = 0

    def execute(self, context: ToolExecutionContext) -> ToolExecutionResult:
        self.calls += 1
        return ToolExecutionResult(
            request_id=context.request.request_id,
            tool_name=context.request.tool_name,
            status=ToolExecutionStatus.SUCCESS,
        )


def _decide(
    tool_name: str,
    arguments: dict[str, object],
    timeout_seconds: float = 5.0,
    permission: object = "read_only",
):
    catalog = StaticToolCatalog()
    request = _request(tool_name, arguments, timeout_seconds, permission)
    return DenyByDefaultToolPolicy().decide(request, catalog.definition_for(tool_name))


def _request(
    tool_name: str,
    arguments: dict[str, object],
    timeout_seconds: float = 5.0,
    permission: object = "read_only",
) -> ToolExecutionRequest:
    return ToolExecutionRequest(
        request_id="req-1",
        session_id="default",
        tool_name=tool_name,
        arguments=arguments,
        permission=permission,  # type: ignore[arg-type]
        timeout_seconds=timeout_seconds,
    )


def _execute_if_allowed(
    decision: PolicyDecisionKind,
    executor: RecordingExecutor,
    request: ToolExecutionRequest,
) -> ToolExecutionResult | None:
    if decision != PolicyDecisionKind.ALLOW:
        return None
    return executor.execute(ToolExecutionContext(request=request, workspace_id="w"))
