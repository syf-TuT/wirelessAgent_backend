"""
FastAPI Application Factory.

Creates and configures the FastAPI application instance.
"""
import json
from contextlib import asynccontextmanager
from typing import List, Union

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_cached_settings, get_settings


def _parse_cors_list(value: Union[str, List[str]]) -> List[str]:
    """Parse CORS configuration from string or list."""
    if isinstance(value, list):
        return value
    
    if isinstance(value, str):
        value = value.strip()
        # Try to parse as JSON array
        if value.startswith("["):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass
        # Parse as comma-separated list
        return [item.strip() for item in value.split(",") if item.strip()]
    
    return [str(value)]


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured FastAPI application instance.
    """
    settings = get_cached_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Application lifespan manager.

        Handles startup and shutdown events.
        """
        # Startup
        print(f"Starting {settings.app_name} v{settings.app_version}")
        yield
        # Shutdown
        print(f"Shutting down {settings.app_name}")

    app = FastAPI(
        title=settings.app_name,
        description=settings.app_description,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_parse_cors_list(settings.cors_origins),
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=_parse_cors_list(settings.cors_allow_methods),
        allow_headers=_parse_cors_list(settings.cors_allow_headers),
    )

    # Register API routers (will be added in F006)
    # from app.api.v1.router import api_router
    # app.include_router(api_router, prefix="/api/v1")

    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "description": settings.app_description,
        }

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy"}

    return app


# Create the application instance for ASGI servers
app = create_app()
