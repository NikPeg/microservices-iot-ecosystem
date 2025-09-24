# Task 6: MVP Architecture Design

## Overview

Task 6 focuses on creating a Minimum Viable Product (MVP) by developing new microservices that integrate with the existing monolithic application. This represents the first step in the gradual migration from monolith to microservices architecture using the Strangler Fig pattern.

## MVP Architecture Strategy

### 1. Selected Microservices for MVP

Based on the domain analysis from Task 2, we will implement two core microservices:

#### Device Management Service (Java/Spring Boot)
- **Port**: 8082
- **Language**: Java 17 with Spring Boot 3.x
- **Database**: PostgreSQL (separate schema: device_service)
- **Responsibilities**:
  - Device registration and lifecycle management
  - Device command execution
  - Device status monitoring
  - Integration with existing monolith

#### Telemetry Service (Python/FastAPI)
- **Port**: 8083
- **Language**: Python 3.11 with FastAPI
- **Database**: InfluxDB for time-series data + Redis for caching
- **Responsibilities**:
  - Sensor data collection and storage
  - Real-time telemetry processing
  - Data aggregation and analytics
  - Integration with message broker

### 2. Integration Strategy

#### Message Broker Integration
- **Technology**: Redis Pub/Sub (lightweight for MVP)
- **Alternative**: RabbitMQ (for production scalability)
- **Purpose**: Asynchronous communication between services

#### Communication Patterns
1. **Synchronous**: REST API calls for immediate responses
2. **Asynchronous**: Message broker for event-driven communication
3. **Hybrid**: Gradual migration from monolith to microservices

### 3. MVP Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        MVP Architecture                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────────┐    │
│  │   Client    │    │   API        │    │   Smart Home    │    │
│  │ Application │◄──►│   Gateway    │◄──►│   Monolith      │    │
│  │             │    │  (Port 8080) │    │   (Go)          │    │
│  └─────────────┘    └──────────────┘    └─────────────────┘    │
│                             │                      │            │
│                             │                      │            │
│  ┌─────────────────────────────────────────────────┼────────────┤
│  │                Message Broker                   │            │
│  │              (Redis Pub/Sub)                    │            │
│  │                                                 │            │
│  │  ┌──────────────┐              ┌───────────────┐│            │
│  │  │   Device     │◄────────────►│   Telemetry   ││            │
│  │  │ Management   │              │   Service     ││            │
│  │  │   Service    │              │  (Python/     ││            │
│  │  │(Java/Spring) │              │   FastAPI)    ││            │
│  │  │ Port 8082    │              │  Port 8083    ││            │
│  │  └──────────────┘              └───────────────┘│            │
│  │         │                              │        │            │
│  │         ▼                              ▼        │            │
│  │  ┌──────────────┐              ┌───────────────┐│            │
│  │  │ PostgreSQL   │              │   InfluxDB    ││            │
│  │  │ (device_db)  │              │ (telemetry)   ││            │
│  │  └──────────────┘              └───────────────┘│            │
│  └─────────────────────────────────────────────────┘            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Implementation Plan

### Phase 1: Infrastructure Setup
1. **Message Broker**: Deploy Redis for pub/sub messaging
2. **Databases**: Set up separate databases for each microservice
3. **Network**: Configure Docker network for service communication

### Phase 2: Device Management Service (Java/Spring Boot)
1. **Core Features**:
   - Device CRUD operations
   - Device command handling
   - Status monitoring
   - REST API endpoints

2. **Integration Points**:
   - Receive device commands from monolith
   - Publish device events to message broker
   - Sync device data with monolith database

### Phase 3: Telemetry Service (Python/FastAPI)
1. **Core Features**:
   - Sensor data ingestion
   - Time-series data storage
   - Real-time data processing
   - Data aggregation APIs

2. **Integration Points**:
   - Consume sensor data from message broker
   - Provide telemetry APIs to monolith
   - Store data in InfluxDB for analytics

### Phase 4: Integration & Testing
1. **Service Integration**: Connect all services via message broker
2. **Data Synchronization**: Ensure data consistency between services
3. **End-to-End Testing**: Validate complete workflows
4. **Performance Testing**: Measure system performance

## Technology Stack

### Device Management Service
- **Language**: Java 17
- **Framework**: Spring Boot 3.2
- **Database**: PostgreSQL 16
- **Build Tool**: Maven
- **Container**: OpenJDK 17 Alpine

### Telemetry Service  
- **Language**: Python 3.11
- **Framework**: FastAPI 0.104
- **Database**: InfluxDB 2.7 + Redis 7
- **Package Manager**: Poetry/pip
- **Container**: Python 3.11 Alpine

### Message Broker
- **Primary**: Redis 7 (Pub/Sub)
- **Alternative**: RabbitMQ 3.12
- **Purpose**: Asynchronous communication

### Existing Services
- **Monolith**: Go with Gin framework
- **Temperature API**: Go service (from Task 5)
- **Database**: PostgreSQL with comprehensive schema

## Data Flow Patterns

### 1. Device Command Flow
```
Client → API Gateway → Monolith → Message Broker → Device Service → Device
```

### 2. Telemetry Data Flow
```
Sensor → Temperature API → Message Broker → Telemetry Service → InfluxDB
```

### 3. Status Update Flow
```
Device Service → Message Broker → Monolith → Client
```

## Integration Patterns

### 1. Strangler Fig Pattern
- Gradually migrate functionality from monolith to microservices
- Maintain backward compatibility during transition
- Route traffic based on feature flags

### 2. Database per Service
- Each microservice has its own database
- Data synchronization via events
- Eventual consistency model

### 3. Event-Driven Architecture
- Services communicate via events
- Loose coupling between components
- Scalable and resilient design

## MVP Success Criteria

### Functional Requirements
1. ✅ Device registration and management
2. ✅ Telemetry data collection and storage
3. ✅ Real-time device status updates
4. ✅ Integration with existing monolith
5. ✅ Message broker communication

### Non-Functional Requirements
1. ✅ Response time < 500ms for API calls
2. ✅ 99% uptime for critical services
3. ✅ Horizontal scalability support
4. ✅ Docker containerization
5. ✅ Comprehensive monitoring

### Technical Requirements
1. ✅ RESTful APIs for all services
2. ✅ OpenAPI documentation
3. ✅ Health check endpoints
4. ✅ Structured logging
5. ✅ Error handling and recovery

## Migration Strategy

### Step 1: Parallel Implementation
- Implement new microservices alongside monolith
- Maintain data synchronization
- Test functionality in parallel

### Step 2: Traffic Routing
- Gradually route traffic to microservices
- Use feature flags for controlled rollout
- Monitor performance and reliability

### Step 3: Monolith Decomposition
- Remove functionality from monolith
- Update integration points
- Maintain backward compatibility

### Step 4: Full Migration
- Complete migration to microservices
- Decommission monolith components
- Optimize microservice architecture

## Risk Mitigation

### Technical Risks
1. **Data Consistency**: Implement eventual consistency patterns
2. **Network Latency**: Use caching and async processing
3. **Service Dependencies**: Implement circuit breakers
4. **Database Migration**: Use gradual migration approach

### Operational Risks
1. **Monitoring**: Implement comprehensive observability
2. **Deployment**: Use blue-green deployment strategy
3. **Rollback**: Maintain rollback capabilities
4. **Performance**: Continuous performance monitoring

## Next Steps

1. **Create Device Management Service** (Java/Spring Boot)
2. **Create Telemetry Service** (Python/FastAPI)
3. **Set up Redis message broker**
4. **Implement service integration**
5. **Create Docker containers and compose file**
6. **Test end-to-end functionality**
7. **Document implementation and results**

This MVP architecture provides a solid foundation for the gradual migration from monolith to microservices while maintaining system stability and functionality.