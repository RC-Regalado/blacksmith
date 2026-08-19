"""Minimal command line interface."""

import logging
import sys
from collections.abc import Callable, Sequence
from uuid import uuid4

from ai_assistant.application.runtime import AgentRuntime
from ai_assistant.domain.errors import AssistantError
from ai_assistant.platform.application import ExecutionEngine, ExecutionOutcome
from ai_assistant.platform.domain.objective import Objective


logger = logging.getLogger(__name__)


class CliApplication:
    def __init__(
        self,
        runtime: AgentRuntime,
        objective_engine: ExecutionEngine | None = None,
        session_id: str = "default",
        knowledge_cli=None,
        objective_id_factory: Callable[[], str] | None = None,
    ) -> None:
        self._runtime = runtime
        self._objective_engine = objective_engine
        self._session_id = session_id
        self._knowledge_cli = knowledge_cli
        self._objective_id_factory = objective_id_factory or (lambda: uuid4().hex)

    def run(self, argv: Sequence[str] | None = None) -> None:
        args = tuple(() if argv is None else argv)
        if args:
            self._run_command(args)
            return
        while True:
            try:
                user_input = input("> ").strip()
            except EOFError:
                break

            if user_input in {"exit", "quit"}:
                break
            if not user_input:
                continue

            try:
                response = self._runtime.respond(user_input)
                print(response.content)
            except AssistantError as error:
                logger.error("expected assistant error type=%s", type(error).__name__)
                print(f"Error: {error}", file=sys.stderr)

    def _run_command(self, args: tuple[str, ...]) -> None:
        verbose = "--verbose" in args
        metrics = "--metrics" in args
        filtered = tuple(arg for arg in args if arg not in {"--verbose", "--metrics"})
        if filtered[0] == "knowledge":
            if self._knowledge_cli is None:
                print("Error: knowledge CLI is unavailable.", file=sys.stderr)
                return
            self._knowledge_cli.run(filtered[1:])
            return
        if filtered[0] != "objective" or len(filtered) != 2:
            print(
                'Usage: python main.py objective [--verbose] [--metrics] "Describe the objective"',
                file=sys.stderr,
            )
            return
        if self._objective_engine is None:
            print("Error: objective execution requires tools and workspace.", file=sys.stderr)
            return
        try:
            objective = Objective(f"obj-{self._objective_id_factory()}", filtered[1])
            outcome = self._objective_engine.run(objective, self._session_id)
            _print_planner_response(self._objective_engine, verbose)
            _print_outcome(outcome)
            if metrics:
                _print_metrics(outcome, self._objective_engine)
        except AssistantError as error:
            _print_planner_response(self._objective_engine, verbose)
            logger.error("expected assistant error type=%s", type(error).__name__)
            print(f"Error: {error}", file=sys.stderr)


class CliConfirmationPrompter:
    def confirm(self, session_id: str, workspace_id: str, permission: str) -> bool:
        prompt = (
            f"Allow {permission} for session {session_id} "
            f"in workspace {workspace_id}? Type yes to allow: "
        )
        return input(prompt).strip().lower() == "yes"


def _print_outcome(outcome: ExecutionOutcome) -> None:
    print(f"Objective: {outcome.objective.objective_id}")
    print(f"Execution: {outcome.execution.status.value}")
    print(f"Evaluation: {outcome.evaluation.status.value}")
    print(
        "Budget: "
        f"tasks={outcome.usage.tasks} "
        f"model_calls={outcome.usage.model_calls} "
        f"tool_calls={outcome.usage.tool_calls} "
        f"output_bytes={outcome.usage.output_bytes}"
    )
    print("Plan:")
    for task in outcome.plan.tasks:
        print(f"- {task.task_id}: {task.capability.value}")
    print("Evidence:")
    for item in outcome.result.evidence or ("none",):
        print(f"- {item}")
    if outcome.result.observations:
        print("Summary:")
        for item in outcome.result.observations:
            print(f"- {item}")
    if outcome.result.error_code:
        print(f"Error code: {outcome.result.error_code}")


def _print_metrics(outcome: ExecutionOutcome, engine: ExecutionEngine) -> None:
    print("Metrics:")
    print(f"- duration_seconds={outcome.usage.duration_seconds:.4f}")
    _print_context_metrics("planning", engine.last_planning_context_metrics)
    _print_context_metrics("synthesis", engine.last_synthesis_context_metrics)


def _print_context_metrics(label: str, metrics) -> None:
    if metrics is None:
        return
    print(
        f"- context_{label}: "
        f"candidates={metrics.knowledge_candidates} "
        f"ranked={metrics.ranked_candidates} "
        f"selected={metrics.knowledge_chunks_selected} "
        f"raw_tokens={metrics.raw_context_estimated_tokens} "
        f"compiled_tokens={metrics.compiled_context_estimated_tokens} "
        f"reduction_ratio={metrics.context_reduction_ratio:.4f}"
    )


def _print_planner_response(engine: ExecutionEngine, verbose: bool) -> None:
    if not verbose or engine.last_planner_response is None:
        return
    print("Planner model response:", file=sys.stderr)
    print(engine.last_planner_response, file=sys.stderr)
