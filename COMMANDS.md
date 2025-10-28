# OrcheNet Command Reference

Quick reference for common commands and operations.

## Starting OrcheNet

### Automated Start

```bash
# All-in-one (may have PATH issues)
./start.sh          # Linux/Mac
start.bat           # Windows

# Individual components (recommended)
./start-backend.sh  # Linux/Mac
start-backend.bat   # Windows

./start-frontend.sh # Linux/Mac (new terminal)
start-frontend.bat  # Windows (new terminal)
```

### Manual Start

**Backend:**
```bash
cd backend
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm run dev
```

## Database Operations

### Initialize Database
```bash
cd backend
python init_db.py
```

### Initialize with Sample Data
```bash
python init_db.py --seed
```

### Reset Database (DESTRUCTIVE)
```bash
python init_db.py --drop --seed
```

### View Database (SQLite)
```bash
sqlite3 orchenet.db
.tables
SELECT * FROM devices;
SELECT * FROM tasks;
.quit
```

## API Commands

### Health Check
```bash
curl http://localhost:8000/health
```

### List All Devices
```bash
curl http://localhost:8000/api/devices
```

### Get Device by ID
```bash
curl http://localhost:8000/api/devices/1
```

### Create Device
```bash
curl -X POST http://localhost:8000/api/devices \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test-device",
    "vendor": "mikrotik",
    "model": "RB4011",
    "ip_address": "192.168.1.1",
    "ssh_username": "admin",
    "ssh_password": "password",
    "check_in_method": "http",
    "check_in_interval": 300
  }'
```

### Update Device Configuration
```bash
curl -X PUT http://localhost:8000/api/devices/1/config \
  -H "Content-Type: application/json" \
  -d @config.json
```

### Delete Device
```bash
curl -X DELETE http://localhost:8000/api/devices/1
```

### List Tasks
```bash
curl http://localhost:8000/api/tasks
```

### List Tasks for Device
```bash
curl "http://localhost:8000/api/tasks?device_id=1"
```

### Create Task
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": 1,
    "task_type": "status_collection",
    "payload": {}
  }'
```

### Retry Failed Task
```bash
curl -X POST http://localhost:8000/api/tasks/1/retry
```

### Device Check-In
```bash
curl -X POST http://localhost:8000/api/checkin \
  -H "Content-Type: application/json" \
  -d '{
    "device_name": "test-device",
    "vendor": "mikrotik",
    "firmware_version": "7.12",
    "status_data": {"cpu": 25, "memory": 40}
  }'
```

### Submit Task Result
```bash
curl -X POST http://localhost:8000/api/checkin/result/1 \
  -H "Content-Type: application/json" \
  -d '{"success": true, "result": {"status": "completed"}}'
```

## Development Commands

### Backend

**Activate Virtual Environment:**
```bash
cd backend
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

**Install Dependencies:**
```bash
pip install -r requirements.txt
```

**Run Tests:**
```bash
pytest
```

**Format Code:**
```bash
black app/
isort app/
```

**Type Check:**
```bash
mypy app/
```

### Frontend

**Install Dependencies:**
```bash
cd frontend
npm install
```

**Run Development Server:**
```bash
npm run dev
```

**Build for Production:**
```bash
npm run build
```

**Preview Production Build:**
```bash
npm run preview
```

**Lint Code:**
```bash
npm run lint
```

## Logging

### View Logs
```bash
tail -f backend.log
tail -f frontend.log
```

### Clear Logs
```bash
> backend.log  # Or: echo. > backend.log (Windows)
> frontend.log
```

## Process Management

### Find Process Using Port
```bash
# Linux/Mac
lsof -i :8000
lsof -i :5173

# Windows
netstat -ano | findstr :8000
netstat -ano | findstr :5173
```

### Kill Process
```bash
# Linux/Mac
kill <PID>
kill -9 <PID>  # Force kill

# Windows
taskkill /PID <PID> /F
```

## System Information

### Check Python Version
```bash
python --version
python3 --version
```

### Check Node Version
```bash
node --version
npm --version
```

### Check Installed Packages
```bash
# Backend
cd backend
source venv/bin/activate
pip list

# Frontend
cd frontend
npm list --depth=0
```

## Cleanup Commands

### Clean Backend
```bash
cd backend
rm -rf venv __pycache__ *.db logs/*.log
# Windows: rmdir /s venv & del *.db
```

### Clean Frontend
```bash
cd frontend
rm -rf node_modules .vite dist
# Windows: rmdir /s node_modules .vite dist
```

### Clean Everything
```bash
# Stop services first!
./stop.sh

# Then clean
rm -rf backend/venv backend/__pycache__ backend/*.db
rm -rf frontend/node_modules frontend/.vite frontend/dist
rm -f *.log *.pid

# Windows equivalent:
# rmdir /s backend\venv frontend\node_modules
# del backend\*.db *.log *.pid
```

## Git Commands

### Check Status
```bash
git status
```

### View Changes
```bash
git diff
```

### Commit Changes
```bash
git add .
git commit -m "Description of changes"
```

### Push to Remote
```bash
git push origin main
```

### Pull Latest
```bash
git pull origin main
```

## Environment Management

### Copy Environment Files
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Windows:
# copy backend\.env.example backend\.env
# copy frontend\.env.example frontend\.env
```

### Edit Environment Files
```bash
# Linux/Mac
nano backend/.env
nano frontend/.env

# Windows
notepad backend\.env
notepad frontend\.env
```

## Quick Diagnostics

### Full System Check
```bash
# Prerequisites
python --version
node --version
npm --version

# Backend
cd backend
source venv/bin/activate
python -c "import fastapi; print('FastAPI OK')"
python -c "from app.database import engine; print('Database OK')"

# Frontend
cd ../frontend
npm list react --depth=0

# Services
curl http://localhost:8000/health
curl http://localhost:5173
```

### Check All Services
```bash
# Backend
curl -s http://localhost:8000/health | grep healthy

# Frontend
curl -s http://localhost:5173 | grep -i orchenet

# Database
cd backend && python -c "from app.database import SessionLocal; db = SessionLocal(); print(f'Devices: {len(db.query(__import__(\"app.models.device\", fromlist=[\"Device\"]).Device).all())}')"
```

## URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:5173 | Main Web UI |
| Backend API | http://localhost:8000 | REST API |
| API Docs (Swagger) | http://localhost:8000/docs | Interactive API documentation |
| API Docs (ReDoc) | http://localhost:8000/redoc | Alternative API documentation |
| Health Check | http://localhost:8000/health | Backend health status |

## Common Workflows

### Add New Device
```bash
# 1. Create device
curl -X POST http://localhost:8000/api/devices -H "Content-Type: application/json" -d @device.json

# 2. Get device ID from response
# 3. Push configuration
curl -X PUT http://localhost:8000/api/devices/{id}/config -H "Content-Type: application/json" -d @config.json

# 4. Check task created
curl "http://localhost:8000/api/tasks?device_id={id}"
```

### Monitor Device
```bash
# Check device status
curl http://localhost:8000/api/devices/1

# Check recent tasks
curl "http://localhost:8000/api/tasks?device_id=1&limit=10"

# Simulate check-in
curl -X POST http://localhost:8000/api/checkin -H "Content-Type: application/json" -d '{...}'
```

### Troubleshoot Failed Task
```bash
# Get task details
curl http://localhost:8000/api/tasks/1

# Check error message
curl http://localhost:8000/api/tasks/1 | jq '.error_message'

# Retry task
curl -X POST http://localhost:8000/api/tasks/1/retry
```

## Keyboard Shortcuts

### Terminal
- `Ctrl+C` - Stop current process
- `Ctrl+Z` - Suspend current process
- `Ctrl+D` - Exit shell/logout

### Browser (DevTools)
- `F12` - Open developer tools
- `Ctrl+Shift+R` - Hard reload (bypass cache)
- `Ctrl+Shift+C` - Inspect element

## File Locations

| File | Location | Purpose |
|------|----------|---------|
| Database | `backend/orchenet.db` | SQLite database |
| Backend Logs | `backend.log` | Backend server logs |
| Frontend Logs | `frontend.log` | Frontend server logs |
| Backend Config | `backend/.env` | Backend environment variables |
| Frontend Config | `frontend/.env` | Frontend environment variables |
| Device Scripts | `device-scripts/*/` | Device-side check-in scripts |

## Quick Reference Card

```
Start:    ./start-backend.sh && ./start-frontend.sh
Stop:     Ctrl+C (or ./stop.sh)
Health:   curl localhost:8000/health
Devices:  curl localhost:8000/api/devices
Tasks:    curl localhost:8000/api/tasks
Logs:     tail -f backend.log
Reset DB: cd backend && python init_db.py --drop --seed
UI:       http://localhost:5173
API:      http://localhost:8000
Docs:     http://localhost:8000/docs
```
