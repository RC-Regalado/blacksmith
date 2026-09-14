"""Tool execution application ports."""

from abc import ABC, abstractmethod

from ai_assistant.domain.tools import (
    InteractionLogEvent,
    ToolAuditEvent,
    ToolCallLogEvent,
    ToolDefinition,
    ToolExecutionContext,
    ToolExecutionRequest,
    ToolExecutionResult,
    ToolProfileId,
    ToolPolicyDecision,
)


class ToolCatalog(ABC):
    @abstractmethod
    def definition_for(self, tool_name: str) -> ToolDefinition:
        raise NotImplementedError


class ToolPolicy(ABC):
    @abstractmethod
    def decide(
        self, request: ToolExecutionRequest, definition: ToolDefinition
    ) -> ToolPolicyDecision:
        raise NotImplementedError


class PathPolicy(ABC):
    @abstractmethod
    def validate(
        self, request: ToolExecutionRequest, definition: ToolDefinition
    ) -> ToolExecutionContext:
        raise NotImplementedError


class ToolExecutor(ABC):
    @abstractmethod
    def execute(self, context: ToolExecutionContext) -> ToolExecutionResult:
        raise NotImplementedError


class AuditRecorder(ABC):
    @abstractmethod
    def record(self, event: ToolAuditEvent) -> None:
        raise NotImplementedError


class ToolDiagnosticLogger(ABC):
    @abstractmethod
    def record(self, event: ToolCallLogEvent) -> None:
        raise NotImplementedError


class InteractionDiagnosticLogger(ABC):
    @abstractmethod
    def record(self, event: InteractionLogEvent) -> None:
        raise NotImplementedError


class ConfirmationPrompter(ABC):
    @abstractmethod
    def confirm(
        self,
        session_id: str,
        workspace_id: str,
        permission: str,
    ) -> bool:
        raise NotImplementedError


class ToolProfileRegistry(ABC):
    @abstractmethod
    def definition_for(self, profile_id: ToolProfileId) -> object:
        raise NotImplementedError
