"""Tests for deterministic conversation retrieval policy."""

from ai_assistant.knowledge import ConversationRetrievalPolicy


def test_retrieval_policy_respects_context_enabled() -> None:
    policy = ConversationRetrievalPolicy()

    assert policy.allow("Explain project architecture", context_enabled=False) is False


def test_retrieval_policy_bypasses_short_acknowledgements() -> None:
    policy = ConversationRetrievalPolicy()

    assert policy.allow("ok", context_enabled=True) is False
    assert policy.allow("thank you", context_enabled=True) is False


def test_retrieval_policy_allows_project_code_document_questions() -> None:
    policy = ConversationRetrievalPolicy()

    assert policy.allow("Explain the ExecutionEngine architecture", context_enabled=True) is True
    assert policy.allow("Where are the README docs indexed?", context_enabled=True) is True


def test_retrieval_policy_bypasses_volatile_live_state_questions() -> None:
    policy = ConversationRetrievalPolicy()

    assert policy.allow("What is the current git status?", context_enabled=True) is False
    assert policy.allow("What is the current test result?", context_enabled=True) is False
    assert policy.allow("Show the latest build result", context_enabled=True) is False
    assert policy.allow("git status", context_enabled=True) is False
    assert policy.allow("are tests passing?", context_enabled=True) is False
    assert policy.allow("show build result", context_enabled=True) is False
