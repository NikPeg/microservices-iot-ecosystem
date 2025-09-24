"""
Telemetry data models for the Telemetry Service
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


class TelemetryData(BaseModel):
    """Telemetry data point model"""

    device_id: UUID = Field(..., description="Device UUID")
    measurement: str = Field(..., description="Measurement type (temperature, humidity, etc.)")
    value: float = Field(..., description="Measurement value")
    unit: str = Field(..., description="Unit of measurement")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of measurement")
    location: Optional[str] = Field(None, description="Device location")
    tags: Optional[Dict[str, str]] = Field(default_factory=dict, description="Additional tags")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

    @validator('measurement')
    def validate_measurement(cls, v):
        """Validate measurement type"""
        allowed_measurements = [
            'temperature', 'humidity', 'pressure', 'light', 'motion',
            'battery', 'battery_level', 'voltage', 'current', 'power', 'energy',
            'co2', 'tvoc', 'pm25', 'pm10', 'noise'
        ]
        if v.lower() not in allowed_measurements:
            raise ValueError(f'Invalid measurement type: {v}')
        return v.lower()

    @validator('value')
    def validate_value(cls, v, values):
        """Validate measurement value based on type"""
        measurement = values.get('measurement', '').lower()

        # Define reasonable ranges for different measurements
        ranges = {
            'temperature': (-50, 100),  # Celsius
            'humidity': (0, 100),       # Percentage
            'pressure': (300, 1200),    # hPa
            'light': (0, 100000),       # Lux
            'battery': (0, 100),        # Percentage
            'battery_level': (0, 100),  # Percentage
            'voltage': (0, 50),         # Volts
            'current': (0, 100),        # Amperes
            'power': (0, 10000),        # Watts
            'co2': (0, 5000),          # ppm
            'pm25': (0, 500),          # μg/m³
            'pm10': (0, 500),          # μg/m³
            'noise': (0, 120),         # dB
        }

        if measurement in ranges:
            min_val, max_val = ranges[measurement]
            if not (min_val <= v <= max_val):
                raise ValueError(f'Value {v} out of range for {measurement}: [{min_val}, {max_val}]')

        return v

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class TelemetryQuery(BaseModel):
    """Query parameters for telemetry data"""

    device_id: str = Field(..., description="Device ID")
    start_time: str = Field(..., description="Start time in RFC3339 format")
    end_time: str = Field(..., description="End time in RFC3339 format")
    measurement: Optional[str] = Field(None, description="Filter by measurement type")
    limit: int = Field(default=1000, ge=1, le=10000, description="Maximum number of records")
    offset: int = Field(default=0, ge=0, description="Offset for pagination")

    @validator('start_time', 'end_time')
    def validate_time_format(cls, v):
        """Validate time format"""
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError(f'Invalid time format: {v}. Use RFC3339 format.')
        return v


class TelemetryResponse(BaseModel):
    """Response model for telemetry queries"""

    device_id: str = Field(..., description="Device ID")
    measurement: Optional[str] = Field(None, description="Measurement type filter")
    start_time: str = Field(..., description="Query start time")
    end_time: str = Field(..., description="Query end time")
    count: int = Field(..., description="Number of records returned")
    data: List[Dict[str, Any]] = Field(..., description="Telemetry data points")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AlertRule(BaseModel):
    """Alert rule configuration"""

    id: UUID = Field(..., description="Alert rule ID")
    device_id: Optional[UUID] = Field(None, description="Device ID (null for global rules)")
    measurement: str = Field(..., description="Measurement type")
    condition: str = Field(..., description="Alert condition (gt, lt, eq, ne)")
    threshold: float = Field(..., description="Threshold value")
    severity: str = Field(..., description="Alert severity (low, medium, high, critical)")
    message: str = Field(..., description="Alert message template")
    enabled: bool = Field(default=True, description="Whether rule is enabled")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('condition')
    def validate_condition(cls, v):
        """Validate alert condition"""
        allowed_conditions = ['gt', 'lt', 'eq', 'ne', 'gte', 'lte']
        if v not in allowed_conditions:
            raise ValueError(f'Invalid condition: {v}. Allowed: {allowed_conditions}')
        return v

    @validator('severity')
    def validate_severity(cls, v):
        """Validate alert severity"""
        allowed_severities = ['low', 'medium', 'high', 'critical']
        if v.lower() not in allowed_severities:
            raise ValueError(f'Invalid severity: {v}. Allowed: {allowed_severities}')
        return v.lower()


class Alert(BaseModel):
    """Alert instance model"""

    id: UUID = Field(..., description="Alert ID")
    rule_id: UUID = Field(..., description="Alert rule ID")
    device_id: UUID = Field(..., description="Device ID")
    measurement: str = Field(..., description="Measurement type")
    value: float = Field(..., description="Measurement value that triggered alert")
    threshold: float = Field(..., description="Threshold value")
    condition: str = Field(..., description="Alert condition")
    severity: str = Field(..., description="Alert severity")
    message: str = Field(..., description="Alert message")
    status: str = Field(default="active", description="Alert status (active, acknowledged, resolved)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    acknowledged_at: Optional[datetime] = Field(None)
    resolved_at: Optional[datetime] = Field(None)

    @validator('status')
    def validate_status(cls, v):
        """Validate alert status"""
        allowed_statuses = ['active', 'acknowledged', 'resolved']
        if v.lower() not in allowed_statuses:
            raise ValueError(f'Invalid status: {v}. Allowed: {allowed_statuses}')
        return v.lower()


class DeviceStats(BaseModel):
    """Device statistics model"""

    device_id: UUID = Field(..., description="Device ID")
    measurement_count: int = Field(..., description="Total number of measurements")
    last_seen: datetime = Field(..., description="Last telemetry timestamp")
    measurements: Dict[str, Dict[str, Any]] = Field(..., description="Statistics per measurement type")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class BatchTelemetryData(BaseModel):
    """Batch telemetry data model"""

    device_id: UUID = Field(..., description="Device UUID")
    data_points: List[Dict[str, Any]] = Field(..., description="List of telemetry data points")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Batch timestamp")

    @validator('data_points')
    def validate_data_points(cls, v):
        """Validate data points structure"""
        if not v:
            raise ValueError('Data points cannot be empty')

        required_fields = ['measurement', 'value', 'unit']
        for point in v:
            for field in required_fields:
                if field not in point:
                    raise ValueError(f'Missing required field: {field}')

        return v

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
