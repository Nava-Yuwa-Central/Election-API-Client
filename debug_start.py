import os
import sys
import traceback

# Set env vars for testing
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
os.environ["SECRET_KEY"] = "test"

try:
    print("Attempting to import app.main...")
    from app.main import app
    print("Import successful!")
except Exception:
    print("Import failed!")
    traceback.print_exc()
