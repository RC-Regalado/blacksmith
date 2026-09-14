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


class ToolAuditStoreError(AssistantError):
    """Tool audit persistence failed."""


class ExecutionStoreError(AssistantError):
    """Execution persistence failed."""


class KnowledgeStoreError(AssistantError):
    """Knowledge persistence failed."""


class InvalidMessageError(AssistantError):
    """A message failed validation."""


class InvalidSessionError(AssistantError):
    """A session identifier failed validation."""


class InvalidToolCallError(AssistantError):
    """A declarative tool call failed validation."""


class ToolPathError(InvalidToolCallError):
    """A workspace path failed validation with a stable, typed reason.

    Subclasses carry a machine-readable ``code`` so the tool-execution
    platform can decide, internally, which failures are safe to retry
    automatically. Only ``recoverable = True`` subclasses (currently just
    :class:`PathNotFoundError`) may enter the path-recovery mechanism;
    every other subclass represents a security or type decision that must
    never trigger an alternative-path search.
    """

    code: str = "path_denied"
    recoverable: bool = False


class PathNotFoundError(ToolPathError):
    """The requested path does not exist. Eligible for case-only recovery."""

    code = "path_not_found"
    recoverable = True


class AmbiguousPathError(ToolPathError):
    """Case-insensitive recovery matched more than one candidate."""

    code = "ambiguous_path"


class PathOutsideWorkspaceError(ToolPathError):
    """The path escapes the configured workspace (traversal, symlink, absolute)."""

    code = "path_outside_workspace"


class SensitivePathError(ToolPathError):
    """The path is hidden or matches a denied sensitive-file pattern."""

    code = "sensitive_path"


class PathPermissionDeniedError(ToolPathError):
    """The path exists but is not accessible to the process."""

    code = "permission_denied"


class UnsupportedFileTypeError(ToolPathError):
    """The path exists but is not the type the tool expects."""

    code = "unsupported_file_type"


class InvalidKnowledgeError(AssistantError):
    """A knowledge domain object failed validation."""
