# Development Workflow Guide

## Development Server Setup

**Development Server:** orche-dev.goxtt.net (143.20.131.211)
**Local Development:** Windows machine (C:\Users\AlteredGenome\Documents\GitHub\orchenet)

## Initial Setup on Development Server

### 1. First-Time Deployment

```bash
# SSH to development server
ssh root@143.20.131.211

# Clone repository
cd /opt
git clone https://github.com/yourusername/orchenet.git orchenet

# Run installation
cd orchenet/deploy
chmod +x install.sh
./install.sh

# Wait for installation to complete (5-10 minutes)
```

### 2. Verify Installation

```bash
# Check services
/opt/orchenet/status.sh

# Access web interface
# http://orche-dev.goxtt.net
# or
# http://143.20.131.211
```

## Development Workflows

### Method 1: Git Push/Pull (Recommended for Stable Changes)

**Best for:** Completed features, bug fixes, stable changes

**Workflow:**

```bash
# On Windows (Git Bash or PowerShell):

# 1. Make your changes in VS Code or your editor

# 2. Commit changes
git add .
git commit -m "Add new feature XYZ"

# 3. Push to remote
git push origin main

# 4. SSH to dev server and pull
ssh root@143.20.131.211
cd /opt/orchenet
git pull origin main

# 5. Restart services
systemctl restart orchenet-backend
systemctl restart nginx

# 6. Check status
systemctl status orchenet-backend
```

**Or use the automated script:**

```bash
# On Windows (Git Bash):
cd /c/Users/AlteredGenome/Documents/GitHub/orchenet
./deploy-to-dev.sh
```

### Method 2: Rsync (Fast Sync for Testing)

**Best for:** Quick iterations, testing changes, development

**Workflow:**

```bash
# On Windows (Git Bash):
cd /c/Users/AlteredGenome/Documents/GitHub/orchenet

# Run sync script
./sync-to-dev.sh

# Script will:
# - Sync backend files (excluding venv)
# - Sync frontend files (excluding node_modules)
# - Sync device scripts
# - Sync documentation
# - Optionally rebuild frontend
# - Optionally restart services
```

**Advantages:**
- ✓ Fast (only changed files)
- ✓ No git commits needed
- ✓ Great for rapid testing

**Disadvantages:**
- ✗ Not version controlled
- ✗ Can get out of sync with git

### Method 3: VS Code Remote SSH (Live Editing)

**Best for:** Real-time development, debugging

**Setup:**

1. **Install VS Code Extension:**
   - Open VS Code
   - Install "Remote - SSH" extension

2. **Configure SSH Connection:**
   - Press F1 → "Remote-SSH: Open SSH Configuration File"
   - Add:
     ```
     Host orche-dev
         HostName 143.20.131.211
         User root
         Port 22
     ```

3. **Connect to Server:**
   - Press F1 → "Remote-SSH: Connect to Host"
   - Select "orche-dev"
   - Open folder: `/opt/orchenet`

4. **Edit Files Directly on Server**
   - Changes are instant
   - Backend auto-reloads with uvicorn

**Advantages:**
- ✓ Edit directly on server
- ✓ No sync needed
- ✓ Great for debugging

**Disadvantages:**
- ✗ Requires SSH access
- ✗ Edits not on local machine

### Method 4: Watch & Auto-Deploy (Active Development)

**Best for:** Continuous development with auto-sync

**Setup:**

```bash
# Install fswatch (if not installed)
# Windows Git Bash: scoop install fswatch
# macOS: brew install fswatch
# Linux/WSL: apt-get install inotify-tools

# On Windows (Git Bash):
cd /c/Users/AlteredGenome/Documents/GitHub/orchenet
./watch-and-deploy.sh

# Leave running in background
# Automatically syncs on file changes
```

**Advantages:**
- ✓ Automatic sync on save
- ✓ Fast feedback loop
- ✓ Great for active development

**Disadvantages:**
- ✗ Requires running process
- ✗ Can be resource intensive

## Recommended Development Workflow

### Daily Development

```
1. Edit files on Windows using your preferred editor
2. Test locally if possible
3. Use rsync sync for quick testing: ./sync-to-dev.sh
4. Verify on dev server: http://orche-dev.goxtt.net
5. When satisfied, commit to git
6. Use deploy script for final deployment: ./deploy-to-dev.sh
```

### Quick Fixes

```
1. SSH to server: ssh root@143.20.131.211
2. Edit file directly: nano /opt/orchenet/backend/app/...
3. Restart service: systemctl restart orchenet-backend
4. Pull changes back to local: git pull
```

### Testing New Features

```
1. Create feature branch: git checkout -b feature/new-thing
2. Develop on Windows
3. Sync to dev server: ./sync-to-dev.sh
4. Test thoroughly
5. Commit and merge to main
6. Deploy: ./deploy-to-dev.sh
```

## Common Tasks

### Restart Backend Only

```bash
ssh root@143.20.131.211 "systemctl restart orchenet-backend"
```

### View Logs

```bash
# Real-time logs
ssh root@143.20.131.211 "journalctl -u orchenet-backend -f"

# Last 100 lines
ssh root@143.20.131.211 "journalctl -u orchenet-backend -n 100 --no-pager"
```

### Check Service Status

```bash
ssh root@143.20.131.211 "/opt/orchenet/status.sh"
```

### Rebuild Frontend

```bash
ssh root@143.20.131.211 "cd /opt/orchenet/frontend && npm install && npm run build && systemctl restart nginx"
```

### Update Python Dependencies

```bash
ssh root@143.20.131.211 "cd /opt/orchenet && source venv/bin/activate && pip install -r backend/requirements.txt && systemctl restart orchenet-backend"
```

### Backup Database

```bash
ssh root@143.20.131.211 "/opt/orchenet/backup.sh"
```

### Pull Database to Local (for testing)

```bash
scp root@143.20.131.211:/opt/orchenet/data/orchenet.db ./local-orchenet.db
```

## File Synchronization Details

### What Gets Synced

**Backend:**
- ✓ Python source files (*.py)
- ✓ Configuration files
- ✓ Requirements.txt
- ✗ Virtual environment (venv)
- ✗ Database file (orchenet.db)
- ✗ Cache files (__pycache__)

**Frontend:**
- ✓ Source files (src/)
- ✓ Configuration files
- ✗ node_modules
- ✗ dist/ (rebuilt on server)

**Device Scripts:**
- ✓ All provisioning scripts
- ✓ README files

**Documentation:**
- ✓ All .md files

### Excluded Files (Never Synced)

```
# Python
venv/
__pycache__/
*.pyc
*.pyo
.pytest_cache/

# Node.js
node_modules/
dist/
.vite/

# Data
*.db
*.db-journal
logs/
*.log

# OS
.DS_Store
Thumbs.db
```

## Troubleshooting

### Sync Script Fails

```bash
# Check SSH connection
ssh root@143.20.131.211 "echo 'Connected'"

# Check rsync is installed
which rsync

# Verbose sync
rsync -avz --progress [source] [destination]
```

### Service Won't Start After Sync

```bash
# Check logs
ssh root@143.20.131.211 "journalctl -u orchenet-backend -n 50 --no-pager"

# Check Python syntax
ssh root@143.20.131.211 "cd /opt/orchenet && source venv/bin/activate && python -m py_compile backend/app/main.py"

# Restart manually
ssh root@143.20.131.211 "systemctl restart orchenet-backend"
```

### Permission Issues

```bash
# Fix ownership
ssh root@143.20.131.211 "chown -R orchenet:orchenet /opt/orchenet"

# Fix permissions
ssh root@143.20.131.211 "chmod -R 755 /opt/orchenet"
```

### Git Conflicts

```bash
# On server, stash changes
ssh root@143.20.131.211
cd /opt/orchenet
git stash
git pull origin main
git stash pop
```

## SSH Configuration

### Setup SSH Key (No Password)

```bash
# Generate SSH key (if not exists)
ssh-keygen -t ed25519 -C "orchenet-dev"

# Copy to server
ssh-copy-id root@143.20.131.211

# Test
ssh root@143.20.131.211 "echo 'SSH Key Working'"
```

### SSH Config File

Create/edit `~/.ssh/config`:

```
Host orche-dev
    HostName 143.20.131.211
    User root
    Port 22
    IdentityFile ~/.ssh/id_ed25519
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

Now you can just use: `ssh orche-dev`

## Git Workflow

### Feature Branch Workflow

```bash
# Create feature branch
git checkout -b feature/wireguard-improvements

# Make changes, commit
git add .
git commit -m "Improve WireGuard peer management"

# Sync to dev for testing
./sync-to-dev.sh

# Test on dev server
# http://orche-dev.goxtt.net

# If good, merge to main
git checkout main
git merge feature/wireguard-improvements
git push origin main

# Deploy to dev
./deploy-to-dev.sh
```

### Hotfix Workflow

```bash
# Fix directly on server for emergency
ssh root@143.20.131.211
nano /opt/orchenet/backend/app/...
systemctl restart orchenet-backend

# Pull changes back to local
git pull

# Commit the fix
git add .
git commit -m "Hotfix: Fix XYZ issue"
git push origin main
```

## Best Practices

1. **Always commit before deploying to production**
   - Development server = testing ground
   - Git main branch = stable code

2. **Use descriptive commit messages**
   ```bash
   git commit -m "Add WireGuard peer status monitoring"
   ```

3. **Test on dev server before production**
   - Deploy to orche-dev.goxtt.net first
   - Verify everything works
   - Then deploy to production

4. **Keep dev server in sync with git**
   - Regularly pull latest code
   - Avoid manual edits on server

5. **Backup before major changes**
   ```bash
   ssh root@143.20.131.211 "/opt/orchenet/backup.sh"
   ```

6. **Monitor logs during development**
   ```bash
   ssh root@143.20.131.211 "journalctl -u orchenet-backend -f"
   ```

## Quick Reference

```bash
# Deploy changes (git)
./deploy-to-dev.sh

# Sync changes (rsync)
./sync-to-dev.sh

# Watch for changes
./watch-and-deploy.sh

# SSH to server
ssh root@143.20.131.211

# View logs
ssh root@143.20.131.211 "journalctl -u orchenet-backend -f"

# Restart backend
ssh root@143.20.131.211 "systemctl restart orchenet-backend"

# Check status
ssh root@143.20.131.211 "/opt/orchenet/status.sh"

# Backup
ssh root@143.20.131.211 "/opt/orchenet/backup.sh"
```

## Summary

- **Quick testing**: Use `./sync-to-dev.sh`
- **Stable deployment**: Use `./deploy-to-dev.sh`
- **Live editing**: Use VS Code Remote SSH
- **Active development**: Use `./watch-and-deploy.sh`
- **Emergency fixes**: SSH directly and edit

Choose the method that fits your current task!
