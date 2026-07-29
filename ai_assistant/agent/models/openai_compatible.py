"""OpenAI Responses API model provider."""

from dataclasses import dataclass
import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ai_assistant.agent.message import Message
from ai_assistant.agent.models.provider import ModelProvider


@dataclass(frozen=True, slots=True)
class OpenAICompatibleModel(ModelProvider):
    model: str
    api_key: str | None = None
    base_url: str = "https://api.openai.com/v1"
    timeout_seconds: float = 60.0

    def chat(self, messages: list[Message]) -> Message:
        if not messages:
            raise ValueError("OpenAICompatibleModel requires messages.")

        payload = self._build_payload(messages)
        data = self._post_json("/responses", payload)
        return Message(role="assistant", content=self._extract_text(data))

    def _build_payload(self, messages: list[Message]) -> dict[str, Any]:
        system_messages = [
            message.content for message in messages if message.role == "system"
        ]
        input_messages = [message for message in messages if message.role != "system"]
        payload: dict[str, Any] = {
            "model": self.model,
            "input": [self._input_item(message) for message in input_messages],
            "store": False,
        }
        if system_messages:
            payload["instructions"] = "\n\n".join(system_messages)
        return payload

    def _input_item(self, message: Message) -> dict[str, Any]:
        return {"role": message.role, "content": message.content}

    def _post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        request = Request(
            url=f"{self.base_url.rstrip('/')}{path}",
            data=json.dumps(payload).encode("utf-8"),
            headers=self._headers(),
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            raise RuntimeError(self._http_error_message(error)) from error
        except URLError as error:
            raise RuntimeError(f"OpenAI request failed: {error.reason}") from error

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _http_error_message(self, error: HTTPError) -> str:
        body = error.read().decode("utf-8", errors="replace")
        return f"OpenAI request failed with HTTP {error.code}: {body}"

    def _extract_text(self, data: dict[str, Any]) -> str:
        output_text = data.get("output_text")
        if isinstance(output_text, str) and output_text:
            return output_text

        for item in data.get("output", []):
            text = self._extract_item_text(item)
            if text:
                return text
        raise RuntimeError("OpenAI response did not include assistant text.")

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
