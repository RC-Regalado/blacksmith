"""Phase 5.1 adversarial and regression checklist."""

import builtins

import pytest

from ai_assistant.agent.message import Message
from ai_assistant.agent.planner import ToolCallDetector
from ai_assistant.agent.runtime import AgentRuntime
from ai_assistant.application.context import ContextBuilder
from ai_assistant.application.conversation_context import ConversationContextService
from ai_assistant.domain.tools import ToolExecutionResult, ToolExecutionStatus
from ai_assistant.interfaces.cli.app import CliApplication
from ai_assistant.knowledge import (
    CompiledContext,
    ContextBudget,
    ContextCompiler,
    ContextEvidence,
    ContextPurpose,
    ConversationKnowledgeContextProvider,
    ConversationRetrievalPolicy,
    FreshnessStatus,
    HybridRetriever,
    KnowledgeChunk,
    KnowledgeDocument,
    KnowledgeRanker,
    KnowledgeSourceType,
    RetrievalCandidate,
)

from tests.test_agent_runtime import (
    EmptyContextProvider,
    FakeConversationStore,
    FakeToolCoordinator,
    SequenceModel,
)


pytestmark = pytest.mark.unit


def test_context_disabled_and_enabled_empty_paths() -> None:
    provider = EmptyContextProvider()
    service = ConversationContextService(
        ContextBuilder("system"),
        context_provider=provider,
        retrieval_policy=ConversationRetrievalPolicy(),
    )

    disabled = service.build_with_retrieval([], "Explain project architecture")
    empty = service.build_with_retrieval([], "Explain project architecture", include_knowledge=True)

    assert [message.role for message in disabled] == ["system", "user"]
    assert provider.calls == 1
    assert "no fresh indexed knowledge matched" in empty[1].content


def test_context_enabled_with_stale_index_excludes_stale_knowledge(tmp_path) -> None:
    from ai_assistant.infrastructure.storage.sqlite_knowledge import SQLiteKnowledgeStore

    store = SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3")
    store.save_document(KnowledgeDocument("doc-1", KnowledgeSourceType.FILE, "README.md", "v1", "doc-hash"))
    store.save_chunks("doc-1", (KnowledgeChunk("chunk-1", "doc-1", "blacksmith stale text", 0, 3, "hash-1"),))
    store.mark_document_stale("doc-1")
    service = ConversationContextService(
        ContextBuilder("system"),
        context_provider=ConversationKnowledgeContextProvider(
            HybridRetriever(store),
            KnowledgeRanker(),
            ContextCompiler(store),
        ),
        retrieval_policy=ConversationRetrievalPolicy(),
    )

    messages = service.build_with_retrieval([], "Explain blacksmith architecture", include_knowledge=True)

    assert "blacksmith stale text" not in "\n".join(message.content for message in messages)
    assert "no fresh indexed knowledge matched" in messages[1].content


def test_short_chat_project_query_and_live_state_policy() -> None:
    policy = ConversationRetrievalPolicy()

    assert policy.allow("ok", context_enabled=True) is False
    assert policy.allow("Explain ExecutionEngine architecture", context_enabled=True) is True
    assert policy.allow("What is currently changed in Git?", context_enabled=True) is False


def test_tool_policy_path_preserved_for_context_enabled_live_state() -> None:
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
        context_builder=ContextBuilder("system"),
        conversation_context=ConversationContextService(
            ContextBuilder("system"),
            context_provider=provider,
            retrieval_policy=ConversationRetrievalPolicy(),
        ),
        memory=FakeConversationStore(),
        model=SequenceModel(
            [
                '{"tool_call":{"name":"git_status","arguments":{"path":"."}}}',
                "live state answer",
            ]
        ),
        tool_detector=ToolCallDetector(),
        tool_coordinator=coordinator,
        include_knowledge_context=True,
        session_id="alpha",
    )

    runtime.respond("What is currently changed in Git?")

    assert provider.calls == 0
    assert [request.tool_name for request in coordinator.requests] == ["git_status"]


def test_project_summary_query_expansion_does_not_override_live_state_bypass() -> None:
    provider = EmptyContextProvider()
    service = ConversationContextService(
        ContextBuilder("system"),
        context_provider=provider,
        retrieval_policy=ConversationRetrievalPolicy(),
    )

    messages = service.build_with_retrieval(
        [],
        "What is the current project git status?",
        include_knowledge=True,
    )

    assert [message.role for message in messages] == ["system", "user"]
    assert provider.calls == 0


def test_budget_overflow_and_provenance_preservation(tmp_path) -> None:
    from ai_assistant.infrastructure.storage.sqlite_knowledge import SQLiteKnowledgeStore

    store = SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3")
    store.save_document(KnowledgeDocument("doc-1", KnowledgeSourceType.FILE, "README.md", "v1", "doc-hash"))
    store.save_chunks("doc-1", (KnowledgeChunk("chunk-1", "doc-1", "too many tokens", 0, 3, "hash-1"),))
    candidate = RetrievalCandidate(
        "chunk-1",
        "doc-1",
        KnowledgeSourceType.FILE,
        "README.md",
        "v1",
        "hash-1",
        1.0,
        "fts5",
        3,
        FreshnessStatus.FRESH,
    )

    ranked = KnowledgeRanker().rank((candidate,), 1)
    overflow = ContextCompiler(store).compile(
        ContextPurpose.CONVERSATION,
        ranked,
        ContextBudget(max_context_tokens=2, max_sources=1, max_chunks=1, max_chunk_tokens=2),
    )
    compiled = ContextCompiler(store).compile(
        ContextPurpose.CONVERSATION,
        ranked,
        ContextBudget(max_context_tokens=8, max_sources=1, max_chunks=1, max_chunk_tokens=8),
    )

    assert overflow.evidence == ()
    assert compiled.evidence == (ContextEvidence(candidate, "too many tokens"),)


def test_metrics_disabled_enabled_and_malformed_cli_args(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    inputs = iter(["hello", "quit"])
    monkeypatch.setattr(builtins, "input", lambda _prompt: next(inputs))

    CliApplication(MetricsRuntime()).run(("chat", "--context"))

    output = capsys.readouterr().out
    assert "context_conversation:" not in output

    inputs = iter(["hello", "quit"])
    monkeypatch.setattr(builtins, "input", lambda _prompt: next(inputs))
    CliApplication(MetricsRuntime()).run(("chat", "--context", "--metrics"))
    CliApplication(MetricsRuntime()).run(("chat", "bogus"))

    output = capsys.readouterr().out
    assert "context_conversation: candidates=1 ranked=1 selected=1" in output
    assert "Usage: python main.py chat [--context] [--metrics]" in output


class MetricsRuntime:
    include_knowledge_context = False
    last_context_diagnostic = None
    last_context_metrics = type(
        "Metrics",
        (),
        {
            "knowledge_candidates": 1,
            "ranked_candidates": 1,
            "knowledge_chunks_selected": 1,
            "raw_context_estimated_tokens": 2,
            "compiled_context_estimated_tokens": 1,
            "context_reduction_ratio": 0.5,
        },
    )()

    def respond(self, _user_input: str) -> Message:
        return Message(role="assistant", content="ok")
