"""Script to import entities from external API into local database."""

import asyncio
import httpx
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.config import settings
from app.models.entity import Entity, EntityType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EXTERNAL_API_BASE = "https://nes.newnepal.org/api"


def extract_name(external_data: Dict[str, Any], lang: str = "en") -> Optional[str]:
    """Extract name from external API entity structure.
    
    Args:
        external_data: Entity data from external API
        lang: Language code ('en' for English, 'ne' for Nepali)
        
    Returns:
        Name string or None
    """
    names = external_data.get("names", [])
    if not names:
        return None
    
    # Get first name entry
    name_entry = names[0] if isinstance(names, list) else names
    
    # Extract language-specific name
    lang_data = name_entry.get(lang, {})
    if isinstance(lang_data, dict):
        return lang_data.get("full") or lang_data.get("short") or lang_data.get("first")
    return None

def map_external_to_entity(external_data: Dict[str, Any]) -> Dict[str, Any]:
    """Map external API data to our Entity model.
    
    Args:
        external_data: Data from external API
        
    Returns:
        Dictionary with entity fields
    """
    # Extract English name
    name = extract_name(external_data, "en")
    if not name:
        # Fallback to any available name
        name = external_data.get("name") or external_data.get("id", "").split("/")[-1]
    
    # Extract Nepali name
    name_nepali = extract_name(external_data, "ne")
    
    # Extract entity type - handle None values properly
    entity_type_raw = external_data.get("entity_type") or external_data.get("type")
    entity_type_str = (entity_type_raw or "").lower() if entity_type_raw else ""
    
    sub_type_raw = external_data.get("sub_type")
    sub_type = (sub_type_raw or "").lower() if sub_type_raw else ""
    
    # Map entity type
    if entity_type_str == "organization" and sub_type == "political_party":
        entity_type = EntityType.POLITICAL_PARTY
    elif entity_type_str == "organization":
        entity_type = EntityType.ORGANIZATION
    elif entity_type_str == "person":
        entity_type = EntityType.PERSON
    elif entity_type_str == "government":
        entity_type = EntityType.GOVERNMENT
    else:
        entity_type = EntityType.OTHER
    
    # Extract description/bio
    description = (
        external_data.get("description") 
        or external_data.get("bio") 
        or external_data.get("summary")
    )
    
    # Build metadata with all additional fields
    meta_data = {
        "external_id": external_data.get("id"),
        "source": "nes.newnepal.org",
        "entity_type_original": entity_type_str if entity_type_str else None,
        "sub_type": sub_type if sub_type else None,
    }
    
    # Add all other fields that aren't already mapped
    excluded_fields = {
        "id", "name", "names", "entity_type", "type", "sub_type", 
        "description", "bio", "summary"
    }
    for key, value in external_data.items():
        if key not in excluded_fields and value is not None:
            meta_data[key] = value
    
    entity_data = {
        "name": name,
        "name_nepali": name_nepali,
        "description": description,
        "entity_type": entity_type,
        "meta_data": meta_data,
    }
    
    return entity_data


async def fetch_entities_from_api(
    query: Optional[str] = None, 
    entity_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """Fetch entities from external API.
    
    Args:
        query: Optional search query (e.g., entity name)
        entity_type: Optional entity type filter (person, organization, location)
        limit: Maximum number of entities to fetch
        offset: Offset for pagination
        
    Returns:
        List of entity data dictionaries
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        url = f"{EXTERNAL_API_BASE}/entities"
        params = {
            "limit": limit,
            "offset": offset,
        }
        
        if query:
            params["query"] = query
        
        if entity_type:
            params["entity_type"] = entity_type
            
        try:
            response = await client.get(
                url, 
                params=params, 
                headers={"accept": "application/json"}
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Handle API response format: {"entities": [...], "total": ..., "limit": ..., "offset": ...}
            if isinstance(data, dict) and "entities" in data:
                entities = data["entities"]
                total = data.get("total", len(entities))
                logger.info(f"Fetched {len(entities)} entities (total available: {total})")
                return entities
            elif isinstance(data, list):
                return data
            else:
                logger.warning(f"Unexpected response format: {data}")
                return []
                
        except httpx.HTTPError as e:
            logger.error(f"Error fetching from API: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
            return []


async def fetch_all_entities(
    query: Optional[str] = None,
    entity_type: Optional[str] = None,
    max_entities: int = 1000
) -> List[Dict[str, Any]]:
    """Fetch all entities with pagination.
    
    Args:
        query: Optional search query
        entity_type: Optional entity type filter
        max_entities: Maximum total entities to fetch
        
    Returns:
        List of all entity data dictionaries
    """
    all_entities = []
    limit = 100
    offset = 0
    
    while len(all_entities) < max_entities:
        entities = await fetch_entities_from_api(
            query=query,
            entity_type=entity_type,
            limit=limit,
            offset=offset
        )
        
        if not entities:
            break
        
        all_entities.extend(entities)
        
        if len(entities) < limit:
            # Last page
            break
        
        offset += limit
        
        # Small delay to respect rate limits
        await asyncio.sleep(0.1)
    
    return all_entities[:max_entities]


async def entity_exists(session: AsyncSession, name: str) -> bool:
    """Check if entity with given name already exists.
    
    Args:
        session: Database session
        name: Entity name to check
        
    Returns:
        True if entity exists, False otherwise
    """
    result = await session.execute(
        select(Entity).where(Entity.name == name)
    )
    return result.scalar_one_or_none() is not None


async def import_entity(
    session: AsyncSession, 
    entity_data: Dict[str, Any], 
    skip_existing: bool = True
) -> Optional[Entity]:
    """Import a single entity into the database.
    
    Args:
        session: Database session
        entity_data: Entity data dictionary
        skip_existing: If True, skip entities that already exist
        
    Returns:
        Created Entity object or None if skipped
    """
    try:
        # Check if entity already exists
        if skip_existing and await entity_exists(session, entity_data["name"]):
            logger.info(f"Skipping existing entity: {entity_data['name']}")
            return None
        
        # Create entity
        db_entity = Entity(**entity_data)
        session.add(db_entity)
        await session.commit()
        await session.refresh(db_entity)
        
        logger.info(f"Imported entity: {db_entity.name} (ID: {db_entity.id})")
        return db_entity
        
    except Exception as e:
        logger.error(f"Error importing entity {entity_data.get('name', 'unknown')}: {e}")
        await session.rollback()
        return None


async def import_entities(
    query: Optional[str] = None,
    entity_type: Optional[str] = None,
    limit: int = 100,
    skip_existing: bool = True,
    fetch_all: bool = False
):
    """Main import function.
    
    Args:
        query: Optional search query (e.g., "Pushpa Kamal Dahal")
        entity_type: Optional entity type filter (person, organization, location)
        limit: Maximum number of entities to import (if fetch_all=False)
        skip_existing: If True, skip entities that already exist
        fetch_all: If True, fetch all entities with pagination
    """
    logger.info(f"Starting import from {EXTERNAL_API_BASE}")
    logger.info(f"Query: {query or 'All entities'}")
    logger.info(f"Entity type: {entity_type or 'All types'}")
    logger.info(f"Limit: {limit if not fetch_all else 'All (with pagination)'}")
    
    # Fetch entities from external API
    if fetch_all:
        external_entities = await fetch_all_entities(
            query=query,
            entity_type=entity_type,
            max_entities=limit if limit > 0 else 10000
        )
    else:
        external_entities = await fetch_entities_from_api(
            query=query,
            entity_type=entity_type,
            limit=limit
        )
    
    if not external_entities:
        logger.warning("No entities found in external API")
        return
    
    logger.info(f"Fetched {len(external_entities)} entities from external API")
    
    # Import entities into database
    async with AsyncSessionLocal() as session:
        imported_count = 0
        skipped_count = 0
        error_count = 0
        
        for external_entity in external_entities:
            try:
                entity_data = map_external_to_entity(external_entity)
                
                if not entity_data.get("name"):
                    logger.warning(f"Skipping entity without name: {external_entity.get('id', 'unknown')}")
                    skipped_count += 1
                    continue
                
                result = await import_entity(session, entity_data, skip_existing=skip_existing)
                
                if result:
                    imported_count += 1
                else:
                    skipped_count += 1
                    
            except Exception as e:
                logger.error(f"Error processing entity: {e}")
                error_count += 1
        
        logger.info(f"Import complete: {imported_count} imported, {skipped_count} skipped, {error_count} errors")


async def main():
    """Main entry point."""
    import sys
    
    # Parse command line arguments
    query = None
    entity_type = None
    limit = 100
    fetch_all = False
    
    args = sys.argv[1:]
    
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--query" or arg == "-q":
            query = args[i + 1] if i + 1 < len(args) else None
            i += 2
        elif arg == "--type" or arg == "-t":
            entity_type = args[i + 1] if i + 1 < len(args) else None
            i += 2
        elif arg == "--limit" or arg == "-l":
            limit = int(args[i + 1]) if i + 1 < len(args) else 100
            i += 2
        elif arg == "--all" or arg == "-a":
            fetch_all = True
            i += 1
        else:
            # Backward compatibility: first arg is query
            if query is None:
                query = arg
            i += 1
    
    await import_entities(
        query=query,
        entity_type=entity_type,
        limit=limit,
        fetch_all=fetch_all
    )


if __name__ == "__main__":
    asyncio.run(main())