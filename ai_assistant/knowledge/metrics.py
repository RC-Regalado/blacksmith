"""Lightweight context efficiency metrics."""

from dataclasses import dataclass

from ai_assistant.knowledge.domain import CompiledContext, ContextPurpose, RetrievalCandidate
from ai_assistant.knowledge.ranking import RankedCandidate


@dataclass(frozen=True, slots=True)
class ContextMetrics:
    purpose: ContextPurpose
    knowledge_candidates: int
    knowledge_chunks_selected: int
    raw_context_estimated_tokens: int
    compiled_context_estimated_tokens: int
    ranked_candidates: int
    lexical_candidates: int = 0
    symbol_candidates: int = 0
    semantic_candidates: int = 0
    merged_candidates: int = 0
    selected_candidates: int = 0
    unique_sources_selected: int = 0

    @property
    def context_reduction_ratio(self) -> float:
        if self.raw_context_estimated_tokens <= 0:
            return 0.0
        reduction = 1.0 - (
            self.compiled_context_estimated_tokens / self.raw_context_estimated_tokens
        )
        return max(0.0, reduction)


def context_metrics(
    purpose: ContextPurpose,
    candidates: tuple[RetrievalCandidate, ...],
    ranked: tuple[RankedCandidate, ...],
    context: CompiledContext,
) -> ContextMetrics:
    return ContextMetrics(
        purpose=purpose,
        knowledge_candidates=len(candidates),
        knowledge_chunks_selected=len(context.evidence),
        raw_context_estimated_tokens=sum(candidate.token_count for candidate in candidates),
        compiled_context_estimated_tokens=context.token_count,
        ranked_candidates=len(ranked),
        lexical_candidates=_method_count(candidates, "fts5"),
        symbol_candidates=_method_count(candidates, "symbol"),
        semantic_candidates=_method_count(candidates, "semantic"),
        merged_candidates=len(candidates),
        selected_candidates=len(context.evidence),
        unique_sources_selected=len(
            {item.candidate.document_id for item in context.evidence}
        ),
    )


def _method_count(candidates: tuple[RetrievalCandidate, ...], method: str) -> int:
    return sum(
        1 for candidate in candidates if method in candidate.retrieval_method.split("+")
    )
