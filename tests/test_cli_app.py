"""Tests for CLI application wiring."""

import builtins

import pytest

from ai_assistant.agent.message import Message
from ai_assistant.bootstrap.container import create_application
from ai_assistant.cli.app import CliApplication


pytestmark = pytest.mark.unit


def test_cli_application_can_run_with_fake_runtime(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    inputs = iter(["hello", "quit"])
    monkeypatch.setattr(builtins, "input", lambda _prompt: next(inputs))

    CliApplication(FakeRuntime()).run()

    assert capsys.readouterr().out == "ok\n"


def test_bootstrap_creates_cli_application() -> None:
    assert isinstance(create_application(), CliApplication)


class FakeRuntime:
    def respond(self, user_input: str) -> Message:
        return Message(role="assistant", content="ok")
