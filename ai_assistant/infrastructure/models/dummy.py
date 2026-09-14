"""Dummy model provider for local testing."""

from ai_assistant.application.ports.models import ModelProvider
from ai_assistant.domain.errors import InvalidMessageError
from ai_assistant.domain.message import Message
from ai_assistant.domain.model_response import FinishReason, ModelResponse


class DummyModel(ModelProvider):
    def chat(self, messages: list[Message]) -> ModelResponse:
        last_user = next(
            (message for message in reversed(messages) if message.role == "user"),
            None,
        )
        if last_user is None:
            raise InvalidMessageError("DummyModel requires at least one user message.")

        return ModelResponse(
            message=Message(role="assistant", content=f"Echo: {last_user.content}"),
            finish_reason=FinishReason.STOP,
        )
