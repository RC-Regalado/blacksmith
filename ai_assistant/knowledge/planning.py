"""Planning context assembly."""

import logging

from ai_assistant.knowledge.compiler import ContextCompiler
from ai_assistant.knowledge.domain import CompiledContext, ContextBudget, ContextPurpose, KnowledgeQuery
from ai_assistant.knowledge.metrics import ContextMetrics, context_metrics
from ai_assistant.knowledge.ranking import KnowledgeRanker
from ai_assistant.knowledge.retrieval import HybridRetriever
from ai_assistant.platform.domain.execution import ExecutionResult
from ai_assistant.platform.domain.objective import Objective

logger = logging.getLogger(__name__)


class PlanningContextProvider:
    def __init__(
        self,
        retriever: HybridRetriever,
        ranker: KnowledgeRanker,
        compiler: ContextCompiler,
        budget: ContextBudget | None = None,
    ) -> None:
        self._retriever = retriever
        self._ranker = ranker
        self._compiler = compiler
        self._budget = budget or ContextBudget()
        self.last_metrics: ContextMetrics | None = None

    def build(self, objective: Objective) -> CompiledContext:
        query = KnowledgeQuery(objective.description, limit=self._budget.max_chunks)
        candidates = self._retriever.retrieve(query)
        ranked = self._ranker.rank(candidates, self._budget.max_chunks)
        context = self._compiler.compile(ContextPurpose.PLANNING, ranked, self._budget)
        self.last_metrics = context_metrics(ContextPurpose.PLANNING, candidates, ranked, context)
        _log_metrics(self.last_metrics)
        return context


class SynthesisContextProvider:
    def __init__(
        self,
        retriever: HybridRetriever,
        ranker: KnowledgeRanker,
        compiler: ContextCompiler,
        budget: ContextBudget | None = None,
    ) -> None:
        self._retriever = retriever
        self._ranker = ranker
        self._compiler = compiler
        self._budget = budget or ContextBudget()
        self.last_metrics: ContextMetrics | None = None

    def observations(self, objective: Objective, result: ExecutionResult) -> tuple[str, ...]:
        context = self._build(objective, result)
        return tuple(
            f"Context {item.candidate.source_uri}: {item.text}"
            for item in context.evidence
        )

    def _build(self, objective: Objective, result: ExecutionResult) -> CompiledContext:
        query = KnowledgeQuery(objective.description, limit=self._budget.max_chunks)
        candidates = self._retriever.retrieve(query)
        ranked = self._ranker.rank(candidates, self._budget.max_chunks)
        context = self._compiler.compile(ContextPurpose.SYNTHESIS, ranked, self._budget)
        self.last_metrics = context_metrics(ContextPurpose.SYNTHESIS, candidates, ranked, context)
        _log_metrics(self.last_metrics)
        return context


def _log_metrics(metrics: ContextMetrics) -> None:
    logger.info(
        "context metrics purpose=%s candidates=%s ranked=%s selected=%s raw_tokens=%s "
        "compiled_tokens=%s reduction_ratio=%.4f",
        metrics.purpose,
        metrics.knowledge_candidates,
        metrics.ranked_candidates,
        metrics.knowledge_chunks_selected,
        metrics.raw_context_estimated_tokens,
        metrics.compiled_context_estimated_tokens,
        metrics.context_reduction_ratio,
    )
