"""Evaluator port."""

from abc import ABC, abstractmethod
from collections.abc import Mapping

from ai_assistant.platform.domain.evaluation import EvaluationResult
from ai_assistant.platform.domain.execution import ExecutionResult
from ai_assistant.platform.domain.objective import Objective
from ai_assistant.platform.domain.task import PlatformTaskStatus


class Evaluator(ABC):
    @abstractmethod
    def evaluate(
        self,
        objective: Objective,
        execution_result: ExecutionResult,
        task_states: Mapping[str, PlatformTaskStatus] | None = None,
    ) -> EvaluationResult:
        raise NotImplementedError
