"""Deterministic conversation context/generation budget (ADR-071).

A single local approximation (`estimate_tokens`) is the one shared unit used
to enforce the conversational input budget, replacing the previous mix of raw
character length (`ContextBuilder`) and word count
(`ConversationContextService`) as separate, inconsistent enforcement units
for what is conceptually the same overall prompt-size decision. It is not a
real tokenizer; it is a deterministic, local, provider-agnostic estimate.
"""

from dataclasses import dataclass

from ai_assistant.application.errors import ConfigurationError


def estimate_tokens(text: str) -> int:
    return max(len(text.split()), (len(text) + 3) // 4)


@dataclass(frozen=True, slots=True)
class ConversationContextBudget:
    provider_context_window: int = 8192
    reserved_output_tokens: int = 2048
    safety_margin_tokens: int = 0

    def __post_init__(self) -> None:
        if self.provider_context_window <= 0:
            raise ConfigurationError("provider_context_window must be positive.")
        if self.reserved_output_tokens < 0:
            raise ConfigurationError("reserved_output_tokens cannot be negative.")
        if self.safety_margin_tokens < 0:
            raise ConfigurationError("safety_margin_tokens cannot be negative.")
        if self.reserved_output_tokens + self.safety_margin_tokens >= self.provider_context_window:
            raise ConfigurationError(
                "reserved_output_tokens plus safety_margin_tokens must be less than provider_context_window."
            )

    @property
    def max_input_tokens(self) -> int:
        return self.provider_context_window - self.reserved_output_tokens - self.safety_margin_tokens
