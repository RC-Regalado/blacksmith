"""Execution store port."""

from abc import ABC, abstractmethod

from ai_assistant.platform.domain.checkpoint import Checkpoint
from ai_assistant.platform.domain.execution import ExecutionRecord
from ai_assistant.platform.domain.objective import Objective
from ai_assistant.platform.domain.plan import Plan
from ai_assistant.platform.domain.task import PlatformTaskStatus


class ExecutionStore(ABC):
    @abstractmethod
    def save_objective(self, objective: Objective) -> None:
        raise NotImplementedError

    @abstractmethod
    def load_objective(self, objective_id: str) -> Objective | None:
        raise NotImplementedError

    @abstractmethod
    def save_plan(self, plan: Plan) -> None:
        raise NotImplementedError

    @abstractmethod
    def load_plan(self, plan_id: str) -> Plan | None:
        raise NotImplementedError

    @abstractmethod
    def save_execution(self, execution: ExecutionRecord) -> None:
        raise NotImplementedError

    @abstractmethod
    def load_execution(self, execution_id: str) -> ExecutionRecord | None:
        raise NotImplementedError

    @abstractmethod
    def update_task_status(
        self,
        plan_id: str,
        task_id: str,
        status: PlatformTaskStatus,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def load_task_status(
        self,
        plan_id: str,
        task_id: str,
    ) -> PlatformTaskStatus | None:
        raise NotImplementedError

    @abstractmethod
    def save_checkpoint(self, checkpoint: Checkpoint) -> None:
        raise NotImplementedError

    @abstractmethod
    def checkpoints_for_execution(self, execution_id: str) -> tuple[Checkpoint, ...]:
        raise NotImplementedError
