"""Framework-agnostic agent runtime loop."""

from dataclasses import dataclass

from ai_assistant.agent.context import ContextBuilder
from ai_assistant.agent.memory import ConversationMemory
from ai_assistant.agent.message import Message
from ai_assistant.agent.models.provider import ModelProvider
from ai_assistant.agent.planner import ToolCallDetector


@dataclass(slots=True)
class AgentRuntime:
    context_builder: ContextBuilder
    memory: ConversationMemory
    model: ModelProvider
    tool_detector: ToolCallDetector

    def respond(self, user_input: str) -> Message:
        context = self.context_builder.build(self.memory.history(), user_input)
        response = self.model.chat(context)
        self._persist_turn(user_input, response)
        self.tool_detector.detect(response)
        return response

    def _persist_turn(self, user_input: str, response: Message) -> None:
        self.memory.append(Message(role="user", content=user_input))
        self.memory.append(response)

