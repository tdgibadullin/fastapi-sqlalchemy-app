"""Main application entry point."""

from fastapi import FastAPI

from app.api.main import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=(
        None
        if settings.ENVIRONMENT == "production"
        else f"{settings.API_V1_STR}/openapi.json"
    ),
)

app.include_router(api_router, prefix=settings.API_V1_STR)
