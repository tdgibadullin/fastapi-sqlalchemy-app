"""Script for seeding the database with initial test data."""

import asyncio
import logging

from sqlalchemy import select

from app.core.db import AsyncSessionLocal
from app.core.logger import setup_logging
from app.core.security import get_password_hash
from app.models.post import Post
from app.models.user import User

logger = logging.getLogger(__name__)


async def seed_data() -> None:
    """Populate the database with sample users and posts.

    Provides baseline data to facilitate local development, ensuring the
    application is immediately usable after a fresh installation.
    """
    logger.info("Starting database seeding...")

    async with AsyncSessionLocal() as session:
        if await session.scalar(select(User.id).limit(1)):
            logger.info("Database already seeded, skipping")
            return

        user1 = User(
            username="alice",
            email="user1@example.com",
            hashed_password=get_password_hash("password123"),
        )
        user2 = User(
            username="bob",
            email="user2@example.com",
            hashed_password=get_password_hash("password321"),
        )
        session.add_all([user1, user2])
        await session.flush()

        posts = [
            Post(
                title="First Post by Alice",
                body="Hello world! This is my first post on this shiny new "
                "app.",
                owner_id=user1.id,
            ),
            Post(
                title="uv is insanely fast",
                body="I switched my project to uv, and the builds are "
                "practically instant.",
                owner_id=user1.id,
            ),
            Post(
                title="Bob's introduction",
                body="Hi everyone, Bob here. Just testing out the ownership "
                "validation to make sure Alice can't delete this post.",
                owner_id=user2.id,
            ),
            Post(
                title="PostgreSQL 18 Features",
                body="Exploring the new performance improvements in the "
                "latest PG release.",
                owner_id=user2.id,
            ),
            Post(
                title="Another one from Alice",
                body="Just filling up the database with some initial content "
                "to make the app feel alive.",
                owner_id=user1.id,
            ),
        ]
        session.add_all(posts)

        await session.commit()

        logger.info(
            "Successfully seeded 2 users (%s: %s, %s: %s) and 5 posts",
            user1.username,
            user1.email,
            user2.username,
            user2.email,
        )


if __name__ == "__main__":
    setup_logging()
    asyncio.run(seed_data())
