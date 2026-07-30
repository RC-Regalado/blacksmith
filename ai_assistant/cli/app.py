"""Compatibility exports for CLI adapter."""

from ai_assistant.bootstrap.container import create_application
from ai_assistant.interfaces.cli.app import CliApplication


def run_cli() -> None:
    create_application().run()


__all__ = ["CliApplication", "run_cli"]
