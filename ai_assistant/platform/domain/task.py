"""Task domain model."""

from dataclasses import dataclass, replace
from enum import StrEnum
from types import MappingProxyType
from typing import Mapping

from ai_assistant.domain.errors import InvalidToolCallError


class CapabilityName(StrEnum):
    INSPECT_DIRECTORY = "InspectDirectory"
    READ_FILE = "ReadFile"
    INSPECT_FILE_METADATA = "InspectFileMetadata"
    SEARCH_TEXT = "SearchText"
    INSPECT_GIT_STATUS = "InspectGitStatus"
    INSPECT_GIT_DIFF = "InspectGitDiff"
    RUN_TESTS = "RunTests"
    BUILD_PROJECT = "BuildProject"


class PlatformTaskStatus(StrEnum):
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


_TERMINAL_TASK_STATUSES = frozenset(
    {
        PlatformTaskStatus.SUCCEEDED,
        PlatformTaskStatus.FAILED,
        PlatformTaskStatus.SKIPPED,
        PlatformTaskStatus.BLOCKED,
        PlatformTaskStatus.CANCELLED,
    }
)

_TASK_TRANSITIONS = {
    PlatformTaskStatus.PENDING: frozenset(
        {PlatformTaskStatus.READY, PlatformTaskStatus.SKIPPED, PlatformTaskStatus.CANCELLED}
    ),
    PlatformTaskStatus.READY: frozenset(
        {PlatformTaskStatus.RUNNING, PlatformTaskStatus.SKIPPED, PlatformTaskStatus.CANCELLED}
    ),
    PlatformTaskStatus.RUNNING: frozenset(
        {PlatformTaskStatus.SUCCEEDED, PlatformTaskStatus.FAILED, PlatformTaskStatus.BLOCKED}
    ),
    **{status: frozenset() for status in _TERMINAL_TASK_STATUSES},
}


@dataclass(frozen=True, slots=True)
class PlatformTask:
    task_id: str
    objective_id: str
    description: str
    capability: CapabilityName
    arguments: Mapping[str, object] = MappingProxyType({})
    dependencies: tuple[str, ...] = ()
    status: PlatformTaskStatus = PlatformTaskStatus.PENDING

    def __post_init__(self) -> None:
        _require_text(self.task_id, "task_id")
        _require_text(self.objective_id, "objective_id")
        _require_text(self.description, "description")
        if not isinstance(self.capability, CapabilityName):
            try:
                object.__setattr__(self, "capability", CapabilityName(self.capability))
            except ValueError as exc:
                raise InvalidToolCallError("unknown task capability.") from exc
        if not isinstance(self.dependencies, tuple):
            object.__setattr__(self, "dependencies", tuple(self.dependencies))
        if self.task_id in self.dependencies:
            raise InvalidToolCallError("task cannot depend on itself.")
        object.__setattr__(self, "arguments", MappingProxyType(dict(self.arguments)))

    def transition(self, status: PlatformTaskStatus) -> "PlatformTask":
        if status == self.status:
            return self
        if status not in _TASK_TRANSITIONS[self.status]:
            raise InvalidToolCallError(
                f"invalid task transition {self.status.value}->{status.value}"
            )
        return replace(self, status=status)


def _require_text(value: str, name: str) -> None:
    if not isinstance(value, str) or not value:
        raise InvalidToolCallError(f"{name} must be a non-empty string.")
