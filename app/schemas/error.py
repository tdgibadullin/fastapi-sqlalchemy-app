"""Pydantic schemas for API error responses."""

from typing import Annotated

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Schema for error data returned in API responses."""

    detail: Annotated[
        str,
        Field(description="Error message detailing what went wrong."),
    ]
