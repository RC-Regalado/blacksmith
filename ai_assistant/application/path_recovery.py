"""Deterministic, non-fuzzy recovery for case-only workspace path mistakes.

Scope: read-only tools explicitly opted in by the coordinator (currently
``read_file`` and ``file_metadata``). This module resolves a single, exact,
case-insensitive match on the final path segment of an already-failed
lookup:

- zero candidates -> the original :class:`PathNotFoundError` is re-raised;
- exactly one candidate -> its corrected relative path is returned;
- more than one candidate -> :class:`AmbiguousPathError` is raised and no
  candidate is picked arbitrarily.

The parent directory itself must already resolve inside the workspace;
there is no recursive resolution of multi-segment mismatches and no
distance-based fuzzy matching. Hidden and sensitive-pattern names are never
offered as recovery candidates. The corrected path is not trusted on its
own: callers must re-run it through the full :class:`PathPolicy` pipeline,
which independently re-enforces workspace confinement, symlink checks and
sensitive-path denial before anything is read.
"""

from fnmatch import fnmatchcase
from pathlib import Path

from ai_assistant.application.errors import ConfigurationError
from ai_assistant.domain.errors import (
    AmbiguousPathError,
    PathNotFoundError,
    PathOutsideWorkspaceError,
    PathPermissionDeniedError,
)

_DENIED_CANDIDATE_PATTERNS = (
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


class PathRecoveryPolicy:
    """Finds a unique case-insensitive basename match for a missing path."""

    def __init__(self, workspace: str | None) -> None:
        if not workspace:
            raise ConfigurationError("AI_ASSISTANT_WORKSPACE is required")
        self._workspace = Path(workspace).resolve(strict=True)

    def resolve(self, relative_path: Path) -> Path:
        parent = relative_path.parent
        basename = relative_path.name

        try:
            parent_dir = (self._workspace / parent).resolve(strict=True)
        except PermissionError as exc:
            raise PathPermissionDeniedError("parent path is not accessible") from exc
        except OSError as exc:
            raise PathNotFoundError("path does not exist") from exc

        try:
            parent_dir.relative_to(self._workspace)
        except ValueError as exc:
            raise PathOutsideWorkspaceError("path escapes workspace") from exc

        if _has_denied_segment(parent_dir.relative_to(self._workspace)):
            # Never even list inside a hidden/sensitive directory. The full
            # PathPolicy re-validation would catch a match anyway, but the
            # lookup itself should not touch such a location.
            raise PathNotFoundError("path does not exist")

        try:
            candidates = sorted(
                entry.name
                for entry in parent_dir.iterdir()
                if _is_recovery_candidate(entry.name, basename)
            )
        except PermissionError as exc:
            raise PathPermissionDeniedError("parent path is not accessible") from exc
        except OSError as exc:
            # The parent segment resolved to something that exists but is
            # not a directory (e.g. a file with the exact requested name).
            raise PathNotFoundError("path does not exist") from exc

        if not candidates:
            raise PathNotFoundError("path does not exist")
        if len(candidates) > 1:
            raise AmbiguousPathError(
                "multiple case-insensitive matches for the requested path"
            )
        return parent / candidates[0]


def _has_denied_segment(relative_parent: Path) -> bool:
    for part in relative_parent.parts:
        if part in {"", "."}:
            continue
        if part.startswith("."):
            return True
        if any(fnmatchcase(part, pattern) for pattern in _DENIED_CANDIDATE_PATTERNS):
            return True
    return False


def _is_recovery_candidate(name: str, basename: str) -> bool:
    if name == basename:
        return False
    if name.lower() != basename.lower():
        return False
    if name.startswith("."):
        return False
    return not any(fnmatchcase(name, pattern) for pattern in _DENIED_CANDIDATE_PATTERNS)
