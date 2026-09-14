"""Tests for synthesis context integration."""

from ai_assistant.application.tool_coordinator import ToolExecutionCoordinator
from ai_assistant.domain.tools import ToolExecutionRequest, ToolExecutionResult, ToolExecutionStatus
from ai_assistant.infrastructure.storage.sqlite_knowledge import SQLiteKnowledgeStore
from ai_assistant.knowledge import (
    ContextCompiler,
    HybridRetriever,
    KnowledgeChunk,
    KnowledgeDocument,
    KnowledgeRanker,
    KnowledgeSourceType,
    SynthesisContextProvider,
)
from ai_assistant.platform.application import (
    BudgetManager,
    CheckpointService,
    DeterministicPlanner,
    ExecutionEngine,
    ObjectiveEvaluator,
    PlanValidator,
    StaticCapabilityRegistry,
    TaskScheduler,
)
from ai_assistant.platform.domain import CapabilityName, ExecutionBudget, Objective, Plan, PlatformTask
from tests.test_platform_execution_engine import _Registry, _Store


def test_execution_engine_adds_synthesis_context_without_changing_evidence(tmp_path) -> None:
    store = SQLiteKnowledgeStore(tmp_path / "knowledge.sqlite3")
    store.save_document(KnowledgeDocument("doc-1", KnowledgeSourceType.FILE, "README.md", "v1", "doc-hash"))
    store.save_chunks("doc-1", (KnowledgeChunk("chunk-1", "doc-1", "blacksmith setup", 0, 2, "chunk-hash"),))
    objective = Objective("obj-1", "blacksmith", success_criteria=("task-1:list_directory:success",))
    plan = Plan("plan-1", "obj-1", (PlatformTask("task-1", "obj-1", "List", CapabilityName.INSPECT_DIRECTORY, {"path": "."}),))
    provider = SynthesisContextProvider(HybridRetriever(store), KnowledgeRanker(), ContextCompiler(store))
    engine = _engine(plan, provider)

    outcome = engine.run(objective, "session-1", ExecutionBudget())

    assert outcome.result.evidence == ("task-1:list_directory:success",)
    assert "Context README.md: blacksmith setup" in outcome.result.observations
    assert provider.last_metrics is not None
    assert provider.last_metrics.knowledge_candidates == 1


def _engine(plan: Plan, synthesis) -> ExecutionEngine:
    registry = _Registry()
    store = _Store()
    return ExecutionEngine(
        DeterministicPlanner({"obj-1": plan}),
        PlanValidator(registry),
        registry,
        TaskScheduler(store),
        BudgetManager(),
        store,
        CheckpointService(store, id_factory=lambda: "chk-1"),
        ObjectiveEvaluator(),
        _Coordinator(),
        synthesis,
    )


class _Coordinator(ToolExecutionCoordinator):
    def __init__(self) -> None:
        pass

    def execute(self, request: ToolExecutionRequest) -> ToolExecutionResult:
        return ToolExecutionResult(request.request_id, request.tool_name, ToolExecutionStatus.SUCCESS, {"entries": ()})
