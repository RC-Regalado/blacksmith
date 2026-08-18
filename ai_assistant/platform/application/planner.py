"""Planner implementations for tests and structured model output."""

from collections.abc import Mapping
import json

from ai_assistant.application.ports.models import ModelProvider
from ai_assistant.domain.errors import InvalidToolCallError
from ai_assistant.domain.message import Message
from ai_assistant.platform.domain.objective import Objective
from ai_assistant.platform.domain.plan import Plan
from ai_assistant.platform.domain.task import CapabilityName, PlatformTask
from ai_assistant.platform.ports.capability_registry import CapabilityRegistry
from ai_assistant.platform.ports.planner import Planner


class DeterministicPlanner(Planner):
    def __init__(self, plans: Mapping[str, Plan]) -> None:
        self._plans = dict(plans)

    def create_plan(self, objective: Objective) -> Plan:
        plan = self._plans.get(objective.objective_id)
        if not isinstance(plan, Plan):
            raise InvalidToolCallError("planner returned a malformed plan.")
        if plan.objective_id != objective.objective_id:
            raise InvalidToolCallError("planner returned a plan for a different objective.")
        return plan


class ModelBackedPlanner(Planner):
    def __init__(self, model: ModelProvider, registry: CapabilityRegistry) -> None:
        self._model = model
        self._registry = registry
        self.last_response_content: str | None = None

    def create_plan(self, objective: Objective) -> Plan:
        response = self._model.chat(_messages(objective, self._registry))
        self.last_response_content = response.content
        payload = _loads_object(response.content)
        plan_id = _text(payload, "plan_id")
        tasks = tuple(
            _task(objective.objective_id, index, item)
            for index, item in enumerate(_list(payload, "tasks"), start=1)
        )
        return Plan(plan_id, objective.objective_id, tasks)


def _messages(objective: Objective, registry: CapabilityRegistry) -> list[Message]:
    capabilities = [
        {"name": definition.name.value, "input_schema": _plain(definition.input_schema)}
        for definition in registry.definitions()
    ]
    return [
        Message(
            role="system",
            content=(
                "Return only valid JSON. Do not add Markdown, labels, explanations, "
                "tool calls or trailing commas. Schema: "
                '{"plan_id":"plan-id","tasks":[{"task_id":"task-1",'
                '"description":"short task","capability":"InspectGitStatus",'
                '"arguments":{"path":"."},"dependencies":[]}]}. '
                "Use capability and arguments keys. Use only listed capability names."
            ),
        ),
        Message(
            role="user",
            content=json.dumps(
                {
                    "objective_id": objective.objective_id,
                    "description": objective.description,
                    "success_criteria": objective.success_criteria,
                    "capabilities": capabilities,
                }
            ),
        ),
    ]


def _loads_object(content: str) -> Mapping[str, object]:
    source = _json_source(content)
    try:
        payload = json.loads(source)
    except json.JSONDecodeError as exc:
        raise InvalidToolCallError("planner returned invalid JSON.") from exc
    if not isinstance(payload, Mapping):
        raise InvalidToolCallError("planner returned a malformed plan.")
    return payload


def _json_source(content: str) -> str:
    stripped = content.strip()
    if stripped.startswith("```") and stripped.endswith("```"):
        _, _, rest = stripped.partition("\n")
        stripped = rest.removesuffix("```").strip()
    if stripped.startswith("{"):
        return stripped
    candidate = _first_json_object(stripped)
    return candidate or stripped


def _first_json_object(content: str) -> str | None:
    depth = 0
    start = None
    in_string = False
    escaped = False
    for index, char in enumerate(content):
        if in_string:
            escaped = char == "\\" and not escaped
            if char == '"' and not escaped:
                in_string = False
            elif char != "\\":
                escaped = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            start = index if start is None else start
            depth += 1
        elif char == "}" and depth:
            depth -= 1
            if depth == 0 and start is not None:
                return content[start : index + 1]
    return None


def _task(objective_id: str, index: int, payload: object) -> PlatformTask:
    if not isinstance(payload, Mapping):
        raise InvalidToolCallError("planner returned a malformed task.")
    capability = _capability(_text_any(payload, "capability", "action"))
    return PlatformTask(
        _text(payload, "task_id", default=f"task-{index}"),
        objective_id,
        _text(payload, "description", default=str(capability.value)),
        capability,
        _mapping_any(payload, "arguments", "input", "parameters"),
        tuple(_list(payload, "dependencies", default=())),
    )


def _capability(value: str) -> CapabilityName:
    try:
        return CapabilityName(value)
    except ValueError as exc:
        raise InvalidToolCallError("planner returned an unknown capability.") from exc


def _text(payload: Mapping[str, object], key: str, default: str | None = None) -> str:
    return _text_any(payload, key, default=default)


def _text_any(payload: Mapping[str, object], *keys: str, default: str | None = None) -> str:
    value = next((payload[key] for key in keys if key in payload), default)
    if not isinstance(value, str) or not value:
        raise InvalidToolCallError(
            f"planner field {'/'.join(keys)} must be a non-empty string."
        )
    return value


def _list(
    payload: Mapping[str, object],
    key: str,
    default: tuple[object, ...] | None = None,
) -> list[object] | tuple[object, ...]:
    value = payload.get(key, default)
    if not isinstance(value, list | tuple):
        raise InvalidToolCallError(f"planner field {key} must be a list.")
    return value


def _mapping(payload: Mapping[str, object], key: str) -> Mapping[str, object]:
    return _mapping_any(payload, key)


def _mapping_any(payload: Mapping[str, object], *keys: str) -> Mapping[str, object]:
    value = next((payload[key] for key in keys if key in payload), None)
    if not isinstance(value, Mapping):
        raise InvalidToolCallError(f"planner field {'/'.join(keys)} must be an object.")
    return value


def _plain(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, tuple | list):
        return [_plain(item) for item in value]
    return value
