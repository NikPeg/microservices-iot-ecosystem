"""
Integration tests for Smart Home Service.
"""
import pytest
import requests


class TestSmartHomeService:
    """Test Smart Home Service API endpoints."""

    def test_get_all_sensors(self, config, wait_for_services):
        """Test getting all sensors."""
        response = requests.get(f"{config.smart_home_url}/api/v1/sensors")

        assert response.status_code == 200
        sensors = response.json()
        assert isinstance(sensors, list)

    def test_create_new_sensor(self, config, wait_for_services):
        """Test creating a new sensor."""
        sensor_data = {
            "name": "Test Humidity Sensor",
            "type": "humidity",
            "location": "Bedroom",
            "unit": "%"
        }

        response = requests.post(
            f"{config.smart_home_url}/api/v1/sensors",
            json=sensor_data,
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 201
        created_sensor = response.json()
        assert created_sensor["name"] == sensor_data["name"]
        assert created_sensor["type"] == sensor_data["type"]
        assert "id" in created_sensor

    def test_get_sensor_by_id(self, config, test_sensor_id):
        """Test getting a sensor by ID."""
        response = requests.get(f"{config.smart_home_url}/api/v1/sensors/{test_sensor_id}")

        assert response.status_code == 200
        sensor = response.json()
        assert sensor["id"] == test_sensor_id

    def test_update_sensor_value(self, config, test_sensor_id):
        """Test updating sensor value."""
        value_data = {
            "value": 23.5,
            "status": "active"
        }

        response = requests.patch(
            f"{config.smart_home_url}/api/v1/sensors/{test_sensor_id}/value",
            json=value_data,
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 200
        result = response.json()
        assert "message" in result or "status" in result or "value" in result

    def test_get_temperature_by_location(self, config, wait_for_services):
        """Test getting temperature by location."""
        response = requests.get(f"{config.smart_home_url}/api/v1/sensors/temperature/living_room")

        assert response.status_code == 200
        temperature_data = response.json()
        assert isinstance(temperature_data, (dict, list))

    def test_update_sensor(self, config, test_sensor_id):
        """Test updating sensor information."""
        update_data = {
            "name": "Updated Test Sensor",
            "type": "temperature",
            "location": "Living Room",
            "unit": "°C"
        }

        response = requests.put(
            f"{config.smart_home_url}/api/v1/sensors/{test_sensor_id}",
            json=update_data,
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 200
        updated_sensor = response.json()
        assert updated_sensor["name"] == update_data["name"]

    def test_get_nonexistent_sensor(self, config, wait_for_services):
        """Test getting a non-existent sensor."""
        response = requests.get(f"{config.smart_home_url}/api/v1/sensors/99999")

        # Should return 404 for non-existent sensor
        assert response.status_code == 404

    def test_create_sensor_with_invalid_data(self, config, wait_for_services):
        """Test creating sensor with invalid data."""
        invalid_data = {
            "invalid_field": "invalid_value"
        }

        response = requests.post(
            f"{config.smart_home_url}/api/v1/sensors",
            json=invalid_data,
            headers={"Content-Type": "application/json"}
        )

        # Should return 400 or 422 for invalid data
        assert response.status_code in [400, 422]

    def test_update_nonexistent_sensor(self, config, wait_for_services):
        """Test updating a non-existent sensor."""
        update_data = {
            "name": "Non-existent Sensor",
            "type": "temperature",
            "location": "Nowhere",
            "unit": "°C"
        }

        response = requests.put(
            f"{config.smart_home_url}/api/v1/sensors/99999",
            json=update_data,
            headers={"Content-Type": "application/json"}
        )

        # Should return 404 for non-existent sensor
        assert response.status_code == 404
