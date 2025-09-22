"""
Integration tests for Device Service.
"""
import pytest
import requests
import time


class TestDeviceService:
    """Test Device Service API endpoints."""

    def test_get_all_devices(self, config, wait_for_services):
        """Test getting all devices."""
        response = requests.get(f"{config.device_service_url}/device-service/api/v1/devices")

        assert response.status_code == 200
        devices_response = response.json()
        # Device service returns paginated response
        if isinstance(devices_response, dict) and 'content' in devices_response:
            devices = devices_response['content']
            assert isinstance(devices, list)
        else:
            # Fallback for direct list response
            assert isinstance(devices_response, list)

    def test_create_device(self, config, wait_for_services):
        """Test creating a new device."""
        device_data = {
            "name": "Test Light Switch",
            "deviceType": "SWITCH",
            "homeId": "123e4567-e89b-12d3-a456-426614174000",
            "roomId": "123e4567-e89b-12d3-a456-426614174001",
            "userId": "123e4567-e89b-12d3-a456-426614174002",
            "status": "ONLINE",
            "batteryLevel": 90,
            "firmwareVersion": "2.1.0",
            "manufacturer": "TestCorp",
            "model": "TC-SWITCH-001"
        }

        response = requests.post(
            f"{config.device_service_url}/device-service/api/v1/devices",
            json=device_data,
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 201
        created_device = response.json()
        assert created_device["name"] == device_data["name"]
        assert created_device["deviceType"] == device_data["deviceType"]
        assert "id" in created_device

        # Cleanup
        device_id = created_device["id"]
        requests.delete(f"{config.device_service_url}/device-service/api/v1/devices/{device_id}")

    def test_get_device_by_id(self, config, test_device_id):
        """Test getting a device by ID."""
        response = requests.get(f"{config.device_service_url}/device-service/api/v1/devices/{test_device_id}")

        assert response.status_code == 200
        device = response.json()
        assert device["id"] == test_device_id
        assert device["name"] == config.test_device_data["name"]

    def test_update_device_status(self, config, test_device_id):
        """Test updating device status."""
        response = requests.patch(
            f"{config.device_service_url}/device-service/api/v1/devices/{test_device_id}/status",
            params={"status": "OFFLINE"}
        )

        assert response.status_code == 200

        # Verify the status was updated
        get_response = requests.get(f"{config.device_service_url}/device-service/api/v1/devices/{test_device_id}")
        assert get_response.status_code == 200
        device = get_response.json()
        assert device["status"] == "OFFLINE"

    def test_send_command_to_device(self, config, test_device_id):
        """Test sending a command to a device."""
        command_data = {
            "commandType": "TURN_ON",
            "parameters": "{\"brightness\":80}",
            "issuedBy": "123e4567-e89b-12d3-a456-426614174002"
        }

        response = requests.post(
            f"{config.device_service_url}/device-service/api/v1/devices/{test_device_id}/commands",
            json=command_data,
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 202

    def test_get_device_commands(self, config, test_device_id):
        """Test getting device commands."""
        response = requests.get(f"{config.device_service_url}/device-service/api/v1/devices/{test_device_id}/commands")

        assert response.status_code == 200
        commands = response.json()
        assert isinstance(commands, list)

    def test_get_devices_by_home_id(self, config, wait_for_services):
        """Test getting devices by home ID."""
        home_id = "123e4567-e89b-12d3-a456-426614174000"
        response = requests.get(f"{config.device_service_url}/device-service/api/v1/devices/home/{home_id}")

        assert response.status_code == 200
        devices_response = response.json()
        # Handle paginated response
        if isinstance(devices_response, dict) and 'content' in devices_response:
            devices = devices_response['content']
            assert isinstance(devices, list)
        else:
            assert isinstance(devices_response, list)

    def test_search_devices(self, config, wait_for_services):
        """Test searching devices."""
        response = requests.get(
            f"{config.device_service_url}/device-service/api/v1/devices/search",
            params={"q": "Test"}
        )

        assert response.status_code == 200
        devices_response = response.json()
        # Handle paginated response
        if isinstance(devices_response, dict) and 'content' in devices_response:
            devices = devices_response['content']
            assert isinstance(devices, list)
        else:
            assert isinstance(devices_response, list)

    def test_get_low_battery_devices(self, config, wait_for_services):
        """Test getting low battery devices."""
        response = requests.get(
            f"{config.device_service_url}/device-service/api/v1/devices/low-battery",
            params={"threshold": 20}
        )

        assert response.status_code == 200
        devices_response = response.json()
        # Handle paginated response
        if isinstance(devices_response, dict) and 'content' in devices_response:
            devices = devices_response['content']
            assert isinstance(devices, list)
        else:
            assert isinstance(devices_response, list)

    def test_get_offline_devices(self, config, wait_for_services):
        """Test getting offline devices."""
        response = requests.get(
            f"{config.device_service_url}/device-service/api/v1/devices/offline",
            params={"hours": 24}
        )

        assert response.status_code == 200
        devices_response = response.json()
        # Handle paginated response
        if isinstance(devices_response, dict) and 'content' in devices_response:
            devices = devices_response['content']
            assert isinstance(devices, list)
        else:
            assert isinstance(devices_response, list)

    def test_get_devices_with_filters(self, config, wait_for_services):
        """Test getting devices with filters."""
        response = requests.get(
            f"{config.device_service_url}/device-service/api/v1/devices",
            params={"deviceType": "THERMOSTAT", "status": "ONLINE"}
        )

        assert response.status_code == 200
        devices_response = response.json()
        # Handle paginated response
        if isinstance(devices_response, dict) and 'content' in devices_response:
            devices = devices_response['content']
            assert isinstance(devices, list)
        else:
            assert isinstance(devices_response, list)

    def test_invalid_endpoint(self, config, wait_for_services):
        """Test invalid endpoint returns 404."""
        response = requests.get(f"{config.device_service_url}/api/v1/invalid")

        assert response.status_code == 404
