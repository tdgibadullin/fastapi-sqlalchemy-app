"""Logging configuration for the application."""

import logging
import sys

from app.core.config import settings


def setup_logging() -> None:
    """Configure application logging.

    Sets up the root logger with environment-specific formatting and
    levels. Redirects Uvicorn loggers to propagate through the root
    configuration.
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    if settings.ENVIRONMENT == "local":
        log_format += " (%(filename)s:%(lineno)d)"

    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )
    if settings.ENVIRONMENT == "local":
        logging.getLogger("app").setLevel(logging.DEBUG)

    uvicorn_loggers = ("uvicorn", "uvicorn.access", "uvicorn.error")
    for logger_name in uvicorn_loggers:
        uvicorn_logger = logging.getLogger(logger_name)
        uvicorn_logger.handlers.clear()
        uvicorn_logger.propagate = True
