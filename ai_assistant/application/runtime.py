"""Framework-agnostic agent runtime loop."""

from dataclasses import dataclass, field
import logging
from time import perf_counter

from ai_assistant.application.context import ContextBuilder
from ai_assistant.application.ports.memory import ConversationMemory
from ai_assistant.application.ports.models import ModelProvider
from ai_assistant.application.tool_calls import ToolCallDetector
from ai_assistant.domain.message import Message
from ai_assistant.domain.session import DEFAULT_SESSION_ID, SessionId, validate_session_id
from ai_assistant.domain.tools import ToolCallPlan


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class AgentRuntime:
    context_builder: ContextBuilder
    memory: ConversationMemory
    model: ModelProvider
    tool_detector: ToolCallDetector
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
            self._persist_turn(user_input, response)
            self.last_tool_plan = self.tool_detector.detect(response)
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

    def _persist_turn(self, user_input: str, response: Message) -> None:
        self.memory.append_many(
            self.session_id,
            [
                Message(role="user", content=user_input),
                response,
            ],
        )
