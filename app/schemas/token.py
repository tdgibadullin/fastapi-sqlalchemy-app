"""Authentication token-related Pydantic schemas."""

from pydantic import BaseModel


class Token(BaseModel):
    """Schema for auth token data returned in API responses."""

    access_token: str
    token_type: str
