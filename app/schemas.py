"""Pydantic schemas for API input/output.

This module defines the schemas used for validating and serializing data
exchanged with the API.
"""

from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    """Request data for creating a new user."""

    email: EmailStr
    password: str


class UserOut(BaseModel):
    """Response data for a user profile.

    Excludes sensitive information like hashed passwords. Configured for
    compatibility with ORM models.
    """

    id: int
    email: EmailStr
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """Authentication token payload."""

    access_token: str
    token_type: str


class PostCreate(BaseModel):
    """Request data for creating a new post."""

    title: str
    body: str


class PostOut(BaseModel):
    """Response data for a post.

    Configured for compatibility with ORM models.
    """

    id: int
    title: str
    body: str
    owner_id: int | None = None

    model_config = ConfigDict(from_attributes=True)
