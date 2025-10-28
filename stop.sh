#!/bin/bash
# OrcheNet Stop Script (Linux/Mac)
# Stops backend and frontend services

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Stopping OrcheNet services...${NC}"
echo ""

# Stop backend
if [ -f ".backend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo "Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        echo -e "${GREEN}✓ Backend stopped${NC}"
    else
        echo "Backend process not running"
    fi
    rm .backend.pid
else
    echo "No backend PID file found"
fi

# Stop frontend
if [ -f ".frontend.pid" ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo "Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        echo -e "${GREEN}✓ Frontend stopped${NC}"
    else
        echo "Frontend process not running"
    fi
    rm .frontend.pid
else
    echo "No frontend PID file found"
fi

echo ""
echo -e "${GREEN}✓ OrcheNet services stopped${NC}"
