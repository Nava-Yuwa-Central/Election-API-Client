import sqlite3
import json

try:
    conn = sqlite3.connect('nepal_entity.db')
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables:", tables)
    
    # Check entities
    if ('entities',) in tables:
        cursor.execute("SELECT id, name, metadata FROM entities LIMIT 5")
        rows = cursor.fetchall()
        print("\nFirst 5 entities:")
        for row in rows:
            print(f"ID: {row[0]}, Name: {row[1]}")
            # print(f"Meta: {row[2]}")
            
        cursor.execute("SELECT count(*) FROM entities")
        count = cursor.fetchone()[0]
        print(f"\nTotal entities: {count}")

        # Check for specific ID from logs if possible, but let's just see format first.
        # ID: d077cf36-9f6b-4336-b46e-5c8ba481cfe6
        target_id = 'd077cf36-9f6b-4336-b46e-5c8ba481cfe6'
        # UUIDs are usually stored as strings in SQLite or BLOBs.
        cursor.execute("SELECT * FROM entities WHERE id = ?", (target_id,))
        match = cursor.fetchone()
        print(f"\nSearch for {target_id}: {'Found' if match else 'Not Found'}")

    conn.close()

except Exception as e:
    print(f"Error: {e}")
