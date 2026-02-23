"""API endpoints for user management."""

from typing import TYPE_CHECKING

from fastapi import APIRouter, HTTPException, status

import app.crud.user as user_crud
from app.api.deps import CurrentUser
from app.core.db import SessionDep
from app.schemas.user import UserCreate, UserOut, UserUpdate

if TYPE_CHECKING:
    from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(
    session: SessionDep,
    user_in: UserCreate,
) -> User:
    """Register a new user.

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

    return await user_crud.create_user(session=session, user_in=user_in)


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
    """Update the current user.

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

    return await user_crud.update_user(
        session=session,
        user=current_user,
        user_in=user_in,
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
