# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OrcheNet is a self-hosted, web-based network device management platform using an agent-based "phone home" architecture. Devices check in with a central server to fetch tasks, eliminating the need for public IPs or inbound firewall rules. Configuration is managed through vendor-agnostic YAML files.

## Architecture

The project consists of three main components:

### 1. Backend (backend/)
- **Framework:** Python with FastAPI for asynchronous API operations
- **Database:** SQLAlchemy ORM with SQLite initially, designed for PostgreSQL migration
- **Vendor Abstraction:** Modular system to support multiple network device vendors
- **Initial Target:** MikroTik RouterOS support
- **Future Vendors:** Fortinet, WatchGuard, Ubiquiti

### 2. Frontend (frontend/)
- **Framework:** Modern SPA using Svelte or React
- **Purpose:** Web UI for device status, configuration editing, and task monitoring
- **Communication:** REST API calls to FastAPI backend

### 3. Agent (agent/)
- **Language:** Lightweight Python script
- **Deployment:** Runs on each managed network device
- **Communication:** HTTPS to backend server for check-ins and task fetching
- **Security:** No inbound connections required on managed devices

## Key Architectural Principles

### Configuration as Source of Truth
- All device configurations stored in structured YAML format
- YAML files are vendor-agnostic abstractions
- Backend translates YAML to vendor-specific commands
- Enables versioning, backup, and consistent settings across infrastructure

### Agent-Based Communication Flow
1. Agent on device initiates connection to server
2. Server responds with pending tasks/configuration updates
3. Agent executes tasks and reports results
4. No direct server-to-device connections required

### Vendor Abstraction Layer
- Abstract interface for device operations (config, status, commands)
- Each vendor implements the interface with specific logic
- YAML-to-command translation is vendor-specific
- Makes adding new vendors straightforward

## Development Status

✅ **Completed:**
- Project structure initialization
- Database models (Device, Task)
- Vendor abstraction layer (base interface)
- Core API endpoints (devices, tasks, check-in)
- SSH connection manager
- Vendor-specific translators (MikroTik, Fortinet, Ubiquiti, WatchGuard)
- FortiManager-inspired Web UI
- Vendor-specific check-in mechanisms

🚧 **In Progress:**
- Integration testing
- Device provisioning workflows
- Real-time status monitoring

📋 **Planned:**
- Configuration rollback functionality
- Bulk operations
- Advanced reporting
- Multi-site management

## Development Commands

**Note:** Commands will be defined once the project structure is created. Expected patterns:

### Backend Development
```bash
# Navigate to backend
cd backend/

# Install dependencies (expected)
pip install -r requirements.txt

# Run FastAPI development server (expected)
uvicorn main:app --reload

# Run tests (expected)
pytest
```

### Frontend Development
```bash
# Navigate to frontend
cd frontend/

# Install dependencies (expected - npm or pnpm)
npm install  # or pnpm install

# Run development server (expected)
npm run dev

# Build for production (expected)
npm run build
```

### Agent Testing
```bash
# Navigate to agent
cd agent/

# Test agent locally (expected)
python agent.py --config test_config.yaml
```

## Important Implementation Notes

### Security Considerations
- All agent-server communication over HTTPS
- Agent authentication mechanism required
- Secure storage of device credentials
- YAML config validation to prevent injection attacks

### Database Design
- Start with SQLite for simplicity
- Design schema for easy PostgreSQL migration
- Consider device state, task queue, configuration history
- Audit logging for configuration changes

### YAML Configuration Schema
- Must support vendor-agnostic abstractions
- Hierarchical structure for complex device configs
- Validation schema to catch errors before deployment
- Support for templates and variables

### Vendor Module Pattern
Each vendor module should implement:
- Configuration parser (YAML → vendor commands)
- Status collector (device → normalized format)
- Command executor (with error handling)
- Capability discovery (what features are supported)

## Vendor-Specific Check-In Methods

OrcheNet uses different check-in methods optimized for each vendor's capabilities:

### FortiGate (Fortinet)
**Method:** Automation Stitch + SSH
- **Check-In:** FortiGate automation stitch makes periodic HTTP POST to `/api/checkin`
- **Configuration Push:** OrcheNet connects via SSH to apply configurations
- **Advantages:** Native FortiOS feature, no additional software needed
- **Configuration:** See `device-scripts/fortigate/README.md`
- **Future:** FGFM protocol support planned for more native integration

**Automation Stitch Setup:**
```
config system automation-action
    edit "orchenet-checkin"
        set action-type webhook
        set uri "https://orchenet.example.com/api/checkin"
end

config system automation-trigger
    edit "orchenet-schedule"
        set trigger-type scheduled
        set trigger-frequency hourly
end

config system automation-stitch
    edit "orchenet-checkin-stitch"
        set trigger "orchenet-schedule"
        set action "orchenet-checkin"
        set status enable
end
```

### MikroTik (RouterOS)
**Method:** Scheduled Script + SSH
- **Check-In:** RouterOS script runs periodically via scheduler, calls `/api/checkin`
- **Configuration Push:** OrcheNet connects via SSH to apply configurations
- **Advantages:** Highly flexible, full RouterOS scripting available
- **Configuration:** See `device-scripts/mikrotik/README.md`

**Script Installation:**
```
# Upload script
/system script add name=orchenet-checkin source=[/file get orchenet-checkin.rsc contents]

# Schedule execution
/system scheduler add name=orchenet-checkin interval=1h on-event="/system script run orchenet-checkin" start-time=startup
```

### Ubiquiti (UniFi)
**Method:** Controller API Integration
- **Check-In:** OrcheNet queries UniFi Controller API periodically
- **Configuration Push:** OrcheNet sends API calls to Controller
- **Advantages:** Controller already manages devices, no device-side setup
- **Configuration:** Configure controller credentials in OrcheNet device settings
- **Note:** Devices don't need individual setup; controller handles all communication

**Integration:**
- UniFi Controller API endpoint: `https://controller:8443/api`
- OrcheNet polls controller for device status
- Configuration changes applied via controller REST API
- Supports UDM, USW (switches), UAP (access points)

### WatchGuard (Firebox)
**Method:** SSH-Only (Allowed Hosts)
- **Check-In:** OrcheNet initiates SSH connection to poll device status
- **Configuration Push:** Commands sent via SSH session
- **Reason:** WatchGuard doesn't support phone-home mechanisms
- **Advantages:** Simple, secure with allowed-hosts restrictions
- **Configuration:** See `device-scripts/watchguard/README.md`

**Security Setup:**
```
# Restrict SSH access to OrcheNet server only
set ssh allowed-hosts ORCHENET_SERVER_IP/32
set admin orchenet allowed-hosts ORCHENET_SERVER_IP/32

# Enable SSH
set ssh enabled
set ssh port 22
```

## Communication Flow by Vendor

### Phone-Home Vendors (FortiGate, MikroTik)
```
┌─────────────┐                    ┌─────────────┐
│   Device    │──── HTTP POST ────>│  OrcheNet   │
│ (FortiGate/ │<─── Tasks JSON ────│   Server    │
│  MikroTik)  │                    └─────────────┘
└─────────────┘
       │
       │ If tasks pending
       │
       v
┌─────────────┐                    ┌─────────────┐
│  OrcheNet   │──── SSH ──────────>│   Device    │
│   Server    │   Config Commands  │             │
└─────────────┘<─── Response ──────└─────────────┘
```

### Controller-Based (UniFi)
```
┌─────────────┐                    ┌─────────────┐
│  OrcheNet   │──── API Query ────>│   UniFi     │
│   Server    │<─── Device List ───│ Controller  │
└─────────────┘                    └─────────────┘
       │                                  │
       │ Config Change                    │ API Call
       v                                  v
┌─────────────┐                    ┌─────────────┐
│  OrcheNet   │──── API POST ─────>│   UniFi     │
│   Server    │                    │ Controller  │
└─────────────┘                    └─────────────┘
                                          │
                                          │ Auto-provision
                                          v
                                   ┌─────────────┐
                                   │  UniFi      │
                                   │  Devices    │
                                   └─────────────┘
```

### SSH-Only (WatchGuard)
```
┌─────────────┐                    ┌─────────────┐
│  OrcheNet   │──── SSH Poll ─────>│ WatchGuard  │
│   Server    │<─── Status ────────│   Firebox   │
└─────────────┘                    └─────────────┘
       │
       │ Config needed
       v
┌─────────────┐                    ┌─────────────┐
│  OrcheNet   │──── SSH ──────────>│ WatchGuard  │
│   Server    │   CLI Commands     │   Firebox   │
└─────────────┘<─── Response ──────└─────────────┘
```

## API Endpoints Reference

### Device Management
- `POST /api/devices` - Register new device
- `GET /api/devices` - List all devices
- `GET /api/devices/{id}` - Get device details
- `PUT /api/devices/{id}` - Update device
- `DELETE /api/devices/{id}` - Remove device
- `PUT /api/devices/{id}/config` - Update device configuration (triggers deployment)

### Task Management
- `POST /api/tasks` - Create new task
- `GET /api/tasks` - List tasks (filter by device/status)
- `GET /api/tasks/{id}` - Get task details
- `PUT /api/tasks/{id}` - Update task status
- `POST /api/tasks/{id}/retry` - Retry failed task

### Check-In (Phone-Home)
- `POST /api/checkin` - Device check-in endpoint
  - Request body: `{device_name, vendor, serial_number, firmware_version, status_data}`
  - Returns: List of pending tasks
- `POST /api/checkin/result/{task_id}` - Submit task execution result
- `GET /api/checkin/pending/{device_id}` - Get pending tasks for device
