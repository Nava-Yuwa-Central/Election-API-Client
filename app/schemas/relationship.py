"""Pydantic schemas for Relationship endpoints."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class RelationshipBase(BaseModel):
    """Base schema for Relationship with common fields."""

    source_entity_id: UUID = Field(
        ..., description="ID of the source entity", examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    target_entity_id: UUID = Field(
        ..., description="ID of the target entity", examples=["123e4567-e89b-12d3-a456-426614174001"]
    )
    relationship_type: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Type of relationship",
        examples=["member_of", "works_for", "partner_with"],
    )
    description: Optional[str] = Field(
        None, description="Detailed description of the relationship"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional metadata in JSON format"
    )


class RelationshipCreate(RelationshipBase):
    """Schema for creating a new relationship."""

    class Config:
        json_schema_extra = {
            "example": {
                "source_entity_id": "123e4567-e89b-12d3-a456-426614174000",
                "target_entity_id": "123e4567-e89b-12d3-a456-426614174001",
                "relationship_type": "member_of",
                "description": "Member since 2020",
                "metadata": {"role": "President", "start_date": "2020-01-01"},
            }
        }


class RelationshipUpdate(BaseModel):
    """Schema for updating an existing relationship (all fields optional)."""

    relationship_type: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "description": "Updated relationship description",
                "metadata": {"end_date": "2025-01-01"},
            }
        }


class RelationshipResponse(RelationshipBase):
    """Schema for relationship responses with all fields."""

    id: UUID = Field(..., description="Unique relationship identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174002",
                "source_entity_id": "123e4567-e89b-12d3-a456-426614174000",
                "target_entity_id": "123e4567-e89b-12d3-a456-426614174001",
                "relationship_type": "member_of",
                "description": "Member since 2020",
                "metadata": {"role": "President"},
                "created_at": "2025-11-23T05:00:00Z",
                "updated_at": "2025-11-23T06:00:00Z",
            }
        }

