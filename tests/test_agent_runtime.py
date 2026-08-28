"""Tests for the Phase 1 agent runtime."""

import json

import pytest

from ai_assistant.agent.context import ContextBuilder
from ai_assistant.application.conversation_budget import ConversationContextBudget
from ai_assistant.application.conversation_context import ConversationContextService
from ai_assistant.application.ports.memory import (
    ConversationMemory,
    SessionId,
)
from ai_assistant.application.ports.models import ModelProvider
from ai_assistant.agent.message import FinishReason, Message, ModelResponse
from ai_assistant.agent.planner import ToolCallDetector
from ai_assistant.agent.runtime import AgentRuntime
from ai_assistant.application.tool_catalog import StaticToolCatalog
from ai_assistant.domain.tools import (
    InteractionLogEvent,
    InteractionStage,
    SanitizedToolError,
    ToolExecutionRequest,
    ToolExecutionResult,
    ToolExecutionStatus,
    ToolPermission,
)
from ai_assistant.infrastructure.tool_diagnostics import JsonlInteractionDiagnosticLogger
from ai_assistant.knowledge import CompiledContext, ContextBudget, ContextPurpose
from ai_assistant.knowledge import ConversationRetrievalPolicy


pytestmark = pytest.mark.unit


def test_runtime_persists_user_and_assistant_turn() -> None:
    memory = FakeConversationStore()
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="System prompt"),
        memory=memory,
        model=FakeModel("Echo: Hello"),
        tool_detector=ToolCallDetector(),
        session_id="alpha",
    )

    response = runtime.respond("Hello")

    assert response == Message(role="assistant", content="Echo: Hello")
    assert memory.history("alpha") == [
        Message(role="user", content="Hello", session_id="alpha"),
        Message(role="assistant", content="Echo: Hello", session_id="alpha"),
    ]
    assert memory.history("beta") == []


def test_runtime_persists_complete_turn_atomically() -> None:
    memory = FailingTurnStore()
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="System prompt"),
        memory=memory,
        model=FakeModel("Echo: Hello"),
        tool_detector=ToolCallDetector(),
        session_id="alpha",
    )

    with pytest.raises(RuntimeError, match="store failed"):
        runtime.respond("Hello")

    assert memory.history("alpha") == []


def test_context_builder_merges_system_history_and_user_input() -> None:
    builder = ContextBuilder(system_prompt="System prompt")
    history = [Message(role="assistant", content="Prior response")]

    context = builder.build(history=history, user_input="Next")

    assert context == [
        Message(role="system", content="System prompt"),
        Message(role="assistant", content="Prior response"),
        Message(role="user", content="Next"),
    ]


def test_context_builder_prefers_recent_history_within_budget() -> None:
    # Budget is a word-count estimate (ADR-071), not a character count: each
    # history message below costs 3 estimated tokens, so budget=9 leaves room
    # (after the 1-token system prompt and 1-token user input) for only the
    # two most recent of three history messages.
    builder = ContextBuilder(system_prompt="S", context_limit=9)
    history = [
        Message(role="user", content="old message body"),
        Message(role="assistant", content="mid message body"),
        Message(role="assistant", content="new message body"),
    ]

    context = builder.build(history=history, user_input="U")

    assert context == [
        Message(role="system", content="S"),
        Message(role="assistant", content="mid message body"),
        Message(role="assistant", content="new message body"),
        Message(role="user", content="U"),
    ]


def test_context_builder_preserves_system_and_current_input_when_over_budget() -> None:
    builder = ContextBuilder(system_prompt="system", context_limit=1)

    context = builder.build(
        history=[Message(role="assistant", content="history")],
        user_input="current",
    )

    assert context == [
        Message(role="system", content="system"),
        Message(role="user", content="current"),
    ]


def test_runtime_stores_tool_call_plan_without_execution() -> None:
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="System prompt"),
        memory=FakeConversationStore(),
        model=FakeModel('{"tool_call":{"name":"search","arguments":{"q":"x"}}}'),
        tool_detector=ToolCallDetector(),
        session_id="alpha",
    )

    runtime.respond("Hello")

    assert runtime.last_tool_plan.has_tool_call is True
    assert runtime.last_tool_plan.tool_name == "search"


def test_runtime_uses_tool_result_for_final_answer() -> None:
    memory = FakeConversationStore()
    model = SequenceModel(
        [
            '{"tool_call":{"id":"call-1","name":"read_file","arguments":{"path":"notes.txt"}}}',
            "Final answer from tool result",
        ]
    )
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="System prompt"),
        memory=memory,
        model=model,
        tool_detector=ToolCallDetector(),
        tool_coordinator=FakeToolCoordinator(
            ToolExecutionResult(
                request_id="call-1",
                tool_name="read_file",
                status=ToolExecutionStatus.SUCCESS,
                content={"content": "notes"},
            )
        ),
        session_id="alpha",
    )

    response = runtime.respond("Read notes")

    assert response == Message(role="assistant", content="Final answer from tool result")
    assert model.calls[1][-1].role == "tool"
    assert runtime.tool_coordinator.requests[0].timeout_seconds == 5.0
    assert memory.history("alpha") == [
        Message(role="user", content="Read notes", session_id="alpha"),
        Message(
            role="assistant",
            content='{"tool_call":{"id":"call-1","name":"read_file","arguments":{"path":"notes.txt"}}}',
            session_id="alpha",
        ),
        Message(
            role="tool",
            content='{"content": {"content": "notes"}, "status": "success", "truncated": false}',
            session_id="alpha",
            tool_name="read_file",
            tool_call_id="call-1",
        ),
        Message(
            role="assistant",
            content="Final answer from tool result",
            session_id="alpha",
        ),
    ]


def test_runtime_tool_error_contract_does_not_relabel_malformed_response() -> None:
    model = SequenceModel(
        [
            '{"tool_call":{"id":"call-1","name":"list_directory","arguments":{"path":"."}}}',
            "Final answer",
        ]
    )
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="System prompt"),
        memory=FakeConversationStore(),
        model=model,
        tool_detector=ToolCallDetector(),
        tool_coordinator=FakeToolCoordinator(
            ToolExecutionResult(
                request_id="call-1",
                tool_name="list_directory",
                status=ToolExecutionStatus.ERROR,
                error=SanitizedToolError(
                    code="malformed_response",
                    message="Tool execution failed.",
                ),
            )
        ),
        session_id="alpha",
    )

    runtime.respond("List files")

    tool_payload = json.loads(model.calls[1][-1].content)
    assert tool_payload["error"]["code"] == "malformed_response"
    assert tool_payload["error"]["code"] not in {"permission_denied", "path_denied", "not_found"}


def test_runtime_executes_operator_tool_json_without_model_call() -> None:
    model = SequenceModel(["should not be used"])
    coordinator = FakeToolCoordinator(
        ToolExecutionResult(
            request_id="alpha:list_directory",
            tool_name="list_directory",
            status=ToolExecutionStatus.SUCCESS,
            content={"entries": []},
        )
    )
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="System prompt"),
        memory=FakeConversationStore(),
        model=model,
        tool_detector=ToolCallDetector(),
        tool_coordinator=coordinator,
        session_id="alpha",
    )

    response = runtime.respond(
        '{"tool_call":{"name":"list_directory","arguments":{"path":"."}}}'
    )

    assert model.calls == []
    assert coordinator.requests[0].tool_name == "list_directory"
    assert response.content == (
        '{"content": {"entries": []}, "status": "success", "truncated": false}'
    )


def test_runtime_uses_configured_tool_timeout() -> None:
    coordinator = FakeToolCoordinator(
        ToolExecutionResult(
            request_id="alpha:read_file",
            tool_name="read_file",
            status=ToolExecutionStatus.SUCCESS,
            content={"content": "notes"},
        )
    )
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="System prompt"),
        memory=FakeConversationStore(),
        model=SequenceModel(
            [
                '{"tool_call":{"name":"read_file","arguments":{"path":"notes.txt"}}}',
                "Final answer",
            ]
        ),
        tool_detector=ToolCallDetector(),
        tool_coordinator=coordinator,
        tool_timeout_seconds=7.5,
        session_id="alpha",
    )

    runtime.respond("Read notes")

    assert coordinator.requests[0].timeout_seconds == 7.5


def test_runtime_derives_tool_permission_from_catalog() -> None:
    coordinator = FakeToolCoordinator(
        ToolExecutionResult(
            request_id="alpha:run_tests",
            tool_name="run_tests",
            status=ToolExecutionStatus.SUCCESS,
            content={"exit_code": 0},
        )
    )
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="System prompt"),
        memory=FakeConversationStore(),
        model=SequenceModel(
            [
                '{"tool_call":{"name":"run_tests","arguments":{"path":".","profile_id":"core-tests"}}}',
                "Final answer",
            ]
        ),
        tool_detector=ToolCallDetector(),
        tool_catalog=StaticToolCatalog(),
        tool_coordinator=coordinator,
        session_id="alpha",
    )

    runtime.respond("Run tests")

    assert coordinator.requests[0].permission == ToolPermission.EXECUTE_PROJECT


def test_runtime_context_enabled_preserves_tool_round() -> None:
    provider = EmptyContextProvider()
    coordinator = FakeToolCoordinator(
        ToolExecutionResult(
            request_id="alpha:git_status",
            tool_name="git_status",
            status=ToolExecutionStatus.SUCCESS,
            content={"entries": []},
        )
    )
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="System prompt"),
        conversation_context=ConversationContextService(
            ContextBuilder(system_prompt="System prompt"),
            context_provider=provider,
            retrieval_policy=AllowPolicy(),
        ),
        memory=FakeConversationStore(),
        model=SequenceModel(
            [
                '{"tool_call":{"name":"git_status","arguments":{"path":"."}}}',
                "Final answer",
            ]
        ),
        tool_detector=ToolCallDetector(),
        tool_catalog=StaticToolCatalog(),
        tool_coordinator=coordinator,
        include_knowledge_context=True,
        session_id="alpha",
    )

    response = runtime.respond("Explain project architecture")

    assert response.content == "Final answer"
    assert provider.calls == 1
    assert coordinator.requests[0].tool_name == "git_status"
    assert len(coordinator.requests) == 1


def test_runtime_context_enabled_live_state_bypasses_retrieval_before_tool_call() -> None:
    provider = EmptyContextProvider()
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="System prompt"),
        conversation_context=ConversationContextService(
            ContextBuilder(system_prompt="System prompt"),
            context_provider=provider,
            retrieval_policy=ConversationRetrievalPolicy(),
        ),
        memory=FakeConversationStore(),
        model=SequenceModel(
            [
                '{"tool_call":{"name":"git_status","arguments":{"path":"."}}}',
                "Final answer",
            ]
        ),
        tool_detector=ToolCallDetector(),
        tool_catalog=StaticToolCatalog(),
        tool_coordinator=FakeToolCoordinator(
            ToolExecutionResult(
                request_id="alpha:git_status",
                tool_name="git_status",
                status=ToolExecutionStatus.SUCCESS,
                content={"entries": []},
            )
        ),
        include_knowledge_context=True,
        session_id="alpha",
    )

    runtime.respond("What is the current git status?")

    assert provider.calls == 0


def test_runtime_stops_once_tool_loop_budget_is_exhausted() -> None:
    # ADR-069 superseded ADR-024's hard one-round cap: distinct (non-duplicate)
    # requests execute up to the configured budget (default 3 rounds), and
    # only the round that would exceed it is blocked, producing a real
    # synthesized answer rather than a fixed rejection string.
    coordinator = FakeToolCoordinator(
        ToolExecutionResult(
            request_id="alpha:read_file",
            tool_name="read_file",
            status=ToolExecutionStatus.SUCCESS,
            content={"content": "notes"},
        )
    )
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="System prompt"),
        memory=FakeConversationStore(),
        model=SequenceModel(
            [
                '{"tool_call":{"name":"read_file","arguments":{"path":"one.txt"}}}',
                '{"tool_call":{"name":"read_file","arguments":{"path":"two.txt"}}}',
                '{"tool_call":{"name":"read_file","arguments":{"path":"three.txt"}}}',
                '{"tool_call":{"name":"read_file","arguments":{"path":"four.txt"}}}',
                "Here is what I found in the notes.",
            ]
        ),
        tool_detector=ToolCallDetector(),
        tool_coordinator=coordinator,
        session_id="alpha",
    )

    response = runtime.respond("Read notes")

    assert len(coordinator.requests) == 3
    assert response == Message(role="assistant", content="Here is what I found in the notes.")


def test_runtime_completes_list_directory_then_read_file_within_budget() -> None:
    # The literal FINDING-001 fix: a legitimate discovery-read flow that the
    # old one-round cap always blocked now succeeds within the default budget.
    coordinator = ScriptedCoordinator(
        [
            ToolExecutionResult(
                request_id="alpha:list_directory",
                tool_name="list_directory",
                status=ToolExecutionStatus.SUCCESS,
                content={"entries": ["AGENTS.md"]},
            ),
            ToolExecutionResult(
                request_id="alpha:read_file",
                tool_name="read_file",
                status=ToolExecutionStatus.SUCCESS,
                content={"content": "hexagonal architecture rules"},
            ),
        ]
    )
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="system"),
        memory=FakeConversationStore(),
        model=SequenceModel(
            [
                '{"tool_call":{"name":"list_directory","arguments":{"path":"."}}}',
                '{"tool_call":{"name":"read_file","arguments":{"path":"AGENTS.md"}}}',
                "The AGENTS.md file documents the hexagonal architecture rules.",
            ]
        ),
        tool_detector=ToolCallDetector(),
        tool_coordinator=coordinator,
        session_id="alpha",
    )

    response = runtime.respond("What does AGENTS.md say?")

    assert [request.tool_name for request in coordinator.requests] == ["list_directory", "read_file"]
    assert "hexagonal architecture rules" in response.content
    assert "Tool round limit reached" not in response.content


def test_runtime_rejects_duplicate_tool_call_without_re_executing() -> None:
    coordinator = FakeToolCoordinator(
        ToolExecutionResult(
            request_id="alpha:read_file",
            tool_name="read_file",
            status=ToolExecutionStatus.SUCCESS,
            content={"content": "notes"},
        )
    )
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="system"),
        memory=FakeConversationStore(),
        model=SequenceModel(
            [
                '{"tool_call":{"name":"read_file","arguments":{"path":"notes.txt"}}}',
                '{"tool_call":{"name":"read_file","arguments":{"path":"notes.txt"}}}',
                "I already have the notes content above.",
            ]
        ),
        tool_detector=ToolCallDetector(),
        tool_coordinator=coordinator,
        session_id="alpha",
    )

    response = runtime.respond("Read notes.txt twice")

    assert len(coordinator.requests) == 1  # the exact repeat was never executed
    assert response.content == "I already have the notes content above."


def test_runtime_rejects_duplicate_tool_call_after_an_identical_failure() -> None:
    # M5.2.15 adversarial scenario: "duplicate failure" — an exact repeat of
    # a call that already FAILED is rejected without re-executing, same as
    # an exact repeat of a success (DuplicateCallGuard does not care about
    # the prior outcome, since a byte-for-byte repeat can't add evidence).
    coordinator = FakeToolCoordinator(
        ToolExecutionResult(
            request_id="alpha:read_file",
            tool_name="read_file",
            status=ToolExecutionStatus.DENIED,
            error=SanitizedToolError("path_denied", "sanitized"),
        )
    )
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="system"),
        memory=FakeConversationStore(),
        model=SequenceModel(
            [
                '{"tool_call":{"name":"read_file","arguments":{"path":"missing.txt"}}}',
                '{"tool_call":{"name":"read_file","arguments":{"path":"missing.txt"}}}',
                "I could not read that file, and retrying would not help.",
            ]
        ),
        tool_detector=ToolCallDetector(),
        tool_coordinator=coordinator,
        session_id="alpha",
    )

    response = runtime.respond("Read missing.txt")

    assert len(coordinator.requests) == 1  # the exact repeat was never re-executed
    assert response.content == "I could not read that file, and retrying would not help."


def test_runtime_allows_a_changed_strategy_to_succeed_after_a_failure() -> None:
    # M5.2.15 adversarial scenario: "changed strategy after failure" — a
    # failed attempt does not block a genuinely different follow-up call
    # (different fingerprint) from executing and succeeding within budget.
    coordinator = ScriptedCoordinator(
        [
            ToolExecutionResult(
                request_id="alpha:read_file",
                tool_name="read_file",
                status=ToolExecutionStatus.DENIED,
                error=SanitizedToolError("path_denied", "sanitized"),
            ),
            ToolExecutionResult(
                request_id="alpha:read_file",
                tool_name="read_file",
                status=ToolExecutionStatus.SUCCESS,
                content={"content": "notes"},
            ),
        ]
    )
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="system"),
        memory=FakeConversationStore(),
        model=SequenceModel(
            [
                '{"tool_call":{"name":"read_file","arguments":{"path":"notes.txt.bak"}}}',
                '{"tool_call":{"name":"read_file","arguments":{"path":"notes.txt"}}}',
                "Found it under the corrected filename.",
            ]
        ),
        tool_detector=ToolCallDetector(),
        tool_coordinator=coordinator,
        session_id="alpha",
    )

    response = runtime.respond("Read notes.txt")

    assert [request.arguments["path"] for request in coordinator.requests] == [
        "notes.txt.bak",
        "notes.txt",
    ]
    assert response.content == "Found it under the corrected filename."


def test_runtime_completes_a_full_bounded_three_round_flow_without_exhaustion() -> None:
    # M5.2.15 adversarial scenario: "bounded three-round flow" — exactly at
    # the default budget boundary (max_model_tool_rounds=3), all three
    # distinct rounds execute and the turn completes naturally on the
    # model's own say-so, never touching the budget-exhaustion path at all.
    coordinator = ScriptedCoordinator(
        [
            ToolExecutionResult(
                request_id="alpha:read_file",
                tool_name="read_file",
                status=ToolExecutionStatus.SUCCESS,
                content={"content": "part 1"},
            ),
            ToolExecutionResult(
                request_id="alpha:read_file",
                tool_name="read_file",
                status=ToolExecutionStatus.SUCCESS,
                content={"content": "part 2"},
            ),
            ToolExecutionResult(
                request_id="alpha:read_file",
                tool_name="read_file",
                status=ToolExecutionStatus.SUCCESS,
                content={"content": "part 3"},
            ),
        ]
    )
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="system"),
        memory=FakeConversationStore(),
        model=SequenceModel(
            [
                '{"tool_call":{"name":"read_file","arguments":{"path":"one.txt"}}}',
                '{"tool_call":{"name":"read_file","arguments":{"path":"two.txt"}}}',
                '{"tool_call":{"name":"read_file","arguments":{"path":"three.txt"}}}',
                "Assembled all three parts into one answer.",
            ]
        ),
        tool_detector=ToolCallDetector(),
        tool_coordinator=coordinator,
        session_id="alpha",
    )

    response = runtime.respond("Read one.txt, two.txt and three.txt")

    assert len(coordinator.requests) == 3
    assert response.content == "Assembled all three parts into one answer."
    assert runtime.last_interaction_metrics.outcome == "tool_loop"
    assert runtime.last_interaction_metrics.tool_rounds == 3


def test_runtime_stops_via_progress_guard_after_repeated_failures() -> None:
    coordinator = FakeToolCoordinator(
        ToolExecutionResult(
            request_id="alpha:read_file",
            tool_name="read_file",
            status=ToolExecutionStatus.DENIED,
            error=SanitizedToolError("path_denied", "sanitized"),
        )
    )
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="system"),
        memory=FakeConversationStore(),
        model=SequenceModel(
            [
                '{"tool_call":{"name":"read_file","arguments":{"path":"one.txt"}}}',
                '{"tool_call":{"name":"read_file","arguments":{"path":"two.txt"}}}',
                '{"tool_call":{"name":"read_file","arguments":{"path":"three.txt"}}}',
                "I could not read any of the requested files.",
            ]
        ),
        tool_detector=ToolCallDetector(),
        tool_coordinator=coordinator,
        session_id="alpha",
    )

    response = runtime.respond("Read one.txt, then two.txt, then three.txt")

    assert len(coordinator.requests) == 2  # third distinct attempt blocked by the progress guard
    assert response.content == "I could not read any of the requested files."


def test_runtime_correlates_interaction_events_across_context_model_and_tool_stages() -> None:
    # ADR-070/FINDING-009: one turn must produce a correlated event stream
    # (context/retrieval, model request/response, tool activity, completion)
    # all sharing the same interaction_id.
    sink = RecordingInteractionLogger()
    coordinator = ScriptedCoordinator(
        [
            ToolExecutionResult(
                request_id="alpha:list_directory",
                tool_name="list_directory",
                status=ToolExecutionStatus.SUCCESS,
                content={"entries": ["AGENTS.md"]},
            ),
        ]
    )
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="system"),
        memory=FakeConversationStore(),
        model=SequenceModel(
            [
                '{"tool_call":{"name":"list_directory","arguments":{"path":"."}}}',
                "Here are the entries.",
            ]
        ),
        tool_detector=ToolCallDetector(),
        tool_coordinator=coordinator,
        interaction_diagnostics=sink,
        session_id="alpha",
    )

    runtime.respond("List the directory")

    interaction_id = runtime.last_interaction_id
    assert interaction_id
    stages = [event.stage for event in sink.events]
    assert InteractionStage.CONTEXT_RETRIEVAL in stages
    assert InteractionStage.MODEL_REQUEST in stages
    assert InteractionStage.MODEL_RESPONSE in stages
    assert InteractionStage.INTERACTION_COMPLETED in stages
    assert all(event.interaction_id == interaction_id for event in sink.events)
    assert all(event.session_id == "alpha" for event in sink.events)


def test_runtime_emits_final_synthesis_event_on_budget_exhaustion() -> None:
    sink = RecordingInteractionLogger()
    coordinator = FakeToolCoordinator(
        ToolExecutionResult(
            request_id="alpha:read_file",
            tool_name="read_file",
            status=ToolExecutionStatus.SUCCESS,
            content={"content": "notes"},
        )
    )
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="system"),
        memory=FakeConversationStore(),
        model=SequenceModel(
            [
                '{"tool_call":{"name":"read_file","arguments":{"path":"one.txt"}}}',
                '{"tool_call":{"name":"read_file","arguments":{"path":"two.txt"}}}',
                '{"tool_call":{"name":"read_file","arguments":{"path":"three.txt"}}}',
                '{"tool_call":{"name":"read_file","arguments":{"path":"four.txt"}}}',
                "Here is what I found in the notes.",
            ]
        ),
        tool_detector=ToolCallDetector(),
        tool_coordinator=coordinator,
        interaction_diagnostics=sink,
        session_id="alpha",
    )

    runtime.respond("Read notes")

    synthesis_events = [
        event for event in sink.events if event.stage == InteractionStage.FINAL_SYNTHESIS
    ]
    assert len(synthesis_events) == 1
    assert synthesis_events[0].payload["reason"] == "tool_loop_budget_exhausted"
    assert synthesis_events[0].payload["fallback_used"] is False


def test_runtime_reports_interaction_metrics_for_a_direct_model_answer() -> None:
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="system"),
        memory=FakeConversationStore(),
        model=MetadataModel(
            "Echo",
            finish_reason=FinishReason.LENGTH,
            prompt_tokens=12,
            output_tokens=34,
            truncated=True,
        ),
        tool_detector=ToolCallDetector(),
        session_id="alpha",
    )

    runtime.respond("Hello")

    metrics = runtime.last_interaction_metrics
    assert metrics is not None
    assert metrics.outcome == "direct_answer"
    assert metrics.model_calls == 1
    assert metrics.finish_reason == FinishReason.LENGTH
    assert metrics.prompt_tokens == 12
    assert metrics.output_tokens == 34
    assert metrics.truncated is True
    assert metrics.tool_rounds == 0
    assert metrics.tool_requests == 0
    assert metrics.executor_operations == 0
    assert metrics.retrieval_attempted is False


def test_runtime_does_not_redact_token_counts_in_interaction_diagnostics(tmp_path) -> None:
    # Regression: `redact_sensitive` matches "token"/"prompt" as substrings,
    # so a naively-named "prompt_tokens"/"output_tokens" JSONL payload key
    # would be silently blanked to "[redacted]" even though a token *count*
    # is not a secret. Verified through the real JSONL sink (in-memory event
    # objects skip sanitization entirely, so this must round-trip through
    # `JsonlInteractionDiagnosticLogger` to actually exercise the bug).
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="system"),
        memory=FakeConversationStore(),
        model=MetadataModel("Echo", prompt_tokens=12, output_tokens=34),
        tool_detector=ToolCallDetector(),
        interaction_diagnostics=JsonlInteractionDiagnosticLogger(tmp_path),
        model_provider_name="ollama",
        model_name="qwen3.5:4b",
        session_id="alpha",
    )

    runtime.respond("Hello")

    files = list(tmp_path.iterdir())
    assert len(files) == 1
    rows = [json.loads(line) for line in files[0].read_text(encoding="utf-8").splitlines()]
    completed = next(row for row in rows if row["stage"] == "interaction_completed")
    response_row = next(row for row in rows if row["stage"] == "model_response")
    assert completed["payload"]["input_length"] == 12
    assert completed["payload"]["output_length"] == 34
    assert response_row["payload"]["input_length"] == 12
    assert response_row["payload"]["output_length"] == 34


def test_runtime_coordinates_context_budget_with_ollama_generation_limits() -> None:
    # FINDING-008 (ADR-071): the application-level context budget and the
    # Ollama-side generation limits are configured independently; this
    # asserts they land in one observable record instead of staying two
    # numbers an operator would have to cross-reference by hand.
    sink = RecordingInteractionLogger()
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="system"),
        conversation_context=ConversationContextService(
            ContextBuilder(system_prompt="system"),
            ConversationContextBudget(provider_context_window=4096, reserved_output_tokens=512),
        ),
        memory=FakeConversationStore(),
        model=FakeModel("ok"),
        tool_detector=ToolCallDetector(),
        interaction_diagnostics=sink,
        ollama_num_ctx=2048,
        ollama_num_predict=256,
        session_id="alpha",
    )

    runtime.respond("Hello")

    context_event = next(
        event for event in sink.events if event.stage == InteractionStage.CONTEXT_RETRIEVAL
    )
    assert context_event.payload["provider_context_window"] == 4096
    assert context_event.payload["reserved_output_length"] == 512
    assert context_event.payload["max_input_length"] == 3584
    assert context_event.payload["model_num_ctx"] == 2048
    assert context_event.payload["model_num_predict"] == 256


def test_runtime_context_budget_coordination_survives_jsonl_redaction(tmp_path) -> None:
    # Regression: the in-memory sink above never exercises `redact_sensitive`
    # at all, so it would pass even if these payload keys collided with the
    # sanitizer's "token" substring match (as `reserved_output_tokens`/
    # `max_input_tokens` originally did). Round-trip through the real JSONL
    # logger to prove the numbers actually survive.
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="system"),
        conversation_context=ConversationContextService(
            ContextBuilder(system_prompt="system"),
            ConversationContextBudget(provider_context_window=4096, reserved_output_tokens=512),
        ),
        memory=FakeConversationStore(),
        model=FakeModel("ok"),
        tool_detector=ToolCallDetector(),
        interaction_diagnostics=JsonlInteractionDiagnosticLogger(tmp_path),
        ollama_num_ctx=2048,
        ollama_num_predict=256,
        session_id="alpha",
    )

    runtime.respond("Hello")

    files = list(tmp_path.iterdir())
    rows = [json.loads(line) for line in files[0].read_text(encoding="utf-8").splitlines()]
    context_row = next(row for row in rows if row["stage"] == "context_retrieval")
    assert context_row["payload"]["provider_context_window"] == 4096
    assert context_row["payload"]["reserved_output_length"] == 512
    assert context_row["payload"]["max_input_length"] == 3584
    assert context_row["payload"]["model_num_ctx"] == 2048
    assert context_row["payload"]["model_num_predict"] == 256


def test_runtime_reports_interaction_metrics_for_a_bounded_tool_loop() -> None:
    coordinator = ScriptedCoordinator(
        [
            ToolExecutionResult(
                request_id="alpha:list_directory",
                tool_name="list_directory",
                status=ToolExecutionStatus.SUCCESS,
                content={"entries": ["AGENTS.md"]},
            ),
            ToolExecutionResult(
                request_id="alpha:read_file",
                tool_name="read_file",
                status=ToolExecutionStatus.SUCCESS,
                content={"content": "hexagonal architecture rules"},
                executor_operations=3,
            ),
        ]
    )
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="system"),
        memory=FakeConversationStore(),
        model=SequenceModel(
            [
                '{"tool_call":{"name":"list_directory","arguments":{"path":"."}}}',
                '{"tool_call":{"name":"read_file","arguments":{"path":"AGENTS.md"}}}',
                "The AGENTS.md file documents the hexagonal architecture rules.",
            ]
        ),
        tool_detector=ToolCallDetector(),
        tool_coordinator=coordinator,
        session_id="alpha",
    )

    runtime.respond("What does AGENTS.md say?")

    metrics = runtime.last_interaction_metrics
    assert metrics is not None
    assert metrics.outcome == "tool_loop"
    assert metrics.model_calls == 3
    assert metrics.tool_rounds == 2
    assert metrics.tool_requests == 2
    assert metrics.executor_operations == 4  # 1 (list_directory) + 3 (read_file recovery)
    assert metrics.recovery_operations == 2  # only read_file's extra 2 operations count


def test_runtime_persists_tool_round_atomically() -> None:
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="System prompt"),
        memory=FailingTurnStore(),
        model=SequenceModel(
            [
                '{"tool_call":{"name":"read_file","arguments":{"path":"notes.txt"}}}',
                "Final answer",
            ]
        ),
        tool_detector=ToolCallDetector(),
        tool_coordinator=FakeToolCoordinator(
            ToolExecutionResult(
                request_id="alpha:read_file",
                tool_name="read_file",
                status=ToolExecutionStatus.SUCCESS,
                content={"content": "notes"},
            )
        ),
        session_id="alpha",
    )

    with pytest.raises(RuntimeError, match="store failed"):
        runtime.respond("Read notes")


class FailingTurnStore(ConversationMemory):
    def __init__(self) -> None:
        self._messages: list[Message] = []

    def append(self, session_id: SessionId, message: Message) -> None:
        self.append_many(session_id, [message])

    def append_many(self, session_id: SessionId, messages: list[Message]) -> None:
        raise RuntimeError("store failed")

    def history(self, session_id: SessionId) -> list[Message]:
        return list(self._messages)


class FakeConversationStore(ConversationMemory):
    def __init__(self) -> None:
        self._messages: list[Message] = []

    def append(self, session_id: SessionId, message: Message) -> None:
        self.append_many(session_id, [message])

    def append_many(self, session_id: SessionId, messages: list[Message]) -> None:
        self._messages.extend(
            Message(
                role=message.role,
                content=message.content,
                session_id=session_id,
                tool_name=message.tool_name,
                tool_call_id=message.tool_call_id,
            )
            for message in messages
        )

    def history(self, session_id: SessionId) -> list[Message]:
        return [
            message for message in self._messages if message.session_id == session_id
        ]


class FakeModel(ModelProvider):
    def __init__(self, response: str) -> None:
        self._response = response

    def chat(self, messages: list[Message]) -> ModelResponse:
        return ModelResponse(
            message=Message(role="assistant", content=self._response),
            finish_reason=FinishReason.STOP,
        )


class SequenceModel(ModelProvider):
    def __init__(self, responses: list[str]) -> None:
        self._responses = responses
        self.calls: list[list[Message]] = []

    def chat(self, messages: list[Message]) -> ModelResponse:
        self.calls.append(messages)
        return ModelResponse(
            message=Message(role="assistant", content=self._responses.pop(0)),
            finish_reason=FinishReason.STOP,
        )


class MetadataModel(ModelProvider):
    def __init__(
        self,
        response: str,
        *,
        finish_reason: FinishReason = FinishReason.STOP,
        prompt_tokens: int | None = None,
        output_tokens: int | None = None,
        truncated: bool = False,
    ) -> None:
        self._response = response
        self._finish_reason = finish_reason
        self._prompt_tokens = prompt_tokens
        self._output_tokens = output_tokens
        self._truncated = truncated

    def chat(self, messages: list[Message]) -> ModelResponse:
        return ModelResponse(
            message=Message(role="assistant", content=self._response),
            finish_reason=self._finish_reason,
            prompt_tokens=self._prompt_tokens,
            output_tokens=self._output_tokens,
            truncated=self._truncated,
        )


class RecordingInteractionLogger:
    def __init__(self) -> None:
        self.events: list[InteractionLogEvent] = []

    def record(self, event: InteractionLogEvent) -> None:
        self.events.append(event)


class FakeToolCoordinator:
    def __init__(self, result: ToolExecutionResult) -> None:
        self.result = result
        self.requests: list[ToolExecutionRequest] = []

    def execute(self, request: ToolExecutionRequest) -> ToolExecutionResult:
        self.requests.append(request)
        return self.result


class ScriptedCoordinator:
    def __init__(self, results: list[ToolExecutionResult]) -> None:
        self._results = results
        self.requests: list[ToolExecutionRequest] = []

    def execute(self, request: ToolExecutionRequest) -> ToolExecutionResult:
        self.requests.append(request)
        return self._results.pop(0)


class EmptyContextProvider:
    def __init__(self) -> None:
        self.calls = 0

    def build(self, _text: str) -> CompiledContext:
        self.calls += 1
        return CompiledContext(ContextPurpose.CONVERSATION, (), ContextBudget())


class AllowPolicy:
    def allow(self, _text: str, *, context_enabled: bool) -> bool:
        return context_enabled
