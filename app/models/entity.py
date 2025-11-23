"""Entity model for storing Nepali public entities."""

from sqlalchemy import Column, String, DateTime, Text, Enum, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from app.core.database import Base


class EntityType(str, enum.Enum):
    """Enumeration of entity types."""

    PERSON = "person"
    ORGANIZATION = "organization"
    GOVERNMENT = "government"
    POLITICAL_PARTY = "political_party"
    OTHER = "other"


class Entity(Base):
    """Model for Nepali public entities.

    Stores information about people, organizations, government bodies,
    political parties, and other entities in Nepal.

    Attributes:
        id: Unique identifier (UUID)
        name: Entity name in English
        name_nepali: Entity name in Nepali (optional)
        entity_type: Type of entity (person, organization, etc.)
        description: Detailed description
        metadata: Flexible JSONB field for additional data
        created_at: Timestamp when entity was created
        updated_at: Timestamp when entity was last updated
        version: Version string for versioning
    """

    __tablename__ = "entities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False, index=True)
    name_nepali = Column(String(255), nullable=True, index=True)
    entity_type = Column(Enum(EntityType), nullable=False, index=True)
    description = Column(Text, nullable=True)
    # Use 'meta_data' as Python attribute name, but map to 'metadata' column in DB
    meta_data = Column("metadata", JSONB, nullable=True, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    version = Column(String(50), default="1.0")

    # Composite indexes for better query performance
    __table_args__ = (
        Index("ix_entities_name_type", "name", "entity_type"),
        Index("ix_entities_metadata", meta_data, postgresql_using="gin"),  # Use meta_data here
        Index("ix_entities_created_at_desc", created_at.desc()),
    )

    def __repr__(self) -> str:
        """String representation of Entity.

        Returns:
            String representation
        """
        return f"<Entity(id={self.id}, name={self.name}, type={self.entity_type})>"