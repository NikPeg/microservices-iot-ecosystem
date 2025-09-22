"""
Health check tests for all microservices.
"""
import pytest
import requests


class TestHealthChecks:
    """Test health endpoints for all services."""

    def test_device_service_health(self, config, wait_for_services):
        """Test Device Service health endpoint."""
        response = requests.get(f"{config.device_service_url}/device-service/actuator/health")

        assert response.status_code == 200
        health_data = response.json()
        assert health_data.get("status") == "UP"

    def test_telemetry_service_health(self, config, wait_for_services):
        """Test Telemetry Service health endpoint."""
        response = requests.get(f"{config.telemetry_service_url}/health")

        assert response.status_code == 200
        health_data = response.json()
        assert "status" in health_data

    def test_temperature_api_health(self, config, wait_for_services):
        """Test Temperature API health endpoint."""
        response = requests.get(f"{config.temperature_api_url}/health")

        assert response.status_code == 200

    def test_smart_home_service_health(self, config, wait_for_services):
        """Test Smart Home Service health endpoint."""
        response = requests.get(f"{config.smart_home_url}/health")

        assert response.status_code == 200
