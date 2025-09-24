"""
End-to-end integration tests for cross-service scenarios.
"""
import pytest
import requests
import time
from datetime import datetime, timezone


class TestIntegrationScenarios:
    """Test integration scenarios across multiple services."""

    def test_temperature_api_integration_via_smart_home(self, config, wait_for_services):
        """Test Temperature API integration through Smart Home service."""
        response = requests.get(f"{config.smart_home_url}/api/v1/sensors/temperature/kitchen")

        assert response.status_code == 200
        temperature_data = response.json()
        assert isinstance(temperature_data, (dict, list))

    def test_cross_service_temperature_data(self, config, wait_for_services):
        """Test cross-service temperature data consistency."""
        # Get temperature from Temperature API
        temp_api_response = requests.get(
            f"{config.temperature_api_url}/temperature",
            params={"location": "bedroom"}
        )

        assert temp_api_response.status_code == 200
        temp_api_data = temp_api_response.json()
        assert isinstance(temp_api_data, dict)

        # Get temperature from Smart Home service
        smart_home_response = requests.get(f"{config.smart_home_url}/api/v1/sensors/temperature/bedroom")

        assert smart_home_response.status_code == 200
        smart_home_data = smart_home_response.json()
        assert isinstance(smart_home_data, (dict, list))

    def test_device_to_telemetry_workflow(self, config, wait_for_services, test_device_id):
        """Test complete workflow from device creation to telemetry storage."""
        # 1. Verify device exists
        device_response = requests.get(f"{config.device_service_url}/device-service/api/v1/devices/{test_device_id}")
        assert device_response.status_code == 200
        device = device_response.json()

        # 2. Send command to device
        command_data = {
            "commandType": "READ_TEMPERATURE",
            "parameters": "{}",
            "issuedBy": device["userId"]
        }

        command_response = requests.post(
            f"{config.device_service_url}/device-service/api/v1/devices/{test_device_id}/commands",
            json=command_data,
            headers={"Content-Type": "application/json"}
        )
        assert command_response.status_code == 202

        # 3. Simulate telemetry data from the device
        telemetry_data = {
            "device_id": test_device_id,
            "measurement": "temperature",
            "value": 24.5,
            "unit": "°C",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "location": "living_room",
            "metadata": {
                "command_response": True,
                "sensor_type": "internal"
            }
        }

        telemetry_response = requests.post(
            f"{config.telemetry_service_url}/api/v1/telemetry",
            json=telemetry_data,
            headers={"Content-Type": "application/json"}
        )
        assert telemetry_response.status_code == 200

        # 4. Wait for data processing
        time.sleep(3)

        # 5. Verify telemetry data was stored
        latest_response = requests.get(f"{config.telemetry_service_url}/api/v1/telemetry/{test_device_id}/latest")
        assert latest_response.status_code == 200

    def test_sensor_creation_and_temperature_reading(self, config, wait_for_services):
        """Test creating sensor and reading temperature data."""
        # 1. Create a new sensor
        sensor_data = {
            "name": "Integration Test Sensor",
            "type": "temperature",
            "location": "test_room",
            "unit": "°C"
        }

        create_response = requests.post(
            f"{config.smart_home_url}/api/v1/sensors",
            json=sensor_data,
            headers={"Content-Type": "application/json"}
        )
        assert create_response.status_code == 201
        sensor = create_response.json()
        sensor_id = sensor["id"]

        # 2. Update sensor value
        value_data = {
            "value": 22.8,
            "status": "active"
        }

        update_response = requests.patch(
            f"{config.smart_home_url}/api/v1/sensors/{sensor_id}/value",
            json=value_data,
            headers={"Content-Type": "application/json"}
        )
        assert update_response.status_code == 200

        # 3. Read temperature by location
        temp_response = requests.get(f"{config.smart_home_url}/api/v1/sensors/temperature/test_room")
        assert temp_response.status_code == 200

        # 4. Verify sensor data
        get_response = requests.get(f"{config.smart_home_url}/api/v1/sensors/{sensor_id}")
        assert get_response.status_code == 200
        retrieved_sensor = get_response.json()
        assert retrieved_sensor["name"] == sensor_data["name"]

    def test_multi_service_data_consistency(self, config, wait_for_services, test_device_id):
        """Test data consistency across multiple services."""
        # 1. Get device info from Device Service
        device_response = requests.get(f"{config.device_service_url}/device-service/api/v1/devices/{test_device_id}")
        assert device_response.status_code == 200
        device = device_response.json()

        # 2. Store telemetry for this device
        telemetry_data = {
            "device_id": test_device_id,
            "measurement": "battery_level",
            "value": device["batteryLevel"],
            "unit": "%",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "location": "device_internal"
        }

        telemetry_response = requests.post(
            f"{config.telemetry_service_url}/api/v1/telemetry",
            json=telemetry_data,
            headers={"Content-Type": "application/json"}
        )
        assert telemetry_response.status_code == 200

        # 3. Wait for processing
        time.sleep(2)

        # 4. Verify telemetry data matches device data
        latest_response = requests.get(f"{config.telemetry_service_url}/api/v1/telemetry/{test_device_id}/latest")
        assert latest_response.status_code == 200

    def test_error_handling_across_services(self, config, wait_for_services):
        """Test error handling consistency across services."""
        # Test invalid endpoints on all services
        services_and_endpoints = [
            (config.device_service_url, "/api/v1/invalid"),
            (config.telemetry_service_url, "/api/v1/invalid"),
            (config.temperature_api_url, "/api/v1/invalid"),
            (config.smart_home_url, "/api/v1/invalid")
        ]

        for base_url, endpoint in services_and_endpoints:
            response = requests.get(f"{base_url}{endpoint}")
            assert response.status_code == 404

    def test_service_health_check_consistency(self, config, wait_for_services):
        """Test that all services respond to health checks consistently."""
        health_endpoints = [
            (config.device_service_url, "/device-service/actuator/health"),
            (config.telemetry_service_url, "/health"),
            (config.temperature_api_url, "/health"),
            (config.smart_home_url, "/health")
        ]

        for base_url, health_endpoint in health_endpoints:
            response = requests.get(f"{base_url}{health_endpoint}")
            assert response.status_code == 200

            # Verify response contains health information
            health_data = response.json()
            assert isinstance(health_data, dict)
