"""API v1 package."""

from fastapi import APIRouter

from app.api.v1.endpoints import jobs, cv, discord, health

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(cv.router, prefix="/cv", tags=["cv"])
api_router.include_router(discord.router, prefix="/discord", tags=["discord"])
api_router.include_router(health.router, prefix="/health", tags=["health"])