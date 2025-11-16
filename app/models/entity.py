from sqlalchemy import Column, String, DateTime, Text, Enum, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.core.database import Base
import uuid
import enum

class EntityType(str, enum.Enum):
    PERSON = "person"
    ORGANIZATION = "organization"
    GOVERNMENT = "government"
    POLITICAL_PARTY = "political_party"
    OTHER = "other"

class Entity(Base):
    __tablename__ = "entities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    name_nepali = Column(String(255), nullable=True, index=True)
    entity_type = Column(Enum(EntityType), nullable=False, index=True)
    description = Column(Text, nullable=True)
    metadata = Column(JSONB, nullable=True, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    version = Column(String(50), default="1.0")

    __table_args__ = (
        Index('ix_entities_name_type', 'name', 'entity_type'),
        Index('ix_entities_metadata', 'metadata', postgresql_using='gin'),
    )

    def __repr__(self):
        return f"<Entity(id={self.id}, name={self.name}, type={self.entity_type})>"
