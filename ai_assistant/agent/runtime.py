"""Framework-agnostic agent runtime loop."""

from dataclasses import dataclass

from ai_assistant.agent.context import ContextBuilder
from ai_assistant.agent.memory import (
    DEFAULT_SESSION_ID,
    ConversationMemory,
    SessionId,
    validate_session_id,
)
from ai_assistant.agent.message import Message
from ai_assistant.agent.models.provider import ModelProvider
from ai_assistant.agent.planner import ToolCallDetector


@dataclass(slots=True)
class AgentRuntime:
    context_builder: ContextBuilder
    memory: ConversationMemory
    model: ModelProvider
    tool_detector: ToolCallDetector
    session_id: SessionId = DEFAULT_SESSION_ID

    def __post_init__(self) -> None:
        self.session_id = validate_session_id(self.session_id)

    def respond(self, user_input: str) -> Message:
        context = self.context_builder.build(
            self.memory.history(self.session_id),
            user_input,
        )
        response = self.model.chat(context)
        self._persist_turn(user_input, response)
        self.tool_detector.detect(response)
        return response

    def _persist_turn(self, user_input: str, response: Message) -> None:
        self.memory.append(
            self.session_id,
            Message(role="user", content=user_input),
        )
        self.memory.append(self.session_id, response)
