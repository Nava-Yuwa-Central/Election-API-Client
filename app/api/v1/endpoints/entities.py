from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.models.entity import Entity, EntityType
from app.schemas.entity import EntityCreate, EntityUpdate, EntityResponse

router = APIRouter()

@router.post("/", response_model=EntityResponse, status_code=201)
async def create_entity(
    entity: EntityCreate,
    db: AsyncSession = Depends(get_db)
):
    db_entity = Entity(**entity.model_dump())
    db.add(db_entity)
    await db.commit()
    await db.refresh(db_entity)
    return db_entity

@router.get("/", response_model=List[EntityResponse])
async def list_entities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    entity_type: Optional[EntityType] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Entity)

    if entity_type:
        query = query.where(Entity.entity_type == entity_type)

    if search:
        query = query.where(
            or_(
                Entity.name.ilike(f"%{search}%"),
                Entity.name_nepali.ilike(f"%{search}%")
            )
        )

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    entities = result.scalars().all()
    return entities

@router.get("/{entity_id}", response_model=EntityResponse)
async def get_entity(
    entity_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Entity).where(Entity.id == entity_id))
    entity = result.scalar_one_or_none()

    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    return entity

@router.put("/{entity_id}", response_model=EntityResponse)
async def update_entity(
    entity_id: UUID,
    entity_update: EntityUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Entity).where(Entity.id == entity_id))
    entity = result.scalar_one_or_none()

    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    update_data = entity_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(entity, field, value)

    await db.commit()
    await db.refresh(entity)
    return entity

@router.delete("/{entity_id}", status_code=204)
async def delete_entity(
    entity_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Entity).where(Entity.id == entity_id))
    entity = result.scalar_one_or_none()

    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    await db.delete(entity)
    await db.commit()
    return None
