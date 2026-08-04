"""Approved fixed argv profiles for Phase 3 process tools."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from types import MappingProxyType

from ai_assistant.domain.errors import InvalidToolCallError
from ai_assistant.domain.tools import ToolPermission, ToolProfileId

_SHELL_EXECUTABLES = {"sh", "bash", "zsh", "fish", "csh", "ksh"}
_PACKAGE_MANAGERS = {"pip", "pip3", "npm", "pnpm", "yarn"}


@dataclass(frozen=True, slots=True)
class ToolProfile:
    profile_id: ToolProfileId
    argv: tuple[str, ...]
    permission: ToolPermission
    timeout_seconds: float
    env: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not _safe_argv(self.argv):
            raise InvalidToolCallError("profile argv must be fixed safe strings.")
        if self.permission != ToolPermission.EXECUTE_PROJECT:
            raise InvalidToolCallError("profile permission must execute project.")
        if self.timeout_seconds <= 0:
            raise InvalidToolCallError("profile timeout must be positive.")
        object.__setattr__(self, "argv", tuple(self.argv))
        object.__setattr__(self, "env", MappingProxyType(_safe_env(self.env)))


class StaticToolProfileRegistry:
    def __init__(self, profiles: Sequence[ToolProfile]) -> None:
        self._profiles = {profile.profile_id.value: profile for profile in profiles}

    def definition_for(self, profile_id: ToolProfileId) -> ToolProfile:
        try:
            return self._profiles[profile_id.value]
        except KeyError as exc:
            raise InvalidToolCallError(f"Unknown profile: {profile_id.value}") from exc

    def definitions(self) -> tuple[ToolProfile, ...]:
        return tuple(self._profiles.values())


def default_profile_registry() -> StaticToolProfileRegistry:
    return StaticToolProfileRegistry(
        [
            ToolProfile(
                profile_id=ToolProfileId("core-tests"),
                argv=(
                    "python",
                    "-m",
                    "pytest",
                    "-m",
                    "not ollama and not toolserver",
                    "-q",
                ),
                permission=ToolPermission.EXECUTE_PROJECT,
                timeout_seconds=120.0,
                env={"PYTHONDONTWRITEBYTECODE": "1"},
            ),
            ToolProfile(
                profile_id=ToolProfileId("c-toolserver-tests"),
                argv=("python", "-m", "pytest", "-m", "toolserver", "-q"),
                permission=ToolPermission.EXECUTE_PROJECT,
                timeout_seconds=120.0,
                env={"PYTHONDONTWRITEBYTECODE": "1"},
            ),
        ]
    )


def _safe_argv(argv: Sequence[str]) -> bool:
    return (
        bool(argv)
        and all(_safe_arg(arg) for arg in argv)
        and argv[0] not in _SHELL_EXECUTABLES
        and argv[0] not in _PACKAGE_MANAGERS
        and tuple(argv[:3]) != ("python", "-m", "pip")
    )


def _safe_arg(value: str) -> bool:
    return isinstance(value, str) and bool(value) and "\x00" not in value


def _safe_env(env: Mapping[str, str]) -> dict[str, str]:
    safe: dict[str, str] = {}
    for key, value in env.items():
        if not _safe_env_key(key) or not isinstance(value, str) or "\x00" in value:
            raise InvalidToolCallError("profile environment must be sanitized.")
        safe[key] = value
    return safe


def _safe_env_key(value: str) -> bool:
    return value.isidentifier() and value.upper() == value
