"""Database infrastructure layer.

This module initializes the SQLAlchemy engine, session factory, and base
class for ORM models.

It also defines a FastAPI dependency for per-request SQLAlchemy
sessions.
"""

from typing import TYPE_CHECKING, Annotated

from fastapi import Depends
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

if TYPE_CHECKING:
    from collections.abc import Generator

# Database constraint and index naming convention for the SQLAlchemy
# declarative base class.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models.

    Attributes:
        metadata: MetaData instance configured with a naming convention
            to ensure deterministic constraint and index names across
            all database environments.
    """

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


def get_db() -> Generator[Session]:
    """Yields a SQLAlchemy session and closes it after use."""
    with SessionLocal() as db:
        yield db


# Type alias to simplify injecting per-request SQLAlchemy sessions.
SessionDep = Annotated[Session, Depends(get_db)]
