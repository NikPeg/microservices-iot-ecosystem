"""
Configuration settings for Telemetry Service
"""

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Application settings
    app_name: str = "telemetry-service"
    debug: bool = False
    version: str = "1.0.0"
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8082
    
    # CORS settings
    allowed_origins: List[str] = ["*"]
    
    # InfluxDB settings
    influxdb_url: str = Field(default="http://localhost:8086", env="INFLUXDB_URL")
    influxdb_token: str = Field(default="telemetry-token", env="INFLUXDB_TOKEN")
    influxdb_org: str = Field(default="smart-home", env="INFLUXDB_ORG")
    influxdb_bucket: str = Field(default="telemetry", env="INFLUXDB_BUCKET")
    influxdb_timeout: int = Field(default=10000, env="INFLUXDB_TIMEOUT")
    
    # Redis settings
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_password: str = Field(default="", env="REDIS_PASSWORD")
    redis_db: int = Field(default=0, env="REDIS_DB")
    redis_timeout: int = Field(default=5, env="REDIS_TIMEOUT")
    
    # Message broker channels
    redis_telemetry_channel: str = "telemetry.data"
    redis_device_events_channel: str = "device.events"
    redis_alerts_channel: str = "alerts.notifications"
    
    # Telemetry processing settings
    batch_size: int = Field(default=100, env="TELEMETRY_BATCH_SIZE")
    batch_timeout: int = Field(default=5, env="TELEMETRY_BATCH_TIMEOUT")
    retention_days: int = Field(default=365, env="TELEMETRY_RETENTION_DAYS")
    
    # Alert thresholds
    temperature_high_threshold: float = Field(default=35.0, env="TEMP_HIGH_THRESHOLD")
    temperature_low_threshold: float = Field(default=5.0, env="TEMP_LOW_THRESHOLD")
    humidity_high_threshold: float = Field(default=80.0, env="HUMIDITY_HIGH_THRESHOLD")
    humidity_low_threshold: float = Field(default=20.0, env="HUMIDITY_LOW_THRESHOLD")
    battery_low_threshold: float = Field(default=20.0, env="BATTERY_LOW_THRESHOLD")
    battery_critical_threshold: float = Field(default=10.0, env="BATTERY_CRITICAL_THRESHOLD")
    
    # Logging settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    # Integration settings
    device_service_url: str = Field(default="http://localhost:8081", env="DEVICE_SERVICE_URL")
    monolith_url: str = Field(default="http://localhost:8080", env="MONOLITH_URL")
    
    # Monitoring settings
    metrics_enabled: bool = Field(default=True, env="METRICS_ENABLED")
    health_check_interval: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()