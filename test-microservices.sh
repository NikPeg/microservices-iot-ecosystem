#!/bin/bash

# Smart Home Microservices Test Script
# This script tests all microservices endpoints with curl commands
# Make sure all services are running via docker-compose up

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

# Test counter
TOTAL_TESTS=0
PASSED_TESTS=0

# Function to print test header
print_test_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

# Function to run curl test
run_test() {
    local test_name="$1"
    local curl_command="$2"
    local expected_status="$3"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -e "\n${YELLOW}Test: $test_name${NC}"
    echo "Command: $curl_command"

    # Execute curl command and capture response
    response=$(eval "$curl_command" 2>/dev/null)
    status_code=$(eval "$curl_command -w '%{http_code}' -o /dev/null -s" 2>/dev/null)

    if [ "$status_code" = "$expected_status" ]; then
        echo -e "${GREEN}✓ PASSED${NC} (Status: $status_code)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        if [ ! -z "$response" ]; then
            echo "Response: $response" | head -c 200
            if [ ${#response} -gt 200 ]; then
                echo "..."
            fi
        fi
    else
        echo -e "${RED}✗ FAILED${NC} (Expected: $expected_status, Got: $status_code)"
        if [ ! -z "$response" ]; then
            echo "Response: $response" | head -c 200
        fi
    fi
}

# Function to create test data
create_test_data() {
    echo -e "\n${YELLOW}Creating test data...${NC}"

    # Create a test device for device service
    TEST_DEVICE_JSON='{
        "name": "Test Smart Thermostat",
        "deviceType": "THERMOSTAT",
        "homeId": "123e4567-e89b-12d3-a456-426614174000",
        "roomId": "123e4567-e89b-12d3-a456-426614174001",
        "status": "ONLINE",
        "batteryLevel": 85,
        "firmwareVersion": "1.2.3",
        "manufacturer": "TestCorp",
        "model": "TC-THERM-001"
    }'

    # Try to create device and capture device ID
    device_response=$(curl -s -X POST "$DEVICE_SERVICE_URL/device-service/api/v1/devices" \
        -H "Content-Type: application/json" \
        -d "$TEST_DEVICE_JSON" 2>/dev/null || echo "")

    if [ ! -z "$device_response" ]; then
        DEVICE_ID=$(echo "$device_response" | grep -o '"id":"[^"]*"' | cut -d'"' -f4 2>/dev/null || echo "")
        echo "Created test device with ID: $DEVICE_ID"
    fi

    # Create a test sensor for smart home service
    TEST_SENSOR_JSON='{
        "name": "Test Living Room Temperature",
        "type": "temperature",
        "location": "Living Room",
        "unit": "°C"
    }'

    sensor_response=$(curl -s -X POST "$SMART_HOME_URL/api/v1/sensors" \
        -H "Content-Type: application/json" \
        -d "$TEST_SENSOR_JSON" 2>/dev/null || echo "")

    if [ ! -z "$sensor_response" ]; then
        SENSOR_ID=$(echo "$sensor_response" | grep -o '"id":[0-9]*' | cut -d':' -f2 2>/dev/null || echo "1")
        echo "Created test sensor with ID: $SENSOR_ID"
    else
        SENSOR_ID="1"
    fi
}

echo -e "${GREEN}Smart Home Microservices Test Suite${NC}"
echo -e "${GREEN}====================================${NC}"

# ========================================
# HEALTH CHECKS
# ========================================
print_test_header "HEALTH CHECKS"

run_test "Device Service Health" \
    "curl -s '$DEVICE_SERVICE_URL/device-service/actuator/health'" \
    "200"

run_test "Telemetry Service Health" \
    "curl -s '$TELEMETRY_SERVICE_URL/health'" \
    "200"

run_test "Temperature API Health" \
    "curl -s '$TEMPERATURE_API_URL/health'" \
    "200"

run_test "Smart Home Service Health" \
    "curl -s '$SMART_HOME_URL/health'" \
    "200"

# ========================================
# TEMPERATURE API TESTS
# ========================================
print_test_header "TEMPERATURE API TESTS"

run_test "Get Temperature by Location" \
    "curl -s '$TEMPERATURE_API_URL/temperature?location=living_room'" \
    "200"

run_test "Get Temperature by Sensor ID" \
    "curl -s '$TEMPERATURE_API_URL/temperature/sensor-living_room-001'" \
    "200"

run_test "Temperature API - Missing Location Parameter" \
    "curl -s '$TEMPERATURE_API_URL/temperature'" \
    "400"

# ========================================
# SMART HOME SERVICE TESTS
# ========================================
print_test_header "SMART HOME SERVICE TESTS"

# Create test data first
create_test_data

run_test "Get All Sensors" \
    "curl -s '$SMART_HOME_URL/api/v1/sensors'" \
    "200"

run_test "Create New Sensor" \
    "curl -s -X POST '$SMART_HOME_URL/api/v1/sensors' -H 'Content-Type: application/json' -d '{\"name\":\"Test Humidity Sensor\",\"type\":\"humidity\",\"location\":\"Bedroom\",\"unit\":\"%\"}'" \
    "201"

run_test "Get Sensor by ID" \
    "curl -s '$SMART_HOME_URL/api/v1/sensors/$SENSOR_ID'" \
    "200"

run_test "Update Sensor Value" \
    "curl -s -X PATCH '$SMART_HOME_URL/api/v1/sensors/$SENSOR_ID/value' -H 'Content-Type: application/json' -d '{\"value\":23.5,\"status\":\"active\"}'" \
    "200"

run_test "Get Temperature by Location" \
    "curl -s '$SMART_HOME_URL/api/v1/sensors/temperature/living_room'" \
    "200"

run_test "Update Sensor" \
    "curl -s -X PUT '$SMART_HOME_URL/api/v1/sensors/$SENSOR_ID' -H 'Content-Type: application/json' -d '{\"name\":\"Updated Test Sensor\",\"type\":\"temperature\",\"location\":\"Living Room\",\"unit\":\"°C\"}'" \
    "200"

# ========================================
# DEVICE SERVICE TESTS
# ========================================
print_test_header "DEVICE SERVICE TESTS"

run_test "Get All Devices" \
    "curl -s '$DEVICE_SERVICE_URL/device-service/api/v1/devices'" \
    "200"

run_test "Create New Device" \
    "curl -s -X POST '$DEVICE_SERVICE_URL/device-service/api/v1/devices' -H 'Content-Type: application/json' -d '{\"name\":\"Test Light Switch\",\"deviceType\":\"SWITCH\",\"homeId\":\"123e4567-e89b-12d3-a456-426614174000\",\"roomId\":\"123e4567-e89b-12d3-a456-426614174001\",\"status\":\"ONLINE\",\"batteryLevel\":90,\"firmwareVersion\":\"2.1.0\",\"manufacturer\":\"TestCorp\",\"model\":\"TC-SWITCH-001\"}'" \
    "201"

if [ ! -z "$DEVICE_ID" ]; then
    run_test "Get Device by ID" \
        "curl -s '$DEVICE_SERVICE_URL/device-service/api/v1/devices/$DEVICE_ID'" \
        "200"

    run_test "Update Device Status" \
        "curl -s -X PATCH '$DEVICE_SERVICE_URL/device-service/api/v1/devices/$DEVICE_ID/status?status=OFFLINE'" \
        "200"

    run_test "Send Command to Device" \
        "curl -s -X POST '$DEVICE_SERVICE_URL/device-service/api/v1/devices/$DEVICE_ID/commands' -H 'Content-Type: application/json' -d '{\"commandType\":\"TURN_ON\",\"parameters\":\"{\\\"brightness\\\":80}\",\"issuedBy\":\"123e4567-e89b-12d3-a456-426614174002\"}'" \
        "202"

    run_test "Get Device Commands" \
        "curl -s '$DEVICE_SERVICE_URL/device-service/api/v1/devices/$DEVICE_ID/commands'" \
        "200"
fi

run_test "Get Devices by Home ID" \
    "curl -s '$DEVICE_SERVICE_URL/device-service/api/v1/devices/home/123e4567-e89b-12d3-a456-426614174000'" \
    "200"

run_test "Search Devices" \
    "curl -s '$DEVICE_SERVICE_URL/device-service/api/v1/devices/search?q=Test'" \
    "200"

run_test "Get Low Battery Devices" \
    "curl -s '$DEVICE_SERVICE_URL/device-service/api/v1/devices/low-battery?threshold=20'" \
    "200"

run_test "Get Offline Devices" \
    "curl -s '$DEVICE_SERVICE_URL/device-service/api/v1/devices/offline?hours=24'" \
    "200"

run_test "Get Devices with Filters" \
    "curl -s '$DEVICE_SERVICE_URL/device-service/api/v1/devices?deviceType=THERMOSTAT&status=ONLINE'" \
    "200"

# ========================================
# TELEMETRY SERVICE TESTS
# ========================================
print_test_header "TELEMETRY SERVICE TESTS"

# Test telemetry endpoints
TELEMETRY_DATA='{
    "device_id": "123e4567-e89b-12d3-a456-426614174000",
    "measurement": "temperature",
    "value": 22.5,
    "unit": "°C",
    "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
    "location": "living_room",
    "metadata": {
        "sensor_type": "DHT22",
        "accuracy": "±0.5°C"
    }
}'

run_test "Store Telemetry Data" \
    "curl -s -X POST '$TELEMETRY_SERVICE_URL/api/v1/telemetry' -H 'Content-Type: application/json' -d '$TELEMETRY_DATA'" \
    "200"

TELEMETRY_BATCH='[
    {
        "device_id": "123e4567-e89b-12d3-a456-426614174000",
        "measurement": "temperature",
        "value": 23.0,
        "unit": "°C",
        "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
        "location": "bedroom"
    },
    {
        "device_id": "123e4567-e89b-12d3-a456-426614174001",
        "measurement": "humidity",
        "value": 65.0,
        "unit": "%",
        "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
        "location": "bedroom"
    }
]'

run_test "Store Telemetry Batch" \
    "curl -s -X POST '$TELEMETRY_SERVICE_URL/api/v1/telemetry/batch' -H 'Content-Type: application/json' -d '$TELEMETRY_BATCH'" \
    "200"

# Wait a moment for data to be processed
sleep 2

# macOS compatible date commands
if [[ "$OSTYPE" == "darwin"* ]]; then
    START_TIME=$(date -u -v-1H +%Y-%m-%dT%H:%M:%SZ)
else
    START_TIME=$(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ)
fi
END_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)

run_test "Get Device Telemetry" \
    "curl -s '$TELEMETRY_SERVICE_URL/api/v1/telemetry/123e4567-e89b-12d3-a456-426614174000?start_time=$START_TIME&end_time=$END_TIME&limit=10'" \
    "200"

run_test "Get Latest Telemetry" \
    "curl -s '$TELEMETRY_SERVICE_URL/api/v1/telemetry/123e4567-e89b-12d3-a456-426614174000/latest'" \
    "200"

run_test "Get Latest Telemetry with Measurement Filter" \
    "curl -s '$TELEMETRY_SERVICE_URL/api/v1/telemetry/123e4567-e89b-12d3-a456-426614174000/latest?measurement=temperature'" \
    "200"

run_test "Get Aggregated Telemetry" \
    "curl -s '$TELEMETRY_SERVICE_URL/api/v1/telemetry/123e4567-e89b-12d3-a456-426614174000/aggregated?start_time=$START_TIME&end_time=$END_TIME&measurement=temperature&aggregation=mean&window=1h'" \
    "200"

run_test "Get Device Alerts" \
    "curl -s '$TELEMETRY_SERVICE_URL/api/v1/devices/123e4567-e89b-12d3-a456-426614174000/alerts'" \
    "200"

# ========================================
# INTEGRATION TESTS
# ========================================
print_test_header "INTEGRATION TESTS"

run_test "Temperature API Integration via Smart Home" \
    "curl -s '$SMART_HOME_URL/api/v1/sensors/temperature/kitchen'" \
    "200"

run_test "Cross-service Temperature Data" \
    "curl -s '$TEMPERATURE_API_URL/temperature?location=bedroom'" \
    "200"

# Test invalid endpoints
run_test "Invalid Device Service Endpoint" \
    "curl -s '$DEVICE_SERVICE_URL/api/v1/invalid'" \
    "404"

run_test "Invalid Telemetry Service Endpoint" \
    "curl -s '$TELEMETRY_SERVICE_URL/api/v1/invalid'" \
    "404"

# ========================================
# CLEANUP (Optional)
# ========================================
print_test_header "CLEANUP"

if [ ! -z "$DEVICE_ID" ]; then
    run_test "Delete Test Device" \
        "curl -s -X DELETE '$DEVICE_SERVICE_URL/device-service/api/v1/devices/$DEVICE_ID'" \
        "204"
fi

if [ ! -z "$SENSOR_ID" ] && [ "$SENSOR_ID" != "1" ]; then
    run_test "Delete Test Sensor" \
        "curl -s -X DELETE '$SMART_HOME_URL/api/v1/sensors/$SENSOR_ID'" \
        "500"
fi

# ========================================
# TEST SUMMARY
# ========================================
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}TEST SUMMARY${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Total Tests: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
echo -e "${RED}Failed: $((TOTAL_TESTS - PASSED_TESTS))${NC}"

if [ $PASSED_TESTS -eq $TOTAL_TESTS ]; then
    echo -e "\n${GREEN}🎉 All tests passed! All microservices are working correctly.${NC}"
    exit 0
else
    echo -e "\n${RED}❌ Some tests failed. Please check the microservices.${NC}"
    exit 1
fi
