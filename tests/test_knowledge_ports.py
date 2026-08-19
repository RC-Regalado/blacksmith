"""Tests for Phase 5 knowledge source ports."""

from pathlib import Path

import pytest

from ai_assistant.knowledge import (
    AdrKnowledgeSource,
    ConversationKnowledgeSource,
    ExecutionKnowledgeSource,
    FileKnowledgeSource,
    KnowledgeChunk,
    KnowledgeDocument,
    KnowledgeQuery,
    KnowledgeSource,
    KnowledgeSourceType,
    KnowledgeStore,
    KnowledgeSymbol,
)


pytestmark = pytest.mark.unit


def test_knowledge_source_port_is_abstract() -> None:
    for port in (
        KnowledgeSource,
        FileKnowledgeSource,
        AdrKnowledgeSource,
        ExecutionKnowledgeSource,
        ConversationKnowledgeSource,
        KnowledgeStore,
    ):
        with pytest.raises(TypeError):
            port()


def test_fake_file_source_can_implement_port_without_store_access() -> None:
    source = _FakeFileSource()
    query = KnowledgeQuery("readme", (KnowledgeSourceType.FILE,))

    assert source.source_type == KnowledgeSourceType.FILE
    assert source.list_documents(query) == (source.document,)
    assert source.load_document("doc-1") == source.document
    assert source.load_document("missing") is None
    assert source.chunks_for("doc-1") == (source.chunk,)
    assert source.symbols_for("doc-1") == (source.symbol,)


def test_knowledge_ports_have_no_infrastructure_dependency_leaks() -> None:
    forbidden = ("sqlite", "ollama", "protobuf", "toolserver")
    text = Path("ai_assistant/knowledge/ports.py").read_text(encoding="utf-8").lower()
    assert not any(term in text for term in forbidden)


class _FakeFileSource(FileKnowledgeSource):
    document = KnowledgeDocument("doc-1", KnowledgeSourceType.FILE, "README.md", "v1", "hash")
    chunk = KnowledgeChunk("chunk-1", "doc-1", "hello", 0, 1, "chunk-hash")
    symbol = KnowledgeSymbol("sym-1", "doc-1", "chunk-1", "README", "heading")

    def list_documents(self, query=None):
        return (self.document,)

    def load_document(self, document_id):
        return self.document if document_id == self.document.document_id else None

    def chunks_for(self, document_id):
        return (self.chunk,) if document_id == self.document.document_id else ()

    def symbols_for(self, document_id):
        return (self.symbol,) if document_id == self.document.document_id else ()
