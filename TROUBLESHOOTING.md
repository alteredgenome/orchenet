# OrcheNet Troubleshooting Guide

## Common Startup Issues

### "uvicorn is not recognized" or "vite is not recognized"

This means the packages aren't installed or the virtual environment isn't activated properly.

#### Solution 1: Use Individual Start Scripts

Instead of `start.bat`, use the individual scripts:

**Windows:**
```batch
REM Terminal 1 - Backend
start-backend.bat

REM Terminal 2 - Frontend (in a new terminal)
start-frontend.bat
```

**Linux/Mac:**
```bash
# Terminal 1 - Backend
chmod +x start-backend.sh
./start-backend.sh

# Terminal 2 - Frontend (in a new terminal)
chmod +x start-frontend.sh
./start-frontend.sh
```

#### Solution 2: Manual Setup

**Backend:**
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py --seed

# Start server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend (new terminal):**
```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac

# Start server
npm run dev
```

### Port Already in Use

**Error:** `Address already in use` or `Port 8000 is already allocated`

**Solution:**

**Find and kill the process:**

Windows:
```batch
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

Linux/Mac:
```bash
lsof -i :8000
kill <PID>
```

**Or use different ports:**

Backend:
```bash
python -m uvicorn app.main:app --reload --port 8001
```

Frontend will automatically try next available port (5174, 5175, etc.)

### Python Not Found

**Error:** `python is not recognized`

**Solution:**
1. Install Python 3.9+ from https://python.org
2. During installation, check "Add Python to PATH"
3. Restart your terminal
4. Verify: `python --version` or `python3 --version`

### Node.js Not Found

**Error:** `node is not recognized` or `npm is not recognized`

**Solution:**
1. Install Node.js 18+ from https://nodejs.org
2. Restart your terminal
3. Verify: `node --version` and `npm --version`

### Module Import Errors

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
cd backend
# Make sure virtual environment is activated
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Database Errors

**Error:** `OperationalError: unable to open database file`

**Solution:**
```bash
cd backend

# Make sure you have write permissions
# Create logs directory if needed
mkdir logs  # Linux/Mac
md logs     # Windows

# Initialize database
python init_db.py --seed
```

**Error:** `Database is locked`

**Solution:**
1. Stop all running backend instances
2. Delete database file: `rm orchenet.db` (Linux/Mac) or `del orchenet.db` (Windows)
3. Reinitialize: `python init_db.py --seed`

### Frontend Won't Load

**Error:** Blank page or `Failed to fetch`

**Solution:**
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check browser console (F12) for errors
3. Verify `frontend/.env` has correct `VITE_API_URL`
4. Check CORS settings in `backend/.env`

### CORS Errors

**Error:** `Access to fetch blocked by CORS policy`

**Solution:**

Edit `backend/.env`:
```env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:5174
```

Or in `backend/app/main.py`, temporarily set:
```python
allow_origins=["*"]  # Allow all origins (development only!)
```

## Startup Script Issues

### start.bat Opens and Closes Immediately

**Solution:**
Run from command prompt to see errors:
```batch
cmd
cd C:\path\to\orchenet
start.bat
```

### start.sh: Permission Denied

**Solution:**
```bash
chmod +x start.sh stop.sh start-backend.sh start-frontend.sh
./start.sh
```

### start.sh: Line Endings Error

**Error:** `\r: command not found`

**Solution:** Convert line endings to Unix format:
```bash
dos2unix start.sh
# Or
sed -i 's/\r$//' start.sh
```

## Runtime Issues

### Backend Crashes on Startup

**Check logs:**
```bash
# If running in background
tail -f backend.log

# Or run in foreground to see errors
cd backend
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
python -m uvicorn app.main:app --reload
```

### Task Processor Not Running

**Check health endpoint:**
```bash
curl http://localhost:8000/health
```

Should show: `"task_processor": "running"`

**If not running:**
1. Check backend logs for errors
2. Restart backend
3. Verify no errors in `backend/app/services/task_processor.py`

### SSH Connection Failures

**Error:** `Failed to connect to device`

**Solution:**
1. Verify device is reachable: `ping <device-ip>`
2. Test SSH manually: `ssh admin@<device-ip>`
3. Check firewall allows SSH from OrcheNet server
4. Verify credentials in device configuration
5. Check device allows SSH from your IP

### API Returns 500 Errors

**Solution:**
1. Check backend logs: `tail -f backend.log`
2. Look for Python tracebacks
3. Common causes:
   - Database connection issues
   - Invalid device configuration
   - SSH connection timeouts
   - Missing dependencies

### Tasks Stay Pending

**Possible Causes:**
1. Device not checking in (for HTTP check-in devices)
2. SSH credentials incorrect (for SSH devices)
3. Task processor not running
4. Device unreachable

**Solutions:**
1. Check task processor: `curl http://localhost:8000/health`
2. View pending tasks: `curl http://localhost:8000/api/tasks?status=pending`
3. Check device connectivity
4. Review backend logs for errors

## Performance Issues

### Slow API Response

**Solutions:**
1. Switch from SQLite to PostgreSQL
2. Add database indexes
3. Reduce check-in frequency
4. Limit number of concurrent SSH connections

### High Memory Usage

**Solutions:**
1. Close unused SSH connections
2. Reduce task retention time
3. Clear old completed tasks
4. Restart backend periodically

## Development Issues

### Changes Not Reflected

**Backend:**
- Make sure `--reload` flag is used
- Check for syntax errors in logs
- Restart manually if auto-reload fails

**Frontend:**
- Clear browser cache (Ctrl+F5)
- Check Vite is in dev mode
- Restart npm dev server

### Import Errors After Adding Code

**Solution:**
```bash
# Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

## Clean Reinstall

If all else fails, clean reinstall:

```bash
# Stop everything
./stop.sh  # or close all terminals

# Backend
cd backend
rm -rf venv orchenet.db __pycache__ logs
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python init_db.py --seed

# Frontend
cd ../frontend
rm -rf node_modules package-lock.json .vite
npm install

# Restart
cd ..
./start.sh  # or use individual scripts
```

## Getting Help

If you're still having issues:

1. **Check logs:**
   - `backend.log` - Backend errors
   - `frontend.log` - Frontend errors
   - Browser console (F12) - Frontend JavaScript errors

2. **Verify setup:**
   ```bash
   python --version  # Should be 3.9+
   node --version    # Should be 18+
   npm --version
   ```

3. **Test components individually:**
   - Backend: `curl http://localhost:8000/health`
   - Frontend: Open http://localhost:5173
   - Database: `cd backend && python -c "from app.database import engine; print(engine)"`

4. **Check GitHub Issues:** Search for similar problems

5. **Create Issue:** Include:
   - Operating system and version
   - Python version
   - Node.js version
   - Error messages
   - Relevant log output

## Quick Reference

### Restart Everything
```bash
# Stop
./stop.sh  # or Ctrl+C in terminals

# Start
./start.sh  # or individual scripts
```

### View Logs
```bash
tail -f backend.log
tail -f frontend.log
```

### Reset Database
```bash
cd backend
python init_db.py --drop --seed
```

### Check Status
```bash
# Backend health
curl http://localhost:8000/health

# List devices
curl http://localhost:8000/api/devices

# List tasks
curl http://localhost:8000/api/tasks
```

### Common Ports
- Backend API: 8000
- Frontend UI: 5173 (or 5174, 5175 if taken)
- PostgreSQL: 5432 (if using)
- Redis: 6379 (if using)
