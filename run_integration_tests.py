#!/usr/bin/env python3
"""
Quick integration test runner script.
"""
import subprocess
import sys
import time
import requests
from datetime import datetime


def check_service_health(url, name):
    """Check if a service is healthy."""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✓ {name} is healthy")
            return True
        else:
            print(f"✗ {name} returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ {name} is not accessible: {e}")
        return False


def run_tests():
    """Run integration tests."""
    print("=" * 60)
    print("Smart Home Integration Tests")
    print("=" * 60)
    print(f"Started at: {datetime.now()}")

    # Check service health first
    print("\n1. Checking service health...")
    services = [
        ("http://localhost:8081/device-service/actuator/health", "Device Service"),
        ("http://localhost:8082/health", "Telemetry Service"),
        ("http://localhost:8083/health", "Temperature API"),
        ("http://localhost:8080/health", "Smart Home Service")
    ]

    healthy_services = 0
    for url, name in services:
        if check_service_health(url, name):
            healthy_services += 1

    print(f"\nServices healthy: {healthy_services}/{len(services)}")

    if healthy_services < len(services):
        print("⚠️  Some services are not healthy. Tests may fail.")

    # Run pytest tests
    print("\n2. Running integration tests...")
    try:
        result = subprocess.run([
            "python", "-m", "pytest",
            "tests/integration/",
            "-v",
            "--tb=short",
            "--maxfail=5"
        ], capture_output=True, text=True, timeout=120)

        print("STDOUT:")
        print(result.stdout)

        if result.stderr:
            print("STDERR:")
            print(result.stderr)

        print(f"\nTest execution completed with exit code: {result.returncode}")
        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print("⚠️  Tests timed out after 2 minutes")
        return False
    except Exception as e:
        print(f"✗ Error running tests: {e}")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
