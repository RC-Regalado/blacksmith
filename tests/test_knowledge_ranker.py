"""Tests for deterministic knowledge ranking."""

import pytest

from ai_assistant.knowledge import (
    FreshnessStatus,
    KnowledgeRanker,
    KnowledgeSourceType,
    RetrievalCandidate,
)


pytestmark = pytest.mark.unit


def test_knowledge_ranker_exposes_component_scores_and_total() -> None:
    ranked = KnowledgeRanker().rank((_candidate("chunk-1", "fts5+symbol", 0.5),), limit=1)

    assert ranked[0].total_score == pytest.approx(1.05)
    assert ranked[0].components["base"] == 0.5
    assert ranked[0].components["method"] == pytest.approx(0.55)


def test_knowledge_ranker_is_deterministic_on_ties() -> None:
    candidates = (
        _candidate("chunk-b", "fts5", 0.5, "b.md"),
        _candidate("chunk-a", "fts5", 0.5, "a.md"),
    )

    ranked = KnowledgeRanker().rank(candidates, limit=2)

    assert [item.candidate.chunk_id for item in ranked] == ["chunk-a", "chunk-b"]


def test_knowledge_ranker_excludes_stale_candidates_and_respects_limit() -> None:
    candidates = (
        _candidate("chunk-1", "semantic", 0.7, freshness=FreshnessStatus.STALE),
        _candidate("chunk-2", "symbol", 0.1),
        _candidate("chunk-3", "semantic", 0.7),
    )

    ranked = KnowledgeRanker().rank(candidates, limit=1)

    assert [item.candidate.chunk_id for item in ranked] == ["chunk-3"]


def test_knowledge_ranker_rejects_invalid_limit() -> None:
    with pytest.raises(ValueError, match="limit"):
        KnowledgeRanker().rank((), limit=0)


def _candidate(
    chunk_id: str,
    method: str,
    score: float,
    source_uri: str = "README.md",
    freshness: FreshnessStatus = FreshnessStatus.FRESH,
) -> RetrievalCandidate:
    return RetrievalCandidate(
        chunk_id,
        "doc-1",
        KnowledgeSourceType.FILE,
        source_uri,
        "v1",
        "hash",
        score,
        method,
        1,
        freshness,
    )
