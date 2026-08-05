"""Tests for approved process profile registry."""

from types import MappingProxyType

import pytest

from ai_assistant.application.profile_registry import (
    StaticToolProfileRegistry,
    ToolProfile,
    default_profile_registry,
)
from ai_assistant.domain.errors import InvalidToolCallError
from ai_assistant.domain.tools import ToolPermission, ToolProfileId


pytestmark = pytest.mark.unit


def test_default_registry_returns_fixed_core_profile() -> None:
    profile = default_profile_registry().definition_for(ToolProfileId("core-tests"))

    assert profile.argv == (
        "python",
        "-m",
        "pytest",
        "-m",
        "not ollama and not toolserver",
        "-q",
    )
    assert profile.permission == ToolPermission.EXECUTE_PROJECT
    assert profile.env == {"PYTHONDONTWRITEBYTECODE": "1"}
    assert isinstance(profile.env, MappingProxyType)


def test_default_registry_returns_fixed_build_profile() -> None:
    profile = default_profile_registry().definition_for(ToolProfileId("python-compile"))

    assert profile.argv == ("python", "-m", "compileall", "-q", "ai_assistant", "main.py")
    assert profile.permission == ToolPermission.EXECUTE_PROJECT
    assert profile.timeout_seconds == 180.0


def test_unknown_profile_is_denied() -> None:
    with pytest.raises(InvalidToolCallError, match="Unknown profile"):
        default_profile_registry().definition_for(ToolProfileId("missing"))


def test_model_cannot_supply_argv_through_lookup() -> None:
    registry = default_profile_registry()

    profile = registry.definition_for(ToolProfileId("core-tests"))

    assert "rm -rf /" not in profile.argv


def test_profile_rejects_shell_executable() -> None:
    with pytest.raises(InvalidToolCallError, match="argv"):
        _profile(argv=("sh", "-c", "pytest"))


@pytest.mark.parametrize("argv", [("pip", "install", "x"), ("python", "-m", "pip")])
def test_profile_rejects_package_installers(argv: tuple[str, ...]) -> None:
    with pytest.raises(InvalidToolCallError, match="argv"):
        _profile(argv=argv)


def test_profile_rejects_invalid_env_key() -> None:
    with pytest.raises(InvalidToolCallError, match="environment"):
        _profile(env={"api_key": "secret"})


def test_profile_rejects_invalid_output_limits() -> None:
    with pytest.raises(InvalidToolCallError, match="stdout"):
        _profile(stdout_limit_bytes=0)
    with pytest.raises(InvalidToolCallError, match="stderr"):
        _profile(stderr_limit_bytes=2_097_153)


def test_profile_definitions_are_immutable() -> None:
    profiles = default_profile_registry().definitions()

    assert isinstance(profiles, tuple)
    with pytest.raises(TypeError):
        profiles[0].env["PYTHONDONTWRITEBYTECODE"] = "0"


def _profile(
    argv: tuple[str, ...] = ("python", "-m", "pytest", "-q"),
    env: dict[str, str] | None = None,
    stdout_limit_bytes: int = 131072,
    stderr_limit_bytes: int = 131072,
) -> ToolProfile:
    return ToolProfile(
        profile_id=ToolProfileId("custom"),
        argv=argv,
        permission=ToolPermission.EXECUTE_PROJECT,
        timeout_seconds=30.0,
        stdout_limit_bytes=stdout_limit_bytes,
        stderr_limit_bytes=stderr_limit_bytes,
        env=env or {"PYTHONDONTWRITEBYTECODE": "1"},
    )
