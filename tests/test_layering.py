"""Layer dependency checks."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


def _imports_under(package: str) -> set[str]:
    modules: set[str] = set()
    package_path = ROOT / package.replace(".", "/")
    for path in package_path.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules.add(node.module)
    return modules


@pytest.mark.unit
def test_domain_does_not_import_outer_layers() -> None:
    forbidden = (
        "ai_assistant.application",
        "ai_assistant.infrastructure",
        "ai_assistant.interfaces",
        "ai_assistant.storage",
        "ai_assistant.cli",
    )
    assert not any(
        module.startswith(forbidden) for module in _imports_under("ai_assistant.domain")
    )


@pytest.mark.unit
def test_application_does_not_import_adapters() -> None:
    forbidden = (
        "ai_assistant.infrastructure",
        "ai_assistant.storage",
        "ai_assistant.interfaces",
        "ai_assistant.cli",
    )
    assert not any(
        module.startswith(forbidden)
        for module in _imports_under("ai_assistant.application")
    )


@pytest.mark.unit
def test_cli_adapter_does_not_construct_dependencies() -> None:
    imports = _imports_under("ai_assistant.interfaces.cli")
    assert "ai_assistant.bootstrap.container" not in imports
    assert "ai_assistant.infrastructure.models.adapter" not in imports
    assert "ai_assistant.infrastructure.storage.sqlite_memory" not in imports
