#!/bin/bash

# Quick Health Check Script for Smart Home Microservices
# This script performs basic health checks on all microservices

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Base URLs
DEVICE_SERVICE_URL="http://localhost:8081"
TELEMETRY_SERVICE_URL="http://localhost:8082"
TEMPERATURE_API_URL="http://localhost:8083"
SMART_HOME_URL="http://localhost:8080"

echo -e "${GREEN}Smart Home Microservices - Quick Health Check${NC}"
echo -e "${GREEN}=============================================${NC}"

# Function to check service health
check_service() {
    local service_name="$1"
    local url="$2"

    echo -n -e "${YELLOW}Checking $service_name...${NC} "

    if curl -s -f "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ HEALTHY${NC}"
        return 0
    else
        echo -e "${RED}✗ UNHEALTHY${NC}"
        return 1
    fi
}

# Check all services
FAILED_SERVICES=0

check_service "Device Service" "$DEVICE_SERVICE_URL/device-service/actuator/health" || FAILED_SERVICES=$((FAILED_SERVICES + 1))
check_service "Telemetry Service" "$TELEMETRY_SERVICE_URL/health" || FAILED_SERVICES=$((FAILED_SERVICES + 1))
check_service "Temperature API" "$TEMPERATURE_API_URL/health" || FAILED_SERVICES=$((FAILED_SERVICES + 1))
check_service "Smart Home Service" "$SMART_HOME_URL/health" || FAILED_SERVICES=$((FAILED_SERVICES + 1))

echo -e "\n${BLUE}Quick API Tests:${NC}"

# Quick functional tests
echo -n -e "${YELLOW}Temperature API...${NC} "
if curl -s "$TEMPERATURE_API_URL/temperature?location=living_room" | grep -q "value" 2>/dev/null; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
    FAILED_SERVICES=$((FAILED_SERVICES + 1))
fi

echo -n -e "${YELLOW}Smart Home Sensors...${NC} "
if curl -s "$SMART_HOME_URL/api/v1/sensors" | grep -q "\[" 2>/dev/null; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
    FAILED_SERVICES=$((FAILED_SERVICES + 1))
fi

echo -n -e "${YELLOW}Device Service...${NC} "
if curl -s "$DEVICE_SERVICE_URL/device-service/api/v1/devices" | grep -q -E "(content|timestamp)" 2>/dev/null; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
    FAILED_SERVICES=$((FAILED_SERVICES + 1))
fi

# Summary
echo -e "\n${BLUE}Summary:${NC}"
if [ $FAILED_SERVICES -eq 0 ]; then
    echo -e "${GREEN}🎉 All services are healthy and responding!${NC}"
    echo -e "${BLUE}Run './test-microservices.sh' for comprehensive testing.${NC}"
    exit 0
else
    echo -e "${RED}❌ $FAILED_SERVICES service(s) failed health check.${NC}"
    echo -e "${YELLOW}Make sure all services are running with: docker-compose up${NC}"
    exit 1
fi
