"""Dummy model provider for local testing."""

from ai_assistant.application.ports.models import ModelProvider
from ai_assistant.agent.message import Message


class DummyModel(ModelProvider):
    def chat(self, messages: list[Message]) -> Message:
        last_user = next(
            (message for message in reversed(messages) if message.role == "user"),
            None,
        )
        if last_user is None:
            raise ValueError("DummyModel requires at least one user message.")

        return Message(role="assistant", content=f"Echo: {last_user.content}")
