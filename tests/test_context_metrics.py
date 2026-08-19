"""Tests for context efficiency metrics."""

import pytest

from ai_assistant.knowledge import (
    CompiledContext,
    ContextBudget,
    ContextEvidence,
    ContextMetrics,
    ContextPurpose,
    KnowledgeSourceType,
    RetrievalCandidate,
    context_metrics,
)
from ai_assistant.knowledge.ranking import RankedCandidate


pytestmark = pytest.mark.unit


def test_context_metrics_reports_reduction_ratio() -> None:
    selected = _candidate("chunk-1", 2)
    omitted = _candidate("chunk-2", 6)
    context = CompiledContext(
        ContextPurpose.PLANNING,
        (ContextEvidence(selected, "selected text"),),
        ContextBudget(),
    )

    metrics = context_metrics(
        ContextPurpose.PLANNING,
        (selected, omitted),
        (RankedCandidate(selected, 1.0, {}),),
        context,
    )

    assert metrics.knowledge_candidates == 2
    assert metrics.knowledge_chunks_selected == 1
    assert metrics.raw_context_estimated_tokens == 8
    assert metrics.compiled_context_estimated_tokens == 2
    assert metrics.context_reduction_ratio == 0.75


def test_empty_context_metrics_has_zero_reduction() -> None:
    metrics = ContextMetrics(ContextPurpose.SYNTHESIS, 0, 0, 0, 0, 0)

    assert metrics.context_reduction_ratio == 0.0


def _candidate(chunk_id: str, tokens: int) -> RetrievalCandidate:
    return RetrievalCandidate(
        chunk_id,
        "doc-1",
        KnowledgeSourceType.FILE,
        "README.md",
        "v1",
        f"{chunk_id}-hash",
        1.0,
        "fts5",
        tokens,
    )
