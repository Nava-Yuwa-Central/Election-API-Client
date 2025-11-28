import uvicorn
import os

if __name__ == "__main__":
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
    os.environ["SECRET_KEY"] = "test"
    uvicorn.run("app.main:app", host="0.0.0.0", port=8195, log_level="info")
