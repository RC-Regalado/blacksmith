"""JSONL file sink for tool-loop diagnostics."""

from dataclasses import asdict
from pathlib import Path
import json
import re

from ai_assistant.application.ports.tools import ToolDiagnosticLogger
from ai_assistant.domain.tools import ToolCallLogEvent
from ai_assistant.infrastructure.sanitization import redact_sensitive

_SAFE = re.compile(r"[^A-Za-z0-9._-]+")


class JsonlToolDiagnosticLogger(ToolDiagnosticLogger):
    def __init__(self, directory: str | Path) -> None:
        self._directory = Path(directory)

    def record(self, event: ToolCallLogEvent) -> None:
        self._directory.mkdir(parents=True, exist_ok=True)
        path = self._directory / _filename(event.model, event.session_id, event.timestamp.date().isoformat())
        with path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(_payload(event), sort_keys=True, default=str) + "\n")


def _payload(event: ToolCallLogEvent) -> dict[str, object]:
    payload = asdict(event)
    payload["timestamp"] = event.timestamp.isoformat()
    payload["status"] = event.status.value
    payload["arguments"] = redact_sensitive(event.arguments)
    payload["result"] = redact_sensitive(event.result)
    payload["error"] = redact_sensitive(event.error)
    return payload


def _filename(model: str, session_id: str, date: str) -> str:
    return f"log-{_safe(model)}-{_safe(session_id)}-{date}.log"


def _safe(value: str) -> str:
    cleaned = _SAFE.sub("-", value.replace("/", "-").replace("\\", "-")).strip(".-")
    return cleaned or "unknown"
