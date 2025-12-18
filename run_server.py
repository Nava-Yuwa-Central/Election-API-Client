import uvicorn
import os

if __name__ == "__main__":
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./nepal_entity.db"
    os.environ["CORS_ORIGINS"] = '["http://localhost:3000", "http://localhost:8000", "http://localhost:8195"]'
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./nepal_entity.db"
    os.environ["SECRET_KEY"] = "test"
    uvicorn.run("app.main:app", host="0.0.0.0", port=8195, log_level="info")
