#!/bin/bash
# Start OrcheNet Backend Only

set -e

cd backend

if [ ! -d "venv" ]; then
    echo "ERROR: Virtual environment not found!"
    echo "Please run ./start.sh first to set up the environment."
    exit 1
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Starting backend server..."
echo ""
echo "Backend will be available at:"
echo "  API: http://localhost:8000"
echo "  Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
