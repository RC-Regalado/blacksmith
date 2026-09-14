"""End-to-end Phase 5.1 conversation scenarios."""

import pytest

from ai_assistant.agent.message import FinishReason, Message, ModelResponse
from ai_assistant.agent.planner import ToolCallDetector
from ai_assistant.agent.runtime import AgentRuntime
from ai_assistant.application.context import ContextBuilder
from ai_assistant.application.conversation_context import ConversationContextService
from ai_assistant.domain.tools import ToolExecutionResult, ToolExecutionStatus
from ai_assistant.infrastructure.storage.sqlite_knowledge import SQLiteKnowledgeStore
from ai_assistant.knowledge import (
    ContextCompiler,
    ConversationKnowledgeContextProvider,
    ConversationRetrievalPolicy,
    HybridRetriever,
    KnowledgeChunk,
    KnowledgeDocument,
    KnowledgeRanker,
    KnowledgeSourceType,
)

from tests.test_agent_runtime import FakeConversationStore, FakeToolCoordinator


pytestmark = pytest.mark.unit


def test_plain_chat_skips_retrieval_and_tools() -> None:
    provider = CountingProvider()
    model = InspectingModel(["hello back"])
    runtime = _runtime(
        model,
        context_provider=provider,
        include_knowledge_context=False,
    )

    response = runtime.respond("Hello")

    assert response.content == "hello back"
    assert provider.calls == 0
    assert runtime.last_tool_plan.has_tool_call is False


def test_context_aware_project_chat_uses_fresh_knowledge_without_tool_call(tmp_path) -> None:
    store = _knowledge_store(tmp_path, stale=False)
    model = InspectingModel(["ExecutionEngine validates plans using PlanValidator evidence."])
    runtime = _runtime(
        model,
        context_provider=_provider(store),
        include_knowledge_context=True,
    )

    response = runtime.respond("Explain how ExecutionEngine validates plans.")

    context_text = "\n".join(message.content for message in model.calls[0])
    assert "Explain how ExecutionEngine validates plans with PlanValidator" in context_text
    assert response.content.startswith("ExecutionEngine validates")
    assert runtime.last_tool_plan.has_tool_call is False
    assert runtime.tool_coordinator is None


def test_live_state_question_uses_git_status_tool_not_indexed_knowledge(tmp_path) -> None:
    store = _knowledge_store(tmp_path, stale=False)
    model = InspectingModel(
        [
            '{"tool_call":{"name":"git_status","arguments":{"path":"."}}}',
            "Live Git status is clean.",
        ]
    )
    coordinator = FakeToolCoordinator(
        ToolExecutionResult(
            request_id="alpha:git_status",
            tool_name="git_status",
            status=ToolExecutionStatus.SUCCESS,
            content={"entries": []},
        )
    )
    runtime = _runtime(
        model,
        context_provider=_provider(store),
        include_knowledge_context=True,
        tool_coordinator=coordinator,
    )

    response = runtime.respond("What is currently changed in Git?")

    assert response.content == "Live Git status is clean."
    assert [request.tool_name for request in coordinator.requests] == ["git_status"]
    assert all(
        "Explain how ExecutionEngine validates plans with PlanValidator" not in message.content
        for message in model.calls[0]
    )


def test_empty_and_stale_knowledge_emit_diagnostic_without_rebuild(tmp_path) -> None:
    empty_store = SQLiteKnowledgeStore(tmp_path / "empty.sqlite3")
    stale_store = _knowledge_store(tmp_path, stale=True)

    empty_runtime = _runtime(
        InspectingModel(["fallback"]),
        context_provider=_provider(empty_store),
        include_knowledge_context=True,
    )
    stale_runtime = _runtime(
        InspectingModel(["fallback"]),
        context_provider=_provider(stale_store),
        include_knowledge_context=True,
    )

    empty_runtime.respond("Explain how ExecutionEngine validates plans.")
    stale_runtime.respond("Explain how ExecutionEngine validates plans.")

    assert "no fresh indexed knowledge matched" in empty_runtime.last_context_diagnostic
    assert "No rebuild was run." in empty_runtime.last_context_diagnostic
    assert "no fresh indexed knowledge matched" in stale_runtime.last_context_diagnostic
    assert "Explain how ExecutionEngine validates plans with PlanValidator" not in "\n".join(
        message.content for message in stale_runtime.model.calls[0]
    )


def _runtime(
    model,
    *,
    context_provider,
    include_knowledge_context: bool,
    tool_coordinator=None,
) -> AgentRuntime:
    return AgentRuntime(
        context_builder=ContextBuilder("system"),
        conversation_context=ConversationContextService(
            ContextBuilder("system"),
            context_provider=context_provider,
            retrieval_policy=ConversationRetrievalPolicy(),
        ),
        memory=FakeConversationStore(),
        model=model,
        tool_detector=ToolCallDetector(),
        tool_coordinator=tool_coordinator,
        include_knowledge_context=include_knowledge_context,
        session_id="alpha",
    )


def _knowledge_store(tmp_path, *, stale: bool) -> SQLiteKnowledgeStore:
    store = SQLiteKnowledgeStore(tmp_path / ("stale.sqlite3" if stale else "fresh.sqlite3"))
    store.save_document(KnowledgeDocument("doc-1", KnowledgeSourceType.FILE, "README.md", "v1", "doc-hash"))
    store.save_chunks(
        "doc-1",
        (
            KnowledgeChunk(
                "chunk-1",
                "doc-1",
                "Explain how ExecutionEngine validates plans with PlanValidator",
                0,
                6,
                "hash-1",
            ),
        ),
    )
    if stale:
        store.mark_document_stale("doc-1")
    return store


def _provider(store: SQLiteKnowledgeStore) -> ConversationKnowledgeContextProvider:
    return ConversationKnowledgeContextProvider(
        HybridRetriever(store),
        KnowledgeRanker(),
        ContextCompiler(store),
    )


class CountingProvider:
    calls = 0
    last_metrics = None

    def build(self, _text: str):
        self.calls += 1
        raise AssertionError("retrieval should be skipped")


class InspectingModel:
    def __init__(self, responses: list[str]) -> None:
        self._responses = responses
        self.calls: list[list[Message]] = []

    def chat(self, messages: list[Message]) -> ModelResponse:
        self.calls.append(messages)
        return ModelResponse(
            message=Message(role="assistant", content=self._responses.pop(0)),
            finish_reason=FinishReason.STOP,
        )
