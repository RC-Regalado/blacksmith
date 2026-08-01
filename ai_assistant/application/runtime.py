"""Framework-agnostic agent runtime loop."""

from dataclasses import dataclass, field
import json
import logging
from time import perf_counter

from ai_assistant.application.context import ContextBuilder
from ai_assistant.application.ports.memory import ConversationMemory
from ai_assistant.application.ports.models import ModelProvider
from ai_assistant.application.tool_coordinator import ToolExecutionCoordinator
from ai_assistant.application.tool_calls import ToolCallDetector
from ai_assistant.domain.message import Message
from ai_assistant.domain.session import DEFAULT_SESSION_ID, SessionId, validate_session_id
from ai_assistant.domain.tools import (
    ToolCallPlan,
    ToolExecutionRequest,
    ToolExecutionResult,
)


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class AgentRuntime:
    context_builder: ContextBuilder
    memory: ConversationMemory
    model: ModelProvider
    tool_detector: ToolCallDetector
    tool_coordinator: ToolExecutionCoordinator | None = None
    tool_timeout_seconds: float = 5.0
    session_id: SessionId = DEFAULT_SESSION_ID
    last_tool_plan: ToolCallPlan = field(
        default_factory=lambda: ToolCallPlan(has_tool_call=False),
        init=False,
    )

    def __post_init__(self) -> None:
        self.session_id = validate_session_id(self.session_id)

    def respond(self, user_input: str) -> Message:
        started = perf_counter()
        logger.info("agent turn started session_id=%s", self.session_id)
        context = self.context_builder.build(
            self.memory.history(self.session_id),
            user_input,
        )
        try:
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
        tool_result = self.tool_coordinator.execute(self._tool_request())
        tool_message = Message(
            role="tool",
            content=_tool_result_content(tool_result),
            tool_name=tool_result.tool_name,
            tool_call_id=self.last_tool_plan.tool_call.tool_call_id,
        )
        response = self.model.chat([*context, tool_request_message, tool_message])
        final_plan = self.tool_detector.detect(response)
        if final_plan.has_tool_call:
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


def _tool_result_content(result: ToolExecutionResult) -> str:
    payload: dict[str, object] = {
        "status": result.status.value,
        "content": dict(result.content or {}),
        "truncated": result.truncated,
    }
    if result.error:
        payload["error"] = {"code": result.error.code, "message": result.error.message}
    return json.dumps(payload, sort_keys=True)
