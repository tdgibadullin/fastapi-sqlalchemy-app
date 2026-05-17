"""Tests for post management API endpoints."""

from typing import TYPE_CHECKING

import pytest
from fastapi import status

from app.models.post import Post
from app.schemas.post import PostOut
from tests.constants import (
    NONEXISTENT_ID,
    POST_BODY,
    POST_TITLE,
)

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.models.user import User

NEW_TITLE = "New Title"
NEW_BODY = "New body"


async def test_create_post(
    client: AsyncClient,
    db_session: AsyncSession,
    user: User,
    auth_headers: dict[str, str],
) -> None:
    """Test that a user can create a post.

    Args:
        client: HTTP client fixture.
        db_session: Database session fixture.
        user: Test user fixture.
        auth_headers: Fixture providing authorization headers with the
            test user's access token.
    """
    payload = {"title": POST_TITLE, "body": POST_BODY}

    response = await client.post(
        "/posts/",
        headers=auth_headers,
        json=payload,
    )

    assert response.status_code == status.HTTP_201_CREATED
    response_json = response.json()
    assert {k: response_json.get(k) for k in payload} == payload
    assert response_json["owner_id"] == user.id

    db_session.expire_all()
    created_post = await db_session.get(Post, response_json["id"])

    assert PostOut.model_validate(created_post).model_dump(mode="json") == (
        PostOut(**response_json).model_dump(mode="json")
    )


@pytest.mark.parametrize(
    ("query_params", "idx"),
    [
        pytest.param(
            {"limit": 1},
            1,
            id="limit",
        ),
        pytest.param(
            {"skip": 1, "limit": 1},
            0,
            id="skip_and_limit",
        ),
    ],
)
async def test_read_posts(
    client: AsyncClient,
    db_session: AsyncSession,
    user: User,
    query_params: dict[str, int],
    idx: int,
) -> None:
    """Test that posts can be retrieved and paginated.

    Args:
        client: HTTP client fixture.
        db_session: Database session fixture.
        user: Test user fixture.
        query_params: Pagination parameters.
        idx: Index of the post in the local `posts` list to compare
            against.
    """
    posts = [
        Post(
            title=f"{POST_TITLE} {i}",
            body=f"{POST_BODY} {i}",
            owner_id=user.id,
        )
        for i in range(2)
    ]
    db_session.add_all(posts)
    await db_session.flush()

    response = await client.get("/posts/", params=query_params)

    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert len(response_json) == query_params["limit"]
    assert PostOut(**response_json[0]).model_dump(mode="json") == (
        PostOut.model_validate(posts[idx]).model_dump(mode="json")
    )


async def test_read_post(
    client: AsyncClient,
    post: Post,
) -> None:
    """Test that a single post can be retrieved.

    Args:
        client: HTTP client fixture.
        post: Test post fixture.
    """
    response = await client.get(f"/posts/{post.id}")

    assert response.status_code == status.HTTP_200_OK
    assert PostOut(**response.json()).model_dump(mode="json") == (
        PostOut.model_validate(post).model_dump(mode="json")
    )


async def test_read_post_not_found(client: AsyncClient) -> None:
    """Test that retrieving a nonexistent post returns a 404 error.

    Args:
        client: HTTP client fixture.
    """
    response = await client.get(f"/posts/{NONEXISTENT_ID}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Post not found"


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param(
            {"title": NEW_TITLE},
            id="update_title",
        ),
        pytest.param(
            {"body": NEW_BODY},
            id="update_body",
        ),
        pytest.param(
            {"title": NEW_TITLE, "body": NEW_BODY},
            id="update_title_and_body",
        ),
    ],
)
async def test_update_post(
    client: AsyncClient,
    db_session: AsyncSession,
    post: Post,
    auth_headers: dict[str, str],
    payload: dict[str, str],
) -> None:
    """Test that a user can update their post title and/or body.

    Args:
        client: HTTP client fixture.
        db_session: Database session fixture.
        post: Test post fixture.
        auth_headers: Fixture providing authorization headers with the
            current user's access token.
        payload: Post update payload.
    """
    response = await client.patch(
        f"/posts/{post.id}",
        headers=auth_headers,
        json=payload,
    )

    assert response.status_code == status.HTTP_200_OK
    assert {k: response.json().get(k) for k in payload} == payload

    post_id = post.id
    db_session.expire(post)
    updated_post = await db_session.get(Post, post_id)

    assert {k: getattr(updated_post, k) for k in payload} == payload


async def test_update_post_not_found(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """Test that updating a nonexistent post returns a 404 error.

    Args:
        client: HTTP client fixture.
        auth_headers: Fixture providing authorization headers with the
            current user's access token.
    """
    response = await client.patch(
        f"/posts/{NONEXISTENT_ID}",
        headers=auth_headers,
        json={"title": NEW_TITLE},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Post not found"


async def test_update_post_forbidden(
    client: AsyncClient,
    post: Post,
    other_auth_headers: dict[str, str],
) -> None:
    """Test that a user cannot update another user's post.

    Args:
        client: HTTP client fixture.
        post: Test post fixture.
        other_auth_headers: Fixture providing authorization headers with
            an access token for a non-owner of the post.
    """
    response = await client.patch(
        f"/posts/{post.id}",
        headers=other_auth_headers,
        json={"title": NEW_TITLE},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Permission denied"


async def test_delete_post(
    client: AsyncClient,
    db_session: AsyncSession,
    post: Post,
    auth_headers: dict[str, str],
) -> None:
    """Test that a user can delete their post.

    Args:
        client: HTTP client fixture.
        db_session: Database session fixture.
        post: Test post fixture.
        auth_headers: Fixture providing authorization headers with the
            current user's access token.
    """
    response = await client.delete(f"/posts/{post.id}", headers=auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db_session.expunge(post)
    assert await db_session.get(Post, post.id) is None


async def test_delete_post_not_found(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """Test that deleting a nonexistent post returns a 404 error.

    Args:
        client: HTTP client fixture.
        auth_headers: Fixture providing authorization headers with the
            current user's access token.
    """
    response = await client.delete(
        f"/posts/{NONEXISTENT_ID}",
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Post not found"


async def test_delete_post_forbidden(
    client: AsyncClient,
    post: Post,
    other_auth_headers: dict[str, str],
) -> None:
    """Test that a user cannot delete another user's post.

    Args:
        client: HTTP client fixture.
        post: Test post fixture.
        other_auth_headers: Fixture providing authorization headers with
            an access token for a non-owner of the post.
    """
    response = await client.delete(
        f"/posts/{post.id}",
        headers=other_auth_headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Permission denied"
