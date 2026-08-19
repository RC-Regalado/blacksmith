"""Symbol extraction from derived knowledge chunks."""

from ai_assistant.knowledge.domain import KnowledgeChunk, KnowledgeDocument, KnowledgeSymbol
from ai_assistant.knowledge.hashing import hash_text


def symbols_for_chunks(
    document: KnowledgeDocument,
    chunks: tuple[KnowledgeChunk, ...],
) -> tuple[KnowledgeSymbol, ...]:
    symbols: list[KnowledgeSymbol] = []
    seen: set[tuple[str, str, str]] = set()
    for chunk in chunks:
        name = _metadata_text(chunk, "symbol_name")
        kind = _metadata_text(chunk, "symbol_kind")
        if not name or not kind:
            continue
        key = (chunk.chunk_id, kind, name)
        if key in seen:
            continue
        seen.add(key)
        symbols.append(
            KnowledgeSymbol(
                f"{document.document_id}:{kind}:{hash_text(chunk.chunk_id + name)[:12]}",
                document.document_id,
                chunk.chunk_id,
                name,
                kind,
                _metadata_text(chunk, "source_uri") or document.source_uri,
            )
        )
    return tuple(symbols)


def _metadata_text(chunk: KnowledgeChunk, key: str) -> str:
    value = chunk.metadata.get(key)
    return value if isinstance(value, str) else ""
