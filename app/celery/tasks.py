"""Celery tasks."""

from email.message import EmailMessage
from email.utils import formataddr
from smtplib import SMTP, SMTPException

from celery.utils.log import get_task_logger

from app.celery.celery_app import celery_app
from app.core.config import settings

logger = get_task_logger(__name__)


@celery_app.task(
    autoretry_for=(OSError, SMTPException),
    max_retries=5,
    retry_backoff=True,
    soft_time_limit=25,
    time_limit=30,
)
def send_welcome_email(email: str, username: str) -> None:
    """Send a welcome email to a newly registered user.

    This task connects to the configured SMTP server to dispatch the
    email. It handles system-level or SMTP exceptions and retries
    automatically in the background.

    Args:
        email: Recipient's email address.
        username: Recipient's username.
    """
    logger.info("Starting welcome email task for %s (%s)", email, username)

    msg = EmailMessage()
    msg.set_content(f"Hello {username}, welcome to {settings.PROJECT_NAME}!")
    msg["Subject"] = "Welcome!"
    msg["From"] = formataddr((settings.SENDER_NAME, settings.SENDER_EMAIL))
    msg["To"] = email

    with SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
        if settings.SMTP_TLS:
            server.starttls()
        if settings.SMTP_USER and settings.SMTP_PASSWORD:
            server.login(
                settings.SMTP_USER,
                settings.SMTP_PASSWORD.get_secret_value(),
            )
        server.send_message(msg)

    logger.info("Welcome email successfully sent to %s (%s)", email, username)
