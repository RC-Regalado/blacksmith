"""SQLite-backed derived knowledge store."""

import json
import sqlite3
import unicodedata
from pathlib import Path
from math import sqrt

from ai_assistant.domain.errors import KnowledgeStoreError
from ai_assistant.knowledge.domain import (
    EmbeddingVector,
    FreshnessStatus,
    KnowledgeChunk,
    KnowledgeDocument,
    KnowledgeQuery,
    KnowledgeSourceType,
    KnowledgeSymbol,
    RetrievalCandidate,
)
from ai_assistant.knowledge.ports import KnowledgeStore

_FTS_STOPWORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "are",
        "como",
        "de",
        "del",
        "does",
        "el",
        "en",
        "este",
        "esta",
        "hace",
        "how",
        "is",
        "la",
        "los",
        "que",
        "the",
        "this",
        "what",
        "with",
    }
)


class SQLiteKnowledgeStore(KnowledgeStore):
    def __init__(self, database_path: str | Path) -> None:
        self._database_path = Path(database_path)
        self._initialize()

    def save_document(self, document: KnowledgeDocument) -> None:
        try:
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT OR REPLACE INTO knowledge_documents
                    (document_id, source_type, source_uri, source_version,
                     content_hash, title, metadata, freshness)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    _document_to_row(document),
                )
        except sqlite3.Error as exc:
            raise KnowledgeStoreError("Failed to persist knowledge document.") from exc

    def load_document(self, document_id: str) -> KnowledgeDocument | None:
        try:
            with self._connect() as connection:
                row = connection.execute(
                    """
                    SELECT document_id, source_type, source_uri, source_version,
                           content_hash, title, metadata, freshness
                    FROM knowledge_documents WHERE document_id = ?
                    """,
                    (document_id,),
                ).fetchone()
        except sqlite3.Error as exc:
            raise KnowledgeStoreError("Failed to load knowledge document.") from exc
        return None if row is None else _document_from_row(row)

    def list_documents(
        self,
        source_type: KnowledgeSourceType | None = None,
    ) -> tuple[KnowledgeDocument, ...]:
        query = "SELECT document_id, source_type, source_uri, source_version, content_hash, title, metadata, freshness FROM knowledge_documents"
        parameters: tuple[str, ...] = ()
        if source_type is not None:
            query += " WHERE source_type = ?"
            parameters = (KnowledgeSourceType(source_type).value,)
        query += " ORDER BY document_id ASC"
        try:
            with self._connect() as connection:
                rows = connection.execute(query, parameters).fetchall()
        except sqlite3.Error as exc:
            raise KnowledgeStoreError("Failed to list knowledge documents.") from exc
        return tuple(_document_from_row(row) for row in rows)

    def delete_document(self, document_id: str) -> None:
        try:
            with self._connect() as connection:
                connection.execute(
                    "DELETE FROM knowledge_chunks_fts WHERE document_id = ?",
                    (document_id,),
                )
                connection.execute(
                    "DELETE FROM knowledge_documents WHERE document_id = ?",
                    (document_id,),
                )
        except sqlite3.Error as exc:
            raise KnowledgeStoreError("Failed to delete knowledge document.") from exc

    def document_is_current(
        self,
        document_id: str,
        source_version: str,
        content_hash: str,
    ) -> bool:
        try:
            with self._connect() as connection:
                row = connection.execute(
                    """
                    SELECT source_version, content_hash, freshness
                    FROM knowledge_documents WHERE document_id = ?
                    """,
                    (document_id,),
                ).fetchone()
        except sqlite3.Error as exc:
            raise KnowledgeStoreError("Failed to check knowledge document freshness.") from exc
        return row == (source_version, content_hash, FreshnessStatus.FRESH.value)

    def mark_document_stale(self, document_id: str) -> None:
        try:
            with self._connect() as connection:
                _mark_documents_stale(connection, "document_id = ?", (document_id,))
        except sqlite3.Error as exc:
            raise KnowledgeStoreError("Failed to mark knowledge document stale.") from exc

    def mark_missing_documents_stale(
        self,
        source_type: KnowledgeSourceType,
        active_source_uris: tuple[str, ...],
    ) -> None:
        condition = "source_type = ?"
        parameters = (KnowledgeSourceType(source_type).value,)
        if active_source_uris:
            placeholders = ", ".join("?" for _ in active_source_uris)
            condition += f" AND source_uri NOT IN ({placeholders})"
            parameters += tuple(active_source_uris)
        try:
            with self._connect() as connection:
                _mark_documents_stale(connection, condition, parameters)
        except sqlite3.Error as exc:
            raise KnowledgeStoreError("Failed to mark missing knowledge documents stale.") from exc

    def save_chunks(self, document_id: str, chunks: tuple[KnowledgeChunk, ...]) -> None:
        try:
            with self._connect() as connection:
                connection.execute("DELETE FROM knowledge_symbols WHERE document_id = ?", (document_id,))
                connection.execute(
                    """
                    DELETE FROM knowledge_embeddings
                    WHERE chunk_id IN (
                        SELECT chunk_id FROM knowledge_chunks WHERE document_id = ?
                    )
                    """,
                    (document_id,),
                )
                connection.execute("DELETE FROM knowledge_chunks_fts WHERE document_id = ?", (document_id,))
                connection.execute("DELETE FROM knowledge_chunks WHERE document_id = ?", (document_id,))
                connection.executemany(
                    """
                    INSERT INTO knowledge_chunks
                    (chunk_id, document_id, text, ordinal, token_count, content_hash, metadata, freshness)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    [_chunk_to_row(chunk) for chunk in chunks],
                )
                connection.executemany(
                    """
                    INSERT INTO knowledge_chunks_fts (chunk_id, document_id, text, metadata)
                    VALUES (?, ?, ?, ?)
                    """,
                    [_chunk_fts_row(chunk) for chunk in chunks],
                )
        except sqlite3.Error as exc:
            raise KnowledgeStoreError("Failed to persist knowledge chunks.") from exc

    def chunks_for(self, document_id: str) -> tuple[KnowledgeChunk, ...]:
        try:
            with self._connect() as connection:
                rows = connection.execute(
                    """
                    SELECT chunk_id, document_id, text, ordinal, token_count,
                           content_hash, metadata, freshness
                    FROM knowledge_chunks WHERE document_id = ?
                    ORDER BY ordinal ASC, chunk_id ASC
                    """,
                    (document_id,),
                ).fetchall()
        except sqlite3.Error as exc:
            raise KnowledgeStoreError("Failed to load knowledge chunks.") from exc
        return tuple(_chunk_from_row(row) for row in rows)

    def save_symbols(self, document_id: str, symbols: tuple[KnowledgeSymbol, ...]) -> None:
        try:
            with self._connect() as connection:
                connection.execute("DELETE FROM knowledge_symbols WHERE document_id = ?", (document_id,))
                connection.executemany(
                    """
                    INSERT INTO knowledge_symbols
                    (symbol_id, document_id, chunk_id, name, kind, location)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    [_symbol_to_row(symbol) for symbol in symbols],
                )
        except sqlite3.Error as exc:
            raise KnowledgeStoreError("Failed to persist knowledge symbols.") from exc

    def symbols_for(self, document_id: str) -> tuple[KnowledgeSymbol, ...]:
        try:
            with self._connect() as connection:
                rows = connection.execute(
                    """
                    SELECT symbol_id, document_id, chunk_id, name, kind, location
                    FROM knowledge_symbols WHERE document_id = ?
                    ORDER BY symbol_id ASC
                    """,
                    (document_id,),
                ).fetchall()
        except sqlite3.Error as exc:
            raise KnowledgeStoreError("Failed to load knowledge symbols.") from exc
        return tuple(_symbol_from_row(row) for row in rows)

    def lexical_search(self, query: KnowledgeQuery) -> tuple[RetrievalCandidate, ...]:
        try:
            with self._connect() as connection:
                rows = connection.execute(*_lexical_sql(query)).fetchall()
        except sqlite3.Error as exc:
            raise KnowledgeStoreError("Failed to search lexical knowledge index.") from exc
        return tuple(_take_matching_metadata(rows, query))

    def save_embedding(self, chunk_id: str, embedding: EmbeddingVector) -> None:
        try:
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT OR REPLACE INTO knowledge_embeddings
                    (chunk_id, text_hash, provider_id, model, model_version, dimension, values_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    _embedding_to_row(chunk_id, embedding),
                )
        except sqlite3.Error as exc:
            raise KnowledgeStoreError("Failed to persist knowledge embedding.") from exc

    def embeddings_for_chunk(self, chunk_id: str) -> tuple[EmbeddingVector, ...]:
        try:
            with self._connect() as connection:
                rows = connection.execute(
                    """
                    SELECT text_hash, provider_id, model, model_version, dimension, values_json
                    FROM knowledge_embeddings
                    WHERE chunk_id = ?
                    ORDER BY provider_id ASC, model ASC, model_version ASC
                    """,
                    (chunk_id,),
                ).fetchall()
        except sqlite3.Error as exc:
            raise KnowledgeStoreError("Failed to load knowledge embeddings.") from exc
        return tuple(_embedding_from_row(row) for row in rows)

    def semantic_search(
        self,
        embedding: EmbeddingVector,
        limit: int = 10,
    ) -> tuple[RetrievalCandidate, ...]:
        if limit <= 0:
            raise KnowledgeStoreError("semantic search limit must be positive.")
        try:
            with self._connect() as connection:
                rows = connection.execute(
                    """
                    SELECT e.values_json, c.chunk_id, c.document_id, d.source_type,
                           d.source_uri, d.source_version, c.content_hash,
                           c.token_count, c.freshness
                    FROM knowledge_embeddings e
                    JOIN knowledge_chunks c ON c.chunk_id = e.chunk_id
                    JOIN knowledge_documents d ON d.document_id = c.document_id
                    WHERE e.provider_id = ?
                      AND e.model = ?
                      AND e.model_version = ?
                      AND e.dimension = ?
                      AND c.freshness = ?
                      AND d.freshness = ?
                    """,
                    (
                        embedding.provider_id,
                        embedding.model,
                        embedding.model_version,
                        embedding.dimension,
                        FreshnessStatus.FRESH.value,
                        FreshnessStatus.FRESH.value,
                    ),
                ).fetchall()
        except sqlite3.Error as exc:
            raise KnowledgeStoreError("Failed to search semantic knowledge embeddings.") from exc
        return tuple(_semantic_candidates(rows, embedding, limit))

    def clear(self) -> None:
        try:
            with self._connect() as connection:
                connection.execute("DELETE FROM knowledge_symbols")
                connection.execute("DELETE FROM knowledge_embeddings")
                connection.execute("DELETE FROM knowledge_chunks_fts")
                connection.execute("DELETE FROM knowledge_chunks")
                connection.execute("DELETE FROM knowledge_documents")
        except sqlite3.Error as exc:
            raise KnowledgeStoreError("Failed to clear knowledge store.") from exc

    def _initialize(self) -> None:
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with self._connect() as connection:
                _create_schema(connection)
        except sqlite3.Error as exc:
            raise KnowledgeStoreError("Failed to initialize knowledge store.") from exc

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._database_path)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection


def _create_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS knowledge_documents (
            document_id TEXT PRIMARY KEY,
            source_type TEXT NOT NULL,
            source_uri TEXT NOT NULL,
            source_version TEXT NOT NULL,
            content_hash TEXT NOT NULL,
            title TEXT NOT NULL,
            metadata TEXT NOT NULL,
            freshness TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS knowledge_chunks (
            chunk_id TEXT PRIMARY KEY,
            document_id TEXT NOT NULL,
            text TEXT NOT NULL,
            ordinal INTEGER NOT NULL,
            token_count INTEGER NOT NULL,
            content_hash TEXT NOT NULL,
            metadata TEXT NOT NULL,
            freshness TEXT NOT NULL,
            FOREIGN KEY (document_id) REFERENCES knowledge_documents(document_id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_document
            ON knowledge_chunks(document_id, ordinal);
        CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_chunks_fts
            USING fts5(chunk_id UNINDEXED, document_id UNINDEXED, text, metadata UNINDEXED);
        CREATE TABLE IF NOT EXISTS knowledge_embeddings (
            chunk_id TEXT NOT NULL,
            text_hash TEXT NOT NULL,
            provider_id TEXT NOT NULL,
            model TEXT NOT NULL,
            model_version TEXT NOT NULL,
            dimension INTEGER NOT NULL,
            values_json TEXT NOT NULL,
            PRIMARY KEY (chunk_id, provider_id, model, model_version),
            FOREIGN KEY (chunk_id) REFERENCES knowledge_chunks(chunk_id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS knowledge_symbols (
            symbol_id TEXT PRIMARY KEY,
            document_id TEXT NOT NULL,
            chunk_id TEXT NOT NULL,
            name TEXT NOT NULL,
            kind TEXT NOT NULL,
            location TEXT NOT NULL,
            FOREIGN KEY (document_id) REFERENCES knowledge_documents(document_id) ON DELETE CASCADE,
            FOREIGN KEY (chunk_id) REFERENCES knowledge_chunks(chunk_id) ON DELETE CASCADE
        );
        """
    )


def _mark_documents_stale(
    connection: sqlite3.Connection,
    condition: str,
    parameters: tuple[str, ...],
) -> None:
    stale = FreshnessStatus.STALE.value
    document_ids = f"SELECT document_id FROM knowledge_documents WHERE {condition}"
    connection.execute(f"UPDATE knowledge_documents SET freshness = ? WHERE {condition}", (stale, *parameters))
    connection.execute(
        f"UPDATE knowledge_chunks SET freshness = ? WHERE document_id IN ({document_ids})",
        (stale, *parameters),
    )


def _lexical_sql(query: KnowledgeQuery) -> tuple[str, tuple[str, ...]]:
    sql = """
        SELECT c.chunk_id, c.document_id, d.source_type, d.source_uri, d.source_version,
               c.content_hash, c.token_count, c.freshness, c.metadata, bm25(knowledge_chunks_fts) AS rank
        FROM knowledge_chunks_fts
        JOIN knowledge_chunks c ON c.chunk_id = knowledge_chunks_fts.chunk_id
        JOIN knowledge_documents d ON d.document_id = c.document_id
        WHERE knowledge_chunks_fts MATCH ?
          AND c.freshness = ?
          AND d.freshness = ?
    """
    parameters: tuple[str, ...] = (_fts_phrase(query.text), FreshnessStatus.FRESH.value, FreshnessStatus.FRESH.value)
    if query.source_types:
        placeholders = ", ".join("?" for _ in query.source_types)
        sql += f" AND d.source_type IN ({placeholders})"
        parameters += tuple(source_type.value for source_type in query.source_types)
    sql += " ORDER BY rank ASC, c.chunk_id ASC"
    return sql, parameters


def _fts_phrase(text: str) -> str:
    terms = _fts_terms(text)
    if not terms:
        return '"' + text.replace('"', '""') + '"'
    return " OR ".join(f'"{term}"' for term in terms)


def _fts_terms(text: str) -> tuple[str, ...]:
    ascii_text = (
        unicodedata.normalize("NFKD", text.casefold())
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    normalized = "".join(char if char.isalnum() else " " for char in ascii_text)
    seen: set[str] = set()
    terms: list[str] = []
    for token in normalized.split():
        if len(token) < 3 or token in _FTS_STOPWORDS or token in seen:
            continue
        seen.add(token)
        terms.append(token)
    return tuple(terms)


def _candidate_from_row(row: tuple[object, ...]) -> RetrievalCandidate:
    return RetrievalCandidate(
        str(row[0]),
        str(row[1]),
        KnowledgeSourceType(str(row[2])),
        str(row[3]),
        str(row[4]),
        str(row[5]),
        _score(float(row[9])),
        "fts5",
        int(row[6]),
        FreshnessStatus(str(row[7])),
    )


def _take_matching_metadata(
    rows: list[tuple[object, ...]],
    query: KnowledgeQuery,
) -> list[RetrievalCandidate]:
    matched: list[RetrievalCandidate] = []
    for row in rows:
        if _metadata_matches(json.loads(str(row[8])), query):
            matched.append(_candidate_from_row(row))
        if len(matched) >= query.limit:
            break
    return matched


def _metadata_matches(metadata: dict[str, object], query: KnowledgeQuery) -> bool:
    return all(metadata.get(key) == value for key, value in query.metadata_filters.items())


def _score(rank: float) -> float:
    return 1.0 / (1.0 + max(0.0, rank))


def _embedding_to_row(chunk_id: str, embedding: EmbeddingVector) -> tuple[str, str, str, str, str, int, str]:
    return (
        chunk_id,
        embedding.text_hash,
        embedding.provider_id,
        embedding.model,
        embedding.model_version,
        embedding.dimension,
        json.dumps(embedding.values),
    )


def _embedding_from_row(row: tuple[object, ...]) -> EmbeddingVector:
    values = tuple(float(value) for value in json.loads(str(row[5])))
    if int(row[4]) != len(values):
        raise KnowledgeStoreError("Stored embedding dimension does not match values.")
    return EmbeddingVector(str(row[0]), values, str(row[1]), str(row[2]), str(row[3]))


def _semantic_candidates(
    rows: list[tuple[object, ...]],
    embedding: EmbeddingVector,
    limit: int,
) -> list[RetrievalCandidate]:
    scored = [
        (_cosine(embedding.values, tuple(float(value) for value in json.loads(str(row[0])))), row)
        for row in rows
    ]
    scored.sort(key=lambda item: (-item[0], str(item[1][1])))
    return [_semantic_candidate(row, score) for score, row in scored[:limit]]


def _semantic_candidate(row: tuple[object, ...], score: float) -> RetrievalCandidate:
    return RetrievalCandidate(
        str(row[1]),
        str(row[2]),
        KnowledgeSourceType(str(row[3])),
        str(row[4]),
        str(row[5]),
        str(row[6]),
        score,
        "semantic",
        int(row[7]),
        FreshnessStatus(str(row[8])),
    )


def _cosine(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    if len(left) != len(right):
        raise KnowledgeStoreError("Embedding dimension mismatch.")
    left_norm = sqrt(sum(value * value for value in left))
    right_norm = sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return sum(a * b for a, b in zip(left, right, strict=True)) / (left_norm * right_norm)


def _document_to_row(document: KnowledgeDocument) -> tuple[str, str, str, str, str, str, str, str]:
    return (
        document.document_id,
        document.source_type.value,
        document.source_uri,
        document.source_version,
        document.content_hash,
        document.title,
        json.dumps(dict(document.metadata)),
        document.freshness.value,
    )


def _document_from_row(row: tuple[object, ...]) -> KnowledgeDocument:
    return KnowledgeDocument(
        str(row[0]),
        KnowledgeSourceType(str(row[1])),
        str(row[2]),
        str(row[3]),
        str(row[4]),
        str(row[5]),
        json.loads(str(row[6])),
        FreshnessStatus(str(row[7])),
    )


def _chunk_to_row(chunk: KnowledgeChunk) -> tuple[str, str, str, int, int, str, str, str]:
    return (
        chunk.chunk_id,
        chunk.document_id,
        chunk.text,
        chunk.ordinal,
        chunk.token_count,
        chunk.content_hash,
        json.dumps(dict(chunk.metadata)),
        chunk.freshness.value,
    )


def _chunk_fts_row(chunk: KnowledgeChunk) -> tuple[str, str, str, str]:
    return (
        chunk.chunk_id,
        chunk.document_id,
        chunk.text,
        json.dumps(dict(chunk.metadata)),
    )


def _chunk_from_row(row: tuple[object, ...]) -> KnowledgeChunk:
    return KnowledgeChunk(
        str(row[0]),
        str(row[1]),
        str(row[2]),
        int(row[3]),
        int(row[4]),
        str(row[5]),
        json.loads(str(row[6])),
        FreshnessStatus(str(row[7])),
    )


def _symbol_to_row(symbol: KnowledgeSymbol) -> tuple[str, str, str, str, str, str]:
    return (
        symbol.symbol_id,
        symbol.document_id,
        symbol.chunk_id,
        symbol.name,
        symbol.kind,
        symbol.location,
    )


def _symbol_from_row(row: tuple[object, ...]) -> KnowledgeSymbol:
    return KnowledgeSymbol(str(row[0]), str(row[1]), str(row[2]), str(row[3]), str(row[4]), str(row[5]))
