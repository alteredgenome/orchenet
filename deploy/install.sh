#!/bin/bash
###############################################################################
# OrcheNet Installation Script for Debian 13
# This script installs and configures OrcheNet on a fresh Debian server
###############################################################################

set -e  # Exit on any error

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/orchenet"
VENV_DIR="$INSTALL_DIR/venv"
USER="orchenet"
GROUP="orchenet"
WIREGUARD_INTERFACE="wg0"
WIREGUARD_SUBNET="10.99.0.0/24"
WIREGUARD_SERVER_IP="10.99.0.1"
WIREGUARD_PORT="51820"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}OrcheNet Installation Script${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: This script must be run as root${NC}"
    echo "Please run: sudo bash install.sh"
    exit 1
fi

# Update system
echo -e "${YELLOW}Step 1: Updating system packages...${NC}"
apt-get update
apt-get upgrade -y

# Install system dependencies
echo -e "${YELLOW}Step 2: Installing system dependencies...${NC}"
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    git \
    wireguard \
    wireguard-tools \
    iptables \
    nodejs \
    npm \
    nginx \
    sqlite3 \
    curl \
    wget \
    sudo \
    procps

# Enable IP forwarding for WireGuard
echo -e "${YELLOW}Step 3: Configuring IP forwarding...${NC}"
# Create sysctl.conf if it doesn't exist
touch /etc/sysctl.conf
if ! grep -q "net.ipv4.ip_forward=1" /etc/sysctl.conf; then
    echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
    sysctl -p
    echo -e "${GREEN}✓ IP forwarding enabled${NC}"
else
    echo -e "${GREEN}✓ IP forwarding already enabled${NC}"
fi

# Create orchenet user
echo -e "${YELLOW}Step 4: Creating orchenet user...${NC}"
if ! id -u $USER > /dev/null 2>&1; then
    useradd -r -s /bin/bash -d $INSTALL_DIR -m $USER
    echo -e "${GREEN}✓ User $USER created${NC}"
else
    echo -e "${GREEN}✓ User $USER already exists${NC}"
fi

# Setup application files
echo -e "${YELLOW}Step 5: Setting up application files...${NC}"

# Determine source directory (where this script is run from)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Source directory: $SCRIPT_DIR"
echo "Install directory: $INSTALL_DIR"

# Check if we're already in the install directory
if [ "$SCRIPT_DIR" = "$INSTALL_DIR" ]; then
    echo -e "${GREEN}✓ Already in install directory, skipping copy${NC}"
else
    # Different location, need to copy
    if [ ! -d "$INSTALL_DIR" ]; then
        mkdir -p $INSTALL_DIR
    fi

    echo "Copying files from: $SCRIPT_DIR"
    echo "Installing to: $INSTALL_DIR"

    # Copy backend
    cp -r "$SCRIPT_DIR/backend" "$INSTALL_DIR/"
    # Copy frontend
    cp -r "$SCRIPT_DIR/frontend" "$INSTALL_DIR/"
    # Copy agent
    cp -r "$SCRIPT_DIR/agent" "$INSTALL_DIR/"
    # Copy device scripts
    cp -r "$SCRIPT_DIR/device-scripts" "$INSTALL_DIR/"
    # Copy deploy scripts
    cp -r "$SCRIPT_DIR/deploy" "$INSTALL_DIR/"
    # Copy documentation
    cp "$SCRIPT_DIR/README.md" "$INSTALL_DIR/" 2>/dev/null || true
    cp "$SCRIPT_DIR/CLAUDE.md" "$INSTALL_DIR/" 2>/dev/null || true

    echo -e "${GREEN}✓ Application files copied${NC}"
fi

# Create necessary directories
mkdir -p "$INSTALL_DIR/logs"
mkdir -p "$INSTALL_DIR/data"
mkdir -p "/etc/wireguard"

# Set permissions
chown -R $USER:$GROUP $INSTALL_DIR
chmod -R 755 $INSTALL_DIR

echo -e "${GREEN}✓ Application files ready${NC}"

# Create Python virtual environment
echo -e "${YELLOW}Step 6: Creating Python virtual environment...${NC}"
sudo -u $USER python3 -m venv $VENV_DIR
echo -e "${GREEN}✓ Virtual environment created${NC}"

# Install Python dependencies
echo -e "${YELLOW}Step 7: Installing Python dependencies...${NC}"
sudo -u $USER $VENV_DIR/bin/pip install --upgrade pip
sudo -u $USER $VENV_DIR/bin/pip install -r "$INSTALL_DIR/backend/requirements.txt"
echo -e "${GREEN}✓ Python dependencies installed${NC}"

# Install Node.js dependencies and build frontend
echo -e "${YELLOW}Step 8: Building frontend...${NC}"
cd "$INSTALL_DIR/frontend"
sudo -u $USER npm install
sudo -u $USER npm run build
echo -e "${GREEN}✓ Frontend built${NC}"

# Initialize database
echo -e "${YELLOW}Step 9: Initializing database...${NC}"

# Ensure data directory has proper permissions for orchenet user
chown $USER:$GROUP "$INSTALL_DIR/data"
chmod 775 "$INSTALL_DIR/data"

cd "$INSTALL_DIR/backend"
sudo -u $USER $VENV_DIR/bin/python init_db.py

# Set proper permissions on database file (if created)
if [ -f "$INSTALL_DIR/data/orchenet.db" ]; then
    chown $USER:$GROUP "$INSTALL_DIR/data/orchenet.db"
    chmod 664 "$INSTALL_DIR/data/orchenet.db"
    echo -e "${GREEN}✓ Database permissions set${NC}"
fi

echo -e "${GREEN}✓ Database initialized${NC}"

# Setup WireGuard server
echo -e "${YELLOW}Step 10: Setting up WireGuard VPN server...${NC}"

# Generate WireGuard server keys
WG_SERVER_PRIVATE_KEY=$(wg genkey)
WG_SERVER_PUBLIC_KEY=$(echo "$WG_SERVER_PRIVATE_KEY" | wg pubkey)

# Create WireGuard configuration
cat > /etc/wireguard/$WIREGUARD_INTERFACE.conf <<EOF
[Interface]
PrivateKey = $WG_SERVER_PRIVATE_KEY
Address = $WIREGUARD_SERVER_IP/24
ListenPort = $WIREGUARD_PORT
PostUp = iptables -A FORWARD -i $WIREGUARD_INTERFACE -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i $WIREGUARD_INTERFACE -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

# Peers will be added dynamically by OrcheNet

EOF

chmod 600 /etc/wireguard/$WIREGUARD_INTERFACE.conf

# Save WireGuard keys for later use
echo "$WG_SERVER_PRIVATE_KEY" > "$INSTALL_DIR/data/wg-server-private.key"
echo "$WG_SERVER_PUBLIC_KEY" > "$INSTALL_DIR/data/wg-server-public.key"
chmod 600 "$INSTALL_DIR/data/wg-server-private.key"
chmod 644 "$INSTALL_DIR/data/wg-server-public.key"
chown $USER:$GROUP "$INSTALL_DIR/data/wg-server-"*.key

echo -e "${GREEN}✓ WireGuard server configured${NC}"
echo -e "${GREEN}  Server Public Key: $WG_SERVER_PUBLIC_KEY${NC}"

# Enable and start WireGuard
systemctl enable wg-quick@$WIREGUARD_INTERFACE
systemctl start wg-quick@$WIREGUARD_INTERFACE

echo -e "${GREEN}✓ WireGuard service started${NC}"

# Create systemd service for backend
echo -e "${YELLOW}Step 11: Creating systemd services...${NC}"

cat > /etc/systemd/system/orchenet-backend.service <<EOF
[Unit]
Description=OrcheNet Backend API Server
After=network.target

[Service]
Type=simple
User=$USER
Group=$GROUP
WorkingDirectory=$INSTALL_DIR/backend
Environment="PATH=$VENV_DIR/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=$VENV_DIR/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✓ Backend service created${NC}"

# Configure Nginx as reverse proxy
echo -e "${YELLOW}Step 12: Configuring Nginx...${NC}"

# Get server's public IP
SERVER_IP=$(curl -s ifconfig.me || echo "YOUR_SERVER_IP")

cat > /etc/nginx/sites-available/orchenet <<EOF
server {
    listen 80;
    server_name _;

    # Frontend
    location / {
        root $INSTALL_DIR/frontend/dist;
        try_files \$uri \$uri/ /index.html;
    }

    # Backend API
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

    # WebSocket for CLI
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

# Enable site
ln -sf /etc/nginx/sites-available/orchenet /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test and reload Nginx
nginx -t
systemctl enable nginx
systemctl restart nginx

echo -e "${GREEN}✓ Nginx configured${NC}"

# Reload systemd and enable services
echo -e "${YELLOW}Step 13: Enabling services...${NC}"
systemctl daemon-reload
systemctl enable orchenet-backend
systemctl start orchenet-backend

echo -e "${GREEN}✓ Services enabled and started${NC}"

# Configure sudoers for WireGuard management
echo -e "${YELLOW}Step 14: Configuring sudoers for WireGuard...${NC}"
cat > /etc/sudoers.d/orchenet <<EOF
# Allow orchenet user to manage WireGuard without password
$USER ALL=(ALL) NOPASSWD: /usr/bin/wg
$USER ALL=(ALL) NOPASSWD: /usr/bin/wg-quick
$USER ALL=(ALL) NOPASSWD: /bin/systemctl restart wg-quick@*
$USER ALL=(ALL) NOPASSWD: /bin/systemctl reload wg-quick@*
$USER ALL=(ALL) NOPASSWD: /usr/bin/tee /etc/wireguard/*.conf
$USER ALL=(ALL) NOPASSWD: /bin/cat /etc/wireguard/*.conf
$USER ALL=(ALL) NOPASSWD: /bin/chmod * /etc/wireguard/*.conf
EOF

chmod 440 /etc/sudoers.d/orchenet
echo -e "${GREEN}✓ Sudoers configured for WireGuard management${NC}"

# Configure firewall (if ufw is installed)
if command -v ufw &> /dev/null; then
    echo -e "${YELLOW}Step 15: Configuring firewall...${NC}"
    ufw allow 80/tcp comment "HTTP"
    ufw allow 443/tcp comment "HTTPS"
    ufw allow $WIREGUARD_PORT/udp comment "WireGuard"
    ufw allow 22/tcp comment "SSH"
    echo -e "${GREEN}✓ Firewall rules configured${NC}"
else
    echo -e "${YELLOW}Note: ufw not installed, skipping firewall configuration${NC}"
fi

# Create convenience scripts
echo -e "${YELLOW}Step 16: Creating management scripts...${NC}"

# Status script
cat > $INSTALL_DIR/status.sh <<'EOF'
#!/bin/bash
echo "===== OrcheNet Status ====="
echo ""
echo "Backend Service:"
systemctl status orchenet-backend --no-pager | grep Active
echo ""
echo "WireGuard Status:"
systemctl status wg-quick@wg0 --no-pager | grep Active
wg show wg0 2>/dev/null | head -n 5 || echo "WireGuard not running"
echo ""
echo "Nginx Status:"
systemctl status nginx --no-pager | grep Active
echo ""
echo "Connected Peers:"
wg show wg0 peers 2>/dev/null | wc -l
EOF

chmod +x $INSTALL_DIR/status.sh

# Logs script
cat > $INSTALL_DIR/logs.sh <<'EOF'
#!/bin/bash
echo "Viewing OrcheNet logs (Ctrl+C to exit)..."
journalctl -u orchenet-backend -f
EOF

chmod +x $INSTALL_DIR/logs.sh

# Restart script
cat > $INSTALL_DIR/restart.sh <<'EOF'
#!/bin/bash
echo "Restarting OrcheNet services..."
systemctl restart orchenet-backend
systemctl restart nginx
echo "Services restarted"
EOF

chmod +x $INSTALL_DIR/restart.sh

chown $USER:$GROUP $INSTALL_DIR/*.sh

echo -e "${GREEN}✓ Management scripts created${NC}"

# Wait for backend to start
echo -e "${YELLOW}Waiting for backend to start...${NC}"
sleep 5

# Initialize WireGuard in OrcheNet database
echo -e "${YELLOW}Step 16: Initializing WireGuard in OrcheNet...${NC}"
curl -X POST http://127.0.0.1:8000/api/wireguard/setup \
    -H "Content-Type: application/json" \
    -d "{\"server_private_key\": \"$WG_SERVER_PRIVATE_KEY\"}" \
    2>/dev/null || echo "Note: WireGuard initialization will be done via web interface"

# Print completion message
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${GREEN}OrcheNet is now running!${NC}"
echo ""
echo "Access the web interface:"
echo -e "  ${GREEN}http://$SERVER_IP${NC}"
echo ""
echo "WireGuard VPN Server:"
echo -e "  ${GREEN}Public Key: $WG_SERVER_PUBLIC_KEY${NC}"
echo -e "  ${GREEN}Endpoint: $SERVER_IP:$WIREGUARD_PORT${NC}"
echo -e "  ${GREEN}VPN Network: $WIREGUARD_SUBNET${NC}"
echo ""
echo "Management commands:"
echo -e "  Status:  ${YELLOW}$INSTALL_DIR/status.sh${NC}"
echo -e "  Logs:    ${YELLOW}$INSTALL_DIR/logs.sh${NC}"
echo -e "  Restart: ${YELLOW}$INSTALL_DIR/restart.sh${NC}"
echo ""
echo "Service management:"
echo -e "  ${YELLOW}systemctl status orchenet-backend${NC}"
echo -e "  ${YELLOW}systemctl restart orchenet-backend${NC}"
echo -e "  ${YELLOW}systemctl status wg-quick@wg0${NC}"
echo ""
echo "Next steps:"
echo "  1. Access the web interface and log in"
echo "  2. Add your first MikroTik device"
echo "  3. Generate provisioning script:"
echo -e "     ${YELLOW}cd $INSTALL_DIR/device-scripts/mikrotik${NC}"
echo -e "     ${YELLOW}python3 generate-provision-script.py --device-id 1 --server http://$SERVER_IP:8000${NC}"
echo ""
echo -e "${GREEN}Installation logs saved to: /var/log/orchenet-install.log${NC}"
echo ""
