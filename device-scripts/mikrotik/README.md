# MikroTik RouterOS Check-In Configuration

This directory contains the check-in script for MikroTik RouterOS devices.

## Installation

### 1. Upload Script to Router

**Via WebFig/WinBox:**
1. Open System → Scripts
2. Click the "+" button to add new script
3. Name: `orchenet-checkin`
4. Copy contents of `orchenet-checkin.rsc` into the source field
5. Click OK

**Via SSH/Terminal:**
```bash
# Copy the script file to the router
scp orchenet-checkin.rsc admin@192.168.1.1:

# Import the script
ssh admin@192.168.1.1
/system script add name=orchenet-checkin source=[/file get orchenet-checkin.rsc contents]
```

### 2. Configure Variables

Edit the script and update these variables:
- `orchenetServer` - Your OrcheNet server URL (e.g., https://orchenet.example.com)
- `orchenetApiKey` - Device-specific API key from OrcheNet

### 3. Schedule Script Execution

Add a scheduler entry to run the script periodically (e.g., every hour):

```
/system scheduler add \
    name=orchenet-checkin \
    interval=1h \
    on-event="/system script run orchenet-checkin" \
    start-time=startup
```

**Alternative intervals:**
- Every 30 minutes: `interval=30m`
- Every 15 minutes: `interval=15m`
- Every 5 minutes: `interval=5m`
- Daily at 3 AM: `interval=1d start-time=03:00:00`

### 4. Test Script Manually

```
/system script run orchenet-checkin
```

Check logs to verify:
```
/log print where topics~"script"
```

## SSH Configuration for Remote Management

OrcheNet will connect via SSH to push configurations. Ensure SSH is properly configured:

### 1. Enable SSH Service

```
/ip service set ssh port=22 disabled=no
```

### 2. Create Dedicated User for OrcheNet

```
/user add \
    name=orchenet \
    group=full \
    password=YOUR_STRONG_PASSWORD
```

### 3. Restrict SSH Access (Recommended)

Limit SSH access to OrcheNet server IP only:

```
/ip service set ssh address=ORCHENET_SERVER_IP/32
```

Or use firewall rules:

```
/ip firewall filter add \
    chain=input \
    protocol=tcp \
    dst-port=22 \
    src-address=!ORCHENET_SERVER_IP \
    action=drop \
    comment="Block SSH except from OrcheNet"
```

### 4. Use SSH Keys (More Secure)

Generate SSH key on OrcheNet server:
```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/orchenet_mikrotik
```

Add public key to MikroTik:
```
/user ssh-keys import public-key-file=orchenet_mikrotik.pub user=orchenet
```

Disable password authentication (optional):
```
/ip ssh set strong-crypto=yes
```

## Script Features

The `orchenet-checkin.rsc` script performs the following:

1. **System Status Collection**
   - CPU load
   - Memory usage
   - System uptime
   - RouterOS version
   - Board information

2. **Check-In Process**
   - Sends device information to OrcheNet server
   - Includes serial number and firmware version
   - Receives pending tasks from server

3. **Error Handling**
   - Logs successful check-ins
   - Logs errors if unable to connect
   - Continues router operation even if check-in fails

4. **Task Retrieval**
   - Fetches pending configuration tasks
   - Processes tasks from server
   - Reports task completion status

## Advanced Configuration

### Custom Check-In Intervals Based on Time

```
# More frequent during business hours
/system scheduler add \
    name=orchenet-checkin-business \
    interval=15m \
    start-time=08:00:00 \
    stop-time=18:00:00 \
    on-event="/system script run orchenet-checkin"

# Less frequent after hours
/system scheduler add \
    name=orchenet-checkin-afterhours \
    interval=1h \
    start-time=18:00:00 \
    stop-time=08:00:00 \
    on-event="/system script run orchenet-checkin"
```

### Firewall Rules for OrcheNet Communication

```
# Allow outbound HTTPS to OrcheNet server
/ip firewall filter add \
    chain=output \
    protocol=tcp \
    dst-port=443 \
    dst-address=ORCHENET_SERVER_IP \
    action=accept \
    comment="Allow OrcheNet check-in"

# Allow inbound SSH from OrcheNet server
/ip firewall filter add \
    chain=input \
    protocol=tcp \
    dst-port=22 \
    src-address=ORCHENET_SERVER_IP \
    action=accept \
    comment="Allow OrcheNet SSH"
```

## Monitoring and Troubleshooting

### View Check-In Logs

```
/log print where message~"OrcheNet"
```

### Test HTTPS Connectivity to Server

```
/tool fetch url=https://orchenet.example.com/health mode=https output=user
```

### Debug Script Execution

Add debug logging to the script:
```
:log debug "OrcheNet: Variable orchenetServer = $orchenetServer"
:log debug "OrcheNet: Variable deviceName = $deviceName"
```

### Common Issues

**Issue: "Script failed - unable to connect"**
- Check internet connectivity
- Verify OrcheNet server URL is correct
- Ensure HTTPS is not blocked by firewall
- Check if server certificate is valid

**Issue: "Script not running on schedule"**
- Verify scheduler is enabled: `/system scheduler print`
- Check system time is correct: `/system clock print`
- Review scheduler logs: `/log print where topics~"system,info"`

**Issue: "Authentication failed"**
- Verify API key is correct in script
- Check device is registered in OrcheNet
- Ensure device name matches OrcheNet configuration

## Security Best Practices

1. **Use Strong Passwords**: Generate complex passwords for the orchenet user
2. **Restrict SSH Access**: Only allow OrcheNet server IP
3. **Use SSH Keys**: Prefer key-based authentication over passwords
4. **Regular Updates**: Keep RouterOS updated to latest stable version
5. **Firewall Rules**: Only allow necessary traffic to/from OrcheNet server
6. **API Key Rotation**: Periodically rotate API keys
7. **Audit Logs**: Regularly review system logs for suspicious activity

## Uninstallation

To remove OrcheNet integration:

```
# Remove scheduler
/system scheduler remove orchenet-checkin

# Remove script
/system script remove orchenet-checkin

# Remove user (optional)
/user remove orchenet

# Remove firewall rules (if added)
/ip firewall filter remove [find comment~"OrcheNet"]
```
