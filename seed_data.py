
import asyncio
import aiosqlite
import logging
from uuid import uuid4
from datetime import datetime
import json
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = "./nepal_entity.db"
JSON_DATA_PATH = "./parliament_data.json"

IMAGE_BASE_URL = "https://hr.parliament.gov.np/uploads/images/members/"

async def seed_data():
    logger.info(f"Seeding database at {DB_PATH}")
    
    if not os.path.exists(JSON_DATA_PATH):
        logger.error(f"Data file {JSON_DATA_PATH} not found!")
        return

    with open(JSON_DATA_PATH, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
    
    # Extract the list of members
    # The structure is data -> data -> data -> [list]
    members = raw_data.get("data", {}).get("data", [])
    
    if not members:
        logger.warning("No members found in JSON data.")
        return

    async with aiosqlite.connect(DB_PATH) as db:
        for member in members:
            # Basic info
            name = member.get("name")
            if not name:
                continue

            # Find Nepali name
            name_nepali = ""
            description = ""
            translations = member.get("parliament_member_translations", [])
            for t in translations:
                if t.get("locale") == "np":
                    name_nepali = t.get("name", "")
                if t.get("locale") == "en":
                    # Use English description if available, or fallback
                    desc = t.get("description", "")
                    if desc:
                        description = desc

            # Metadata content
            party_data = member.get("political_party", {})
            district_data = member.get("district", {})
            image_data = member.get("images", {})
            
            # Construct photo URL
            photo_filename = ""
            if image_data and isinstance(image_data, dict):
                # Try to get 'original' from nested images
                nested_images = image_data.get("images", {})
                if nested_images and "original" in nested_images:
                    photo_filename = nested_images["original"]
                elif "imageName" in image_data:
                     # Fallback if specific structure matches
                     photo_filename = image_data["imageName"] + "." + image_data.get("clientOriginalExtension", "jpg")
            
            photo_url = f"{IMAGE_BASE_URL}{photo_filename}" if photo_filename else "assets/placeholder.jpg"
            
            # Additional metadata
            metadata = {
                "party": party_data.get("party_name_en", "Independent"),
                "province": district_data.get("name_en", "Unknown"), # Mapping district to generic location for now
                "district": district_data.get("name_en", ""),
                "education": "Unknown", # Not in API response directly
                "criminal_cases": 0, # Not in API
                "assets": 0, # Not in API
                "liabilities": 0, # Not in API
                "age": "N/A", # Calculate from dob if needed
                "photo_url": photo_url,
                "api_id": member.get("id"),
                "email": member.get("email", ""),
                "contact": member.get("mobile_no", "")
            }
            
            # Calculate Age if DOB exists
            dob = member.get("dob")
            if dob:
                try:
                    # Very rough estimate if it's YYYY-MM-DD
                    birth_year = int(dob.split("-")[0])
                    current_year = datetime.now().year
                    metadata["age"] = current_year - birth_year
                except:
                    pass

            # Check if exists (by name to avoid duplicates with manual seed, or api_id)
            cursor = await db.execute("SELECT id, metadata FROM entities WHERE name = ?", (name,))
            existing = await cursor.fetchone()
            
            if not existing:
                leader_id = str(uuid4())
                now = datetime.now()
                await db.execute(
                    """
                    INSERT INTO entities (id, name, name_nepali, entity_type, description, metadata, created_at, updated_at, version)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        leader_id,
                        name,
                        name_nepali,
                        "person",
                        description,
                        json.dumps(metadata),
                        now,
                        now,
                        "1.0"
                    )
                )
                logger.info(f"Inserted: {name}")
            else:
                 # Update existing
                 logger.info(f"Updating: {name}")
                 # Merge metadata potentially
                 current_meta = json.loads(existing[1]) if existing[1] else {}
                 current_meta.update(metadata)
                 
                 await db.execute(
                    """
                    UPDATE entities SET metadata = ?, name_nepali = ?, description = ? WHERE name = ?
                    """,
                    (json.dumps(current_meta), name_nepali, description, name)
                 )
        
        await db.commit()
    logger.info(f"Seeding complete! Processed {len(members)} members.")

if __name__ == "__main__":
    asyncio.run(seed_data())
