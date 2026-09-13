"""Framework-agnostic agent runtime loop."""

from dataclasses import dataclass, field
import json
import logging
from time import perf_counter
from uuid import uuid4

from ai_assistant.application.context import ContextBuilder
from ai_assistant.application.conversation_budget import estimate_tokens
from ai_assistant.application.conversation_context import ConversationContextService
from ai_assistant.application.errors import ConfigurationError
from ai_assistant.application.interaction_metrics import InteractionMetrics
from ai_assistant.application.ports.memory import ConversationMemory
from ai_assistant.application.ports.models import ModelProvider
from ai_assistant.application.ports.tools import InteractionDiagnosticLogger, ToolCatalog, ToolDiagnosticLogger
from ai_assistant.application.tool_diagnostics import InteractionDiagnostics, ToolLoopDiagnostics
from ai_assistant.application.tool_coordinator import ToolExecutionCoordinator
from ai_assistant.application.tool_calls import ToolCallDetector
from ai_assistant.application.tool_loop import (
    DuplicateCallGuard,
    ProgressGuard,
    ToolCallAttempt,
    ToolLoopBudget,
    fingerprint,
)
from ai_assistant.domain.message import Message, MessageProvenance
from ai_assistant.domain.model_response import FinishReason, ModelResponse
from ai_assistant.domain.session import DEFAULT_SESSION_ID, SessionId, validate_session_id
from ai_assistant.domain.tools import (
    InteractionStage,
    SanitizedToolError,
    ToolCallPlan,
    ToolExecutionRequest,
    ToolExecutionResult,
    ToolExecutionStatus,
    ToolPermission,
)
from ai_assistant.knowledge.metrics import ContextMetrics


logger = logging.getLogger(__name__)

_REASON_BUDGET_EXHAUSTED = "tool_loop_budget_exhausted"
_REASON_NO_PROGRESS = "no_progress"
_REASON_MESSAGES = {
    _REASON_BUDGET_EXHAUSTED: "the tool loop budget for this turn was exhausted",
    _REASON_NO_PROGRESS: "repeated tool attempts made no further progress",
}


@dataclass(slots=True)
class AgentRuntime:
    context_builder: ContextBuilder
    memory: ConversationMemory
    model: ModelProvider
    tool_detector: ToolCallDetector
    conversation_context: ConversationContextService | None = None
    tool_catalog: ToolCatalog | None = None
    tool_coordinator: ToolExecutionCoordinator | None = None
    tool_diagnostics: ToolDiagnosticLogger | None = None
    interaction_diagnostics: InteractionDiagnosticLogger | None = None
    tool_loop_budget: ToolLoopBudget = field(default_factory=ToolLoopBudget)
    model_provider_name: str = "unknown"
    model_name: str = "unknown"
    tool_timeout_seconds: float = 5.0
    include_knowledge_context: bool = False
    model_context_window: int | None = None
    model_max_output_tokens: int | None = None
    session_id: SessionId = DEFAULT_SESSION_ID
    last_tool_plan: ToolCallPlan = field(
        default_factory=lambda: ToolCallPlan(has_tool_call=False),
        init=False,
    )
    last_context_diagnostic: str | None = field(default=None, init=False)
    last_context_metrics: ContextMetrics | None = field(default=None, init=False)
    last_interaction_id: str | None = field(default=None, init=False)
    last_interaction_metrics: InteractionMetrics | None = field(default=None, init=False)
    _model_calls_used: int = field(default=0, init=False)
    _last_model_response: ModelResponse | None = field(default=None, init=False)
    _tool_rounds_used: int = field(default=0, init=False)
    _executor_operations_used_total: int = field(default=0, init=False)
    _recovery_operations_used_total: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        self.session_id = validate_session_id(self.session_id)
        self._validate_provider_budget()

    def _validate_provider_budget(self) -> None:
        if self.conversation_context is None:
            return
        budget = getattr(self.conversation_context, "budget", None)
        if budget is None:
            return
        if (
            self.model_context_window is not None
            and self.model_context_window != budget.provider_context_window
        ):
            raise ConfigurationError("model_context_window must match provider_context_window.")
        if (
            self.model_max_output_tokens is not None
            and self.model_max_output_tokens != budget.reserved_output_tokens
        ):
            raise ConfigurationError("model_max_output_tokens must match reserved_output_tokens.")

    def respond(self, user_input: str) -> Message:
        started = perf_counter()
        self.last_interaction_id = uuid4().hex
        self._reset_turn_accumulators()
        logger.info(
            "agent turn started session_id=%s interaction_id=%s",
            self.session_id,
            self.last_interaction_id,
        )
        context_service = self.conversation_context or ConversationContextService(self.context_builder)
        context = context_service.build_with_retrieval(
            self.memory.history(self.session_id),
            user_input,
            include_knowledge=self.include_knowledge_context,
        )
        self.last_context_diagnostic = context_service.last_diagnostic
        self.last_context_metrics = context_service.last_metrics
        self._record_context_retrieval()
        outcome = "error"
        try:
            model_response = self._call_model(context, round_index=1)
            self.last_tool_plan = self.tool_detector.detect(model_response.message)
            if self.last_tool_plan.has_tool_call and self.tool_coordinator:
                response = self._run_tool_loop(user_input, context, model_response.message)
                outcome = "tool_loop"
            else:
                response = model_response.message
                self._persist_turn(user_input, response)
                outcome = "direct_answer"
        except Exception:
            duration_ms = (perf_counter() - started) * 1000
            logger.error(
                "agent turn failed session_id=%s interaction_id=%s duration_ms=%.2f",
                self.session_id,
                self.last_interaction_id,
                duration_ms,
            )
            self._complete_interaction("error", duration_ms)
            raise
        duration_ms = (perf_counter() - started) * 1000
        logger.info(
            "agent turn completed session_id=%s interaction_id=%s duration_ms=%.2f",
            self.session_id,
            self.last_interaction_id,
            duration_ms,
        )
        self._complete_interaction(outcome, duration_ms)
        return response

    def _run_tool_loop(
        self,
        user_input: str,
        context: list[Message],
        tool_request_message: Message,
    ) -> Message:
        """Drive a bounded, guarded multi-round tool loop (ADR-069).

        Every threshold comes from `self.tool_loop_budget`; no round/request
        limit is hardcoded here. `DuplicateCallGuard`/`ProgressGuard` decide
        whether a proposed call is worth spending budget on, deterministically,
        from the turn's own recorded history alone. Path recovery inside
        `ToolExecutionCoordinator.execute()` never counts as an extra round.
        """
        diagnostics = self._diagnostics()
        duplicate_guard = DuplicateCallGuard()
        progress_guard = ProgressGuard()
        conversation = list(context)
        persisted: list[Message] = [
            Message(
                role="user",
                content=user_input,
                provenance=MessageProvenance.OPERATOR_INPUT,
            )
        ]
        history: list[ToolCallAttempt] = []
        executor_operations_used = 0
        round_index = 1

        while True:
            tool_call = self.last_tool_plan.tool_call
            candidate_fp = fingerprint(tool_call.name, tool_call.arguments)
            persisted.append(tool_request_message)

            if (
                round_index > self.tool_loop_budget.max_model_tool_rounds
                or len(history) >= self.tool_loop_budget.max_tool_requests
                or executor_operations_used >= self.tool_loop_budget.max_executor_operations
            ):
                return self._finish_with_synthesis(
                    conversation, persisted, history, _REASON_BUDGET_EXHAUSTED
                )
            if progress_guard.is_stalled(history):
                return self._finish_with_synthesis(
                    conversation, persisted, history, _REASON_NO_PROGRESS
                )

            request = self._tool_request()
            diagnostics.requested(request, round_index=round_index, tool_call_count=round_index)
            self._tool_rounds_used += 1
            if duplicate_guard.is_duplicate(history, candidate_fp):
                tool_result = _duplicate_rejection(request)
                diagnostics.rejected(
                    request,
                    round_index=round_index,
                    tool_call_count=round_index,
                    code="duplicate_tool_call",
                    message="Duplicate tool call rejected; no new evidence would result.",
                )
            else:
                tool_started = perf_counter()
                tool_result = self.tool_coordinator.execute(request)
                diagnostics.completed(
                    request,
                    tool_result,
                    round_index=round_index,
                    tool_call_count=round_index,
                    duration_ms=(perf_counter() - tool_started) * 1000,
                )

            self._record_tool_spend(tool_result)
            executor_operations_used += tool_result.executor_operations
            history.append(ToolCallAttempt(candidate_fp, tool_call.name, tool_result.status))
            tool_message = Message(
                role="tool",
                content=_tool_result_content(tool_result),
                tool_name=tool_result.tool_name,
                tool_call_id=tool_call.tool_call_id,
                provenance=MessageProvenance.TOOL_RESULT,
            )
            persisted.append(tool_message)
            conversation = [*conversation, tool_request_message, tool_message]

            model_response = self._call_model(conversation, round_index=round_index)
            round_index += 1
            self.last_tool_plan = self.tool_detector.detect(model_response.message)
            if not self.last_tool_plan.has_tool_call:
                persisted.append(model_response.message)
                self.memory.append_many(self.session_id, persisted)
                return model_response.message
            tool_request_message = model_response.message

    def _finish_with_synthesis(
        self,
        conversation: list[Message],
        persisted: list[Message],
        history: list[ToolCallAttempt],
        reason: str,
    ) -> Message:
        """Stop executing tools and produce a real final answer if possible.

        Asks the model once more for a natural-language wrap-up using only
        the evidence already gathered — this extra call executes no tool and
        does not count against the tool-loop budget. If the model still
        insists on a tool call, fall back to a deterministic, sanitized
        summary of what was executed/rejected rather than looping further.
        """
        diagnostics = self._diagnostics()
        round_index = len(history) + 1
        rejected_request = self._tool_request()
        diagnostics.requested(rejected_request, round_index=round_index, tool_call_count=round_index)
        diagnostics.rejected(
            rejected_request,
            round_index=round_index,
            tool_call_count=round_index,
            code=reason,
            message=f"Tool loop stopped: {_REASON_MESSAGES[reason]}.",
        )
        self._tool_rounds_used += 1
        synthesis_prompt = Message(
            role="user",
            provenance=MessageProvenance.RUNTIME_DIAGNOSTIC,
            content=(
                "No more tools are available this turn "
                f"({_REASON_MESSAGES[reason]}). Provide your best final answer to "
                "the user's original question using only the tool results already "
                "shown above. Do not request any tool."
            ),
        )
        synthesis_response = self._call_model(
            [*conversation, synthesis_prompt], round_index=round_index
        )
        final_plan = self.tool_detector.detect(synthesis_response.message)
        if final_plan.has_tool_call:
            response = Message(role="assistant", content=_exhaustion_summary(history, reason))
        else:
            response = synthesis_response.message
        self._interaction_diagnostics().record(
            InteractionStage.FINAL_SYNTHESIS,
            session_id=self.session_id,
            interaction_id=self.last_interaction_id,
            payload={
                "reason": reason,
                "attempts": len(history),
                "fallback_used": final_plan.has_tool_call,
            },
        )
        self.last_tool_plan = ToolCallPlan(has_tool_call=False)
        persisted.append(response)
        self.memory.append_many(self.session_id, persisted)
        return response

    def _call_model(self, messages: list[Message], *, round_index: int) -> ModelResponse:
        bounded_messages, composition = self._bounded_model_messages(messages)
        self._interaction_diagnostics().record(
            InteractionStage.MODEL_REQUEST,
            session_id=self.session_id,
            interaction_id=self.last_interaction_id,
            payload={
                "round_index": round_index,
                "message_count": len(bounded_messages),
                **composition,
            },
        )
        started = perf_counter()
        response = self.model.chat(bounded_messages)
        duration_ms = (perf_counter() - started) * 1000
        self._model_calls_used += 1
        self._last_model_response = response
        termination_cause = _termination_cause(
            response,
            context_window=self.model_context_window,
            output_limit=self.model_max_output_tokens,
        )
        self._interaction_diagnostics().record(
            InteractionStage.MODEL_RESPONSE,
            session_id=self.session_id,
            interaction_id=self.last_interaction_id,
            payload={
                "round_index": round_index,
                "finish_reason": response.finish_reason.value,
                # Named to avoid `redact_sensitive`'s substring-based
                # "token"/"prompt" sensitive-key match: these are estimated
                # token *counts* (ModelResponse.prompt_tokens/.output_tokens),
                # not prompt content or a credential, but the shared
                # sanitizer cannot tell the difference by key name alone.
                "input_length": response.prompt_tokens,
                "output_length": response.output_tokens,
                "truncated": response.truncated,
                "termination_cause": termination_cause,
            },
            duration_ms=duration_ms,
        )
        return response

    def _bounded_model_messages(
        self,
        messages: list[Message],
    ) -> tuple[list[Message], dict[str, int]]:
        budget = self._effective_input_budget()
        required = _required_message_indexes(messages)
        selected = set(required)
        required_cost = sum(estimate_tokens(messages[index].content) for index in selected)
        if required_cost > budget:
            raise ConfigurationError("required model input exceeds effective input budget.")
        remaining = budget - required_cost
        for index in _optional_message_order(messages, selected):
            cost = estimate_tokens(messages[index].content)
            if cost <= remaining:
                selected.add(index)
                remaining -= cost
        bounded = [message for index, message in enumerate(messages) if index in selected]
        composition = _composition_metrics(bounded, budget)
        composition["original_message_count"] = len(messages)
        composition["dropped_message_count"] = len(messages) - len(bounded)
        return bounded, composition

    def _effective_input_budget(self) -> int:
        budget = getattr(self.conversation_context, "budget", None)
        if budget is not None:
            return budget.max_input_tokens
        if self.model_context_window is not None and self.model_max_output_tokens is not None:
            return self.model_context_window - self.model_max_output_tokens
        return self.context_builder.context_limit

    def _tool_request(self) -> ToolExecutionRequest:
        tool_call = self.last_tool_plan.tool_call
        if tool_call is None:
            raise RuntimeError("tool call is required")
        return ToolExecutionRequest(
            request_id=tool_call.tool_call_id or f"{self.session_id}:{tool_call.name}",
            session_id=self.session_id,
            tool_name=tool_call.name,
            arguments=tool_call.arguments,
            permission=(
                self.tool_catalog.definition_for(tool_call.name).permission
                if self.tool_catalog
                else ToolPermission.READ_ONLY
            ),
            timeout_seconds=self.tool_timeout_seconds,
            interaction_id=self.last_interaction_id,
            origin=MessageProvenance.MODEL_OUTPUT,
        )

    def _persist_turn(self, user_input: str, response: Message) -> None:
        self.memory.append_many(
            self.session_id,
            [
                Message(role="user", content=user_input),
                response,
            ],
        )

    def _diagnostics(self) -> ToolLoopDiagnostics:
        return ToolLoopDiagnostics(
            self.tool_diagnostics,
            self.model_provider_name,
            self.model_name,
        )

    def _interaction_diagnostics(self) -> InteractionDiagnostics:
        return InteractionDiagnostics(
            self.interaction_diagnostics,
            self.model_provider_name,
            self.model_name,
        )

    def _reset_turn_accumulators(self) -> None:
        self._model_calls_used = 0
        self._last_model_response = None
        self._tool_rounds_used = 0
        self._executor_operations_used_total = 0
        self._recovery_operations_used_total = 0
        self.last_interaction_metrics = None

    def _record_context_retrieval(self) -> None:
        metrics = self.last_context_metrics
        payload: dict[str, object] = {
            "include_knowledge": self.include_knowledge_context,
            "retrieval_attempted": metrics is not None,
            "diagnostic": self.last_context_diagnostic,
        }
        if metrics is not None:
            payload["knowledge_candidates"] = metrics.knowledge_candidates
            payload["knowledge_chunks_selected"] = metrics.knowledge_chunks_selected
            payload["context_reduction_ratio"] = metrics.context_reduction_ratio
            payload["lexical_candidates"] = metrics.lexical_candidates
            payload["symbol_candidates"] = metrics.symbol_candidates
            payload["semantic_candidates"] = metrics.semantic_candidates
            payload["merged_candidates"] = metrics.merged_candidates
            payload["selected_candidates"] = metrics.selected_candidates
            payload["unique_sources_selected"] = metrics.unique_sources_selected
        # FINDING-008 (ADR-071): surface the provider-neutral runtime budget
        # as one observable record per turn.
        # Key names deliberately avoid the substring "token" (see the
        # matching comment in `_call_model`): `redact_sensitive` would
        # otherwise blank `reserved_output_tokens`/`max_input_tokens` even
        # though these are budget sizes, not secrets or prompt content.
        budget = getattr(self.conversation_context, "budget", None)
        if budget is not None:
            payload["provider_context_window"] = budget.provider_context_window
            payload["reserved_output_length"] = budget.reserved_output_tokens
            payload["context_safety_margin"] = budget.safety_margin_tokens
            payload["max_input_length"] = budget.max_input_tokens
        payload["model_context_window"] = self.model_context_window
        payload["model_max_output_length"] = self.model_max_output_tokens
        self._interaction_diagnostics().record(
            InteractionStage.CONTEXT_RETRIEVAL,
            session_id=self.session_id,
            interaction_id=self.last_interaction_id,
            payload=payload,
        )

    def _record_tool_spend(self, result: ToolExecutionResult) -> None:
        self._executor_operations_used_total += result.executor_operations
        self._recovery_operations_used_total += max(0, result.executor_operations - 1)

    def _complete_interaction(self, outcome: str, duration_ms: float) -> None:
        response = self._last_model_response
        knowledge_chunks_selected = (
            self.last_context_metrics.knowledge_chunks_selected
            if self.last_context_metrics
            else 0
        )
        metrics = InteractionMetrics(
            interaction_id=self.last_interaction_id or "",
            outcome=outcome,
            model_calls=self._model_calls_used,
            prompt_tokens=response.prompt_tokens if response else None,
            output_tokens=response.output_tokens if response else None,
            finish_reason=response.finish_reason if response else None,
            truncated=response.truncated if response else False,
            tool_rounds=self._tool_rounds_used,
            tool_requests=self._tool_rounds_used,
            executor_operations=self._executor_operations_used_total,
            recovery_operations=self._recovery_operations_used_total,
            retrieval_attempted=self.last_context_metrics is not None,
            knowledge_chunks_selected=knowledge_chunks_selected,
        )
        self.last_interaction_metrics = metrics
        self._interaction_diagnostics().record(
            InteractionStage.INTERACTION_COMPLETED,
            session_id=self.session_id,
            interaction_id=self.last_interaction_id,
            payload={
                "outcome": metrics.outcome,
                "model_calls": metrics.model_calls,
                # See the matching comment in `_call_model`: renamed to dodge
                # `redact_sensitive`'s "token" substring match on a field
                # that holds a count, not a credential or prompt content.
                "input_length": metrics.prompt_tokens,
                "output_length": metrics.output_tokens,
                "finish_reason": metrics.finish_reason.value if metrics.finish_reason else None,
                "truncated": metrics.truncated,
                "tool_rounds": metrics.tool_rounds,
                "tool_requests": metrics.tool_requests,
                "executor_operations": metrics.executor_operations,
                "recovery_operations": metrics.recovery_operations,
                "retrieval_attempted": metrics.retrieval_attempted,
                "knowledge_chunks_selected": metrics.knowledge_chunks_selected,
            },
            duration_ms=duration_ms,
        )


def _tool_result_content(result: ToolExecutionResult) -> str:
    payload: dict[str, object] = {
        "status": result.status.value,
        "content": dict(result.content or {}),
        "truncated": result.truncated,
    }
    if result.error:
        payload["error"] = {"code": result.error.code, "message": result.error.message}
    return json.dumps(payload, sort_keys=True)


def _duplicate_rejection(request: ToolExecutionRequest) -> ToolExecutionResult:
    return ToolExecutionResult(
        request_id=request.request_id,
        tool_name=request.tool_name,
        status=ToolExecutionStatus.DENIED,
        error=SanitizedToolError(
            code="duplicate_tool_call",
            message="Duplicate tool call rejected.",
        ),
        executor_operations=0,
    )


def _required_message_indexes(messages: list[Message]) -> set[int]:
    indexes: set[int] = set()
    if messages:
        indexes.add(0)
    user_indexes = [index for index, message in enumerate(messages) if message.role == "user"]
    if user_indexes:
        indexes.add(user_indexes[-1])
    return indexes


def _optional_message_order(messages: list[Message], selected: set[int]) -> list[int]:
    indexes = [index for index in range(len(messages)) if index not in selected]
    return sorted(indexes, key=lambda index: (_message_priority(messages, index), -index))


def _message_priority(messages: list[Message], index: int) -> int:
    message = messages[index]
    if message.role == "tool":
        return 0
    if _is_knowledge_message(message):
        return 1
    return 2


def _composition_metrics(messages: list[Message], budget: int) -> dict[str, int]:
    latest_user = _latest_user_index(messages)
    return {
        "system_input_length": sum(
            _base_system_tokens(message) for index, message in enumerate(messages) if index == 0
        ),
        "history_input_length": sum(
            estimate_tokens(message.content)
            for index, message in enumerate(messages)
            if index != 0
            and index != latest_user
            and message.role not in {"system", "tool"}
            and not _is_knowledge_message(message)
        ),
        "knowledge_input_length": sum(
            estimate_tokens(message.content)
            for index, message in enumerate(messages)
            if index != 0 and _is_knowledge_message(message)
        ),
        "tool_schema_input_length": sum(
            _tool_instruction_tokens(message) for index, message in enumerate(messages) if index == 0
        ),
        "tool_result_input_length": sum(
            estimate_tokens(message.content) for message in messages if message.role == "tool"
        ),
        "user_input_length": estimate_tokens(messages[latest_user].content)
        if latest_user is not None
        else 0,
        "estimated_final_input_length": sum(estimate_tokens(message.content) for message in messages),
        "effective_input_budget": budget,
    }


def _latest_user_index(messages: list[Message]) -> int | None:
    for index in range(len(messages) - 1, -1, -1):
        if messages[index].role == "user":
            return index
    return None


def _is_knowledge_message(message: Message) -> bool:
    return message.provenance in {
        MessageProvenance.RETRIEVED_KNOWLEDGE,
        MessageProvenance.RUNTIME_DIAGNOSTIC,
    } or message.role == "system" and (
        message.content.startswith("Relevant derived knowledge:")
        or message.content.startswith("Knowledge context requested,")
    )


def _base_system_tokens(message: Message) -> int:
    return estimate_tokens(_split_tool_instructions(message.content)[0])


def _tool_instruction_tokens(message: Message) -> int:
    return estimate_tokens(_split_tool_instructions(message.content)[1])


def _split_tool_instructions(content: str) -> tuple[str, str]:
    marker = "When the user asks to use a local tool"
    index = content.find(marker)
    if index < 0:
        return content, ""
    return content[:index].strip(), content[index:].strip()


def _termination_cause(
    response: ModelResponse,
    *,
    context_window: int | None,
    output_limit: int | None,
) -> str | None:
    if response.finish_reason != FinishReason.LENGTH:
        return None
    if (
        context_window is not None
        and response.prompt_tokens is not None
        and response.output_tokens is not None
        and response.prompt_tokens + response.output_tokens >= context_window
    ):
        return "context_window"
    if output_limit is not None and response.output_tokens is not None and response.output_tokens >= output_limit:
        return "generation_limit"
    return "unknown"


def _exhaustion_summary(history: list[ToolCallAttempt], reason: str) -> str:
    lines = [f"No further tools were executed ({_REASON_MESSAGES[reason]})."]
    if history:
        lines.append("Attempted this turn:")
        lines.extend(f"- {attempt.tool_name}: {attempt.status.value}" for attempt in history)
    return "\n".join(lines)
