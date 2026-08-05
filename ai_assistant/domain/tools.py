"""Declarative tool-call domain models."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
import re
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
    READ_METADATA = "read_metadata"
    READ_CONTENT = "read_content"
    READ_REPOSITORY = "read_repository"
    EXECUTE_PROJECT = "execute_project"
    WRITE_WORKSPACE = "write_workspace"


class WriteMode(StrEnum):
    CREATE = "create"
    REPLACE = "replace"


class AuditRetentionClass(StrEnum):
    METADATA_SEARCH = "metadata_search"
    GIT_INSPECTION = "git_inspection"
    TEST_BUILD = "test_build"
    WRITE = "write"
    SECURITY_DENIAL = "security_denial"
    CRITICAL_ERROR = "critical_error"


_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_PROFILE_ID_RE = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")


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
class ConfirmationGrant:
    session_id: str
    workspace_id: str
    permission: ToolPermission
    granted_at: datetime
    policy_version: str

    def __post_init__(self) -> None:
        _require_text(self.session_id, "session_id")
        _require_text(self.workspace_id, "workspace_id")
        _require_text(self.policy_version, "policy_version")
        if self.permission not in {
            ToolPermission.EXECUTE_PROJECT,
            ToolPermission.WRITE_WORKSPACE,
        }:
            raise InvalidToolCallError("confirmation permission must require consent.")

    @property
    def scope(self) -> tuple[str, str, ToolPermission]:
        return (self.session_id, self.workspace_id, self.permission)


@dataclass(frozen=True, slots=True)
class ToolProfileId:
    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or not _PROFILE_ID_RE.fullmatch(self.value):
            raise InvalidToolCallError("profile_id must be a safe identifier.")


@dataclass(frozen=True, slots=True)
class HashMetadata:
    sha256: str
    size_bytes: int

    def __post_init__(self) -> None:
        if not isinstance(self.sha256, str) or not _SHA256_RE.fullmatch(self.sha256):
            raise InvalidToolCallError("sha256 must be 64 lowercase hex characters.")
        if self.size_bytes < 0:
            raise InvalidToolCallError("size_bytes cannot be negative.")


@dataclass(frozen=True, slots=True)
class WriteRequest:
    path: str
    content: str
    mode: WriteMode
    expected_sha256: str | None = None

    def __post_init__(self) -> None:
        _require_text(self.path, "path")
        if not isinstance(self.content, str):
            raise InvalidToolCallError("content must be text.")
        if self.expected_sha256 is not None and not _SHA256_RE.fullmatch(
            self.expected_sha256
        ):
            raise InvalidToolCallError(
                "expected_sha256 must be 64 lowercase hex characters."
            )


@dataclass(frozen=True, slots=True)
class WriteResult:
    path: str
    mode: WriteMode
    bytes_written: int
    before: HashMetadata | None
    after: HashMetadata

    def __post_init__(self) -> None:
        _require_text(self.path, "path")
        if self.bytes_written < 0:
            raise InvalidToolCallError("bytes_written cannot be negative.")
        if self.mode == WriteMode.REPLACE and self.before is None:
            raise InvalidToolCallError("before hash is required for replace.")


@dataclass(frozen=True, slots=True)
class AuditRetentionRule:
    retention_class: AuditRetentionClass
    days: int

    def __post_init__(self) -> None:
        if self.days <= 0:
            raise InvalidToolCallError("retention days must be positive.")


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
    if not isinstance(value, str) or not value.strip():
        raise InvalidToolCallError(f"{name} must be a non-empty string.")


def _freeze(value: object) -> object:
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _freeze(item) for key, item in value.items()})
    if isinstance(value, list | tuple):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, set):
        return frozenset(_freeze(item) for item in value)
    return value
