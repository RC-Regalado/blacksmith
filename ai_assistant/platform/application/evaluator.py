"""Objective evaluator."""

from collections.abc import Mapping

from ai_assistant.platform.domain.evaluation import EvaluationResult, EvaluationStatus
from ai_assistant.platform.domain.execution import ExecutionResult, ExecutionStatus
from ai_assistant.platform.domain.objective import Objective
from ai_assistant.platform.domain.task import PlatformTaskStatus
from ai_assistant.platform.ports.evaluator import Evaluator


class ObjectiveEvaluator(Evaluator):
    def evaluate(
        self,
        objective: Objective,
        execution_result: ExecutionResult,
        task_states: Mapping[str, PlatformTaskStatus] | None = None,
    ) -> EvaluationResult:
        evidence = tuple(execution_result.evidence)
        failed_tasks = tuple(
            task_id
            for task_id, status in (task_states or {}).items()
            if status != PlatformTaskStatus.SUCCEEDED
        )
        if failed_tasks:
            return EvaluationResult(
                objective.objective_id,
                EvaluationStatus.FAILED,
                evidence,
                f"tasks not succeeded: {', '.join(failed_tasks)}",
            )
        missing = tuple(
            criterion
            for criterion in objective.success_criteria
            if not any(criterion in item for item in evidence)
        )
        if execution_result.status != ExecutionStatus.COMPLETED:
            return EvaluationResult(
                objective.objective_id,
                EvaluationStatus.FAILED,
                evidence,
                "execution failed",
            )
        if missing:
            return EvaluationResult(
                objective.objective_id,
                EvaluationStatus.FAILED,
                evidence,
                f"missing evidence: {', '.join(missing)}",
            )
        return EvaluationResult(
            objective.objective_id,
            EvaluationStatus.PASSED,
            evidence or ("no criteria required",),
            "objective evidence satisfied",
        )


class DeterministicEvaluator(ObjectiveEvaluator):
    """Backward-compatible deterministic evaluator name."""
