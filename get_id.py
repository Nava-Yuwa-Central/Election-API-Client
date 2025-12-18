
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DATABASE_URL = "sqlite+aiosqlite:///./nepal_entity.db"

async def get_id():
    engine = create_async_engine(DATABASE_URL)
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT id, name FROM entities LIMIT 1"))
        row = result.fetchone()
        if row:
            print(f"ID: {row[0]}")
            print(f"Name: {row[1]}")
        else:
            print("No entities found")

if __name__ == "__main__":
    asyncio.run(get_id())
