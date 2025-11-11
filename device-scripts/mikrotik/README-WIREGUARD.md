# MikroTik WireGuard Provisioning for OrcheNet

This directory contains scripts to provision MikroTik routers for management via OrcheNet using WireGuard VPN.

## Architecture Overview

```
┌─────────────────┐                                ┌──────────────────┐
│ MikroTik Router │ ◄─────── WireGuard VPN ──────► │ OrcheNet Server  │
│   10.99.0.X     │         (Encrypted)            │    10.99.0.1     │
└─────────────────┘                                └──────────────────┘
        │                                                    │
        │ 1. Periodic Check-in (HTTP over VPN)             │
        ├──────────────────────────────────────────────────►│
        │                                                    │
        │ 2. Tasks/Config Available? (JSON Response)        │
        │◄──────────────────────────────────────────────────┤
        │                                                    │
        │ 3. OrcheNet Connects via SSH (over VPN)          │
        │◄──────────────────────────────────────────────────┤
        │                                                    │
        │ 4. Configuration Applied                          │
        │◄──────────────────────────────────────────────────┤
```

## Why WireGuard?

1. **No Public IP Required**: Router initiates VPN connection to server
2. **Secure**: All traffic encrypted with modern cryptography
3. **Firewall Friendly**: Single UDP port outbound, no inbound rules needed
4. **Reliable**: SSH over VPN is more stable than direct internet SSH
5. **Private**: Management traffic isolated on private VPN network

## Prerequisites

- OrcheNet server installed and running (see `/deploy/install.sh`)
- MikroTik router with RouterOS 7.x or later (WireGuard support)
- Router has internet access
- Access to router via Winbox, WebFig, or SSH

## Quick Start

### Step 1: Add Device to OrcheNet

1. Access OrcheNet web interface: `http://YOUR_SERVER_IP`
2. Navigate to "Devices" > "Add Device"
3. Fill in device details:
   - **Name**: e.g., "Router-Site-A"
   - **Vendor**: MikroTik
   - **IP Address**: Router's current public/local IP (temporary, will use VPN)
   - **SSH Username**: (leave empty for now, will be created)
   - **SSH Password**: (leave empty for now, will be created)
4. Click "Add Device"
5. Note the **Device ID** (shown in device list or URL)

### Step 2: Generate Provisioning Script

On your OrcheNet server, run:

```bash
cd /opt/orchenet/device-scripts/mikrotik

python3 generate-provision-script.py \
    --device-id 1 \
    --server https://YOUR_SERVER_PUBLIC_IP:8000 \
    --server-ip YOUR_SERVER_PUBLIC_IP \
    --output provision-router-site-a.rsc
```

**Parameters:**
- `--device-id`: Device ID from OrcheNet (from Step 1)
- `--server`: OrcheNet API URL (use HTTPS if you have SSL configured)
- `--server-ip`: Server's public IP address (for WireGuard endpoint)
- `--output`: Output filename for the provisioning script

**What this does:**
1. Fetches OrcheNet server's WireGuard public key
2. Generates a WireGuard key pair for the router
3. Registers the router as a WireGuard peer in OrcheNet
4. Allocates a VPN IP address (e.g., 10.99.0.2)
5. Creates a customized RouterOS script with all necessary configuration

**Output:**
```
OrcheNet MikroTik Provisioning Script Generator
==================================================
Server: https://YOUR_SERVER_IP:8000
Device ID: 1

Fetching OrcheNet server information...
✓ Server Public Key: abcd1234...
✓ Server VPN IP: 10.99.0.1
✓ Listen Port: 51820

Generating WireGuard keypair for device...
✓ Device Public Key: efgh5678...

Registering device with OrcheNet...
✓ Device Name: Router-Site-A
✓ Assigned VPN IP: 10.99.0.2

Generating provisioning script...
✓ Provisioning script generated: provision-router-site-a.rsc

==================================================
SUCCESS! Next steps:
...
```

### Step 3: Copy Script to Router

Transfer the generated script to your MikroTik router using one of these methods:

**Option A: SCP (Secure Copy)**
```bash
scp provision-router-site-a.rsc admin@ROUTER_IP:
```

**Option B: Winbox**
1. Open Winbox and connect to router
2. Navigate to "Files"
3. Drag and drop the `.rsc` file

**Option C: WebFig**
1. Open browser to `http://ROUTER_IP`
2. Navigate to "Files"
3. Click "Upload" and select the `.rsc` file

**Option D: Copy-Paste (for small scripts)**
1. Open router terminal (Winbox, SSH, or WebFig)
2. Copy the contents of the `.rsc` file
3. Paste directly into terminal

### Step 4: Run Provisioning Script

Connect to the router terminal (SSH, Winbox, or WebFig) and run:

```routeros
/import provision-router-site-a.rsc
```

The script will:
1. ✓ Create WireGuard interface (`orchenet-wg`)
2. ✓ Configure WireGuard peer (OrcheNet server)
3. ✓ Assign VPN IP address (e.g., 10.99.0.2)
4. ✓ Add route to VPN network
5. ✓ Create SSH user (`orchenet`)
6. ✓ Enable SSH service
7. ✓ Configure firewall to allow SSH from VPN
8. ✓ Create check-in script
9. ✓ Schedule periodic check-ins (every 5 minutes)
10. ✓ Test WireGuard connection

**Monitor the output for any errors!**

### Step 5: Verify Connection

**On the Router:**
```routeros
# Check WireGuard interface status
/interface wireguard peers print

# You should see:
#  interface=orchenet-wg
#  public-key="..."
#  endpoint-address=YOUR_SERVER_IP
#  current-endpoint-address=YOUR_SERVER_IP
#  current-endpoint-port=51820
#  allowed-address=10.99.0.0/24
#  tx=1234 rx=5678

# Test ping to server
/ping 10.99.0.1 count=5
```

**On the Server:**
```bash
# Check WireGuard peers
sudo wg show wg0

# You should see your router listed with a recent handshake

# Test SSH to router via VPN
ssh orchenet@10.99.0.2
```

**In OrcheNet Web Interface:**
1. Navigate to "Devices"
2. Your router should show status: "Online"
3. Last check-in should be within the last 5 minutes
4. WireGuard status should show "Connected"

### Step 6: Secure the Router

**IMPORTANT**: Change the default SSH password!

```routeros
/user set orchenet password=YOUR_SECURE_PASSWORD_HERE
```

**Even better**: Use SSH key authentication:

1. Generate SSH key on server:
   ```bash
   ssh-keygen -t ed25519 -C "orchenet"
   ```

2. Copy public key to router:
   ```bash
   ssh-copy-id orchenet@10.99.0.2
   ```

3. Update device credentials in OrcheNet web interface

4. Disable password authentication (optional):
   ```routeros
   /user set orchenet password=""
   ```

## What Gets Configured

### WireGuard Interface
- **Interface Name**: `orchenet-wg`
- **Private Key**: Auto-generated
- **Listen Port**: 51821
- **IP Address**: Assigned by OrcheNet (e.g., 10.99.0.2/32)

### WireGuard Peer (Server)
- **Public Key**: OrcheNet server's public key
- **Endpoint**: Server IP:51820
- **Allowed IPs**: 10.99.0.0/24
- **Persistent Keepalive**: 25 seconds

### SSH Configuration
- **User**: `orchenet`
- **Group**: `full` (admin access)
- **Password**: `CHANGE_ME_TO_SECURE_PASSWORD` (must be changed!)
- **Service**: Enabled on port 22

### Firewall Rules
- **Rule**: Allow SSH from VPN network (10.99.0.0/24)
- **Interface**: `orchenet-wg`
- **Position**: Placed before other rules

### Check-in Script
- **Name**: `orchenet-checkin`
- **Interval**: 5 minutes
- **Function**: Reports device status to OrcheNet
- **Trigger**: Scheduler (runs on startup and every 5 minutes)

### Routes
- **Destination**: 10.99.0.0/24
- **Gateway**: `orchenet-wg` interface

## Troubleshooting

### WireGuard Interface Not Coming Up

```routeros
# Check interface status
/interface wireguard print

# Check if keys are valid
/interface wireguard print detail

# Check firewall isn't blocking WireGuard
/ip firewall filter print
```

**Solution**: Ensure UDP port 51820 is not blocked by ISP or upstream firewall.

### No Handshake with Server

```routeros
/interface wireguard peers print

# If "current-endpoint-address" is empty, there's no connection
```

**Solutions**:
1. Check server is reachable: `/ping SERVER_IP`
2. Verify server's WireGuard is running: `sudo systemctl status wg-quick@wg0`
3. Check server firewall allows UDP 51820: `sudo ufw status`
4. Verify endpoint IP is correct in peer configuration

### Router Not Appearing in OrcheNet

**Check on Router:**
```routeros
# Run check-in manually
/system script run orchenet-checkin

# Check logs
/log print where topics~"script"
```

**Check on Server:**
```bash
# View OrcheNet logs
sudo journalctl -u orchenet-backend -f

# Check if request is reaching server
sudo tail -f /var/log/nginx/access.log
```

**Common Issues**:
- API URL incorrect in script
- Server not accessible from VPN IP
- Nginx not proxying requests correctly

### SSH Not Working

```bash
# From server, try to SSH to router
ssh -v orchenet@10.99.0.2
```

**Solutions**:
1. Verify SSH service is running on router: `/ip service print`
2. Check firewall rule allows SSH from VPN: `/ip firewall filter print`
3. Verify user exists: `/user print`
4. Check password or SSH key is correct

### Cannot Ping Server from Router

```routeros
/ping 10.99.0.1 count=5
```

**Solutions**:
1. Check WireGuard peer has recent handshake: `/interface wireguard peers print`
2. Verify route exists: `/ip route print where dst-address~"10.99"`
3. Check server firewall allows ping: `sudo ufw status`

## Manual Configuration (Alternative to Script)

If you prefer to configure manually or the script fails, follow these steps:

### 1. Generate WireGuard Keys

On your local machine or server:
```bash
wg genkey | tee device-private.key | wg pubkey > device-public.key
```

### 2. Register Device with OrcheNet

```bash
curl -X POST http://YOUR_SERVER:8000/api/wireguard/peers \
    -H "Content-Type: application/json" \
    -d '{"device_id": 1, "public_key": "DEVICE_PUBLIC_KEY"}'
```

Note the assigned VPN IP address.

### 3. Configure on Router

```routeros
# Create WireGuard interface
/interface wireguard add \
    name=orchenet-wg \
    private-key="DEVICE_PRIVATE_KEY" \
    listen-port=51821

# Add server as peer
/interface wireguard peers add \
    interface=orchenet-wg \
    public-key="SERVER_PUBLIC_KEY" \
    endpoint-address=SERVER_IP \
    endpoint-port=51820 \
    allowed-address=10.99.0.0/24 \
    persistent-keepalive=25s

# Assign IP
/ip address add \
    address=ASSIGNED_VPN_IP/32 \
    interface=orchenet-wg

# Add route
/ip route add \
    dst-address=10.99.0.0/24 \
    gateway=orchenet-wg

# Create SSH user
/user add \
    name=orchenet \
    password=SECURE_PASSWORD \
    group=full

# Enable SSH
/ip service enable ssh

# Add firewall rule
/ip firewall filter add \
    chain=input \
    protocol=tcp \
    dst-port=22 \
    src-address=10.99.0.0/24 \
    in-interface=orchenet-wg \
    action=accept \
    place-before=0 \
    comment="Allow SSH from OrcheNet"
```

### 4. Create Check-in Script

See `orchenet-checkin.rsc` for the check-in script template.

## Advanced Configuration

### Custom Check-in Interval

Edit scheduler:
```routeros
/system scheduler set orchenet-checkin interval=10m
```

### Multiple Servers (Failover)

Add additional WireGuard peers for redundancy:
```routeros
/interface wireguard peers add \
    interface=orchenet-wg \
    public-key="BACKUP_SERVER_PUBLIC_KEY" \
    endpoint-address=BACKUP_SERVER_IP \
    endpoint-port=51820 \
    allowed-address=10.99.0.0/24
```

### VPN Only SSH Access

To ensure SSH is only accessible via VPN:

```routeros
# Disable SSH from WAN
/ip firewall filter add \
    chain=input \
    protocol=tcp \
    dst-port=22 \
    in-interface=ether1 \
    action=drop \
    comment="Block SSH from WAN"
```

(Replace `ether1` with your WAN interface)

## Security Best Practices

1. **Change Default Password**: Always change `orchenet` user password
2. **Use SSH Keys**: Prefer key-based authentication over passwords
3. **Restrict Firewall**: Only allow SSH from OrcheNet VPN subnet
4. **Keep RouterOS Updated**: Regularly update to latest stable version
5. **Monitor Logs**: Check `/log print` regularly for suspicious activity
6. **Backup Configuration**: `/system backup save name=pre-orchenet`
7. **Test Before Production**: Verify on test router first

## Removal/Unprovisioning

To remove OrcheNet configuration:

```routeros
# Stop scheduler
/system scheduler remove orchenet-checkin

# Remove script
/system script remove orchenet-checkin

# Remove firewall rule
/ip firewall filter remove [find comment="Allow SSH from OrcheNet"]

# Remove route
/ip route remove [find gateway=orchenet-wg]

# Remove IP address
/ip address remove [find interface=orchenet-wg]

# Remove peer
/interface wireguard peers remove [find interface=orchenet-wg]

# Remove interface
/interface wireguard remove orchenet-wg

# Remove user
/user remove orchenet
```

Then remove device from OrcheNet web interface.

## Support

For issues or questions:
- Check OrcheNet logs: `sudo journalctl -u orchenet-backend -f`
- Check router logs: `/log print`
- Review WireGuard status: `sudo wg show`
- Open an issue on GitHub

## Files in This Directory

- `README-WIREGUARD.md` - This file
- `generate-provision-script.py` - Script generator (requires `requests`)
- `provision-orchenet.rsc` - Template provisioning script
- `orchenet-checkin.rsc` - Check-in script template

## Next Steps

After provisioning:
1. Verify device shows "Online" in OrcheNet
2. Test configuration deployment via web interface
3. Use Web CLI feature to access router terminal
4. Set up additional devices
5. Configure backup/monitoring policies
