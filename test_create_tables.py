import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.database import Base
from app.models.entity import Entity

async def test_create_tables():
    try:
        engine = create_async_engine("sqlite+aiosqlite:///./test.db", echo=True)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Tables created successfully")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_create_tables())
