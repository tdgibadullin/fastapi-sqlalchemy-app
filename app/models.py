"""SQLAlchemy ORM models.

This module defines the database models used by the application.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Text,
    ForeignKey,
    DateTime,
    func,
)
from sqlalchemy.orm import relationship

from app.db.session import Base


class User(Base):
    """Represents a user in the database.

    Attributes:
        id (int): Primary key.
        email (str): Unique email address of the user.
        hashed_password (str): Securely hashed password.
        is_active (bool): Indicates whether the user account is active.
        posts (list[Post]): Posts authored by this user.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    posts = relationship("Post", back_populates="owner")

    def __repr__(self):
        """Returns a debug string representation of the User object."""
        return f"<User id={self.id} email={self.email!r}>"


class Post(Base):
    """Represents a blog post in the database.

    Attributes:
        id (int): Primary key.
        title (str): Post title.
        body (str): Main textual content of the post.
        created_at (datetime): Timestamp when the post was created.
        owner_id (int | None): Foreign key referencing the post's author.
        owner (User | None): The user this post belongs to.
    """

    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="posts")

    def __repr__(self):
        """Returns a debug string representation of the Post object."""
        return f"<Post id={self.id} title={self.title!r}>"
