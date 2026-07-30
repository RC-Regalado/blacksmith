"""Minimal command line interface."""

import logging
import sys

from ai_assistant.application.runtime import AgentRuntime
from ai_assistant.domain.errors import AssistantError


logger = logging.getLogger(__name__)


class CliApplication:
    def __init__(self, runtime: AgentRuntime) -> None:
        self._runtime = runtime

    def run(self) -> None:
        while True:
            try:
                user_input = input("> ").strip()
            except EOFError:
                break

            if user_input in {"exit", "quit"}:
                break
            if not user_input:
                continue

            try:
                response = self._runtime.respond(user_input)
                print(response.content)
            except AssistantError as error:
                logger.error("expected assistant error type=%s", type(error).__name__)
                print(f"Error: {error}", file=sys.stderr)
