"""Integration tests for local read-only tool executor."""

import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from ai_assistant.domain.tools import (
    ToolExecutionContext,
    ToolExecutionRequest,
    ToolExecutionStatus,
    ToolPermission,
    ToolProfileId,
)
from ai_assistant.application.profile_registry import StaticToolProfileRegistry, ToolProfile
from ai_assistant.infrastructure.tools import local_read_only
from ai_assistant.infrastructure.tools.local_read_only import LocalReadOnlyToolExecutor


pytestmark = pytest.mark.integration


def test_list_directory_returns_structured_entries(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "README.md").write_text("hello", encoding="utf-8")
    (tmp_path / ".env").write_text("secret", encoding="utf-8")

    result = LocalReadOnlyToolExecutor().execute(_context(tmp_path, "list_directory", "."))

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.content == {
        "path": ".",
        "entries": [
            {"name": "README.md", "type": "file", "size": 5},
            {"name": "src", "type": "directory", "size": None},
        ],
        "truncated": False,
    }


def test_read_file_is_bounded_and_reports_truncation(tmp_path: Path) -> None:
    (tmp_path / "notes.txt").write_text("abcdef", encoding="utf-8")

    result = LocalReadOnlyToolExecutor().execute(
        _context(tmp_path, "read_file", "notes.txt", {"max_bytes": 3})
    )

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.truncated is True
    assert result.content == {
        "path": "notes.txt",
        "content": "abc",
        "bytes_read": 3,
        "truncated": True,
    }


def test_file_metadata_returns_no_file_content(tmp_path: Path) -> None:
    (tmp_path / "notes.txt").write_text("abcdef", encoding="utf-8")

    result = LocalReadOnlyToolExecutor().execute(
        _context(tmp_path, "file_metadata", "notes.txt", permission=ToolPermission.READ_METADATA)
    )

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.content is not None
    assert result.content["path"] == "notes.txt"
    assert result.content["type"] == "file"
    assert result.content["size"] == 6
    assert "content" not in result.content


def test_search_text_returns_bounded_literal_matches(tmp_path: Path) -> None:
    if shutil.which("rg") is None:
        pytest.skip("rg is required for productive search_text")
    (tmp_path / "notes.txt").write_text("hello.*\nhellox\n", encoding="utf-8")

    result = LocalReadOnlyToolExecutor().execute(
        _context(
            tmp_path,
            "search_text",
            ".",
            {"query": "hello.*", "max_matches": 1},
            permission=ToolPermission.READ_CONTENT,
        )
    )

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.truncated is False
    assert result.content == {
        "matches": [{"path": "notes.txt", "line": 1, "preview": "hello.*"}],
        "truncated": False,
    }


def test_search_text_marks_truncation(tmp_path: Path) -> None:
    if shutil.which("rg") is None:
        pytest.skip("rg is required for productive search_text")
    (tmp_path / "a.txt").write_text("needle\nneedle\n", encoding="utf-8")

    result = LocalReadOnlyToolExecutor().execute(
        _context(
            tmp_path,
            "search_text",
            ".",
            {"query": "needle", "max_matches": 1},
            permission=ToolPermission.READ_CONTENT,
        )
    )

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.truncated is True
    assert result.content is not None
    assert result.content["truncated"] is True
    assert len(result.content["matches"]) == 1


def test_search_text_bounds_files_and_bytes(tmp_path: Path) -> None:
    if shutil.which("rg") is None:
        pytest.skip("rg is required for productive search_text")
    (tmp_path / "a.txt").write_text("needle\n", encoding="utf-8")
    (tmp_path / "b.txt").write_text("needle\n", encoding="utf-8")
    (tmp_path / "big.txt").write_text("needle\n" + ("x" * 20), encoding="utf-8")

    result = LocalReadOnlyToolExecutor().execute(
        _context(
            tmp_path,
            "search_text",
            ".",
            {"query": "needle", "max_files": 1, "max_bytes_per_file": 100},
            permission=ToolPermission.READ_CONTENT,
        )
    )

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.truncated is True
    assert result.content is not None
    assert result.content["matches"] == [
        {"path": "a.txt", "line": 1, "preview": "needle"}
    ]

    bytes_result = LocalReadOnlyToolExecutor().execute(
        _context(
            tmp_path,
            "search_text",
            ".",
            {"query": "needle", "max_files": 10, "max_bytes_per_file": 8},
            permission=ToolPermission.READ_CONTENT,
        )
    )

    assert bytes_result.status == ToolExecutionStatus.SUCCESS
    assert bytes_result.content is not None
    paths = {match["path"] for match in bytes_result.content["matches"]}
    assert paths == {"a.txt", "b.txt"}


def test_search_text_excludes_hidden_sensitive_and_redacts_preview(tmp_path: Path) -> None:
    if shutil.which("rg") is None:
        pytest.skip("rg is required for productive search_text")
    (tmp_path / "visible.txt").write_text("token=abc123\n", encoding="utf-8")
    (tmp_path / ".hidden.txt").write_text("needle\n", encoding="utf-8")
    (tmp_path / "secret.pem").write_text("needle\n", encoding="utf-8")

    result = LocalReadOnlyToolExecutor().execute(
        _context(
            tmp_path,
            "search_text",
            ".",
            {"query": "token"},
            permission=ToolPermission.READ_CONTENT,
        )
    )

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.content == {
        "matches": [{"path": "visible.txt", "line": 1, "preview": "token=[REDACTED]"}],
        "truncated": False,
    }

    denied = LocalReadOnlyToolExecutor().execute(
        _context(
            tmp_path,
            "search_text",
            ".",
            {"query": "needle"},
            permission=ToolPermission.READ_CONTENT,
        )
    )

    assert denied.status == ToolExecutionStatus.SUCCESS
    assert denied.content == {"matches": [], "truncated": False}


def test_search_text_reports_missing_rg(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(local_read_only, "_RG", "__missing_rg__")
    (tmp_path / "notes.txt").write_text("needle", encoding="utf-8")

    result = LocalReadOnlyToolExecutor().execute(
        _context(
            tmp_path,
            "search_text",
            ".",
            {"query": "needle"},
            permission=ToolPermission.READ_CONTENT,
        )
    )

    assert result.status == ToolExecutionStatus.ERROR
    assert result.error is not None
    assert result.error.code == "search_backend_unavailable"


def test_git_status_returns_structured_entries(tmp_path: Path) -> None:
    _git(tmp_path, "init")
    (tmp_path / "tracked.txt").write_text("old\n", encoding="utf-8")
    _git(tmp_path, "add", "tracked.txt")
    _git(tmp_path, "commit", "-m", "initial")
    (tmp_path / "tracked.txt").write_text("new\n", encoding="utf-8")
    (tmp_path / "new.txt").write_text("new\n", encoding="utf-8")

    result = LocalReadOnlyToolExecutor().execute(
        _context(
            tmp_path,
            "git_status",
            ".",
            permission=ToolPermission.READ_REPOSITORY,
        )
    )

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.content is not None
    assert result.content["repository"] == "."
    assert result.content["truncated"] is False
    assert sorted(result.content["entries"], key=lambda row: row["path"]) == [
        {"path": "new.txt", "index": "?", "worktree": "?"},
        {"path": "tracked.txt", "index": " ", "worktree": "M"},
    ]


def test_git_status_marks_truncation(tmp_path: Path) -> None:
    _git(tmp_path, "init")
    (tmp_path / "a.txt").write_text("a\n", encoding="utf-8")
    (tmp_path / "b.txt").write_text("b\n", encoding="utf-8")

    result = LocalReadOnlyToolExecutor().execute(
        _context(
            tmp_path,
            "git_status",
            ".",
            {"max_entries": 1},
            permission=ToolPermission.READ_REPOSITORY,
        )
    )

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.truncated is True
    assert result.content is not None
    assert result.content["truncated"] is True
    assert len(result.content["entries"]) == 1


def test_git_status_omits_hidden_and_sensitive_paths(tmp_path: Path) -> None:
    _git(tmp_path, "init")
    (tmp_path / ".env").write_text("SECRET=value\n", encoding="utf-8")
    (tmp_path / "secret.pem").write_text("secret\n", encoding="utf-8")
    (tmp_path / "visible.txt").write_text("ok\n", encoding="utf-8")

    result = LocalReadOnlyToolExecutor().execute(
        _context(
            tmp_path,
            "git_status",
            ".",
            permission=ToolPermission.READ_REPOSITORY,
        )
    )

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.content is not None
    assert result.content["entries"] == [
        {"path": "visible.txt", "index": "?", "worktree": "?"}
    ]


def test_git_status_denies_repo_outside_workspace(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    workspace = repo / "workspace"
    workspace.mkdir(parents=True)
    _git(repo, "init")

    result = LocalReadOnlyToolExecutor().execute(
        _context(
            workspace,
            "git_status",
            ".",
            permission=ToolPermission.READ_REPOSITORY,
        )
    )

    assert result.status == ToolExecutionStatus.ERROR
    assert result.error is not None
    assert result.error.code == "git_repo_outside_workspace"


def test_git_status_uses_fixed_environment(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _git(tmp_path, "init")
    calls: list[dict[str, object]] = []
    real_run = subprocess.run

    def recording_run(*args: object, **kwargs: object):
        calls.append({"args": args, "kwargs": kwargs})
        return real_run(*args, **kwargs)

    monkeypatch.setattr(subprocess, "run", recording_run)

    result = LocalReadOnlyToolExecutor().execute(
        _context(
            tmp_path,
            "git_status",
            ".",
            permission=ToolPermission.READ_REPOSITORY,
        )
    )

    assert result.status == ToolExecutionStatus.SUCCESS
    status_call = calls[-1]
    argv = status_call["args"][0]
    env = status_call["kwargs"]["env"]
    assert "status" in argv
    assert "core.hooksPath=/dev/null" in argv
    assert "pager.status=false" in argv
    assert env["GIT_PAGER"] == "cat"
    assert env["PAGER"] == "cat"
    assert env["GIT_EXTERNAL_DIFF"] == ""


def test_git_diff_returns_worktree_diff(tmp_path: Path) -> None:
    _git(tmp_path, "init")
    (tmp_path / "tracked.txt").write_text("old\n", encoding="utf-8")
    _git(tmp_path, "add", "tracked.txt")
    _git(tmp_path, "commit", "-m", "initial")
    (tmp_path / "tracked.txt").write_text("new\n", encoding="utf-8")

    result = LocalReadOnlyToolExecutor().execute(
        _context(
            tmp_path,
            "git_diff",
            ".",
            {"scope": "worktree"},
            permission=ToolPermission.READ_REPOSITORY,
        )
    )

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.content is not None
    assert result.content["scope"] == "worktree"
    assert "-old" in result.content["diff"]
    assert "+new" in result.content["diff"]


def test_git_diff_returns_staged_diff(tmp_path: Path) -> None:
    _git(tmp_path, "init")
    (tmp_path / "tracked.txt").write_text("old\n", encoding="utf-8")
    _git(tmp_path, "add", "tracked.txt")
    _git(tmp_path, "commit", "-m", "initial")
    (tmp_path / "tracked.txt").write_text("new\n", encoding="utf-8")
    _git(tmp_path, "add", "tracked.txt")

    result = LocalReadOnlyToolExecutor().execute(
        _context(
            tmp_path,
            "git_diff",
            ".",
            {"scope": "staged"},
            permission=ToolPermission.READ_REPOSITORY,
        )
    )

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.content is not None
    assert result.content["scope"] == "staged"
    assert "-old" in result.content["diff"]
    assert "+new" in result.content["diff"]


def test_git_diff_marks_truncation(tmp_path: Path) -> None:
    _git(tmp_path, "init")
    (tmp_path / "tracked.txt").write_text("old\n", encoding="utf-8")
    _git(tmp_path, "add", "tracked.txt")
    _git(tmp_path, "commit", "-m", "initial")
    (tmp_path / "tracked.txt").write_text("new\n", encoding="utf-8")

    result = LocalReadOnlyToolExecutor().execute(
        _context(
            tmp_path,
            "git_diff",
            ".",
            {"scope": "worktree", "max_bytes": 20},
            permission=ToolPermission.READ_REPOSITORY,
        )
    )

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.truncated is True
    assert result.content is not None
    assert result.content["truncated"] is True
    assert len(result.content["diff"].encode("utf-8")) <= 20


def test_git_diff_omits_sensitive_paths_and_redacts_content(tmp_path: Path) -> None:
    _git(tmp_path, "init")
    (tmp_path / "visible.txt").write_text("password=old\n", encoding="utf-8")
    (tmp_path / ".env").write_text("password=hidden-old\n", encoding="utf-8")
    (tmp_path / "secret.pem").write_text("password=secret-old\n", encoding="utf-8")
    _git(tmp_path, "add", "visible.txt", ".env", "secret.pem")
    _git(tmp_path, "commit", "-m", "initial")
    (tmp_path / "visible.txt").write_text("password=new\n", encoding="utf-8")
    (tmp_path / ".env").write_text("password=hidden-new\n", encoding="utf-8")
    (tmp_path / "secret.pem").write_text("password=secret-new\n", encoding="utf-8")

    result = LocalReadOnlyToolExecutor().execute(
        _context(
            tmp_path,
            "git_diff",
            ".",
            {"scope": "worktree"},
            permission=ToolPermission.READ_REPOSITORY,
        )
    )

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.content is not None
    diff = result.content["diff"]
    assert ".env" not in diff
    assert "secret.pem" not in diff
    assert "password=old" not in diff
    assert "password=new" not in diff
    assert "password=[REDACTED]" in diff


def test_run_tests_executes_approved_profile(tmp_path: Path) -> None:
    executor = LocalReadOnlyToolExecutor(_profiles(_profile("ok-profile", "print('ok')")))

    result = executor.execute(
        _context(
            tmp_path,
            "run_tests",
            ".",
            {"profile_id": "ok-profile"},
            permission=ToolPermission.EXECUTE_PROJECT,
        )
    )

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.content is not None
    assert result.content["exit_code"] == 0
    assert result.content["stdout"] == "ok\n"
    assert "duration_ms" in result.content


def test_run_tests_denies_unknown_profile(tmp_path: Path) -> None:
    result = LocalReadOnlyToolExecutor(_profiles()).execute(
        _context(
            tmp_path,
            "run_tests",
            ".",
            {"profile_id": "missing"},
            permission=ToolPermission.EXECUTE_PROJECT,
        )
    )

    assert result.status == ToolExecutionStatus.ERROR
    assert result.error is not None
    assert result.error.code == "unknown_profile"


def test_run_tests_bounds_output_and_redacts(tmp_path: Path) -> None:
    executor = LocalReadOnlyToolExecutor(
        _profiles(_profile("loud-profile", "print('token=abcdef')"))
    )

    result = executor.execute(
        _context(
            tmp_path,
            "run_tests",
            ".",
            {"profile_id": "loud-profile", "stdout_limit_bytes": 12},
            permission=ToolPermission.EXECUTE_PROJECT,
        )
    )

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.truncated is True
    assert result.content is not None
    assert "abcdef" not in result.content["stdout"]
    assert len(result.content["stdout"].encode("utf-8")) <= 12
    assert result.content["stdout_truncated"] is True


def test_run_tests_reports_timeout(tmp_path: Path) -> None:
    executor = LocalReadOnlyToolExecutor(
        _profiles(_profile("slow-profile", "import time; time.sleep(1)", timeout=0.01))
    )

    result = executor.execute(
        _context(
            tmp_path,
            "run_tests",
            ".",
            {"profile_id": "slow-profile"},
            permission=ToolPermission.EXECUTE_PROJECT,
        )
    )

    assert result.status == ToolExecutionStatus.TIMEOUT
    assert result.error is not None
    assert result.error.code == "process_timeout"


def test_run_tests_uses_no_shell_and_sanitized_environment(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    calls: list[dict[str, object]] = []
    real_run = subprocess.run

    def recording_run(*args: object, **kwargs: object):
        calls.append({"args": args, "kwargs": kwargs})
        return real_run(*args, **kwargs)

    monkeypatch.setenv("SECRET_TOKEN", "secret")
    monkeypatch.setattr(subprocess, "run", recording_run)
    executor = LocalReadOnlyToolExecutor(_profiles(_profile("ok-profile", "print('ok')")))

    result = executor.execute(
        _context(
            tmp_path,
            "run_tests",
            ".",
            {"profile_id": "ok-profile"},
            permission=ToolPermission.EXECUTE_PROJECT,
        )
    )

    assert result.status == ToolExecutionStatus.SUCCESS
    kwargs = calls[-1]["kwargs"]
    assert kwargs["shell"] is False
    assert "SECRET_TOKEN" not in kwargs["env"]


def test_build_project_executes_approved_profile(tmp_path: Path) -> None:
    executor = LocalReadOnlyToolExecutor(_profiles(_profile("build-ok", "print('built')")))

    result = executor.execute(
        _context(
            tmp_path,
            "build_project",
            ".",
            {"profile_id": "build-ok"},
            permission=ToolPermission.EXECUTE_PROJECT,
        )
    )

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.content is not None
    assert result.content["profile_id"] == "build-ok"
    assert result.content["exit_code"] == 0
    assert result.content["stdout"] == "built\n"


def test_build_project_denies_unknown_profile(tmp_path: Path) -> None:
    result = LocalReadOnlyToolExecutor(_profiles()).execute(
        _context(
            tmp_path,
            "build_project",
            ".",
            {"profile_id": "missing"},
            permission=ToolPermission.EXECUTE_PROJECT,
        )
    )

    assert result.status == ToolExecutionStatus.ERROR
    assert result.error is not None
    assert result.error.code == "unknown_profile"


def test_executor_repeats_path_validation_before_access(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside.txt"
    outside.write_text("secret", encoding="utf-8")

    result = LocalReadOnlyToolExecutor().execute(
        _context(tmp_path, "read_file", "../outside.txt")
    )

    assert result.status == ToolExecutionStatus.ERROR
    assert result.error is not None
    assert result.error.code == "local_executor_error"


def test_binary_file_is_decoded_with_replacement(tmp_path: Path) -> None:
    (tmp_path / "binary.bin").write_bytes(b"a\xffb")

    result = LocalReadOnlyToolExecutor().execute(
        _context(tmp_path, "read_file", "binary.bin")
    )

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.content is not None
    assert result.content["content"] == "a\ufffdb"
    assert result.content["bytes_read"] == 3


def test_executor_enforces_read_limit_independently(tmp_path: Path) -> None:
    (tmp_path / "big.txt").write_bytes(b"x" * 70000)

    result = LocalReadOnlyToolExecutor().execute(
        _context(tmp_path, "read_file", "big.txt", {"max_bytes": 70000})
    )

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.content is not None
    assert result.content["bytes_read"] == 65536
    assert result.truncated is True


def test_executor_enforces_directory_entry_limit_independently(tmp_path: Path) -> None:
    for index in range(1002):
        (tmp_path / f"{index:04}.txt").write_text("x", encoding="utf-8")

    result = LocalReadOnlyToolExecutor().execute(
        _context(tmp_path, "list_directory", ".", {"max_entries": 2000})
    )

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.content is not None
    assert len(result.content["entries"]) == 1000
    assert result.truncated is True


def _context(
    workspace: Path,
    tool_name: str,
    path: str,
    arguments: dict[str, object] | None = None,
    permission: ToolPermission = ToolPermission.READ_ONLY,
) -> ToolExecutionContext:
    args = {"path": path, **(arguments or {})}
    return ToolExecutionContext(
        request=ToolExecutionRequest(
            request_id="req-1",
            session_id="default",
            tool_name=tool_name,
            arguments=args,
            permission=permission,
        ),
        workspace_id=str(workspace),
        resolved_path=str((workspace / path).resolve()),
        relative_path=path,
    )


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=cwd,
        env={
            "GIT_AUTHOR_NAME": "Test",
            "GIT_AUTHOR_EMAIL": "test@example.invalid",
            "GIT_COMMITTER_NAME": "Test",
            "GIT_COMMITTER_EMAIL": "test@example.invalid",
            "PATH": os.environ.get("PATH", ""),
        },
        check=True,
        capture_output=True,
        text=True,
    )


def _profiles(*profiles: ToolProfile) -> StaticToolProfileRegistry:
    return StaticToolProfileRegistry(profiles)


def _profile(profile_id: str, code: str, timeout: float = 5.0) -> ToolProfile:
    return ToolProfile(
        profile_id=ToolProfileId(profile_id),
        argv=(sys.executable, "-c", code),
        permission=ToolPermission.EXECUTE_PROJECT,
        timeout_seconds=timeout,
        stdout_limit_bytes=64,
        stderr_limit_bytes=64,
        env={"PYTHONDONTWRITEBYTECODE": "1"},
    )
