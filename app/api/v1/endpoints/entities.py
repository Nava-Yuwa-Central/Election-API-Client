"""Entity API endpoints for CRUD operations."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from typing import List, Optional
from uuid import UUID
import logging

from app.core.database import get_db
from app.core.exceptions import EntityNotFoundError, DatabaseError
from app.models.entity import Entity, EntityType
from app.schemas.entity import EntityCreate, EntityUpdate, EntityResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/",
    response_model=EntityResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new entity",
    description="Create a new Nepali public entity with the provided information.",
    response_description="The created entity",
)
async def create_entity(
    entity: EntityCreate, db: AsyncSession = Depends(get_db)
) -> Entity:
    """Create a new entity.

    Args:
        entity: Entity data
        db: Database session

    Returns:
        Created entity

    Raises:
        DatabaseError: If database operation fails
    """
    try:
        entity_data = entity.model_dump()
        # Map 'metadata' from schema to 'meta_data' in model
        if 'metadata' in entity_data:
            entity_data['meta_data'] = entity_data.pop('metadata')
        db_entity = Entity(**entity_data)
        db.add(db_entity)
        await db.commit()
        await db.refresh(db_entity)
        logger.info(f"Created entity: {db_entity.id}")
        return db_entity
    except Exception as e:
        logger.error(f"Error creating entity: {str(e)}")
        await db.rollback()
        raise DatabaseError(f"Failed to create entity: {str(e)}")


@router.get(
    "/",
    response_model=List[EntityResponse],
    summary="List entities",
    description="Retrieve a list of entities with optional filtering and pagination.",
    response_description="List of entities",
)
async def list_entities(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
    entity_type: Optional[EntityType] = Query(
        None, description="Filter by entity type"
    ),
    search: Optional[str] = Query(
        None, description="Search in name or name_nepali fields"
    ),
    db: AsyncSession = Depends(get_db),
) -> List[Entity]:
    """List all entities with filtering and pagination.

    Args:
        skip: Number of items to skip (offset)
        limit: Maximum number of items to return
        entity_type: Filter by entity type
        search: Search query for name fields
        db: Database session

    Returns:
        List of entities

    Raises:
        DatabaseError: If database operation fails
    """
    try:
        query = select(Entity).order_by(Entity.created_at.desc())

        if entity_type:
            query = query.where(Entity.entity_type == entity_type)

        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    Entity.name.ilike(search_pattern),
                    Entity.name_nepali.ilike(search_pattern),
                )
            )

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        entities = result.scalars().all()
        
        logger.info(f"Retrieved {len(entities)} entities")
        return entities
    except Exception as e:
        logger.error(f"Error listing entities: {str(e)}")
        raise DatabaseError(f"Failed to list entities: {str(e)}")


@router.get(
    "/{entity_id}",
    response_model=EntityResponse,
    summary="Get an entity",
    description="Retrieve a specific entity by its ID.",
    response_description="The requested entity",
)
async def get_entity(
    entity_id: UUID, db: AsyncSession = Depends(get_db)
) -> Entity:
    """Get a specific entity by ID.

    Args:
        entity_id: UUID of the entity
        db: Database session

    Returns:
        Entity object

    Raises:
        EntityNotFoundError: If entity is not found
        DatabaseError: If database operation fails
    """
    try:
        result = await db.execute(select(Entity).where(Entity.id == entity_id))
        entity = result.scalar_one_or_none()

        if not entity:
            logger.warning(f"Entity not found: {entity_id}")
            raise EntityNotFoundError(str(entity_id))

        logger.info(f"Retrieved entity: {entity_id}")
        return entity
    except EntityNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error getting entity: {str(e)}")
        raise DatabaseError(f"Failed to get entity: {str(e)}")


@router.put(
    "/{entity_id}",
    response_model=EntityResponse,
    summary="Update an entity",
    description="Update an existing entity's information.",
    response_description="The updated entity",
)
async def update_entity(
    entity_id: UUID,
    entity_update: EntityUpdate,
    db: AsyncSession = Depends(get_db),
) -> Entity:
    """Update an existing entity.

    Args:
        entity_id: UUID of the entity to update
        entity_update: Updated entity data
        db: Database session

    Returns:
        Updated entity

    Raises:
        EntityNotFoundError: If entity is not found
        DatabaseError: If database operation fails
    """
    try:
        result = await db.execute(select(Entity).where(Entity.id == entity_id))
        entity = result.scalar_one_or_none()

        if not entity:
            logger.warning(f"Entity not found for update: {entity_id}")
            raise EntityNotFoundError(str(entity_id))

        update_data = entity_update.model_dump(exclude_unset=True)
        # Map 'metadata' from schema to 'meta_data' in model
        if 'metadata' in update_data:
            update_data['meta_data'] = update_data.pop('metadata')
        for field, value in update_data.items():
            setattr(entity, field, value)

        await db.commit()
        await db.refresh(entity)
        logger.info(f"Updated entity: {entity_id}")
        return entity
    except EntityNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error updating entity: {str(e)}")
        await db.rollback()
        raise DatabaseError(f"Failed to update entity: {str(e)}")


@router.delete(
    "/{entity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an entity",
    description="Delete an entity and all its relationships (cascade delete).",
)
async def delete_entity(
    entity_id: UUID, db: AsyncSession = Depends(get_db)
) -> None:
    """Delete an entity.

    Args:
        entity_id: UUID of the entity to delete
        db: Database session

    Raises:
        EntityNotFoundError: If entity is not found
        DatabaseError: If database operation fails
    """
    try:
        result = await db.execute(select(Entity).where(Entity.id == entity_id))
        entity = result.scalar_one_or_none()

        if not entity:
            logger.warning(f"Entity not found for deletion: {entity_id}")
            raise EntityNotFoundError(str(entity_id))

        await db.delete(entity)
        await db.commit()
        logger.info(f"Deleted entity: {entity_id}")
    except EntityNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error deleting entity: {str(e)}")
        await db.rollback()
        raise DatabaseError(f"Failed to delete entity: {str(e)}")