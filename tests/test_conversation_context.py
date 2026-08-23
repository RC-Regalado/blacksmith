"""Tests for conversation context assembly."""

import pytest

from ai_assistant.application.context import ContextBuilder
from ai_assistant.application.conversation_context import ConversationContextService
from ai_assistant.domain.errors import InvalidKnowledgeError
from ai_assistant.domain.message import Message
from ai_assistant.knowledge import (
    CompiledContext,
    ContextBudget,
    ContextEvidence,
    ContextPurpose,
    FreshnessStatus,
    KnowledgeSourceType,
    RetrievalCandidate,
)


pytestmark = pytest.mark.unit


def test_conversation_context_excludes_knowledge_by_default() -> None:
    service = ConversationContextService(ContextBuilder("system"))

    messages = service.build([Message(role="assistant", content="prior")], "question", _compiled())

    assert [message.role for message in messages] == ["system", "assistant", "user"]
    assert all("Relevant derived knowledge" not in message.content for message in messages)


def test_conversation_context_includes_separate_knowledge_when_enabled() -> None:
    service = ConversationContextService(ContextBuilder("system"))

    messages = service.build([], "question", _compiled(), include_knowledge=True)

    assert [message.role for message in messages] == ["system", "system", "user"]
    assert "Relevant derived knowledge" in messages[1].content
    assert "README.md#chunk-1" in messages[1].content
    assert messages[-1].content == "question"


def test_conversation_context_enforces_total_budget() -> None:
    service = ConversationContextService(ContextBuilder("system"), max_total_context_tokens=1)

    messages = service.build([], "question", _compiled(), include_knowledge=True)

    assert [message.role for message in messages] == ["system", "user"]


def test_conversation_context_rejects_planning_context() -> None:
    service = ConversationContextService(ContextBuilder("system"))

    with pytest.raises(InvalidKnowledgeError, match="conversation-purpose"):
        service.build([], "question", _compiled(ContextPurpose.PLANNING), include_knowledge=True)


def test_conversation_context_retrieval_empty_index_adds_visible_diagnostic() -> None:
    service = ConversationContextService(
        ContextBuilder("system"),
        context_provider=EmptyProvider(),
    )

    messages = service.build_with_retrieval([], "question", include_knowledge=True)

    assert "no fresh indexed knowledge matched" in messages[1].content
    assert service.last_diagnostic == messages[1].content
    assert messages[-1].content == "question"


def test_conversation_context_retrieval_disabled_does_not_call_retriever() -> None:
    provider = EmptyProvider()
    service = ConversationContextService(
        ContextBuilder("system"),
        context_provider=provider,
    )

    messages = service.build_with_retrieval([], "question")

    assert provider.calls == 0
    assert service.last_diagnostic is None
    assert [message.role for message in messages] == ["system", "user"]


def test_conversation_context_policy_bypasses_retrieval() -> None:
    provider = EmptyProvider()
    service = ConversationContextService(
        ContextBuilder("system"),
        context_provider=provider,
        retrieval_policy=BypassPolicy(),
    )

    messages = service.build_with_retrieval([], "ok", include_knowledge=True)

    assert provider.calls == 0
    assert [message.role for message in messages] == ["system", "user"]


def _compiled(purpose: ContextPurpose = ContextPurpose.CONVERSATION) -> CompiledContext:
    candidate = RetrievalCandidate(
        "chunk-1",
        "doc-1",
        KnowledgeSourceType.FILE,
        "README.md",
        "v1",
        "hash",
        1.0,
        "fts5",
        2,
        FreshnessStatus.FRESH,
    )
    return CompiledContext(
        purpose,
        (ContextEvidence(candidate, "blacksmith setup"),),
        ContextBudget(max_context_tokens=8, max_sources=1, max_chunks=1, max_chunk_tokens=8),
    )


class EmptyProvider:
    def __init__(self) -> None:
        self.calls = 0

    def build(self, _text: str) -> CompiledContext:
        self.calls += 1
        return CompiledContext(ContextPurpose.CONVERSATION, (), ContextBudget())


class BypassPolicy:
    def allow(self, _text: str, *, context_enabled: bool) -> bool:
        return False
