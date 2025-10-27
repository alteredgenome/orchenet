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
