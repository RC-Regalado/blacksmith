"""Tests for the static read-only tool catalog."""

import pytest

from ai_assistant.application.tool_catalog import StaticToolCatalog
from ai_assistant.domain.errors import InvalidToolCallError
from ai_assistant.domain.tools import ToolPermission


pytestmark = pytest.mark.unit


def test_static_catalog_registers_only_productive_read_only_tools() -> None:
    catalog = StaticToolCatalog()

    names = {definition.name for definition in catalog.definitions()}

    assert names == {"list_directory", "read_file"}
    assert all(
        definition.permission == ToolPermission.READ_ONLY
        for definition in catalog.definitions()
    )


@pytest.mark.parametrize(
    "tool_name",
    ["LIST_DIRECTORY", "list_dir", "read-file", "noop", "read_file "],
)
def test_static_catalog_rejects_unknown_and_case_variant_names(tool_name: str) -> None:
    catalog = StaticToolCatalog()

    with pytest.raises(InvalidToolCallError, match="Unknown tool"):
        catalog.definition_for(tool_name)


def test_static_catalog_uses_exact_name_lookup() -> None:
    catalog = StaticToolCatalog()

    definition = catalog.definition_for("read_file")

    assert definition.name == "read_file"
    assert definition.defaults["max_bytes"] == 16384
    assert definition.limits["max_bytes"] == 65536


def test_static_catalog_uses_configured_defaults_capped_by_hard_limits() -> None:
    catalog = StaticToolCatalog(
        tool_timeout=40,
        max_read_bytes=70000,
        max_directory_entries=2000,
        max_directory_depth=9,
    )

    read_file = catalog.definition_for("read_file")
    list_directory = catalog.definition_for("list_directory")

    assert read_file.defaults["timeout_seconds"] == 30.0
    assert read_file.defaults["max_bytes"] == 65536
    assert list_directory.defaults["max_entries"] == 1000
    assert list_directory.defaults["max_depth"] == 3


def test_tool_definition_metadata_is_immutable() -> None:
    definition = StaticToolCatalog().definition_for("list_directory")

    with pytest.raises(TypeError):
        definition.defaults["max_entries"] = 1

    with pytest.raises(TypeError):
        definition.limits["max_entries"] = 1

    with pytest.raises(TypeError):
        definition.input_schema["required"] = []
