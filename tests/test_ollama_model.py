"""Tests for native Ollama model provider."""

import builtins
from io import BytesIO
import json
from pathlib import Path
from urllib.error import HTTPError, URLError

import pytest

from ai_assistant.agent.message import Message
from ai_assistant.agent.models.ollama import OllamaModelProvider
from ai_assistant.application.errors import (
    ModelConnectionError,
    ModelNotFoundError,
    ModelProtocolError,
    ModelTimeoutError,
)
from ai_assistant.bootstrap.config import AppConfig
from ai_assistant.bootstrap.container import create_application


pytestmark = pytest.mark.unit


def test_ollama_builds_native_chat_payload() -> None:
    provider = OllamaModelProvider(model="gemma")

    payload = provider._build_payload([Message(role="user", content="hello")])

    assert payload == {
        "model": "gemma",
        "messages": [{"role": "user", "content": "hello"}],
        "stream": False,
    }


def test_ollama_chat_returns_assistant_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "ai_assistant.agent.models.ollama.urlopen",
        lambda *_args, **_kwargs: FakeResponse(
            {"message": {"role": "assistant", "content": "hola"}}
        ),
    )

    response = OllamaModelProvider(model="gemma").chat(
        [Message(role="user", content="hello")]
    )

    assert response == Message(role="assistant", content="hola")


def test_ollama_posts_to_api_chat_with_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def fake_urlopen(request, timeout: float):
        captured["url"] = request.full_url
        captured["timeout"] = timeout
        return FakeResponse({"message": {"content": "ok"}})

    monkeypatch.setattr("ai_assistant.agent.models.ollama.urlopen", fake_urlopen)

    OllamaModelProvider(
        model="gemma",
        base_url="http://ollama.test",
        timeout_seconds=2.5,
    ).chat([Message(role="user", content="x")])

    assert captured == {
        "url": "http://ollama.test/api/chat",
        "timeout": 2.5,
    }


def test_ollama_missing_model_maps_to_typed_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "ai_assistant.agent.models.ollama.urlopen",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            HTTPError("url", 404, "not found", None, BytesIO(b"body"))
        ),
    )

    with pytest.raises(ModelNotFoundError, match="model was not found"):
        OllamaModelProvider(model="missing").chat([Message(role="user", content="x")])


def test_ollama_connection_failure_maps_to_typed_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "ai_assistant.agent.models.ollama.urlopen",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(URLError("down")),
    )

    with pytest.raises(ModelConnectionError, match="service is not available"):
        OllamaModelProvider(model="gemma").chat([Message(role="user", content="x")])


def test_ollama_timeout_maps_to_typed_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "ai_assistant.agent.models.ollama.urlopen",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(URLError(TimeoutError())),
    )

    with pytest.raises(ModelTimeoutError, match="timed out"):
        OllamaModelProvider(model="gemma").chat([Message(role="user", content="x")])


def test_ollama_empty_response_maps_to_protocol_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "ai_assistant.agent.models.ollama.urlopen",
        lambda *_args, **_kwargs: FakeResponse({"message": {"content": ""}}),
    )

    with pytest.raises(ModelProtocolError, match="assistant text"):
        OllamaModelProvider(model="gemma").chat([Message(role="user", content="x")])


def test_cli_responds_with_simulated_ollama(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(
        "ai_assistant.agent.models.ollama.urlopen",
        lambda *_args, **_kwargs: FakeResponse(
            {"message": {"role": "assistant", "content": "ollama ok"}}
        ),
    )
    inputs = iter(["hello", "quit"])
    monkeypatch.setattr(builtins, "input", lambda _prompt: next(inputs))
    app = create_application(
        AppConfig(
            provider="ollama",
            model="gemma",
            base_url="http://localhost:11434",
            database=str(tmp_path / "assistant.sqlite3"),
        )
    )

    app.run()

    assert "ollama ok\n" in capsys.readouterr().out


class FakeResponse:
    def __init__(self, data: dict[str, object]) -> None:
        self._body = json.dumps(data).encode("utf-8")

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self) -> bytes:
        return self._body
