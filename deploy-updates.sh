#!/bin/bash
# Quick deployment script for OrcheNet updates
# Run this on the server after pushing changes to git

set -e

echo "===== OrcheNet Update Deployment ====="
echo ""

# Pull latest changes
echo "Pulling latest changes from git..."
git pull

# Rebuild frontend
echo "Building frontend..."
cd frontend
npm run build
cd ..

# Restart backend service
echo "Restarting backend service..."
sudo systemctl restart orchenet-backend

# Wait a moment for service to start
sleep 3

# Check service status
echo ""
echo "Service status:"
sudo systemctl status orchenet-backend --no-pager | grep Active

echo ""
echo "===== Update Complete ====="
echo "Check logs with: journalctl -u orchenet-backend -f"
