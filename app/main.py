"""Nepal Entity Service FastAPI Application."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from slowapi.errors import RateLimitExceeded
import logging
from pathlib import Path

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

# Mount static files (frontend)
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/frontend", StaticFiles(directory=str(frontend_path)), name="frontend")
    logger.info(f"Mounted frontend static files from {frontend_path}")
else:
    logger.warning(f"Frontend directory not found at {frontend_path}")


@app.get(
    "/",
    response_class=HTMLResponse,
    summary="Root endpoint - Serve frontend",
    description="Serve the Who's My Neta Nepal frontend",
    tags=["General"],
)
async def root():
    """Serve the frontend index.html.

    Returns:
        HTML content of the frontend
    """
    index_path = Path(__file__).parent.parent / "frontend" / "index.html"
    
    if index_path.exists():
        return FileResponse(index_path)
    else:
        # Fallback to API information
        from fastapi.responses import JSONResponse
        return JSONResponse({
            "message": "Who's My Neta Nepal - API",
            "version": settings.API_VERSION,
            "frontend": "Not found",
            "docs": "/docs",
            "health": "/health",
            "environment": settings.ENVIRONMENT,
        })


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

