"""Execution store port."""

from abc import ABC, abstractmethod

from ai_assistant.platform.domain.execution import ExecutionRecord


class ExecutionStore(ABC):
    @abstractmethod
    def save(self, execution: ExecutionRecord) -> None:
        raise NotImplementedError

