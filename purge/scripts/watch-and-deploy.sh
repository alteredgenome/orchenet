#!/bin/bash
###############################################################################
# Watch for Changes and Auto-Deploy
# Monitors local files and syncs on changes
# Requires: inotify-tools or fswatch
###############################################################################

DEV_SERVER="root@143.20.131.211"
DEV_PATH="/opt/orchenet"
LOCAL_PATH="/c/Users/AlteredGenome/Documents/GitHub/orchenet"

echo "===== Watching for changes ====="
echo "Monitoring: $LOCAL_PATH"
echo "Target: $DEV_SERVER:$DEV_PATH"
echo "Press Ctrl+C to stop"
echo ""

# Function to sync and restart
sync_and_restart() {
    echo "[$(date '+%H:%M:%S')] Change detected, syncing..."

    # Sync backend Python files
    rsync -az --delete \
        --exclude 'venv' \
        --exclude '__pycache__' \
        --exclude '*.pyc' \
        --exclude 'orchenet.db' \
        $LOCAL_PATH/backend/ $DEV_SERVER:$DEV_PATH/backend/

    # Restart backend if Python files changed
    if [[ "$1" == *".py"* ]]; then
        echo "Python file changed, restarting backend..."
        ssh $DEV_SERVER "systemctl restart orchenet-backend"
    fi

    echo "[$(date '+%H:%M:%S')] Sync complete"
    echo ""
}

# Check if fswatch is available (macOS/Windows Git Bash)
if command -v fswatch &> /dev/null; then
    fswatch -o $LOCAL_PATH/backend | while read change; do
        sync_and_restart "$change"
    done
# Check if inotifywait is available (Linux/WSL)
elif command -v inotifywait &> /dev/null; then
    while inotifywait -r -e modify,create,delete $LOCAL_PATH/backend; do
        sync_and_restart
    done
else
    echo "Error: fswatch or inotifywait not found"
    echo "Install with:"
    echo "  macOS: brew install fswatch"
    echo "  Linux: apt-get install inotify-tools"
    echo "  Windows: Use Git Bash with fswatch"
    exit 1
fi
