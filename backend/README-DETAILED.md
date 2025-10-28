# OrcheNet Backend - Detailed Documentation

FastAPI-based backend server for OrcheNet network device orchestration platform.

## Features

- **Multi-Vendor Support**: MikroTik, Fortinet, Ubiquiti, WatchGuard
- **RESTful API**: Full CRUD operations for devices and tasks
- **Vendor Abstraction**: Unified YAML configuration translates to vendor-specific commands
- **SSH Management**: Secure SSH connections with connection pooling
- **Check-In System**: Supports multiple check-in methods per vendor
- **Task Queue**: Asynchronous task execution and status tracking
- **UniFi Integration**: Native UniFi Controller API integration

## Architecture

```
backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   ├── database.py             # Database connection and session
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── device.py          # Device model
│   │   └── task.py            # Task model
│   ├── schemas/                # Pydantic schemas
│   │   ├── device.py          # Device API schemas
│   │   └── task.py            # Task API schemas
│   ├── routers/                # API route handlers
│   │   ├── devices.py         # Device management endpoints
│   │   ├── tasks.py           # Task management endpoints
│   │   └── checkin.py         # Device check-in endpoints
│   ├── services/               # Business logic services
│   │   ├── ssh_manager.py     # SSH connection management
│   │   └── unifi_controller.py # UniFi Controller integration
│   └── vendors/                # Vendor-specific translators
│       ├── base.py            # Abstract vendor interface
│       ├── mikrotik/
│       │   └── translator.py  # MikroTik RouterOS translator
│       ├── fortinet/
│       │   └── translator.py  # FortiOS translator
│       ├── ubiquiti/
│       │   └── translator.py  # UniFi translator
│       └── watchguard/
│           └── translator.py  # WatchGuard Fireware translator
├── requirements.txt            # Python dependencies
└── README.md                  # Quick start guide
```

## Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Redis (for background tasks, optional)

### Setup

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create virtual environment (recommended):**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Initialize database:**
```bash
python -c "from app.database import engine, Base; from app.models import device, task; Base.metadata.create_all(bind=engine)"
```

## Running the Server

### Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

### Production Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Or use Gunicorn with Uvicorn workers:

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Database
DATABASE_URL=sqlite:///./orchenet.db
# For PostgreSQL: postgresql://user:password@localhost/orchenet

# Security
SECRET_KEY=your-secret-key-change-in-production
API_KEY_HEADER=X-API-Key

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=False

# CORS (comma-separated origins)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Redis (optional, for background tasks)
REDIS_URL=redis://localhost:6379/0

# SSH
SSH_TIMEOUT=30
SSH_MAX_CONNECTIONS=10

# Logging
LOG_LEVEL=INFO
```

## API Usage

### Device Management

**Register a new device:**
```bash
curl -X POST http://localhost:8000/api/devices \
  -H "Content-Type: application/json" \
  -d '{
    "name": "fw-main",
    "vendor": "mikrotik",
    "model": "RB4011",
    "ip_address": "192.168.1.1",
    "ssh_username": "admin",
    "ssh_password": "password",
    "check_in_method": "http",
    "check_in_interval": 300
  }'
```

**List all devices:**
```bash
curl http://localhost:8000/api/devices
```

**Get device details:**
```bash
curl http://localhost:8000/api/devices/1
```

**Update device configuration:**
```bash
curl -X PUT http://localhost:8000/api/devices/1/config \
  -H "Content-Type: application/json" \
  -d '{
    "device": {
      "name": "fw-main",
      "vendor": "mikrotik"
    },
    "system": {
      "hostname": "fw-main",
      "timezone": "America/New_York"
    },
    "interfaces": [
      {
        "name": "ether1",
        "enabled": true,
        "addressing": {
          "mode": "dhcp"
        },
        "zone": "wan"
      }
    ]
  }'
```

### Task Management

**Create a task:**
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": 1,
    "task_type": "config_update",
    "payload": {
      "config": {...}
    }
  }'
```

**List tasks:**
```bash
curl http://localhost:8000/api/tasks?device_id=1&status=pending
```

### Device Check-In

**Device check-in (called by devices):**
```bash
curl -X POST http://localhost:8000/api/checkin \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer DEVICE_API_KEY" \
  -d '{
    "device_name": "fw-main",
    "vendor": "mikrotik",
    "serial_number": "12345678",
    "firmware_version": "7.12.1",
    "status_data": {
      "cpu": 15,
      "memory": 45,
      "uptime": "30d 5h 23m"
    }
  }'
```

**Submit task result:**
```bash
curl -X POST http://localhost:8000/api/checkin/result/1 \
  -H "Content-Type: application/json" \
  -d '{
    "success": true,
    "result": {
      "commands_executed": 5,
      "status": "completed"
    }
  }'
```

## Vendor-Specific Setup

### MikroTik
- Deploy `device-scripts/mikrotik/orchenet-checkin.rsc` to device
- Configure SSH access from OrcheNet server
- See `device-scripts/mikrotik/README.md`

### FortiGate
- Configure automation stitch for check-in
- Enable SSH with allowed-hosts restriction
- See `device-scripts/fortigate/README.md`

### Ubiquiti UniFi
- Configure UniFi Controller credentials in device settings
- OrcheNet communicates via Controller API
- No device-side configuration needed

### WatchGuard
- Enable SSH with allowed-hosts
- Create dedicated admin account for OrcheNet
- See `device-scripts/watchguard/README.md`

## Security Considerations

### Production Deployment

1. **Use HTTPS**: Deploy behind reverse proxy (nginx, Caddy)
2. **Strong Secrets**: Generate secure `SECRET_KEY`
3. **Database Security**: Use PostgreSQL with strong passwords
4. **SSH Keys**: Prefer SSH keys over passwords
5. **API Authentication**: Implement proper API key management
6. **CORS**: Configure `CORS_ORIGINS` appropriately
7. **Firewall**: Restrict access to API and SSH ports
8. **Updates**: Keep dependencies updated
9. **Monitoring**: Set up logging and alerting
10. **Backups**: Regular database backups

## License

See main repository LICENSE file.
