# WatchGuard Configuration Management

WatchGuard Firebox devices do not support phone-home capabilities, so OrcheNet manages them exclusively via SSH with allowed-hosts restrictions.

## SSH Configuration

### 1. Enable SSH on WatchGuard Firebox

**Via Fireware Web UI:**
1. Navigate to System → Management
2. Enable SSH access
3. Set SSH port (default: 22)
4. Configure allowed hosts/networks

**Via CLI:**
```
set ssh enabled
set ssh port 22
set ssh allowed-hosts ORCHENET_SERVER_IP
```

### 2. Create Dedicated Admin Account

Create a dedicated account for OrcheNet with appropriate permissions:

**Via Web UI:**
1. Go to System → Administrators
2. Add new administrator
3. Username: `orchenet`
4. Password: Strong password
5. Role: Admin (or custom role with configuration permissions)
6. Allowed hosts: OrcheNet server IP

**Via CLI:**
```
add admin name orchenet password YOUR_STRONG_PASSWORD
set admin orchenet role admin
set admin orchenet allowed-hosts ORCHENET_SERVER_IP
set admin orchenet status enabled
```

### 3. Configure Allowed Hosts

Restrict SSH and admin access to only the OrcheNet server:

```
set ssh allowed-hosts ORCHENET_SERVER_IP/32
set management allowed-hosts ORCHENET_SERVER_IP/32
```

### 4. Firewall Rules for Management

Ensure firewall policies allow SSH from OrcheNet server:

**Via Web UI:**
1. Navigate to Firewall → Firewall Policies
2. Create new policy:
   - From: External (or appropriate zone)
   - To: Firebox
   - Service: SSH
   - Source: OrcheNet Server IP
   - Action: Allow
   - Enable logging

**Via CLI:**
```
add policy name "OrcheNet-SSH-Access"
set policy "OrcheNet-SSH-Access" from External to Firebox
set policy "OrcheNet-SSH-Access" source ORCHENET_SERVER_IP
set policy "OrcheNet-SSH-Access" service SSH
set policy "OrcheNet-SSH-Access" action allow
set policy "OrcheNet-SSH-Access" logging enabled
set policy "OrcheNet-SSH-Access" enabled
```

## SSH Key Authentication (Recommended)

For enhanced security, use SSH key-based authentication:

### 1. Generate SSH Key Pair on OrcheNet Server

```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/orchenet_watchguard
```

### 2. Add Public Key to WatchGuard

**Via Web UI:**
1. Go to System → Administrators
2. Edit the `orchenet` user
3. Add the public key content to SSH public keys field

**Via CLI:**
```
set admin orchenet ssh-public-key "ssh-rsa AAAAB3NzaC1yc2EA... orchenet@server"
```

### 3. Configure SSH on OrcheNet Server

Add to `~/.ssh/config`:
```
Host watchguard-fw
    HostName WATCHGUARD_IP
    User orchenet
    IdentityFile ~/.ssh/orchenet_watchguard
    StrictHostKeyChecking yes
```

## Configuration Management Methods

### Method 1: CLI Commands (Recommended for Simple Changes)

OrcheNet sends individual CLI commands via SSH:

```bash
ssh orchenet@watchguard-fw "set interface eth0 ip 192.168.1.1 netmask 255.255.255.0"
```

### Method 2: Configuration File Upload (For Complex Changes)

1. OrcheNet generates complete configuration XML
2. Uploads via SCP or TFTP
3. Applies configuration

**Upload via SCP:**
```bash
scp config.xml orchenet@watchguard-fw:/tmp/
ssh orchenet@watchguard-fw "import config /tmp/config.xml"
```

### Method 3: Configuration Templates

OrcheNet can use pre-built configuration templates for common scenarios:
- Site-to-site VPN setup
- Guest network configuration
- VLAN deployment
- Firewall policy sets

## Status Monitoring

Since WatchGuard doesn't phone home, OrcheNet periodically queries status via SSH:

### Commands for Status Collection

```bash
# System status
show system status

# Interface status
show interface

# Policy status
show policy

# VPN status
show vpn ipsec

# Resource usage
show system performance

# Log recent events
show log tail 50
```

### Polling Configuration

Configure polling interval in OrcheNet device settings:
- Normal interval: 5-15 minutes
- Offline detection: 3 failed polls
- Emergency changes: Immediate SSH connection

## Security Best Practices

### 1. Network Isolation

- Place WatchGuard management interface on dedicated management VLAN
- Only allow OrcheNet server access to management interface
- Use separate interface for management (not WAN)

### 2. Access Control

```
# Restrict SSH to management IP only
set ssh allowed-hosts ORCHENET_SERVER_IP/32

# Restrict admin access
set admin orchenet allowed-hosts ORCHENET_SERVER_IP/32

# Disable password authentication if using keys
set ssh password-authentication disabled
```

### 3. Logging and Auditing

```
# Enable command auditing
set audit-logging enabled

# Send logs to syslog server
set syslog server SYSLOG_SERVER_IP
set syslog facility local7
set syslog severity info
```

### 4. Session Timeout

```
set ssh idle-timeout 600
set admin-timeout 900
```

### 5. Certificate-Based Authentication

For newer Fireware versions supporting certificate authentication:
```
set ssh certificate-authentication enabled
add ssh trusted-ca-certificate "CA_CERTIFICATE_CONTENT"
```

## Backup and Rollback

### Automatic Backups Before Changes

OrcheNet automatically backs up configuration before applying changes:

```bash
# Backup current config
ssh orchenet@watchguard-fw "export config backup-$(date +%Y%m%d-%H%M%S).xml"
```

### Rollback Procedure

If configuration change fails:

```bash
# Restore from backup
ssh orchenet@watchguard-fw "import config backup-TIMESTAMP.xml"
```

## High Availability Considerations

For WatchGuard clusters (Active/Passive or Active/Active):

### Active/Passive Cluster
- OrcheNet connects to cluster IP
- Configuration syncs automatically between members
- Only configure primary device

### Active/Active Cluster
- OrcheNet manages each device separately
- Ensure consistent configuration across cluster members
- Use configuration templates for consistency

### Configuration Synchronization

```
# Enable config sync
set cluster config-sync enabled
set cluster config-sync peer PEER_IP
```

## Troubleshooting

### Connection Issues

**Test SSH connectivity:**
```bash
ssh -v orchenet@WATCHGUARD_IP
```

**Check allowed hosts:**
```
show ssh allowed-hosts
show admin orchenet
```

**Verify firewall policy:**
```
show policy | grep SSH
```

### Configuration Application Failures

**View recent system logs:**
```
show log system tail 100
```

**Check configuration syntax:**
```
validate config FILENAME
```

**View pending configuration:**
```
show config pending
```

### Performance Issues

**Check system resources:**
```
show system performance
show system memory
show system cpu
```

**Review connection table:**
```
show connections
show sessions
```

## Monitoring Integration

### SNMP (Optional)

Enable SNMP for additional monitoring:

```
set snmp enabled
set snmp community PUBLIC_COMMUNITY ro
set snmp community PRIVATE_COMMUNITY rw
set snmp allowed-hosts ORCHENET_SERVER_IP
set snmp trap-destination ORCHENET_SERVER_IP
```

### Syslog Integration

Forward logs to OrcheNet:

```
set syslog server ORCHENET_SERVER_IP
set syslog port 514
set syslog protocol udp
set syslog facility local7
set syslog severity info
```

## API Support (Future)

WatchGuard is developing REST API capabilities in newer Fireware versions. Once available, OrcheNet will support:
- API-based configuration management
- Real-time status monitoring
- Event-driven updates

This will reduce SSH overhead and improve management efficiency.

## Example Complete Configuration

See `watchguard-orchenet-config.txt` for a complete example CLI configuration for OrcheNet integration.
