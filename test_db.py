import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def test_db():
    try:
        engine = create_async_engine("sqlite+aiosqlite:///./test.db", echo=True)
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print(result.scalar())
        print("Success")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_db())
