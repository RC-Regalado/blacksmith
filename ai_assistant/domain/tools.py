"""Declarative tool-call domain models."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from types import MappingProxyType

from ai_assistant.domain.errors import InvalidToolCallError


@dataclass(frozen=True, slots=True)
class ToolCall:
    name: str
    arguments: Mapping[str, object]
    tool_call_id: str | None = None


@dataclass(frozen=True, slots=True)
class ToolCallPlan:
    has_tool_call: bool
    tool_call: ToolCall | None = None

    @property
    def tool_name(self) -> str | None:
        return self.tool_call.name if self.tool_call else None


class ToolPermission(StrEnum):
    READ_ONLY = "read_only"


@dataclass(frozen=True, slots=True)
class ToolDefinition:
    name: str
    description: str
    input_schema: Mapping[str, object]
    permission: ToolPermission = ToolPermission.READ_ONLY
    defaults: Mapping[str, object] = field(default_factory=dict)
    limits: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require_text(self.name, "name")
        _require_text(self.description, "description")
        object.__setattr__(self, "input_schema", _freeze(self.input_schema))
        object.__setattr__(self, "defaults", _freeze(self.defaults))
        object.__setattr__(self, "limits", _freeze(self.limits))


class PolicyDecisionKind(StrEnum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_CONFIRMATION = "require_confirmation"


class ToolExecutionStatus(StrEnum):
    ALLOWED = "allowed"
    DENIED = "denied"
    SUCCESS = "success"
    TIMEOUT = "timeout"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class ToolExecutionRequest:
    request_id: str
    session_id: str
    tool_name: str
    arguments: Mapping[str, object]
    permission: ToolPermission = ToolPermission.READ_ONLY
    timeout_seconds: float = 5.0
    dry_run: bool = False

    def __post_init__(self) -> None:
        _require_text(self.request_id, "request_id")
        _require_text(self.session_id, "session_id")
        _require_text(self.tool_name, "tool_name")
        if not isinstance(self.arguments, Mapping):
            raise InvalidToolCallError("arguments must be an object.")
        if self.timeout_seconds <= 0:
            raise InvalidToolCallError("timeout_seconds must be positive.")


@dataclass(frozen=True, slots=True)
class ToolPolicyDecision:
    kind: PolicyDecisionKind
    reason_code: str | None = None

    def __post_init__(self) -> None:
        if self.kind == PolicyDecisionKind.DENY:
            _require_text(self.reason_code or "", "reason_code")


@dataclass(frozen=True, slots=True)
class ToolExecutionContext:
    request: ToolExecutionRequest
    workspace_id: str
    resolved_path: str | None = None
    relative_path: str | None = None

    def __post_init__(self) -> None:
        _require_text(self.workspace_id, "workspace_id")
        if self.resolved_path is not None:
            _require_text(self.resolved_path, "resolved_path")
        if self.relative_path is not None:
            _require_text(self.relative_path, "relative_path")


@dataclass(frozen=True, slots=True)
class SanitizedToolError:
    code: str
    message: str

    def __post_init__(self) -> None:
        _require_text(self.code, "code")
        _require_text(self.message, "message")


@dataclass(frozen=True, slots=True)
class ToolExecutionResult:
    request_id: str
    tool_name: str
    status: ToolExecutionStatus
    content: Mapping[str, object] | None = None
    error: SanitizedToolError | None = None
    truncated: bool = False

    def __post_init__(self) -> None:
        _require_text(self.request_id, "request_id")
        _require_text(self.tool_name, "tool_name")
        if self.status in {ToolExecutionStatus.ERROR, ToolExecutionStatus.TIMEOUT}:
            if self.error is None:
                raise InvalidToolCallError("error is required for failed results.")


@dataclass(frozen=True, slots=True)
class ToolAuditEvent:
    request_id: str
    session_id: str
    tool_name: str
    permission: ToolPermission
    decision: PolicyDecisionKind
    status: ToolExecutionStatus
    workspace_id: str
    argument_summary: Mapping[str, object]
    started_at: datetime
    ended_at: datetime
    duration_ms: float
    dry_run: bool = False
    denial_reason: str | None = None
    error_code: str | None = None
    artifact_ids: Sequence[str] = ()

    def __post_init__(self) -> None:
        _require_text(self.request_id, "request_id")
        _require_text(self.session_id, "session_id")
        _require_text(self.tool_name, "tool_name")
        _require_text(self.workspace_id, "workspace_id")
        if self.duration_ms < 0:
            raise InvalidToolCallError("duration_ms cannot be negative.")
        if self.ended_at < self.started_at:
            raise InvalidToolCallError("ended_at cannot be before started_at.")


def _require_text(value: str, name: str) -> None:
    if not value.strip():
        raise InvalidToolCallError(f"{name} must be a non-empty string.")


def _freeze(value: object) -> object:
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _freeze(item) for key, item in value.items()})
    if isinstance(value, list | tuple):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, set):
        return frozenset(_freeze(item) for item in value)
    return value
