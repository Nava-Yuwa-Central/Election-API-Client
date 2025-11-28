import os
import asyncio
import traceback

# Set env vars
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
os.environ["SECRET_KEY"] = "test"

async def test_lifespan():
    try:
        print("Importing app...")
        from app.main import app
        from app.core.database import engine, Base
        
        print("Running lifespan startup...")
        # Simulate what lifespan does
        async with engine.begin() as conn:
            print("Creating tables...")
            await conn.run_sync(Base.metadata.create_all)
        print("Tables created successfully!")
        
    except Exception:
        print("Lifespan failed!")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_lifespan())
