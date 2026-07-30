"""Contract tests for OpenAI-compatible provider."""

from io import BytesIO
import json
from urllib.error import HTTPError, URLError

import pytest

from ai_assistant.agent.message import Message
from ai_assistant.infrastructure.models.openai_compatible import OpenAICompatibleModel
from ai_assistant.application.errors import (
    ModelConnectionError,
    ModelNotFoundError,
    ModelProtocolError,
    ModelTimeoutError,
)
from ai_assistant.application.ports.models import ModelProvider


pytestmark = pytest.mark.contract


def test_openai_compatible_implements_model_provider() -> None:
    provider: ModelProvider = OpenAICompatibleModel(model="test")

    assert isinstance(provider, OpenAICompatibleModel)


def test_openai_request_mapper_uses_responses_payload() -> None:
    provider = OpenAICompatibleModel(model="test-model")

    payload = provider._build_payload(
        [
            Message(role="system", content="system"),
            Message(role="user", content="hello"),
        ]
    )

    assert payload == {
        "model": "test-model",
        "input": [{"role": "user", "content": "hello"}],
        "store": False,
        "stream": False,
        "instructions": "system",
    }


def test_openai_chat_posts_to_responses_with_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def fake_urlopen(request, timeout: float):
        captured["url"] = request.full_url
        captured["timeout"] = timeout
        captured["body"] = json.loads(request.data.decode("utf-8"))
        return FakeResponse({"output_text": "ok"})

    monkeypatch.setattr(
        "ai_assistant.infrastructure.models.openai_compatible.urlopen",
        fake_urlopen,
    )

    response = OpenAICompatibleModel(
        model="test",
        base_url="http://openai.test/v1",
        timeout_seconds=2.5,
    ).chat([Message(role="user", content="hello")])

    assert response == Message(role="assistant", content="ok")
    assert captured["url"] == "http://openai.test/v1/responses"
    assert captured["timeout"] == 2.5
    assert captured["body"] == {
        "model": "test",
        "input": [{"role": "user", "content": "hello"}],
        "store": False,
        "stream": False,
    }


def test_openai_response_mapper_reads_nested_output_text() -> None:
    provider = OpenAICompatibleModel(model="test")

    assert provider._extract_text(
        {
            "output": [
                {
                    "type": "message",
                    "content": [{"type": "output_text", "text": "nested"}],
                }
            ]
        }
    ) == "nested"


def test_openai_non_object_json_maps_to_protocol_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "ai_assistant.infrastructure.models.openai_compatible.urlopen",
        lambda *_args, **_kwargs: RawResponse(b"[]"),
    )

    with pytest.raises(ModelProtocolError, match="must be an object"):
        OpenAICompatibleModel(model="test").chat([Message(role="user", content="x")])


def test_openai_timeout_maps_to_typed_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "ai_assistant.infrastructure.models.openai_compatible.urlopen",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(URLError(TimeoutError())),
    )

    with pytest.raises(ModelTimeoutError, match="timed out"):
        OpenAICompatibleModel(model="test").chat([Message(role="user", content="x")])


def test_openai_missing_model_maps_to_typed_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "ai_assistant.infrastructure.models.openai_compatible.urlopen",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            HTTPError("url", 404, "not found", None, BytesIO(b"body"))
        ),
    )

    with pytest.raises(ModelNotFoundError, match="model was not found"):
        OpenAICompatibleModel(model="missing").chat([Message(role="user", content="x")])


def test_openai_connection_error_maps_to_typed_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "ai_assistant.infrastructure.models.openai_compatible.urlopen",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(URLError("down")),
    )

    with pytest.raises(ModelConnectionError, match="OpenAI request failed"):
        OpenAICompatibleModel(model="test").chat([Message(role="user", content="x")])


class FakeResponse:
    def __init__(self, data: dict[str, object]) -> None:
        self._body = json.dumps(data).encode("utf-8")

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self) -> bytes:
        return self._body


class RawResponse:
    def __init__(self, body: bytes) -> None:
        self._body = body

    def __enter__(self) -> "RawResponse":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self) -> bytes:
        return self._body
