"""Tests for planner context integration."""

import json

import pytest

from ai_assistant.application.ports.models import ModelProvider
from ai_assistant.application.tool_catalog import StaticToolCatalog
from ai_assistant.infrastructure.storage.sqlite_knowledge import SQLiteKnowledgeStore
from ai_assistant.knowledge import (
    ContextCompiler,
    HybridRetriever,
    KnowledgeChunk,
    KnowledgeDocument,
    KnowledgeRanker,
    KnowledgeSourceType,
    PlanningContextProvider,
)
from ai_assistant.platform.application import ModelBackedPlanner, StaticCapabilityRegistry
from ai_assistant.platform.domain import Objective
from ai_assistant.domain.message import Message
from ai_assistant.domain.model_response import FinishReason, ModelResponse


pytestmark = pytest.mark.unit


def test_model_backed_planner_includes_compiled_context(tmp_path) -> None:
    store = SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3")
    store.save_document(KnowledgeDocument("doc-1", KnowledgeSourceType.FILE, "README.md", "v1", "doc-hash"))
    store.save_chunks("doc-1", (KnowledgeChunk("chunk-1", "doc-1", "blacksmith setup", 0, 2, "chunk-hash"),))
    model = _Model()
    provider = PlanningContextProvider(HybridRetriever(store), KnowledgeRanker(), ContextCompiler(store))
    planner = ModelBackedPlanner(
        model,
        StaticCapabilityRegistry(StaticToolCatalog()),
        provider,
    )

    planner.create_plan(Objective("obj-1", "blacksmith"))

    payload = json.loads(model.messages[1].content)
    assert payload["compiled_context"][0]["chunk_id"] == "chunk-1"
    assert payload["compiled_context"][0]["text"] == "blacksmith setup"
    assert provider.last_metrics is not None
    assert provider.last_metrics.knowledge_candidates == 1
    assert provider.last_metrics.knowledge_chunks_selected == 1


class _Model(ModelProvider):
    def __init__(self) -> None:
        self.messages: list[Message] = []

    def chat(self, messages: list[Message]) -> ModelResponse:
        self.messages = messages
        return ModelResponse(
            message=Message(
                role="assistant",
                content='{"plan_id":"plan-1","tasks":[{"capability":"InspectDirectory","arguments":{"path":"."}}]}',
            ),
            finish_reason=FinishReason.STOP,
        )
