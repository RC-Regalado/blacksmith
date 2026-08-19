"""Manual knowledge CLI."""

from fnmatch import fnmatchcase
from pathlib import Path

from ai_assistant.application.errors import ConfigurationError, InvalidToolCallError
from ai_assistant.knowledge import (
    FreshnessStatus,
    KnowledgeDocument,
    KnowledgeQuery,
    KnowledgeSourceType,
    chunk_document,
    hash_text,
    symbols_for_chunks,
)
from ai_assistant.knowledge.ports import KnowledgeStore

_SENSITIVE_PATTERNS = (
    ".env",
    ".env.*",
    "*.pem",
    "*.key",
    "*.p12",
    "*.pfx",
    "id_rsa",
    "id_ed25519",
    "credentials.json",
    "secrets.*",
    "*.kubeconfig",
)


class KnowledgeCli:
    def __init__(
        self,
        store: KnowledgeStore,
        workspace: str | None,
        max_file_bytes: int,
    ) -> None:
        self._store = store
        self._workspace = None if workspace is None else Path(workspace).resolve(strict=True)
        self._max_file_bytes = max_file_bytes

    def run(self, args: tuple[str, ...]) -> None:
        if not args:
            _print_usage()
            return
        command = args[0]
        if command == "status" and len(args) == 1:
            self._status()
        elif command == "index" and len(args) == 2:
            self._index(args[1], clear=False)
        elif command == "rebuild" and len(args) == 2:
            self._index(args[1], clear=True)
        elif command == "query" and len(args) >= 2:
            self._query(" ".join(args[1:]))
        else:
            _print_usage()

    def _status(self) -> None:
        documents = self._store.list_documents()
        chunks = sum(len(self._store.chunks_for(document.document_id)) for document in documents)
        symbols = sum(len(self._store.symbols_for(document.document_id)) for document in documents)
        fresh = sum(document.freshness == FreshnessStatus.FRESH for document in documents)
        print(f"documents={len(documents)} fresh={fresh} chunks={chunks} symbols={symbols}")

    def _index(self, path: str, *, clear: bool) -> None:
        workspace = self._require_workspace()
        if clear:
            self._store.clear()
        files = _files_for(_resolve(workspace, path))
        indexed = skipped = 0
        for file_path in files:
            if self._index_file(workspace, file_path):
                indexed += 1
            else:
                skipped += 1
        print(f"indexed={indexed} skipped={skipped}")

    def _query(self, text: str) -> None:
        for candidate in self._store.lexical_search(KnowledgeQuery(text)):
            print(f"{candidate.chunk_id} {candidate.source_uri} score={candidate.score:.4f}")

    def _index_file(self, workspace: Path, path: Path) -> bool:
        relative = path.relative_to(workspace).as_posix()
        content = _read_text(path, self._max_file_bytes)
        content_hash = hash_text(content)
        version = f"{path.stat().st_mtime_ns}:{path.stat().st_size}"
        document_id = f"file:{relative}"
        if self._store.document_is_current(document_id, version, content_hash):
            return False
        document = KnowledgeDocument(
            document_id,
            KnowledgeSourceType.FILE,
            relative,
            version,
            content_hash,
            path.name,
        )
        chunks = chunk_document(document, content)
        symbols = symbols_for_chunks(document, chunks)
        self._store.save_document(document)
        self._store.save_chunks(document.document_id, chunks)
        self._store.save_symbols(document.document_id, symbols)
        return True

    def _require_workspace(self) -> Path:
        if self._workspace is None:
            raise ConfigurationError("AI_ASSISTANT_WORKSPACE is required for knowledge indexing.")
        return self._workspace


def _resolve(workspace: Path, path: str) -> Path:
    relative = Path(path)
    if relative.is_absolute() or ".." in relative.parts:
        raise InvalidToolCallError("knowledge path must be relative to workspace.")
    _require_allowed_components(relative)
    resolved = (workspace / relative).resolve(strict=True)
    try:
        resolved.relative_to(workspace)
    except ValueError as exc:
        raise InvalidToolCallError("knowledge path escapes workspace.") from exc
    _require_allowed_components(resolved.relative_to(workspace))
    return resolved


def _files_for(path: Path) -> tuple[Path, ...]:
    if path.is_file():
        return (path,)
    if not path.is_dir():
        raise InvalidToolCallError("knowledge path must be a file or directory.")
    return tuple(sorted(item for item in path.rglob("*") if item.is_file() and _allowed_file(item, path)))


def _allowed_file(path: Path, root: Path) -> bool:
    try:
        _require_allowed_components(path.relative_to(root))
    except InvalidToolCallError:
        return False
    return True


def _require_allowed_components(path: Path) -> None:
    for part in path.parts:
        if part in {"", "."}:
            continue
        if part.startswith("."):
            raise InvalidToolCallError("hidden knowledge paths are denied.")
        if any(fnmatchcase(part, pattern) for pattern in _SENSITIVE_PATTERNS):
            raise InvalidToolCallError("sensitive knowledge paths are denied.")


def _read_text(path: Path, max_file_bytes: int) -> str:
    if path.stat().st_size > max_file_bytes:
        raise InvalidToolCallError("knowledge file exceeds max read bytes.")
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise InvalidToolCallError("knowledge file is not valid utf-8.") from exc


def _print_usage() -> None:
    print("Usage: python main.py knowledge status|index PATH|rebuild PATH|query TEXT")
