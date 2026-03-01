"""Logging configuration for the application."""

import logging
import sys

from app.core.config import settings


def setup_logging() -> None:
    """Configure application logging.

    Sets up the root logger with environment-specific formatting and
    levels. Redirects web server loggers to propagate through the root
    configuration.
    """
    log_format = (
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s "
        "(%(filename)s:%(lineno)d)"
        if settings.ENVIRONMENT == "local"
        else "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    if settings.ENVIRONMENT == "local":
        logging.getLogger("app").setLevel(logging.DEBUG)

    server_loggers = (
        "gunicorn",
        "gunicorn.access",
        "gunicorn.error",
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
    )

    for logger_name in server_loggers:
        server_logger = logging.getLogger(logger_name)
        server_logger.handlers.clear()
        server_logger.propagate = True
