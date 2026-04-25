"""Celery application initialization and configuration."""

import logging
import sys

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

    Applies the global logging configuration and enriches Celery task
    logs with task IDs and names.

    Args:
        **_: Unused keyword arguments passed by the Celery signal.
    """
    setup_root_logging()

    task_log_format = (
        "%(asctime)s - [%(task_id)s] - %(task_name)s - %(name)s "
        "- %(levelname)s - %(message)s"
    )
    if settings.ENVIRONMENT == "local":
        task_log_format += " (%(filename)s:%(lineno)d)"

    task_formatter = TaskFormatter(task_log_format)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(task_formatter)

    task_logger = logging.getLogger("app.celery")
    task_logger.addHandler(console_handler)
    task_logger.propagate = False
