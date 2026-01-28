@echo off
echo 🇳🇵 Starting Nepal Entity Service...
echo.

call venv\Scripts\activate.bat

echo 🚀 Server starting at http://localhost:8195
echo 📚 API Documentation: http://localhost:8195/docs
echo 👥 Leaders Page: http://localhost:8195/leaders.html
echo 🏛️ Parties Page: http://localhost:8195/parties.html
echo.
echo Press Ctrl+C to stop the server
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8195