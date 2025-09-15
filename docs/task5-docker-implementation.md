# Task 5: Docker Implementation and Temperature API Service

## Overview

Task 5 focuses on creating a practical implementation of a microservice with Docker containerization. This task demonstrates the transition from architectural design to actual implementation by creating a temperature-api service that simulates IoT sensor data.

## Objectives

1. **Create Temperature API Service**: Implement a simple microservice that returns random temperature values
2. **Docker Containerization**: Package the service in a Docker container running on port 8081
3. **Database Integration**: Configure PostgreSQL database with initialization scripts
4. **Service Orchestration**: Update docker-compose.yml to orchestrate all services
5. **Integration Testing**: Verify the system works with the existing Postman collection

## Implementation Details

### 1. Temperature API Service

**Location**: [`apps/temperature-api/`](../apps/temperature-api/)

**Technology Stack**:
- **Language**: Go 1.21
- **Framework**: Gin (lightweight HTTP web framework)
- **Architecture**: RESTful API with JSON responses
- **Port**: 8081 (as specified in requirements)

**Key Features**:
- Location-based temperature simulation with realistic ranges
- Time-based variations (day/night cycles)
- Multiple API endpoints for different access patterns
- Health check endpoint for monitoring
- CORS support for web integration
- Comprehensive error handling

**API Endpoints**:

```http
GET /health
# Health check endpoint
Response: {"status": "ok", "timestamp": "...", "version": "1.0.0"}

GET /temperature?location={location}
# Get temperature by location
Response: {
  "value": 22.5,
  "unit": "°C",
  "timestamp": "2024-01-15T10:30:00Z",
  "location": "living_room",
  "status": "active",
  "sensor_id": "sensor-living_room-123",
  "sensor_type": "temperature",
  "description": "Temperature reading for living_room"
}

GET /temperature/{sensorId}
# Get temperature by sensor ID
Response: Similar to above with sensor-specific data
```

**Temperature Simulation Logic**:
- **Living Room**: 22°C ± 3°C
- **Bedroom**: 20°C ± 2.5°C
- **Kitchen**: 24°C ± 4°C
- **Bathroom**: 23°C ± 2°C
- **Garage**: 15°C ± 8°C
- **Outdoor**: 10°C ± 15°C
- **Time Variations**: ±1°C for day/night cycles

### 2. Docker Implementation

**Dockerfile Features**:
- **Multi-stage build** for optimized image size
- **Alpine Linux** base image for security and size
- **Non-root user** for security best practices
- **Health check** integration
- **Environment variable** configuration
- **Static binary** compilation for portability

**Build Process**:
```dockerfile
# Build stage with Go 1.21
FROM golang:1.21-alpine AS builder
# ... build process ...

# Runtime stage with minimal Alpine
FROM alpine:latest
# ... runtime configuration ...
```

**Security Measures**:
- Non-root user execution
- Minimal attack surface with Alpine
- No unnecessary packages
- Health check monitoring

### 3. PostgreSQL Database Configuration

**Database Setup**:
- **Image**: PostgreSQL 16 Alpine
- **Database**: `smarthome`
- **Credentials**: postgres/postgres (development only)
- **Port**: 5432
- **Volume**: Persistent data storage

**Initialization Script** ([`apps/postgres-init/init.sql`](../apps/postgres-init/init.sql)):
- **Complete schema** based on ER diagrams from Task 3
- **Sample data** for testing and development
- **Indexes** for performance optimization
- **Triggers** for automatic timestamp updates
- **Extensions** (uuid-ossp, pgcrypto) for advanced features

**Database Schema Highlights**:
- **Users**: Authentication and user management
- **Homes & Rooms**: Hierarchical structure
- **Devices & Device Types**: IoT device management
- **Sensor Readings**: Time-series data storage
- **Automation Rules**: Business logic storage
- **Notifications**: User communication

### 4. Docker Compose Orchestration

**Services Configuration**:

```yaml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_DB=smarthome
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./postgres-init:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d smarthome"]
      interval: 10s
      timeout: 5s
      retries: 5

  temperature-api:
    build:
      context: ./temperature-api
      dockerfile: Dockerfile
    environment:
      - PORT=8081
      - GIN_MODE=release
    ports:
      - "8081:8081"
    healthcheck:
      test: ["CMD", "wget", "--spider", "http://localhost:8081/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  app:
    build:
      context: ./smart_home
      dockerfile: Dockerfile
    depends_on:
      postgres:
        condition: service_healthy
      temperature-api:
        condition: service_started
    environment:
      - DATABASE_URL=postgres://postgres:postgres@postgres:5432/smarthome
      - TEMPERATURE_API_URL=http://temperature-api:8081
    ports:
      - "8080:8080"
```

**Key Features**:
- **Health checks** for all services
- **Service dependencies** with proper startup order
- **Network isolation** with custom bridge network
- **Volume persistence** for database data
- **Environment variable** configuration
- **Port mapping** for external access

### 5. Integration Architecture

**Service Communication**:
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Smart Home    │    │  Temperature API │    │   PostgreSQL    │
│   Application   │◄──►│    Service       │    │    Database     │
│   (Port 8080)   │    │   (Port 8081)    │    │   (Port 5432)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  │
                        ┌─────────▼─────────┐
                        │  Docker Network   │
                        │ smarthome-network │
                        └───────────────────┘
```

**Data Flow**:
1. **Client Request** → Smart Home App (port 8080)
2. **Temperature Query** → Smart Home App → Temperature API (port 8081)
3. **Database Operations** → Smart Home App → PostgreSQL (port 5432)
4. **Response** → Smart Home App → Client

## Testing Strategy

### Manual Testing Commands

```bash
# Start all services
docker-compose up -d

# Check service health
curl http://localhost:8081/health
curl http://localhost:8080/health

# Test temperature API
curl "http://localhost:8081/temperature?location=living_room"
curl "http://localhost:8081/temperature/TEMP001"

# Check database connection
docker-compose exec postgres psql -U postgres -d smarthome -c "SELECT COUNT(*) FROM devices;"
```

### Postman Collection Integration

The existing Postman collection ([`apps/smarthome-api.postman_collection.json`](../apps/smarthome-api.postman_collection.json)) can be used to test:

1. **Smart Home API endpoints** (port 8080)
2. **Temperature API endpoints** (port 8081)
3. **Database integration** through the main application
4. **End-to-end workflows** with real data

### Expected Test Results

**Temperature API Response**:
```json
{
  "value": 22.3,
  "unit": "°C",
  "timestamp": "2024-01-15T10:30:00Z",
  "location": "living_room",
  "status": "active",
  "sensor_id": "sensor-living_room-456",
  "sensor_type": "temperature",
  "description": "Temperature reading for living_room"
}
```

**Database Verification**:
- Tables created successfully
- Sample data inserted
- Indexes and triggers functional
- Foreign key constraints working

## Deployment Instructions

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- Available ports: 8080, 8081, 5432

### Step-by-Step Deployment

1. **Clone Repository**:
   ```bash
   git clone <repository-url>
   cd microservices-iot-ecosystem/apps
   ```

2. **Build and Start Services**:
   ```bash
   docker-compose up --build -d
   ```

3. **Verify Services**:
   ```bash
   docker-compose ps
   docker-compose logs temperature-api
   docker-compose logs postgres
   ```

4. **Test Integration**:
   ```bash
   # Test temperature API
   curl "http://localhost:8081/temperature?location=bedroom"
   
   # Test main application
   curl http://localhost:8080/api/devices
   ```

5. **Monitor Health**:
   ```bash
   # Check all service health
   docker-compose exec temperature-api wget -qO- http://localhost:8081/health
   ```

### Troubleshooting

**Common Issues**:

1. **Port Conflicts**:
   - Check if ports 8080, 8081, 5432 are available
   - Modify port mappings in docker-compose.yml if needed

2. **Database Connection Issues**:
   - Verify PostgreSQL health check passes
   - Check database credentials and connection string
   - Review postgres logs: `docker-compose logs postgres`

3. **Temperature API Build Issues**:
   - Ensure Go modules are properly configured
   - Check Dockerfile syntax and build context
   - Review build logs: `docker-compose logs temperature-api`

4. **Network Connectivity**:
   - Verify all services are on the same network
   - Check service names match docker-compose configuration
   - Test internal connectivity: `docker-compose exec app ping temperature-api`

## Performance Considerations

### Resource Requirements
- **Temperature API**: ~50MB RAM, minimal CPU
- **PostgreSQL**: ~100MB RAM, moderate I/O
- **Smart Home App**: ~100MB RAM, moderate CPU
- **Total**: ~250MB RAM minimum

### Scalability Features
- **Stateless design** for horizontal scaling
- **Database connection pooling** for efficiency
- **Health checks** for load balancer integration
- **Container orchestration** ready for Kubernetes

### Monitoring Integration
- **Health endpoints** for uptime monitoring
- **Structured logging** for log aggregation
- **Metrics endpoints** (future enhancement)
- **Distributed tracing** (future enhancement)

## Security Implementation

### Container Security
- **Non-root user** execution
- **Minimal base images** (Alpine Linux)
- **No unnecessary packages** or tools
- **Read-only file systems** where possible

### Network Security
- **Internal network** isolation
- **Port exposure** only where necessary
- **Service-to-service** communication within Docker network
- **Environment variable** configuration (no hardcoded secrets)

### Database Security
- **Connection encryption** (TLS ready)
- **User privilege separation** (development setup)
- **Password hashing** with bcrypt
- **SQL injection** prevention with parameterized queries

## Future Enhancements

### Short-term Improvements
1. **Authentication/Authorization** for API endpoints
2. **Rate limiting** to prevent abuse
3. **Metrics collection** with Prometheus
4. **Centralized logging** with ELK stack

### Long-term Roadmap
1. **Kubernetes deployment** manifests
2. **CI/CD pipeline** integration
3. **Multi-environment** configuration
4. **Service mesh** integration (Istio)
5. **Event-driven architecture** with message queues

## Conclusion

Task 5 successfully demonstrates the practical implementation of microservices architecture concepts developed in previous tasks. The temperature-api service provides a working example of:

- **Microservice implementation** with modern Go practices
- **Docker containerization** with security best practices
- **Service orchestration** with Docker Compose
- **Database integration** with PostgreSQL
- **API design** following REST principles
- **Testing strategy** for integration verification

This implementation serves as a foundation for the complete Smart Home IoT Ecosystem, showing how architectural designs translate into working software systems.

## Files Created

### Temperature API Service
- [`apps/temperature-api/main.go`](../apps/temperature-api/main.go) - Main service implementation
- [`apps/temperature-api/go.mod`](../apps/temperature-api/go.mod) - Go module definition
- [`apps/temperature-api/go.sum`](../apps/temperature-api/go.sum) - Dependency checksums
- [`apps/temperature-api/Dockerfile`](../apps/temperature-api/Dockerfile) - Container definition
- [`apps/temperature-api/README.md`](../apps/temperature-api/README.md) - Service documentation

### Database Configuration
- [`apps/postgres-init/init.sql`](../apps/postgres-init/init.sql) - Database initialization script

### Orchestration
- [`apps/docker-compose.yml`](../apps/docker-compose.yml) - Updated service orchestration

### Documentation
- [`docs/task5-docker-implementation.md`](task5-docker-implementation.md) - This comprehensive documentation