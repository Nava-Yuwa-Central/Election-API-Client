#!/bin/bash

# Start FastAPI and Next.js together for development

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Starting Election API Client Development Environment${NC}"
echo ""

# Check if postgres is running
if ! docker-compose ps | grep -q "nes-postgres.*Up"; then
    echo "Starting PostgreSQL..."
    docker-compose up -d postgres
    sleep 3
fi

# Start FastAPI in background
echo -e "${GREEN}Starting FastAPI backend on http://localhost:8195${NC}"
cd "$(dirname "$0")"
source election-api/bin/activate 2>/dev/null || true
uvicorn app.main:app --reload --port 8195 &
FASTAPI_PID=$!

# Wait a bit for FastAPI to start
sleep 2

# Start Next.js
echo -e "${GREEN}Starting Next.js frontend on http://localhost:3000${NC}"
cd web_ui
npm run dev &
NEXTJS_PID=$!

echo ""
echo -e "${GREEN}Both services are starting...${NC}"
echo "FastAPI: http://localhost:8195"
echo "Next.js: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both services"

# Wait for user interrupt
trap "kill $FASTAPI_PID $NEXTJS_PID 2>/dev/null; exit" INT TERM
wait