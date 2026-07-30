"""Conversation session primitives."""

from ai_assistant.domain.errors import InvalidSessionError


SessionId = str
DEFAULT_SESSION_ID: SessionId = "default"


def validate_session_id(session_id: SessionId) -> SessionId:
    if not session_id.strip():
        raise InvalidSessionError("Session ID cannot be empty.")
    return session_id
