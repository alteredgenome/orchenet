# OrcheNet Testing Guide

This guide covers testing OrcheNet functionality without requiring actual network devices.

## Testing Strategy

OrcheNet can be tested at multiple levels:
1. **API Testing**: Direct API calls
2. **Frontend Testing**: Web UI interaction
3. **Integration Testing**: End-to-end workflows
4. **Mock Device Testing**: Simulated device check-ins

## Prerequisites

- OrcheNet running (see QUICKSTART.md)
- `curl` or Postman for API testing
- Web browser for UI testing

## 1. API Testing

### Health Check

```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "task_processor": "running"
}
```

### Create Test Devices

**MikroTik Device:**
```bash
curl -X POST http://localhost:8000/api/devices \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test-mikrotik",
    "vendor": "mikrotik",
    "model": "RB4011",
    "ip_address": "192.168.1.1",
    "mac_address": "AA:BB:CC:DD:EE:01",
    "ssh_username": "admin",
    "ssh_password": "test123",
    "ssh_port": 22,
    "check_in_method": "http",
    "check_in_interval": 300
  }'
```

**FortiGate Device:**
```bash
curl -X POST http://localhost:8000/api/devices \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test-fortigate",
    "vendor": "fortinet",
    "model": "FortiGate 60E",
    "ip_address": "192.168.2.1",
    "mac_address": "AA:BB:CC:DD:EE:02",
    "ssh_username": "admin",
    "ssh_password": "test123",
    "check_in_method": "http",
    "check_in_interval": 300
  }'
```

**UniFi Device:**
```bash
curl -X POST http://localhost:8000/api/devices \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test-unifi",
    "vendor": "ubiquiti",
    "model": "USW-24-POE",
    "mac_address": "AA:BB:CC:DD:EE:03",
    "api_url": "https://unifi.local:8443",
    "ssh_username": "admin",
    "ssh_password": "test123",
    "check_in_method": "controller",
    "check_in_interval": 300,
    "metadata": {"unifi_site": "default"}
  }'
```

**WatchGuard Device:**
```bash
curl -X POST http://localhost:8000/api/devices \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test-watchguard",
    "vendor": "watchguard",
    "model": "Firebox T35",
    "ip_address": "192.168.3.1",
    "mac_address": "AA:BB:CC:DD:EE:04",
    "ssh_username": "admin",
    "ssh_password": "test123",
    "check_in_method": "ssh",
    "check_in_interval": 600
  }'
```

### List Devices

```bash
curl http://localhost:8000/api/devices
```

**Expected**: Array of devices you created

### Get Specific Device

```bash
curl http://localhost:8000/api/devices/1
```

### Filter Devices

**By vendor:**
```bash
curl "http://localhost:8000/api/devices?vendor=mikrotik"
```

**By status:**
```bash
curl "http://localhost:8000/api/devices?status=online"
```

### Update Device Configuration

```bash
curl -X PUT http://localhost:8000/api/devices/1/config \
  -H "Content-Type: application/json" \
  -d '{
    "device": {
      "name": "test-mikrotik",
      "vendor": "mikrotik"
    },
    "system": {
      "hostname": "test-router",
      "timezone": "America/New_York",
      "dns": {
        "servers": ["8.8.8.8", "1.1.1.1"]
      }
    },
    "interfaces": [
      {
        "name": "ether1",
        "enabled": true,
        "addressing": {
          "mode": "dhcp"
        },
        "zone": "wan"
      },
      {
        "name": "ether2",
        "enabled": true,
        "addressing": {
          "mode": "static",
          "ipv4": {
            "address": "192.168.1.1/24"
          }
        },
        "zone": "lan"
      }
    ]
  }'
```

**Expected**: This creates a task to apply the configuration

### Create Manual Task

**Status Collection Task:**
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": 1,
    "task_type": "status_collection",
    "payload": {}
  }'
```

**Command Execution Task:**
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": 1,
    "task_type": "command_execution",
    "payload": {
      "commands": ["/system resource print", "/interface print"]
    }
  }'
```

### List Tasks

```bash
curl http://localhost:8000/api/tasks
```

**Filter by device:**
```bash
curl "http://localhost:8000/api/tasks?device_id=1"
```

**Filter by status:**
```bash
curl "http://localhost:8000/api/tasks?status=pending"
```

### Retry Failed Task

```bash
curl -X POST http://localhost:8000/api/tasks/1/retry
```

## 2. Simulated Device Check-Ins

### MikroTik Check-In

```bash
curl -X POST http://localhost:8000/api/checkin \
  -H "Content-Type: application/json" \
  -d '{
    "device_name": "test-mikrotik",
    "vendor": "mikrotik",
    "serial_number": "12345678",
    "firmware_version": "7.12.1",
    "status_data": {
      "cpu": 25,
      "memory": 45,
      "uptime": "5d 12h 30m",
      "version": "7.12.1",
      "board": "RB4011"
    }
  }'
```

**Expected**: Returns array of pending tasks for the device

### FortiGate Check-In

```bash
curl -X POST http://localhost:8000/api/checkin \
  -H "Content-Type: application/json" \
  -d '{
    "device_name": "test-fortigate",
    "vendor": "fortinet",
    "serial_number": "FG60E-87654321",
    "firmware_version": "v7.4.1",
    "status_data": {
      "cpu": 15,
      "memory": 35,
      "sessions": 1234
    }
  }'
```

### Submit Task Result

After check-in returns tasks, simulate task completion:

```bash
curl -X POST http://localhost:8000/api/checkin/result/1 \
  -H "Content-Type: application/json" \
  -d '{
    "success": true,
    "result": {
      "commands_executed": 5,
      "status": "completed",
      "message": "Configuration applied successfully"
    }
  }'
```

**For failed task:**
```bash
curl -X POST http://localhost:8000/api/checkin/result/2 \
  -H "Content-Type: application/json" \
  -d '{
    "success": false,
    "error_message": "Connection timeout"
  }'
```

## 3. Testing Configuration Translation

### Test MikroTik Translation

Create a file `test-config.yaml`:
```yaml
device:
  name: test-router
  vendor: mikrotik

system:
  hostname: test-router
  timezone: America/New_York
  dns:
    servers:
      - 8.8.8.8
      - 1.1.1.1
  ntp:
    servers:
      - pool.ntp.org

interfaces:
  - name: ether1
    enabled: true
    description: "WAN Interface"
    addressing:
      mode: dhcp
    zone: wan

  - name: ether2
    enabled: true
    description: "LAN Interface"
    addressing:
      mode: static
      ipv4:
        address: 192.168.1.1/24
    zone: lan

firewall:
  policies:
    - name: "Allow LAN to WAN"
      source_zone: lan
      destination_zone: wan
      action: accept
      nat: true
      log: true

    - name: "Block WAN to LAN"
      source_zone: wan
      destination_zone: lan
      action: drop
      log: true
```

**Push configuration:**
```bash
curl -X PUT http://localhost:8000/api/devices/1/config \
  -H "Content-Type: application/json" \
  -d @test-config.yaml
```

**Check task was created:**
```bash
curl "http://localhost:8000/api/tasks?device_id=1&status=pending"
```

## 4. Frontend Testing

### Access Web UI

Open http://localhost:5173 in your browser

### Test Dashboard

1. Navigate to Dashboard
2. Verify stats cards show correct counts
3. Check device type cards display
4. Verify alerts table is visible

### Test Device List

1. Click "Firewalls / Routers"
2. Verify device table shows your test devices
3. Check status badges display correctly
4. Try filtering/searching

### Test Device Details

1. Click on a device name
2. Verify all tabs are accessible:
   - Overview
   - Configuration
   - Interfaces
   - Policies
   - VPN
   - Logs
   - History
3. Try editing configuration in YAML editor
4. Save changes and verify task is created

### Test Task View

1. View pending tasks
2. Check task status updates
3. Verify completed/failed tasks display correctly

## 5. End-to-End Workflow Test

### Complete Device Lifecycle

1. **Create Device**
```bash
curl -X POST http://localhost:8000/api/devices \
  -H "Content-Type: application/json" \
  -d '{
    "name": "lifecycle-test",
    "vendor": "mikrotik",
    "model": "hEX",
    "ip_address": "192.168.100.1",
    "ssh_username": "admin",
    "ssh_password": "test",
    "check_in_method": "http"
  }'
```

2. **Verify Device Created**
```bash
curl http://localhost:8000/api/devices | grep lifecycle-test
```

3. **Push Configuration**
```bash
curl -X PUT http://localhost:8000/api/devices/{id}/config \
  -H "Content-Type: application/json" \
  -d '{"device": {"name": "lifecycle-test", "vendor": "mikrotik"}, "system": {"hostname": "test"}}'
```

4. **Check Task Created**
```bash
curl "http://localhost:8000/api/tasks?device_id={id}"
```

5. **Simulate Check-In**
```bash
curl -X POST http://localhost:8000/api/checkin \
  -H "Content-Type: application/json" \
  -d '{"device_name": "lifecycle-test", "vendor": "mikrotik"}'
```

6. **Verify Task Returned**
- Check response includes pending task

7. **Submit Task Result**
```bash
curl -X POST http://localhost:8000/api/checkin/result/{task_id} \
  -H "Content-Type: application/json" \
  -d '{"success": true, "result": {"status": "completed"}}'
```

8. **Verify Task Completed**
```bash
curl http://localhost:8000/api/tasks/{task_id}
```

9. **Delete Device**
```bash
curl -X DELETE http://localhost:8000/api/devices/{id}
```

## 6. Error Handling Tests

### Invalid Device Data

```bash
curl -X POST http://localhost:8000/api/devices \
  -H "Content-Type: application/json" \
  -d '{
    "name": "",
    "vendor": "invalid"
  }'
```

**Expected**: HTTP 422 with validation errors

### Non-Existent Device

```bash
curl http://localhost:8000/api/devices/99999
```

**Expected**: HTTP 404 Not Found

### Invalid Configuration

```bash
curl -X PUT http://localhost:8000/api/devices/1/config \
  -H "Content-Type: application/json" \
  -d '{"invalid": "config"}'
```

**Expected**: Task created but will fail validation

### Check Task Failed

```bash
curl "http://localhost:8000/api/tasks?status=failed"
```

## 7. Performance Testing

### Bulk Device Creation

```bash
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/devices \
    -H "Content-Type: application/json" \
    -d "{
      \"name\": \"bulk-device-$i\",
      \"vendor\": \"mikrotik\",
      \"ip_address\": \"192.168.$i.1\"
    }"
done
```

### Concurrent Check-Ins

```bash
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/checkin \
    -H "Content-Type: application/json" \
    -d "{\"device_name\": \"bulk-device-$i\", \"vendor\": \"mikrotik\"}" &
done
wait
```

## 8. Task Processor Testing

### Verify Task Processor Running

```bash
curl http://localhost:8000/health
```

**Expected**: `"task_processor": "running"`

### Monitor Task Processing

1. Create several tasks
2. Watch them transition from pending → in_progress → completed
3. Check logs for processing messages

**Watch logs:**
```bash
tail -f backend.log | grep "Task"
```

## 9. Database Testing

### View Database Contents

**SQLite:**
```bash
cd backend
sqlite3 orchenet.db

.tables
SELECT * FROM devices;
SELECT * FROM tasks;
.quit
```

### Test Database Initialization

```bash
cd backend
python init_db.py --drop --seed
```

**Expected**: Database dropped and recreated with sample data

## 10. Cleanup

### Delete All Test Data

```bash
# Delete all devices
for id in $(curl -s http://localhost:8000/api/devices | jq '.[].id'); do
  curl -X DELETE http://localhost:8000/api/devices/$id
done

# Or reinitialize database
cd backend
python init_db.py --drop --seed
```

## Test Checklist

- [ ] Backend starts without errors
- [ ] Frontend loads successfully
- [ ] Health endpoint returns healthy
- [ ] Can create devices for all 4 vendors
- [ ] Can list and filter devices
- [ ] Can update device configuration
- [ ] Tasks are created automatically
- [ ] Can create manual tasks
- [ ] Simulated check-ins work
- [ ] Task results can be submitted
- [ ] Task processor processes tasks
- [ ] Frontend displays devices correctly
- [ ] Frontend device details work
- [ ] Configuration YAML editor works
- [ ] All API endpoints respond correctly
- [ ] Error handling works as expected
- [ ] Database persists data
- [ ] Logs show expected output

## Troubleshooting Test Issues

### API Returns 500 Errors

Check backend logs:
```bash
tail -f backend.log
```

### Frontend Can't Connect to API

1. Verify backend is running: `curl http://localhost:8000/health`
2. Check CORS settings in backend/.env
3. Verify VITE_API_URL in frontend/.env

### Tasks Stay in Pending

1. Check task processor is running: `curl http://localhost:8000/health`
2. Check backend logs for errors
3. Verify device connection details are correct

### Database Errors

1. Stop backend
2. Delete database: `rm backend/orchenet.db`
3. Reinitialize: `cd backend && python init_db.py --seed`
4. Restart backend

## Next Steps

After testing:
1. Deploy device-side scripts to real devices
2. Configure actual device credentials
3. Test with real network equipment
4. Monitor logs for issues
5. Adjust configuration as needed

---

**Testing Complete!**

If all tests pass, your OrcheNet installation is working correctly and ready for production use with real devices.
