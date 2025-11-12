# Installation Recovery Guide

If installation fails partway through, here's how to recover and continue.

## Your Current Situation

Installation failed at Step 6 due to missing `sudo` command in minimal Proxmox container.

## Quick Recovery Steps

### Option 1: Install sudo and Continue Manually

```bash
# 1. Install sudo (as root)
apt-get install -y sudo procps

# 2. Continue with the specific failed steps
# Since the user and files are already created, just do:

# Create Python virtual environment
su - orchenet -c "python3 -m venv /opt/orchenet/venv"

# Install Python dependencies
su - orchenet -c "/opt/orchenet/venv/bin/pip install --upgrade pip"
su - orchenet -c "/opt/orchenet/venv/bin/pip install -r /opt/orchenet/backend/requirements.txt"

# Build frontend
cd /opt/orchenet/frontend
su - orchenet -c "cd /opt/orchenet/frontend && npm install && npm run build"

# Initialize database
cd /opt/orchenet/backend
su - orchenet -c "/opt/orchenet/venv/bin/python /opt/orchenet/backend/init_db.py"

# Setup WireGuard (as root)
WG_SERVER_PRIVATE_KEY=$(wg genkey)
WG_SERVER_PUBLIC_KEY=$(echo "$WG_SERVER_PRIVATE_KEY" | wg pubkey)

cat > /etc/wireguard/wg0.conf <<EOF
[Interface]
PrivateKey = $WG_SERVER_PRIVATE_KEY
Address = 10.99.0.1/24
ListenPort = 51820
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE
EOF

chmod 600 /etc/wireguard/wg0.conf

# Save keys
echo "$WG_SERVER_PRIVATE_KEY" > /opt/orchenet/data/wg-server-private.key
echo "$WG_SERVER_PUBLIC_KEY" > /opt/orchenet/data/wg-server-public.key
chmod 600 /opt/orchenet/data/wg-server-private.key
chmod 644 /opt/orchenet/data/wg-server-public.key
chown orchenet:orchenet /opt/orchenet/data/wg-server-*.key

echo "WireGuard Public Key: $WG_SERVER_PUBLIC_KEY"

# Enable WireGuard
systemctl enable wg-quick@wg0
systemctl start wg-quick@wg0

# Create backend service
cat > /etc/systemd/system/orchenet-backend.service <<EOF
[Unit]
Description=OrcheNet Backend API Server
After=network.target

[Service]
Type=simple
User=orchenet
Group=orchenet
WorkingDirectory=/opt/orchenet/backend
Environment="PATH=/opt/orchenet/venv/bin"
ExecStart=/opt/orchenet/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx
SERVER_IP=$(curl -s ifconfig.me || echo "localhost")

cat > /etc/nginx/sites-available/orchenet <<EOF
server {
    listen 80;
    server_name _;

    location / {
        root /opt/orchenet/frontend/dist;
        try_files \$uri \$uri/ /index.html;
    }

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }

    location /api/webcli/ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_read_timeout 86400;
    }
}
EOF

ln -sf /etc/nginx/sites-available/orchenet /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

nginx -t
systemctl enable nginx
systemctl restart nginx

# Start services
systemctl daemon-reload
systemctl enable orchenet-backend
systemctl start orchenet-backend

# Check status
systemctl status orchenet-backend
systemctl status wg-quick@wg0
systemctl status nginx

echo ""
echo "Installation complete!"
echo "Access web interface at: http://$SERVER_IP"
```

### Option 2: Clean Start with Fixed Script

```bash
# 1. Stop any running services
systemctl stop orchenet-backend 2>/dev/null || true
systemctl stop wg-quick@wg0 2>/dev/null || true

# 2. Remove partial installation
rm -rf /opt/orchenet
userdel -r orchenet 2>/dev/null || true
rm -f /etc/systemd/system/orchenet-backend.service
rm -f /etc/nginx/sites-enabled/orchenet
rm -f /etc/nginx/sites-available/orchenet
rm -rf /etc/wireguard/wg0.conf

# 3. Install sudo
apt-get install -y sudo procps

# 4. Pull updated script from git
cd /root/orchenet
git pull

# 5. Re-run installation
cd deploy
./install.sh
```

### Option 3: Use Pre-Install Script First

```bash
# 1. Run pre-install script for minimal containers
cd /root/orchenet/deploy
chmod +x pre-install.sh
./pre-install.sh

# 2. Then run main install
./install.sh
```

## Verify Installation

After completing any option above:

```bash
# Check all services
systemctl status orchenet-backend
systemctl status wg-quick@wg0
systemctl status nginx

# Test backend
curl http://localhost:8000/health

# Check if you can access web interface
curl -I http://localhost
```

## Common Issues in Minimal Containers

### Missing sudo
```bash
apt-get install -y sudo
```

### Missing /etc/sysctl.conf
```bash
touch /etc/sysctl.conf
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
sysctl -p
```

### Missing basic commands (ps, netstat, etc.)
```bash
apt-get install -y procps net-tools
```

### Missing ca-certificates (for HTTPS)
```bash
apt-get install -y ca-certificates apt-transport-https
```

## If All Else Fails: Manual Installation

See the manual steps in this file above under "Option 1" - they can be run one by one to see exactly where any issue occurs.
