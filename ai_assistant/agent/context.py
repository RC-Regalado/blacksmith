"""Context construction for model calls."""

from dataclasses import dataclass

from ai_assistant.agent.message import Message


@dataclass(frozen=True, slots=True)
class ContextBuilder:
    system_prompt: str

    def build(self, history: list[Message], user_input: str) -> list[Message]:
        if not user_input.strip():
            raise ValueError("User input cannot be empty.")

        return [
            Message(role="system", content=self.system_prompt),
            *history,
            Message(role="user", content=user_input),
        ]

