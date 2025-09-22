# Smart Home Microservices Testing Guide

This document describes how to test all the microservices in the Smart Home IoT ecosystem using the provided curl test scripts.

## Prerequisites

1. **All microservices must be running**:
   ```bash
   cd apps
   docker-compose up -d
   ```

2. **Wait for services to be healthy**:
   ```bash
   docker-compose ps
   ```
   All services should show "healthy" status.

3. **Required tools**:
   - `curl` (for HTTP requests)
   - `bash` (for running scripts)

## Test Scripts

### 1. Quick Health Check (`quick-test.sh`)

**Purpose**: Fast health check of all microservices

**Usage**:
```bash
./quick-test.sh
```

**What it tests**:
- ✅ Service health endpoints
- ✅ Basic API functionality
- ✅ Service connectivity

**Expected output**:
```
Smart Home Microservices - Quick Health Check
=============================================
Checking Device Service... ✓ HEALTHY
Checking Telemetry Service... ✓ HEALTHY
Checking Temperature API... ✓ HEALTHY
Checking Smart Home Service... ✓ HEALTHY

Quick API Tests:
Temperature API... ✓ OK
Smart Home Sensors... ✓ OK
Device Service... ✓ OK

Summary:
🎉 All services are healthy and responding!
```

### 2. Comprehensive Test Suite (`test-microservices.sh`)

**Purpose**: Complete testing of all microservice endpoints

**Usage**:
```bash
./test-microservices.sh
```

**What it tests**:

#### Health Checks
- Device Service health endpoint
- Telemetry Service health endpoint
- Temperature API health endpoint
- Smart Home Service health endpoint

#### Temperature API Tests
- Get temperature by location
- Get temperature by sensor ID
- Error handling for missing parameters

#### Smart Home Service Tests
- CRUD operations for sensors
- Temperature integration
- Sensor value updates

#### Device Service Tests
- CRUD operations for devices
- Device command management
- Device status updates
- Search and filtering
- Battery and connectivity monitoring

#### Telemetry Service Tests
- Store single telemetry data
- Store telemetry batches
- Query telemetry data
- Aggregated telemetry queries
- Device alerts

#### Integration Tests
- Cross-service communication
- Data consistency
- Error handling

## Service Endpoints

### Device Service (Port 8081)
```
Base URL: http://localhost:8081

Health: GET /device-service/actuator/health
Devices: GET /api/v1/devices
Device by ID: GET /api/v1/devices/{id}
Create Device: POST /api/v1/devices
Update Device: PUT /api/v1/devices/{id}
Delete Device: DELETE /api/v1/devices/{id}
Device Commands: POST /api/v1/devices/{id}/commands
Search Devices: GET /api/v1/devices/search?q={query}
Low Battery: GET /api/v1/devices/low-battery
Offline Devices: GET /api/v1/devices/offline
```

### Telemetry Service (Port 8082)
```
Base URL: http://localhost:8082

Health: GET /health
Store Telemetry: POST /api/v1/telemetry
Store Batch: POST /api/v1/telemetry/batch
Get Telemetry: GET /api/v1/telemetry/{device_id}
Latest Data: GET /api/v1/telemetry/{device_id}/latest
Aggregated: GET /api/v1/telemetry/{device_id}/aggregated
Device Alerts: GET /api/v1/devices/{device_id}/alerts
```

### Temperature API (Port 8083)
```
Base URL: http://localhost:8083

Health: GET /health
Temperature by Location: GET /temperature?location={location}
Temperature by Sensor: GET /temperature/{sensorId}
```

### Smart Home Service (Port 8080)
```
Base URL: http://localhost:8080

Health: GET /health
Sensors: GET /api/v1/sensors
Sensor by ID: GET /api/v1/sensors/{id}
Create Sensor: POST /api/v1/sensors
Update Sensor: PUT /api/v1/sensors/{id}
Delete Sensor: DELETE /api/v1/sensors/{id}
Update Value: PATCH /api/v1/sensors/{id}/value
Temperature: GET /api/v1/sensors/temperature/{location}
```

## Sample Test Data

### Device Creation
```json
{
  "name": "Smart Thermostat",
  "deviceType": "THERMOSTAT",
  "homeId": "123e4567-e89b-12d3-a456-426614174000",
  "roomId": "123e4567-e89b-12d3-a456-426614174001",
  "status": "ONLINE",
  "batteryLevel": 85,
  "firmwareVersion": "1.2.3",
  "manufacturer": "TestCorp",
  "model": "TC-THERM-001"
}
```

### Sensor Creation
```json
{
  "name": "Living Room Temperature",
  "type": "temperature",
  "location": "Living Room",
  "unit": "°C"
}
```

### Telemetry Data
```json
{
  "device_id": "123e4567-e89b-12d3-a456-426614174000",
  "measurement": "temperature",
  "value": 22.5,
  "unit": "°C",
  "timestamp": "2024-01-01T12:00:00Z",
  "location": "living_room",
  "metadata": {
    "sensor_type": "DHT22",
    "accuracy": "±0.5°C"
  }
}
```

### Device Command
```json
{
  "commandType": "TURN_ON",
  "parameters": "{\"brightness\":80}",
  "issuedBy": "123e4567-e89b-12d3-a456-426614174002"
}
```

## Manual Testing Examples

### Test Temperature API
```bash
# Get temperature for living room
curl "http://localhost:8083/temperature?location=living_room"

# Get temperature by sensor ID
curl "http://localhost:8083/temperature/sensor-bedroom-001"
```

### Test Device Service
```bash
# Get all devices
curl "http://localhost:8081/api/v1/devices"

# Create a new device
curl -X POST "http://localhost:8081/api/v1/devices" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Light","deviceType":"LIGHT","homeId":"123e4567-e89b-12d3-a456-426614174000","status":"ONLINE"}'
```

### Test Telemetry Service
```bash
# Store telemetry data
curl -X POST "http://localhost:8082/api/v1/telemetry" \
  -H "Content-Type: application/json" \
  -d '{"device_id":"test-device","measurement":"temperature","value":23.5,"unit":"°C","timestamp":"2024-01-01T12:00:00Z"}'

# Get latest telemetry
curl "http://localhost:8082/api/v1/telemetry/test-device/latest"
```

## Troubleshooting

### Services Not Responding
1. Check if containers are running:
   ```bash
   docker-compose ps
   ```

2. Check container logs:
   ```bash
   docker-compose logs [service-name]
   ```

3. Restart services:
   ```bash
   docker-compose restart
   ```

### Port Conflicts
If ports are already in use, modify the port mappings in `docker-compose.yml`:
- Device Service: 8081
- Telemetry Service: 8082 (bound to 127.0.0.1)
- Temperature API: 8083
- Smart Home Service: 8080

### Database Issues
1. Check database health:
   ```bash
   docker-compose exec postgres pg_isready
   docker-compose exec device-postgres pg_isready
   ```

2. Reset databases:
   ```bash
   docker-compose down -v
   docker-compose up -d
   ```

## Expected Test Results

- **Quick Test**: Should complete in ~5 seconds with all services healthy
- **Full Test Suite**: Should complete in ~30-60 seconds with 40+ tests passing
- **Success Rate**: 100% when all services are properly configured and running

## Integration Points

The test scripts verify these integration points:
1. **Smart Home ↔ Temperature API**: Temperature data retrieval
2. **Device Service ↔ Telemetry Service**: Device telemetry storage
3. **All Services ↔ Databases**: Data persistence and retrieval
4. **All Services ↔ Redis**: Caching and message queuing

## Monitoring

For ongoing monitoring, you can:
1. Run `quick-test.sh` periodically for health checks
2. Use the full test suite for regression testing
3. Monitor individual service logs for errors
4. Check database connectivity and performance

---

**Note**: These test scripts create and clean up test data automatically. However, some test data may persist if tests are interrupted. You can manually clean up using the DELETE endpoints or by resetting the databases.
