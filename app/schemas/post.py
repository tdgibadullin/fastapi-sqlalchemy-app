"""Post-related Pydantic schemas."""

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


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
    created_at: datetime
    owner_id: int
