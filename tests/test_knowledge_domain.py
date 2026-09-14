"""Tests for Phase 5 knowledge domain models."""

from pathlib import Path

import pytest

from ai_assistant.domain.errors import InvalidKnowledgeError
from ai_assistant.knowledge import (
    CompiledContext,
    ContextBudget,
    ContextEvidence,
    ContextPurpose,
    FreshnessStatus,
    KnowledgeChunk,
    KnowledgeDocument,
    KnowledgeQuery,
    KnowledgeSourceType,
    KnowledgeSymbol,
    RetrievalCandidate,
)


pytestmark = pytest.mark.unit


def test_knowledge_domain_models_are_immutable_and_importable() -> None:
    document = KnowledgeDocument("doc-1", "file", "README.md", "v1", "hash")
    chunk = KnowledgeChunk("chunk-1", document.document_id, "hello", 0, 1, "chunk-hash")
    symbol = KnowledgeSymbol("sym-1", document.document_id, chunk.chunk_id, "main", "function")
    query = KnowledgeQuery("hello", ("file",), limit=3)

    assert document.source_type == KnowledgeSourceType.FILE
    assert chunk.freshness == FreshnessStatus.FRESH
    assert symbol.name == "main"
    assert query.source_types == (KnowledgeSourceType.FILE,)


def test_compiled_context_requires_fresh_provenance_and_budget() -> None:
    candidate = _candidate("chunk-1", token_count=10)
    context = CompiledContext(
        ContextPurpose.PLANNING,
        (ContextEvidence(candidate, "fresh text"),),
        ContextBudget(max_context_tokens=10, max_sources=1, max_chunks=1, max_chunk_tokens=10),
    )

    assert context.token_count == 10

    with pytest.raises(InvalidKnowledgeError, match="fresh knowledge"):
        ContextEvidence(_candidate("chunk-2", freshness=FreshnessStatus.STALE), "stale")
    with pytest.raises(InvalidKnowledgeError, match="token budget"):
        CompiledContext(
            ContextPurpose.SYNTHESIS,
            (ContextEvidence(_candidate("chunk-3", token_count=11), "too large"),),
            ContextBudget(max_context_tokens=10),
        )
    with pytest.raises(InvalidKnowledgeError, match="per-chunk"):
        CompiledContext(
            ContextPurpose.SYNTHESIS,
            (ContextEvidence(_candidate("chunk-4", token_count=9), "too large"),),
            ContextBudget(max_context_tokens=10, max_chunk_tokens=8),
        )


def test_knowledge_domain_fails_explicitly() -> None:
    with pytest.raises(InvalidKnowledgeError, match="document_id"):
        KnowledgeDocument("", KnowledgeSourceType.FILE, "README.md", "v1", "hash")
    with pytest.raises(InvalidKnowledgeError, match="limit"):
        KnowledgeQuery("hello", limit=0)
    with pytest.raises(InvalidKnowledgeError, match="score"):
        _candidate("chunk-1", score=-1)
    with pytest.raises(InvalidKnowledgeError, match="metadata filter"):
        KnowledgeQuery("hello", metadata_filters={"": "python"})


def test_knowledge_domain_has_no_infrastructure_dependency_leaks() -> None:
    forbidden = ("sqlite", "ollama", "protobuf", "toolserver")
    for path in Path("ai_assistant/knowledge").glob("*.py"):
        text = path.read_text(encoding="utf-8").lower()
        assert not any(term in text for term in forbidden), path


def _candidate(
    chunk_id: str,
    *,
    score: float = 1.0,
    token_count: int = 1,
    freshness: FreshnessStatus = FreshnessStatus.FRESH,
) -> RetrievalCandidate:
    return RetrievalCandidate(
        chunk_id,
        "doc-1",
        KnowledgeSourceType.FILE,
        "README.md",
        "v1",
        "hash",
        score,
        "lexical",
        token_count,
        freshness,
    )
