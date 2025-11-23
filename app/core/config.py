"""Configuration settings for the Nepal Entity Service."""

from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache
import secrets


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8195
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)  # Generate if not provided
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Authentication
    REQUIRE_AUTHENTICATION: bool = False  # Set to True to enforce auth
    
    # CORS - Restrictive by default
    CORS_ORIGINS: List[str] = []  # Empty = no CORS allowed
    
    # Add trusted origins via environment variable
    # Example: CORS_ORIGINS=["https://yourapp.com","https://www.yourapp.com"]
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins with development fallback.
        
        Returns:
            List of allowed origins
        """
        if self.ENVIRONMENT == "development" and not self.CORS_ORIGINS:
            return ["http://localhost:3000", "http://localhost:8000"]
        return self.CORS_ORIGINS if self.CORS_ORIGINS else []
    
    # Redis (future use)
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_EXPIRY: int = 3600
    
    # API
    API_VERSION: str = "2.0.0"
    API_TITLE: str = "Nepal Entity Service API"
    API_DESCRIPTION: str = "🇳🇵 Open Source API for managing Nepali public entities"

    class Config:
        """Pydantic config class."""

        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance.

    Returns:
        Settings instance
    """
    return Settings()


settings = get_settings()


