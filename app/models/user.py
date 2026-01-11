"""SQLAlchemy ORM model for users."""

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

if TYPE_CHECKING:
    from app.models.post import Post


class User(Base):
    """Represents a user (author) of the blog.

    Attributes:
        id: Primary key.
        email: Unique email address of the user.
        hashed_password: Securely hashed password.
        is_active: Indicates whether the user account is active.
        posts: Posts authored by this user.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)
    posts: Mapped[list["Post"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        """Return a debug string representation of the User object."""
        return f"<User id={self.id} email={self.email!r}>"
