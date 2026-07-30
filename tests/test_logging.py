"""Tests for safe logging behavior."""

from io import BytesIO
import logging
from urllib.error import HTTPError

import pytest

from ai_assistant.application.errors import ConfigurationError, ModelProtocolError
from ai_assistant.agent.context import ContextBuilder
from ai_assistant.agent.message import Message
from ai_assistant.agent.models.adapter import ModelAdapter, ModelAdapterConfig
from ai_assistant.agent.models.openai_compatible import OpenAICompatibleModel
from ai_assistant.agent.planner import ToolCallDetector
from ai_assistant.agent.runtime import AgentRuntime
from ai_assistant.application.ports.memory import ConversationMemory, SessionId
from ai_assistant.application.ports.models import ModelProvider
from ai_assistant.bootstrap.logging import configure_logging


pytestmark = pytest.mark.unit


def test_configure_logging_sets_root_level() -> None:
    configure_logging("DEBUG")

    assert logging.getLogger().level == logging.DEBUG


def test_configure_logging_rejects_unknown_level() -> None:
    with pytest.raises(ConfigurationError, match="AI_ASSISTANT_LOG_LEVEL"):
        configure_logging("LOUD")


def test_model_adapter_logs_provider_and_model_without_api_key(
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.INFO)

    ModelAdapter.from_config(
        ModelAdapterConfig(provider="dummy", model="test-model", api_key="secret-key")
    )

    assert "provider=dummy" in caplog.text
    assert "model=test-model" in caplog.text
    assert "secret-key" not in caplog.text


def test_runtime_logs_without_message_content(
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.INFO)
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="system secret"),
        memory=FakeConversationStore(),
        model=FakeModel("assistant secret"),
        tool_detector=ToolCallDetector(),
        session_id="alpha",
    )

    runtime.respond("user secret")

    assert "agent turn completed" in caplog.text
    assert "duration_ms=" in caplog.text
    assert "user secret" not in caplog.text
    assert "assistant secret" not in caplog.text
    assert "system secret" not in caplog.text


def test_openai_error_log_omits_response_body_and_api_key(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    def fail_request(*_args: object, **_kwargs: object) -> None:
        raise HTTPError(
            url="http://example.test/responses",
            code=500,
            msg="server error",
            hdrs=None,
            fp=BytesIO(b"body secret"),
        )

    caplog.set_level(logging.ERROR)
    monkeypatch.setattr(
        "ai_assistant.agent.models.openai_compatible.urlopen",
        fail_request,
    )
    model = OpenAICompatibleModel(
        model="test-model",
        api_key="api-secret",
        base_url="http://example.test",
    )

    with pytest.raises(ModelProtocolError, match="HTTP 500"):
        model.chat([Message(role="user", content="prompt secret")])

    assert "model request failed" in caplog.text
    assert "duration_ms=" in caplog.text
    assert "body secret" not in caplog.text
    assert "api-secret" not in caplog.text
    assert "prompt secret" not in caplog.text


class FakeConversationStore(ConversationMemory):
    def __init__(self) -> None:
        self._messages: list[Message] = []

    def append(self, session_id: SessionId, message: Message) -> None:
        self.append_many(session_id, [message])

    def append_many(self, session_id: SessionId, messages: list[Message]) -> None:
        self._messages.extend(messages)

    def history(self, session_id: SessionId) -> list[Message]:
        return list(self._messages)


class FakeModel(ModelProvider):
    def __init__(self, response: str) -> None:
        self._response = response

    def chat(self, messages: list[Message]) -> Message:
        return Message(role="assistant", content=self._response)
