"""SQLAlchemy ORM models.

This module defines the database models used by the application.
"""

from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:
    from datetime import datetime


class User(Base):
    """Represents a user in the database.

    Attributes:
        id: Primary key.
        email: Unique email address of the user.
        hashed_password: Securely hashed password.
        is_active: Indicates whether the user account is active.
        posts: Posts authored by this user.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(
        String(254),
        unique=True,
        index=True,
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    posts: Mapped[list[Post]] = relationship(back_populates="owner")

    def __repr__(self) -> str:
        """Returns a debug string representation of the User object."""
        return f"<User id={self.id} email={self.email!r}>"


class Post(Base):
    """Represents a blog post in the database.

    Attributes:
        id: Primary key.
        title: Post title.
        body: Main textual content of the post.
        created_at: Timestamp when the post was created.
        owner_id: Foreign key referencing the post's author.
        owner: The user this post belongs to.
    """

    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    owner: Mapped[User | None] = relationship(back_populates="posts")

    def __repr__(self) -> str:
        """Returns a debug string representation of the Post object."""
        return f"<Post id={self.id} title={self.title!r}>"
