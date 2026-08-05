"""Tests for the static read-only tool catalog."""

import pytest

from ai_assistant.application.tool_catalog import StaticToolCatalog
from ai_assistant.domain.errors import InvalidToolCallError
from ai_assistant.domain.tools import ToolPermission


pytestmark = pytest.mark.unit


def test_static_catalog_registers_productive_tools() -> None:
    catalog = StaticToolCatalog()

    names = {definition.name for definition in catalog.definitions()}

    assert names == {
        "build_project",
        "file_metadata",
        "git_diff",
        "git_status",
        "list_directory",
        "read_file",
        "run_tests",
        "search_text",
        "write",
    }
    assert "audit_purge" not in names
    assert catalog.definition_for("build_project").permission == ToolPermission.EXECUTE_PROJECT
    assert catalog.definition_for("file_metadata").permission == ToolPermission.READ_METADATA
    assert catalog.definition_for("git_diff").permission == ToolPermission.READ_REPOSITORY
    assert catalog.definition_for("git_status").permission == ToolPermission.READ_REPOSITORY
    assert catalog.definition_for("list_directory").permission == ToolPermission.READ_ONLY
    assert catalog.definition_for("read_file").permission == ToolPermission.READ_ONLY
    assert catalog.definition_for("run_tests").permission == ToolPermission.EXECUTE_PROJECT
    assert catalog.definition_for("search_text").permission == ToolPermission.READ_CONTENT
    assert catalog.definition_for("write").permission == ToolPermission.WRITE_WORKSPACE


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
    build_project = catalog.definition_for("build_project")
    file_metadata = catalog.definition_for("file_metadata")
    git_diff = catalog.definition_for("git_diff")
    git_status = catalog.definition_for("git_status")
    run_tests = catalog.definition_for("run_tests")
    search_text = catalog.definition_for("search_text")
    write = catalog.definition_for("write")

    assert read_file.defaults["timeout_seconds"] == 30.0
    assert read_file.defaults["max_bytes"] == 65536
    assert list_directory.defaults["max_entries"] == 1000
    assert list_directory.defaults["max_depth"] == 3
    assert build_project.defaults["timeout_seconds"] == 180.0
    assert build_project.limits["timeout_seconds"] == 1200.0
    assert file_metadata.defaults["timeout_seconds"] == 30.0
    assert git_diff.defaults["max_bytes"] == 16384
    assert git_diff.limits["max_bytes"] == 65536
    assert git_status.defaults["max_entries"] == 200
    assert git_status.limits["max_entries"] == 1000
    assert run_tests.defaults["stdout_limit_bytes"] == 131072
    assert run_tests.limits["stdout_limit_bytes"] == 2097152
    assert search_text.defaults["max_matches"] == 20
    assert search_text.limits["max_files"] == 200
    assert write.defaults["max_bytes"] == 65536
    assert write.limits["max_bytes"] == 65536


def test_tool_definition_metadata_is_immutable() -> None:
    definition = StaticToolCatalog().definition_for("list_directory")

    with pytest.raises(TypeError):
        definition.defaults["max_entries"] = 1

    with pytest.raises(TypeError):
        definition.limits["max_entries"] = 1

    with pytest.raises(TypeError):
        definition.input_schema["required"] = []
