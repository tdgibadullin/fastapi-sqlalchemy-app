"""Main API router combining all v1 endpoints."""

from fastapi import APIRouter

from app.api.v1 import login, posts, users

api_router = APIRouter()

api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(posts.router)
