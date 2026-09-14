"""Normalization and chunking for derived knowledge."""

import ast
from dataclasses import dataclass

from ai_assistant.domain.errors import InvalidKnowledgeError
from ai_assistant.knowledge.domain import KnowledgeChunk, KnowledgeDocument
from ai_assistant.knowledge.hashing import hash_text


@dataclass(frozen=True, slots=True)
class ChunkingConfig:
    max_tokens: int = 200
    overlap_tokens: int = 0

    def __post_init__(self) -> None:
        if self.max_tokens <= 0:
            raise InvalidKnowledgeError("max_tokens must be positive.")
        if self.overlap_tokens < 0 or self.overlap_tokens >= self.max_tokens:
            raise InvalidKnowledgeError("overlap_tokens must be smaller than max_tokens.")


def normalize_text(content: str) -> str:
    lines = content.replace("\r\n", "\n").replace("\r", "\n").expandtabs(4).split("\n")
    cleaned: list[str] = []
    blank = False
    for line in lines:
        stripped = line.rstrip()
        if stripped:
            cleaned.append(stripped)
            blank = False
        elif not blank:
            cleaned.append("")
            blank = True
    return "\n".join(cleaned).strip()


def chunk_document(
    document: KnowledgeDocument,
    content: str,
    config: ChunkingConfig = ChunkingConfig(),
) -> tuple[KnowledgeChunk, ...]:
    normalized = normalize_text(content)
    if not normalized:
        return ()
    chunks: list[KnowledgeChunk] = []
    base_metadata = document_metadata(document)
    for label, text in _units(document.source_uri, normalized):
        metadata = _unit_metadata(label, base_metadata)
        for piece in _bounded_chunks(text, config):
            chunks.append(_chunk(document.document_id, piece, len(chunks), metadata))
    return tuple(chunks)


def document_metadata(document: KnowledgeDocument) -> dict[str, str]:
    return {
        "source_uri": document.source_uri,
        "source_type": document.source_type.value,
        "source_version": document.source_version,
        "document_hash": document.content_hash,
        "language": infer_language(document.source_uri),
    }


def infer_language(source_uri: str) -> str:
    suffix = source_uri.rsplit(".", 1)[-1].lower() if "." in source_uri else ""
    return {
        "md": "markdown",
        "markdown": "markdown",
        "py": "python",
        "txt": "text",
    }.get(suffix, "text")


def _units(source_uri: str, text: str) -> tuple[tuple[str, str], ...]:
    if source_uri.endswith(".py"):
        python_units = _python_units(text)
        if python_units:
            return python_units
    markdown_units = _markdown_units(text)
    if markdown_units:
        return markdown_units
    return tuple(("", paragraph) for paragraph in text.split("\n\n") if paragraph.strip())


def _unit_metadata(label: str, base_metadata: dict[str, str]) -> dict[str, str]:
    metadata = dict(base_metadata)
    if not label:
        return metadata
    metadata["section"] = label
    if ":" in label:
        symbol_kind, symbol_name = label.split(":", 1)
        metadata["symbol_kind"] = _symbol_kind(symbol_kind)
        metadata["symbol_name"] = symbol_name
    elif metadata["language"] == "markdown":
        metadata["symbol_kind"] = "heading"
        metadata["symbol_name"] = label
    return metadata


def _symbol_kind(value: str) -> str:
    return {
        "ClassDef": "class",
        "FunctionDef": "function",
        "AsyncFunctionDef": "function",
    }.get(value, value.lower())


def _python_units(text: str) -> tuple[tuple[str, str], ...]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return ()
    lines = text.splitlines()
    nodes = [node for node in tree.body if isinstance(node, ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef)]
    if not nodes:
        return ()
    units = _leading_unit(lines, nodes[0].lineno)
    for node in nodes:
        end = getattr(node, "end_lineno", node.lineno)
        units.append((f"{type(node).__name__}:{node.name}", "\n".join(lines[node.lineno - 1 : end])))
    return tuple(units)


def _leading_unit(lines: list[str], first_lineno: int) -> list[tuple[str, str]]:
    prefix = "\n".join(lines[: first_lineno - 1]).strip()
    return [] if not prefix else [("module", prefix)]


def _markdown_units(text: str) -> tuple[tuple[str, str], ...]:
    units: list[tuple[str, str]] = []
    current_title = ""
    current_lines: list[str] = []
    for line in text.splitlines():
        if line.startswith("#"):
            _append_unit(units, current_title, current_lines)
            current_title = line.lstrip("#").strip()
            current_lines = [line]
        else:
            current_lines.append(line)
    _append_unit(units, current_title, current_lines)
    return tuple(units)


def _append_unit(units: list[tuple[str, str]], title: str, lines: list[str]) -> None:
    text = "\n".join(lines).strip()
    if text:
        units.append((title, text))


def _bounded_chunks(text: str, config: ChunkingConfig) -> tuple[str, ...]:
    words = text.split()
    if len(words) <= config.max_tokens:
        return (text,)
    step = config.max_tokens - config.overlap_tokens
    return tuple(" ".join(words[index : index + config.max_tokens]) for index in range(0, len(words), step))


def _chunk(
    document_id: str,
    text: str,
    ordinal: int,
    metadata: dict[str, str],
) -> KnowledgeChunk:
    return KnowledgeChunk(
        f"{document_id}:{ordinal}:{hash_text(text)[:12]}",
        document_id,
        text,
        ordinal,
        len(text.split()),
        hash_text(text),
        metadata,
    )
