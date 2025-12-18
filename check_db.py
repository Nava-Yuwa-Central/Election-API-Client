
import asyncio
import aiosqlite

async def check_db():
    async with aiosqlite.connect("nepal_entity.db") as db:
        async with db.execute("SELECT count(*) FROM entities") as cursor:
            count = await cursor.fetchone()
            print(f"Total entities: {count[0]}")
            
        async with db.execute("SELECT name, entity_type, metadata FROM entities") as cursor:
            rows = await cursor.fetchall()
            import json
            for i, row in enumerate(rows):
                try:
                    meta = row[2]
                    if meta:
                        json.loads(meta)
                except Exception as e:
                    print(f"Row {i} Name: {row[0]} FAILED metadata parse: {e}")
            print(f"Checked {len(rows)} rows.")

if __name__ == "__main__":
    asyncio.run(check_db())
