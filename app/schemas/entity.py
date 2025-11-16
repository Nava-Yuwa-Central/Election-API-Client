from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from app.models.entity import EntityType

class EntityBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    name_nepali: Optional[str] = Field(None, max_length=255)
    entity_type: EntityType
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class EntityCreate(EntityBase):
    pass

class EntityUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    name_nepali: Optional[str] = Field(None, max_length=255)
    entity_type: Optional[EntityType] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class EntityResponse(EntityBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    version: str

    class Config:
        from_attributes = True
