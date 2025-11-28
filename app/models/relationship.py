"""Relationship model for connections between entities."""

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Index, JSON, Uuid
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Relationship(Base):
    """Model for relationships between entities.

    Stores connections and relationships between different entities,
    such as membership, employment, partnerships, etc.

    Attributes:
        id: Unique identifier (UUID)
        source_entity_id: ID of the source entity
        target_entity_id: ID of the target entity
        relationship_type: Type of relationship (e.g., 'member_of', 'works_for')
        description: Detailed description of the relationship
        metadata: Flexible JSONB field for additional data
        created_at: Timestamp when relationship was created
        updated_at: Timestamp when relationship was last updated
    """

    __tablename__ = "relationships"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    source_entity_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_entity_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    relationship_type = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    # Use 'meta_data' as Python attribute name, but map to 'metadata' column in DB
    meta_data = Column("metadata", JSON, nullable=True, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Composite indexes for better query performance
    __table_args__ = (
        Index("ix_relationships_source_target", "source_entity_id", "target_entity_id"),
        # Index("ix_relationships_metadata", meta_data, postgresql_using="gin"),  # GIN index not supported in SQLite
        Index("ix_relationships_type_created", "relationship_type", created_at.desc()),
    )

    def __repr__(self) -> str:
        """String representation of Relationship.

        Returns:
            String representation
        """
        return f"<Relationship(id={self.id}, type={self.relationship_type})>"