"""Deterministic sequential task scheduler."""

from dataclasses import replace
import logging

from ai_assistant.domain.errors import InvalidToolCallError
from ai_assistant.platform.application.execution_graph import ExecutionGraph
from ai_assistant.platform.domain.task import PlatformTask, PlatformTaskStatus
from ai_assistant.platform.ports.execution_store import ExecutionStore


logger = logging.getLogger(__name__)


class TaskScheduler:
    def __init__(self, store: ExecutionStore) -> None:
        self._store = store

    def start_next(self, plan_id: str, graph: ExecutionGraph) -> PlatformTask | None:
        states = self._load_states(plan_id, graph)
        self._block_failed_dependents(plan_id, graph, states)
        if any(status == PlatformTaskStatus.RUNNING for status in states.values()):
            raise InvalidToolCallError("scheduler already has a running task.")
        ready = graph.ready_tasks(states)
        if not ready:
            return None
        task = ready[0]
        self._store.update_task_status(plan_id, task.task_id, PlatformTaskStatus.READY)
        _log_transition(plan_id, task.task_id, PlatformTaskStatus.READY)
        self._store.update_task_status(plan_id, task.task_id, PlatformTaskStatus.RUNNING)
        _log_transition(plan_id, task.task_id, PlatformTaskStatus.RUNNING)
        return replace(task, status=PlatformTaskStatus.RUNNING)

    def mark_succeeded(self, plan_id: str, task_id: str) -> None:
        self._store.update_task_status(plan_id, task_id, PlatformTaskStatus.SUCCEEDED)
        _log_transition(plan_id, task_id, PlatformTaskStatus.SUCCEEDED)

    def mark_failed(self, plan_id: str, task_id: str) -> None:
        self._store.update_task_status(plan_id, task_id, PlatformTaskStatus.FAILED)
        _log_transition(plan_id, task_id, PlatformTaskStatus.FAILED)

    def _load_states(
        self,
        plan_id: str,
        graph: ExecutionGraph,
    ) -> dict[str, PlatformTaskStatus]:
        return {
            task.task_id: self._store.load_task_status(plan_id, task.task_id) or task.status
            for task in graph.tasks
        }

    def _block_failed_dependents(
        self,
        plan_id: str,
        graph: ExecutionGraph,
        states: dict[str, PlatformTaskStatus],
    ) -> None:
        for task in graph.blocked_tasks(states):
            self._store.update_task_status(plan_id, task.task_id, PlatformTaskStatus.BLOCKED)
            states[task.task_id] = PlatformTaskStatus.BLOCKED
            _log_transition(plan_id, task.task_id, PlatformTaskStatus.BLOCKED)


def _log_transition(plan_id: str, task_id: str, status: PlatformTaskStatus) -> None:
    logger.info(
        "task transition plan_id=%s task_id=%s status=%s",
        plan_id,
        task_id,
        status.value,
    )
