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
            examples=["Author_2026"],
        ),
    ]
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

    username: Annotated[
        str | None,
        Field(
            default=None,
            min_length=3,
            max_length=20,
            pattern=r"^[a-zA-Z0-9_-]+$",
            examples=["New_Author_2026"],
        ),
    ]
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
    username: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime
    is_active: bool
