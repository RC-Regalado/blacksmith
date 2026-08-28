"""Per-turn interaction metrics (ADR-070/ADR-071 observability surface).

Aggregates what one `AgentRuntime.respond()` call actually did — model calls,
token/termination metadata from the last `ModelResponse`, tool-loop budget
spend and knowledge retrieval — into one snapshot exposed as
`AgentRuntime.last_interaction_metrics`. Purely observational: nothing here
feeds back into a policy or budget decision.
"""

from dataclasses import dataclass

from ai_assistant.domain.model_response import FinishReason


@dataclass(frozen=True, slots=True)
class InteractionMetrics:
    interaction_id: str
    outcome: str
    model_calls: int
    prompt_tokens: int | None
    output_tokens: int | None
    finish_reason: FinishReason | None
    truncated: bool
    tool_rounds: int
    tool_requests: int
    executor_operations: int
    recovery_operations: int
    retrieval_attempted: bool
    knowledge_chunks_selected: int

    def __post_init__(self) -> None:
        for field_name in (
            "model_calls",
            "tool_rounds",
            "tool_requests",
            "executor_operations",
            "recovery_operations",
            "knowledge_chunks_selected",
        ):
            if getattr(self, field_name) < 0:
                raise ValueError(f"{field_name} cannot be negative.")
