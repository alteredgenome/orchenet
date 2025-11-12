#!/bin/bash
###############################################################################
# Quick deployment script for updating running OrcheNet installation
# Run this after pulling new changes from git
###############################################################################

set -e

INSTALL_DIR="/opt/orchenet"

echo "=========================================="
echo "OrcheNet Update Deployment"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Error: This script must be run as root"
    exit 1
fi

echo "Step 1: Updating Python dependencies..."
cd $INSTALL_DIR
source venv/bin/activate
pip install -r backend/requirements.txt
echo "✓ Python dependencies updated"
echo ""

echo "Step 2: Rebuilding frontend..."
cd $INSTALL_DIR/frontend
sudo -u orchenet npm install
sudo -u orchenet npm run build
echo "✓ Frontend rebuilt"
echo ""

echo "Step 3: Restarting services..."
systemctl restart orchenet-backend
systemctl restart nginx
echo "✓ Services restarted"
echo ""

echo "Step 4: Checking service status..."
sleep 2
if systemctl is-active --quiet orchenet-backend; then
    echo "✓ Backend is running"
else
    echo "✗ Backend failed to start"
    journalctl -u orchenet-backend -n 20 --no-pager
fi

if systemctl is-active --quiet nginx; then
    echo "✓ Nginx is running"
else
    echo "✗ Nginx failed to start"
fi

echo ""
echo "=========================================="
echo "Update deployment complete!"
echo "=========================================="
echo ""
echo "Clear your browser cache and refresh the page to see changes"
echo ""
