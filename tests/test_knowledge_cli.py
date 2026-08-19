"""Tests for the manual knowledge CLI."""

import pytest

from ai_assistant.application.errors import InvalidToolCallError
from ai_assistant.infrastructure.storage.sqlite_knowledge import SQLiteKnowledgeStore
from ai_assistant.interfaces.cli.knowledge import KnowledgeCli


pytestmark = pytest.mark.unit


def test_knowledge_cli_indexes_queries_and_reports_status(
    tmp_path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "README.md").write_text("# Install\nblacksmith setup\n", encoding="utf-8")
    cli = KnowledgeCli(SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3"), str(workspace), 1024)

    cli.run(("index", "README.md"))
    cli.run(("query", "blacksmith"))
    cli.run(("status",))

    output = capsys.readouterr().out
    assert "indexed=1 skipped=0" in output
    assert "file:README.md:0:" in output
    assert "README.md score=" in output
    assert "documents=1 fresh=1 chunks=1 symbols=1" in output


def test_knowledge_cli_skips_unchanged_file(tmp_path, capsys: pytest.CaptureFixture[str]) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "README.md").write_text("blacksmith setup\n", encoding="utf-8")
    cli = KnowledgeCli(SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3"), str(workspace), 1024)

    cli.run(("index", "README.md"))
    cli.run(("index", "README.md"))

    assert "indexed=0 skipped=1" in capsys.readouterr().out


def test_knowledge_cli_rebuild_clears_previous_derived_state(
    tmp_path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "old.md").write_text("old blacksmith\n", encoding="utf-8")
    (workspace / "new.md").write_text("new blacksmith\n", encoding="utf-8")
    cli = KnowledgeCli(SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3"), str(workspace), 1024)

    cli.run(("index", "old.md"))
    cli.run(("rebuild", "new.md"))
    cli.run(("query", "old"))

    output = capsys.readouterr().out
    assert "indexed=1 skipped=0" in output
    assert "old.md score=" not in output


def test_knowledge_cli_denies_hidden_sensitive_and_oversized_files(tmp_path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / ".env").write_text("secret", encoding="utf-8")
    (workspace / "large.txt").write_text("too large", encoding="utf-8")
    cli = KnowledgeCli(SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3"), str(workspace), 4)

    with pytest.raises(InvalidToolCallError, match="hidden"):
        cli.run(("index", ".env"))
    with pytest.raises(InvalidToolCallError, match="max read bytes"):
        cli.run(("index", "large.txt"))
