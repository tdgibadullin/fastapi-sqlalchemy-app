"""Application security utilities.

This module provides functions for JWT access token creation as well as
password verification and hashing.
"""

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

import jwt
from pwdlib import PasswordHash

from app.core.config import settings

if TYPE_CHECKING:
    from typing import Any

password_hash = PasswordHash.recommended()


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """Generate a JWT access token.

    Args:
        data: Dictionary of JWT claims to include in the token payload.
        expires_delta: Optional duration for the token's validity. If
            not provided, the default expiration from settings is used.

    Returns:
        Encoded token string.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + (
        expires_delta
        or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY.get_secret_value(),
        algorithm=settings.ALGORITHM,
    )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a stored hash.

    Args:
        plain_password: Plain-text password provided by the user.
        hashed_password: Hashed password stored in the database.

    Returns:
        True if the password matches the hash, False otherwise.
    """
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate a secure hash for a plain-text password.

    Args:
        password: Plain-text password to hash.

    Returns:
        Hashed password string.
    """
    return password_hash.hash(password)
