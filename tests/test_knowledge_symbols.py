"""Tests for derived knowledge symbols."""

import pytest

from ai_assistant.knowledge import (
    KnowledgeDocument,
    KnowledgeSourceType,
    chunk_document,
    symbols_for_chunks,
)


pytestmark = pytest.mark.unit


def test_symbols_for_chunks_extracts_python_symbols() -> None:
    document = _document("main.py")
    chunks = chunk_document(document, "class App:\n    pass\n\ndef main():\n    pass")

    symbols = symbols_for_chunks(document, chunks)

    assert [(symbol.name, symbol.kind, symbol.location) for symbol in symbols] == [
        ("App", "class", "main.py"),
        ("main", "function", "main.py"),
    ]
    assert all(symbol.document_id == document.document_id for symbol in symbols)


def test_symbols_for_chunks_extracts_markdown_headings() -> None:
    document = _document("README.md")
    chunks = chunk_document(document, "# Install\nRun setup")

    symbols = symbols_for_chunks(document, chunks)

    assert len(symbols) == 1
    assert symbols[0].name == "Install"
    assert symbols[0].kind == "heading"


def test_symbols_for_chunks_ignores_chunks_without_symbol_metadata() -> None:
    document = _document("notes.txt")
    chunks = chunk_document(document, "plain text")

    assert symbols_for_chunks(document, chunks) == ()


def _document(source_uri: str) -> KnowledgeDocument:
    return KnowledgeDocument("doc-1", KnowledgeSourceType.FILE, source_uri, "v1", "hash")
