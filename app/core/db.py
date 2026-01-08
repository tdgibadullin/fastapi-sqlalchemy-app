"""Database infrastructure layer.

This module initializes the asynchronous SQLAlchemy engine and session
factory, as well as the base class for ORM models.

It also defines a FastAPI dependency for per-request SQLAlchemy
sessions.
"""

from typing import TYPE_CHECKING, Annotated

from fastapi import Depends
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

# Database constraint and index naming convention for the SQLAlchemy
# declarative base class.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=settings.ENVIRONMENT == "local",
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models.

    Attributes:
        metadata: MetaData instance configured with a naming convention
            to ensure deterministic constraint and index names across
            all database environments.
    """

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


async def get_db() -> AsyncGenerator[AsyncSession]:
    """Yields an async SQLAlchemy session and closes it after use."""
    async with AsyncSessionLocal() as session:
        yield session


# Type alias to simplify injecting per-request SQLAlchemy sessions.
SessionDep = Annotated[AsyncSession, Depends(get_db)]
