#!/bin/bash
###############################################################################
# Syncthing Server Setup Script
# Run this on the Debian server (143.20.131.211)
###############################################################################

set -e

echo "===== OrcheNet Syncthing Server Setup ====="
echo ""

# Install Syncthing
echo "Step 1: Installing Syncthing..."
curl -s https://syncthing.net/release-key.txt | apt-key add -
echo "deb https://apt.syncthing.net/ syncthing stable" | tee /etc/apt/sources.list.d/syncthing.list
apt-get update
apt-get install -y syncthing inotify-tools

# Generate initial config
echo "Step 2: Generating Syncthing configuration..."
mkdir -p /root/.config/syncthing
syncthing -generate="/root/.config/syncthing" || true

# Configure to allow remote access
echo "Step 3: Configuring remote access..."
sed -i 's/<address>127.0.0.1:8384<\/address>/<address>0.0.0.0:8384<\/address>/' /root/.config/syncthing/config.xml

# Create systemd service
echo "Step 4: Creating Syncthing systemd service..."
cat > /etc/systemd/system/syncthing.service <<'EOF'
[Unit]
Description=Syncthing - Open Source Continuous File Synchronization
Documentation=man:syncthing(1)
After=network.target

[Service]
User=root
ExecStart=/usr/bin/syncthing -no-browser -gui-address=0.0.0.0:8384
Restart=on-failure
SuccessExitStatus=3 4
RestartForceExitStatus=3 4

[Install]
WantedBy=multi-user.target
EOF

# Enable and start Syncthing
systemctl daemon-reload
systemctl enable syncthing
systemctl start syncthing

# Wait for Syncthing to start
echo "Waiting for Syncthing to start..."
sleep 5

# Create sync directory
mkdir -p /root/orchenet-dev

# Configure firewall
echo "Step 5: Configuring firewall..."
ufw allow 8384/tcp comment "Syncthing Web UI"
ufw allow 22000/tcp comment "Syncthing transfers"
ufw allow 21027/udp comment "Syncthing discovery"

# Create watcher script
echo "Step 6: Creating sync watcher script..."
cat > /root/orchenet-sync-watcher.sh <<'WATCHEREOF'
#!/bin/bash
###############################################################################
# Syncthing Sync Watcher
# Monitors Syncthing folder and applies changes to OrcheNet installation
###############################################################################

SYNC_DIR="/root/orchenet-dev"
INSTALL_DIR="/opt/orchenet"

echo "===== Syncthing Sync Watcher ====="
echo "Monitoring: $SYNC_DIR"
echo "Target: $INSTALL_DIR"
echo ""

# Install inotify-tools if not present
if ! command -v inotifywait &> /dev/null; then
    echo "Installing inotify-tools..."
    apt-get install -y inotify-tools
fi

# Function to sync and restart
apply_changes() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Changes detected, applying..."

    # Sync backend
    rsync -a --delete \
        --exclude 'venv' \
        --exclude '__pycache__' \
        --exclude '*.pyc' \
        --exclude '*.db' \
        --exclude '*.db-journal' \
        $SYNC_DIR/backend/ $INSTALL_DIR/backend/

    # Sync frontend source
    rsync -a --delete \
        --exclude 'node_modules' \
        --exclude 'dist' \
        --exclude '.vite' \
        $SYNC_DIR/frontend/ $INSTALL_DIR/frontend/

    # Sync device scripts
    rsync -a --delete \
        $SYNC_DIR/device-scripts/ $INSTALL_DIR/device-scripts/

    # Sync deploy scripts
    rsync -a \
        $SYNC_DIR/deploy/ $INSTALL_DIR/deploy/

    # Sync docs
    rsync -a \
        $SYNC_DIR/*.md $INSTALL_DIR/ 2>/dev/null || true

    # Fix permissions
    chown -R orchenet:orchenet $INSTALL_DIR/backend 2>/dev/null || true
    chown -R orchenet:orchenet $INSTALL_DIR/frontend 2>/dev/null || true

    # Restart backend if it exists
    if systemctl list-units --full --all | grep -q orchenet-backend; then
        echo "Restarting backend service..."
        systemctl restart orchenet-backend

        # Check if restart was successful
        sleep 2
        if systemctl is-active --quiet orchenet-backend; then
            echo "✓ Backend restarted successfully"
        else
            echo "✗ Backend restart failed!"
            journalctl -u orchenet-backend -n 20 --no-pager
        fi
    else
        echo "Note: orchenet-backend service not found (install OrcheNet first)"
    fi

    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Sync complete"
    echo ""
}

# Initial sync
apply_changes

# Watch for changes (with debouncing)
inotifywait -m -r -e modify,create,delete,move \
    --exclude '(\.git|\.stfolder|venv|node_modules|__pycache__|\.pyc$|\.db$|dist)' \
    $SYNC_DIR | while read path action file; do

    # Only trigger for relevant files
    if [[ "$file" =~ \.(py|js|jsx|ts|tsx|json|md|rsc|sh|yml|yaml)$ ]]; then
        # Debounce - wait 3 seconds for multiple changes
        sleep 3
        apply_changes
    fi
done
WATCHEREOF

chmod +x /root/orchenet-sync-watcher.sh

# Create watcher systemd service
echo "Step 7: Creating watcher systemd service..."
cat > /etc/systemd/system/orchenet-sync-watcher.service <<'EOF'
[Unit]
Description=OrcheNet Syncthing Sync Watcher
After=syncthing.service
Requires=syncthing.service

[Service]
Type=simple
User=root
ExecStart=/root/orchenet-sync-watcher.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable orchenet-sync-watcher
systemctl start orchenet-sync-watcher

# Get server Device ID
echo ""
echo "===== Setup Complete! ====="
echo ""
echo "Syncthing Web UI: http://$(curl -s ifconfig.me):8384"
echo "Syncthing Status: $(systemctl is-active syncthing)"
echo "Watcher Status: $(systemctl is-active orchenet-sync-watcher)"
echo ""
echo "Getting Server Device ID..."
sleep 2

# Try to get device ID
DEVICE_ID=$(cat /root/.config/syncthing/config.xml | grep -o '<device id="[^"]*"' | head -1 | cut -d'"' -f2)

if [ -n "$DEVICE_ID" ]; then
    echo "Server Device ID: $DEVICE_ID"
else
    echo "Device ID not yet available. Check: journalctl -u syncthing -n 20"
fi

echo ""
echo "Next steps:"
echo "1. Open http://$(curl -s ifconfig.me):8384 in browser"
echo "2. Add Windows device with ID: PLMK4CZ-YNIMTUN-5EH4ZCE-QFPLCXQ-6OERKKO-QLP72SD-SNYWCE6-CH4VPQA"
echo "3. Share folder from Windows (orchenet-dev)"
echo "4. Accept folder share on server"
echo ""
