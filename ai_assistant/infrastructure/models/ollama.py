"""Native Ollama chat API model provider."""

from dataclasses import dataclass
import json
import logging
from time import perf_counter
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ai_assistant.application.ports.models import ModelProvider
from ai_assistant.domain.errors import (
    InvalidMessageError,
    ModelConnectionError,
    ModelNotFoundError,
    ModelProtocolError,
    ModelTimeoutError,
)
from ai_assistant.domain.message import Message


logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class OllamaModelProvider(ModelProvider):
    model: str
    base_url: str = "http://localhost:11434"
    timeout_seconds: float = 60.0

    def chat(self, messages: list[Message]) -> Message:
        if not messages:
            raise InvalidMessageError("OllamaModelProvider requires messages.")
        payload = self._build_payload(messages)
        data = self._post_json("/api/chat", payload)
        return Message(role="assistant", content=self._extract_text(data))

    def _build_payload(self, messages: list[Message]) -> dict[str, Any]:
        return {
            "model": self.model,
            "messages": [self._message_item(message) for message in messages],
            "stream": False,
        }

    def _message_item(self, message: Message) -> dict[str, str]:
        return {"role": message.role, "content": message.content}

    def _post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        started = perf_counter()
        request = Request(
            url=f"{self.base_url.rstrip('/')}{path}",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                try:
                    data = json.loads(response.read().decode("utf-8"))
                except json.JSONDecodeError as exc:
                    self._log_failure(started)
                    raise ModelProtocolError("Ollama response was not valid JSON.") from exc
        except HTTPError as error:
            self._log_failure(started, http_status=error.code)
            raise self._http_error(error) from error
        except URLError as error:
            self._log_failure(started)
            raise self._url_error(error) from error
        self._log_success(started)
        return data

    def _extract_text(self, data: dict[str, Any]) -> str:
        message = data.get("message")
        if not isinstance(message, dict):
            raise ModelProtocolError("Ollama response did not include a message.")
        content = message.get("content")
        if not isinstance(content, str) or not content:
            raise ModelProtocolError("Ollama response did not include assistant text.")
        return content

    def _http_error(self, error: HTTPError) -> Exception:
        if error.code == 404:
            return ModelNotFoundError("Configured Ollama model was not found.")
        return ModelProtocolError(f"Ollama request failed with HTTP {error.code}.")

    def _url_error(self, error: URLError) -> Exception:
        if isinstance(error.reason, TimeoutError):
            return ModelTimeoutError("Ollama request timed out.")
        return ModelConnectionError("Ollama service is not available.")

    def _log_success(self, started: float) -> None:
        logger.info(
            "model request completed provider=ollama model=%s duration_ms=%.2f",
            self.model,
            (perf_counter() - started) * 1000,
        )

    def _log_failure(self, started: float, http_status: int | None = None) -> None:
        logger.error(
            "model request failed provider=ollama model=%s duration_ms=%.2f status=%s",
            self.model,
            (perf_counter() - started) * 1000,
            http_status or "unavailable",
        )
