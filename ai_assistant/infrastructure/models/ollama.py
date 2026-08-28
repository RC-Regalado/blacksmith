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
from ai_assistant.domain.model_response import FinishReason, ModelResponse


logger = logging.getLogger(__name__)

_FINISH_REASONS: dict[Any, FinishReason] = {
    "stop": FinishReason.STOP,
    "length": FinishReason.LENGTH,
}


@dataclass(frozen=True, slots=True)
class OllamaModelProvider(ModelProvider):
    model: str
    base_url: str = "http://localhost:11434"
    timeout_seconds: float = 60.0
    num_ctx: int | None = None
    num_predict: int | None = None

    def chat(self, messages: list[Message]) -> ModelResponse:
        if not messages:
            raise InvalidMessageError("OllamaModelProvider requires messages.")
        payload = self._build_payload(messages)
        data = self._post_json("/api/chat", payload)
        used_tool_call = _tool_call_text(data.get("message") or {}) is not None
        message = Message(role="assistant", content=self._extract_text(data))
        return self._to_model_response(message, data, used_tool_call=used_tool_call)

    def _build_payload(self, messages: list[Message]) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [self._message_item(message) for message in messages],
            "stream": False,
        }
        options = self._options()
        if options:
            payload["options"] = options
        return payload

    def _options(self) -> dict[str, int]:
        options: dict[str, int] = {}
        if self.num_ctx is not None:
            options["num_ctx"] = self.num_ctx
        if self.num_predict is not None:
            options["num_predict"] = self.num_predict
        return options

    def _to_model_response(
        self, message: Message, data: dict[str, Any], *, used_tool_call: bool
    ) -> ModelResponse:
        if used_tool_call:
            finish_reason = FinishReason.TOOL_CALL
        else:
            finish_reason = _FINISH_REASONS.get(data.get("done_reason"), FinishReason.UNKNOWN)
        prompt_tokens = data.get("prompt_eval_count")
        output_tokens = data.get("eval_count")
        return ModelResponse(
            message=message,
            finish_reason=finish_reason,
            prompt_tokens=prompt_tokens if isinstance(prompt_tokens, int) else None,
            output_tokens=output_tokens if isinstance(output_tokens, int) else None,
            truncated=finish_reason == FinishReason.LENGTH,
            metadata={
                "done": data.get("done"),
                "configured_num_ctx": self.num_ctx,
                "configured_num_predict": self.num_predict,
            },
        )

    def _message_item(self, message: Message) -> dict[str, str]:
        if message.role == "tool":
            return {"role": "user", "content": f"Tool result:\n{message.content}"}
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

    def _log_success(self, started: float) -> None:
        logger.info(
            "model request completed provider=ollama model=%s duration_ms=%.2f "
            "num_ctx=%s num_predict=%s",
            self.model,
            (perf_counter() - started) * 1000,
            self.num_ctx if self.num_ctx is not None else "default",
            self.num_predict if self.num_predict is not None else "default",
        )

    def _extract_text(self, data: dict[str, Any]) -> str:
        message = data.get("message")
        if not isinstance(message, dict):
            raise ModelProtocolError("Ollama response did not include a message.")
        content = message.get("content")
        if isinstance(content, str) and content:
            return content
        tool_call = _tool_call_text(message)
        if tool_call:
            return tool_call
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

    def _log_failure(self, started: float, http_status: int | None = None) -> None:
        logger.error(
            "model request failed provider=ollama model=%s duration_ms=%.2f status=%s",
            self.model,
            (perf_counter() - started) * 1000,
            http_status or "unavailable",
        )


def _tool_call_text(message: dict[str, Any]) -> str | None:
    tool_calls = message.get("tool_calls")
    if not isinstance(tool_calls, list) or not tool_calls:
        return None
    function = tool_calls[0].get("function") if isinstance(tool_calls[0], dict) else None
    if not isinstance(function, dict) or not isinstance(function.get("name"), str):
        return None
    arguments = function.get("arguments", {})
    if not isinstance(arguments, dict):
        arguments = {}
    return json.dumps(
        {"tool_call": {"name": function["name"], "arguments": arguments}},
        sort_keys=True,
    )
