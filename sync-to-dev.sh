#!/bin/bash
###############################################################################
# Quick Sync to Development Server (using rsync)
# Syncs local changes without git commit
###############################################################################

# Configuration
DEV_SERVER="root@143.20.131.211"
DEV_PATH="/opt/orchenet"
LOCAL_PATH="/c/Users/AlteredGenome/Documents/GitHub/orchenet"

echo "===== Syncing to Development Server ====="
echo "Local:  $LOCAL_PATH"
echo "Remote: $DEV_SERVER:$DEV_PATH"
echo ""

# Sync backend
echo "Syncing backend..."
rsync -avz --delete \
    --exclude 'venv' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '.pytest_cache' \
    --exclude 'orchenet.db' \
    $LOCAL_PATH/backend/ $DEV_SERVER:$DEV_PATH/backend/

# Sync frontend
echo "Syncing frontend source..."
rsync -avz --delete \
    --exclude 'node_modules' \
    --exclude 'dist' \
    --exclude '.vite' \
    $LOCAL_PATH/frontend/ $DEV_SERVER:$DEV_PATH/frontend/

# Sync device scripts
echo "Syncing device scripts..."
rsync -avz --delete \
    $LOCAL_PATH/device-scripts/ $DEV_SERVER:$DEV_PATH/device-scripts/

# Sync deployment scripts
echo "Syncing deployment scripts..."
rsync -avz \
    $LOCAL_PATH/deploy/ $DEV_SERVER:$DEV_PATH/deploy/

# Sync documentation
echo "Syncing documentation..."
rsync -avz \
    $LOCAL_PATH/*.md $DEV_SERVER:$DEV_PATH/

# Rebuild frontend on server
echo ""
read -p "Rebuild frontend on server? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Rebuilding frontend..."
    ssh $DEV_SERVER "cd $DEV_PATH/frontend && npm install && npm run build"
fi

# Restart backend service
echo ""
read -p "Restart backend service? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Restarting backend..."
    ssh $DEV_SERVER "systemctl restart orchenet-backend"
    sleep 2
    ssh $DEV_SERVER "systemctl status orchenet-backend --no-pager | grep Active"
fi

echo ""
echo "===== Sync Complete ====="
echo "View logs: ssh $DEV_SERVER 'journalctl -u orchenet-backend -f'"
echo "Access: http://orche-dev.goxtt.net"
echo ""
