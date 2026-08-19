"""Logging setup for application bootstrap."""

import logging
import os
import sys
from typing import IO

from ai_assistant.application.errors import ConfigurationError


LOG_FORMAT = "%(levelname)s:%(name)s:%(message)s"

_RESET = "\033[0m"
_BOLD = "\033[1m"
_DIM = "\033[2m"
_CONTEXT_COLOR = "\033[33m"  # yellow, matches Nest's context color

_LEVEL_COLORS = {
    logging.DEBUG: "\033[35m",  # magenta
    logging.INFO: "\033[32m",  # green
    logging.WARNING: "\033[33m",  # yellow
    logging.ERROR: "\033[31m",  # red
    logging.CRITICAL: "\033[97;41m",  # white on red
}


class NestStyleFormatter(logging.Formatter):
    """Render records as `timestamp LEVEL [context] message`, Nest-console style."""

    def __init__(self, *, colorize: bool) -> None:
        super().__init__(datefmt="%m/%d/%Y, %H:%M:%S")
        self._colorize = colorize

    def format(self, record: logging.LogRecord) -> str:
        timestamp = self.formatTime(record, self.datefmt)
        level = f"{record.levelname:<8}"
        context = f"[{record.name}]"

        if self._colorize:
            level_color = _LEVEL_COLORS.get(record.levelno, "")
            timestamp = f"{_DIM}{timestamp}{_RESET}"
            level = f"{level_color}{_BOLD}{level}{_RESET}"
            context = f"{_CONTEXT_COLOR}{context}{_RESET}"

        formatted = f"{timestamp}  {level} {context} {record.getMessage()}"
        if record.exc_info:
            formatted = f"{formatted}\n{self.formatException(record.exc_info)}"
        return formatted


def _supports_color(stream: IO[str]) -> bool:
    if os.environ.get("NO_COLOR") is not None:
        return False
    if os.environ.get("FORCE_COLOR") is not None:
        return True
    isatty = getattr(stream, "isatty", None)
    return bool(isatty and isatty())


def configure_logging(level_name: str) -> None:
    level = _level(level_name)
    handler = logging.StreamHandler(stream=sys.stderr)
    handler.setFormatter(NestStyleFormatter(colorize=_supports_color(sys.stderr)))

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)


def _level(level_name: str) -> int:
    level = logging.getLevelName(level_name.upper())
    if not isinstance(level, int):
        raise ConfigurationError(f"Unsupported AI_ASSISTANT_LOG_LEVEL: {level_name!r}")
    return level
