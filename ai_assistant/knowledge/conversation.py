"""Conversation knowledge context provider."""

import unicodedata

from ai_assistant.knowledge.compiler import ContextCompiler
from ai_assistant.knowledge.domain import CompiledContext, ContextBudget, ContextPurpose, KnowledgeQuery
from ai_assistant.knowledge.metrics import ContextMetrics, context_metrics
from ai_assistant.knowledge.ranking import KnowledgeRanker
from ai_assistant.knowledge.retrieval import HybridRetriever

_PROJECT_SUMMARY_TERMS = "AI Assistant README project proyecto arquitectura contexto Context Knowledge Engine"


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
        query = KnowledgeQuery(_conversation_query(text), limit=self._budget.max_chunks)
        candidates = self._retriever.retrieve(query)
        ranked = self._ranker.rank(candidates, self._budget.max_chunks)
        context = self._compiler.compile_conversation_context(ranked, self._budget)
        self.last_metrics = context_metrics(ContextPurpose.CONVERSATION, candidates, ranked, context)
        return context


def _conversation_query(text: str) -> str:
    normalized = _normalize(text)
    tokens = set(normalized.split())
    if (
        ({"project", "proyecto"} & tokens)
        and ({"what", "que", "hace", "does"} & tokens)
        and not ({"current", "actual", "status", "estado", "git", "tests", "build"} & tokens)
    ):
        return f"{text} {_PROJECT_SUMMARY_TERMS}"
    return text


def _normalize(text: str) -> str:
    ascii_text = (
        unicodedata.normalize("NFKD", text.casefold())
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    return " ".join(
        "".join(char if char.isalnum() else " " for char in ascii_text).split()
    )
