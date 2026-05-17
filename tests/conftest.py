"""pytest fixtures."""

from typing import TYPE_CHECKING

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.db import Base, get_db
from app.core.security import create_access_token, get_password_hash
from app.main import app
from app.models.post import Post
from app.models.user import User
from tests.constants import (
    EMAIL,
    OTHER_EMAIL,
    OTHER_USERNAME,
    POST_BODY,
    POST_TITLE,
    TEST_PASSWORD,
    USERNAME,
)

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator
    from unittest.mock import MagicMock

    from pytest_mock import MockerFixture


@pytest.fixture(scope="session")
async def db_engine() -> AsyncGenerator[AsyncEngine]:
    """Yield an asynchronous test database engine."""
    base_db_url = make_url(str(settings.DATABASE_URL))
    test_db_url = base_db_url.set(database=f"{settings.POSTGRES_DB}_test")

    engine = create_async_engine(test_db_url, poolclass=NullPool)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture(scope="session", autouse=True)
async def setup_db(db_engine: AsyncEngine) -> None:
    """Initialize the test database schema.

    Args:
        db_engine: Database engine fixture.
    """
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture
async def db_session(db_engine: AsyncEngine) -> AsyncGenerator[AsyncSession]:
    """Yield an async test database session with automatic rollback.

    Provides a session bound to a transaction savepoint, preventing any
    test data from persisting in the underlying database.

    Args:
        db_engine: Database engine fixture.
    """
    async with db_engine.connect() as conn:
        transaction = await conn.begin()
        session_maker = async_sessionmaker(
            bind=conn,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )

        async with session_maker() as session:
            yield session

        await transaction.rollback()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient]:
    """Yield an asynchronous HTTP test client.

    Overrides the app's get_db dependency to route all endpoint requests
    through the isolated test database session.

    Args:
        db_session: Database session fixture.
    """

    async def override_get_db() -> AsyncGenerator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url=f"http://test{settings.API_V1_STR}",
        ) as c:
            yield c
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def mock_send_welcome_email(mocker: MockerFixture) -> MagicMock:
    """Mock the delay method of the Celery send_welcome_email task.

    Args:
        mocker: pytest-mock fixture providing the patching mechanism.

    Returns:
        MagicMock instance for replacing the intercepted method.
    """
    return mocker.patch(
        "app.api.v1.users.send_welcome_email.delay",
        autospec=True,
    )


@pytest.fixture
async def user(db_session: AsyncSession) -> User:
    """Create a test user in the database.

    Args:
        db_session: Database session fixture.

    Returns:
        Test User instance.
    """
    user = User(
        username=USERNAME,
        email=EMAIL,
        hashed_password=get_password_hash(TEST_PASSWORD),
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture
def auth_headers(user: User) -> dict[str, str]:
    """Return authorization headers for the test user.

    Args:
        user: Test user fixture.

    Returns:
        Dictionary containing the Bearer token header.
    """
    token = create_access_token(data={"sub": str(user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def other_user(db_session: AsyncSession) -> User:
    """Create a secondary test user in the database.

    Args:
        db_session: Database session fixture.

    Returns:
        Secondary test User instance.
    """
    other_user = User(
        username=OTHER_USERNAME,
        email=OTHER_EMAIL,
        hashed_password=get_password_hash(TEST_PASSWORD),
    )
    db_session.add(other_user)
    await db_session.flush()
    return other_user


@pytest.fixture
def other_auth_headers(other_user: User) -> dict[str, str]:
    """Return authorization headers for the secondary test user.

    Args:
        other_user: Secondary test user fixture.

    Returns:
        Dictionary containing the Bearer token header.
    """
    token = create_access_token(data={"sub": str(other_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def post(db_session: AsyncSession, user: User) -> Post:
    """Create a test post in the database.

    Args:
        db_session: Database session fixture.
        user: Test user fixture.

    Returns:
        Test Post instance.
    """
    post = Post(
        title=POST_TITLE,
        body=POST_BODY,
        owner_id=user.id,
    )
    db_session.add(post)
    await db_session.flush()
    return post
