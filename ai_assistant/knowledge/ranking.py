"""Deterministic ranking for retrieved knowledge."""

from dataclasses import dataclass
from types import MappingProxyType

from ai_assistant.knowledge.domain import FreshnessStatus, RetrievalCandidate

_METHOD_WEIGHTS = {
    "symbol": 0.30,
    "fts5": 0.25,
    "semantic": 0.20,
}


@dataclass(frozen=True, slots=True)
class RankedCandidate:
    candidate: RetrievalCandidate
    total_score: float
    components: MappingProxyType[str, float]


class KnowledgeRanker:
    def rank(
        self,
        candidates: tuple[RetrievalCandidate, ...],
        limit: int,
    ) -> tuple[RankedCandidate, ...]:
        if limit <= 0:
            raise ValueError("ranking limit must be positive.")
        ranked = tuple(_rank(candidate) for candidate in candidates if candidate.freshness == FreshnessStatus.FRESH)
        return tuple(sorted(ranked, key=_sort_key)[:limit])


def _rank(candidate: RetrievalCandidate) -> RankedCandidate:
    components = {
        "base": candidate.score,
        "method": _method_score(candidate.retrieval_method),
    }
    return RankedCandidate(
        candidate,
        sum(components.values()),
        MappingProxyType(components),
    )


def _method_score(retrieval_method: str) -> float:
    methods = set(retrieval_method.split("+"))
    return sum(weight for method, weight in _METHOD_WEIGHTS.items() if method in methods)


def _sort_key(item: RankedCandidate) -> tuple[float, str, str]:
    return (-item.total_score, item.candidate.source_uri, item.candidate.chunk_id)
