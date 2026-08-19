"""Adversarial coverage for Phase 5 knowledge behavior."""

import pytest

from ai_assistant.application.errors import InvalidToolCallError
from ai_assistant.domain.errors import InvalidKnowledgeError, KnowledgeStoreError
from ai_assistant.infrastructure.embeddings import DummyEmbeddingProvider
from ai_assistant.infrastructure.storage.sqlite_knowledge import SQLiteKnowledgeStore
from ai_assistant.interfaces.cli.knowledge import KnowledgeCli
from ai_assistant.knowledge import (
    ContextBudget,
    ContextCompiler,
    ContextPurpose,
    FreshnessStatus,
    KnowledgeChunk,
    KnowledgeDocument,
    KnowledgeQuery,
    KnowledgeSourceType,
    RetrievalCandidate,
)
from ai_assistant.knowledge.ranking import KnowledgeRanker


pytestmark = pytest.mark.unit


def test_knowledge_cli_rejects_sensitive_hidden_oversized_and_malformed_files(tmp_path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / ".hidden").write_text("hidden", encoding="utf-8")
    (workspace / "secret.pem").write_text("secret", encoding="utf-8")
    (workspace / "large.txt").write_text("too large", encoding="utf-8")
    (workspace / "bad.txt").write_bytes(b"\xff")
    cli = KnowledgeCli(SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3"), str(workspace), 4)

    with pytest.raises(InvalidToolCallError, match="hidden"):
        cli.run(("index", ".hidden"))
    with pytest.raises(InvalidToolCallError, match="sensitive"):
        cli.run(("index", "secret.pem"))
    with pytest.raises(InvalidToolCallError, match="max read bytes"):
        cli.run(("index", "large.txt"))
    with pytest.raises(InvalidToolCallError, match="utf-8"):
        cli.run(("index", "bad.txt"))


def test_knowledge_store_rebuild_and_duplicate_chunk_adversarial_paths(tmp_path) -> None:
    store = SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3")
    store.save_document(_document())
    duplicate = KnowledgeChunk("chunk-1", "doc-1", "blacksmith", 0, 1, "hash-1")

    with pytest.raises(KnowledgeStoreError, match="chunks"):
        store.save_chunks("doc-1", (duplicate, duplicate))

    store.save_chunks("doc-1", (duplicate,))
    store.clear()

    assert store.list_documents() == ()
    assert store.lexical_search(KnowledgeQuery("blacksmith")) == ()


def test_retrieval_context_excludes_stale_and_rejects_bad_provenance(tmp_path) -> None:
    store = SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3")
    provider = DummyEmbeddingProvider(dimension=4)
    store.save_document(_document())
    store.save_chunks("doc-1", (KnowledgeChunk("chunk-1", "doc-1", "blacksmith", 0, 1, "hash-1"),))
    store.save_embedding("chunk-1", provider.embed_texts(("blacksmith",))[0])

    store.mark_document_stale("doc-1")

    assert store.lexical_search(KnowledgeQuery("blacksmith")) == ()
    assert store.semantic_search(provider.embed_texts(("blacksmith",))[0]) == ()

    ranked = KnowledgeRanker().rank((_candidate(content_hash="wrong"),), 1)
    with pytest.raises(InvalidKnowledgeError, match="provenance|fresh"):
        ContextCompiler(store).compile(ContextPurpose.PLANNING, ranked, ContextBudget())


def test_context_budget_overflow_omits_evidence(tmp_path) -> None:
    store = SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3")
    store.save_document(_document())
    store.save_chunks("doc-1", (KnowledgeChunk("chunk-1", "doc-1", "too many tokens", 0, 3, "hash-1"),))
    ranked = KnowledgeRanker().rank((_candidate(token_count=3),), 1)

    context = ContextCompiler(store).compile(
        ContextPurpose.SYNTHESIS,
        ranked,
        ContextBudget(max_context_tokens=2, max_sources=1, max_chunks=1, max_chunk_tokens=2),
    )

    assert context.evidence == ()


def _document() -> KnowledgeDocument:
    return KnowledgeDocument("doc-1", KnowledgeSourceType.FILE, "README.md", "v1", "doc-hash")


def _candidate(
    *,
    content_hash: str = "hash-1",
    token_count: int = 1,
) -> RetrievalCandidate:
    return RetrievalCandidate(
        "chunk-1",
        "doc-1",
        KnowledgeSourceType.FILE,
        "README.md",
        "v1",
        content_hash,
        1.0,
        "fts5",
        token_count,
        FreshnessStatus.FRESH,
    )
