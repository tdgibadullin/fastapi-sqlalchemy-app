"""API endpoints for user management."""

import logging
from typing import TYPE_CHECKING

from celery.exceptions import CeleryError
from fastapi import APIRouter, HTTPException, status

import app.crud.user as user_crud
from app.api.deps import CurrentUser
from app.celery.tasks import send_welcome_email
from app.core.db import SessionDep
from app.core.security import verify_password
from app.schemas.user import (
    UserCreate,
    UserOut,
    UserPasswordUpdate,
    UserUpdate,
)

if TYPE_CHECKING:
    from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(
    session: SessionDep,
    user_in: UserCreate,
) -> User:
    """Register a new user.

    Creates a user record in the database and triggers a background
    task to send a welcome email.

    Args:
        session: Database session.
        user_in: User creation data.

    Returns:
        Newly created user.

    Raises:
        HTTPException: 409 Conflict if the email or username is already
            taken by another user.
    """
    user = await user_crud.get_user_by_email(
        session=session,
        email=user_in.email,
    )
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already taken",
        )

    user = await user_crud.get_user_by_username(
        session=session,
        username=user_in.username,
    )
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )

    user = await user_crud.create_user(session=session, user_in=user_in)
    logger.info("User %s (%s) registered successfully", user.id, user.email)

    try:
        send_welcome_email.delay(email=user.email, username=user.username)
    except CeleryError:
        logger.exception(
            "Failed to enqueue welcome email for user %s (%s)",
            user.id,
            user.email,
        )

    return user


@router.get("/me", response_model=UserOut)
async def read_user_me(current_user: CurrentUser) -> User:
    """Retrieve the current user.

    Args:
        current_user: Authenticated user.

    Returns:
        Current user.
    """
    return current_user


@router.patch("/me", response_model=UserOut)
async def update_user_me(
    session: SessionDep,
    current_user: CurrentUser,
    user_in: UserUpdate,
) -> User:
    """Update the current user's username and/or email.

    Args:
        session: Database session.
        current_user: Authenticated user.
        user_in: User update data.

    Returns:
        Updated user.

    Raises:
        HTTPException: 409 Conflict if the new email or username is
            already taken by another user.
    """
    if user_in.username and user_in.username != current_user.username:
        user = await user_crud.get_user_by_username(
            session=session,
            username=user_in.username,
        )
        if user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken",
            )

    if user_in.email and user_in.email != current_user.email:
        user = await user_crud.get_user_by_email(
            session=session,
            email=user_in.email,
        )
        if user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already taken",
            )

    return await user_crud.update_user(
        session=session,
        user=current_user,
        user_in=user_in,
    )


@router.patch("/me/password", status_code=status.HTTP_204_NO_CONTENT)
async def update_password_me(
    session: SessionDep,
    current_user: CurrentUser,
    password_in: UserPasswordUpdate,
) -> None:
    """Update the current user's password.

    Requires the current password to authorize the change.

    Args:
        session: Database session.
        current_user: Authenticated user.
        password_in: Password update data.

    Raises:
        HTTPException: 400 Bad Request if the provided current password
            does not match the stored hash, or if the new password is
            the same as the current one.
    """
    is_valid, _ = verify_password(
        password_in.current_password,
        current_user.hashed_password,
    )
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password",
        )

    if password_in.current_password == password_in.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password cannot be the same as the current one",
        )

    await user_crud.update_password(
        session=session,
        user=current_user,
        password=password_in.new_password,
    )
    logger.info(
        "User %s (%s) updated their password",
        current_user.id,
        current_user.email,
    )


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_me(
    session: SessionDep,
    current_user: CurrentUser,
) -> None:
    """Delete the current user.

    Args:
        session: Database session.
        current_user: Authenticated user.
    """
    await user_crud.delete_user(session=session, user=current_user)
    logger.info(
        "User %s (%s) deleted their account",
        current_user.id,
        current_user.email,
    )
