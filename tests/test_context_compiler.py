"""Tests for context compilation."""

import pytest

from ai_assistant.domain.errors import InvalidKnowledgeError
from ai_assistant.infrastructure.storage.sqlite_knowledge import SQLiteKnowledgeStore
from ai_assistant.knowledge import (
    ContextBudget,
    ContextCompiler,
    ContextPurpose,
    FreshnessStatus,
    KnowledgeChunk,
    KnowledgeDocument,
    KnowledgeSourceType,
    RetrievalCandidate,
)
from ai_assistant.knowledge.ranking import KnowledgeRanker


pytestmark = pytest.mark.unit


def test_context_compiler_builds_bounded_context_with_evidence(tmp_path) -> None:
    store = _store(tmp_path)
    ranked = KnowledgeRanker().rank((_candidate("chunk-1", 2),), 1)

    context = ContextCompiler(store).compile(
        ContextPurpose.PLANNING,
        ranked,
        ContextBudget(max_context_tokens=2, max_sources=1, max_chunks=1, max_chunk_tokens=2),
    )

    assert context.token_count == 2
    assert context.evidence[0].text == "blacksmith setup"
    assert context.evidence[0].candidate.chunk_id == "chunk-1"


def test_context_compiler_skips_candidates_over_budget(tmp_path) -> None:
    store = _store(tmp_path)
    ranked = KnowledgeRanker().rank((_candidate("chunk-1", 2),), 1)

    context = ContextCompiler(store).compile(
        ContextPurpose.SYNTHESIS,
        ranked,
        ContextBudget(max_context_tokens=1, max_sources=1, max_chunks=1, max_chunk_tokens=1),
    )

    assert context.evidence == ()


def test_context_compiler_fails_on_provenance_mismatch(tmp_path) -> None:
    store = _store(tmp_path)
    ranked = KnowledgeRanker().rank((_candidate("chunk-1", 2, content_hash="wrong"),), 1)

    with pytest.raises(InvalidKnowledgeError, match="provenance"):
        ContextCompiler(store).compile(ContextPurpose.PLANNING, ranked, ContextBudget())


def test_context_compiler_fails_on_stale_candidate(tmp_path) -> None:
    store = _store(tmp_path)
    ranked = KnowledgeRanker().rank(
        (_candidate("chunk-1", 2, freshness=FreshnessStatus.STALE),),
        1,
    )

    context = ContextCompiler(store).compile(ContextPurpose.PLANNING, ranked, ContextBudget())

    assert context.evidence == ()


def test_context_compiler_builds_distinct_conversation_context(tmp_path) -> None:
    store = _store(tmp_path)
    ranked = KnowledgeRanker().rank((_candidate("chunk-1", 2),), 1)

    context = ContextCompiler(store).compile_conversation_context(ranked, ContextBudget())

    assert context.purpose == ContextPurpose.CONVERSATION
    assert context.evidence[0].candidate.chunk_id == "chunk-1"
    assert context.evidence[0].text == "blacksmith setup"


def _store(tmp_path) -> SQLiteKnowledgeStore:
    store = SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3")
    store.save_document(KnowledgeDocument("doc-1", KnowledgeSourceType.FILE, "README.md", "v1", "doc-hash"))
    store.save_chunks("doc-1", (KnowledgeChunk("chunk-1", "doc-1", "blacksmith setup", 0, 2, "chunk-hash"),))
    return store


def _candidate(
    chunk_id: str,
    token_count: int,
    *,
    content_hash: str = "chunk-hash",
    freshness: FreshnessStatus = FreshnessStatus.FRESH,
) -> RetrievalCandidate:
    return RetrievalCandidate(
        chunk_id,
        "doc-1",
        KnowledgeSourceType.FILE,
        "README.md",
        "v1",
        content_hash,
        1.0,
        "fts5",
        token_count,
        freshness,
    )
