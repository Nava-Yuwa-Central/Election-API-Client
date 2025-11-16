from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.models.relationship import Relationship
from app.models.entity import Entity
from app.schemas.relationship import RelationshipCreate, RelationshipUpdate, RelationshipResponse

router = APIRouter()

@router.post("/", response_model=RelationshipResponse, status_code=201)
async def create_relationship(
    relationship: RelationshipCreate,
    db: AsyncSession = Depends(get_db)
):
    source_result = await db.execute(select(Entity).where(Entity.id == relationship.source_entity_id))
    if not source_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Source entity not found")

    target_result = await db.execute(select(Entity).where(Entity.id == relationship.target_entity_id))
    if not target_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Target entity not found")

    db_relationship = Relationship(**relationship.model_dump())
    db.add(db_relationship)
    await db.commit()
    await db.refresh(db_relationship)
    return db_relationship

@router.get("/", response_model=List[RelationshipResponse])
async def list_relationships(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    entity_id: Optional[UUID] = None,
    relationship_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Relationship)

    if entity_id:
        query = query.where(
            (Relationship.source_entity_id == entity_id) |
            (Relationship.target_entity_id == entity_id)
        )

    if relationship_type:
        query = query.where(Relationship.relationship_type == relationship_type)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    relationships = result.scalars().all()
    return relationships

@router.get("/{relationship_id}", response_model=RelationshipResponse)
async def get_relationship(
    relationship_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Relationship).where(Relationship.id == relationship_id))
    relationship = result.scalar_one_or_none()

    if not relationship:
        raise HTTPException(status_code=404, detail="Relationship not found")

    return relationship

@router.put("/{relationship_id}", response_model=RelationshipResponse)
async def update_relationship(
    relationship_id: UUID,
    relationship_update: RelationshipUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Relationship).where(Relationship.id == relationship_id))
    relationship = result.scalar_one_or_none()

    if not relationship:
        raise HTTPException(status_code=404, detail="Relationship not found")

    update_data = relationship_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(relationship, field, value)

    await db.commit()
    await db.refresh(relationship)
    return relationship

@router.delete("/{relationship_id}", status_code=204)
async def delete_relationship(
    relationship_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Relationship).where(Relationship.id == relationship_id))
    relationship = result.scalar_one_or_none()

    if not relationship:
        raise HTTPException(status_code=404, detail="Relationship not found")

    await db.delete(relationship)
    await db.commit()
    return None
