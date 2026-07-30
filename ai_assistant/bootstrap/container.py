"""Composition root for application dependencies."""

from ai_assistant.application.context import ContextBuilder
from ai_assistant.application.runtime import AgentRuntime
from ai_assistant.application.tool_calls import ToolCallDetector
from ai_assistant.bootstrap.config import AppConfig, load_app_config
from ai_assistant.bootstrap.logging import configure_logging
from ai_assistant.infrastructure.models.adapter import ModelAdapter, ModelAdapterConfig
from ai_assistant.infrastructure.storage.sqlite_memory import SQLiteConversationStore
from ai_assistant.interfaces.cli.app import CliApplication


def create_application(config: AppConfig | None = None) -> CliApplication:
    app_config = config or load_app_config()
    configure_logging(app_config.log_level)
    runtime = AgentRuntime(
        context_builder=ContextBuilder(
            system_prompt=app_config.system_prompt,
            context_limit=app_config.context_limit,
        ),
        memory=SQLiteConversationStore(app_config.database),
        model=ModelAdapter.from_config(_model_config(app_config)),
        tool_detector=ToolCallDetector(),
        session_id=app_config.session,
    )
    return CliApplication(runtime)


def _model_config(config: AppConfig) -> ModelAdapterConfig:
    return ModelAdapterConfig(
        provider=config.provider,
        model=config.model,
        base_url=config.base_url,
        api_key=config.api_key,
        timeout_seconds=config.request_timeout,
    )
