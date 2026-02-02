"""CRUD operations for posts."""

from typing import TYPE_CHECKING

from sqlalchemy import select

from app.models.post import Post

if TYPE_CHECKING:
    from collections.abc import Sequence

    from sqlalchemy.ext.asyncio import AsyncSession

    from app.schemas.post import PostCreate, PostUpdate


async def create_post(
    *,
    session: AsyncSession,
    post_in: PostCreate,
    owner_id: int,
) -> Post:
    """Create a new post.

    Args:
        session: Database session.
        post_in: Post creation data.
        owner_id: ID of the user who authored the post.

    Returns:
        Newly created Post instance.
    """
    post = Post(**post_in.model_dump(), owner_id=owner_id)
    session.add(post)
    await session.commit()
    await session.refresh(post)
    return post


async def get_post_by_id(
    *,
    session: AsyncSession,
    post_id: int,
) -> Post | None:
    """Retrieve a post by its ID.

    Args:
        session: Database session.
        post_id: ID of the post.

    Returns:
        Post instance if found, otherwise None.
    """
    return await session.get(Post, post_id)


async def get_posts(
    *,
    session: AsyncSession,
    skip: int = 0,
    limit: int = 100,
) -> Sequence[Post]:
    """Retrieve a list of posts with pagination.

    Args:
        session: Database session.
        skip: Number of records to skip.
        limit: Maximum number of records to return.

    Returns:
        Sequence of Post instances, ordered by creation time in
        descending order.
    """
    statement = (
        select(Post)
        .order_by(Post.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await session.scalars(statement)
    return result.all()


async def update_post(
    *,
    session: AsyncSession,
    post: Post,
    post_in: PostUpdate,
) -> Post:
    """Update a post.

    Only fields explicitly provided in the input schema are updated.

    Args:
        session: Database session.
        post: Post instance to update.
        post_in: Post update data.

    Returns:
        Updated Post instance.
    """
    update_data = post_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(post, field, value)

    await session.commit()
    await session.refresh(post)
    return post


async def delete_post(
    *,
    session: AsyncSession,
    post: Post,
) -> None:
    """Delete a post.

    Cascading deletes are handled by the database constraint
    (ondelete="CASCADE").

    Args:
        session: Database session.
        post: Post instance to delete.
    """
    await session.delete(post)
    await session.commit()
