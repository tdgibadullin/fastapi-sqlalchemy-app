"""Tests for user authentication API endpoints."""

from typing import TYPE_CHECKING

import pytest
from fastapi import status

from app.schemas.token import Token
from tests.constants import (
    EMAIL,
    INCORRECT_PASSWORD,
    OTHER_EMAIL,
    TEST_PASSWORD,
)

if TYPE_CHECKING:
    from httpx import AsyncClient

    from app.models.user import User


async def test_login_access_token(
    client: AsyncClient,
    user: User,
) -> None:
    """Test that a user can log in and get an access token.

    Args:
        client: HTTP client fixture.
        user: Test user fixture.
    """
    response = await client.post(
        "/login/access-token",
        data={"username": user.email, "password": TEST_PASSWORD},
    )

    assert response.status_code == status.HTTP_200_OK
    assert Token.model_validate(response.json())


@pytest.mark.parametrize(
    ("email", "password"),
    [
        pytest.param(
            # Matches user.email.
            EMAIL,
            INCORRECT_PASSWORD,
            id="incorrect_password",
        ),
        pytest.param(
            OTHER_EMAIL,
            TEST_PASSWORD,
            id="nonexistent_email",
        ),
    ],
)
@pytest.mark.usefixtures("user")
async def test_login_access_token_unauthorized(
    client: AsyncClient,
    email: str,
    password: str,
) -> None:
    """Test that a user cannot log in with invalid credentials.

    Args:
        client: HTTP client fixture.
        email: Email to attempt login with.
        password: Password to attempt login with.
    """
    response = await client.post(
        "/login/access-token",
        data={
            # This field must be named "username" per RFC 6749.
            "username": email,
            "password": password,
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect email or password"
