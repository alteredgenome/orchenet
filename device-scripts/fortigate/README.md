# FortiGate Check-In Configuration

This directory contains configuration for FortiGate devices to check in with OrcheNet.

## Method 1: Automation Stitch (Recommended)

FortiGate automation stitches allow periodic HTTP calls to the OrcheNet server.

### Configuration Steps

1. **Create Webhook Action**

```
config system automation-action
    edit "orchenet-checkin"
        set action-type webhook
        set protocol https
        set uri "https://orchenet.example.com/api/checkin"
        set http-body "{\"device_name\": \"%[fortinet-serial-number]%\", \"vendor\": \"fortinet\", \"firmware_version\": \"%[firmware-version]%\", \"status_data\": {\"cpu\": %[cpu-usage]%, \"memory\": %[memory-usage]%}}"
        set port 443
        set http-headers "Content-Type: application/json"
        set http-headers "Authorization: Bearer YOUR_DEVICE_API_KEY"
    next
end
```

2. **Create Periodic Trigger**

```
config system automation-trigger
    edit "orchenet-schedule"
        set trigger-type scheduled
        set trigger-frequency hourly
        set trigger-minute 0
    next
end
```

3. **Create Automation Stitch**

```
config system automation-stitch
    edit "orchenet-checkin-stitch"
        set trigger "orchenet-schedule"
        set action "orchenet-checkin"
        set status enable
    next
end
```

### Variable Substitution

FortiGate supports the following variables in webhook bodies:
- `%[fortinet-serial-number]%` - Device serial number
- `%[firmware-version]%` - Current firmware version
- `%[cpu-usage]%` - Current CPU usage percentage
- `%[memory-usage]%` - Current memory usage percentage
- `%[hostname]%` - Device hostname

## Method 2: SSH Configuration Push

OrcheNet will SSH to the FortiGate to push configurations.

### Prerequisites

1. **Enable SSH**

```
config system global
    set admin-ssh-v1-compatible disable
    set admin-ssh-port 22
end
```

2. **Configure Admin User**

```
config system admin
    edit "orchenet"
        set accprofile "super_admin"
        set vdom "root"
        set password "YOUR_STRONG_PASSWORD"
        set trusthost1 ORCHENET_SERVER_IP 255.255.255.255
    next
end
```

3. **Allow SSH from OrcheNet Server**

```
config system interface
    edit "wan1"
        set allowaccess ping https ssh
    next
end
```

Or use `trusted-hosts` for more security:

```
config system admin
    edit "orchenet"
        set trusthost1 ORCHENET_SERVER_IP 255.255.255.255
    next
end
```

## Method 3: FGFM Protocol (Future Enhancement)

FortiGate to FortiManager (FGFM) protocol support is planned for future releases. This would allow OrcheNet to act as a FortiManager instance for more native integration.

### Benefits of FGFM
- Native FortiGate protocol
- More efficient than SSH
- Better security with certificate authentication
- Real-time status updates
- Configuration synchronization

This is currently under investigation and will be implemented in a future version if feasible.

## Security Considerations

1. **Use HTTPS**: Always use HTTPS for webhook endpoints
2. **API Keys**: Rotate API keys regularly
3. **Trusted Hosts**: Limit SSH access to OrcheNet server IP only
4. **Strong Passwords**: Use complex passwords for admin accounts
5. **Dedicated Admin Account**: Create a separate admin account for OrcheNet, not the main admin
6. **VDOM Support**: If using VDOMs, configure appropriately

## Troubleshooting

### Webhook Not Firing

1. Check automation stitch status:
```
diagnose test application autod 3
```

2. View automation stitch logs:
```
diagnose debug application autod -1
diagnose debug enable
```

3. Verify webhook can reach server:
```
execute ping orchenet.example.com
```

### SSH Connection Issues

1. Test SSH connectivity:
```
execute ssh orchenet.example.com
```

2. Verify admin account:
```
show system admin
```

3. Check trusted hosts:
```
get system admin orchenet | grep trusthost
```

## Verification

After configuration, verify check-ins are working:

1. Check last check-in time in OrcheNet Web UI
2. Review device status in Dashboard
3. Verify pending tasks are being retrieved
4. Check FortiGate logs for automation stitch execution

## Example Complete Configuration

See `fortigate-orchenet-config.txt` for a complete example configuration that can be pasted into a FortiGate.
