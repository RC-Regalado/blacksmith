"""Context and knowledge engine models."""

from ai_assistant.knowledge.domain import (
    CompiledContext,
    ContextBudget,
    ContextEvidence,
    ContextPurpose,
    EmbeddingVector,
    FreshnessStatus,
    KnowledgeChunk,
    KnowledgeDocument,
    KnowledgeQuery,
    KnowledgeSourceType,
    KnowledgeSymbol,
    RetrievalCandidate,
)
from ai_assistant.knowledge.metrics import ContextMetrics, context_metrics
from ai_assistant.knowledge.chunking import (
    ChunkingConfig,
    chunk_document,
    document_metadata,
    infer_language,
    normalize_text,
)
from ai_assistant.knowledge.compiler import ContextCompiler
from ai_assistant.knowledge.hashing import hash_bytes, hash_text
from ai_assistant.knowledge.ports import (
    AdrKnowledgeSource,
    ConversationKnowledgeSource,
    EmbeddingProvider,
    ExecutionKnowledgeSource,
    FileKnowledgeSource,
    KnowledgeSource,
    KnowledgeStore,
)
from ai_assistant.knowledge.planning import PlanningContextProvider, SynthesisContextProvider
from ai_assistant.knowledge.ranking import KnowledgeRanker, RankedCandidate
from ai_assistant.knowledge.retrieval import HybridRetriever
from ai_assistant.knowledge.symbols import symbols_for_chunks

__all__ = [
    "AdrKnowledgeSource",
    "CompiledContext",
    "ChunkingConfig",
    "ContextCompiler",
    "ContextBudget",
    "ContextEvidence",
    "ContextMetrics",
    "ContextPurpose",
    "ConversationKnowledgeSource",
    "EmbeddingProvider",
    "EmbeddingVector",
    "ExecutionKnowledgeSource",
    "FileKnowledgeSource",
    "FreshnessStatus",
    "HybridRetriever",
    "KnowledgeChunk",
    "KnowledgeDocument",
    "KnowledgeQuery",
    "KnowledgeRanker",
    "KnowledgeSource",
    "KnowledgeSourceType",
    "KnowledgeStore",
    "KnowledgeSymbol",
    "PlanningContextProvider",
    "RetrievalCandidate",
    "RankedCandidate",
    "chunk_document",
    "document_metadata",
    "hash_bytes",
    "hash_text",
    "infer_language",
    "normalize_text",
    "context_metrics",
    "symbols_for_chunks",
    "SynthesisContextProvider",
]
