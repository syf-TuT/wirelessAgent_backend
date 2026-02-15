"""
API v1 Router.

Aggregates all v1 API endpoint routers into a single router
for inclusion in the main FastAPI application.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import allocations, network, intent

# Create main API router
api_router = APIRouter(prefix="/api/v1")

# Include endpoint routers
api_router.include_router(allocations.router)
api_router.include_router(network.router)
api_router.include_router(intent.router)

__all__ = ["api_router"]
