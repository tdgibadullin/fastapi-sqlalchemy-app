"""CRUD operations and related authentication logic for users."""

from typing import TYPE_CHECKING

from sqlalchemy import select

from app.core.security import get_password_hash, verify_password
from app.models.user import User

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.schemas.user import UserCreate, UserUpdate

# Dummy hash for constant-time password verification (timing attack
# mitigation). Used when a user is not found.
DUMMY_HASH = (
    "$argon2id$v=19$m=65536,t=3,p=4$"
    "tJOhkAaIcVzIr6u3ZDVX/Q$"
    "YoPdIuG/i1MwXH6YK/8fBuZMxPoCwhqHRAU+Svz71bo"
)


async def create_user(
    *,
    session: AsyncSession,
    user_in: UserCreate,
) -> User:
    """Create a new user.

    Hashes the password before storing.

    Args:
        session: Database session.
        user_in: User creation data.

    Returns:
        Newly created User instance.
    """
    user = User(
        **user_in.model_dump(exclude={"password"}),
        hashed_password=get_password_hash(user_in.password),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def get_user(
    *,
    session: AsyncSession,
    user_id: int,
) -> User | None:
    """Retrieve a user by their ID.

    Args:
        session: Database session.
        user_id: User's ID.

    Returns:
        User instance if found, otherwise None.
    """
    return await session.get(User, user_id)


async def get_user_by_email(
    *,
    session: AsyncSession,
    email: str,
) -> User | None:
    """Retrieve a user by their email address.

    Args:
        session: Database session.
        email: User's email address.

    Returns:
        User instance if found, otherwise None.
    """
    result = await session.scalars(select(User).where(User.email == email))
    return result.one_or_none()


async def authenticate_user(
    *,
    session: AsyncSession,
    email: str,
    password: str,
) -> User | None:
    """Authenticate a user and update the stored hash if necessary.

    Performs constant-time password verification to mitigate timing
    attacks. Updates the hash if the password is valid and the current
    hasher/the hash itself is outdated.

    Args:
        session: Database session.
        email: User's email address.
        password: User's plain-text password.

    Returns:
        Authenticated User instance if credentials are valid, otherwise
        None.
    """
    user = await get_user_by_email(session=session, email=email)

    if user is None:
        verify_password(password, DUMMY_HASH)
        return None

    is_valid, new_hash = verify_password(
        password,
        user.hashed_password,
    )

    if not is_valid:
        return None

    if new_hash:
        user.hashed_password = new_hash
        await session.commit()
        await session.refresh(user)

    return user


async def update_user(
    *,
    session: AsyncSession,
    user: User,
    user_in: UserUpdate,
) -> User:
    """Update a user.

    Only fields explicitly provided in the input schema are updated. If
    a password is included, it is hashed before being stored.

    Args:
        session: Database session.
        user: User instance to update.
        user_in: User update data.

    Returns:
        Updated User instance.
    """
    update_data = user_in.model_dump(exclude_unset=True)

    if "password" in update_data:
        user.hashed_password = get_password_hash(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(user, field, value)

    await session.commit()
    await session.refresh(user)
    return user


async def delete_user(
    *,
    session: AsyncSession,
    user: User,
) -> None:
    """Delete a user.

    Performs a hard delete. All related entities configured with
    cascading deletes will be removed as well.

    Args:
        session: Database session.
        user: User instance to delete.
    """
    await session.delete(user)
    await session.commit()
