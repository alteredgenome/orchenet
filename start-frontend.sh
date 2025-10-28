#!/bin/bash
# Start OrcheNet Frontend Only

set -e

cd frontend

if [ ! -d "node_modules" ]; then
    echo "ERROR: Node modules not found!"
    echo "Please run ./start.sh first to set up the environment."
    exit 1
fi

echo ""
echo "Starting frontend server..."
echo ""
echo "Frontend will be available at:"
echo "  URL: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

npm run dev
