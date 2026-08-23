"""Domain models for derived local knowledge."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType

from ai_assistant.domain.errors import InvalidKnowledgeError


class KnowledgeSourceType(StrEnum):
    FILE = "file"
    ADR = "adr"
    EXECUTION = "execution"
    CONVERSATION = "conversation"


class FreshnessStatus(StrEnum):
    FRESH = "fresh"
    STALE = "stale"
    UNKNOWN = "unknown"


class ContextPurpose(StrEnum):
    PLANNING = "planning"
    SYNTHESIS = "synthesis"
    CONVERSATION = "conversation"


@dataclass(frozen=True, slots=True)
class ContextBudget:
    max_context_tokens: int = 4096
    max_sources: int = 8
    max_chunks: int = 12
    max_chunk_tokens: int = 800

    def __post_init__(self) -> None:
        _require_positive(self.max_context_tokens, "max_context_tokens")
        _require_positive(self.max_sources, "max_sources")
        _require_positive(self.max_chunks, "max_chunks")
        _require_positive(self.max_chunk_tokens, "max_chunk_tokens")


@dataclass(frozen=True, slots=True)
class KnowledgeDocument:
    document_id: str
    source_type: KnowledgeSourceType
    source_uri: str
    source_version: str
    content_hash: str
    title: str = ""
    metadata: Mapping[str, object] = MappingProxyType({})
    freshness: FreshnessStatus = FreshnessStatus.FRESH

    def __post_init__(self) -> None:
        _require_text(self.document_id, "document_id")
        _coerce_enum(self, "source_type", KnowledgeSourceType)
        _require_text(self.source_uri, "source_uri")
        _require_text(self.source_version, "source_version")
        _require_hash(self.content_hash)
        _coerce_enum(self, "freshness", FreshnessStatus)
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@dataclass(frozen=True, slots=True)
class KnowledgeChunk:
    chunk_id: str
    document_id: str
    text: str
    ordinal: int
    token_count: int
    content_hash: str
    metadata: Mapping[str, object] = MappingProxyType({})
    freshness: FreshnessStatus = FreshnessStatus.FRESH

    def __post_init__(self) -> None:
        _require_text(self.chunk_id, "chunk_id")
        _require_text(self.document_id, "document_id")
        _require_text(self.text, "text")
        _require_non_negative(self.ordinal, "ordinal")
        _require_positive(self.token_count, "token_count")
        _require_hash(self.content_hash)
        _coerce_enum(self, "freshness", FreshnessStatus)
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@dataclass(frozen=True, slots=True)
class KnowledgeSymbol:
    symbol_id: str
    document_id: str
    chunk_id: str
    name: str
    kind: str
    location: str = ""

    def __post_init__(self) -> None:
        _require_text(self.symbol_id, "symbol_id")
        _require_text(self.document_id, "document_id")
        _require_text(self.chunk_id, "chunk_id")
        _require_text(self.name, "name")
        _require_text(self.kind, "kind")


@dataclass(frozen=True, slots=True)
class KnowledgeQuery:
    text: str
    source_types: tuple[KnowledgeSourceType, ...] = ()
    limit: int = 10
    metadata_filters: Mapping[str, str] = MappingProxyType({})

    def __post_init__(self) -> None:
        _require_text(self.text, "text")
        _require_positive(self.limit, "limit")
        object.__setattr__(
            self,
            "source_types",
            tuple(KnowledgeSourceType(value) for value in self.source_types),
        )
        filters = dict(self.metadata_filters)
        for key, value in filters.items():
            _require_text(key, "metadata filter key")
            _require_text(value, "metadata filter value")
        object.__setattr__(self, "metadata_filters", MappingProxyType(filters))


@dataclass(frozen=True, slots=True)
class EmbeddingVector:
    text_hash: str
    values: tuple[float, ...]
    provider_id: str
    model: str
    model_version: str

    def __post_init__(self) -> None:
        _require_hash(self.text_hash)
        if not self.values:
            raise InvalidKnowledgeError("embedding values must not be empty.")
        for value in self.values:
            if not isinstance(value, int | float):
                raise InvalidKnowledgeError("embedding values must be numeric.")
        _require_text(self.provider_id, "provider_id")
        _require_text(self.model, "model")
        _require_text(self.model_version, "model_version")

    @property
    def dimension(self) -> int:
        return len(self.values)


@dataclass(frozen=True, slots=True)
class RetrievalCandidate:
    chunk_id: str
    document_id: str
    source_type: KnowledgeSourceType
    source_uri: str
    source_version: str
    content_hash: str
    score: float
    retrieval_method: str
    token_count: int
    freshness: FreshnessStatus = FreshnessStatus.FRESH

    def __post_init__(self) -> None:
        _require_text(self.chunk_id, "chunk_id")
        _require_text(self.document_id, "document_id")
        _coerce_enum(self, "source_type", KnowledgeSourceType)
        _require_text(self.source_uri, "source_uri")
        _require_text(self.source_version, "source_version")
        _require_hash(self.content_hash)
        _require_non_negative(self.score, "score")
        _require_text(self.retrieval_method, "retrieval_method")
        _require_positive(self.token_count, "token_count")
        _coerce_enum(self, "freshness", FreshnessStatus)


@dataclass(frozen=True, slots=True)
class ContextEvidence:
    candidate: RetrievalCandidate
    text: str

    def __post_init__(self) -> None:
        if not isinstance(self.candidate, RetrievalCandidate):
            raise InvalidKnowledgeError("candidate must be a RetrievalCandidate.")
        _require_text(self.text, "text")
        if self.candidate.freshness != FreshnessStatus.FRESH:
            raise InvalidKnowledgeError("context evidence requires fresh knowledge.")


@dataclass(frozen=True, slots=True)
class CompiledContext:
    purpose: ContextPurpose
    evidence: tuple[ContextEvidence, ...]
    budget: ContextBudget = field(default_factory=ContextBudget)

    def __post_init__(self) -> None:
        _coerce_enum(self, "purpose", ContextPurpose)
        evidence = tuple(self.evidence)
        if not isinstance(self.budget, ContextBudget):
            raise InvalidKnowledgeError("budget must be a ContextBudget.")
        _validate_budget(evidence, self.budget)
        object.__setattr__(self, "evidence", evidence)

    @property
    def token_count(self) -> int:
        return sum(item.candidate.token_count for item in self.evidence)


def _validate_budget(evidence: Sequence[ContextEvidence], budget: ContextBudget) -> None:
    if len(evidence) > budget.max_chunks:
        raise InvalidKnowledgeError("compiled context exceeds chunk budget.")
    if len({item.candidate.document_id for item in evidence}) > budget.max_sources:
        raise InvalidKnowledgeError("compiled context exceeds source budget.")
    if sum(item.candidate.token_count for item in evidence) > budget.max_context_tokens:
        raise InvalidKnowledgeError("compiled context exceeds token budget.")
    if any(item.candidate.token_count > budget.max_chunk_tokens for item in evidence):
        raise InvalidKnowledgeError("compiled context exceeds per-chunk budget.")


def _coerce_enum(obj: object, name: str, enum_type) -> None:
    value = getattr(obj, name)
    if isinstance(value, enum_type):
        return
    try:
        object.__setattr__(obj, name, enum_type(value))
    except ValueError as exc:
        raise InvalidKnowledgeError(f"invalid {name}.") from exc


def _require_text(value: str, name: str) -> None:
    if not isinstance(value, str) or not value:
        raise InvalidKnowledgeError(f"{name} must be a non-empty string.")


def _require_hash(value: str) -> None:
    _require_text(value, "content_hash")


def _require_positive(value: int | float, name: str) -> None:
    if value <= 0:
        raise InvalidKnowledgeError(f"{name} must be positive.")


def _require_non_negative(value: int | float, name: str) -> None:
    if value < 0:
        raise InvalidKnowledgeError(f"{name} cannot be negative.")
