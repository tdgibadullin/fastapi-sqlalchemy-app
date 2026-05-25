"""API endpoints for managing posts."""

import logging
from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, HTTPException, Path, Query, status

import app.crud.post as post_crud
from app.api.deps import CurrentUser
from app.core.db import SessionDep
from app.schemas.error import ErrorResponse
from app.schemas.post import PostCreate, PostOut, PostUpdate

if TYPE_CHECKING:
    from collections.abc import Sequence

    from app.models.post import Post

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("/", response_model=PostOut, status_code=status.HTTP_201_CREATED)
async def create_post(
    session: SessionDep,
    current_user: CurrentUser,
    post_in: PostCreate,
) -> Post:
    """Create a new post.

    Args:
        session: Database session.
        current_user: Authenticated user.
        post_in: Post creation data.

    Returns:
        Newly created post.
    """
    return await post_crud.create_post(
        session=session,
        post_in=post_in,
        owner_id=current_user.id,
    )


@router.get("/", response_model=list[PostOut])
async def read_posts(
    session: SessionDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> Sequence[Post]:
    """Retrieve posts with pagination.

    Args:
        session: Database session.
        skip: Number of records to skip.
        limit: Maximum number of records to return.

    Returns:
        Sequence of posts.
    """
    return await post_crud.get_posts(session=session, skip=skip, limit=limit)


@router.get(
    "/{id}",
    response_model=PostOut,
    responses={404: {"model": ErrorResponse, "description": "Post not found"}},
)
async def read_post(
    session: SessionDep,
    post_id: Annotated[int, Path(alias="id", gt=0)],
) -> Post:
    """Retrieve a post.

    Args:
        session: Database session.
        post_id: ID of the post to retrieve.

    Returns:
        Requested post.

    Raises:
        HTTPException: 404 Not Found if the post does not exist.
    """
    post = await post_crud.get_post(session=session, post_id=post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    return post


@router.patch(
    "/{id}",
    response_model=PostOut,
    responses={
        403: {"model": ErrorResponse, "description": "Permission denied"},
        404: {"model": ErrorResponse, "description": "Post not found"},
    },
)
async def update_post(
    session: SessionDep,
    current_user: CurrentUser,
    post_id: Annotated[int, Path(alias="id", gt=0)],
    post_in: PostUpdate,
) -> Post:
    """Update a post.

    Args:
        session: Database session.
        current_user: Authenticated user.
        post_id: ID of the post to update.
        post_in: Post update data.

    Returns:
        Updated post.

    Raises:
        HTTPException: 404 Not Found if the post does not exist.
        HTTPException: 403 Forbidden if the authenticated user is not
            the post owner.
    """
    post = await post_crud.get_post(session=session, post_id=post_id)

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    if post.owner_id != current_user.id:
        logger.warning(
            "User %s attempted to update post %s belonging to user %s",
            current_user.id,
            post.id,
            post.owner_id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )

    return await post_crud.update_post(
        session=session,
        post=post,
        post_in=post_in,
    )


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        403: {"model": ErrorResponse, "description": "Permission denied"},
        404: {"model": ErrorResponse, "description": "Post not found"},
    },
)
async def delete_post(
    session: SessionDep,
    current_user: CurrentUser,
    post_id: Annotated[int, Path(alias="id", gt=0)],
) -> None:
    """Delete a post.

    Args:
        session: Database session.
        current_user: Authenticated user.
        post_id: ID of the post to delete.

    Raises:
        HTTPException: 404 Not Found if the post does not exist.
        HTTPException: 403 Forbidden if the authenticated user is not
            the post owner.
    """
    post = await post_crud.get_post(session=session, post_id=post_id)

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    if post.owner_id != current_user.id:
        logger.warning(
            "User %s attempted to delete post %s belonging to user %s",
            current_user.id,
            post.id,
            post.owner_id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )

    await post_crud.delete_post(session=session, post=post)
