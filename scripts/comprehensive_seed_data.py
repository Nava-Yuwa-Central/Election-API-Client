"""
Comprehensive data seeding script for Nepal Entity Service
Imports all parliament members and political parties from parliament_data.json
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import get_db, engine, Base
from app.models.entity import Entity, EntityType
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

async def load_parliament_data() -> Dict[str, Any]:
    """Load parliament data from JSON file"""
    data_file = Path(__file__).parent.parent / "parliament_data.json"
    
    if not data_file.exists():
        raise FileNotFoundError(f"Parliament data file not found: {data_file}")
    
    with open(data_file, 'r', encoding='utf-8') as f:
        return json.load(f)

async def create_political_parties(db: AsyncSession, parliament_data: Dict[str, Any]) -> Dict[int, str]:
    """Create political party entities and return mapping of party_id to entity_id"""
    print("📋 Creating political parties...")
    
    parties_map = {}
    unique_parties = {}
    
    # Extract unique parties from parliament data
    for member in parliament_data['data']['data']:
        if member.get('political_party'):
            party = member['political_party']
            party_id = party['id']
            
            if party_id not in unique_parties:
                unique_parties[party_id] = party
    
    print(f"Found {len(unique_parties)} unique political parties")
    
    for party_id, party_data in unique_parties.items():
        # Check if party already exists
        result = await db.execute(
            select(Entity).where(
                Entity.name == party_data['party_name_en'],
                Entity.entity_type == EntityType.POLITICAL_PARTY
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            parties_map[party_id] = str(existing.id)
            print(f"⏭️  Party exists: {party_data['party_name_en']}")
            continue
        
        # Create new party entity
        party_entity = Entity(
            name=party_data['party_name_en'],
            name_nepali=party_data['party_name_np'],
            entity_type=EntityType.POLITICAL_PARTY,
            description=f"Political party in Nepal Parliament",
            metadata={
                "party_id": party_id,
                "sequence": party_data.get('sequence', 0),
                "status": party_data.get('status', 1),
                "parliament_type": party_data.get('parliament_type', 'hr'),
                "created_at": party_data.get('created_at'),
                "updated_at": party_data.get('updated_at')
            }
        )
        
        db.add(party_entity)
        await db.flush()  # Get the ID
        parties_map[party_id] = str(party_entity.id)
        
        print(f"✅ Created party: {party_data['party_name_en']}")
    
    await db.commit()
    return parties_map

async def create_parliament_members(db: AsyncSession, parliament_data: Dict[str, Any], parties_map: Dict[int, str]):
    """Create parliament member entities"""
    print("\n👥 Creating parliament members...")
    
    members_created = 0
    members_skipped = 0
    
    for member in parliament_data['data']['data']:
        # Check if member already exists
        result = await db.execute(
            select(Entity).where(
                Entity.name == member['name'],
                Entity.entity_type == EntityType.PERSON
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            members_skipped += 1
            continue
        
        # Get image URL if available
        image_url = ""
        if member.get('images') and member['images'].get('images'):
            image_name = member['images']['images'].get('original', '')
            if image_name:
                image_url = f"https://hr.parliament.gov.np/uploads/images/{image_name}"
        
        # Get Nepali name from translations
        nepali_name = ""
        if member.get('parliament_member_translations'):
            for translation in member['parliament_member_translations']:
                if translation['locale'] == 'np':
                    nepali_name = translation['name']
                    break
        
        # Get party information
        party_name = ""
        party_id = None
        if member.get('political_party'):
            party_name = member['political_party']['party_name_en']
            party_id = member['political_party']['id']
        
        # Create member entity
        member_entity = Entity(
            name=member['name'],
            name_nepali=nepali_name,
            entity_type=EntityType.PERSON,
            description=member.get('description', ''),
            metadata={
                "member_id": member['id'],
                "code": member.get('code'),
                "slug": member.get('slug'),
                "parliament_type": member.get('parliament_type'),
                "sequence": member.get('sequence'),
                "member_type": member.get('member_type'),
                "dob": member.get('dob'),
                "gender": member.get('gender'),  # 0 = male, 1 = female
                "district": member.get('district', {}).get('name_en', ''),
                "district_nepali": member.get('district', {}).get('name_np', ''),
                "political_party": party_name,
                "political_party_id": party_id,
                "political_party_nepali": member.get('political_party', {}).get('party_name_np', ''),
                "election_type": member.get('election_type', {}).get('election_type_en', ''),
                "election_area_no": member.get('election_area_no'),
                "territory_no": member.get('territory_no'),
                "image_url": image_url,
                "tenure_end_date": member.get('tenure_end_date'),
                "registered_date": member.get('registered_date'),
                "created_at": member.get('created_at'),
                "updated_at": member.get('updated_at')
            }
        )
        
        db.add(member_entity)
        members_created += 1
        
        if members_created % 10 == 0:
            print(f"  Created {members_created} members...")
    
    await db.commit()
    print(f"✅ Created {members_created} parliament members")
    print(f"⏭️  Skipped {members_skipped} existing members")

async def seed_comprehensive_data():
    """Main seeding function"""
    print("=" * 60)
    print("🇳🇵 Nepal Entity Service - Comprehensive Data Seeding")
    print("=" * 60)
    
    try:
        # Load parliament data
        print("📂 Loading parliament data...")
        parliament_data = await load_parliament_data()
        total_members = parliament_data['data']['total']
        print(f"Found {total_members} total parliament members")
        
        # Create database tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables ready")
        
        # Get database session
        async for db in get_db():
            try:
                # Create political parties first
                parties_map = await create_political_parties(db, parliament_data)
                
                # Create parliament members
                await create_parliament_members(db, parliament_data, parties_map)
                
                print("\n🎉 Data seeding completed successfully!")
                print(f"📊 Summary:")
                print(f"   - Political Parties: {len(parties_map)}")
                print(f"   - Parliament Members: {len(parliament_data['data']['data'])}")
                
            except Exception as e:
                print(f"❌ Error during seeding: {e}")
                await db.rollback()
                raise
            finally:
                break  # Only need one iteration
                
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(seed_comprehensive_data())
    
    print("\n✨ Seeding complete! You can now:")
    print("   🚀 Start the server: uvicorn app.main:app --reload --port 8195")
    print("   🌐 View frontend: http://localhost:8195")
    print("   📚 API docs: http://localhost:8195/docs")