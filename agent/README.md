# OrcheNet Agent

Python-based agent that runs on managed network devices to communicate with the OrcheNet server.

## Installation

1. Install Python 3.8 or higher

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create configuration file:
```bash
cp agent.yaml.example agent.yaml
```

4. Edit `agent.yaml` with your settings:
   - Server URL
   - Device ID
   - API key
   - Check-in interval

## Running the Agent

```bash
python agent.py --config agent.yaml
```

Or specify a custom config location:
```bash
python agent.py --config /path/to/config.yaml
```

## Running as a Service

### Linux (systemd)

Create `/etc/systemd/system/orchenet-agent.service`:

```ini
[Unit]
Description=OrcheNet Agent
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/orchenet-agent
ExecStart=/usr/bin/python3 /opt/orchenet-agent/agent.py --config /etc/orchenet/agent.yaml
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
systemctl enable orchenet-agent
systemctl start orchenet-agent
systemctl status orchenet-agent
```

### MikroTik RouterOS

For MikroTik devices, you'll need to schedule the agent to run periodically:

```
/system scheduler add name=orchenet-agent on-event="/tool fetch url=\"https://server/agent-script\" dst-path=agent.rsc; /import agent.rsc" interval=1m
```

## Configuration

See `agent.yaml.example` for all available configuration options.

Key settings:
- `server_url`: OrcheNet server URL
- `device_id`: Unique device identifier
- `api_key`: Authentication key
- `check_in_interval`: Seconds between check-ins (default: 60)
- `log_level`: Logging verbosity (DEBUG, INFO, WARNING, ERROR)

## Logging

Logs are written to stdout by default. For production deployments, redirect to a file:

```bash
python agent.py --config agent.yaml >> /var/log/orchenet-agent.log 2>&1
```

Or configure systemd to handle logging:
```ini
StandardOutput=journal
StandardError=journal
```

## Security

- Always use HTTPS for server communication
- Keep API keys secure and rotate regularly
- Use read-only credentials where possible
- Monitor agent logs for suspicious activity
