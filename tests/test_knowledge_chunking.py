"""Tests for knowledge normalization and chunking."""

import pytest

from ai_assistant.domain.errors import InvalidKnowledgeError
from ai_assistant.knowledge import (
    ChunkingConfig,
    KnowledgeDocument,
    KnowledgeSourceType,
    chunk_document,
    document_metadata,
    infer_language,
    normalize_text,
)


pytestmark = pytest.mark.unit


def test_normalize_text_removes_trailing_space_and_extra_blank_lines() -> None:
    assert normalize_text("a  \r\n\r\n\r\nb\t") == "a\n\nb"


def test_chunk_document_splits_markdown_by_heading_and_budget() -> None:
    document = _document("README.md")
    chunks = chunk_document(document, "# A\none two three\n## B\nfour five six", ChunkingConfig(3))

    assert [chunk.ordinal for chunk in chunks] == [0, 1, 2, 3]
    assert chunks[0].metadata["section"] == "A"
    assert chunks[0].metadata["language"] == "markdown"
    assert chunks[0].metadata["source_uri"] == "README.md"
    assert chunks[2].metadata["section"] == "B"
    assert all(chunk.token_count <= 3 for chunk in chunks)


def test_chunk_document_uses_python_top_level_symbols_when_possible() -> None:
    document = _document("main.py")
    chunks = chunk_document(document, "import os\n\nclass App:\n    pass\n\ndef main():\n    pass")

    assert [chunk.metadata["section"] for chunk in chunks] == [
        "module",
        "ClassDef:App",
        "FunctionDef:main",
    ]
    assert chunks[1].metadata["symbol_kind"] == "class"
    assert chunks[1].metadata["symbol_name"] == "App"
    assert chunks[2].metadata["symbol_kind"] == "function"


def test_chunk_document_falls_back_to_bounded_word_chunks() -> None:
    document = _document("notes.txt")
    chunks = chunk_document(document, "one two three four five", ChunkingConfig(2, overlap_tokens=1))

    assert [chunk.text for chunk in chunks] == ["one two", "two three", "three four", "four five", "five"]


def test_chunking_config_rejects_invalid_budget() -> None:
    with pytest.raises(InvalidKnowledgeError, match="max_tokens"):
        ChunkingConfig(0)
    with pytest.raises(InvalidKnowledgeError, match="overlap_tokens"):
        ChunkingConfig(2, 2)


def test_document_metadata_infers_language_and_provenance() -> None:
    document = _document("script.py")

    assert document_metadata(document) == {
        "source_uri": "script.py",
        "source_type": "file",
        "source_version": "v1",
        "document_hash": "hash",
        "language": "python",
    }
    assert infer_language("README.md") == "markdown"
    assert infer_language("unknown.bin") == "text"


def _document(source_uri: str) -> KnowledgeDocument:
    return KnowledgeDocument("doc-1", KnowledgeSourceType.FILE, source_uri, "v1", "hash")
