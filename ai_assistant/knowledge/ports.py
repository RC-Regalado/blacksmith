"""Ports for knowledge source adapters."""

from abc import ABC, abstractmethod

from ai_assistant.knowledge.domain import (
    EmbeddingVector,
    KnowledgeChunk,
    KnowledgeDocument,
    KnowledgeQuery,
    KnowledgeSourceType,
    KnowledgeSymbol,
    RetrievalCandidate,
)


class EmbeddingProvider(ABC):
    provider_id: str
    model: str
    model_version: str
    dimension: int

    @abstractmethod
    def embed_texts(self, texts: tuple[str, ...]) -> tuple[EmbeddingVector, ...]:
        raise NotImplementedError


class KnowledgeSource(ABC):
    source_type: KnowledgeSourceType

    @abstractmethod
    def list_documents(self, query: KnowledgeQuery | None = None) -> tuple[KnowledgeDocument, ...]:
        raise NotImplementedError

    @abstractmethod
    def load_document(self, document_id: str) -> KnowledgeDocument | None:
        raise NotImplementedError

    @abstractmethod
    def chunks_for(self, document_id: str) -> tuple[KnowledgeChunk, ...]:
        raise NotImplementedError

    @abstractmethod
    def symbols_for(self, document_id: str) -> tuple[KnowledgeSymbol, ...]:
        raise NotImplementedError


class KnowledgeStore(ABC):
    @abstractmethod
    def save_document(self, document: KnowledgeDocument) -> None:
        raise NotImplementedError

    @abstractmethod
    def load_document(self, document_id: str) -> KnowledgeDocument | None:
        raise NotImplementedError

    @abstractmethod
    def list_documents(
        self,
        source_type: KnowledgeSourceType | None = None,
    ) -> tuple[KnowledgeDocument, ...]:
        raise NotImplementedError

    @abstractmethod
    def delete_document(self, document_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def document_is_current(
        self,
        document_id: str,
        source_version: str,
        content_hash: str,
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    def mark_document_stale(self, document_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def mark_missing_documents_stale(
        self,
        source_type: KnowledgeSourceType,
        active_source_uris: tuple[str, ...],
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def save_chunks(self, document_id: str, chunks: tuple[KnowledgeChunk, ...]) -> None:
        raise NotImplementedError

    @abstractmethod
    def chunks_for(self, document_id: str) -> tuple[KnowledgeChunk, ...]:
        raise NotImplementedError

    @abstractmethod
    def save_symbols(self, document_id: str, symbols: tuple[KnowledgeSymbol, ...]) -> None:
        raise NotImplementedError

    @abstractmethod
    def symbols_for(self, document_id: str) -> tuple[KnowledgeSymbol, ...]:
        raise NotImplementedError

    @abstractmethod
    def lexical_search(self, query: KnowledgeQuery) -> tuple[RetrievalCandidate, ...]:
        raise NotImplementedError

    @abstractmethod
    def save_embedding(self, chunk_id: str, embedding: EmbeddingVector) -> None:
        raise NotImplementedError

    @abstractmethod
    def embeddings_for_chunk(self, chunk_id: str) -> tuple[EmbeddingVector, ...]:
        raise NotImplementedError

    @abstractmethod
    def semantic_search(
        self,
        embedding: EmbeddingVector,
        limit: int = 10,
    ) -> tuple[RetrievalCandidate, ...]:
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        raise NotImplementedError


class FileKnowledgeSource(KnowledgeSource):
    source_type = KnowledgeSourceType.FILE


class AdrKnowledgeSource(KnowledgeSource):
    source_type = KnowledgeSourceType.ADR


class ExecutionKnowledgeSource(KnowledgeSource):
    source_type = KnowledgeSourceType.EXECUTION


class ConversationKnowledgeSource(KnowledgeSource):
    source_type = KnowledgeSourceType.CONVERSATION
