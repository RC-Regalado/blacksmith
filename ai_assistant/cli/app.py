"""Minimal command line interface."""

import logging
import sys

from ai_assistant.application.errors import AssistantError
from ai_assistant.agent.runtime import AgentRuntime


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
                logger.error(
                    "expected assistant error type=%s",
                    type(error).__name__,
                )
                print(f"Error: {error}", file=sys.stderr)


def run_cli() -> None:
    from ai_assistant.bootstrap.container import create_application

    create_application().run()
