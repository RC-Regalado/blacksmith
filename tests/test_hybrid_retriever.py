"""Tests for hybrid retrieval."""

import pytest

from ai_assistant.infrastructure.embeddings import DummyEmbeddingProvider
from ai_assistant.infrastructure.storage.sqlite_knowledge import SQLiteKnowledgeStore
from ai_assistant.knowledge import (
    HybridRetriever,
    KnowledgeChunk,
    KnowledgeDocument,
    KnowledgeQuery,
    KnowledgeSourceType,
    KnowledgeSymbol,
)


pytestmark = pytest.mark.unit


def test_hybrid_retriever_merges_lexical_symbol_and_semantic_results(tmp_path) -> None:
    store = SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3")
    provider = DummyEmbeddingProvider(dimension=4)
    document = _document()
    chunk = KnowledgeChunk("chunk-1", "doc-1", "blacksmith setup", 0, 2, "chunk-hash")
    store.save_document(document)
    store.save_chunks("doc-1", (chunk,))
    store.save_symbols("doc-1", (KnowledgeSymbol("sym-1", "doc-1", "chunk-1", "blacksmith", "heading"),))
    store.save_embedding("chunk-1", provider.embed_texts((chunk.text,))[0])

    results = HybridRetriever(store, provider).retrieve(KnowledgeQuery("blacksmith"))

    assert len(results) == 1
    assert results[0].chunk_id == "chunk-1"
    assert results[0].retrieval_method == "fts5+semantic+symbol"


def test_hybrid_retriever_excludes_stale_results(tmp_path) -> None:
    store = SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3")
    provider = DummyEmbeddingProvider(dimension=4)
    store.save_document(_document())
    chunk = KnowledgeChunk("chunk-1", "doc-1", "blacksmith setup", 0, 2, "chunk-hash")
    store.save_chunks("doc-1", (chunk,))
    store.save_symbols("doc-1", (KnowledgeSymbol("sym-1", "doc-1", "chunk-1", "blacksmith", "heading"),))
    store.save_embedding("chunk-1", provider.embed_texts((chunk.text,))[0])

    store.mark_document_stale("doc-1")

    assert HybridRetriever(store, provider).retrieve(KnowledgeQuery("blacksmith")) == ()


def test_hybrid_retriever_respects_query_limit_and_source_filter(tmp_path) -> None:
    store = SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3")
    store.save_document(_document("file-doc", KnowledgeSourceType.FILE, "README.md"))
    store.save_document(_document("adr-doc", KnowledgeSourceType.ADR, "docs/adr/ADR-001.md"))
    store.save_chunks("file-doc", (KnowledgeChunk("file-chunk", "file-doc", "blacksmith", 0, 1, "hash-1"),))
    store.save_chunks("adr-doc", (KnowledgeChunk("adr-chunk", "adr-doc", "blacksmith", 0, 1, "hash-2"),))

    results = HybridRetriever(store).retrieve(KnowledgeQuery("blacksmith", (KnowledgeSourceType.ADR,), 1))

    assert [candidate.chunk_id for candidate in results] == ["adr-chunk"]


def _document(
    document_id: str = "doc-1",
    source_type: KnowledgeSourceType = KnowledgeSourceType.FILE,
    source_uri: str = "README.md",
) -> KnowledgeDocument:
    return KnowledgeDocument(document_id, source_type, source_uri, "v1", "doc-hash")
