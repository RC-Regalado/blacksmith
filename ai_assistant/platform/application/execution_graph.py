"""Immutable execution graph for validated plans."""

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from ai_assistant.domain.errors import InvalidToolCallError
from ai_assistant.platform.domain.plan import Plan
from ai_assistant.platform.domain.task import PlatformTask, PlatformTaskStatus


_FAILED_DEPENDENCY_STATES = frozenset(
    {
        PlatformTaskStatus.FAILED,
        PlatformTaskStatus.BLOCKED,
        PlatformTaskStatus.CANCELLED,
        PlatformTaskStatus.SKIPPED,
    }
)


@dataclass(frozen=True, slots=True)
class ExecutionGraph:
    tasks: tuple[PlatformTask, ...]
    dependencies: Mapping[str, tuple[str, ...]]

    @classmethod
    def from_plan(cls, plan: Plan) -> "ExecutionGraph":
        task_ids = [task.task_id for task in plan.tasks]
        if len(task_ids) != len(set(task_ids)):
            raise InvalidToolCallError("execution graph task IDs must be unique.")
        dependencies = {task.task_id: task.dependencies for task in plan.tasks}
        _reject_missing_dependencies(dependencies)
        _reject_cycles(dependencies)
        return cls(plan.tasks, MappingProxyType(dependencies))

    @property
    def task_ids(self) -> tuple[str, ...]:
        return tuple(task.task_id for task in self.tasks)

    def ready_tasks(
        self,
        states: Mapping[str, PlatformTaskStatus],
    ) -> tuple[PlatformTask, ...]:
        return tuple(
            task
            for task in self.tasks
            if _state(task, states) in {PlatformTaskStatus.PENDING, PlatformTaskStatus.READY}
            and all(states.get(dependency) == PlatformTaskStatus.SUCCEEDED for dependency in task.dependencies)
        )

    def blocked_tasks(
        self,
        states: Mapping[str, PlatformTaskStatus],
    ) -> tuple[PlatformTask, ...]:
        return tuple(
            task
            for task in self.tasks
            if _state(task, states) in {PlatformTaskStatus.PENDING, PlatformTaskStatus.READY}
            and any(states.get(dependency) in _FAILED_DEPENDENCY_STATES for dependency in task.dependencies)
        )


def _state(
    task: PlatformTask,
    states: Mapping[str, PlatformTaskStatus],
) -> PlatformTaskStatus:
    return states.get(task.task_id, task.status)


def _reject_missing_dependencies(dependencies: Mapping[str, tuple[str, ...]]) -> None:
    task_ids = set(dependencies)
    if any(dependency not in task_ids for deps in dependencies.values() for dependency in deps):
        raise InvalidToolCallError("execution graph dependency is missing.")


def _reject_cycles(dependencies: Mapping[str, tuple[str, ...]]) -> None:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str) -> None:
        if task_id in visiting:
            raise InvalidToolCallError("execution graph contains a cycle.")
        if task_id in visited:
            return
        visiting.add(task_id)
        for dependency in dependencies[task_id]:
            visit(dependency)
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in dependencies:
        visit(task_id)
