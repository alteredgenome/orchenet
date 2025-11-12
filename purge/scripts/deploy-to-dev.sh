#!/bin/bash
###############################################################################
# Deploy to Development Server Script
# Pushes code changes to orche-dev.goxtt.net and restarts services
###############################################################################

# Configuration
DEV_SERVER="root@143.20.131.211"
DEV_PATH="/opt/orchenet"
REPO_PATH="C:/Users/AlteredGenome/Documents/GitHub/orchenet"

echo "===== Deploying to Development Server ====="
echo "Server: orche-dev.goxtt.net (143.20.131.211)"
echo ""

# Step 1: Commit changes locally (optional)
read -p "Commit changes locally? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Enter commit message: " commit_msg
    git add .
    git commit -m "$commit_msg"
fi

# Step 2: Push to remote
echo "Pushing to remote repository..."
git push origin main

# Step 3: Pull on dev server
echo "Pulling latest code on dev server..."
ssh $DEV_SERVER "cd $DEV_PATH && git pull origin main"

# Step 4: Update Python dependencies if needed
read -p "Update Python dependencies? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Updating Python dependencies..."
    ssh $DEV_SERVER "cd $DEV_PATH && source venv/bin/activate && pip install -r backend/requirements.txt"
fi

# Step 5: Rebuild frontend if needed
read -p "Rebuild frontend? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Rebuilding frontend..."
    ssh $DEV_SERVER "cd $DEV_PATH/frontend && npm install && npm run build"
fi

# Step 6: Restart services
echo "Restarting services..."
ssh $DEV_SERVER "systemctl restart orchenet-backend && systemctl restart nginx"

# Step 7: Check status
echo ""
echo "Checking service status..."
ssh $DEV_SERVER "systemctl status orchenet-backend --no-pager | grep Active"

echo ""
echo "===== Deployment Complete ====="
echo "Access: http://orche-dev.goxtt.net"
echo ""
