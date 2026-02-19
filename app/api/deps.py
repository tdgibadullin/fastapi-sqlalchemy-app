"""Authentication dependencies for API endpoints."""

from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError

from app.core.config import settings
from app.core.db import SessionDep
from app.crud.user import get_user
from app.models.user import User
from app.schemas.token import TokenPayload

# OAuth 2.0 scheme that extracts the token from headers, handles OpenAPI
# docs, and returns a 401 Unauthorized error if the token is missing.
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

TokenDep = Annotated[str, Depends(oauth2_scheme)]


async def get_current_user(session: SessionDep, token: TokenDep) -> User:
    """Validate the JWT access token and return the corresponding user.

    Args:
        session: Database session.
        token: JWT access token string from the Authorization request
            header.

    Returns:
        User instance associated with the token subject claim.

    Raises:
        HTTPException: 401 Unauthorized if the token is invalid or the
            user does not exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY.get_secret_value(),
            algorithms=[settings.ALGORITHM],
        )
        token_data = TokenPayload(**payload)
    except InvalidTokenError, ValidationError:
        raise credentials_exception from None

    try:
        user_id = int(token_data.sub)
    except ValueError, TypeError:
        raise credentials_exception from None

    user = await get_user(session=session, user_id=user_id)

    if user is None:
        raise credentials_exception

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
