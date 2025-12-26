"""Database access layer.

This module initializes the SQLAlchemy engine, session factory, and base
class for ORM models.

It also defines a FastAPI dependency for per-request database sessions
via the SessionDep type alias.
"""

from typing import TYPE_CHECKING, Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

if TYPE_CHECKING:
    from collections.abc import Generator

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""


def get_db() -> Generator[Session]:
    """Yields a SQLAlchemy session and closes it after use."""
    with SessionLocal() as db:
        yield db


SessionDep = Annotated[Session, Depends(get_db)]
