"""Nepal Entity Service FastAPI Application."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi.errors import RateLimitExceeded
import logging

from app.core.config import settings
from app.core.database import engine, Base, check_database_health
from app.core.logging import setup_logging
from app.core.security import (
    limiter,
    SecurityHeadersMiddleware,
    RequestLoggingMiddleware,
    rate_limit_exceeded_handler,
)
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
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Authentication required: {settings.REQUIRE_AUTHENTICATION}")
    
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

# Production security middleware
if settings.ENVIRONMENT == "production":
    # Force HTTPS
    app.add_middleware(HTTPSRedirectMiddleware)
    
    # Trusted hosts only
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configure with actual domains in production
    )
    
    logger.info("Production security middleware enabled")

# Security headers middleware (all environments)
app.add_middleware(SecurityHeadersMiddleware)

# Request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# CORS middleware with proper configuration
cors_origins = settings.cors_origins_list

logger.info(f"CORS allowed origins: {cors_origins if cors_origins else 'NONE (CORS disabled)'}")

if cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["Authorization", "Content-Type", "Accept"],
        max_age=3600,  # Cache preflight for 1 hour
    )
else:
    logger.warning("CORS is disabled - no origins allowed")

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

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
        "environment": settings.ENVIRONMENT,
        "authentication_required": settings.REQUIRE_AUTHENTICATION,
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

