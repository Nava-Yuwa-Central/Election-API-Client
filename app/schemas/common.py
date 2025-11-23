"""Common Pydantic schemas for the Nepal Entity Service."""

from pydantic import BaseModel, Field
from typing import Generic, TypeVar, List, Optional


T = TypeVar("T")


class PaginationMetadata(BaseModel):
    """Metadata for paginated responses."""

    total: int = Field(..., description="Total number of items")
    skip: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Number of items per page")
    has_more: bool = Field(..., description="Whether there are more items")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response schema."""

    items: List[T] = Field(..., description="List of items")
    metadata: PaginationMetadata = Field(..., description="Pagination metadata")


class ErrorResponse(BaseModel):
    """Standard error response schema."""

    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Entity not found",
                "error_code": "ENTITY_NOT_FOUND"
            }
        }


class HealthCheckResponse(BaseModel):
    """Health check response schema."""

    status: str = Field(..., description="Service status")
    database: str = Field(..., description="Database status")
    version: str = Field(..., description="API version")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "database": "connected",
                "version": "2.0.0"
            }
        }


class MessageResponse(BaseModel):
    """Generic message response schema."""

    message: str = Field(..., description="Response message")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Operation completed successfully"
            }
        }
