"""Nepal Entity Service FastAPI Application."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.core.database import engine, Base, check_database_health
from app.core.logging import setup_logging
from app.api.v1.router import api_router
from app.schemas.common import HealthCheckResponse

# Setup logging
setup_logging(settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events.

    Args:
        app: FastAPI application instance

    Yields:
        Control during application lifetime
    """
    # Startup
    logger.info("Starting Nepal Entity Service API")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")
    yield
    # Shutdown
    logger.info("Shutting down Nepal Entity Service API")


app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "NewNepal Contributors",
        "url": "https://github.com/revil2025o/new1",
    },
    license_info={
        "name": "Hippocratic License 3.0",
        "url": "https://firstdonoharm.dev/version/3/0/license.html",
    },
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1", tags=["v1"])


@app.get(
    "/",
    summary="Root endpoint",
    description="Get basic API information",
    tags=["General"],
)
async def root():
    """Root endpoint with API information.

    Returns:
        Basic API information
    """
    return {
        "message": "Nepal Entity Service API",
        "version": settings.API_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


@app.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Health check",
    description="Check API and database health status",
    tags=["General"],
)
async def health_check() -> HealthCheckResponse:
    """Health check endpoint.

    Returns:
        Health status of API and database
    """
    db_healthy = await check_database_health()

    return HealthCheckResponse(
        status="healthy" if db_healthy else "unhealthy",
        database="connected" if db_healthy else "disconnected",
        version=settings.API_VERSION,
    )

