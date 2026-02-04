"""SQLAlchemy ORM model for users."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

if TYPE_CHECKING:
    from app.models.post import Post


class User(Base):
    """Represents a user (author) of the blog.

    Attributes:
        id: Primary key.
        username: Unique public username.
        email: Unique email address of the user.
        hashed_password: Securely hashed password of the user.
        created_at: Timestamp when the user account was created.
        updated_at: Timestamp when the user account was last updated.
        posts: ORM relationship to the Post model.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    username: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    posts: Mapped[list["Post"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        """Return a debug string representation of the User object."""
        return (
            f"<User id={self.id} "
            f"username={self.username!r} "
            f"email={self.email!r}>"
        )
