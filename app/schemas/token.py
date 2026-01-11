"""Access token-related Pydantic schemas."""

from pydantic import BaseModel


class Token(BaseModel):
    """Schema for access token data returned in API responses."""

    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """Access token payload schema used for authentication."""

    sub: str | None = None
