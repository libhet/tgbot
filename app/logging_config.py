"""Logging setup for the application."""
from __future__ import annotations

import logging
import logging.config
from typing import Any, Dict


def configure_logging(level: str = "INFO") -> None:
    """Configure logging for the application using standard library handlers."""

    logging_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": level,
            }
        },
        "loggers": {
            "": {
                "handlers": ["console"],
                "level": level,
            }
        },
    }
    logging.config.dictConfig(logging_config)
