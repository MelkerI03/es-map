"""Logging utilities for configuring and retrieving application loggers.

This module provides a centralized logging configuration to ensure
consistent formatting and handler setup across the application.
"""

import datetime
import json
import logging
import sys
from pathlib import Path

DEFAULT_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DEFAULT_DATEFMT = "%Y-%m-%d %H:%M:%S"


def setup_logging(
    log_level: str = "INFO",
    log_file: str | Path | None = None,
) -> None:
    """Configure global logging for the application.

    This function initializes the root logger with a console handler and
    optionally a file handler. Existing handlers are cleared to ensure
    a clean configuration.

    Note:
        This should be called once from the application's CLI entrypoint.

    Args:
        level: Logging level as a string (e.g., "DEBUG", "INFO", "WARNING").
        log_file: Optional path to a file where logs should be written.

    Raises:
        ValueError: If the provided logging level is invalid.
    """
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")

    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    root_logger.handlers.clear()

    # formatter = logging.Formatter(
    #     fmt=DEFAULT_FORMAT,
    #     datefmt=DEFAULT_DATEFMT,
    # )
    formatter = JsonFormatter()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Optional file logging
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """Retrieve a logger instance for a given module or component.

    Args:
        name: The name of the logger, typically __name__.

    Returns:
        A configured logger instance.
    """
    return logging.getLogger(name)


class JsonFormatter(logging.Formatter):
    """Format log records as structured JSON."""

    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": datetime.date.fromtimestamp(record.created).strftime(
                DEFAULT_DATEFMT
            ),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Include extra fields (anything not standard)
        standard_fields = {
            "name",
            "msg",
            "args",
            "levelname",
            "levelno",
            "pathname",
            "filename",
            "module",
            "exc_info",
            "exc_text",
            "stack_info",
            "lineno",
            "funcName",
            "created",
            "msecs",
            "relativeCreated",
            "thread",
            "threadName",
            "taskName",
            "processName",
            "process",
        }

        for key, value in record.__dict__.items():
            if key not in standard_fields:
                log_record[key] = value

        return json.dumps(log_record, indent=2)
