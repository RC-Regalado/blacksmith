"""Tests for the structured model-backed planner."""

import json

import pytest

from ai_assistant.application.ports.models import ModelProvider
from ai_assistant.application.tool_catalog import StaticToolCatalog
from ai_assistant.domain.errors import InvalidToolCallError
from ai_assistant.domain.message import Message
from ai_assistant.platform.application import ModelBackedPlanner, StaticCapabilityRegistry
from ai_assistant.platform.domain import CapabilityName, Objective


pytestmark = pytest.mark.unit


def test_model_backed_planner_maps_strict_json_to_plan() -> None:
    model = _Model(
        json.dumps(
            {
                "plan_id": "plan-1",
                "tasks": [
                    {
                        "task_id": "task-1",
                        "description": "Read README",
                        "capability": "ReadFile",
                        "arguments": {"path": "README.md"},
                        "dependencies": [],
                    }
                ],
            }
        )
    )
    planner = ModelBackedPlanner(model, StaticCapabilityRegistry(StaticToolCatalog()))

    plan = planner.create_plan(Objective("obj-1", "Inspect README"))

    assert plan.plan_id == "plan-1"
    assert plan.objective_id == "obj-1"
    assert plan.tasks[0].capability == CapabilityName.READ_FILE
    assert "ReadFile" in model.messages[1].content
    assert "write" not in model.messages[1].content.lower()
    assert planner.last_response_content == model._response


def test_model_backed_planner_accepts_fenced_json() -> None:
    planner = ModelBackedPlanner(
        _Model(
            '```json\n{"plan_id":"plan-1","tasks":[{"task_id":"task-1",'
            '"description":"List","capability":"InspectDirectory",'
            '"arguments":{"path":"."},"dependencies":[]}]}\n```'
        ),
        StaticCapabilityRegistry(StaticToolCatalog()),
    )

    plan = planner.create_plan(Objective("obj-1", "Inspect"))

    assert plan.tasks[0].capability == CapabilityName.INSPECT_DIRECTORY


def test_model_backed_planner_accepts_json_inside_text() -> None:
    planner = ModelBackedPlanner(
        _Model(
            'Plan:\n{"plan_id":"plan-1","tasks":[{"task_id":"task-1",'
            '"description":"Status","capability":"InspectGitStatus",'
            '"arguments":{"path":"."}}]}\nDone.'
        ),
        StaticCapabilityRegistry(StaticToolCatalog()),
    )

    plan = planner.create_plan(Objective("obj-1", "Inspect"))

    assert plan.tasks[0].capability == CapabilityName.INSPECT_GIT_STATUS


def test_model_backed_planner_accepts_action_input_aliases() -> None:
    planner = ModelBackedPlanner(
        _Model(
            json.dumps(
                {
                    "plan_id": "p-1",
                    "tasks": [
                        {
                            "task_id": "t-1",
                            "action": "InspectGitStatus",
                            "input": {"path": "."},
                        }
                    ],
                }
            )
        ),
        StaticCapabilityRegistry(StaticToolCatalog()),
    )

    plan = planner.create_plan(Objective("obj-1", "Inspect"))

    assert plan.tasks[0].description == "InspectGitStatus"
    assert plan.tasks[0].capability == CapabilityName.INSPECT_GIT_STATUS
    assert plan.tasks[0].arguments["path"] == "."


def test_model_backed_planner_accepts_parameters_and_missing_task_id() -> None:
    planner = ModelBackedPlanner(
        _Model(
            json.dumps(
                {
                    "plan_id": "p-1",
                    "tasks": [
                        {
                            "capability": "InspectGitStatus",
                            "parameters": {"path": ".", "max_entries": 50},
                        }
                    ],
                }
            )
        ),
        StaticCapabilityRegistry(StaticToolCatalog()),
    )

    plan = planner.create_plan(Objective("obj-1", "Inspect"))

    assert plan.tasks[0].task_id == "task-1"
    assert plan.tasks[0].capability == CapabilityName.INSPECT_GIT_STATUS
    assert plan.tasks[0].arguments["max_entries"] == 50


def test_model_backed_planner_rejects_invalid_json() -> None:
    planner = ModelBackedPlanner(_Model("not json"), StaticCapabilityRegistry(StaticToolCatalog()))

    with pytest.raises(InvalidToolCallError, match="invalid JSON"):
        planner.create_plan(Objective("obj-1", "Inspect"))


def test_model_backed_planner_rejects_unknown_capability() -> None:
    planner = ModelBackedPlanner(
        _Model(
            json.dumps(
                {
                    "plan_id": "plan-1",
                    "tasks": [
                        {
                            "task_id": "task-1",
                            "description": "Write",
                            "capability": "write",
                            "arguments": {"path": "README.md"},
                        }
                    ],
                }
            )
        ),
        StaticCapabilityRegistry(StaticToolCatalog()),
    )

    with pytest.raises(InvalidToolCallError, match="unknown capability"):
        planner.create_plan(Objective("obj-1", "Inspect"))


def test_model_backed_planner_rejects_malformed_task() -> None:
    planner = ModelBackedPlanner(
        _Model(json.dumps({"plan_id": "plan-1", "tasks": [{"task_id": "task-1"}]})),
        StaticCapabilityRegistry(StaticToolCatalog()),
    )

    with pytest.raises(InvalidToolCallError, match="planner field"):
        planner.create_plan(Objective("obj-1", "Inspect"))


class _Model(ModelProvider):
    def __init__(self, response: str) -> None:
        self._response = response
        self.messages: list[Message] = []

    def chat(self, messages: list[Message]) -> Message:
        self.messages = messages
        return Message(role="assistant", content=self._response)
