"""Typed internal errors."""


class AssistantError(Exception):
    """Base class for expected assistant errors."""


class ConfigurationError(AssistantError):
    """Configuration is invalid or unsupported."""


class ModelConnectionError(AssistantError):
    """Model provider cannot be reached."""


class ModelNotFoundError(AssistantError):
    """Configured model does not exist."""


class ModelTimeoutError(AssistantError):
    """Model provider request timed out."""


class ModelProtocolError(AssistantError):
    """Model provider returned an invalid response."""


class ConversationStoreError(AssistantError):
    """Conversation persistence failed."""


class InvalidMessageError(AssistantError):
    """A message failed validation."""


class InvalidSessionError(AssistantError):
    """A session identifier failed validation."""


class InvalidToolCallError(AssistantError):
    """A declarative tool call failed validation."""
