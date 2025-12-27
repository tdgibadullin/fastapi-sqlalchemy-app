"""Pydantic schemas for API input/output.

This module provides the schemas used for validating and serializing
data exchanged with the API.
"""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """Schema for user creation input.

    Prohibits providing extra data.
    """

    model_config = ConfigDict(extra="forbid")

    email: Annotated[
        EmailStr,
        Field(
            max_length=254,
            examples=["user@example.com"],
        ),
    ]
    password: Annotated[
        str,
        Field(
            min_length=12,
            max_length=128,
            examples=["StrongPass123!"],
        ),
    ]


class UserUpdate(BaseModel):
    """Schema for user update input.

    All fields are optional. Prohibits providing extra data.
    """

    model_config = ConfigDict(extra="forbid")

    email: Annotated[
        EmailStr | None,
        Field(
            default=None,
            max_length=254,
            examples=["new@example.com"],
        ),
    ]
    password: Annotated[
        str | None,
        Field(
            default=None,
            min_length=12,
            max_length=128,
            examples=["NewStrongPass123!"],
        ),
    ]


class UserOut(BaseModel):
    """Schema for user data returned in API responses.

    Supports retrieving data from ORM objects via attribute access.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    is_active: bool


class PostCreate(BaseModel):
    """Schema for post creation input.

    Prohibits providing extra data.
    """

    model_config = ConfigDict(extra="forbid")

    title: Annotated[
        str,
        Field(
            min_length=2,
            max_length=255,
            examples=["My Post"],
        ),
    ]
    body: Annotated[
        str,
        Field(
            min_length=1,
            max_length=100000,
            examples=["This is the content of my post..."],
        ),
    ]


class PostUpdate(BaseModel):
    """Schema for post update input.

    All fields are optional. Prohibits providing extra data.
    """

    model_config = ConfigDict(extra="forbid")

    title: Annotated[
        str | None,
        Field(
            default=None,
            min_length=2,
            max_length=255,
            examples=["My Updated Post"],
        ),
    ]
    body: Annotated[
        str | None,
        Field(
            default=None,
            min_length=1,
            max_length=100000,
            examples=["This is the updated content of my post..."],
        ),
    ]


class PostOut(BaseModel):
    """Schema for post data returned in API responses.

    Supports retrieving data from ORM objects via attribute access.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    body: str
    owner_id: int


class Token(BaseModel):
    """Schema for auth token data returned in API responses."""

    access_token: str
    token_type: str
