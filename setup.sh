#!/bin/bash
# OrcheNet Setup Script - Clean Installation

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  OrcheNet Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 is not installed${NC}"
    echo "Please install Python 3.9+ from https://python.org"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 found${NC}"

if ! command -v node &> /dev/null; then
    echo -e "${RED}ERROR: Node.js is not installed${NC}"
    echo "Please install Node.js 18+ from https://nodejs.org"
    exit 1
fi
echo -e "${GREEN}✓ Node.js found${NC}"

if ! command -v npm &> /dev/null; then
    echo -e "${RED}ERROR: npm is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ npm found${NC}"

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Setting Up Backend${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

cd backend

# Clean previous installation if exists
if [ -d "venv" ]; then
    echo "Removing old virtual environment..."
    rm -rf venv
fi

if [ -f "orchenet.db" ]; then
    echo "Removing old database..."
    rm orchenet.db
fi

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip -q

# Install dependencies
echo "Installing Python dependencies..."
echo "This may take a few minutes..."
pip install -r requirements.txt || {
    echo -e "${YELLOW}WARNING: Some packages failed to install${NC}"
    echo "The system will still work for basic functionality."
}

# Create .env file
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo -e "${YELLOW}Please edit backend/.env with your configuration${NC}"
fi

# Initialize database
echo ""
echo "Initializing database with sample data..."
python init_db.py --seed

cd ..
echo ""
echo -e "${GREEN}✓ Backend setup complete${NC}"
echo ""

# Setup Frontend
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Setting Up Frontend${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

cd frontend

# Clean previous installation if exists
if [ -d "node_modules" ]; then
    echo "Removing old node_modules..."
    rm -rf node_modules
fi

if [ -f "package-lock.json" ]; then
    rm package-lock.json
fi

# Install dependencies
echo "Installing Node.js dependencies..."
echo "This may take a few minutes..."
npm install || {
    echo -e "${YELLOW}WARNING: npm install had issues${NC}"
    echo "Trying with --legacy-peer-deps..."
    npm install --legacy-peer-deps
}

# Create .env file
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
fi

cd ..
echo ""
echo -e "${GREEN}✓ Frontend setup complete${NC}"
echo ""

# Create logs directory
mkdir -p logs

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Setup Complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "To start OrcheNet, you have two options:"
echo ""
echo "Option 1 - Individual terminals (Recommended):"
echo "  Terminal 1: ./start-backend.sh"
echo "  Terminal 2: ./start-frontend.sh"
echo ""
echo "Option 2 - All-in-one:"
echo "  ./start.sh"
echo ""
echo "The application will be available at:"
echo "  Frontend: http://localhost:5173"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
