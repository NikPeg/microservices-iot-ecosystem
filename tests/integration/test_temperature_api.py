"""
Integration tests for Temperature API.
"""
import pytest
import requests


class TestTemperatureAPI:
    """Test Temperature API endpoints."""

    def test_get_temperature_by_location(self, config, wait_for_services):
        """Test getting temperature by location."""
        response = requests.get(
            f"{config.temperature_api_url}/temperature",
            params={"location": "living_room"}
        )

        assert response.status_code == 200
        temperature_data = response.json()
        assert isinstance(temperature_data, dict)
        assert "temperature" in temperature_data or "value" in temperature_data

    def test_get_temperature_by_sensor_id(self, config, wait_for_services):
        """Test getting temperature by sensor ID."""
        response = requests.get(f"{config.temperature_api_url}/temperature/sensor-living_room-001")

        assert response.status_code == 200
        temperature_data = response.json()
        assert isinstance(temperature_data, dict)

    def test_temperature_missing_location_parameter(self, config, wait_for_services):
        """Test temperature endpoint without location parameter."""
        response = requests.get(f"{config.temperature_api_url}/temperature")

        assert response.status_code == 400

    def test_get_temperature_invalid_location(self, config, wait_for_services):
        """Test getting temperature for invalid location."""
        response = requests.get(
            f"{config.temperature_api_url}/temperature",
            params={"location": "nonexistent_location"}
        )

        # Should return 200 with empty/default data or 404
        assert response.status_code in [200, 404]

    def test_get_temperature_invalid_sensor_id(self, config, wait_for_services):
        """Test getting temperature for invalid sensor ID."""
        response = requests.get(f"{config.temperature_api_url}/temperature/invalid-sensor-id")

        # Should return 404 for invalid sensor
        assert response.status_code == 404

    def test_temperature_api_different_locations(self, config, wait_for_services):
        """Test temperature API with different locations."""
        locations = ["living_room", "bedroom", "kitchen", "bathroom"]

        for location in locations:
            response = requests.get(
                f"{config.temperature_api_url}/temperature",
                params={"location": location}
            )

            # Should return 200 for all locations (even if no data)
            assert response.status_code == 200
            temperature_data = response.json()
            assert isinstance(temperature_data, dict)
