# Temperature API Service

A simple Go-based microservice that simulates temperature sensor readings for the Smart Home IoT Ecosystem.

## Overview

The Temperature API service provides random temperature data for different locations within a smart home environment. It's designed to simulate external temperature sensors and integrate with the main smart home application.

## Features

- **REST API endpoints** for temperature data retrieval
- **Location-based temperature simulation** with realistic ranges
- **Time-based variations** (day/night cycles)
- **Health check endpoint** for monitoring
- **Docker containerization** for easy deployment
- **CORS support** for web applications
- **JSON response format** with comprehensive metadata

## API Endpoints

### GET /health
Health check endpoint for monitoring service status.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

### GET /temperature?location={location}
Get temperature reading for a specific location.

**Parameters:**
- `location` (required): The location name (e.g., "living_room", "bedroom", "kitchen")

**Response:**
```json
{
  "value": 22.5,
  "unit": "°C",
  "timestamp": "2024-01-15T10:30:00Z",
  "location": "living_room",
  "status": "active",
  "sensor_id": "sensor-living_room-123",
  "sensor_type": "temperature",
  "description": "Temperature reading for living_room"
}
```

### GET /temperature/{sensorId}
Get temperature reading from a specific sensor ID.

**Parameters:**
- `sensorId` (path): The sensor identifier

**Response:**
```json
{
  "value": 20.8,
  "unit": "°C",
  "timestamp": "2024-01-15T10:30:00Z",
  "location": "bedroom",
  "status": "active",
  "sensor_id": "TEMP002",
  "sensor_type": "temperature",
  "description": "Temperature reading from sensor TEMP002"
}
```

## Temperature Simulation

The service generates realistic temperature values based on:

- **Location type**: Different base temperatures for different rooms
  - Living Room: 22°C ± 3°C
  - Bedroom: 20°C ± 2.5°C
  - Kitchen: 24°C ± 4°C
  - Bathroom: 23°C ± 2°C
  - Garage: 15°C ± 8°C
  - Outdoor: 10°C ± 15°C
  - Default: 21°C ± 4°C

- **Time variations**: Day/night cycle adjustments
  - Daytime (6:00-18:00): +1°C
  - Nighttime (18:00-6:00): -1°C

- **Random variations**: Within realistic ranges for each location type

## Configuration

The service can be configured using environment variables:

- `PORT`: Server port (default: 8081)
- `GIN_MODE`: Gin framework mode (default: release)

## Docker Support

### Building the Image
```bash
docker build -t temperature-api .
```

### Running the Container
```bash
docker run -p 8081:8081 temperature-api
```

### Using Docker Compose
The service is integrated into the main docker-compose.yml file:

```yaml
temperature-api:
  build:
    context: ./temperature-api
    dockerfile: Dockerfile
  container_name: smarthome-temperature-api
  environment:
    - PORT=8081
    - GIN_MODE=release
  ports:
    - "8081:8081"
  healthcheck:
    test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:8081/health"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 40s
  restart: unless-stopped
  networks:
    - smarthome-network
```

## Development

### Prerequisites
- Go 1.21 or later
- Docker (for containerization)

### Local Development
```bash
# Install dependencies
go mod download

# Run the service
go run main.go

# The service will be available at http://localhost:8081
```

### Testing the API
```bash
# Health check
curl http://localhost:8081/health

# Get temperature for living room
curl "http://localhost:8081/temperature?location=living_room"

# Get temperature by sensor ID
curl http://localhost:8081/temperature/TEMP001
```

## Integration with Smart Home Application

The temperature-api service is designed to integrate with the main smart home application through:

1. **Service Discovery**: The main application connects to `http://temperature-api:8081` within the Docker network
2. **Environment Variables**: The main app uses `TEMPERATURE_API_URL=http://temperature-api:8081`
3. **Health Monitoring**: Regular health checks ensure service availability
4. **Data Format**: Consistent JSON response format for easy parsing

## Security Considerations

- **CORS enabled** for cross-origin requests
- **Non-root user** in Docker container for security
- **Health checks** for monitoring and alerting
- **Input validation** for location parameters
- **Error handling** for invalid requests

## Monitoring and Logging

- **Health check endpoint** for uptime monitoring
- **Structured logging** with Gin framework
- **Docker health checks** for container orchestration
- **Graceful error responses** with appropriate HTTP status codes

## Future Enhancements

- **Authentication/Authorization** for secure access
- **Rate limiting** to prevent abuse
- **Metrics collection** for monitoring
- **Configuration management** for different environments
- **Database persistence** for historical data
- **WebSocket support** for real-time updates
- **Multiple sensor types** (humidity, pressure, etc.)