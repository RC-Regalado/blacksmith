"""Optional real Ollama smoke test."""

import os

import pytest

from ai_assistant.agent.message import Message
from ai_assistant.agent.models.ollama import OllamaModelProvider


pytestmark = pytest.mark.ollama


def test_real_ollama_chat() -> None:
    model = os.getenv("AI_ASSISTANT_MODEL")
    if not model:
        pytest.skip("Set AI_ASSISTANT_MODEL to run real Ollama smoke test.")

    provider = OllamaModelProvider(
        model=model,
        base_url=os.getenv("AI_ASSISTANT_BASE_URL", "http://localhost:11434"),
        timeout_seconds=float(os.getenv("AI_ASSISTANT_REQUEST_TIMEOUT", "60")),
    )

    response = provider.chat([Message(role="user", content="Reply with ok.")])

    assert response.role == "assistant"
    assert response.content
