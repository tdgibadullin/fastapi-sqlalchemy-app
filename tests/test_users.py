"""Tests for user management API endpoints."""

from typing import TYPE_CHECKING

import pytest
from celery.exceptions import CeleryError
from fastapi import status

from app.core.security import verify_password
from app.models.post import Post
from app.models.user import User
from app.schemas.user import UserOut
from tests.constants import (
    EMAIL,
    INCORRECT_PASSWORD,
    OTHER_EMAIL,
    OTHER_USERNAME,
    TEST_PASSWORD,
    USERNAME,
)

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession

NEW_USERNAME = "new_user"
NEW_EMAIL = "new_user@example.com"
# Mock credential for the test environment only.
NEW_PASSWORD = "NewPassword.321"  # noqa: S105


async def test_register_user(
    client: AsyncClient,
    db_session: AsyncSession,
    mock_send_welcome_email: MagicMock,
) -> None:
    """Test that a user can register and a welcome email is sent.

    Args:
        client: HTTP client fixture.
        db_session: Database session fixture.
        mock_send_welcome_email: Fixture for mocking the delay method of
            the Celery send_welcome_email task.
    """
    payload = {
        "username": USERNAME,
        "email": EMAIL,
        "password": TEST_PASSWORD,
    }

    response = await client.post("/users/", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    response_json = response.json()
    assert (
        response_json["username"],
        response_json["email"],
    ) == (
        payload["username"],
        payload["email"],
    )

    db_session.expire_all()
    created_user = await db_session.get(User, response_json["id"])

    assert UserOut.model_validate(created_user).model_dump(mode="json") == (
        UserOut(**response_json).model_dump(mode="json")
    )
    mock_send_welcome_email.assert_called_once_with(
        email=payload["email"],
        username=payload["username"],
    )


async def test_register_user_celery_error(
    client: AsyncClient,
    db_session: AsyncSession,
    mock_send_welcome_email: MagicMock,
) -> None:
    """Test that a user can register even if the Celery task fails.

    Args:
        client: HTTP client fixture.
        db_session: Database session fixture.
        mock_send_welcome_email: Fixture for mocking the delay method of
            the Celery send_welcome_email task.
    """
    mock_send_welcome_email.side_effect = CeleryError(
        "Message broker is unreachable"
    )
    payload = {
        "username": USERNAME,
        "email": EMAIL,
        "password": TEST_PASSWORD,
    }

    response = await client.post("/users/", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    response_json = response.json()
    assert (
        response_json["username"],
        response_json["email"],
    ) == (
        payload["username"],
        payload["email"],
    )

    db_session.expire_all()
    created_user = await db_session.get(User, response_json["id"])

    assert UserOut.model_validate(created_user).model_dump(mode="json") == (
        UserOut(**response_json).model_dump(mode="json")
    )
    mock_send_welcome_email.assert_called_once_with(
        email=payload["email"],
        username=payload["username"],
    )


@pytest.mark.parametrize(
    ("payload", "expected_detail"),
    [
        pytest.param(
            {
                # Conflicts with other_user.username.
                "username": OTHER_USERNAME,
                "email": EMAIL,
                "password": TEST_PASSWORD,
            },
            "Username already taken",
            id="username_conflict",
        ),
        pytest.param(
            {
                "username": USERNAME,
                # Conflicts with other_user.email.
                "email": OTHER_EMAIL,
                "password": TEST_PASSWORD,
            },
            "Email already taken",
            id="email_conflict",
        ),
    ],
)
@pytest.mark.usefixtures("other_user")
async def test_register_user_conflict(
    client: AsyncClient,
    payload: dict[str, str],
    expected_detail: str,
) -> None:
    """Test that a user cannot register with a taken username or email.

    Args:
        client: HTTP client fixture.
        payload: Registration payload with conflicting data.
        expected_detail: Expected error message in the response `detail`
            field.
    """
    response = await client.post("/users/", json=payload)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == expected_detail


async def test_read_user_me(
    client: AsyncClient,
    user: User,
    auth_headers: dict[str, str],
) -> None:
    """Test that a user can retrieve their profile.

    Args:
        client: HTTP client fixture.
        user: Test user fixture.
        auth_headers: Fixture providing authorization headers with the
            test user's access token.
    """
    response = await client.get("/users/me", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert UserOut(**response.json()).model_dump(mode="json") == (
        UserOut.model_validate(user).model_dump(mode="json")
    )


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param(
            {"username": NEW_USERNAME},
            id="update_username",
        ),
        pytest.param(
            {"email": NEW_EMAIL},
            id="update_email",
        ),
        pytest.param(
            {"username": NEW_USERNAME, "email": NEW_EMAIL},
            id="update_username_and_email",
        ),
    ],
)
async def test_update_user_me(
    client: AsyncClient,
    db_session: AsyncSession,
    user: User,
    auth_headers: dict[str, str],
    payload: dict[str, str],
) -> None:
    """Test that a user can update their username and/or email.

    Args:
        client: HTTP client fixture.
        db_session: Database session fixture.
        user: Test user fixture.
        auth_headers: Fixture providing authorization headers with the
            test user's access token.
        payload: Profile update payload.
    """
    response = await client.patch(
        "/users/me",
        headers=auth_headers,
        json=payload,
    )

    assert response.status_code == status.HTTP_200_OK
    assert {k: response.json().get(k) for k in payload} == payload

    user_id = user.id
    db_session.expire(user)
    updated_user = await db_session.get(User, user_id)

    assert {k: getattr(updated_user, k) for k in payload} == payload


@pytest.mark.parametrize(
    ("payload", "expected_detail"),
    [
        pytest.param(
            # Conflicts with other_user.username.
            {"username": OTHER_USERNAME},
            "Username already taken",
            id="username_conflict",
        ),
        pytest.param(
            # Conflicts with other_user.email.
            {"email": OTHER_EMAIL},
            "Email already taken",
            id="email_conflict",
        ),
    ],
)
@pytest.mark.usefixtures("other_user")
async def test_update_user_me_conflict(
    client: AsyncClient,
    auth_headers: dict[str, str],
    payload: dict[str, str],
    expected_detail: str,
) -> None:
    """Test that profile update fails if the username or email is taken.

    Args:
        client: HTTP client fixture.
        auth_headers: Fixture providing authorization headers with the
            current user's access token.
        payload: Profile update payload with conflicting data.
        expected_detail: Expected error message in the response `detail`
            field.
    """
    response = await client.patch(
        "/users/me",
        headers=auth_headers,
        json=payload,
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == expected_detail


async def test_update_password_me(
    client: AsyncClient,
    db_session: AsyncSession,
    user: User,
    auth_headers: dict[str, str],
) -> None:
    """Test that a user can update their password.

    Args:
        client: HTTP client fixture.
        db_session: Database session fixture.
        user: Test user fixture.
        auth_headers: Fixture providing authorization headers with the
            test user's access token.
    """
    payload = {
        "current_password": TEST_PASSWORD,
        "new_password": NEW_PASSWORD,
    }

    response = await client.patch(
        "/users/me/password",
        headers=auth_headers,
        json=payload,
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    user_id = user.id
    db_session.expire(user)
    updated_user = await db_session.get(User, user_id)

    assert updated_user is not None
    assert isinstance(updated_user.hashed_password, str)
    is_valid, _ = verify_password(
        payload["new_password"],
        updated_user.hashed_password,
    )
    assert is_valid


@pytest.mark.parametrize(
    ("payload", "expected_detail"),
    [
        pytest.param(
            {
                "current_password": INCORRECT_PASSWORD,
                "new_password": NEW_PASSWORD,
            },
            "Incorrect current password",
            id="incorrect_current_password",
        ),
        pytest.param(
            {
                "current_password": TEST_PASSWORD,
                "new_password": TEST_PASSWORD,
            },
            "New password cannot be the same as the current one",
            id="same_as_current_password",
        ),
    ],
)
async def test_update_password_me_bad_request(
    client: AsyncClient,
    auth_headers: dict[str, str],
    payload: dict[str, str],
    expected_detail: str,
) -> None:
    """Test that password update fails if the input is invalid.

    Args:
        client: HTTP client fixture.
        auth_headers: Fixture providing authorization headers with the
            current user's access token.
        payload: Password update payload with invalid data.
        expected_detail: Expected error message in the response `detail`
            field.
    """
    response = await client.patch(
        "/users/me/password",
        headers=auth_headers,
        json=payload,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == expected_detail


async def test_delete_user_me(
    client: AsyncClient,
    db_session: AsyncSession,
    user: User,
    auth_headers: dict[str, str],
) -> None:
    """Test that a user can delete their profile.

    Args:
        client: HTTP client fixture.
        db_session: Database session fixture.
        user: Test user fixture.
        auth_headers: Fixture providing authorization headers with the
            test user's access token.
    """
    response = await client.delete("/users/me", headers=auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db_session.expunge(user)
    assert await db_session.get(User, user.id) is None


async def test_delete_user_me_removes_associated_posts(
    client: AsyncClient,
    db_session: AsyncSession,
    user: User,
    auth_headers: dict[str, str],
    post: Post,
) -> None:
    """Test that deleting a user automatically removes their posts.

    Args:
        client: HTTP client fixture.
        db_session: Database session fixture.
        user: Test user fixture.
        auth_headers: Fixture providing authorization headers with the
            test user's access token.
        post: Test post fixture.
    """
    user_id, post_id = user.id, post.id

    response = await client.delete("/users/me", headers=auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db_session.expire_all()
    assert await db_session.get(User, user_id) is None
    assert await db_session.get(Post, post_id) is None
