# OrcheNet Quick Start Guide

This guide will get you up and running with OrcheNet in minutes.

## Prerequisites

### Required Software
- **Python 3.9+**: https://www.python.org/downloads/
- **Node.js 18+**: https://nodejs.org/
- **Git**: https://git-scm.com/

### Optional
- **PostgreSQL** (for production): https://www.postgresql.org/
- **Redis** (for enhanced task queuing): https://redis.io/

## Quick Start (Automated)

### Step 1: Run Setup (First Time Only)

**Windows:**
```batch
setup.bat
```

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

The setup script will:
1. Check prerequisites
2. Create Python virtual environment
3. Install all dependencies (with error handling)
4. Initialize database with sample data
5. Create configuration files

### Step 2: Start OrcheNet

**Option A: Individual Scripts (Recommended)**

Open two terminals/command prompts:

**Terminal 1 - Backend:**
```batch
start-backend.bat     # Windows
./start-backend.sh    # Linux/Mac
```

**Terminal 2 - Frontend:**
```batch
start-frontend.bat    # Windows
./start-frontend.sh   # Linux/Mac
```

**Option B: All-in-One Script**

```bash
./start.sh           # Linux/Mac
start.bat            # Windows
```

### Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Stop Services

**Linux/Mac:**
```bash
./stop.sh
# Or press Ctrl+C in each terminal
```

**Windows:**
```batch
REM Close the terminal windows or press Ctrl+C
```

### Troubleshooting Startup

If you encounter any issues, see **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** for solutions.

## Manual Setup

If you prefer manual setup or the automated scripts don't work:

### 1. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env with your settings

# Initialize database
python init_db.py --seed

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Setup Frontend (New Terminal)

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env
# Edit .env if needed

# Start development server
npm run dev
```

## First Steps

### 1. Access the Web UI

Open http://localhost:5173 in your browser

### 2. Add Your First Device

**Via Web UI:**
1. Click "Firewalls / Routers" in sidebar
2. Click "Add Firewall" button
3. Fill in device details:
   - Name: fw-main
   - Vendor: MikroTik
   - IP Address: 192.168.1.1
   - SSH Username: admin
   - SSH Password: your-password
4. Click "Save"

**Via API:**
```bash
curl -X POST http://localhost:8000/api/devices \
  -H "Content-Type: application/json" \
  -d '{
    "name": "fw-main",
    "vendor": "mikrotik",
    "model": "RB4011",
    "ip_address": "192.168.1.1",
    "ssh_username": "admin",
    "ssh_password": "your-password",
    "check_in_method": "http",
    "check_in_interval": 300
  }'
```

### 3. Test Connection

```bash
curl http://localhost:8000/api/devices
```

You should see your device listed.

### 4. Deploy Device-Side Script

#### For MikroTik:
1. Copy `device-scripts/mikrotik/orchenet-checkin.rsc` to your router
2. Update server URL and API key in the script
3. Install script: `/system script add name=orchenet-checkin source=[/file get orchenet-checkin.rsc contents]`
4. Schedule: `/system scheduler add name=orchenet-checkin interval=5m on-event="/system script run orchenet-checkin"`

#### For FortiGate:
1. Follow instructions in `device-scripts/fortigate/README.md`
2. Configure automation stitch for HTTP check-ins
3. Enable SSH access from OrcheNet server

#### For UniFi:
1. No device-side configuration needed
2. Enter UniFi Controller URL and credentials in device settings
3. OrcheNet polls controller directly

#### For WatchGuard:
1. Enable SSH with allowed-hosts
2. Create admin account for OrcheNet
3. See `device-scripts/watchguard/README.md`

### 5. Push Configuration

**Create configuration YAML:**
```yaml
device:
  name: fw-main
  vendor: mikrotik

system:
  hostname: fw-main
  timezone: America/New_York

interfaces:
  - name: ether1
    enabled: true
    addressing:
      mode: dhcp
    zone: wan

  - name: ether2
    enabled: true
    addressing:
      mode: static
      ipv4:
        address: 192.168.1.1/24
    zone: lan
```

**Push via API:**
```bash
curl -X PUT http://localhost:8000/api/devices/1/config \
  -H "Content-Type: application/json" \
  -d @config.yaml
```

Or use the Web UI Configuration tab.

## Testing the System

### 1. Check Backend Health

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "task_processor": "running"
}
```

### 2. List Devices

```bash
curl http://localhost:8000/api/devices
```

### 3. Create a Test Task

```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": 1,
    "task_type": "status_collection",
    "payload": {}
  }'
```

### 4. Check Task Status

```bash
curl http://localhost:8000/api/tasks
```

### 5. Simulate Device Check-In

```bash
curl -X POST http://localhost:8000/api/checkin \
  -H "Content-Type: application/json" \
  -d '{
    "device_name": "fw-main",
    "vendor": "mikrotik",
    "firmware_version": "7.12",
    "status_data": {
      "cpu": 25,
      "memory": 40
    }
  }'
```

## Common Issues

### Backend Won't Start

**Port Already in Use:**
```bash
# Find process using port 8000
# Linux/Mac:
lsof -i :8000
# Windows:
netstat -ano | findstr :8000

# Kill process or use different port:
uvicorn app.main:app --reload --port 8001
```

**Module Import Errors:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend Won't Start

**Port Already in Use:**
```bash
# Vite will automatically try next available port
# Or specify port in vite.config.js
```

**Dependencies Missing:**
```bash
# Clean install
rm -rf node_modules package-lock.json
npm install
```

### Database Errors

**Database Locked (SQLite):**
```bash
# Stop all running instances
# Delete database file
rm orchenet.db

# Reinitialize
python init_db.py --seed
```

**Switch to PostgreSQL:**
1. Install PostgreSQL
2. Create database: `createdb orchenet`
3. Update `.env`: `DATABASE_URL=postgresql://user:pass@localhost/orchenet`
4. Reinitialize: `python init_db.py`

### SSH Connection Failures

1. Verify device IP is reachable: `ping 192.168.1.1`
2. Test SSH manually: `ssh admin@192.168.1.1`
3. Check firewall allows SSH from OrcheNet server
4. Verify credentials in device configuration
5. Check logs: `tail -f backend.log`

## Next Steps

1. **Configure More Devices**: Add switches, access points, modems
2. **Setup Device Scripts**: Deploy check-in scripts to devices
3. **Create Configurations**: Build YAML configs for your network
4. **Monitor**: Watch Dashboard for device status
5. **Automate**: Set up scheduled configuration updates

## Production Deployment

For production deployment, see:
- `backend/README-DETAILED.md` - Production backend setup
- `IMPLEMENTATION-SUMMARY.md` - Security considerations
- Configure PostgreSQL database
- Set up HTTPS reverse proxy (nginx/Caddy)
- Enable authentication
- Set strong SECRET_KEY
- Configure backups
- Set up monitoring and logging

## Getting Help

- **Documentation**: See `/docs` folder
- **API Docs**: http://localhost:8000/docs
- **Configuration Schemas**: `CONFIG*.md` files
- **Device Setup**: `device-scripts/*/README.md` files
- **Issues**: GitHub Issues (if applicable)

## What's Next?

- **View Logs**: `tail -f backend.log frontend.log`
- **API Documentation**: http://localhost:8000/docs
- **Frontend Code**: `frontend/src/`
- **Backend Code**: `backend/app/`
- **Configuration Examples**: `CONFIG.md`

---

**Your OrcheNet installation is now ready!** 🎉

Visit http://localhost:5173 to start managing your network devices.
