# OrcheNet Deployment Guide

Complete guide for deploying OrcheNet on Debian 13 with WireGuard VPN and MikroTik router support.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Detailed Installation](#detailed-installation)
5. [Post-Installation Configuration](#post-installation-configuration)
6. [Adding MikroTik Devices](#adding-mikrotik-devices)
7. [Architecture](#architecture)
8. [Troubleshooting](#troubleshooting)
9. [Maintenance](#maintenance)
10. [Security Considerations](#security-considerations)

## Overview

OrcheNet is a self-hosted network device management platform with:
- **WireGuard VPN**: Secure connection to devices without public IPs
- **Web CLI**: Browser-based terminal access to MikroTik routers
- **Configuration Management**: YAML-based, version-controlled configs
- **Agent-Based Architecture**: Devices phone home, no inbound firewall rules needed
- **Multi-Device Support**: Manage multiple MikroTik routers from single interface

### System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     OrcheNet Server                          │
│  ┌──────────────┐  ┌───────────┐  ┌──────────────┐         │
│  │   Frontend   │  │  Backend  │  │  WireGuard   │         │
│  │   (React)    │  │  (FastAPI)│  │    Server    │         │
│  │   Port 80    │  │  Port 8000│  │  Port 51820  │         │
│  └──────────────┘  └───────────┘  └──────────────┘         │
│         │                │                │                  │
│         └────────────────┴────────────────┘                  │
│                          │                                   │
└──────────────────────────┼───────────────────────────────────┘
                           │
                           │ WireGuard VPN (10.99.0.0/24)
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐       ┌────▼────┐       ┌────▼────┐
   │MikroTik │       │MikroTik │       │MikroTik │
   │Router 1 │       │Router 2 │       │Router 3 │
   │10.99.0.2│       │10.99.0.3│       │10.99.0.4│
   └─────────┘       └─────────┘       └─────────┘
```

## Prerequisites

### Server Requirements

- **OS**: Debian 13 (Bookworm) - fresh installation
- **CPU**: 2+ cores recommended
- **RAM**: 2GB minimum, 4GB recommended
- **Disk**: 20GB minimum, 50GB recommended
- **Network**: Public IP address with internet access
- **Ports**: 80, 443, 51820/udp, 22

### Required Skills

- Basic Linux command line knowledge
- SSH access to servers
- Basic networking concepts (IP addressing, routing)
- Access to configure MikroTik routers

### What You Need

1. Debian 13 server with root access
2. MikroTik router(s) with RouterOS 7.x+
3. SSH client (PuTTY, Terminal, etc.)
4. Web browser for accessing OrcheNet interface

## Quick Start

For experienced users who want to get running quickly:

```bash
# 1. SSH to your Debian server as root
ssh root@your-server-ip

# 2. Download and run installation script
git clone https://github.com/yourusername/orchenet.git
cd orchenet/deploy
chmod +x install.sh
./install.sh

# 3. Access web interface
# Open browser to http://YOUR_SERVER_IP

# 4. Generate provisioning script for first router
cd /opt/orchenet/device-scripts/mikrotik
python3 generate-provision-script.py --device-id 1 --server http://YOUR_SERVER_IP:8000 --server-ip YOUR_SERVER_IP

# 5. Apply script to MikroTik router
# (Copy the generated .rsc file to router and run /import)
```

Done! Your first router should appear in OrcheNet within 5 minutes.

## Detailed Installation

### Step 1: Prepare Debian Server

Update system and install prerequisites:

```bash
# Update package lists
apt-get update
apt-get upgrade -y

# Install git
apt-get install -y git

# Verify you have a public IP
curl ifconfig.me
```

### Step 2: Clone Repository

```bash
# Clone OrcheNet repository
cd /root
git clone https://github.com/yourusername/orchenet.git
cd orchenet
```

### Step 3: Run Installation Script

The installation script will:
- Install all system dependencies (Python, Node.js, WireGuard, Nginx, etc.)
- Create `orchenet` system user
- Set up Python virtual environment
- Build frontend application
- Initialize database
- Configure WireGuard VPN server
- Create systemd services
- Configure Nginx reverse proxy
- Generate WireGuard server keys

```bash
cd deploy
chmod +x install.sh
./install.sh
```

**Installation takes approximately 5-10 minutes.**

Watch for any errors in the output. The script will display:
- ✓ for successful steps
- ⚠️ for warnings
- ✗ for errors

### Step 4: Verify Installation

After installation completes:

```bash
# Check service status
systemctl status orchenet-backend
systemctl status wg-quick@wg0
systemctl status nginx

# Or use the convenience script
/opt/orchenet/status.sh
```

All services should show as "active (running)".

### Step 5: Access Web Interface

Open your web browser and navigate to:

```
http://YOUR_SERVER_IP
```

You should see the OrcheNet dashboard.

**Note**: For production, configure HTTPS with Let's Encrypt (see Security section).

## Post-Installation Configuration

### Configure Environment Variables (Optional)

Edit `/opt/orchenet/backend/.env` to customize:

```bash
# Create .env file
cat > /opt/orchenet/backend/.env <<EOF
# Database
DATABASE_URL=sqlite:////opt/orchenet/data/orchenet.db

# Security
SECRET_KEY=your-random-secret-key-here

# Server
HOST=0.0.0.0
PORT=8000

# Logging
LOG_LEVEL=INFO
LOG_FILE=/opt/orchenet/logs/orchenet.log

# WireGuard
WIREGUARD_SUBNET=10.99.0.0/24
WIREGUARD_SERVER_IP=10.99.0.1
EOF

# Restart backend to apply changes
systemctl restart orchenet-backend
```

### Set Up HTTPS (Recommended)

Install Certbot and configure SSL:

```bash
# Install Certbot
apt-get install -y certbot python3-certbot-nginx

# Get certificate (replace with your domain)
certbot --nginx -d orchenet.yourdomain.com

# Certificate will auto-renew
```

Update Nginx configuration:

```bash
# Edit /etc/nginx/sites-available/orchenet
# Change server_name from _ to orchenet.yourdomain.com

systemctl restart nginx
```

### Configure Firewall

```bash
# Install UFW if not present
apt-get install -y ufw

# Allow SSH (IMPORTANT - do this first!)
ufw allow 22/tcp

# Allow HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Allow WireGuard
ufw allow 51820/udp

# Enable firewall
ufw enable

# Check status
ufw status
```

### Backup WireGuard Keys

**IMPORTANT**: Save these keys securely!

```bash
# Copy keys to safe location
cp /opt/orchenet/data/wg-server-private.key ~/wg-backup/
cp /opt/orchenet/data/wg-server-public.key ~/wg-backup/
cp /etc/wireguard/wg0.conf ~/wg-backup/

# Or print them
cat /opt/orchenet/data/wg-server-public.key
```

## Adding MikroTik Devices

### Overview

Process to add a MikroTik router:
1. Add device in OrcheNet web interface
2. Generate provisioning script
3. Apply script to router
4. Verify connection

### Step 1: Add Device in Web Interface

1. Open OrcheNet web interface: `http://YOUR_SERVER_IP`
2. Navigate to **Devices** > **Add Device**
3. Fill in form:
   - **Name**: e.g., "Site-A-Router"
   - **Vendor**: Select "MikroTik"
   - **Model**: Optional (e.g., "RB4011")
   - **Description**: Optional
   - Leave IP/credentials empty for now (will be configured via WireGuard)
4. Click **Add Device**
5. Note the **Device ID** (shown in device list or URL)

### Step 2: Generate Provisioning Script

On the server:

```bash
cd /opt/orchenet/device-scripts/mikrotik

# Run generator script
python3 generate-provision-script.py \
    --device-id 1 \
    --server http://YOUR_SERVER_IP:8000 \
    --server-ip YOUR_PUBLIC_IP \
    --output provision-site-a.rsc

# Replace:
#   1 = Device ID from web interface
#   YOUR_SERVER_IP = Server IP or domain
#   YOUR_PUBLIC_IP = Server's public IP (for WireGuard endpoint)
```

**Output:**
```
OrcheNet MikroTik Provisioning Script Generator
==================================================
Server: http://YOUR_SERVER_IP:8000
Device ID: 1

Fetching OrcheNet server information...
✓ Server Public Key: ABC123...
✓ Server VPN IP: 10.99.0.1
✓ Listen Port: 51820

Generating WireGuard keypair for device...
✓ Device Public Key: XYZ789...

Registering device with OrcheNet...
✓ Device Name: Site-A-Router
✓ Assigned VPN IP: 10.99.0.2

Generating provisioning script...
✓ Provisioning script generated: provision-site-a.rsc

SUCCESS!
```

### Step 3: Copy Script to Router

**Option A: SCP (Recommended)**

```bash
# From server
scp provision-site-a.rsc admin@ROUTER_IP:

# If router has non-standard SSH port
scp -P 2222 provision-site-a.rsc admin@ROUTER_IP:
```

**Option B: Winbox**

1. Open Winbox
2. Connect to router
3. Go to **Files**
4. Drag and drop `provision-site-a.rsc`

**Option C: Copy-Paste**

1. Open `provision-site-a.rsc` in text editor
2. Copy entire contents
3. Connect to router via Winbox/SSH/WebFig terminal
4. Paste entire script (may need to paste in chunks)

### Step 4: Apply Provisioning Script

Connect to router terminal and run:

```routeros
/import provision-site-a.rsc
```

**Watch the output:**
```
===== OrcheNet Provisioning Script =====
Device: Site-A-Router
Server: YOUR_SERVER_IP

Step 1: Configuring WireGuard interface...
  - WireGuard interface created
Step 2: Adding OrcheNet server as WireGuard peer...
  - Server peer added
Step 3: Assigning IP address to WireGuard interface...
  - IP address assigned: 10.99.0.2/32
Step 4: Adding route to OrcheNet network...
  - Route added
Step 5: Creating SSH user for OrcheNet...
  - User 'orchenet' created
  ! IMPORTANT: Change the password immediately!
Step 6: Enabling SSH service...
  - SSH service enabled on port 22
Step 7: Configuring firewall for OrcheNet access...
  - Firewall rule added
Step 8: Creating check-in script...
  - Check-in script created
Step 9: Scheduling automatic check-ins...
  - Scheduler created (5 minute interval)
Step 10: Testing WireGuard connection...
  - WireGuard interface is UP
  - Ping to OrcheNet server successful

===== Provisioning Complete =====
```

### Step 5: Change Default Password

**CRITICAL SECURITY STEP:**

```routeros
/user set orchenet password=YOUR_STRONG_PASSWORD_HERE
```

### Step 6: Verify Connection

**On Router:**
```routeros
# Check WireGuard status
/interface wireguard peers print

# Should show active connection with recent tx/rx
# Look for "last-handshake" field

# Test ping to server
/ping 10.99.0.1 count=5
```

**On Server:**
```bash
# Check WireGuard peers
sudo wg show wg0

# Should show router's public key and recent handshake

# Test SSH to router
ssh orchenet@10.99.0.2
```

**In Web Interface:**
1. Refresh **Devices** page
2. Router should show **Status: Online** (green)
3. **Last Check-in** should be within last 5 minutes
4. Click device name to see details
5. **WireGuard** tab should show connection status

### Step 7: Test Configuration Deployment

Test that you can manage the router via OrcheNet:

1. In web interface, click on device
2. Go to **Configuration** tab
3. Add simple test configuration:

```yaml
system:
  identity: Site-A-Router-Managed-By-OrcheNet
```

4. Click **Deploy Configuration**
5. Watch task status - should complete successfully
6. On router, verify: `/system identity print`

### Step 8: Test Web CLI

1. In web interface, click on device
2. Go to **CLI** tab
3. You should see a terminal interface
4. Type commands:
   ```
   /system resource print
   /interface print
   ```
5. Should see live output from router

## Architecture

### Component Overview

#### Backend (FastAPI + Python)
- **Location**: `/opt/orchenet/backend`
- **Port**: 8000 (internal)
- **Database**: SQLite at `/opt/orchenet/data/orchenet.db`
- **Service**: `orchenet-backend.service`
- **Logs**: `journalctl -u orchenet-backend -f`

**Key Features:**
- REST API for device/task management
- WireGuard peer management
- WebSocket for web CLI
- Configuration translation (YAML → RouterOS commands)
- SSH connection management
- Background task processor

#### Frontend (React + Vite)
- **Location**: `/opt/orchenet/frontend/dist`
- **Access**: Via Nginx on port 80/443
- **Framework**: React 18 with Vite build system

**Key Features:**
- Device management interface
- Configuration editor (YAML)
- Task monitoring
- Web-based CLI terminal
- Real-time status updates

#### WireGuard VPN Server
- **Interface**: wg0
- **Config**: `/etc/wireguard/wg0.conf`
- **Service**: `wg-quick@wg0.service`
- **Port**: 51820/udp
- **Network**: 10.99.0.0/24

**Purpose:**
- Secure connection to managed devices
- No public IP required on devices
- Encrypted management traffic
- Firewall-friendly (single UDP port outbound)

#### Nginx Reverse Proxy
- **Config**: `/etc/nginx/sites-available/orchenet`
- **Service**: `nginx.service`
- **Ports**: 80 (HTTP), 443 (HTTPS)

**Routes:**
- `/` → Frontend (static files)
- `/api/*` → Backend API
- `/api/webcli/ws/*` → WebSocket for CLI

### Data Flow

#### Device Check-In
```
1. MikroTik runs check-in script every 5 minutes
2. Script sends HTTP POST to /api/checkin via WireGuard VPN
3. Backend responds with pending tasks (if any)
4. Device records check-in timestamp
5. Web interface shows device as "Online"
```

#### Configuration Deployment
```
1. User edits YAML config in web interface
2. User clicks "Deploy Configuration"
3. Backend creates task in database
4. Device checks in and receives task
5. Backend connects to device via SSH (over VPN)
6. Backend translates YAML → RouterOS commands
7. Backend executes commands via SSH
8. Results saved to database
9. Web interface shows task completed
```

#### Web CLI Session
```
1. User clicks "CLI" button in web interface
2. Frontend opens WebSocket to /api/webcli/ws/{device_id}
3. Backend establishes SSH connection to device (over VPN)
4. User input sent via WebSocket → SSH
5. SSH output sent back via WebSocket → Browser
6. Terminal rendered in browser
```

### File Structure

```
/opt/orchenet/
├── backend/              # Python FastAPI application
│   ├── app/
│   │   ├── models/       # Database models
│   │   ├── routers/      # API endpoints
│   │   ├── services/     # Business logic
│   │   ├── vendors/      # Vendor translators
│   │   └── main.py       # Application entry point
│   ├── requirements.txt  # Python dependencies
│   └── init_db.py        # Database initialization
├── frontend/             # React application
│   ├── dist/             # Built files (served by Nginx)
│   └── src/              # Source code
├── agent/                # Device agent (future use)
├── device-scripts/       # Provisioning scripts
│   └── mikrotik/
│       ├── generate-provision-script.py
│       ├── provision-orchenet.rsc
│       └── README-WIREGUARD.md
├── data/                 # Application data
│   ├── orchenet.db       # SQLite database
│   ├── wg-server-private.key
│   └── wg-server-public.key
├── logs/                 # Application logs
├── venv/                 # Python virtual environment
└── *.sh                  # Management scripts
```

### Network Topology

```
Internet
    │
    ├─── Port 80/443 ────> Nginx ──> Frontend (static)
    │                         │
    │                         └────> Backend API (:8000)
    │
    └─── Port 51820/udp ──> WireGuard Server (10.99.0.1)
                                │
                                ├─> Device 1 (10.99.0.2)
                                ├─> Device 2 (10.99.0.3)
                                └─> Device 3 (10.99.0.4)
```

All management traffic (HTTP API, SSH) flows through WireGuard VPN.

## Troubleshooting

### Services Not Starting

**Check service status:**
```bash
systemctl status orchenet-backend
systemctl status wg-quick@wg0
systemctl status nginx
```

**View logs:**
```bash
# Backend logs
journalctl -u orchenet-backend -n 100 --no-pager

# WireGuard logs
journalctl -u wg-quick@wg0 -n 50 --no-pager

# Nginx logs
tail -n 100 /var/log/nginx/error.log
```

**Common issues:**
- **Port already in use**: Check if another service is using port 8000
- **Permission denied**: Ensure `orchenet` user has correct permissions
- **Module not found**: Reinstall Python dependencies

### Cannot Access Web Interface

**Check Nginx:**
```bash
nginx -t  # Test configuration
systemctl status nginx
tail -f /var/log/nginx/access.log
```

**Check firewall:**
```bash
ufw status
# Ensure port 80 is allowed
```

**Test backend directly:**
```bash
curl http://localhost:8000/health
# Should return {"status": "healthy"}
```

### Router Not Connecting via WireGuard

**On Server:**
```bash
# Check WireGuard is running
systemctl status wg-quick@wg0

# Show peers
sudo wg show wg0

# Check firewall
ufw status | grep 51820
```

**On Router:**
```routeros
# Check WireGuard interface
/interface wireguard print

# Check peer status
/interface wireguard peers print

# Test connectivity
/ping 10.99.0.1
```

**Common issues:**
- ISP blocks UDP 51820: Try different port
- Incorrect endpoint IP: Verify server public IP
- Keys mismatch: Regenerate and re-provision
- Firewall blocking: Check UFW on server

### Device Not Appearing in OrcheNet

**Check on Router:**
```routeros
# Run check-in manually
/system script run orchenet-checkin

# Check logs
/log print where topics~"script"
```

**Check on Server:**
```bash
# View backend logs
journalctl -u orchenet-backend -f

# Check database
sqlite3 /opt/orchenet/data/orchenet.db "SELECT * FROM devices;"
```

**Common issues:**
- Check-in script not running: Verify scheduler
- Network connectivity: Can router reach 10.99.0.1?
- API URL incorrect in script
- Backend not processing requests

### SSH Not Working Over VPN

```bash
# From server
ssh -v orchenet@10.99.0.2
```

**On Router:**
```routeros
# Check SSH service
/ip service print

# Check firewall
/ip firewall filter print where chain=input

# Check user
/user print
```

**Common issues:**
- SSH not enabled: `/ip service enable ssh`
- Firewall blocking: Check rule exists for VPN subnet
- Wrong credentials: Verify password or SSH key

### Web CLI Not Working

**In browser console (F12):**
- Check for WebSocket connection errors
- Verify `/api/webcli/ws/1` is connecting

**On server:**
```bash
# Check backend logs
journalctl -u orchenet-backend -f

# Test SSH manually
ssh orchenet@DEVICE_VPN_IP
```

**Common issues:**
- WebSocket not connecting: Check Nginx WebSocket proxy configuration
- SSH credentials missing: Configure in device settings
- Device offline: Check WireGuard connection

## Maintenance

### Regular Tasks

**Daily:**
- Check service status: `/opt/orchenet/status.sh`
- Review logs for errors: `journalctl -u orchenet-backend -since today`

**Weekly:**
- Check disk space: `df -h`
- Review device check-in times
- Verify WireGuard connections: `sudo wg show wg0`

**Monthly:**
- Update system packages: `apt-get update && apt-get upgrade`
- Backup database (see below)
- Review and rotate logs
- Update OrcheNet (when new version available)

### Backup and Restore

**Backup Database:**
```bash
# Stop backend
systemctl stop orchenet-backend

# Backup database
sqlite3 /opt/orchenet/data/orchenet.db ".backup '/root/orchenet-backup-$(date +%Y%m%d).db'"

# Or simple copy
cp /opt/orchenet/data/orchenet.db /root/orchenet-backup-$(date +%Y%m%d).db

# Backup WireGuard keys
cp /opt/orchenet/data/wg-*.key /root/

# Start backend
systemctl start orchenet-backend
```

**Restore Database:**
```bash
systemctl stop orchenet-backend
cp /root/orchenet-backup-YYYYMMDD.db /opt/orchenet/data/orchenet.db
chown orchenet:orchenet /opt/orchenet/data/orchenet.db
systemctl start orchenet-backend
```

**Automated Backup Script:**
```bash
cat > /opt/orchenet/backup.sh <<'EOF'
#!/bin/bash
BACKUP_DIR="/root/orchenet-backups"
DATE=$(date +%Y%m%d-%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
sqlite3 /opt/orchenet/data/orchenet.db ".backup '$BACKUP_DIR/orchenet-$DATE.db'"

# Backup WireGuard config
cp /etc/wireguard/wg0.conf $BACKUP_DIR/wg0-$DATE.conf
cp /opt/orchenet/data/wg-*.key $BACKUP_DIR/

# Keep only last 7 days
find $BACKUP_DIR -name "orchenet-*.db" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/orchenet-$DATE.db"
EOF

chmod +x /opt/orchenet/backup.sh

# Add to crontab
echo "0 2 * * * /opt/orchenet/backup.sh" | crontab -
```

### Log Management

**View logs:**
```bash
# Backend logs
journalctl -u orchenet-backend -f

# All logs today
journalctl -u orchenet-backend -since today

# Last 100 lines
journalctl -u orchenet-backend -n 100 --no-pager

# Errors only
journalctl -u orchenet-backend -p err
```

**Rotate logs:**
```bash
# Configure log rotation
cat > /etc/logrotate.d/orchenet <<EOF
/opt/orchenet/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
EOF
```

### Updating OrcheNet

When a new version is released:

```bash
# Backup first!
/opt/orchenet/backup.sh

# Pull latest code
cd /root/orchenet
git pull

# Update Python dependencies
sudo -u orchenet /opt/orchenet/venv/bin/pip install -r backend/requirements.txt

# Rebuild frontend
cd /opt/orchenet/frontend
sudo -u orchenet npm install
sudo -u orchenet npm run build

# Restart services
systemctl restart orchenet-backend
systemctl restart nginx

# Check status
/opt/orchenet/status.sh
```

## Security Considerations

### Essential Security Measures

1. **Change Default Passwords**
   - Change `orchenet` user password on all routers
   - Use strong, unique passwords (20+ characters)

2. **Use SSH Keys**
   ```bash
   # Generate key on server
   ssh-keygen -t ed25519 -C "orchenet"

   # Copy to router
   ssh-copy-id orchenet@10.99.0.2
   ```

3. **Enable HTTPS**
   - Use Let's Encrypt for free SSL certificates
   - Force HTTPS redirects in Nginx

4. **Firewall Configuration**
   - Only open necessary ports
   - Restrict SSH to specific IPs if possible

5. **Keep System Updated**
   ```bash
   apt-get update && apt-get upgrade -y
   ```

6. **Regular Backups**
   - Automate database backups
   - Store backups off-server

7. **Monitor Logs**
   - Review logs regularly for suspicious activity
   - Set up alerts for repeated login failures

### Advanced Security

**Enable Authentication (Future Feature)**
- API key authentication for devices
- User authentication for web interface
- Role-based access control

**VPN Security**
- Rotate WireGuard keys periodically
- Use different VPN subnets for different sites
- Implement network segmentation

**Audit Logging**
- Enable detailed logging of all configuration changes
- Log all CLI access
- Store audit logs separately

**Network Security**
- Place OrcheNet server in DMZ
- Use VLANs to isolate management traffic
- Implement intrusion detection (fail2ban)

## Migration from SQLite to PostgreSQL (Optional)

For production at scale, consider PostgreSQL:

```bash
# Install PostgreSQL
apt-get install -y postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql <<EOF
CREATE DATABASE orchenet;
CREATE USER orchenet WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE orchenet TO orchenet;
EOF

# Update .env
echo "DATABASE_URL=postgresql://orchenet:secure_password@localhost/orchenet" >> /opt/orchenet/backend/.env

# Install PostgreSQL driver
sudo -u orchenet /opt/orchenet/venv/bin/pip install psycopg2-binary

# Migrate data (use alembic or custom script)

# Restart backend
systemctl restart orchenet-backend
```

## Support and Resources

- **Documentation**: `/opt/orchenet/README.md`
- **MikroTik Guide**: `/opt/orchenet/device-scripts/mikrotik/README-WIREGUARD.md`
- **Logs**: `journalctl -u orchenet-backend -f`
- **Status**: `/opt/orchenet/status.sh`

## Summary of Commands

```bash
# Installation
./deploy/install.sh

# Service management
systemctl status orchenet-backend
systemctl restart orchenet-backend
systemctl stop orchenet-backend

# View logs
journalctl -u orchenet-backend -f
/opt/orchenet/logs.sh

# Check status
/opt/orchenet/status.sh

# WireGuard management
sudo wg show wg0
systemctl status wg-quick@wg0

# Backup
/opt/orchenet/backup.sh

# Provision device
cd /opt/orchenet/device-scripts/mikrotik
python3 generate-provision-script.py --device-id 1 --server http://SERVER_IP:8000 --server-ip SERVER_IP
```

## Next Steps

After successful installation:

1. ✓ Access web interface
2. ✓ Add first MikroTik device
3. ✓ Provision device with generated script
4. ✓ Verify device appears online
5. ✓ Test configuration deployment
6. ✓ Test web CLI access
7. Configure HTTPS with SSL certificate
8. Set up automated backups
9. Add more devices
10. Explore advanced features

---

**Congratulations!** You now have a fully functional OrcheNet installation managing your MikroTik network infrastructure via secure WireGuard VPN.
