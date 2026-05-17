"""Tests for API endpoint dependencies."""

from typing import TYPE_CHECKING

import pytest
from fastapi import status

from app.core.security import create_access_token
from tests.constants import NONEXISTENT_ID

if TYPE_CHECKING:
    from httpx import AsyncClient


@pytest.mark.parametrize(
    "token",
    [
        pytest.param(
            "malformed.token.string",
            id="malformed_token",
        ),
        pytest.param(
            create_access_token(data={"wrong_field": "123"}),
            id="missing_subject_claim",
        ),
        pytest.param(
            create_access_token(data={"sub": "not_an_integer"}),
            id="noninteger_subject_claim",
        ),
        pytest.param(
            create_access_token(data={"sub": str(NONEXISTENT_ID)}),
            id="nonexistent_user",
        ),
    ],
)
async def test_get_current_user_unauthorized(
    client: AsyncClient,
    token: str,
) -> None:
    """Test that access to protected endpoints is denied for bad tokens.

    Args:
        client: HTTP client fixture.
        token: Access token string failing validation requirements.
    """
    response = await client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Could not validate credentials"
