"""Pydantic schemas for Entity endpoints."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
import bleach

from app.models.entity import EntityType


class EntityBase(BaseModel):
    """Base schema for Entity with common fields."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Entity name in English",
        examples=["Nepal Government", "Ram Sharma"],
    )
    name_nepali: Optional[str] = Field(
        None,
        max_length=255,
        description="Entity name in Nepali (optional)",
        examples=["नेपाल सरकार", "राम शर्मा"],
    )
    entity_type: EntityType = Field(
        ..., description="Type of entity", examples=["government", "person"]
    )
    description: Optional[str] = Field(
        None, max_length=5000, description="Detailed description of the entity"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional metadata in JSON format"
    )

    @field_validator("description")
    @classmethod
    def sanitize_description(cls, v: Optional[str]) -> Optional[str]:
        """Sanitize description to prevent XSS.

        Args:
            v: Description value

        Returns:
            Sanitized description
        """
        if v:
            # Remove all HTML tags and scripts
            return bleach.clean(v, tags=[], strip=True)
        return v

    @field_validator("metadata")
    @classmethod
    def sanitize_metadata(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Sanitize metadata string values.

        Args:
            v: Metadata dictionary

        Returns:
            Sanitized metadata
        """
        if v:
            sanitized = {}
            for key, value in v.items():
                if isinstance(value, str):
                    # Sanitize string values
                    sanitized[key] = bleach.clean(value, tags=[], strip=True)
                else:
                    # Keep other types as-is
                    sanitized[key] = value
            return sanitized
        return v


class EntityCreate(EntityBase):
    """Schema for creating a new entity."""

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Nepal Government",
                "name_nepali": "नेपाल सरकार",
                "entity_type": "government",
                "description": "Federal Government of Nepal",
                "metadata": {"established": "2015", "capital": "Kathmandu"},
            }
        }


class EntityUpdate(BaseModel):
    """Schema for updating an existing entity (all fields optional)."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    name_nepali: Optional[str] = Field(None, max_length=255)
    entity_type: Optional[EntityType] = None
    description: Optional[str] = Field(None, max_length=5000)
    metadata: Optional[Dict[str, Any]] = None

    @field_validator("description")
    @classmethod
    def sanitize_description(cls, v: Optional[str]) -> Optional[str]:
        """Sanitize description to prevent XSS."""
        if v:
            return bleach.clean(v, tags=[], strip=True)
        return v

    @field_validator("metadata")
    @classmethod
    def sanitize_metadata(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Sanitize metadata string values."""
        if v:
            sanitized = {}
            for key, value in v.items():
                if isinstance(value, str):
                    sanitized[key] = bleach.clean(value, tags=[], strip=True)
                else:
                    sanitized[key] = value
            return sanitized
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "description": "Updated description",
                "metadata": {"last_updated": "2025-11-23"},
            }
        }



class EntityResponse(EntityBase):
    """Schema for entity responses with all fields."""

    id: UUID = Field(..., description="Unique entity identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    version: str = Field(..., description="Entity version")
    # Map 'meta_data' from model to 'metadata' in response
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        alias="meta_data",  # Read from model's meta_data attribute
        description="Additional metadata in JSON format"
    )

    class Config:
        from_attributes = True
        populate_by_name = True  # Allow both 'metadata' and 'meta_data' in JSON
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Nepal Government",
                "name_nepali": "नेपाल सरकार",
                "entity_type": "government",
                "description": "Federal Government of Nepal",
                "metadata": {"established": "2015"},
                "created_at": "2025-11-23T05:00:00Z",
                "updated_at": "2025-11-23T06:00:00Z",
                "version": "1.0",
            }
        }

