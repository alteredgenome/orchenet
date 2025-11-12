# Syncthing Setup for OrcheNet Development

Syncthing provides automatic, continuous synchronization between your Windows development machine and the Debian server.

## Overview

**Local (Windows):**
- `C:\Users\AlteredGenome\Documents\GitHub\orchenet`
- Edit with VS Code, your favorite IDE, etc.
- Changes sync automatically

**Remote (Debian):**
- `orche-dev.goxtt.net (143.20.131.211)`
- `/root/orchenet-dev` (Syncthing folder)
- Changes automatically applied to `/opt/orchenet`

## Installation

### Step 1: Install Syncthing on Windows

**Option A: Using Scoop (Recommended)**

```powershell
# Install Scoop if not already installed
# https://scoop.sh

scoop install syncthing

# Start Syncthing
syncthing
```

**Option B: Using Chocolatey**

```powershell
choco install syncthing
syncthing
```

**Option C: Manual Download**

1. Download from https://syncthing.net/downloads/
2. Extract to `C:\Program Files\Syncthing`
3. Run `syncthing.exe`

### Step 2: Install Syncthing on Debian Server

```bash
# SSH to server
ssh root@143.20.131.211

# Add Syncthing repository
curl -s https://syncthing.net/release-key.txt | apt-key add -
echo "deb https://apt.syncthing.net/ syncthing stable" | tee /etc/apt/sources.list.d/syncthing.list

# Update and install
apt-get update
apt-get install -y syncthing

# Create syncthing user (optional, or use root)
useradd -m -s /bin/bash syncthing
```

### Step 3: Configure Syncthing on Server

```bash
# Generate initial config
syncthing -generate="/root/.config/syncthing"

# Edit config to allow remote access
nano /root/.config/syncthing/config.xml
```

Find the GUI address line and change from:
```xml
<address>127.0.0.1:8384</address>
```

To:
```xml
<address>0.0.0.0:8384</address>
```

Save and exit.

### Step 4: Create Systemd Service for Syncthing

```bash
# Create service file
cat > /etc/systemd/system/syncthing.service <<EOF
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

# Enable and start service
systemctl daemon-reload
systemctl enable syncthing
systemctl start syncthing

# Check status
systemctl status syncthing
```

### Step 5: Configure Firewall

```bash
# Allow Syncthing ports
ufw allow 8384/tcp comment "Syncthing Web UI"
ufw allow 22000/tcp comment "Syncthing transfers"
ufw allow 21027/udp comment "Syncthing discovery"

# Reload firewall
ufw reload
```

## Configuration

### Step 6: Access Syncthing Web UIs

**Windows:**
- Open browser to http://localhost:8384

**Debian Server:**
- Open browser to http://143.20.131.211:8384

### Step 7: Connect Devices

**On Windows Syncthing:**

1. Open http://localhost:8384
2. Go to **Actions** → **Show ID**
3. Copy your Device ID

**On Server Syncthing:**

1. Open http://143.20.131.211:8384
2. Click **Add Remote Device**
3. Paste Windows Device ID
4. Give it a name: "Windows Dev Machine"
5. Click **Save**

**On Windows Syncthing:**

1. You'll get a notification "New Device"
2. Click **Add Device**
3. Give it a name: "OrcheNet Dev Server"
4. Click **Save**

### Step 8: Share OrcheNet Folder

**On Windows Syncthing:**

1. Click **Add Folder**
2. **Folder Path**: `C:\Users\AlteredGenome\Documents\GitHub\orchenet`
3. **Folder Label**: "OrcheNet Development"
4. **Folder ID**: `orchenet-dev` (remember this)
5. Go to **Sharing** tab
6. Check the box next to "OrcheNet Dev Server"
7. Click **Save**

**On Server Syncthing:**

1. You'll get a notification "New Folder Shared"
2. Click to accept
3. Change **Folder Path** to: `/root/orchenet-dev`
4. Click **Save**

### Step 9: Wait for Initial Sync

- Syncthing will sync all files
- This may take a few minutes
- Watch progress in Web UI

## Auto-Apply Changes Script

Since Syncthing syncs to `/root/orchenet-dev`, we need a script to apply changes to `/opt/orchenet` and restart services.

### Step 10: Create Watcher Script

```bash
# SSH to server
ssh root@143.20.131.211

# Create watcher script
cat > /root/orchenet-sync-watcher.sh <<'EOF'
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
    chown -R orchenet:orchenet $INSTALL_DIR/backend
    chown -R orchenet:orchenet $INSTALL_DIR/frontend

    # Restart backend
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
EOF

# Make executable
chmod +x /root/orchenet-sync-watcher.sh
```

### Step 11: Create Systemd Service for Watcher

```bash
cat > /etc/systemd/system/orchenet-sync-watcher.service <<EOF
[Unit]
Description=OrcheNet Syncthing Sync Watcher
After=syncthing.service orchenet-backend.service
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

# Enable and start
systemctl daemon-reload
systemctl enable orchenet-sync-watcher
systemctl start orchenet-sync-watcher

# Check status
systemctl status orchenet-sync-watcher
```

## Verification

### Check Sync Status

**On Windows:**
```
Open http://localhost:8384
Check folder status - should show "Up to Date"
```

**On Server:**
```bash
# Check Syncthing is running
systemctl status syncthing

# Check watcher is running
systemctl status orchenet-sync-watcher

# View watcher logs
journalctl -u orchenet-sync-watcher -f

# Check files are syncing
ls -la /root/orchenet-dev
```

### Test the Setup

**On Windows:**

1. Open a Python file in VS Code
2. Make a small change (add a comment)
3. Save the file
4. Watch the magic happen!

**On Server:**

```bash
# Watch the watcher logs
journalctl -u orchenet-sync-watcher -f

# Should see:
# [timestamp] Changes detected, applying...
# Restarting backend service...
# ✓ Backend restarted successfully
# [timestamp] Sync complete
```

**In Browser:**
- Changes should be live at http://orche-dev.goxtt.net

## Usage

### Daily Development Workflow

1. **Edit files on Windows** using VS Code or any editor
2. **Save** (Ctrl+S)
3. **Syncthing automatically syncs** to server (within seconds)
4. **Watcher detects changes** and applies them
5. **Backend restarts** automatically
6. **Test changes** at http://orche-dev.goxtt.net

That's it! No manual commands needed!

## Syncthing Ignore Patterns

Create `.stignore` in your Windows folder to exclude files:

```bash
# On Windows, create:
# C:\Users\AlteredGenome\Documents\GitHub\orchenet\.stignore

# Python
venv/
__pycache__/
*.pyc
*.pyo
*.db
*.db-journal
.pytest_cache/

# Node.js
node_modules/
dist/
.vite/

# Logs
logs/
*.log

# OS
.DS_Store
Thumbs.db
.vscode/
.idea/

# Git
.git/
```

## Monitoring

### View Syncthing Logs

```bash
# Server Syncthing
journalctl -u syncthing -f

# Watcher
journalctl -u orchenet-sync-watcher -f

# Backend (to see if changes applied)
journalctl -u orchenet-backend -f
```

### Check Sync Status

```bash
# Syncthing status
systemctl status syncthing

# Watcher status
systemctl status orchenet-sync-watcher

# OrcheNet status
systemctl status orchenet-backend
```

## Troubleshooting

### Syncthing Not Syncing

```bash
# Restart Syncthing
systemctl restart syncthing

# Check firewall
ufw status | grep -E '8384|22000|21027'

# Check logs
journalctl -u syncthing -n 50 --no-pager
```

### Watcher Not Applying Changes

```bash
# Check if watcher is running
systemctl status orchenet-sync-watcher

# Restart watcher
systemctl restart orchenet-sync-watcher

# Check logs
journalctl -u orchenet-sync-watcher -f

# Manual apply
rsync -av /root/orchenet-dev/backend/ /opt/orchenet/backend/
systemctl restart orchenet-backend
```

### Backend Not Restarting

```bash
# Check backend logs
journalctl -u orchenet-backend -n 100 --no-pager

# Check for Python syntax errors
cd /opt/orchenet
source venv/bin/activate
python -m py_compile backend/app/main.py

# Manual restart
systemctl restart orchenet-backend
```

### Files Not Syncing

```bash
# Check .stignore patterns
cat /root/orchenet-dev/.stignore

# Check Syncthing Web UI
# http://143.20.131.211:8384

# Force rescan
# In Syncthing Web UI: Actions → Rescan All
```

## Advantages of Syncthing

✅ **Automatic**: No manual commands needed
✅ **Bidirectional**: Edit on either machine
✅ **Real-time**: Changes sync in seconds
✅ **Versioning**: Built-in file versioning
✅ **Conflict Resolution**: Handles conflicts gracefully
✅ **No Cloud**: Direct peer-to-peer sync
✅ **Works Offline**: Syncs when connection restored
✅ **Cross-Platform**: Works on Windows, Linux, Mac

## Security

**Syncthing Security:**
- Encrypted transfers (TLS)
- Device authentication
- No data on third-party servers
- Private peer-to-peer

**Recommendations:**
- Use SSH tunnel for extra security:
  ```bash
  ssh -L 8384:localhost:8384 root@143.20.131.211
  # Access via http://localhost:8384
  ```
- Set GUI password in Syncthing settings
- Use firewall rules to restrict access

## Backup Consideration

**Important**: Syncthing syncs deletions too!

- If you delete a file on Windows, it deletes on server
- Enable **File Versioning** in Syncthing:
  1. Open folder settings
  2. **File Versioning** → **Simple File Versioning**
  3. Keep versions for 30 days

## Quick Reference

```bash
# Start/Stop Services
systemctl start syncthing
systemctl stop syncthing
systemctl restart syncthing
systemctl start orchenet-sync-watcher
systemctl stop orchenet-sync-watcher

# View Logs
journalctl -u syncthing -f
journalctl -u orchenet-sync-watcher -f
journalctl -u orchenet-backend -f

# Check Status
systemctl status syncthing
systemctl status orchenet-sync-watcher
systemctl status orchenet-backend

# Manual Sync
rsync -av /root/orchenet-dev/ /opt/orchenet/
systemctl restart orchenet-backend

# Web UIs
# Windows: http://localhost:8384
# Server: http://143.20.131.211:8384
# OrcheNet: http://orche-dev.goxtt.net
```

## Summary

With Syncthing:
1. Edit code on Windows
2. Save file (Ctrl+S)
3. Automatically syncs to server
4. Watcher applies changes
5. Backend restarts
6. Changes live at http://orche-dev.goxtt.net

**No manual commands needed!** Just edit and save. 🎉
