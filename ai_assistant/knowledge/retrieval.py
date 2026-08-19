"""Hybrid retrieval over derived knowledge."""

from dataclasses import replace

from ai_assistant.knowledge.domain import (
    FreshnessStatus,
    KnowledgeChunk,
    KnowledgeDocument,
    KnowledgeQuery,
    RetrievalCandidate,
)
from ai_assistant.knowledge.ports import EmbeddingProvider, KnowledgeStore


class HybridRetriever:
    def __init__(
        self,
        store: KnowledgeStore,
        embedding_provider: EmbeddingProvider | None = None,
    ) -> None:
        self._store = store
        self._embedding_provider = embedding_provider

    def retrieve(self, query: KnowledgeQuery) -> tuple[RetrievalCandidate, ...]:
        candidates = [
            *self._store.lexical_search(query),
            *self._symbol_search(query),
            *self._semantic_search(query),
        ]
        return tuple(_deduplicate(candidates, query.limit))

    def _semantic_search(self, query: KnowledgeQuery) -> tuple[RetrievalCandidate, ...]:
        if self._embedding_provider is None:
            return ()
        embedding = self._embedding_provider.embed_texts((query.text,))[0]
        return self._store.semantic_search(embedding, query.limit)

    def _symbol_search(self, query: KnowledgeQuery) -> tuple[RetrievalCandidate, ...]:
        matches: list[RetrievalCandidate] = []
        for document in self._documents(query):
            chunks = {chunk.chunk_id: chunk for chunk in self._store.chunks_for(document.document_id)}
            for symbol in self._store.symbols_for(document.document_id):
                chunk = chunks.get(symbol.chunk_id)
                if chunk is None or chunk.freshness != FreshnessStatus.FRESH:
                    continue
                if query.text.casefold() not in f"{symbol.name} {symbol.kind}".casefold():
                    continue
                matches.append(_symbol_candidate(document, chunk))
        return tuple(matches[: query.limit])

    def _documents(self, query: KnowledgeQuery) -> tuple[KnowledgeDocument, ...]:
        if query.source_types:
            documents = tuple(
                document
                for source_type in query.source_types
                for document in self._store.list_documents(source_type)
            )
        else:
            documents = self._store.list_documents()
        return tuple(document for document in documents if document.freshness == FreshnessStatus.FRESH)


def _symbol_candidate(document: KnowledgeDocument, chunk: KnowledgeChunk) -> RetrievalCandidate:
    return RetrievalCandidate(
        chunk.chunk_id,
        document.document_id,
        document.source_type,
        document.source_uri,
        document.source_version,
        chunk.content_hash,
        1.0,
        "symbol",
        chunk.token_count,
        chunk.freshness,
    )


def _deduplicate(
    candidates: list[RetrievalCandidate],
    limit: int,
) -> list[RetrievalCandidate]:
    merged: dict[str, RetrievalCandidate] = {}
    for candidate in candidates:
        if candidate.freshness != FreshnessStatus.FRESH:
            continue
        existing = merged.get(candidate.chunk_id)
        if existing is None:
            merged[candidate.chunk_id] = candidate
        else:
            merged[candidate.chunk_id] = _merge(existing, candidate)
    return sorted(merged.values(), key=lambda item: (-item.score, item.chunk_id))[:limit]


def _merge(left: RetrievalCandidate, right: RetrievalCandidate) -> RetrievalCandidate:
    score = max(left.score, right.score)
    method = "+".join(sorted(set(left.retrieval_method.split("+") + right.retrieval_method.split("+"))))
    return replace(left, score=score, retrieval_method=method)
