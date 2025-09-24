"""
Configuration and fixtures for integration tests.
"""
import os
import time
import pytest
import requests
from typing import Dict, Any
from datetime import datetime, timezone


class ServiceConfig:
    """Configuration for microservices endpoints."""

    def __init__(self):
        self.device_service_url = os.getenv("DEVICE_SERVICE_URL", "http://localhost:8081")
        self.telemetry_service_url = os.getenv("TELEMETRY_SERVICE_URL", "http://localhost:8082")
        self.temperature_api_url = os.getenv("TEMPERATURE_API_URL", "http://localhost:8083")
        self.smart_home_url = os.getenv("SMART_HOME_URL", "http://localhost:8080")

        # Test data
        self.test_device_data = {
            "name": "Test Smart Thermostat",
            "deviceType": "THERMOSTAT",
            "homeId": "123e4567-e89b-12d3-a456-426614174000",
            "roomId": "123e4567-e89b-12d3-a456-426614174001",
            "userId": "123e4567-e89b-12d3-a456-426614174002",
            "status": "ONLINE",
            "batteryLevel": 85,
            "firmwareVersion": "1.2.3",
            "manufacturer": "TestCorp",
            "model": "TC-THERM-001"
        }

        self.test_sensor_data = {
            "name": "Test Living Room Temperature",
            "type": "temperature",
            "location": "Living Room",
            "unit": "°C"
        }


@pytest.fixture(scope="session")
def config():
    """Service configuration fixture."""
    return ServiceConfig()


@pytest.fixture(scope="session")
def wait_for_services(config):
    """Wait for all services to be ready."""
    services = [
        (config.device_service_url, "/device-service/actuator/health"),
        (config.telemetry_service_url, "/health"),
        (config.temperature_api_url, "/health"),
        (config.smart_home_url, "/health")
    ]

    max_retries = 30
    retry_delay = 2

    for base_url, health_endpoint in services:
        for attempt in range(max_retries):
            try:
                response = requests.get(f"{base_url}{health_endpoint}", timeout=5)
                if response.status_code == 200:
                    print(f"✓ Service {base_url} is ready")
                    break
            except requests.exceptions.RequestException:
                pass

            if attempt == max_retries - 1:
                pytest.fail(f"Service {base_url} is not ready after {max_retries} attempts")

            time.sleep(retry_delay)


@pytest.fixture
def test_device_id(config, wait_for_services):
    """Create a test device and return its ID."""
    response = requests.post(
        f"{config.device_service_url}/device-service/api/v1/devices",
        json=config.test_device_data,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 201:
        device_data = response.json()
        device_id = device_data.get("id")
        yield device_id

        # Cleanup
        try:
            requests.delete(f"{config.device_service_url}/device-service/api/v1/devices/{device_id}")
        except:
            pass
    else:
        pytest.skip(f"Could not create test device: {response.status_code} - {response.text}")


@pytest.fixture
def test_sensor_id(config, wait_for_services):
    """Create a test sensor and return its ID."""
    response = requests.post(
        f"{config.smart_home_url}/api/v1/sensors",
        json=config.test_sensor_data,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 201:
        sensor_data = response.json()
        sensor_id = sensor_data.get("id", 1)
        yield sensor_id

        # Cleanup (if delete endpoint exists)
        try:
            requests.delete(f"{config.smart_home_url}/api/v1/sensors/{sensor_id}")
        except:
            pass
    else:
        # If creation fails, use default ID
        yield 1


@pytest.fixture
def telemetry_data():
    """Generate test telemetry data."""
    return {
        "device_id": "123e4567-e89b-12d3-a456-426614174000",
        "measurement": "temperature",
        "value": 22.5,
        "unit": "°C",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "location": "living_room",
        "metadata": {
            "sensor_type": "DHT22",
            "accuracy": "±0.5°C"
        }
    }


@pytest.fixture
def telemetry_batch_data():
    """Generate batch telemetry data."""
    timestamp = datetime.now(timezone.utc).isoformat()
    return [
        {
            "device_id": "123e4567-e89b-12d3-a456-426614174000",
            "measurement": "temperature",
            "value": 23.0,
            "unit": "°C",
            "timestamp": timestamp,
            "location": "bedroom"
        },
        {
            "device_id": "123e4567-e89b-12d3-a456-426614174001",
            "measurement": "humidity",
            "value": 65.0,
            "unit": "%",
            "timestamp": timestamp,
            "location": "bedroom"
        }
    ]
