"""Tests for the dedicated SQLite knowledge store."""

import sqlite3

import pytest

from ai_assistant.infrastructure.embeddings import DummyEmbeddingProvider
from ai_assistant.infrastructure.storage.sqlite_knowledge import SQLiteKnowledgeStore
from ai_assistant.domain.errors import KnowledgeStoreError
from ai_assistant.knowledge import (
    EmbeddingVector,
    FreshnessStatus,
    KnowledgeChunk,
    KnowledgeDocument,
    KnowledgeQuery,
    KnowledgeSourceType,
    KnowledgeSymbol,
)


pytestmark = pytest.mark.unit


def test_sqlite_knowledge_store_reloads_documents_chunks_and_symbols(tmp_path) -> None:
    database = tmp_path / "knowledge.sqlite3"
    store = SQLiteKnowledgeStore(database)
    document = _document(metadata={"language": "python"})
    chunks = (
        KnowledgeChunk("chunk-2", "doc-1", "second", 1, 1, "chunk-hash-2"),
        KnowledgeChunk("chunk-1", "doc-1", "first", 0, 1, "chunk-hash-1"),
    )
    symbol = KnowledgeSymbol("sym-1", "doc-1", "chunk-1", "main", "function", "main.py:1")

    store.save_document(document)
    store.save_chunks("doc-1", chunks)
    store.save_symbols("doc-1", (symbol,))
    restored = SQLiteKnowledgeStore(database)

    assert restored.load_document("doc-1") == document
    assert restored.chunks_for("doc-1") == (chunks[1], chunks[0])
    assert restored.symbols_for("doc-1") == (symbol,)


def test_sqlite_knowledge_store_lists_by_source_type(tmp_path) -> None:
    store = SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3")
    file_doc = _document("file-doc", KnowledgeSourceType.FILE, "README.md")
    adr_doc = _document("adr-doc", KnowledgeSourceType.ADR, "docs/adr/ADR-001.md")

    store.save_document(adr_doc)
    store.save_document(file_doc)

    assert store.list_documents() == (adr_doc, file_doc)
    assert store.list_documents(KnowledgeSourceType.FILE) == (file_doc,)


def test_sqlite_knowledge_store_deletes_and_clears_derived_state(tmp_path) -> None:
    store = SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3")
    store.save_document(_document())
    store.save_chunks("doc-1", (KnowledgeChunk("chunk-1", "doc-1", "first", 0, 1, "chunk-hash"),))
    store.save_symbols("doc-1", (KnowledgeSymbol("sym-1", "doc-1", "chunk-1", "main", "function"),))

    store.delete_document("doc-1")

    assert store.load_document("doc-1") is None
    assert store.chunks_for("doc-1") == ()
    assert store.symbols_for("doc-1") == ()

    store.save_document(_document())
    store.clear()
    assert store.list_documents() == ()


def test_sqlite_knowledge_store_uses_dedicated_tables(tmp_path) -> None:
    database = tmp_path / "knowledge.sqlite3"
    SQLiteKnowledgeStore(database)

    with sqlite3.connect(database) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }

    assert "messages" not in tables
    assert "tool_audit" not in tables
    assert "executions" not in tables
    assert {
        "knowledge_documents",
        "knowledge_chunks",
        "knowledge_embeddings",
        "knowledge_symbols",
    }.issubset(tables)


def test_sqlite_knowledge_store_preserves_freshness_state(tmp_path) -> None:
    store = SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3")
    document = _document(freshness=FreshnessStatus.STALE)
    chunk = KnowledgeChunk(
        "chunk-1",
        "doc-1",
        "stale text",
        0,
        2,
        "chunk-hash",
        freshness=FreshnessStatus.STALE,
    )

    store.save_document(document)
    store.save_chunks("doc-1", (chunk,))

    assert store.load_document("doc-1") == document
    assert store.chunks_for("doc-1") == (chunk,)


def test_sqlite_knowledge_store_detects_unchanged_fresh_document(tmp_path) -> None:
    store = SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3")
    store.save_document(_document())

    assert store.document_is_current("doc-1", "v1", "doc-hash")
    assert not store.document_is_current("doc-1", "v2", "doc-hash")
    assert not store.document_is_current("doc-1", "v1", "other-hash")
    assert not store.document_is_current("missing", "v1", "doc-hash")


def test_sqlite_knowledge_store_marks_document_and_chunks_stale(tmp_path) -> None:
    store = SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3")
    store.save_document(_document())
    store.save_chunks("doc-1", (KnowledgeChunk("chunk-1", "doc-1", "text", 0, 1, "chunk-hash"),))

    store.mark_document_stale("doc-1")

    assert store.load_document("doc-1").freshness == FreshnessStatus.STALE
    assert store.chunks_for("doc-1")[0].freshness == FreshnessStatus.STALE
    assert not store.document_is_current("doc-1", "v1", "doc-hash")


def test_sqlite_knowledge_store_marks_deleted_sources_stale(tmp_path) -> None:
    store = SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3")
    active = _document("active-doc", KnowledgeSourceType.FILE, "README.md")
    deleted = _document("deleted-doc", KnowledgeSourceType.FILE, "deleted.md")
    adr = _document("adr-doc", KnowledgeSourceType.ADR, "docs/adr/ADR-001.md")

    for document in (active, deleted, adr):
        store.save_document(document)

    store.mark_missing_documents_stale(KnowledgeSourceType.FILE, ("README.md",))

    assert store.load_document("active-doc").freshness == FreshnessStatus.FRESH
    assert store.load_document("deleted-doc").freshness == FreshnessStatus.STALE
    assert store.load_document("adr-doc").freshness == FreshnessStatus.FRESH


def test_sqlite_knowledge_store_lexical_search_returns_fresh_candidates(tmp_path) -> None:
    store = SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3")
    store.save_document(_document())
    store.save_chunks(
        "doc-1",
        (
            KnowledgeChunk(
                "chunk-1",
                "doc-1",
                "install blacksmith locally",
                0,
                3,
                "chunk-hash",
                {"language": "markdown"},
            ),
        ),
    )

    results = store.lexical_search(KnowledgeQuery("blacksmith"))

    assert len(results) == 1
    assert results[0].chunk_id == "chunk-1"
    assert results[0].retrieval_method == "fts5"
    assert results[0].freshness == FreshnessStatus.FRESH


def test_sqlite_knowledge_store_lexical_search_filters_source_and_metadata(tmp_path) -> None:
    store = SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3")
    file_doc = _document("file-doc", KnowledgeSourceType.FILE, "main.py")
    adr_doc = _document("adr-doc", KnowledgeSourceType.ADR, "docs/adr/ADR-001.md")
    store.save_document(file_doc)
    store.save_document(adr_doc)
    store.save_chunks(
        "file-doc",
        (KnowledgeChunk("file-chunk", "file-doc", "blacksmith setup", 0, 2, "hash-1", {"language": "python"}),),
    )
    store.save_chunks(
        "adr-doc",
        (KnowledgeChunk("adr-chunk", "adr-doc", "blacksmith setup", 0, 2, "hash-2", {"language": "markdown"}),),
    )

    results = store.lexical_search(
        KnowledgeQuery(
            "blacksmith",
            (KnowledgeSourceType.FILE,),
            metadata_filters={"language": "python"},
        )
    )

    assert [candidate.chunk_id for candidate in results] == ["file-chunk"]


def test_sqlite_knowledge_store_lexical_search_excludes_stale_chunks(tmp_path) -> None:
    store = SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3")
    store.save_document(_document())
    store.save_chunks("doc-1", (KnowledgeChunk("chunk-1", "doc-1", "blacksmith setup", 0, 2, "hash-1"),))

    store.mark_document_stale("doc-1")

    assert store.lexical_search(KnowledgeQuery("blacksmith")) == ()


def test_sqlite_knowledge_store_lexical_search_quotes_invalid_fts_syntax(tmp_path) -> None:
    store = SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3")
    store.save_document(_document())
    store.save_chunks("doc-1", (KnowledgeChunk("chunk-1", "doc-1", "what is blacksmith?", 0, 3, "hash-1"),))

    assert store.lexical_search(KnowledgeQuery('"blacksmith?"'))[0].chunk_id == "chunk-1"


def test_sqlite_knowledge_store_persists_embeddings(tmp_path) -> None:
    store = SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3")
    embedding = DummyEmbeddingProvider(dimension=4).embed_texts(("blacksmith setup",))[0]
    store.save_document(_document())
    store.save_chunks("doc-1", (KnowledgeChunk("chunk-1", "doc-1", "blacksmith setup", 0, 2, "hash-1"),))

    store.save_embedding("chunk-1", embedding)

    assert store.embeddings_for_chunk("chunk-1") == (embedding,)


def test_sqlite_knowledge_store_semantic_search_returns_fresh_candidates(tmp_path) -> None:
    store = SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3")
    provider = DummyEmbeddingProvider(dimension=4)
    store.save_document(_document())
    store.save_chunks(
        "doc-1",
        (
            KnowledgeChunk("chunk-1", "doc-1", "blacksmith setup", 0, 2, "hash-1"),
            KnowledgeChunk("chunk-2", "doc-1", "unrelated banana", 1, 2, "hash-2"),
        ),
    )
    first, second = provider.embed_texts(("blacksmith setup", "unrelated banana"))
    store.save_embedding("chunk-1", first)
    store.save_embedding("chunk-2", second)

    results = store.semantic_search(provider.embed_texts(("blacksmith setup",))[0], limit=1)

    assert len(results) == 1
    assert results[0].chunk_id == "chunk-1"
    assert results[0].retrieval_method == "semantic"


def test_sqlite_knowledge_store_semantic_search_excludes_stale_and_mismatched_embeddings(
    tmp_path,
) -> None:
    store = SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3")
    provider = DummyEmbeddingProvider(dimension=4)
    other_provider = EmbeddingVector("hash", (1.0, 0.0), "dummy", "other", "v1")
    store.save_document(_document())
    store.save_chunks("doc-1", (KnowledgeChunk("chunk-1", "doc-1", "blacksmith setup", 0, 2, "hash-1"),))
    store.save_embedding("chunk-1", provider.embed_texts(("blacksmith setup",))[0])

    assert store.semantic_search(other_provider) == ()

    store.mark_document_stale("doc-1")
    assert store.semantic_search(provider.embed_texts(("blacksmith setup",))[0]) == ()


def test_sqlite_knowledge_store_semantic_search_rejects_invalid_limit(tmp_path) -> None:
    store = SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3")
    embedding = DummyEmbeddingProvider(dimension=4).embed_texts(("blacksmith setup",))[0]

    with pytest.raises(KnowledgeStoreError, match="limit"):
        store.semantic_search(embedding, limit=0)


def _document(
    document_id: str = "doc-1",
    source_type: KnowledgeSourceType = KnowledgeSourceType.FILE,
    source_uri: str = "README.md",
    freshness: FreshnessStatus = FreshnessStatus.FRESH,
    metadata=None,
) -> KnowledgeDocument:
    return KnowledgeDocument(
        document_id,
        source_type,
        source_uri,
        "v1",
        "doc-hash",
        "Readme",
        {} if metadata is None else metadata,
        freshness,
    )
