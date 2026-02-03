@echo off
cls
echo.
echo ========================================
echo 🇳🇵 Nepal Entity Service - React Version
echo ========================================
echo.
echo This will start both:
echo 1. Python API Server (port 8197)
echo 2. React Dev Server (port 3000)
echo.
echo Installing dependencies...
call npm install
echo.
echo Starting servers...
echo.
echo API Server: http://localhost:8197
echo React App: http://localhost:3000
echo.
call npm start