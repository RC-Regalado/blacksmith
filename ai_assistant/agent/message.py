"""Compatibility exports for domain messages."""

from ai_assistant.domain.message import Message, Role
from ai_assistant.domain.model_response import FinishReason, ModelResponse

__all__ = ["FinishReason", "Message", "ModelResponse", "Role"]
