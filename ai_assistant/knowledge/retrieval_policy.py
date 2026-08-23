"""Deterministic conversation retrieval policy."""

_ACKNOWLEDGEMENTS = {"ok", "okay", "thanks", "thank you", "yes", "no", "hello", "hi"}
_PROJECT_TERMS = {
    "architecture",
    "code",
    "class",
    "function",
    "module",
    "project",
    "readme",
    "adr",
    "document",
    "docs",
    "test",
    "executionengine",
}
_LIVE_STATE_TERMS = ("current", "currently", "now", "latest", "today")
_LIVE_STATE_TARGETS = ("git", "status", "diff", "test", "tests", "build", "changed", "changes")
_LIVE_STATE_PHRASES = (
    "git status",
    "git diff",
    "test result",
    "tests passing",
    "build result",
    "show build",
)


class ConversationRetrievalPolicy:
    def allow(self, text: str, *, context_enabled: bool) -> bool:
        if not context_enabled:
            return False
        normalized = " ".join(text.casefold().strip().split())
        if not normalized or normalized in _ACKNOWLEDGEMENTS or len(normalized.split()) <= 2:
            return False
        if any(term in normalized for term in _LIVE_STATE_TERMS) and any(
            target in normalized for target in _LIVE_STATE_TARGETS
        ):
            return False
        if any(phrase in normalized for phrase in _LIVE_STATE_PHRASES):
            return False
        return any(term in normalized for term in _PROJECT_TERMS)
