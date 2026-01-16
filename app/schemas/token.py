"""Access token-related Pydantic schemas."""

from typing import Annotated

from pydantic import BaseModel, Field


class Token(BaseModel):
    """Schema for access token data returned in API responses."""

    access_token: Annotated[
        str,
        Field(description="JWT access token string."),
    ]
    token_type: Annotated[
        str,
        Field(description="Type of the token issued."),
    ]


class TokenPayload(BaseModel):
    """Access token payload schema used for authentication."""

    sub: Annotated[
        str | None,
        Field(
            default=None,
            description="Subject claim of the token (user identifier).",
        ),
    ]
