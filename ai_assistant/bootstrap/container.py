"""Composition root for application dependencies."""

import os

from ai_assistant.agent.context import ContextBuilder
from ai_assistant.agent.models.adapter import ModelAdapter
from ai_assistant.agent.planner import ToolCallDetector
from ai_assistant.agent.runtime import AgentRuntime
from ai_assistant.application.ports.memory import DEFAULT_SESSION_ID
from ai_assistant.cli.app import CliApplication
from ai_assistant.storage.sqlite_memory import SQLiteConversationStore


def create_application() -> CliApplication:
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="You are a local AI assistant."),
        memory=SQLiteConversationStore("assistant.sqlite3"),
        model=ModelAdapter.from_env(),
        tool_detector=ToolCallDetector(),
        session_id=os.getenv("AI_ASSISTANT_SESSION", DEFAULT_SESSION_ID),
    )
    return CliApplication(runtime)
