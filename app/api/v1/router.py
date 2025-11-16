from fastapi import APIRouter
from app.api.v1.endpoints import entities, relationships

api_router = APIRouter()
api_router.include_router(entities.router, prefix="/entities", tags=["entities"])
api_router.include_router(relationships.router, prefix="/relationships", tags=["relationships"])
