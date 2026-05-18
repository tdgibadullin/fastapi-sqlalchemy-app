"""API endpoint for application health monitoring."""

import logging

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.db import SessionDep

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check(session: SessionDep) -> dict[str, str]:
    """Check application health by verifying database connectivity.

    Args:
        session: Database session.

    Returns:
        Dictionary indicating the service is healthy.

    Raises:
        HTTPException: 503 Service Unavailable if the database cannot be
            reached.
    """
    try:
        await session.scalar(text("SELECT 1"))
    except SQLAlchemyError as exc:
        logger.exception("Health check failed: database connectivity issue")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is unavailable",
        ) from exc

    return {"status": "ok"}
