"""Tests for Phase 4 capability registry."""

import pytest

from ai_assistant.application.tool_catalog import StaticToolCatalog
from ai_assistant.domain.errors import InvalidToolCallError
from ai_assistant.platform.application import StaticCapabilityRegistry
from ai_assistant.platform.domain import CapabilityName
from ai_assistant.platform.ports import CapabilityRegistry


pytestmark = pytest.mark.unit


def test_registry_exposes_read_only_capabilities_without_write() -> None:
    registry: CapabilityRegistry = StaticCapabilityRegistry(StaticToolCatalog())

    names = registry.names()

    assert CapabilityName.READ_FILE in names
    assert "write" not in {name.value.lower() for name in names}
    assert registry.tool_name_for(CapabilityName.READ_FILE) == "read_file"


def test_registry_returns_planner_metadata_without_tool_name() -> None:
    registry = StaticCapabilityRegistry(StaticToolCatalog())

    definition = registry.definition_for(CapabilityName.INSPECT_DIRECTORY)

    assert definition.name == CapabilityName.INSPECT_DIRECTORY
    assert definition.description
    assert "required" in definition.input_schema
    assert not hasattr(definition, "tool_name")


def test_registry_rejects_unknown_capability() -> None:
    registry: CapabilityRegistry = StaticCapabilityRegistry(StaticToolCatalog())

    with pytest.raises(InvalidToolCallError, match="unknown capability"):
        registry.tool_name_for("write")  # type: ignore[arg-type]


def test_registry_has_exact_phase4_capability_set() -> None:
    registry = StaticCapabilityRegistry(StaticToolCatalog())

    assert registry.names() == tuple(CapabilityName)
    assert len(registry.definitions()) == len(CapabilityName)
