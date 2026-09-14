"""Execution budget enforcement."""

from dataclasses import replace
from enum import StrEnum

from ai_assistant.domain.errors import InvalidToolCallError
from ai_assistant.platform.domain.budget import BudgetUsage, ExecutionBudget


class BudgetExceededCode(StrEnum):
    TASK_LIMIT_EXCEEDED = "task_limit_exceeded"
    MODEL_CALL_LIMIT_EXCEEDED = "model_call_limit_exceeded"
    TOOL_CALL_LIMIT_EXCEEDED = "tool_call_limit_exceeded"
    DURATION_LIMIT_EXCEEDED = "duration_limit_exceeded"
    OUTPUT_LIMIT_EXCEEDED = "output_limit_exceeded"
    WRITE_LIMIT_EXCEEDED = "write_limit_exceeded"
    REPLAN_LIMIT_EXCEEDED = "replan_limit_exceeded"


class BudgetExceededError(InvalidToolCallError):
    def __init__(self, code: BudgetExceededCode) -> None:
        self.code = code
        super().__init__(code.value)


class BudgetManager:
    def record_task(self, budget: ExecutionBudget, usage: BudgetUsage) -> BudgetUsage:
        return self._checked(budget, replace(usage, tasks=usage.tasks + 1))

    def record_model_call(self, budget: ExecutionBudget, usage: BudgetUsage) -> BudgetUsage:
        return self._checked(budget, replace(usage, model_calls=usage.model_calls + 1))

    def record_tool_call(self, budget: ExecutionBudget, usage: BudgetUsage) -> BudgetUsage:
        return self._checked(budget, replace(usage, tool_calls=usage.tool_calls + 1))

    def record_duration(
        self,
        budget: ExecutionBudget,
        usage: BudgetUsage,
        seconds: float,
    ) -> BudgetUsage:
        return self._checked(
            budget,
            replace(usage, duration_seconds=usage.duration_seconds + seconds),
        )

    def record_output(
        self,
        budget: ExecutionBudget,
        usage: BudgetUsage,
        bytes_count: int,
    ) -> BudgetUsage:
        return self._checked(budget, replace(usage, output_bytes=usage.output_bytes + bytes_count))

    def record_write(self, budget: ExecutionBudget, usage: BudgetUsage) -> BudgetUsage:
        return self._checked(budget, replace(usage, writes=usage.writes + 1))

    def record_replan(self, budget: ExecutionBudget, usage: BudgetUsage) -> BudgetUsage:
        return self._checked(budget, replace(usage, replans=usage.replans + 1))

    def _checked(self, budget: ExecutionBudget, usage: BudgetUsage) -> BudgetUsage:
        if usage.tasks > budget.max_tasks:
            raise BudgetExceededError(BudgetExceededCode.TASK_LIMIT_EXCEEDED)
        if usage.model_calls > budget.max_model_calls:
            raise BudgetExceededError(BudgetExceededCode.MODEL_CALL_LIMIT_EXCEEDED)
        if usage.tool_calls > budget.max_tool_calls:
            raise BudgetExceededError(BudgetExceededCode.TOOL_CALL_LIMIT_EXCEEDED)
        if usage.duration_seconds > budget.max_duration_seconds:
            raise BudgetExceededError(BudgetExceededCode.DURATION_LIMIT_EXCEEDED)
        if usage.output_bytes > budget.max_output_bytes:
            raise BudgetExceededError(BudgetExceededCode.OUTPUT_LIMIT_EXCEEDED)
        if usage.writes > budget.max_writes:
            raise BudgetExceededError(BudgetExceededCode.WRITE_LIMIT_EXCEEDED)
        if usage.replans > budget.max_replans:
            raise BudgetExceededError(BudgetExceededCode.REPLAN_LIMIT_EXCEEDED)
        return usage
