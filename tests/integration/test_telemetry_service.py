"""
Integration tests for Telemetry Service.
"""
import pytest
import requests
import time
from datetime import datetime, timezone, timedelta


class TestTelemetryService:
    """Test Telemetry Service API endpoints."""

    def test_store_telemetry_data(self, config, wait_for_services, telemetry_data):
        """Test storing single telemetry data point."""
        response = requests.post(
            f"{config.telemetry_service_url}/api/v1/telemetry",
            json=telemetry_data,
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 200
        result = response.json()
        assert "message" in result or "status" in result

    def test_store_telemetry_batch(self, config, wait_for_services, telemetry_batch_data):
        """Test storing batch telemetry data."""
        response = requests.post(
            f"{config.telemetry_service_url}/api/v1/telemetry/batch",
            json=telemetry_batch_data,
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 200
        result = response.json()
        assert "message" in result or "status" in result

    def test_get_device_telemetry(self, config, wait_for_services, telemetry_data):
        """Test getting device telemetry data."""
        # First store some data
        requests.post(
            f"{config.telemetry_service_url}/api/v1/telemetry",
            json=telemetry_data,
            headers={"Content-Type": "application/json"}
        )

        # Wait a moment for data to be processed
        time.sleep(2)

        # Generate time range
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=1)

        device_id = telemetry_data["device_id"]
        response = requests.get(
            f"{config.telemetry_service_url}/api/v1/telemetry/{device_id}",
            params={
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "limit": 10
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))

    def test_get_latest_telemetry(self, config, wait_for_services, telemetry_data):
        """Test getting latest telemetry data."""
        # First store some data
        requests.post(
            f"{config.telemetry_service_url}/api/v1/telemetry",
            json=telemetry_data,
            headers={"Content-Type": "application/json"}
        )

        # Wait a moment for data to be processed
        time.sleep(2)

        device_id = telemetry_data["device_id"]
        response = requests.get(f"{config.telemetry_service_url}/api/v1/telemetry/{device_id}/latest")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))

    def test_get_latest_telemetry_with_measurement_filter(self, config, wait_for_services, telemetry_data):
        """Test getting latest telemetry with measurement filter."""
        # First store some data
        requests.post(
            f"{config.telemetry_service_url}/api/v1/telemetry",
            json=telemetry_data,
            headers={"Content-Type": "application/json"}
        )

        # Wait a moment for data to be processed
        time.sleep(2)

        device_id = telemetry_data["device_id"]
        response = requests.get(
            f"{config.telemetry_service_url}/api/v1/telemetry/{device_id}/latest",
            params={"measurement": "temperature"}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))

    def test_get_aggregated_telemetry(self, config, wait_for_services, telemetry_data):
        """Test getting aggregated telemetry data."""
        # First store some data
        requests.post(
            f"{config.telemetry_service_url}/api/v1/telemetry",
            json=telemetry_data,
            headers={"Content-Type": "application/json"}
        )

        # Wait a moment for data to be processed
        time.sleep(2)

        # Generate time range
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=1)

        device_id = telemetry_data["device_id"]
        response = requests.get(
            f"{config.telemetry_service_url}/api/v1/telemetry/{device_id}/aggregated",
            params={
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "measurement": "temperature",
                "aggregation": "mean",
                "window": "1h"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))

    def test_get_device_alerts(self, config, wait_for_services):
        """Test getting device alerts."""
        device_id = "123e4567-e89b-12d3-a456-426614174000"
        response = requests.get(f"{config.telemetry_service_url}/api/v1/devices/{device_id}/alerts")

        assert response.status_code == 200
        alerts = response.json()
        assert isinstance(alerts, (list, dict))

    def test_invalid_endpoint(self, config, wait_for_services):
        """Test invalid endpoint returns 404."""
        response = requests.get(f"{config.telemetry_service_url}/api/v1/invalid")

        assert response.status_code == 404

    def test_invalid_telemetry_data(self, config, wait_for_services):
        """Test storing invalid telemetry data."""
        invalid_data = {
            "invalid_field": "invalid_value"
        }

        response = requests.post(
            f"{config.telemetry_service_url}/api/v1/telemetry",
            json=invalid_data,
            headers={"Content-Type": "application/json"}
        )

        # Should return 400 or 422 for invalid data
        assert response.status_code in [400, 422]
