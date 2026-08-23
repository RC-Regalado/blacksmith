"""Conversation knowledge context provider."""

from ai_assistant.knowledge.compiler import ContextCompiler
from ai_assistant.knowledge.domain import CompiledContext, ContextBudget, ContextPurpose, KnowledgeQuery
from ai_assistant.knowledge.metrics import ContextMetrics, context_metrics
from ai_assistant.knowledge.ranking import KnowledgeRanker
from ai_assistant.knowledge.retrieval import HybridRetriever


class ConversationKnowledgeContextProvider:
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

    def build(self, text: str) -> CompiledContext:
        query = KnowledgeQuery(text, limit=self._budget.max_chunks)
        candidates = self._retriever.retrieve(query)
        ranked = self._ranker.rank(candidates, self._budget.max_chunks)
        context = self._compiler.compile_conversation_context(ranked, self._budget)
        self.last_metrics = context_metrics(ContextPurpose.CONVERSATION, candidates, ranked, context)
        return context
