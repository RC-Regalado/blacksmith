"""Framework-agnostic agent runtime loop."""

from dataclasses import dataclass, field
import json
import logging
from time import perf_counter

from ai_assistant.application.context import ContextBuilder
from ai_assistant.application.conversation_context import ConversationContextService
from ai_assistant.application.ports.memory import ConversationMemory
from ai_assistant.application.ports.models import ModelProvider
from ai_assistant.application.ports.tools import ToolCatalog, ToolDiagnosticLogger
from ai_assistant.application.tool_diagnostics import ToolLoopDiagnostics
from ai_assistant.application.tool_coordinator import ToolExecutionCoordinator
from ai_assistant.application.tool_calls import ToolCallDetector
from ai_assistant.domain.message import Message
from ai_assistant.domain.session import DEFAULT_SESSION_ID, SessionId, validate_session_id
from ai_assistant.domain.tools import (
    ToolCallPlan,
    ToolExecutionRequest,
    ToolExecutionResult,
    ToolPermission,
)
from ai_assistant.knowledge.metrics import ContextMetrics


logger = logging.getLogger(__name__)


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
    model_provider_name: str = "unknown"
    model_name: str = "unknown"
    tool_timeout_seconds: float = 5.0
    include_knowledge_context: bool = False
    session_id: SessionId = DEFAULT_SESSION_ID
    last_tool_plan: ToolCallPlan = field(
        default_factory=lambda: ToolCallPlan(has_tool_call=False),
        init=False,
    )
    last_context_diagnostic: str | None = field(default=None, init=False)
    last_context_metrics: ContextMetrics | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        self.session_id = validate_session_id(self.session_id)

    def respond(self, user_input: str) -> Message:
        started = perf_counter()
        logger.info("agent turn started session_id=%s", self.session_id)
        context_service = self.conversation_context or ConversationContextService(self.context_builder)
        context = context_service.build_with_retrieval(
            self.memory.history(self.session_id),
            user_input,
            include_knowledge=self.include_knowledge_context,
        )
        self.last_context_diagnostic = context_service.last_diagnostic
        self.last_context_metrics = context_service.last_metrics
        try:
            direct_plan = self.tool_detector.detect(
                Message(role="assistant", content=user_input)
            )
            if direct_plan.has_tool_call and self.tool_coordinator:
                self.last_tool_plan = direct_plan
                request = self._tool_request()
                diagnostics = self._diagnostics()
                diagnostics.requested(request, round_index=1, tool_call_count=1)
                tool_started = perf_counter()
                result = self.tool_coordinator.execute(request)
                diagnostics.completed(
                    request,
                    result,
                    round_index=1,
                    tool_call_count=1,
                    duration_ms=(perf_counter() - tool_started) * 1000,
                )
                response = Message(
                    role="assistant",
                    content=_tool_result_content(result),
                )
                self._persist_turn(user_input, response)
                return response
            response = self.model.chat(context)
            self.last_tool_plan = self.tool_detector.detect(response)
            if self.last_tool_plan.has_tool_call and self.tool_coordinator:
                response = self._respond_with_tool_round(user_input, context, response)
            else:
                self._persist_turn(user_input, response)
        except Exception:
            duration_ms = (perf_counter() - started) * 1000
            logger.error(
                "agent turn failed session_id=%s duration_ms=%.2f",
                self.session_id,
                duration_ms,
            )
            raise
        duration_ms = (perf_counter() - started) * 1000
        logger.info(
            "agent turn completed session_id=%s duration_ms=%.2f",
            self.session_id,
            duration_ms,
        )
        return response

    def _respond_with_tool_round(
        self,
        user_input: str,
        context: list[Message],
        tool_request_message: Message,
    ) -> Message:
        request = self._tool_request()
        diagnostics = self._diagnostics()
        diagnostics.requested(request, round_index=1, tool_call_count=1)
        tool_started = perf_counter()
        tool_result = self.tool_coordinator.execute(request)
        diagnostics.completed(
            request,
            tool_result,
            round_index=1,
            tool_call_count=1,
            duration_ms=(perf_counter() - tool_started) * 1000,
        )
        tool_message = Message(
            role="tool",
            content=_tool_result_content(tool_result),
            tool_name=tool_result.tool_name,
            tool_call_id=self.last_tool_plan.tool_call.tool_call_id,
        )
        response = self.model.chat([*context, tool_request_message, tool_message])
        final_plan = self.tool_detector.detect(response)
        if final_plan.has_tool_call:
            self.last_tool_plan = final_plan
            rejected_request = self._tool_request()
            diagnostics.requested(
                rejected_request,
                round_index=2,
                tool_call_count=2,
            )
            diagnostics.rejected(
                rejected_request,
                round_index=2,
                tool_call_count=2,
                code="tool_round_limit_reached",
                message="Tool round limit reached.",
            )
            response = Message(
                role="assistant",
                content="Tool round limit reached; no additional tool was executed.",
            )
        self.last_tool_plan = final_plan
        self.memory.append_many(
            self.session_id,
            [
                Message(role="user", content=user_input),
                tool_request_message,
                tool_message,
                response,
            ],
        )
        return response

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


def _tool_result_content(result: ToolExecutionResult) -> str:
    payload: dict[str, object] = {
        "status": result.status.value,
        "content": dict(result.content or {}),
        "truncated": result.truncated,
    }
    if result.error:
        payload["error"] = {"code": result.error.code, "message": result.error.message}
    return json.dumps(payload, sort_keys=True)
