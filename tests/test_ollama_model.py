"""Tests for native Ollama model provider."""

import builtins
from io import BytesIO
import json
from pathlib import Path
from urllib.error import HTTPError, URLError

import pytest

from ai_assistant.agent.message import FinishReason, Message
from ai_assistant.infrastructure.models.ollama import OllamaModelProvider
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


def test_ollama_maps_tool_result_messages_to_user_payload() -> None:
    provider = OllamaModelProvider(model="gemma")

    payload = provider._build_payload(
        [Message(role="tool", content='{"content":{"entries":[]}}')]
    )

    assert payload["messages"] == [
        {"role": "user", "content": 'Tool result:\n{"content":{"entries":[]}}'}
    ]


def test_ollama_chat_returns_assistant_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "ai_assistant.infrastructure.models.ollama.urlopen",
        lambda *_args, **_kwargs: FakeResponse(
            {"message": {"role": "assistant", "content": "hola"}}
        ),
    )

    response = OllamaModelProvider(model="gemma").chat(
        [Message(role="user", content="hello")]
    )

    assert response.message == Message(role="assistant", content="hola")


def test_ollama_tool_call_response_maps_to_internal_json(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "ai_assistant.infrastructure.models.ollama.urlopen",
        lambda *_args, **_kwargs: FakeResponse(
            {
                "message": {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "function": {
                                "name": "list_directory",
                                "arguments": {"path": "."},
                            }
                        }
                    ],
                }
            }
        ),
    )

    response = OllamaModelProvider(model="gemma").chat(
        [Message(role="user", content="list files")]
    )

    assert json.loads(response.message.content) == {
        "tool_call": {"name": "list_directory", "arguments": {"path": "."}}
    }
    assert response.finish_reason == FinishReason.TOOL_CALL


def test_ollama_length_termination_surfaces_truncation_and_tokens(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "ai_assistant.infrastructure.models.ollama.urlopen",
        lambda *_args, **_kwargs: FakeResponse(
            {
                "message": {"role": "assistant", "content": "hola"},
                "done": True,
                "done_reason": "length",
                "prompt_eval_count": 120,
                "eval_count": 45,
            }
        ),
    )

    response = OllamaModelProvider(model="gemma").chat(
        [Message(role="user", content="hello")]
    )

    assert response.finish_reason == FinishReason.LENGTH
    assert response.truncated is True
    assert response.prompt_tokens == 120
    assert response.output_tokens == 45


def test_ollama_stop_termination_is_not_truncated(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "ai_assistant.infrastructure.models.ollama.urlopen",
        lambda *_args, **_kwargs: FakeResponse(
            {
                "message": {"role": "assistant", "content": "hola"},
                "done": True,
                "done_reason": "stop",
                "prompt_eval_count": 10,
                "eval_count": 5,
            }
        ),
    )

    response = OllamaModelProvider(model="gemma").chat(
        [Message(role="user", content="hello")]
    )

    assert response.finish_reason == FinishReason.STOP
    assert response.truncated is False


def test_ollama_sends_configured_num_ctx_and_num_predict() -> None:
    provider = OllamaModelProvider(model="gemma", num_ctx=4096, num_predict=512)

    payload = provider._build_payload([Message(role="user", content="hello")])

    assert payload["options"] == {"num_ctx": 4096, "num_predict": 512}


def test_ollama_omits_options_when_not_configured() -> None:
    provider = OllamaModelProvider(model="gemma")

    payload = provider._build_payload([Message(role="user", content="hello")])

    assert "options" not in payload


def test_ollama_posts_to_api_chat_with_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def fake_urlopen(request, timeout: float):
        captured["url"] = request.full_url
        captured["timeout"] = timeout
        return FakeResponse({"message": {"content": "ok"}})

    monkeypatch.setattr("ai_assistant.infrastructure.models.ollama.urlopen", fake_urlopen)

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
        "ai_assistant.infrastructure.models.ollama.urlopen",
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
        "ai_assistant.infrastructure.models.ollama.urlopen",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(URLError("down")),
    )

    with pytest.raises(ModelConnectionError, match="service is not available"):
        OllamaModelProvider(model="gemma").chat([Message(role="user", content="x")])


def test_ollama_timeout_maps_to_typed_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "ai_assistant.infrastructure.models.ollama.urlopen",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(URLError(TimeoutError())),
    )

    with pytest.raises(ModelTimeoutError, match="timed out"):
        OllamaModelProvider(model="gemma").chat([Message(role="user", content="x")])


def test_ollama_empty_response_maps_to_protocol_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "ai_assistant.infrastructure.models.ollama.urlopen",
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
        "ai_assistant.infrastructure.models.ollama.urlopen",
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
