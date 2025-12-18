
import asyncio
import aiosqlite

async def fix_db():
    async with aiosqlite.connect("nepal_entity.db") as db:
        await db.execute("UPDATE entities SET entity_type = 'person' WHERE entity_type = 'PERSON'")
        await db.commit()
    print("Updated entity_type to lowercase person")

if __name__ == "__main__":
    asyncio.run(fix_db())
