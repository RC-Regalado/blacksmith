"""Tests for CLI application wiring."""

import builtins
from pathlib import Path

import pytest

from ai_assistant.agent.message import Message
from ai_assistant.bootstrap.config import AppConfig
from ai_assistant.bootstrap.container import create_application
from ai_assistant.cli.app import CliApplication, CliConfirmationPrompter
from ai_assistant.domain.errors import AssistantError, InvalidToolCallError
from ai_assistant.knowledge import ContextMetrics, ContextPurpose
from ai_assistant.platform.domain import (
    BudgetUsage,
    CapabilityName,
    EvaluationResult,
    EvaluationStatus,
    ExecutionRecord,
    ExecutionResult,
    ExecutionStatus,
    Objective,
    Plan,
    PlatformTask,
)


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


def test_cli_top_level_help_lists_commands(capsys: pytest.CaptureFixture[str]) -> None:
    CliApplication(FakeRuntime()).run(("--help",))

    output = capsys.readouterr().out
    assert "Usage: python main.py chat|objective|knowledge [options]" in output
    assert "chat" in output
    assert "objective" in output
    assert "knowledge" in output


@pytest.mark.parametrize(
    ("args", "expected"),
    (
        (("chat", "--help"), "Usage: python main.py chat [--context] [--metrics]"),
        (
            ("objective", "--help"),
            'Usage: python main.py objective [--verbose] [--metrics] "Describe the objective"',
        ),
        (
            ("knowledge", "--help"),
            "Usage: python main.py knowledge status|index PATH|rebuild PATH|query TEXT",
        ),
    ),
)
def test_cli_command_help(args: tuple[str, ...], expected: str, capsys: pytest.CaptureFixture[str]) -> None:
    CliApplication(FakeRuntime()).run(args)

    assert expected in capsys.readouterr().out


def test_cli_chat_command_starts_chat(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    inputs = iter(["hello", "quit"])
    monkeypatch.setattr(builtins, "input", lambda _prompt: next(inputs))

    CliApplication(FakeRuntime()).run(("chat",))

    assert capsys.readouterr().out == "ok\n"


def test_cli_chat_context_flag_enables_runtime_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    inputs = iter(["hello", "quit"])
    runtime = FakeRuntime()
    monkeypatch.setattr(builtins, "input", lambda _prompt: next(inputs))

    CliApplication(runtime).run(("chat", "--context"))

    assert runtime.include_knowledge_context is True


def test_cli_chat_context_flag_does_not_stick_between_runs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime = FakeRuntime()
    inputs = iter(["quit", "quit"])
    monkeypatch.setattr(builtins, "input", lambda _prompt: next(inputs))
    app = CliApplication(runtime)

    app.run(("chat", "--context"))
    app.run(("chat",))

    assert runtime.include_knowledge_context is False


def test_cli_chat_prints_context_diagnostic(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    inputs = iter(["hello", "quit"])
    monkeypatch.setattr(builtins, "input", lambda _prompt: next(inputs))

    CliApplication(DiagnosticRuntime()).run(("chat", "--context"))

    assert "No rebuild was run." in capsys.readouterr().out


def test_cli_chat_metrics_print_context_metrics(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    inputs = iter(["hello", "quit"])
    monkeypatch.setattr(builtins, "input", lambda _prompt: next(inputs))

    CliApplication(MetricsRuntime()).run(("chat", "--context", "--metrics"))

    assert "context_conversation: candidates=2 ranked=1 selected=1" in capsys.readouterr().out


@pytest.mark.parametrize("args", (("bogus",), ("--metrics",), ("chat", "extra")))
def test_cli_malformed_args_print_usage(
    args: tuple[str, ...],
    capsys: pytest.CaptureFixture[str],
) -> None:
    CliApplication(FakeRuntime()).run(args)

    captured = capsys.readouterr()
    assert "Usage: python main.py" in captured.out or "Usage: python main.py" in captured.err


def test_cli_knowledge_errors_are_sanitized(capsys: pytest.CaptureFixture[str]) -> None:
    CliApplication(FakeRuntime(), knowledge_cli=FailingKnowledgeCli()).run(("knowledge", "index", "../"))

    captured = capsys.readouterr()
    assert captured.err == "Error: knowledge path escapes workspace.\n"
    assert "Traceback" not in captured.err


def test_bootstrap_creates_cli_application(tmp_path: Path) -> None:
    config = AppConfig(database=str(tmp_path / "test.sqlite3"))

    assert isinstance(create_application(config), CliApplication)


def test_bootstrap_wires_context_limit(tmp_path: Path) -> None:
    config = AppConfig(database=str(tmp_path / "test.sqlite3"), context_limit=123)

    app = create_application(config)

    assert app._runtime.context_builder.context_limit == 123
    assert app._runtime.conversation_context is not None


def test_bootstrap_leaves_tools_disabled_by_default(tmp_path: Path) -> None:
    config = AppConfig(database=str(tmp_path / "test.sqlite3"))

    app = create_application(config)

    assert app._runtime.tool_coordinator is None


def test_bootstrap_keeps_tools_unavailable_without_workspace(tmp_path: Path) -> None:
    config = AppConfig(
        database=str(tmp_path / "test.sqlite3"),
        execution_database=str(tmp_path / "execution.sqlite3"),
        tool_execution=True,
    )

    app = create_application(config)

    assert app._runtime.tool_coordinator is None


def test_bootstrap_wires_local_tool_coordinator_when_enabled(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    config = AppConfig(
        database=str(tmp_path / "test.sqlite3"),
        execution_database=str(tmp_path / "execution.sqlite3"),
        audit_database=str(tmp_path / "audit.sqlite3"),
        workspace=str(workspace),
        tool_execution=True,
        tool_timeout=3.0,
    )

    app = create_application(config)

    assert app._runtime.tool_coordinator is not None
    assert app._runtime.tool_timeout_seconds == 3.0
    assert app._objective_engine is not None


def test_bootstrap_adds_tool_prompt_when_tools_are_enabled(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    config = AppConfig(
        database=str(tmp_path / "test.sqlite3"),
        execution_database=str(tmp_path / "execution.sqlite3"),
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
        execution_database=str(tmp_path / "execution.sqlite3"),
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


def test_cli_objective_command_prints_sanitized_outcome(
    capsys: pytest.CaptureFixture[str],
) -> None:
    CliApplication(
        FakeRuntime(),
        FakeObjectiveEngine(),
        session_id="session",
        objective_id_factory=lambda: "fixed",
    ).run(("objective", "Inspect repository"))

    output = capsys.readouterr().out
    assert "Objective: obj-fixed" in output
    assert "Execution: completed" in output
    assert "Evaluation: passed" in output
    assert "Budget: tasks=1 model_calls=1 tool_calls=1 output_bytes=12" in output
    assert "- task-1: InspectDirectory" in output
    assert "- task-1:list_directory:success" in output
    assert "Summary:" in output
    assert "- Listed . (1 entries)." in output
    assert "secret file content" not in output


def test_cli_objective_requires_engine(capsys: pytest.CaptureFixture[str]) -> None:
    CliApplication(FakeRuntime()).run(("objective", "Inspect repository"))

    assert "objective execution requires tools and workspace" in capsys.readouterr().err


def test_cli_objective_verbose_prints_planner_response(
    capsys: pytest.CaptureFixture[str],
) -> None:
    CliApplication(FakeRuntime(), FailingObjectiveEngine()).run(
        ("objective", "--verbose", "Inspect repository")
    )

    captured = capsys.readouterr()
    assert "Planner model response:\nnot json\n" in captured.err
    assert "Error: planner returned invalid JSON." in captured.err


def test_cli_objective_metrics_prints_usage_and_context_metrics(
    capsys: pytest.CaptureFixture[str],
) -> None:
    CliApplication(
        FakeRuntime(),
        FakeObjectiveEngine(),
        session_id="session",
        objective_id_factory=lambda: "fixed",
    ).run(("objective", "--metrics", "Inspect repository"))

    output = capsys.readouterr().out
    assert "Metrics:" in output
    assert "- duration_seconds=1.2500" in output
    assert "context_planning: candidates=2 ranked=1 selected=1 raw_tokens=10 compiled_tokens=4" in output
    assert "context_synthesis: candidates=1 ranked=1 selected=1 raw_tokens=4 compiled_tokens=4" in output
    assert "secret file content" not in output


def test_cli_show_metrics_env_applies_to_objective(
    capsys: pytest.CaptureFixture[str],
) -> None:
    CliApplication(
        FakeRuntime(),
        FakeObjectiveEngine(),
        session_id="session",
        objective_id_factory=lambda: "fixed",
        show_metrics=True,
    ).run(("objective", "Inspect repository"))

    assert "Metrics:" in capsys.readouterr().out


def test_cli_show_metrics_env_applies_to_knowledge() -> None:
    knowledge_cli = RecordingKnowledgeCli()

    CliApplication(FakeRuntime(), knowledge_cli=knowledge_cli, show_metrics=True).run(
        ("knowledge", "query", "blacksmith")
    )

    assert knowledge_cli.args == ("query", "blacksmith", "--metrics")


class FakeRuntime:
    include_knowledge_context = False
    last_context_diagnostic = None
    last_context_metrics = None

    def respond(self, user_input: str) -> Message:
        return Message(role="assistant", content="ok")


class FailingRuntime:
    def respond(self, user_input: str) -> Message:
        raise AssistantError("Tool execution failed.")


class DiagnosticRuntime(FakeRuntime):
    def respond(self, user_input: str) -> Message:
        self.last_context_diagnostic = "Knowledge context requested. No rebuild was run."
        return Message(role="assistant", content="ok")


class MetricsRuntime(FakeRuntime):
    def respond(self, user_input: str) -> Message:
        self.last_context_metrics = ContextMetrics(ContextPurpose.CONVERSATION, 2, 1, 10, 4, 1)
        return Message(role="assistant", content="ok")


class FailingKnowledgeCli:
    def run(self, _args: tuple[str, ...]) -> None:
        raise InvalidToolCallError("knowledge path escapes workspace.")


class RecordingKnowledgeCli:
    args: tuple[str, ...] = ()

    def run(self, args: tuple[str, ...]) -> None:
        self.args = args


class FakeObjectiveEngine:
    last_planning_context_metrics = ContextMetrics(ContextPurpose.PLANNING, 2, 1, 10, 4, 1)
    last_synthesis_context_metrics = ContextMetrics(ContextPurpose.SYNTHESIS, 1, 1, 4, 4, 1)

    def run(self, objective: Objective, session_id: str):
        plan = Plan("plan-1", objective.objective_id, (_task(objective),))
        return type(
            "FakeOutcome",
            (),
            {
                "objective": objective,
                "plan": plan,
                "execution": ExecutionRecord(
                    "exec-1",
                    objective.objective_id,
                    "plan-1",
                    ExecutionStatus.COMPLETED,
                ),
                "result": ExecutionResult(
                    "exec-1",
                    ExecutionStatus.COMPLETED,
                    ("task-1:list_directory:success",),
                    observations=("Listed . (1 entries).",),
                ),
                "evaluation": EvaluationResult(
                    objective.objective_id,
                    EvaluationStatus.PASSED,
                    ("task-1:list_directory:success",),
                    "complete",
                ),
                "usage": BudgetUsage(
                    tasks=1,
                    model_calls=1,
                    tool_calls=1,
                    output_bytes=12,
                    duration_seconds=1.25,
                ),
                "content": "secret file content",
            },
        )()


class FailingObjectiveEngine:
    last_planner_response = "not json"

    def run(self, objective: Objective, session_id: str):
        raise InvalidToolCallError("planner returned invalid JSON.")


def _task(objective: Objective) -> PlatformTask:
    return PlatformTask(
        "task-1",
        objective.objective_id,
        "List files",
        CapabilityName.INSPECT_DIRECTORY,
        {"path": "."},
    )
