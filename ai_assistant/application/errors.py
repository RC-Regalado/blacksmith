"""Compatibility exports for typed internal errors."""

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
    ToolAuditStoreError,
)

__all__ = [
    "AssistantError",
    "ConfigurationError",
    "ConversationStoreError",
    "InvalidMessageError",
    "InvalidSessionError",
    "InvalidToolCallError",
    "ModelConnectionError",
    "ModelNotFoundError",
    "ModelProtocolError",
    "ModelTimeoutError",
    "ToolAuditStoreError",
]
