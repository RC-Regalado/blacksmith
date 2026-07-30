"""Minimal command line interface."""

import os

from ai_assistant.application.ports.memory import DEFAULT_SESSION_ID
from ai_assistant.agent.context import ContextBuilder
from ai_assistant.agent.models.adapter import ModelAdapter
from ai_assistant.agent.planner import ToolCallDetector
from ai_assistant.agent.runtime import AgentRuntime
from ai_assistant.storage.sqlite_memory import SQLiteConversationStore


def build_runtime() -> AgentRuntime:
    return AgentRuntime(
        context_builder=ContextBuilder(system_prompt="You are a local AI assistant."),
        memory=SQLiteConversationStore("assistant.sqlite3"),
        model=ModelAdapter.from_env(),
        tool_detector=ToolCallDetector(),
        session_id=os.getenv("AI_ASSISTANT_SESSION", DEFAULT_SESSION_ID),
    )


def run_cli() -> None:
    runtime = build_runtime()
    while True:
        try:
            user_input = input("> ").strip()
        except EOFError:
            break

        if user_input in {"exit", "quit"}:
            break
        if not user_input:
            continue

        response = runtime.respond(user_input)
        print(response.content)
