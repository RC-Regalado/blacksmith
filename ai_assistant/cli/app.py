"""Minimal command line interface."""

from ai_assistant.agent.runtime import AgentRuntime


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

            response = self._runtime.respond(user_input)
            print(response.content)


def run_cli() -> None:
    from ai_assistant.bootstrap.container import create_application

    create_application().run()
