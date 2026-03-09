"""Celery application initialization and configuration."""

import logging

from celery import Celery
from celery.app.log import TaskFormatter
from celery.signals import setup_logging

from app.core.config import settings
from app.core.logger import setup_logging as setup_root_logging

celery_app = Celery(
    "app.celery",
    broker=str(settings.REDIS_URL),
    include=["app.celery.tasks"],
)


@setup_logging.connect
def setup_celery_logging(**_: object) -> None:
    """Integrate Celery loggers with the application's root logger.

    Applies the global logging configuration and enriches
    Celery-specific logs with task IDs and names.

    Args:
        **_: Unused keyword arguments passed by the Celery signal.
    """
    setup_root_logging()

    log_format = (
        "%(asctime)s - %(task_id)s - %(task_name)s - %(name)s - %(levelname)s "
        "- %(message)s"
    )
    if settings.ENVIRONMENT == "local":
        log_format += " (%(filename)s:%(lineno)d)"

    formatter = TaskFormatter(log_format)
    for handler in logging.getLogger().handlers:
        handler.setFormatter(formatter)
