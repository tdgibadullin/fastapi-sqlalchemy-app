"""User-related Pydantic schemas."""

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """Schema for user creation input.

    Prohibits providing extra data.
    """

    model_config = ConfigDict(extra="forbid")

    username: Annotated[
        str,
        Field(
            min_length=3,
            max_length=20,
            pattern=r"^[a-zA-Z0-9_-]+$",
            description="Unique public username.",
            examples=["Author_2026"],
        ),
    ]
    email: Annotated[
        EmailStr,
        Field(
            max_length=254,
            description="Valid, unique email address of the user.",
            examples=["user@example.com"],
        ),
    ]
    password: Annotated[
        str,
        Field(
            min_length=12,
            max_length=128,
            description="Plain-text password of the user.",
            examples=["StrongPass123!"],
        ),
    ]


class UserUpdate(BaseModel):
    """Schema for user update input.

    All fields are optional. Prohibits providing extra data.
    """

    model_config = ConfigDict(extra="forbid")

    username: Annotated[
        str | None,
        Field(
            min_length=3,
            max_length=20,
            pattern=r"^[a-zA-Z0-9_-]+$",
            description="Updated public username. Must be unique.",
            examples=["New_Author_2026"],
        ),
    ] = None
    email: Annotated[
        EmailStr | None,
        Field(
            max_length=254,
            description="Updated valid email address of the user. Must be "
            "unique.",
            examples=["new@example.com"],
        ),
    ] = None
    password: Annotated[
        str | None,
        Field(
            min_length=12,
            max_length=128,
            description="Updated plain-text password of the user.",
            examples=["NewStrongPass123!"],
        ),
    ] = None


class UserOut(BaseModel):
    """Schema for user data returned in API responses.

    Supports retrieving data from ORM objects via attribute access.
    """

    model_config = ConfigDict(from_attributes=True)

    id: Annotated[
        int,
        Field(description="Unique identifier for the user."),
    ]
    username: Annotated[
        str,
        Field(description="Public username."),
    ]
    email: Annotated[
        EmailStr,
        Field(description="User's email address."),
    ]
    created_at: Annotated[
        datetime,
        Field(description="Timestamp when the user account was created."),
    ]
    updated_at: Annotated[
        datetime,
        Field(description="Timestamp when the user account was last updated."),
    ]
