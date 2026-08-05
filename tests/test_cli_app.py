"""Tests for CLI application wiring."""

import builtins
from pathlib import Path

import pytest

from ai_assistant.agent.message import Message
from ai_assistant.bootstrap.config import AppConfig
from ai_assistant.bootstrap.container import create_application
from ai_assistant.cli.app import CliApplication, CliConfirmationPrompter
from ai_assistant.domain.errors import AssistantError


pytestmark = pytest.mark.unit


def test_cli_application_can_run_with_fake_runtime(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    inputs = iter(["hello", "quit"])
    monkeypatch.setattr(builtins, "input", lambda _prompt: next(inputs))

    CliApplication(FakeRuntime()).run()

    assert capsys.readouterr().out == "ok\n"


def test_cli_expected_errors_are_sanitized(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    inputs = iter(["hello", "quit"])
    monkeypatch.setattr(builtins, "input", lambda _prompt: next(inputs))

    CliApplication(FailingRuntime()).run()

    captured = capsys.readouterr()
    assert captured.err == "Error: Tool execution failed.\n"
    assert "Traceback" not in captured.err


def test_bootstrap_creates_cli_application(tmp_path: Path) -> None:
    config = AppConfig(database=str(tmp_path / "test.sqlite3"))

    assert isinstance(create_application(config), CliApplication)


def test_bootstrap_wires_context_limit(tmp_path: Path) -> None:
    config = AppConfig(database=str(tmp_path / "test.sqlite3"), context_limit=123)

    app = create_application(config)

    assert app._runtime.context_builder.context_limit == 123


def test_bootstrap_leaves_tools_disabled_by_default(tmp_path: Path) -> None:
    config = AppConfig(database=str(tmp_path / "test.sqlite3"))

    app = create_application(config)

    assert app._runtime.tool_coordinator is None


def test_bootstrap_keeps_tools_unavailable_without_workspace(tmp_path: Path) -> None:
    config = AppConfig(
        database=str(tmp_path / "test.sqlite3"),
        tool_execution=True,
    )

    app = create_application(config)

    assert app._runtime.tool_coordinator is None


def test_bootstrap_wires_local_tool_coordinator_when_enabled(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    config = AppConfig(
        database=str(tmp_path / "test.sqlite3"),
        audit_database=str(tmp_path / "audit.sqlite3"),
        workspace=str(workspace),
        tool_execution=True,
        tool_timeout=3.0,
    )

    app = create_application(config)

    assert app._runtime.tool_coordinator is not None
    assert app._runtime.tool_timeout_seconds == 3.0


def test_bootstrap_adds_tool_prompt_when_tools_are_enabled(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    config = AppConfig(
        database=str(tmp_path / "test.sqlite3"),
        audit_database=str(tmp_path / "audit.sqlite3"),
        system_prompt="base",
        workspace=str(workspace),
        tool_execution=True,
    )

    app = create_application(config)

    assert "base" in app._runtime.context_builder.system_prompt
    assert "list_directory" in app._runtime.context_builder.system_prompt
    assert "read_file" in app._runtime.context_builder.system_prompt
    assert "run_tests" in app._runtime.context_builder.system_prompt
    assert "write" in app._runtime.context_builder.system_prompt


def test_bootstrap_wires_confirmation_service_when_tools_are_enabled(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    config = AppConfig(
        database=str(tmp_path / "test.sqlite3"),
        audit_database=str(tmp_path / "audit.sqlite3"),
        workspace=str(workspace),
        tool_execution=True,
        tool_executor="local",
    )

    app = create_application(config)

    assert app._runtime.tool_coordinator is not None
    assert app._runtime.tool_coordinator._confirmation is not None


def test_cli_confirmation_prompter_requires_yes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(builtins, "input", lambda _prompt: "no")

    assert CliConfirmationPrompter().confirm("session", "workspace", "write") is False

    monkeypatch.setattr(builtins, "input", lambda _prompt: "yes")

    assert CliConfirmationPrompter().confirm("session", "workspace", "write") is True


class FakeRuntime:
    def respond(self, user_input: str) -> Message:
        return Message(role="assistant", content="ok")


class FailingRuntime:
    def respond(self, user_input: str) -> Message:
        raise AssistantError("Tool execution failed.")
