"""Logging setup for application bootstrap."""

import logging
import sys

from ai_assistant.application.errors import ConfigurationError


LOG_FORMAT = "%(levelname)s:%(name)s:%(message)s"


def configure_logging(level_name: str) -> None:
    level = _level(level_name)
    logging.basicConfig(level=level, stream=sys.stderr, format=LOG_FORMAT)
    logging.getLogger().setLevel(level)


def _level(level_name: str) -> int:
    level = logging.getLevelName(level_name.upper())
    if not isinstance(level, int):
        raise ConfigurationError(f"Unsupported AI_ASSISTANT_LOG_LEVEL: {level_name!r}")
    return level
