"""Tests for Phase 5 embedding provider contract."""

from pathlib import Path

import pytest

from ai_assistant.domain.errors import InvalidKnowledgeError
from ai_assistant.infrastructure.embeddings import DummyEmbeddingProvider
from ai_assistant.knowledge import EmbeddingProvider, EmbeddingVector, hash_text


pytestmark = pytest.mark.unit


def test_embedding_vector_validates_metadata_and_dimension() -> None:
    vector = EmbeddingVector("hash", (1.0, 0.0), "dummy", "model", "v1")

    assert vector.dimension == 2

    with pytest.raises(InvalidKnowledgeError, match="embedding values"):
        EmbeddingVector("hash", (), "dummy", "model", "v1")


def test_dummy_embedding_provider_is_deterministic_and_local() -> None:
    provider = DummyEmbeddingProvider(dimension=4)

    first = provider.embed_texts(("Blacksmith local knowledge",))[0]
    second = provider.embed_texts(("Blacksmith local knowledge",))[0]

    assert first == second
    assert first.text_hash == hash_text("Blacksmith local knowledge")
    assert first.dimension == 4
    assert first.provider_id == "dummy"


def test_dummy_embedding_provider_changes_with_text() -> None:
    provider = DummyEmbeddingProvider(dimension=4)

    left, right = provider.embed_texts(("alpha", "beta"))

    assert left.values != right.values


def test_embedding_provider_rejects_invalid_input() -> None:
    with pytest.raises(InvalidKnowledgeError, match="dimension"):
        DummyEmbeddingProvider(0)
    with pytest.raises(InvalidKnowledgeError, match="non-empty"):
        DummyEmbeddingProvider().embed_texts(("",))


def test_embedding_provider_is_separate_from_model_provider() -> None:
    text = Path("ai_assistant/infrastructure/embeddings/dummy.py").read_text(encoding="utf-8")
    assert "ModelProvider" not in text
    assert "ModelAdapter" not in text

    with pytest.raises(TypeError):
        EmbeddingProvider()
