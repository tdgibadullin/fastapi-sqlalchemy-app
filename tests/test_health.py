"""Tests for application health monitoring API endpoint."""

from typing import TYPE_CHECKING

from fastapi import status
from sqlalchemy.exc import SQLAlchemyError

if TYPE_CHECKING:
    from httpx import AsyncClient
    from pytest_mock import MockerFixture


async def test_health_check(client: AsyncClient) -> None:
    """Test the response from /health upon successful health check.

    Args:
        client: HTTP client fixture.
    """
    response = await client.get("http://test/health")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}


async def test_health_check_service_unavailable(
    client: AsyncClient,
    mocker: MockerFixture,
) -> None:
    """Test the response from /health upon health check failure.

    Args:
        client: HTTP client fixture.
        mocker: pytest-mock fixture to simulate a database exception.
    """
    mocker.patch(
        "sqlalchemy.ext.asyncio.AsyncSession.scalar",
        side_effect=SQLAlchemyError("Database connection failed"),
        autospec=True,
    )

    response = await client.get("http://test/health")

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert response.json()["detail"] == "Database is unavailable"
