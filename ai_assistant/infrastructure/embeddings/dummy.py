"""Deterministic local embedding provider for tests."""

from hashlib import sha256
from math import sqrt

from ai_assistant.domain.errors import InvalidKnowledgeError
from ai_assistant.knowledge import EmbeddingVector, hash_text
from ai_assistant.knowledge.ports import EmbeddingProvider


class DummyEmbeddingProvider(EmbeddingProvider):
    provider_id = "dummy"
    model = "dummy-embedding"
    model_version = "v1"

    def __init__(self, dimension: int = 8) -> None:
        if dimension <= 0:
            raise InvalidKnowledgeError("embedding dimension must be positive.")
        self.dimension = dimension

    def embed_texts(self, texts: tuple[str, ...]) -> tuple[EmbeddingVector, ...]:
        return tuple(self._embed(text) for text in texts)

    def _embed(self, text: str) -> EmbeddingVector:
        if not text:
            raise InvalidKnowledgeError("embedding text must be a non-empty string.")
        values = _normalize(_bucket_text(text, self.dimension))
        return EmbeddingVector(
            hash_text(text),
            values,
            self.provider_id,
            self.model,
            self.model_version,
        )


def _bucket_text(text: str, dimension: int) -> list[float]:
    values = [0.0] * dimension
    for word in text.casefold().split():
        digest = sha256(word.encode("utf-8")).digest()
        for index in range(dimension):
            values[index] += digest[index % len(digest)] / 255.0
    return values


def _normalize(values: list[float]) -> tuple[float, ...]:
    length = sqrt(sum(value * value for value in values))
    if length == 0:
        return tuple(values)
    return tuple(value / length for value in values)
