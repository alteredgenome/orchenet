# OrcheNet Installation Commands

**Complete command sequence to deploy OrcheNet on a fresh Debian 13 server**

Copy and paste these commands in order on your Debian 13 server.

## Prerequisites

- Fresh Debian 13 server
- Root access (or sudo privileges)
- Internet connection
- Public IP address noted

## Step-by-Step Installation

### 1. Login as Root

```bash
ssh root@your-server-ip
```

Or if using sudo:
```bash
ssh your-user@your-server-ip
sudo -i
```

### 2. Update System

```bash
apt-get update
apt-get upgrade -y
```

### 3. Install Git

```bash
apt-get install -y git
```

### 4. Clone OrcheNet Repository

```bash
cd /root
git clone https://github.com/yourusername/orchenet.git
cd orchenet
```

**Note**: Replace `yourusername/orchenet` with the actual repository URL.

### 5. Run Installation Script

```bash
cd deploy
chmod +x install.sh
./install.sh
```

**This will take 5-10 minutes and will:**
- Install Python, Node.js, WireGuard, Nginx, etc.
- Create system user `orchenet`
- Set up Python virtual environment
- Build frontend
- Initialize database
- Configure WireGuard VPN server
- Create systemd services
- Configure Nginx

**Important**: Note the WireGuard server public key displayed at the end!

### 6. Verify Installation

```bash
/opt/orchenet/status.sh
```

Expected output:
```
===== OrcheNet Status =====

Backend Service:
   Active: active (running) since ...

WireGuard Status:
   Active: active (running) since ...
interface: wg0
  public key: ...
  private key: (hidden)
  listening port: 51820

Nginx Status:
   Active: active (running) since ...

Connected Peers:
0
```

### 7. Get Server IP

```bash
curl ifconfig.me
```

Note this IP address - you'll need it for:
- Accessing web interface
- Configuring WireGuard endpoint on devices

### 8. Access Web Interface

Open browser to: `http://YOUR_SERVER_IP`

You should see the OrcheNet dashboard.

---

## Add First MikroTik Device

### 9. Add Device in Web Interface

1. Open `http://YOUR_SERVER_IP` in browser
2. Click **"Devices"** → **"Add Device"**
3. Fill in:
   - Name: `Router-1`
   - Vendor: `MikroTik`
   - Model: (optional, e.g., `RB4011`)
4. Click **"Add Device"**
5. **Note the Device ID** (shown in list or URL, e.g., `1`)

### 10. Generate Provisioning Script

Back on server terminal:

```bash
cd /opt/orchenet/device-scripts/mikrotik

# Replace YOUR_SERVER_IP with actual IP from step 7
# Replace 1 with actual Device ID from step 9
python3 generate-provision-script.py \
    --device-id 1 \
    --server http://YOUR_SERVER_IP:8000 \
    --server-ip YOUR_SERVER_IP \
    --output provision-router-1.rsc
```

**Output will show:**
```
✓ Server Public Key: ...
✓ Assigned VPN IP: 10.99.0.2
✓ Provisioning script generated: provision-router-1.rsc
```

### 11. Copy Script to MikroTik Router

**Option A: Using SCP**

```bash
scp provision-router-1.rsc admin@ROUTER_IP:
```

Replace `ROUTER_IP` with your router's IP address.

**Option B: Using Winbox**

1. Open Winbox on your Windows/Mac
2. Connect to router
3. Go to **Files** menu
4. Drag and drop `provision-router-1.rsc` file

### 12. Apply Script to Router

Connect to router terminal (Winbox, SSH, or WebFig) and run:

```routeros
/import provision-router-1.rsc
```

Watch for successful completion messages.

### 13. Change SSH Password (CRITICAL!)

On router, immediately run:

```routeros
/user set orchenet password=YourStrongPasswordHere123!@#
```

**Use a strong password!** This account has full admin access.

### 14. Verify Connection

**On Router:**
```routeros
/interface wireguard peers print
/ping 10.99.0.1 count=5
```

**On Server:**
```bash
sudo wg show wg0
ssh orchenet@10.99.0.2
```

**In Web Interface:**
- Refresh page
- Router should show **Status: Online**
- Last check-in < 5 minutes

---

## Optional: Configure HTTPS

### 15. Install Certbot

```bash
apt-get install -y certbot python3-certbot-nginx
```

### 16. Get SSL Certificate

```bash
# Replace with your domain
certbot --nginx -d orchenet.yourdomain.com
```

Follow prompts to configure HTTPS.

### 17. Update Nginx Config

```bash
nano /etc/nginx/sites-available/orchenet
```

Change line:
```
server_name _;
```

To:
```
server_name orchenet.yourdomain.com;
```

Save and restart:
```bash
systemctl restart nginx
```

---

## Optional: Configure Firewall

### 18. Install and Configure UFW

```bash
apt-get install -y ufw

# Allow SSH first (IMPORTANT!)
ufw allow 22/tcp

# Allow HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Allow WireGuard
ufw allow 51820/udp

# Enable firewall
ufw enable

# Verify
ufw status
```

---

## Optional: Set Up Automated Backups

### 19. Create Backup Script

```bash
cat > /opt/orchenet/backup.sh <<'EOF'
#!/bin/bash
BACKUP_DIR="/root/orchenet-backups"
DATE=$(date +%Y%m%d-%H%M%S)
mkdir -p $BACKUP_DIR
sqlite3 /opt/orchenet/data/orchenet.db ".backup '$BACKUP_DIR/orchenet-$DATE.db'"
cp /etc/wireguard/wg0.conf $BACKUP_DIR/wg0-$DATE.conf
cp /opt/orchenet/data/wg-*.key $BACKUP_DIR/
find $BACKUP_DIR -name "orchenet-*.db" -mtime +7 -delete
echo "Backup completed: $BACKUP_DIR/orchenet-$DATE.db"
EOF

chmod +x /opt/orchenet/backup.sh
```

### 20. Schedule Daily Backups

```bash
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/orchenet/backup.sh") | crontab -
```

Backups will run daily at 2 AM, keeping last 7 days.

---

## Management Commands Reference

### View Status

```bash
/opt/orchenet/status.sh
```

### View Logs

```bash
/opt/orchenet/logs.sh
# or
journalctl -u orchenet-backend -f
```

### Restart Services

```bash
/opt/orchenet/restart.sh
# or
systemctl restart orchenet-backend
systemctl restart nginx
```

### Check WireGuard Peers

```bash
sudo wg show wg0
```

### Backup Database

```bash
/opt/orchenet/backup.sh
```

### Update System

```bash
apt-get update && apt-get upgrade -y
```

---

## Add Additional Devices

For each additional MikroTik router:

```bash
# 1. Add device in web interface, note new Device ID

# 2. Generate provisioning script
cd /opt/orchenet/device-scripts/mikrotik
python3 generate-provision-script.py \
    --device-id NEW_DEVICE_ID \
    --server http://YOUR_SERVER_IP:8000 \
    --server-ip YOUR_SERVER_IP \
    --output provision-router-N.rsc

# 3. Copy to router and import
scp provision-router-N.rsc admin@ROUTER_IP:

# 4. On router terminal:
# /import provision-router-N.rsc
# /user set orchenet password=StrongPassword
```

Each device gets unique VPN IP: 10.99.0.2, 10.99.0.3, 10.99.0.4, etc.

---

## Troubleshooting Commands

### Service Not Running

```bash
systemctl status orchenet-backend
journalctl -u orchenet-backend -n 100 --no-pager
```

### Can't Access Web Interface

```bash
nginx -t
systemctl status nginx
curl http://localhost:8000/health
```

### WireGuard Issues

```bash
systemctl status wg-quick@wg0
sudo wg show wg0
journalctl -u wg-quick@wg0 -n 50
```

### Router Not Connecting

**On Server:**
```bash
sudo wg show wg0
journalctl -u orchenet-backend -f
```

**On Router:**
```routeros
/interface wireguard peers print
/ping 10.99.0.1
/log print where topics~"script"
```

### Database Issues

```bash
sqlite3 /opt/orchenet/data/orchenet.db "SELECT * FROM devices;"
sqlite3 /opt/orchenet/data/orchenet.db ".schema"
```

---

## Important File Locations

```
/opt/orchenet/                           # Installation directory
├── backend/                             # Python backend
│   └── app/
├── frontend/dist/                       # Web interface
├── data/
│   ├── orchenet.db                      # SQLite database
│   ├── wg-server-private.key           # WireGuard keys
│   └── wg-server-public.key
├── logs/                                # Application logs
├── device-scripts/mikrotik/            # Provisioning scripts
└── venv/                                # Python virtual environment

/etc/wireguard/wg0.conf                  # WireGuard configuration
/etc/nginx/sites-available/orchenet      # Nginx configuration
/etc/systemd/system/orchenet-backend.service  # Systemd service
```

---

## Default Settings

- **Web Interface**: `http://SERVER_IP:80`
- **API Endpoint**: `http://SERVER_IP:8000` (internal)
- **WireGuard Port**: `51820/udp`
- **VPN Network**: `10.99.0.0/24`
- **Server VPN IP**: `10.99.0.1`
- **Device VPN IPs**: `10.99.0.2`, `10.99.0.3`, ...
- **SSH User on Devices**: `orchenet`
- **Check-in Interval**: 5 minutes

---

## Security Checklist

After installation, ensure you:

- [ ] Changed SSH password on all routers
- [ ] Configured HTTPS with SSL certificate (Let's Encrypt)
- [ ] Enabled and configured firewall (UFW)
- [ ] Set up automated backups
- [ ] Used strong passwords (20+ characters)
- [ ] Restricted SSH access to VPN subnet only
- [ ] Reviewed logs for any errors or warnings
- [ ] Tested configuration deployment
- [ ] Tested web CLI access
- [ ] Documented your server IP and WireGuard keys

---

## Quick Reference Card

```bash
# Service Management
systemctl status orchenet-backend    # Check backend status
systemctl restart orchenet-backend   # Restart backend
systemctl status wg-quick@wg0        # Check WireGuard
systemctl restart wg-quick@wg0       # Restart WireGuard

# Logs
journalctl -u orchenet-backend -f    # Follow backend logs
journalctl -u orchenet-backend -since today  # Today's logs
tail -f /var/log/nginx/access.log    # Nginx access logs

# WireGuard
sudo wg show wg0                     # Show all peers
sudo wg show wg0 peers               # List peer public keys

# Database
sqlite3 /opt/orchenet/data/orchenet.db "SELECT * FROM devices;"  # List devices
sqlite3 /opt/orchenet/data/orchenet.db ".backup '/root/backup.db'"  # Backup

# Files
ls -la /opt/orchenet/                # Installation files
ls -la /etc/wireguard/               # WireGuard configs
ls -la /etc/nginx/sites-available/   # Nginx configs

# Network
curl ifconfig.me                     # Get public IP
ss -tulpn | grep :8000              # Check port 8000
ss -tulpn | grep :51820             # Check WireGuard port

# System
df -h                                # Disk space
free -h                              # Memory usage
top                                  # Process monitor
```

---

## Support

For issues:

1. Check service status: `systemctl status orchenet-backend`
2. Check logs: `journalctl -u orchenet-backend -since today`
3. Review installation log: `cat /var/log/orchenet-install.log`
4. Check this documentation: `DEPLOYMENT.md`
5. Verify network connectivity: `ping 10.99.0.1`

---

**Installation Complete!**

Your OrcheNet server is now ready to manage MikroTik routers via secure WireGuard VPN.

Access your dashboard at: `http://YOUR_SERVER_IP`

For detailed documentation, see `DEPLOYMENT.md`.
