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
