"""Evaluator port."""

from abc import ABC, abstractmethod

from ai_assistant.platform.domain.execution import ExecutionRecord


class Evaluator(ABC):
    @abstractmethod
    def evaluate(self, execution: ExecutionRecord) -> bool:
        raise NotImplementedError

