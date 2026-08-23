"""Compile retrieved knowledge into bounded context."""

from ai_assistant.domain.errors import InvalidKnowledgeError
from ai_assistant.knowledge.domain import (
    CompiledContext,
    ContextBudget,
    ContextEvidence,
    ContextPurpose,
    FreshnessStatus,
    KnowledgeChunk,
)
from ai_assistant.knowledge.ports import KnowledgeStore
from ai_assistant.knowledge.ranking import RankedCandidate


class ContextCompiler:
    def __init__(self, store: KnowledgeStore) -> None:
        self._store = store

    def compile(
        self,
        purpose: ContextPurpose,
        ranked: tuple[RankedCandidate, ...],
        budget: ContextBudget,
    ) -> CompiledContext:
        evidence: list[ContextEvidence] = []
        sources: set[str] = set()
        tokens = 0
        for item in ranked:
            chunk = self._chunk_for(item)
            if not _fits(chunk, item, budget, evidence, sources, tokens):
                continue
            evidence.append(ContextEvidence(item.candidate, chunk.text))
            sources.add(item.candidate.document_id)
            tokens += item.candidate.token_count
        return CompiledContext(purpose, tuple(evidence), budget)

    def compile_conversation_context(
        self,
        ranked: tuple[RankedCandidate, ...],
        budget: ContextBudget,
    ) -> CompiledContext:
        return self.compile(ContextPurpose.CONVERSATION, ranked, budget)

    def _chunk_for(self, item: RankedCandidate) -> KnowledgeChunk:
        for chunk in self._store.chunks_for(item.candidate.document_id):
            if chunk.chunk_id == item.candidate.chunk_id:
                _verify(item, chunk)
                return chunk
        raise InvalidKnowledgeError("retrieval candidate chunk was not found.")


def _verify(item: RankedCandidate, chunk: KnowledgeChunk) -> None:
    candidate = item.candidate
    if candidate.freshness != FreshnessStatus.FRESH or chunk.freshness != FreshnessStatus.FRESH:
        raise InvalidKnowledgeError("compiled context requires fresh knowledge.")
    if candidate.content_hash != chunk.content_hash:
        raise InvalidKnowledgeError("retrieval candidate provenance mismatch.")
    if candidate.token_count != chunk.token_count:
        raise InvalidKnowledgeError("retrieval candidate token count mismatch.")


def _fits(
    chunk: KnowledgeChunk,
    item: RankedCandidate,
    budget: ContextBudget,
    evidence: list[ContextEvidence],
    sources: set[str],
    tokens: int,
) -> bool:
    if item.candidate.token_count > budget.max_chunk_tokens:
        return False
    if len(evidence) >= budget.max_chunks:
        return False
    if tokens + item.candidate.token_count > budget.max_context_tokens:
        return False
    if item.candidate.document_id not in sources and len(sources) >= budget.max_sources:
        return False
    return bool(chunk.text)
