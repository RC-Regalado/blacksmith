"""Composition root for application dependencies."""

from pathlib import Path

from ai_assistant.application.context import ContextBuilder
from ai_assistant.application.confirmation import ConfirmationService
from ai_assistant.application.ports.tools import ToolExecutor
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
from ai_assistant.infrastructure.storage.sqlite_execution import SQLiteExecutionStore
from ai_assistant.infrastructure.storage.sqlite_memory import SQLiteConversationStore
from ai_assistant.infrastructure.tools import (
    LocalReadOnlyToolExecutor,
    UnixSocketToolExecutor,
)
from ai_assistant.interfaces.cli.app import CliApplication, CliConfirmationPrompter
from ai_assistant.platform.application import (
    BudgetManager,
    CheckpointService,
    ExecutionEngine,
    ModelBackedPlanner,
    ObjectiveEvaluator,
    PlanValidator,
    StaticCapabilityRegistry,
    TaskScheduler,
)


def create_application(config: AppConfig | None = None) -> CliApplication:
    app_config = config or load_app_config()
    configure_logging(app_config.log_level)
    catalog = _tool_catalog(app_config) if app_config.tool_execution else None
    coordinator = _tool_coordinator(app_config, catalog)
    runtime = AgentRuntime(
        context_builder=ContextBuilder(
            system_prompt=_system_prompt(app_config),
            context_limit=app_config.context_limit,
        ),
        memory=SQLiteConversationStore(app_config.database),
        model=ModelAdapter.from_config(_model_config(app_config)),
        tool_detector=ToolCallDetector(),
        tool_catalog=catalog,
        tool_coordinator=coordinator,
        tool_timeout_seconds=app_config.tool_timeout,
        session_id=app_config.session,
    )
    return CliApplication(
        runtime,
        _execution_engine(app_config, catalog, coordinator),
        app_config.session,
    )


def _system_prompt(config: AppConfig) -> str:
    if not config.tool_execution or not config.workspace:
        return config.system_prompt
    return (
        f"{config.system_prompt}\n"
        "When the user asks to use a local tool, reply only with JSON.\n"
        'For listing files: {"tool_call":{"name":"list_directory","arguments":{"path":"."}}}\n'
        'For reading a file: {"tool_call":{"name":"read_file","arguments":{"path":"README.md","max_bytes":2048}}}\n'
        'For searching text: {"tool_call":{"name":"search_text","arguments":{"path":".","query":"needle"}}}\n'
        'For Git status: {"tool_call":{"name":"git_status","arguments":{"path":"."}}}\n'
        'For Git diff: {"tool_call":{"name":"git_diff","arguments":{"path":".","scope":"worktree"}}}\n'
        'For tests: {"tool_call":{"name":"run_tests","arguments":{"path":".","profile_id":"core-tests"}}}\n'
        'For builds: {"tool_call":{"name":"build_project","arguments":{"path":".","profile_id":"python-compile"}}}\n'
        'For writing: {"tool_call":{"name":"write","arguments":{"path":"notes.txt","mode":"create","content":"text"}}}\n'
        "After a tool result, answer normally."
    )


def _model_config(config: AppConfig) -> ModelAdapterConfig:
    return ModelAdapterConfig(
        provider=config.provider,
        model=config.model,
        base_url=config.base_url,
        api_key=config.api_key,
        timeout_seconds=config.request_timeout,
    )


def _tool_catalog(config: AppConfig) -> StaticToolCatalog:
    return StaticToolCatalog(
        tool_timeout=config.tool_timeout,
        max_read_bytes=config.max_read_bytes,
        max_directory_entries=config.max_directory_entries,
        max_directory_depth=config.max_directory_depth,
    )


def _tool_coordinator(
    config: AppConfig,
    catalog: StaticToolCatalog | None,
) -> ToolExecutionCoordinator | None:
    if not config.tool_execution or not config.workspace or catalog is None:
        return None
    audit = SQLiteAuditRecorder(config.audit_database)
    return ToolExecutionCoordinator(
        catalog=catalog,
        policy=DenyByDefaultToolPolicy(enabled=True),
        path_policy=WorkspacePathPolicy(config.workspace),
        audit=audit,
        executor=_tool_executor(config),
        confirmation=ConfirmationService(CliConfirmationPrompter(), audit),
    )


def _tool_executor(config: AppConfig) -> ToolExecutor:
    if config.tool_executor == "local":
        return LocalReadOnlyToolExecutor()
    return UnixSocketToolExecutor(Path(config.tool_socket))


def _execution_engine(
    config: AppConfig,
    catalog: StaticToolCatalog | None,
    coordinator: ToolExecutionCoordinator | None,
) -> ExecutionEngine | None:
    if catalog is None or coordinator is None:
        return None
    registry = StaticCapabilityRegistry(catalog)
    store = SQLiteExecutionStore(config.execution_database)
    return ExecutionEngine(
        planner=ModelBackedPlanner(ModelAdapter.from_config(_model_config(config)), registry),
        validator=PlanValidator(registry),
        registry=registry,
        scheduler=TaskScheduler(store),
        budget_manager=BudgetManager(),
        store=store,
        checkpoints=CheckpointService(store),
        evaluator=ObjectiveEvaluator(),
        tools=coordinator,
    )
