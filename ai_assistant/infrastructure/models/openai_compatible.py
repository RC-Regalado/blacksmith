"""OpenAI Responses API model provider."""

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
from ai_assistant.domain.model_response import FinishReason, ModelResponse


logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class OpenAICompatibleModel(ModelProvider):
    model: str
    api_key: str | None = None
    base_url: str = "https://api.openai.com/v1"
    timeout_seconds: float = 60.0

    def chat(self, messages: list[Message]) -> ModelResponse:
        if not messages:
            raise InvalidMessageError("OpenAICompatibleModel requires messages.")

        payload = self._build_payload(messages)
        data = self._post_json("/responses", payload)
        message = Message(role="assistant", content=self._extract_text(data))
        return _to_model_response(message, data)

    def _build_payload(self, messages: list[Message]) -> dict[str, Any]:
        system_messages = [
            message.content for message in messages if message.role == "system"
        ]
        input_messages = [message for message in messages if message.role != "system"]
        payload: dict[str, Any] = {
            "model": self.model,
            "input": [self._input_item(message) for message in input_messages],
            "store": False,
            "stream": False,
        }
        if system_messages:
            payload["instructions"] = "\n\n".join(system_messages)
        return payload

    def _input_item(self, message: Message) -> dict[str, Any]:
        return {"role": message.role, "content": message.content}

    def _post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        started = perf_counter()
        request = Request(
            url=f"{self.base_url.rstrip('/')}{path}",
            data=json.dumps(payload).encode("utf-8"),
            headers=self._headers(),
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                try:
                    data = json.loads(response.read().decode("utf-8"))
                except json.JSONDecodeError as exc:
                    self._log_failure(started)
                    raise ModelProtocolError("OpenAI response was not valid JSON.") from exc
                if not isinstance(data, dict):
                    self._log_failure(started)
                    raise ModelProtocolError("OpenAI response JSON must be an object.")
        except HTTPError as error:
            self._log_failure(started, http_status=error.code)
            raise self._http_error(error) from error
        except URLError as error:
            self._log_failure(started)
            raise self._url_error(error) from error
        self._log_success(started)
        return data

    def _log_success(self, started: float) -> None:
        logger.info(
            "model request completed provider=openai model=%s duration_ms=%.2f",
            self.model,
            (perf_counter() - started) * 1000,
        )

    def _log_failure(self, started: float, http_status: int | None = None) -> None:
        logger.error(
            "model request failed provider=openai model=%s duration_ms=%.2f status=%s",
            self.model,
            (perf_counter() - started) * 1000,
            http_status or "unavailable",
        )

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _http_error(self, error: HTTPError) -> Exception:
        if error.code == 404:
            return ModelNotFoundError("Configured OpenAI model was not found.")
        return ModelProtocolError(f"OpenAI request failed with HTTP {error.code}.")

    def _url_error(self, error: URLError) -> Exception:
        if isinstance(error.reason, TimeoutError):
            return ModelTimeoutError("OpenAI request timed out.")
        return ModelConnectionError("OpenAI request failed.")

    def _extract_text(self, data: dict[str, Any]) -> str:
        output_text = data.get("output_text")
        if isinstance(output_text, str) and output_text:
            return output_text

        for item in data.get("output", []):
            text = self._extract_item_text(item)
            if text:
                return text
        raise ModelProtocolError("OpenAI response did not include assistant text.")

    def _extract_item_text(self, item: Any) -> str | None:
        if not isinstance(item, dict) or item.get("type") != "message":
            return None
        for content in item.get("content", []):
            if not isinstance(content, dict):
                continue
            if content.get("type") in {"output_text", "text"}:
                text = content.get("text")
                if isinstance(text, str) and text:
                    return text
        return None


def _to_model_response(message: Message, data: dict[str, Any]) -> ModelResponse:
    status = data.get("status")
    incomplete_reason = data.get("incomplete_details", {})
    if not isinstance(incomplete_reason, dict):
        incomplete_reason = {}
    if status == "completed":
        finish_reason = FinishReason.STOP
    elif incomplete_reason.get("reason") == "max_output_tokens":
        finish_reason = FinishReason.LENGTH
    else:
        finish_reason = FinishReason.UNKNOWN
    usage = data.get("usage", {})
    if not isinstance(usage, dict):
        usage = {}
    prompt_tokens = usage.get("input_tokens")
    output_tokens = usage.get("output_tokens")
    return ModelResponse(
        message=message,
        finish_reason=finish_reason,
        prompt_tokens=prompt_tokens if isinstance(prompt_tokens, int) else None,
        output_tokens=output_tokens if isinstance(output_tokens, int) else None,
        truncated=finish_reason == FinishReason.LENGTH,
        metadata={"status": status},
    )
