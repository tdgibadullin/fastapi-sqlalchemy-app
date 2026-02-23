"""API endpoints for user authentication."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.db import SessionDep
from app.core.security import create_access_token
from app.crud.user import authenticate_user
from app.schemas.token import Token, TokenPayload

router = APIRouter(tags=["login"])


@router.post("/login/access-token")
async def login_access_token(
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """Authenticate a user and return an access token.

    This path operation implements the OAuth 2.0 Password grant flow to
    exchange user credentials for an access token. It is intended for
    first-party clients where the application is trusted to handle the
    user's password directly.

    Args:
        session: Database session.
        form_data: URL-encoded credentials, where the `username` field
            contains the user's email address.

    Returns:
        Access token and its type ("bearer" by default).

    Raises:
        HTTPException: 401 Unauthorized if credentials are incorrect.
    """
    user = await authenticate_user(
        session=session,
        email=form_data.username,
        password=form_data.password,
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data=TokenPayload(sub=str(user.id)).model_dump()
    )
    return Token(access_token=access_token)
