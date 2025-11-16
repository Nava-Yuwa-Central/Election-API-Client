from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class RelationshipBase(BaseModel):
    source_entity_id: UUID
    target_entity_id: UUID
    relationship_type: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class RelationshipCreate(RelationshipBase):
    pass

class RelationshipUpdate(BaseModel):
    relationship_type: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class RelationshipResponse(RelationshipBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
