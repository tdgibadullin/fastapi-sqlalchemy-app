"""Main application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.main import api_router
from app.core.config import settings
from app.core.logger import setup_logging

setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=(
        None
        if settings.ENVIRONMENT == "production"
        else f"{settings.API_V1_STR}/openapi.json"
    ),
)

if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(health_router)
app.include_router(api_router, prefix=settings.API_V1_STR)
