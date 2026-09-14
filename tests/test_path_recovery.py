"""Unit tests for deterministic, case-only path recovery."""

from pathlib import Path

import pytest

from ai_assistant.application.errors import ConfigurationError
from ai_assistant.application.path_recovery import PathRecoveryPolicy
from ai_assistant.domain.errors import (
    AmbiguousPathError,
    PathNotFoundError,
    PathOutsideWorkspaceError,
)


pytestmark = pytest.mark.unit


def test_unique_case_insensitive_match_is_recovered(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("guidelines", encoding="utf-8")
    policy = PathRecoveryPolicy(str(tmp_path))

    resolved = policy.resolve(Path("Agents.md"))

    assert resolved == Path("AGENTS.md")


def test_nested_unique_match_is_recovered(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "README.md").write_text("hi", encoding="utf-8")
    policy = PathRecoveryPolicy(str(tmp_path))

    resolved = policy.resolve(Path("docs/readme.md"))

    assert resolved == Path("docs/README.md")


def test_no_candidate_reraises_not_found(tmp_path: Path) -> None:
    policy = PathRecoveryPolicy(str(tmp_path))

    with pytest.raises(PathNotFoundError):
        policy.resolve(Path("missing.md"))


def test_non_matching_name_is_not_recovered(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("guidelines", encoding="utf-8")
    policy = PathRecoveryPolicy(str(tmp_path))

    with pytest.raises(PathNotFoundError):
        policy.resolve(Path("agent.md"))


def test_multiple_case_variants_raise_ambiguous(tmp_path: Path) -> None:
    (tmp_path / "Agents.md").write_text("a", encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text("b", encoding="utf-8")
    policy = PathRecoveryPolicy(str(tmp_path))

    with pytest.raises(AmbiguousPathError):
        policy.resolve(Path("agents.md"))


def test_missing_parent_directory_reraises_not_found(tmp_path: Path) -> None:
    policy = PathRecoveryPolicy(str(tmp_path))

    with pytest.raises(PathNotFoundError):
        policy.resolve(Path("missing_dir/agents.md"))


def test_hidden_candidate_is_never_offered(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text("SECRET=1", encoding="utf-8")
    policy = PathRecoveryPolicy(str(tmp_path))

    with pytest.raises(PathNotFoundError):
        policy.resolve(Path(".ENV"))


def test_sensitive_pattern_candidate_is_never_offered(tmp_path: Path) -> None:
    (tmp_path / "secret.pem").write_text("key", encoding="utf-8")
    policy = PathRecoveryPolicy(str(tmp_path))

    with pytest.raises(PathNotFoundError):
        policy.resolve(Path("Secret.PEM"))


def test_parent_segment_resolving_to_a_file_does_not_crash(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("content", encoding="utf-8")
    policy = PathRecoveryPolicy(str(tmp_path))

    with pytest.raises(PathNotFoundError):
        policy.resolve(Path("AGENTS.md/section1"))


def test_hidden_parent_directory_is_never_scanned(tmp_path: Path) -> None:
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "config").write_text("x", encoding="utf-8")
    policy = PathRecoveryPolicy(str(tmp_path))

    with pytest.raises(PathNotFoundError):
        policy.resolve(Path(".git/Config"))


def test_sensitive_parent_directory_is_never_scanned(tmp_path: Path) -> None:
    secrets_dir = tmp_path / "secrets.d"
    secrets_dir.mkdir()
    (secrets_dir / "token.txt").write_text("x", encoding="utf-8")
    policy = PathRecoveryPolicy(str(tmp_path))

    with pytest.raises(PathNotFoundError):
        policy.resolve(Path("secrets.d/Token.txt"))


def test_symlinked_parent_escaping_workspace_is_denied(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (workspace / "link").symlink_to(outside, target_is_directory=True)
    policy = PathRecoveryPolicy(str(workspace))

    with pytest.raises(PathOutsideWorkspaceError):
        policy.resolve(Path("link/agents.md"))


@pytest.mark.parametrize("workspace", [None, ""])
def test_missing_workspace_produces_typed_error(workspace: str | None) -> None:
    with pytest.raises(ConfigurationError, match="AI_ASSISTANT_WORKSPACE"):
        PathRecoveryPolicy(workspace)
