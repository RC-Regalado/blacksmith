"""Domain objects for the assistant core."""

from ai_assistant.domain.errors import (
    AssistantError,
    ConfigurationError,
    ConversationStoreError,
    InvalidMessageError,
    InvalidSessionError,
    InvalidToolCallError,
    ModelConnectionError,
    ModelNotFoundError,
    ModelProtocolError,
    ModelTimeoutError,
)
from ai_assistant.domain.message import Message, Role
from ai_assistant.domain.session import DEFAULT_SESSION_ID, SessionId, validate_session_id
from ai_assistant.domain.tools import ToolCall, ToolCallPlan, ToolDefinition

__all__ = [
    "AssistantError",
    "ConfigurationError",
    "ConversationStoreError",
    "DEFAULT_SESSION_ID",
    "InvalidMessageError",
    "InvalidSessionError",
    "InvalidToolCallError",
    "Message",
    "ModelConnectionError",
    "ModelNotFoundError",
    "ModelProtocolError",
    "ModelTimeoutError",
    "Role",
    "SessionId",
    "ToolCall",
    "ToolCallPlan",
    "ToolDefinition",
    "validate_session_id",
]
