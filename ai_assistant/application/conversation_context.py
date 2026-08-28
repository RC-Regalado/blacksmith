"""Conversation context assembly."""

from ai_assistant.application.context import ContextBuilder
from ai_assistant.application.conversation_budget import ConversationContextBudget, estimate_tokens
from ai_assistant.domain.errors import InvalidKnowledgeError
from ai_assistant.domain.message import Message
from ai_assistant.knowledge import CompiledContext, ContextPurpose
from ai_assistant.knowledge.metrics import ContextMetrics


class ConversationContextService:
    def __init__(
        self,
        context_builder: ContextBuilder,
        budget: ConversationContextBudget = ConversationContextBudget(),
        context_provider=None,
        retrieval_policy=None,
    ) -> None:
        self.budget = budget
        self._context_builder = context_builder
        self._context_provider = context_provider
        self._retrieval_policy = retrieval_policy
        self.last_diagnostic: str | None = None
        self.last_metrics: ContextMetrics | None = None

    def build(
        self,
        history: list[Message],
        user_input: str,
        compiled_context: CompiledContext | None = None,
        *,
        include_knowledge: bool = False,
    ) -> list[Message]:
        messages = self._context_builder.build(history, user_input)
        if not include_knowledge or compiled_context is None or not compiled_context.evidence:
            return messages
        if compiled_context.purpose != ContextPurpose.CONVERSATION:
            raise InvalidKnowledgeError("conversation context requires conversation-purpose knowledge.")
        knowledge = _knowledge_message(compiled_context)
        if _token_count(messages) + compiled_context.token_count > self.budget.max_input_tokens:
            return messages
        return [messages[0], knowledge, *messages[1:]]

    def build_with_retrieval(
        self,
        history: list[Message],
        user_input: str,
        *,
        include_knowledge: bool = False,
    ) -> list[Message]:
        if not include_knowledge:
            self.last_diagnostic = None
            self.last_metrics = None
            return self.build(history, user_input)
        if self._retrieval_policy is not None and not self._retrieval_policy.allow(
            user_input,
            context_enabled=True,
        ):
            self.last_diagnostic = None
            self.last_metrics = None
            return self.build(history, user_input)
        compiled_context = self._retrieve(user_input)
        if compiled_context is None:
            self.last_diagnostic = None
            self.last_metrics = None
            return self.build(history, user_input)
        if not compiled_context.evidence:
            self.last_diagnostic = (
                "Knowledge context requested, but no fresh indexed knowledge matched. "
                "No rebuild was run."
            )
            return _with_diagnostic(
                self.build(history, user_input),
                self.last_diagnostic,
            )
        self.last_diagnostic = None
        return self.build(history, user_input, compiled_context, include_knowledge=True)

    def _retrieve(self, user_input: str) -> CompiledContext | None:
        if self._context_provider is None:
            return None
        context = self._context_provider.build(user_input)
        metrics = getattr(self._context_provider, "last_metrics", None)
        self.last_metrics = metrics if isinstance(metrics, ContextMetrics) else None
        return context


def _knowledge_message(context: CompiledContext) -> Message:
    lines = [
        "Relevant derived knowledge:",
        *(
            f"- [{item.candidate.source_uri}#{item.candidate.chunk_id}] {item.text}"
            for item in context.evidence
        ),
    ]
    return Message(role="system", content="\n".join(lines))


def _token_count(messages: list[Message]) -> int:
    return sum(estimate_tokens(message.content) for message in messages)


def _with_diagnostic(messages: list[Message], diagnostic: str) -> list[Message]:
    return [messages[0], Message(role="system", content=diagnostic), *messages[1:]]
