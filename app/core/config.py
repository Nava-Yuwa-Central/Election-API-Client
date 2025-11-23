"""Configuration settings for the Nepal Entity Service."""

from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache


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
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
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

