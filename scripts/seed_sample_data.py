"""
Sample data seeding script for Who's My Neta Nepal
Creates sample leader entities in the database for testing
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import get_db, engine, Base
from app.models.entity import Entity, EntityType
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

# Sample leader data
SAMPLE_LEADERS = [
    {
        "name": "Pushpa Kamal Dahal",
        "name_nepali": "पुष्पकमल दाहाल",
        "entity_type": EntityType.PERSON,
        "description": "Chairperson of Communist Party of Nepal (Maoist Centre)",
        "metadata": {
            "party": "CPN (Maoist Centre)",
            "position": "Member of Parliament",
            "province": "Bagmati",
            "constituency": "Gorkha-2",
            "attendance": 78,
            "questions_asked": 45,
            "photo_url": ""
        }
    },
    {
        "name": "Sher Bahadur Deuba",
        "name_nepali": "शेरबहादुर देउबा",
        "entity_type": EntityType.PERSON,
        "description": "President of Nepali Congress",
        "metadata": {
            "party": "Nepali Congress",
            "position": "Member of Parliament",
            "province": "Sudurpashchim",
            "constituency": "Dadeldhura-1",
            "attendance": 85,
            "questions_asked": 52,
            "photo_url": ""
        }
    },
    {
        "name": "KP Sharma Oli",
        "name_nepali": "केपी शर्मा ओली",
        "entity_type": EntityType.PERSON,
        "description": "Chairman of CPN-UML",
        "metadata": {
            "party": "CPN-UML",
            "position": "Member of Parliament",
            "province": "Koshi",
            "constituency": "Jhapa-5",
            "attendance": 82,
            "questions_asked": 38,
            "photo_url": ""
        }
    },
    {
        "name": "Bimal Prasad Gautam",
        "name_nepali": "विमल प्रसाद गौतम",
        "entity_type": EntityType.PERSON,
        "description": "Member of Parliament",
        "metadata": {
            "party": "Janata Samajwadi Party",
            "position": "Member of Parliament",
            "province": "Madhesh",
            "constituency": "Bara-4",
            "attendance": 72,
            "questions_asked": 28,
            "photo_url": ""
        }
    },
    {
        "name": "Renu Kumari Yadav",
        "name_nepali": "रेणु कुमारी यादव",
        "entity_type": EntityType.PERSON,
        "description": "Member of Parliament",
        "metadata": {
            "party": "Nepali Congress",
            "position": "Member of Parliament",
            "province": "Madhesh",
            "constituency": "Siraha-3",
            "attendance": 88,
            "questions_asked": 42,
            "photo_url": ""
        }
    },
    {
        "name": "Gagan Kumar Thapa",
        "name_nepali": "गगन कुमार थापा",
        "entity_type": EntityType.PERSON,
        "description": "General Secretary of Nepali Congress",
        "metadata": {
            "party": "Nepali Congress",
            "position": "Member of Parliament",
            "province": "Bagmati",
            "constituency": "Kathmandu-4",
            "attendance": 90,
            "questions_asked": 65,
            "photo_url": ""
        }
    },
    {
        "name": "Rekha Sharma",
        "name_nepali": "रेखा शर्मा",
        "entity_type": EntityType.PERSON,
        "description": "Member of Parliament",
        "metadata": {
            "party": "CPN-UML",
            "position": "Member of Parliament",
            "province": "Gandaki",
            "constituency": "Kaski-2",
            "attendance": 76,
            "questions_asked": 33,
            "photo_url": ""
        }
    },
    {
        "name": "Krishna Prasad Sitaula",
        "name_nepali": "कृष्णप्रसाद सिटौला",
        "entity_type": EntityType.PERSON,
        "description": "Senior Leader of Nepali Congress",
        "metadata": {
            "party": "Nepali Congress",
            "position": "Member of Parliament",
            "province": "Koshi",
            "constituency": "Jhapa-1",
            "attendance": 81,
            "questions_asked": 48,
            "photo_url": ""
        }
    },
    {
        "name": "Yogesh Bhattarai",
        "name_nepali": "योगेश भट्टराई",
        "entity_type": EntityType.PERSON,
        "description": "Member of Parliament",
        "metadata": {
            "party": "CPN-UML",
            "position": "Member of Parliament",
            "province": "Lumbini",
            "constituency": "Rupandehi-3",
            "attendance": 79,
            "questions_asked": 37,
            "photo_url": ""
        }
    },
    {
        "name": "Jhakku Prasad Subedi",
        "name_nepali": "झक्कु प्रसाद सुवेदी",
        "entity_type": EntityType.PERSON,
        "description": "Member of Parliament",
        "metadata": {
            "party": "CPN (Maoist Centre)",
            "position": "Member of Parliament",
            "province": "Karnali",
            "constituency": "Surkhet-1",
            "attendance": 74,
            "questions_asked": 31,
            "photo_url": ""
        }
    },
]

async def seed_data():
    """Seed sample leader data into database"""
    print("🌱 Starting data seeding...")
    
    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables ready")
    
    # Get database session
    async for db in get_db():
        try:
            print(f"\n📝 Creating {len(SAMPLE_LEADERS)} sample leaders...")
            
            for leader_data in SAMPLE_LEADERS:
                # Check if leader already exists
                from sqlalchemy import select
                from app.models.entity import Entity
                
                result = await db.execute(
                    select(Entity).where(Entity.name == leader_data["name"])
                )
                existing = result.scalar_one_or_none()
                
                if existing:
                    print(f"⏭️  Skipping {leader_data['name']} (already exists)")
                    continue
                
                # Create new leader
                entity_dict = leader_data.copy()
                entity_dict['meta_data'] = entity_dict.pop('metadata')
                
                leader = Entity(**entity_dict)
                db.add(leader)
                print(f"✅ Created: {leader_data['name']} - {leader_data['metadata']['province']}")
            
            await db.commit()
            print(f"\n🎉 Successfully seeded {len(SAMPLE_LEADERS)} leaders!")
            print("🇳🇵 Who's My Neta Nepal database is ready!")
            
        except Exception as e:
            print(f"❌ Error seeding data: {e}")
            await db.rollback()
            raise
        finally:
            break  # Only need one iteration of get_db generator

if __name__ == "__main__":
    print("=" * 50)
    print("Who's My Neta Nepal - Data Seeding Script")
    print("=" * 50)
    
    asyncio.run(seed_data())
    
    print("\n✨ Done! You can now run the application:")
    print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8195")
    print("\n📍 Access the frontend at: http://localhost:8195")
