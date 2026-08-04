"""Local read-only tool executor.

Binary reads are returned as UTF-8 text with replacement characters. `bytes_read`
always reports raw bytes, not decoded character count.
"""

import json
import os
import re
import shutil
import stat
import subprocess
from fnmatch import fnmatchcase
from pathlib import Path

from ai_assistant.application.path_policy import WorkspacePathPolicy
from ai_assistant.application.ports.tools import ToolExecutor
from ai_assistant.application.tool_catalog import (
    FILE_METADATA,
    GIT_STATUS,
    LIST_DIRECTORY,
    READ_FILE,
    SEARCH_TEXT,
    StaticToolCatalog,
)
from ai_assistant.domain.tools import (
    SanitizedToolError,
    ToolExecutionContext,
    ToolExecutionResult,
    ToolExecutionStatus,
)

_MAX_RESPONSE_BYTES = 1_048_576
_RG = "rg"
_GIT = "git"
_SENSITIVE_GLOBS = (
    "!.env",
    "!.env.*",
    "!*.pem",
    "!*.key",
    "!*.p12",
    "!*.pfx",
    "!id_rsa",
    "!id_ed25519",
    "!credentials.json",
    "!secrets.*",
    "!*.kubeconfig",
)
_SECRET_RE = re.compile(r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*\S+")


class LocalReadOnlyToolExecutor(ToolExecutor):
    def __init__(self) -> None:
        self._catalog = StaticToolCatalog()

    def execute(self, context: ToolExecutionContext) -> ToolExecutionResult:
        try:
            checked = self._validate_again(context)
            if checked.request.tool_name == FILE_METADATA:
                return _file_metadata(checked)
            if checked.request.tool_name == SEARCH_TEXT:
                return _search_text(checked)
            if checked.request.tool_name == GIT_STATUS:
                return _git_status(checked)
            if checked.request.tool_name == READ_FILE:
                return _read_file(checked)
            if checked.request.tool_name == LIST_DIRECTORY:
                return _list_directory(checked)
            return _error(checked, "unknown_tool", "Unknown tool.")
        except Exception as exc:  # noqa: BLE001 - executor returns sanitized errors.
            return ToolExecutionResult(
                request_id=context.request.request_id,
                tool_name=context.request.tool_name,
                status=ToolExecutionStatus.ERROR,
                error=SanitizedToolError(
                    code="local_executor_error",
                    message=str(exc) or "Local tool execution failed.",
                ),
            )

    def _validate_again(self, context: ToolExecutionContext) -> ToolExecutionContext:
        definition = self._catalog.definition_for(context.request.tool_name)
        return WorkspacePathPolicy(context.workspace_id).validate(
            context.request,
            definition,
        )


def _read_file(context: ToolExecutionContext) -> ToolExecutionResult:
    path = _resolved_path(context)
    offset = int(context.request.arguments.get("offset", 0))
    max_bytes = min(int(context.request.arguments.get("max_bytes", 16384)), 65536)
    with path.open("rb") as handle:
        handle.seek(max(offset, 0))
        data = handle.read(max_bytes + 1)
    truncated = len(data) > max_bytes
    data = data[:max_bytes]
    return ToolExecutionResult(
        request_id=context.request.request_id,
        tool_name=context.request.tool_name,
        status=ToolExecutionStatus.SUCCESS,
        content={
            "path": context.relative_path,
            "content": data.decode("utf-8", errors="replace"),
            "bytes_read": len(data),
            "truncated": truncated,
        },
        truncated=truncated,
    )


def _file_metadata(context: ToolExecutionContext) -> ToolExecutionResult:
    path = _resolved_path(context)
    info = path.stat()
    return ToolExecutionResult(
        request_id=context.request.request_id,
        tool_name=context.request.tool_name,
        status=ToolExecutionStatus.SUCCESS,
        content={
            "path": context.relative_path,
            "type": "directory" if path.is_dir() else "file",
            "size": None if path.is_dir() else info.st_size,
            "modified_at": int(info.st_mtime),
        },
    )


def _list_directory(context: ToolExecutionContext) -> ToolExecutionResult:
    path = _resolved_path(context)
    max_entries = min(int(context.request.arguments.get("max_entries", 200)), 1000)
    max_depth = min(int(context.request.arguments.get("max_depth", 0)), 3)
    recursive = bool(context.request.arguments.get("recursive", False))
    entries = list(_entries(path, recursive, max_depth))
    limited = _fit_response(entries[:max_entries])
    return ToolExecutionResult(
        request_id=context.request.request_id,
        tool_name=context.request.tool_name,
        status=ToolExecutionStatus.SUCCESS,
        content={
            "path": context.relative_path,
            "entries": limited,
            "truncated": len(limited) < len(entries) or len(entries) > max_entries,
        },
        truncated=len(limited) < len(entries) or len(entries) > max_entries,
    )


def _search_text(context: ToolExecutionContext) -> ToolExecutionResult:
    rg = shutil.which(_RG)
    if rg is None:
        return _error(context, "search_backend_unavailable", "ripgrep is unavailable.")
    path = _resolved_path(context)
    file_result = _search_files(context, path)
    if isinstance(file_result, ToolExecutionResult):
        return file_result
    return _search_matches(context, rg, *file_result)


def _git_status(context: ToolExecutionContext) -> ToolExecutionResult:
    git = shutil.which(_GIT)
    if git is None:
        return _error(context, "git_unavailable", "git is unavailable.")
    root = _git_root(context, git)
    if isinstance(root, ToolExecutionResult):
        return root
    result = _run_git_status(context, git, root)
    if isinstance(result, ToolExecutionResult):
        return result
    entries, truncated = _git_entries(context, root, result.stdout)
    return ToolExecutionResult(
        request_id=context.request.request_id,
        tool_name=context.request.tool_name,
        status=ToolExecutionStatus.SUCCESS,
        content={
            "repository": root.relative_to(Path(context.workspace_id)).as_posix(),
            "entries": entries,
            "truncated": truncated,
        },
        truncated=truncated,
    )


def _git_root(context: ToolExecutionContext, git: str) -> Path | ToolExecutionResult:
    result = _run_git(
        context,
        git,
        ["rev-parse", "--show-toplevel"],
        cwd=_resolved_path(context),
    )
    if isinstance(result, ToolExecutionResult):
        return result
    root = Path(result.stdout.strip()).resolve()
    try:
        root.relative_to(Path(context.workspace_id))
    except ValueError:
        return _error(context, "git_repo_outside_workspace", "Repository escapes workspace.")
    return root


def _run_git_status(
    context: ToolExecutionContext, git: str, root: Path
) -> subprocess.CompletedProcess[str] | ToolExecutionResult:
    return _run_git(
        context,
        git,
        ["status", "--porcelain=v1", "-z", "-unormal"],
        cwd=root,
    )


def _search_files(
    context: ToolExecutionContext, path: Path
) -> tuple[list[str], bool] | ToolExecutionResult:
    if path.is_file():
        return [context.relative_path or path.name], False
    max_files = int(context.request.arguments.get("max_files", 50))
    max_bytes = int(context.request.arguments.get("max_bytes_per_file", 262144))
    files = list(_candidate_files(path, Path(context.workspace_id), max_bytes, max_files))
    return files[:max_files], len(files) > max_files


def _search_matches(
    context: ToolExecutionContext, rg: str, files: list[str], truncated: bool
) -> ToolExecutionResult:
    if not files:
        return _search_result(context, [], truncated)
    args = [
        rg,
        "--json",
        "--fixed-strings",
        "--line-number",
        "--color",
        "never",
        "--max-filesize",
        str(int(context.request.arguments.get("max_bytes_per_file", 262144))),
        *_sensitive_globs(),
        "--",
        str(context.request.arguments["query"]),
        *files,
    ]
    result = _run_rg(args, context, allow_no_match=True)
    if isinstance(result, ToolExecutionResult):
        return result
    matches, match_truncated = _matches(context, result.stdout)
    return _search_result(context, matches, truncated or match_truncated)


def _matches(
    context: ToolExecutionContext, stdout: str
) -> tuple[list[dict[str, object]], bool]:
    max_matches = int(context.request.arguments.get("max_matches", 20))
    preview_len = int(context.request.arguments.get("max_preview_chars", 160))
    rows: list[dict[str, object]] = []
    for line in stdout.splitlines():
        event = json.loads(line)
        if event.get("type") != "match":
            continue
        if len(rows) >= max_matches:
            return rows, True
        rows.append(_match_row(event["data"], preview_len))
    return rows, False


def _match_row(data: dict[str, object], preview_len: int) -> dict[str, object]:
    text = str(data["lines"]["text"]).rstrip("\n")
    path = str(data["path"]["text"]).removeprefix("./")
    return {
        "path": path,
        "line": int(data["line_number"]),
        "preview": _redact(text[:preview_len]),
    }


def _search_result(
    context: ToolExecutionContext, matches: list[dict[str, object]], truncated: bool
) -> ToolExecutionResult:
    limited = _fit_response(matches)
    was_truncated = truncated or len(limited) < len(matches)
    return ToolExecutionResult(
        request_id=context.request.request_id,
        tool_name=context.request.tool_name,
        status=ToolExecutionStatus.SUCCESS,
        content={"matches": limited, "truncated": was_truncated},
        truncated=was_truncated,
    )


def _run_rg(
    args: list[str], context: ToolExecutionContext, allow_no_match: bool = False
) -> subprocess.CompletedProcess[str] | ToolExecutionResult:
    try:
        result = subprocess.run(
            args,
            cwd=context.workspace_id,
            capture_output=True,
            text=True,
            timeout=context.request.timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return ToolExecutionResult(
            request_id=context.request.request_id,
            tool_name=context.request.tool_name,
            status=ToolExecutionStatus.TIMEOUT,
            error=SanitizedToolError(code="search_timeout", message="Search timed out."),
        )
    if result.returncode == 0 or (allow_no_match and result.returncode == 1):
        return result
    return _error(context, "search_backend_error", "Search backend failed.")


def _run_git(
    context: ToolExecutionContext,
    git: str,
    args: list[str],
    cwd: Path,
) -> subprocess.CompletedProcess[str] | ToolExecutionResult:
    try:
        result = subprocess.run(
            [
                git,
                "-c",
                "core.hooksPath=/dev/null",
                "-c",
                "core.pager=cat",
                "-c",
                "pager.status=false",
                *args,
            ],
            cwd=cwd,
            env={
                "GIT_PAGER": "cat",
                "PAGER": "cat",
                "GIT_EXTERNAL_DIFF": "",
                "GIT_CONFIG_NOSYSTEM": "1",
                "PATH": os.environ.get("PATH", ""),
            },
            capture_output=True,
            text=True,
            timeout=context.request.timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return ToolExecutionResult(
            request_id=context.request.request_id,
            tool_name=context.request.tool_name,
            status=ToolExecutionStatus.TIMEOUT,
            error=SanitizedToolError(code="git_timeout", message="Git timed out."),
        )
    if result.returncode == 0:
        return result
    return _error(context, "git_status_error", "Git status failed.")


def _git_entries(
    context: ToolExecutionContext, root: Path, stdout: str
) -> tuple[list[dict[str, object]], bool]:
    max_entries = int(context.request.arguments.get("max_entries", 200))
    parts = [part for part in stdout.split("\0") if part]
    rows: list[dict[str, object]] = []
    index = 0
    while index < len(parts):
        if len(rows) >= max_entries:
            return rows, True
        item = parts[index]
        index += 1
        row = _git_entry(root, item)
        if row is not None:
            rows.append(row)
        if item[:1] in {"R", "C"} and index < len(parts):
            index += 1
    return rows, False


def _git_entry(root: Path, item: str) -> dict[str, object] | None:
    status = item[:2]
    path = item[3:]
    target = root / path
    if not _allowed_repo_path(path, target):
        return None
    return {"path": path, "index": status[0], "worktree": status[1]}


def _allowed_repo_path(path: str, target: Path) -> bool:
    return (
        all(_allowed_search_name(part) for part in Path(path).parts)
        and not target.is_symlink()
    )


def _candidate_files(
    root: Path, workspace: Path, max_bytes: int, max_files: int
) -> list[str]:
    rows: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if _allowed_search_name(name)]
        for name in sorted(filenames):
            path = Path(dirpath) / name
            if _allowed_search_file(path, name, max_bytes):
                rows.append(path.relative_to(workspace).as_posix())
            if len(rows) > max_files:
                return rows
    return rows


def _allowed_search_file(path: Path, name: str, max_bytes: int) -> bool:
    return (
        _allowed_search_name(name)
        and not path.is_symlink()
        and path.is_file()
        and path.stat().st_size <= max_bytes
    )


def _allowed_search_name(name: str) -> bool:
    patterns = tuple(pattern.removeprefix("!") for pattern in _SENSITIVE_GLOBS)
    return not name.startswith(".") and not any(
        fnmatchcase(name, pattern) for pattern in patterns
    )


def _sensitive_globs() -> list[str]:
    args: list[str] = []
    for pattern in _SENSITIVE_GLOBS:
        args.extend(["--glob", pattern])
    return args


def _redact(text: str) -> str:
    return _SECRET_RE.sub(r"\1=[REDACTED]", text)


def _entries(path: Path, recursive: bool, max_depth: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for child in sorted(path.iterdir(), key=lambda item: item.name):
        if child.name.startswith("."):
            continue
        rows.append(_entry(child, child.name))
        if recursive and max_depth > 0 and _is_directory(child):
            for entry in _entries(child, True, max_depth - 1):
                rows.append({**entry, "name": f"{child.name}/{entry['name']}"})
    return rows


def _entry(path: Path, name: str) -> dict[str, object]:
    mode = path.lstat().st_mode
    if stat.S_ISDIR(mode):
        return {"name": name, "type": "directory", "size": None}
    if stat.S_ISREG(mode):
        return {"name": name, "type": "file", "size": path.stat().st_size}
    return {"name": name, "type": "other", "size": None}


def _is_directory(path: Path) -> bool:
    return stat.S_ISDIR(path.lstat().st_mode)


def _fit_response(entries: list[dict[str, object]]) -> list[dict[str, object]]:
    kept: list[dict[str, object]] = []
    for entry in entries:
        candidate = [*kept, entry]
        if len(json.dumps(candidate).encode("utf-8")) > _MAX_RESPONSE_BYTES:
            break
        kept = candidate
    return kept


def _resolved_path(context: ToolExecutionContext) -> Path:
    if not context.resolved_path:
        raise ValueError("resolved_path is required")
    return Path(context.resolved_path)


def _error(
    context: ToolExecutionContext,
    code: str,
    message: str,
) -> ToolExecutionResult:
    return ToolExecutionResult(
        request_id=context.request.request_id,
        tool_name=context.request.tool_name,
        status=ToolExecutionStatus.ERROR,
        error=SanitizedToolError(code=code, message=message),
    )
