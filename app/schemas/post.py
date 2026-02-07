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
            description="Title of the post.",
            examples=["My Post"],
        ),
    ]
    body: Annotated[
        str,
        Field(
            min_length=1,
            max_length=100000,
            description="Main textual content of the post.",
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
            min_length=2,
            max_length=255,
            description="Updated title of the post.",
            examples=["My Updated Post"],
        ),
    ] = None
    body: Annotated[
        str | None,
        Field(
            min_length=1,
            max_length=100000,
            description="Updated textual content of the post.",
            examples=["This is the updated content of my post..."],
        ),
    ] = None


class PostOut(BaseModel):
    """Schema for post data returned in API responses.

    Supports retrieving data from ORM objects via attribute access.
    """

    model_config = ConfigDict(from_attributes=True)

    id: Annotated[
        int,
        Field(description="Unique identifier for the post."),
    ]
    title: Annotated[
        str,
        Field(description="Title of the post."),
    ]
    body: Annotated[
        str,
        Field(description="Main textual content of the post."),
    ]
    created_at: Annotated[
        datetime,
        Field(description="Timestamp when the post was created."),
    ]
    updated_at: Annotated[
        datetime,
        Field(description="Timestamp when the post was last updated."),
    ]
    owner_id: Annotated[
        int,
        Field(description="ID of the user who authored the post."),
    ]
