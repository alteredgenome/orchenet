#!/bin/bash
# Quick deployment script for OrcheNet updates
# Run this on the server after pushing changes to git

set -e

echo "===== OrcheNet Update Deployment ====="
echo ""

# Pull latest changes
echo "Pulling latest changes from git..."
git pull

# Ensure sudoers configuration is up to date
echo "Updating sudoers configuration for WireGuard..."
sudo bash -c 'cat > /etc/sudoers.d/orchenet <<EOF
# Allow orchenet user to manage WireGuard without password
orchenet ALL=(ALL) NOPASSWD: /usr/bin/wg
orchenet ALL=(ALL) NOPASSWD: /usr/bin/wg-quick
orchenet ALL=(ALL) NOPASSWD: /bin/systemctl restart wg-quick@*
orchenet ALL=(ALL) NOPASSWD: /bin/systemctl reload wg-quick@*
orchenet ALL=(ALL) NOPASSWD: /usr/bin/tee /etc/wireguard/*.conf
orchenet ALL=(ALL) NOPASSWD: /bin/cat /etc/wireguard/*.conf
orchenet ALL=(ALL) NOPASSWD: /bin/chmod * /etc/wireguard/*.conf
EOF
chmod 440 /etc/sudoers.d/orchenet'
echo "✓ Sudoers configuration updated"

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
