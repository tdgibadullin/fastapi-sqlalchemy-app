"""Alembic environment configuration."""

import asyncio
from typing import TYPE_CHECKING

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

# Import models to register them in Base.metadata for Alembic.
import app.models  # noqa: F401
from app.core.config import settings
from app.core.db import Base
from app.core.logger import setup_logging

if TYPE_CHECKING:
    from sqlalchemy.engine import Connection

setup_logging()


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode without a database connection.

    Emits SQL statements instead of executing them against the
    database.
    """
    context.configure(
        url=str(settings.DATABASE_URL),
        target_metadata=Base.metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations in 'online' mode within a sync context.

    Args:
        connection: Synchronous database connection provided by the
            async engine during the run_sync execution.
    """
    context.configure(
        connection=connection,
        target_metadata=Base.metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode using an async engine."""
    connectable = create_async_engine(
        str(settings.DATABASE_URL),
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Entry point for online migrations."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
