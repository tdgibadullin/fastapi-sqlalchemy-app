"""SQLAlchemy ORM model for posts."""

from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

if TYPE_CHECKING:
    from datetime import datetime

    from app.models.user import User


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
    title: Mapped[str] = mapped_column(String(255), index=True)
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        ondelete="CASCADE",
    )
    owner: Mapped["User"] = relationship(back_populates="posts")

    def __repr__(self) -> str:
        """Returns a debug string representation of the Post object."""
        return f"<Post id={self.id} title={self.title!r}>"
