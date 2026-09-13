"""Tests for conversation knowledge context provider."""

from ai_assistant.infrastructure.storage.sqlite_knowledge import SQLiteKnowledgeStore
from ai_assistant.knowledge import (
    ContextCompiler,
    ContextPurpose,
    ConversationKnowledgeContextProvider,
    HybridRetriever,
    KnowledgeChunk,
    KnowledgeDocument,
    KnowledgeRanker,
    KnowledgeSourceType,
)


def test_conversation_knowledge_context_provider_compiles_conversation_context(tmp_path) -> None:
    store = SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3")
    store.save_document(KnowledgeDocument("doc-1", KnowledgeSourceType.FILE, "README.md", "v1", "doc-hash"))
    store.save_chunks("doc-1", (KnowledgeChunk("chunk-1", "doc-1", "blacksmith setup", 0, 2, "chunk-hash"),))
    provider = ConversationKnowledgeContextProvider(
        HybridRetriever(store),
        KnowledgeRanker(),
        ContextCompiler(store),
    )

    context = provider.build("blacksmith")

    assert context.purpose == ContextPurpose.CONVERSATION
    assert context.evidence[0].text == "blacksmith setup"
    assert provider.last_metrics is not None
    assert provider.last_metrics.knowledge_chunks_selected == 1


def test_conversation_knowledge_context_provider_answers_generic_project_summary_query(tmp_path) -> None:
    store = SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3")
    store.save_document(KnowledgeDocument("doc-1", KnowledgeSourceType.FILE, "README.md", "v1", "doc-hash"))
    store.save_chunks(
        "doc-1",
        (
            KnowledgeChunk(
                "chunk-1",
                "doc-1",
                "AI Assistant is a local-first assistant with Context and Knowledge Engine support.",
                0,
                11,
                "chunk-hash",
            ),
        ),
    )
    provider = ConversationKnowledgeContextProvider(
        HybridRetriever(store),
        KnowledgeRanker(),
        ContextCompiler(store),
    )

    context = provider.build("¿Que hace este proyecto?")

    assert context.evidence
    assert provider.last_metrics is not None
    assert provider.last_metrics.knowledge_candidates >= 1


def test_conversation_knowledge_context_limits_single_source_evidence(tmp_path) -> None:
    store = SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3")
    store.save_document(KnowledgeDocument("doc-1", KnowledgeSourceType.FILE, "README.md", "v1", "doc-hash"))
    store.save_chunks(
        "doc-1",
        tuple(
            KnowledgeChunk(
                f"chunk-{index}",
                "doc-1",
                f"timer schedule documentation {index}",
                index,
                4,
                f"chunk-{index}-hash",
            )
            for index in range(5)
        ),
    )
    provider = ConversationKnowledgeContextProvider(
        HybridRetriever(store),
        KnowledgeRanker(),
        ContextCompiler(store),
    )

    context = provider.build("timer schedule")

    assert len(context.evidence) == 3
    assert all("timer schedule" in item.text for item in context.evidence)
    assert provider.last_metrics is not None
    assert provider.last_metrics.knowledge_candidates == 5
    assert provider.last_metrics.knowledge_chunks_selected == 3
    assert provider.last_metrics.unique_sources_selected == 1
