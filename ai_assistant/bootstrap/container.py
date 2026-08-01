"""Composition root for application dependencies."""

from ai_assistant.application.context import ContextBuilder
from ai_assistant.application.path_policy import WorkspacePathPolicy
from ai_assistant.application.runtime import AgentRuntime
from ai_assistant.application.tool_catalog import StaticToolCatalog
from ai_assistant.application.tool_calls import ToolCallDetector
from ai_assistant.application.tool_coordinator import ToolExecutionCoordinator
from ai_assistant.application.tool_policy import DenyByDefaultToolPolicy
from ai_assistant.bootstrap.config import AppConfig, load_app_config
from ai_assistant.bootstrap.logging import configure_logging
from ai_assistant.infrastructure.models.adapter import ModelAdapter, ModelAdapterConfig
from ai_assistant.infrastructure.storage.sqlite_audit import SQLiteAuditRecorder
from ai_assistant.infrastructure.storage.sqlite_memory import SQLiteConversationStore
from ai_assistant.infrastructure.tools import LocalReadOnlyToolExecutor
from ai_assistant.interfaces.cli.app import CliApplication


def create_application(config: AppConfig | None = None) -> CliApplication:
    app_config = config or load_app_config()
    configure_logging(app_config.log_level)
    runtime = AgentRuntime(
        context_builder=ContextBuilder(
            system_prompt=_system_prompt(app_config),
            context_limit=app_config.context_limit,
        ),
        memory=SQLiteConversationStore(app_config.database),
        model=ModelAdapter.from_config(_model_config(app_config)),
        tool_detector=ToolCallDetector(),
        tool_coordinator=_tool_coordinator(app_config),
        tool_timeout_seconds=app_config.tool_timeout,
        session_id=app_config.session,
    )
    return CliApplication(runtime)


def _system_prompt(config: AppConfig) -> str:
    if not config.tool_execution or not config.workspace:
        return config.system_prompt
    return (
        f"{config.system_prompt}\n"
        "When the user asks to inspect local files, reply only with JSON.\n"
        'For listing files: {"tool_call":{"name":"list_directory","arguments":{"path":"."}}}\n'
        'For reading a file: {"tool_call":{"name":"read_file","arguments":{"path":"README.md","max_bytes":2048}}}\n'
        "Use only list_directory and read_file. After a tool result, answer normally."
    )


def _model_config(config: AppConfig) -> ModelAdapterConfig:
    return ModelAdapterConfig(
        provider=config.provider,
        model=config.model,
        base_url=config.base_url,
        api_key=config.api_key,
        timeout_seconds=config.request_timeout,
    )


def _tool_coordinator(config: AppConfig) -> ToolExecutionCoordinator | None:
    if not config.tool_execution or not config.workspace:
        return None
    catalog = StaticToolCatalog(
        tool_timeout=config.tool_timeout,
        max_read_bytes=config.max_read_bytes,
        max_directory_entries=config.max_directory_entries,
        max_directory_depth=config.max_directory_depth,
    )
    return ToolExecutionCoordinator(
        catalog=catalog,
        policy=DenyByDefaultToolPolicy(enabled=True),
        path_policy=WorkspacePathPolicy(config.workspace),
        audit=SQLiteAuditRecorder(config.audit_database),
        executor=LocalReadOnlyToolExecutor(),
    )
