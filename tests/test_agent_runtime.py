"""Tests for the Phase 1 agent runtime."""

import pytest

from ai_assistant.agent.context import ContextBuilder
from ai_assistant.application.conversation_context import ConversationContextService
from ai_assistant.application.ports.memory import (
    ConversationMemory,
    SessionId,
)
from ai_assistant.application.ports.models import ModelProvider
from ai_assistant.agent.message import Message
from ai_assistant.agent.planner import ToolCallDetector
from ai_assistant.agent.runtime import AgentRuntime
from ai_assistant.application.tool_catalog import StaticToolCatalog
from ai_assistant.domain.tools import (
    ToolExecutionRequest,
    ToolExecutionResult,
    ToolExecutionStatus,
    ToolPermission,
)
from ai_assistant.knowledge import CompiledContext, ContextBudget, ContextPurpose
from ai_assistant.knowledge import ConversationRetrievalPolicy


pytestmark = pytest.mark.unit


def test_runtime_persists_user_and_assistant_turn() -> None:
    memory = FakeConversationStore()
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="System prompt"),
        memory=memory,
        model=FakeModel("Echo: Hello"),
        tool_detector=ToolCallDetector(),
        session_id="alpha",
    )

    response = runtime.respond("Hello")

    assert response == Message(role="assistant", content="Echo: Hello")
    assert memory.history("alpha") == [
        Message(role="user", content="Hello", session_id="alpha"),
        Message(role="assistant", content="Echo: Hello", session_id="alpha"),
    ]
    assert memory.history("beta") == []


def test_runtime_persists_complete_turn_atomically() -> None:
    memory = FailingTurnStore()
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="System prompt"),
        memory=memory,
        model=FakeModel("Echo: Hello"),
        tool_detector=ToolCallDetector(),
        session_id="alpha",
    )

    with pytest.raises(RuntimeError, match="store failed"):
        runtime.respond("Hello")

    assert memory.history("alpha") == []


def test_context_builder_merges_system_history_and_user_input() -> None:
    builder = ContextBuilder(system_prompt="System prompt")
    history = [Message(role="assistant", content="Prior response")]

    context = builder.build(history=history, user_input="Next")

    assert context == [
        Message(role="system", content="System prompt"),
        Message(role="assistant", content="Prior response"),
        Message(role="user", content="Next"),
    ]


def test_context_builder_prefers_recent_history_within_budget() -> None:
    builder = ContextBuilder(system_prompt="S", context_limit=9)
    history = [
        Message(role="user", content="old"),
        Message(role="assistant", content="mid"),
        Message(role="assistant", content="new"),
    ]

    context = builder.build(history=history, user_input="U")

    assert context == [
        Message(role="system", content="S"),
        Message(role="assistant", content="mid"),
        Message(role="assistant", content="new"),
        Message(role="user", content="U"),
    ]


def test_context_builder_preserves_system_and_current_input_when_over_budget() -> None:
    builder = ContextBuilder(system_prompt="system", context_limit=1)

    context = builder.build(
        history=[Message(role="assistant", content="history")],
        user_input="current",
    )

    assert context == [
        Message(role="system", content="system"),
        Message(role="user", content="current"),
    ]


def test_runtime_stores_tool_call_plan_without_execution() -> None:
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="System prompt"),
        memory=FakeConversationStore(),
        model=FakeModel('{"tool_call":{"name":"search","arguments":{"q":"x"}}}'),
        tool_detector=ToolCallDetector(),
        session_id="alpha",
    )

    runtime.respond("Hello")

    assert runtime.last_tool_plan.has_tool_call is True
    assert runtime.last_tool_plan.tool_name == "search"


def test_runtime_uses_tool_result_for_final_answer() -> None:
    memory = FakeConversationStore()
    model = SequenceModel(
        [
            '{"tool_call":{"id":"call-1","name":"read_file","arguments":{"path":"notes.txt"}}}',
            "Final answer from tool result",
        ]
    )
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="System prompt"),
        memory=memory,
        model=model,
        tool_detector=ToolCallDetector(),
        tool_coordinator=FakeToolCoordinator(
            ToolExecutionResult(
                request_id="call-1",
                tool_name="read_file",
                status=ToolExecutionStatus.SUCCESS,
                content={"content": "notes"},
            )
        ),
        session_id="alpha",
    )

    response = runtime.respond("Read notes")

    assert response == Message(role="assistant", content="Final answer from tool result")
    assert model.calls[1][-1].role == "tool"
    assert runtime.tool_coordinator.requests[0].timeout_seconds == 5.0
    assert memory.history("alpha") == [
        Message(role="user", content="Read notes", session_id="alpha"),
        Message(
            role="assistant",
            content='{"tool_call":{"id":"call-1","name":"read_file","arguments":{"path":"notes.txt"}}}',
            session_id="alpha",
        ),
        Message(
            role="tool",
            content='{"content": {"content": "notes"}, "status": "success", "truncated": false}',
            session_id="alpha",
            tool_name="read_file",
            tool_call_id="call-1",
        ),
        Message(
            role="assistant",
            content="Final answer from tool result",
            session_id="alpha",
        ),
    ]


def test_runtime_executes_operator_tool_json_without_model_call() -> None:
    model = SequenceModel(["should not be used"])
    coordinator = FakeToolCoordinator(
        ToolExecutionResult(
            request_id="alpha:list_directory",
            tool_name="list_directory",
            status=ToolExecutionStatus.SUCCESS,
            content={"entries": []},
        )
    )
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="System prompt"),
        memory=FakeConversationStore(),
        model=model,
        tool_detector=ToolCallDetector(),
        tool_coordinator=coordinator,
        session_id="alpha",
    )

    response = runtime.respond(
        '{"tool_call":{"name":"list_directory","arguments":{"path":"."}}}'
    )

    assert model.calls == []
    assert coordinator.requests[0].tool_name == "list_directory"
    assert response.content == (
        '{"content": {"entries": []}, "status": "success", "truncated": false}'
    )


def test_runtime_uses_configured_tool_timeout() -> None:
    coordinator = FakeToolCoordinator(
        ToolExecutionResult(
            request_id="alpha:read_file",
            tool_name="read_file",
            status=ToolExecutionStatus.SUCCESS,
            content={"content": "notes"},
        )
    )
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="System prompt"),
        memory=FakeConversationStore(),
        model=SequenceModel(
            [
                '{"tool_call":{"name":"read_file","arguments":{"path":"notes.txt"}}}',
                "Final answer",
            ]
        ),
        tool_detector=ToolCallDetector(),
        tool_coordinator=coordinator,
        tool_timeout_seconds=7.5,
        session_id="alpha",
    )

    runtime.respond("Read notes")

    assert coordinator.requests[0].timeout_seconds == 7.5


def test_runtime_derives_tool_permission_from_catalog() -> None:
    coordinator = FakeToolCoordinator(
        ToolExecutionResult(
            request_id="alpha:run_tests",
            tool_name="run_tests",
            status=ToolExecutionStatus.SUCCESS,
            content={"exit_code": 0},
        )
    )
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="System prompt"),
        memory=FakeConversationStore(),
        model=SequenceModel(
            [
                '{"tool_call":{"name":"run_tests","arguments":{"path":".","profile_id":"core-tests"}}}',
                "Final answer",
            ]
        ),
        tool_detector=ToolCallDetector(),
        tool_catalog=StaticToolCatalog(),
        tool_coordinator=coordinator,
        session_id="alpha",
    )

    runtime.respond("Run tests")

    assert coordinator.requests[0].permission == ToolPermission.EXECUTE_PROJECT


def test_runtime_context_enabled_preserves_tool_round() -> None:
    provider = EmptyContextProvider()
    coordinator = FakeToolCoordinator(
        ToolExecutionResult(
            request_id="alpha:git_status",
            tool_name="git_status",
            status=ToolExecutionStatus.SUCCESS,
            content={"entries": []},
        )
    )
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="System prompt"),
        conversation_context=ConversationContextService(
            ContextBuilder(system_prompt="System prompt"),
            context_provider=provider,
            retrieval_policy=AllowPolicy(),
        ),
        memory=FakeConversationStore(),
        model=SequenceModel(
            [
                '{"tool_call":{"name":"git_status","arguments":{"path":"."}}}',
                "Final answer",
            ]
        ),
        tool_detector=ToolCallDetector(),
        tool_catalog=StaticToolCatalog(),
        tool_coordinator=coordinator,
        include_knowledge_context=True,
        session_id="alpha",
    )

    response = runtime.respond("Explain project architecture")

    assert response.content == "Final answer"
    assert provider.calls == 1
    assert coordinator.requests[0].tool_name == "git_status"
    assert len(coordinator.requests) == 1


def test_runtime_context_enabled_live_state_bypasses_retrieval_before_tool_call() -> None:
    provider = EmptyContextProvider()
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="System prompt"),
        conversation_context=ConversationContextService(
            ContextBuilder(system_prompt="System prompt"),
            context_provider=provider,
            retrieval_policy=ConversationRetrievalPolicy(),
        ),
        memory=FakeConversationStore(),
        model=SequenceModel(
            [
                '{"tool_call":{"name":"git_status","arguments":{"path":"."}}}',
                "Final answer",
            ]
        ),
        tool_detector=ToolCallDetector(),
        tool_catalog=StaticToolCatalog(),
        tool_coordinator=FakeToolCoordinator(
            ToolExecutionResult(
                request_id="alpha:git_status",
                tool_name="git_status",
                status=ToolExecutionStatus.SUCCESS,
                content={"entries": []},
            )
        ),
        include_knowledge_context=True,
        session_id="alpha",
    )

    runtime.respond("What is the current git status?")

    assert provider.calls == 0


def test_runtime_stops_after_second_tool_request() -> None:
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="System prompt"),
        memory=FakeConversationStore(),
        model=SequenceModel(
            [
                '{"tool_call":{"name":"read_file","arguments":{"path":"notes.txt"}}}',
                '{"tool_call":{"name":"read_file","arguments":{"path":"again.txt"}}}',
            ]
        ),
        tool_detector=ToolCallDetector(),
        tool_coordinator=FakeToolCoordinator(
            ToolExecutionResult(
                request_id="alpha:read_file",
                tool_name="read_file",
                status=ToolExecutionStatus.SUCCESS,
                content={"content": "notes"},
            )
        ),
        session_id="alpha",
    )

    response = runtime.respond("Read notes")

    assert response == Message(
        role="assistant",
        content="Tool round limit reached; no additional tool was executed.",
    )


def test_runtime_persists_tool_round_atomically() -> None:
    runtime = AgentRuntime(
        context_builder=ContextBuilder(system_prompt="System prompt"),
        memory=FailingTurnStore(),
        model=SequenceModel(
            [
                '{"tool_call":{"name":"read_file","arguments":{"path":"notes.txt"}}}',
                "Final answer",
            ]
        ),
        tool_detector=ToolCallDetector(),
        tool_coordinator=FakeToolCoordinator(
            ToolExecutionResult(
                request_id="alpha:read_file",
                tool_name="read_file",
                status=ToolExecutionStatus.SUCCESS,
                content={"content": "notes"},
            )
        ),
        session_id="alpha",
    )

    with pytest.raises(RuntimeError, match="store failed"):
        runtime.respond("Read notes")


class FailingTurnStore(ConversationMemory):
    def __init__(self) -> None:
        self._messages: list[Message] = []

    def append(self, session_id: SessionId, message: Message) -> None:
        self.append_many(session_id, [message])

    def append_many(self, session_id: SessionId, messages: list[Message]) -> None:
        raise RuntimeError("store failed")

    def history(self, session_id: SessionId) -> list[Message]:
        return list(self._messages)


class FakeConversationStore(ConversationMemory):
    def __init__(self) -> None:
        self._messages: list[Message] = []

    def append(self, session_id: SessionId, message: Message) -> None:
        self.append_many(session_id, [message])

    def append_many(self, session_id: SessionId, messages: list[Message]) -> None:
        self._messages.extend(
            Message(
                role=message.role,
                content=message.content,
                session_id=session_id,
                tool_name=message.tool_name,
                tool_call_id=message.tool_call_id,
            )
            for message in messages
        )

    def history(self, session_id: SessionId) -> list[Message]:
        return [
            message for message in self._messages if message.session_id == session_id
        ]


class FakeModel(ModelProvider):
    def __init__(self, response: str) -> None:
        self._response = response

    def chat(self, messages: list[Message]) -> Message:
        return Message(role="assistant", content=self._response)


class SequenceModel(ModelProvider):
    def __init__(self, responses: list[str]) -> None:
        self._responses = responses
        self.calls: list[list[Message]] = []

    def chat(self, messages: list[Message]) -> Message:
        self.calls.append(messages)
        return Message(role="assistant", content=self._responses.pop(0))


class FakeToolCoordinator:
    def __init__(self, result: ToolExecutionResult) -> None:
        self.result = result
        self.requests: list[ToolExecutionRequest] = []

    def execute(self, request: ToolExecutionRequest) -> ToolExecutionResult:
        self.requests.append(request)
        return self.result


class EmptyContextProvider:
    def __init__(self) -> None:
        self.calls = 0

    def build(self, _text: str) -> CompiledContext:
        self.calls += 1
        return CompiledContext(ContextPurpose.CONVERSATION, (), ContextBudget())


class AllowPolicy:
    def allow(self, _text: str, *, context_enabled: bool) -> bool:
        return context_enabled
