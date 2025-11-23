"""Relationship API endpoints for CRUD operations."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID
import logging

from app.core.database import get_db
from app.core.exceptions import (
    EntityNotFoundError,
    RelationshipNotFoundError,
    DatabaseError,
)
from app.models.relationship import Relationship
from app.models.entity import Entity
from app.schemas.relationship import (
    RelationshipCreate,
    RelationshipUpdate,
    RelationshipResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/",
    response_model=RelationshipResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new relationship",
    description="Create a relationship between two entities.",
    response_description="The created relationship",
)
async def create_relationship(
    relationship: RelationshipCreate, db: AsyncSession = Depends(get_db)
) -> Relationship:
    """Create a new relationship between entities.

    Args:
        relationship: Relationship data
        db: Database session

    Returns:
        Created relationship

    Raises:
        EntityNotFoundError: If source or target entity not found
        DatabaseError: If database operation fails
    """
    try:
        # Verify source entity exists
        source_result = await db.execute(
            select(Entity).where(Entity.id == relationship.source_entity_id)
        )
        if not source_result.scalar_one_or_none():
            logger.warning(
                f"Source entity not found: {relationship.source_entity_id}"
            )
            raise EntityNotFoundError(str(relationship.source_entity_id))

        # Verify target entity exists
        target_result = await db.execute(
            select(Entity).where(Entity.id == relationship.target_entity_id)
        )
        if not target_result.scalar_one_or_none():
            logger.warning(
                f"Target entity not found: {relationship.target_entity_id}"
            )
            raise EntityNotFoundError(str(relationship.target_entity_id))

        db_relationship = Relationship(**relationship.model_dump())
        db.add(db_relationship)
        await db.commit()
        await db.refresh(db_relationship)
        logger.info(f"Created relationship: {db_relationship.id}")
        return db_relationship
    except EntityNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error creating relationship: {str(e)}")
        await db.rollback()
        raise DatabaseError(f"Failed to create relationship: {str(e)}")


@router.get(
    "/",
    response_model=List[RelationshipResponse],
    summary="List relationships",
    description="Retrieve a list of relationships with optional filtering.",
    response_description="List of relationships",
)
async def list_relationships(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items"),
    entity_id: Optional[UUID] = Query(
        None, description="Filter by entity ID (source or target)"
    ),
    relationship_type: Optional[str] = Query(
        None, description="Filter by relationship type"
    ),
    db: AsyncSession = Depends(get_db),
) -> List[Relationship]:
    """List relationships with filtering and pagination.

    Args:
        skip: Number of items to skip
        limit: Maximum number of items to return
        entity_id: Filter by entity (source or target)
        relationship_type: Filter by relationship type
        db: Database session

    Returns:
        List of relationships

    Raises:
        DatabaseError: If database operation fails
    """
    try:
        query = select(Relationship).order_by(Relationship.created_at.desc())

        if entity_id:
            query = query.where(
                (Relationship.source_entity_id == entity_id)
                | (Relationship.target_entity_id == entity_id)
            )

        if relationship_type:
            query = query.where(Relationship.relationship_type == relationship_type)

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        relationships = result.scalars().all()
        
        logger.info(f"Retrieved {len(relationships)} relationships")
        return relationships
    except Exception as e:
        logger.error(f"Error listing relationships: {str(e)}")
        raise DatabaseError(f"Failed to list relationships: {str(e)}")


@router.get(
    "/{relationship_id}",
    response_model=RelationshipResponse,
    summary="Get a relationship",
    description="Retrieve a specific relationship by its ID.",
    response_description="The requested relationship",
)
async def get_relationship(
    relationship_id: UUID, db: AsyncSession = Depends(get_db)
) -> Relationship:
    """Get a specific relationship by ID.

    Args:
        relationship_id: UUID of the relationship
        db: Database session

    Returns:
        Relationship object

    Raises:
        RelationshipNotFoundError: If relationship not found
        DatabaseError: If database operation fails
    """
    try:
        result = await db.execute(
            select(Relationship).where(Relationship.id == relationship_id)
        )
        relationship = result.scalar_one_or_none()

        if not relationship:
            logger.warning(f"Relationship not found: {relationship_id}")
            raise RelationshipNotFoundError(str(relationship_id))

        logger.info(f"Retrieved relationship: {relationship_id}")
        return relationship
    except RelationshipNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error getting relationship: {str(e)}")
        raise DatabaseError(f"Failed to get relationship: {str(e)}")


@router.put(
    "/{relationship_id}",
    response_model=RelationshipResponse,
    summary="Update a relationship",
    description="Update an existing relationship's information.",
    response_description="The updated relationship",
)
async def update_relationship(
    relationship_id: UUID,
    relationship_update: RelationshipUpdate,
    db: AsyncSession = Depends(get_db),
) -> Relationship:
    """Update an existing relationship.

    Args:
        relationship_id: UUID of the relationship
        relationship_update: Updated relationship data
        db: Database session

    Returns:
        Updated relationship

    Raises:
        RelationshipNotFoundError: If relationship not found
        DatabaseError: If database operation fails
    """
    try:
        result = await db.execute(
            select(Relationship).where(Relationship.id == relationship_id)
        )
        relationship = result.scalar_one_or_none()

        if not relationship:
            logger.warning(f"Relationship not found for update: {relationship_id}")
            raise RelationshipNotFoundError(str(relationship_id))

        update_data = relationship_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(relationship, field, value)

        await db.commit()
        await db.refresh(relationship)
        logger.info(f"Updated relationship: {relationship_id}")
        return relationship
    except RelationshipNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error updating relationship: {str(e)}")
        await db.rollback()
        raise DatabaseError(f"Failed to update relationship: {str(e)}")


@router.delete(
    "/{relationship_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a relationship",
    description="Delete a specific relationship.",
)
async def delete_relationship(
    relationship_id: UUID, db: AsyncSession = Depends(get_db)
) -> None:
    """Delete a relationship.

    Args:
        relationship_id: UUID of the relationship
        db: Database session

    Raises:
        RelationshipNotFoundError: If relationship not found
        DatabaseError: If database operation fails
    """
    try:
        result = await db.execute(
            select(Relationship).where(Relationship.id == relationship_id)
        )
        relationship = result.scalar_one_or_none()

        if not relationship:
            logger.warning(f"Relationship not found for deletion: {relationship_id}")
            raise RelationshipNotFoundError(str(relationship_id))

        await db.delete(relationship)
        await db.commit()
        logger.info(f"Deleted relationship: {relationship_id}")
    except RelationshipNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error deleting relationship: {str(e)}")
        await db.rollback()
        raise DatabaseError(f"Failed to delete relationship: {str(e)}")

