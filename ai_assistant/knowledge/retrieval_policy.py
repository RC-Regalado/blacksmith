"""Deterministic conversation retrieval policy."""

import unicodedata

_ACKNOWLEDGEMENTS = {"ok", "okay", "thanks", "thank you", "yes", "no", "hello", "hi"}
_LIVE_TARGET_WORDS = {"build", "diff", "git", "status", "test", "tests"}
_LIVE_STATE_WORDS = {
    "actual",
    "actualmente",
    "ahora",
    "cambio",
    "cambios",
    "changed",
    "changes",
    "current",
    "currently",
    "diff",
    "estado",
    "hoy",
    "latest",
    "modificada",
    "modificadas",
    "modificado",
    "modificados",
    "modified",
    "now",
    "passing",
    "result",
    "status",
    "today",
}


class ConversationRetrievalPolicy:
    def allow(self, text: str, *, context_enabled: bool) -> bool:
        if not context_enabled:
            return False
        normalized = _normalize(text)
        if not normalized or normalized in _ACKNOWLEDGEMENTS or len(normalized.split()) <= 2:
            return False
        if _is_live_state(normalized):
            return False
        return True


def _normalize(text: str) -> str:
    ascii_text = (
        unicodedata.normalize("NFKD", text.casefold())
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    chars = (char if char.isalnum() else " " for char in ascii_text)
    return " ".join("".join(chars).split())


def _is_live_state(normalized: str) -> bool:
    tokens = set(normalized.split())
    return bool(tokens & _LIVE_TARGET_WORDS) and bool(tokens & _LIVE_STATE_WORDS)
