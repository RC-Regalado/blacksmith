"""Tests for typed internal errors."""

from io import BytesIO
from urllib.error import HTTPError, URLError

import pytest

from ai_assistant.agent.message import Message
from ai_assistant.infrastructure.models.dummy import DummyModel
from ai_assistant.infrastructure.models.openai_compatible import OpenAICompatibleModel
from ai_assistant.application.errors import (
    AssistantError,
    InvalidMessageError,
    ModelConnectionError,
    ModelNotFoundError,
    ModelProtocolError,
)
from ai_assistant.cli.app import CliApplication


pytestmark = pytest.mark.unit


def test_empty_message_raises_typed_error() -> None:
    with pytest.raises(InvalidMessageError, match="Message content"):
        Message(role="user", content="")


def test_dummy_model_without_user_message_raises_typed_error() -> None:
    with pytest.raises(InvalidMessageError, match="DummyModel"):
        DummyModel().chat([Message(role="system", content="system")])


def test_openai_404_maps_to_model_not_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "ai_assistant.infrastructure.models.openai_compatible.urlopen",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            HTTPError("url", 404, "not found", None, BytesIO(b"body secret"))
        ),
    )

    with pytest.raises(ModelNotFoundError, match="model was not found"):
        OpenAICompatibleModel(model="missing").chat([Message(role="user", content="x")])


def test_openai_invalid_json_maps_to_protocol_error(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level("ERROR")
    monkeypatch.setattr(
        "ai_assistant.infrastructure.models.openai_compatible.urlopen",
        lambda *_args, **_kwargs: FakeResponse(b"not json"),
    )

    with pytest.raises(ModelProtocolError, match="valid JSON"):
        OpenAICompatibleModel(model="test").chat([Message(role="user", content="x")])
    assert "model request failed" in caplog.text


def test_openai_url_error_maps_to_connection_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "ai_assistant.infrastructure.models.openai_compatible.urlopen",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(URLError("down")),
    )

    with pytest.raises(ModelConnectionError, match="OpenAI request failed"):
        OpenAICompatibleModel(model="test").chat([Message(role="user", content="x")])


def test_cli_translates_expected_errors_without_traceback(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    inputs = iter(["hello", "quit"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(inputs))

    CliApplication(FailingRuntime()).run()

    captured = capsys.readouterr()
    assert "Error: expected failure" in captured.err
    assert "Traceback" not in captured.err


class FakeResponse:
    def __init__(self, body: bytes) -> None:
        self._body = body

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self) -> bytes:
        return self._body


class FailingRuntime:
    def respond(self, user_input: str) -> Message:
        raise AssistantError("expected failure")
