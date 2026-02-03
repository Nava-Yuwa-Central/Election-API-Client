@echo off
cls
echo.
echo ========================================
echo   Nepal Entity Service - PRO SERVER
echo ========================================
echo.
echo Starting FastAPI production-grade server...
echo Backend: backend/main.py
echo Gateway: http://localhost:8197
echo.

uvicorn backend.main:app --host 0.0.0.0 --port 8197 --reload

echo.
echo Server stopped.
pause
