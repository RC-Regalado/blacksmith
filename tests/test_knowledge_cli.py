"""Tests for the manual knowledge CLI."""

import pytest

from ai_assistant.application.errors import InvalidToolCallError
from ai_assistant.domain.errors import KnowledgeStoreError
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
    assert "status=fresh documents=1 fresh=1 stale=0 chunks=1 symbols=1" in output


def test_knowledge_cli_query_metrics(tmp_path, capsys: pytest.CaptureFixture[str]) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "README.md").write_text("blacksmith local assistant", encoding="utf-8")
    cli = KnowledgeCli(SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3"), str(workspace), 1024)

    cli.run(("index", "README.md"))
    cli.run(("query", "blacksmith", "--metrics"))

    output = capsys.readouterr().out
    assert "Metrics:" in output
    assert "- knowledge_candidates=1" in output


def test_knowledge_cli_status_distinguishes_empty_partial_stale_and_error(
    tmp_path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "fresh.md").write_text("fresh blacksmith\n", encoding="utf-8")
    (workspace / "stale.md").write_text("stale blacksmith\n", encoding="utf-8")
    store = SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3")
    cli = KnowledgeCli(store, str(workspace), 1024)

    cli.run(("status",))
    cli.run(("index", "fresh.md"))
    cli.run(("index", "stale.md"))
    store.mark_document_stale("file:stale.md")
    cli.run(("status",))
    store.mark_document_stale("file:fresh.md")
    cli.run(("status",))
    KnowledgeCli(FailingStatusStore(), str(workspace), 1024).run(("status",))

    output = capsys.readouterr().out
    assert "status=empty documents=0 fresh=0 stale=0 chunks=0 symbols=0" in output
    assert "status=partially-stale documents=2 fresh=1 stale=1 chunks=2 symbols=0" in output
    assert "status=stale documents=2 fresh=0 stale=2 chunks=2 symbols=0" in output
    assert "status=error documents=0 fresh=0 stale=0 chunks=0 symbols=0" in output
    assert "diagnostic=knowledge status unavailable." in output


def test_knowledge_cli_query_reports_empty_stale_and_no_match_diagnostics(
    tmp_path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "README.md").write_text("blacksmith local assistant\n", encoding="utf-8")
    store = SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3")
    cli = KnowledgeCli(store, str(workspace), 1024)

    cli.run(("query", "blacksmith"))
    cli.run(("index", "README.md"))
    cli.run(("query", "missingterm"))
    store.mark_document_stale("file:README.md")
    cli.run(("query", "blacksmith"))

    output = capsys.readouterr().out
    assert "No indexed knowledge is available." in output
    assert "No fresh indexed knowledge matched the query." in output
    assert "Indexed knowledge is stale." in output
    assert "no rebuild was run." in output


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


def test_knowledge_cli_skips_external_symlink_during_recursive_index(tmp_path, capsys) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("secret", encoding="utf-8")
    (workspace / "link.txt").symlink_to(outside)
    cli = KnowledgeCli(SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3"), str(workspace), 1024)

    cli.run(("index", "."))

    assert "indexed=0 skipped=0" in capsys.readouterr().out


def test_knowledge_cli_skips_non_utf8_file_during_recursive_index(tmp_path, capsys) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "README.md").write_text("blacksmith setup\n", encoding="utf-8")
    (workspace / "compiled.pyc").write_bytes(b"\xff\xd8\xb9\x00")
    cli = KnowledgeCli(SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3"), str(workspace), 1024)

    cli.run(("rebuild", "."))

    assert "indexed=1 skipped=1" in capsys.readouterr().out


class FailingStatusStore:
    def list_documents(self):
        raise KnowledgeStoreError("knowledge status unavailable.")
