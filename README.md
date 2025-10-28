![onette_full](https://github.com/alteredgenome/orchenet/blob/main/onette_full.png?raw=true)
# **OrcheNet \- The Network Orchestrator**

## **📖 Overview**

**OrcheNet** is a self-hosted, web-based management tool designed to centrally manage a fleet of network devices from various vendors. Its core architectural principle is an agent-based "phone home" model, which allows devices to be managed securely without requiring public IP addresses or inbound firewall rules.  
Configuration is king. OrcheNet treats device configurations as the source of truth, representing them in a structured, vendor-agnostic **YAML format**. This allows for easy versioning, backup, and consistent application of settings across your infrastructure.  
The project is designed to be highly modular, with initial support for **MikroTik RouterOS** and a clear path to integrate other major vendors.

## **✨ Core Features**

* **Agent-Based Communication:** Devices actively check in with the server to fetch tasks, eliminating the need for direct access from the central server.  
* **YAML Configuration:** Manage complex device settings through simple, human-readable YAML files.  
* **Vendor Agnostic:** A flexible abstraction layer allows for easy expansion to support new hardware vendors.  
* **Web-Based UI:** A clean and modern frontend for viewing device status, editing configurations, and monitoring tasks.  
* **Secure:** Communication between the agent and server is handled over HTTPS.

## **🛠️ Technology Stack**

* **Backend:** **Python** with **FastAPI** for a high-performance, asynchronous API.  
* **Database:** **SQLAlchemy ORM** with an initial **SQLite** backend for simplicity, designed for easy migration to PostgreSQL.  
* **Frontend:** A modern, responsive single-page application (SPA) built with **Svelte** or **React**.  
* **Agent:** A lightweight **Python** script deployed on each managed device.

## **📂 Project Structure**

The repository is organized into three main components:  
orchenet/  
├── backend/       \# FastAPI server, API logic, database models, and vendor modules.  
├── frontend/      \# Svelte/React SPA for the user interface.  
└── agent/         \# Python agent script to be deployed on managed devices.

## **🚀 Project Status**

### ✅ Completed Features

- **✅ Backend Infrastructure**
  - FastAPI application with async task processor
  - SQLAlchemy database models
  - REST API endpoints (devices, tasks, check-in)
  - SSH connection manager
  - Configuration executor service

- **✅ Multi-Vendor Support**
  - MikroTik RouterOS translator
  - Fortinet FortiOS translator
  - Ubiquiti UniFi translator (Controller API)
  - WatchGuard Fireware translator

- **✅ Device Integration**
  - HTTP check-in system (FortiGate, MikroTik)
  - UniFi Controller API integration
  - SSH-based management (all vendors)
  - Device-side scripts and documentation

- **✅ Web UI**
  - FortiManager-inspired interface
  - Device management views
  - Configuration editor (YAML)
  - Task monitoring
  - Real-time status display

- **✅ Configuration Management**
  - Vendor-agnostic YAML schema
  - Automatic translation to vendor commands
  - Configuration versioning
  - Task queue system

- **✅ Documentation**
  - Quick Start Guide
  - Testing Guide
  - Vendor-specific setup guides
  - API documentation
  - Configuration schemas

### 🚧 In Progress

- Authentication and authorization
- Credential encryption
- Advanced error handling
- Comprehensive testing suite

### 📋 Planned

- Configuration rollback
- Bulk operations
- Advanced reporting
- Multi-site management
- Mobile app

### Supported Vendors

| Vendor | Status | Check-In Method | Configuration |
|--------|--------|-----------------|---------------|
| **MikroTik** | ✅ Ready | Script (HTTP) | SSH |
| **Fortinet** | ✅ Ready | Automation Stitch (HTTP) | SSH |
| **Ubiquiti** | ✅ Ready | Controller API | Controller API |
| **WatchGuard** | ✅ Ready | SSH Poll | SSH |

## **📚 Documentation**

### 🚀 Getting Started
* **[QUICKSTART.md](QUICKSTART.md)** - **Start here! Quick setup guide**
* **[TESTING.md](TESTING.md)** - Complete testing guide without real devices
* **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Solutions for common issues
* **[COMMANDS.md](COMMANDS.md)** - Quick command reference

### 📖 Configuration
* **[CONFIG.md](CONFIG.md)** - **Unified vendor-agnostic YAML schema** (recommended)
* **[CONFIG-tik.md](CONFIG-tik.md)** - MikroTik RouterOS specific
* **[CONFIG-ftnt.md](CONFIG-ftnt.md)** - Fortinet specific
* **[CONFIG-ubnt.md](CONFIG-ubnt.md)** - Ubiquiti UniFi specific
* **[CONFIG-wg.md](CONFIG-wg.md)** - WatchGuard specific

### 🛠️ Component Documentation
* **[backend/README.md](backend/README.md)** - Backend setup and API
* **[backend/README-DETAILED.md](backend/README-DETAILED.md)** - Detailed backend guide
* **[frontend/WEBUI-README.md](frontend/WEBUI-README.md)** - Frontend UI guide

### 📡 Device Setup
* **[device-scripts/mikrotik/README.md](device-scripts/mikrotik/README.md)** - MikroTik setup
* **[device-scripts/fortigate/README.md](device-scripts/fortigate/README.md)** - FortiGate setup
* **[device-scripts/watchguard/README.md](device-scripts/watchguard/README.md)** - WatchGuard setup

### 🔧 Development
* **[CLAUDE.md](CLAUDE.md)** - AI assistant and developer guide
* **[IMPLEMENTATION-SUMMARY.md](IMPLEMENTATION-SUMMARY.md)** - Complete implementation details

## **🚦 Getting Started**

### Quick Start (Recommended)

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

**Windows:**
```batch
start.bat
```

The startup script will automatically:
- Install all dependencies
- Initialize the database
- Start backend (http://localhost:8000)
- Start frontend (http://localhost:5173)

**📖 For detailed instructions, see [QUICKSTART.md](QUICKSTART.md)**

### Manual Setup

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python init_db.py --seed
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

### Access the Application

- **Frontend UI**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Stop Services

**Linux/Mac:**
```bash
./stop.sh
```

**Windows:** Close the terminal windows

## **🤝 Contributing**

Contributions are welcome! Please feel free to submit issues and pull requests.

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

See [CLAUDE.md](CLAUDE.md) for detailed architecture and development guidelines.
