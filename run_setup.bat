@echo off
echo Starting Nepal Entity Service Setup...
echo.

echo Step 1: Starting Docker services...
docker compose up -d

echo.
echo Step 2: Waiting for services to be ready...
timeout /t 10

echo.
echo Step 3: Running comprehensive data seeding...
python scripts/comprehensive_seed_data.py

echo.
echo Setup complete! 
echo.
echo Access your application at:
echo - Main App: http://localhost:8195
echo - API Docs: http://localhost:8195/docs
echo - Health Check: http://localhost:8195/health
echo.
pause