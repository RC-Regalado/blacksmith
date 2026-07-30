"""Context construction for model calls."""

from dataclasses import dataclass

from ai_assistant.agent.message import Message


@dataclass(frozen=True, slots=True)
class ContextBuilder:
    system_prompt: str
    context_limit: int = 4096

    def build(self, history: list[Message], user_input: str) -> list[Message]:
        if not user_input.strip():
            raise ValueError("User input cannot be empty.")

        selected_history = self._select_history(history, user_input)
        return [
            Message(role="system", content=self.system_prompt),
            *selected_history,
            Message(role="user", content=user_input),
        ]

    def _select_history(self, history: list[Message], user_input: str) -> list[Message]:
        remaining = self.context_limit - len(self.system_prompt) - len(user_input)
        if remaining <= 0:
            return []

        selected: list[Message] = []
        for message in reversed(history):
            cost = len(message.content)
            if cost > remaining:
                break
            selected.append(message)
            remaining -= cost
        return list(reversed(selected))
