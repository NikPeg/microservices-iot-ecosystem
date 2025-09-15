"""
Telemetry service for processing and storing telemetry data
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from uuid import UUID

import structlog

from app.config import get_settings
from app.database.influxdb import InfluxDBClient
from app.database.redis_client import RedisClient
from app.models.telemetry import TelemetryData, TelemetryQuery, TelemetryResponse, Alert, AlertRule

logger = structlog.get_logger(__name__)
settings = get_settings()


class TelemetryService:
    """Service for telemetry data processing and storage"""
    
    def __init__(self, influxdb_client: InfluxDBClient, redis_client: RedisClient):
        self.influxdb = influxdb_client
        self.redis = redis_client
        self.alert_rules = {}  # In-memory alert rules cache
        self._batch_queue = []
        self._batch_lock = asyncio.Lock()
        
    async def store_telemetry(self, telemetry: TelemetryData):
        """Store single telemetry data point"""
        try:
            # Validate and enrich telemetry data
            enriched_telemetry = await self._enrich_telemetry(telemetry)
            
            # Store in InfluxDB
            await self.influxdb.write_telemetry(enriched_telemetry)
            
            # Check for alerts
            await self._check_alerts(enriched_telemetry)
            
            # Cache latest value
            await self._cache_latest_value(enriched_telemetry)
            
            # Publish event
            await self._publish_telemetry_event(enriched_telemetry)
            
            logger.info("Stored telemetry data", 
                       device_id=str(telemetry.device_id), 
                       measurement=telemetry.measurement)
            
        except Exception as e:
            logger.error("Failed to store telemetry data", 
                        error=str(e), device_id=str(telemetry.device_id))
            raise
    
    async def store_telemetry_batch(self, telemetry_batch: List[TelemetryData]):
        """Store batch of telemetry data points"""
        try:
            # Enrich all telemetry data
            enriched_batch = []
            for telemetry in telemetry_batch:
                enriched = await self._enrich_telemetry(telemetry)
                enriched_batch.append(enriched)
            
            # Store batch in InfluxDB
            await self.influxdb.write_telemetry_batch(enriched_batch)
            
            # Process alerts and caching for each item
            for telemetry in enriched_batch:
                await self._check_alerts(telemetry)
                await self._cache_latest_value(telemetry)
            
            # Publish batch event
            await self._publish_batch_event(enriched_batch)
            
            logger.info("Stored telemetry batch", count=len(telemetry_batch))
            
        except Exception as e:
            logger.error("Failed to store telemetry batch", 
                        error=str(e), count=len(telemetry_batch))
            raise
    
    async def query_telemetry(self, query: TelemetryQuery) -> TelemetryResponse:
        """Query telemetry data"""
        try:
            result = await self.influxdb.query_telemetry(query)
            
            return TelemetryResponse(
                device_id=result["device_id"],
                measurement=result["measurement"],
                start_time=result["start_time"],
                end_time=result["end_time"],
                count=result["count"],
                data=result["data"]
            )
            
        except Exception as e:
            logger.error("Failed to query telemetry data", 
                        error=str(e), device_id=query.device_id)
            raise
    
    async def get_latest_telemetry(self, device_id: str, measurement: Optional[str] = None) -> Dict[str, Any]:
        """Get latest telemetry data for a device"""
        try:
            # Try cache first
            cache_key = f"latest:{device_id}"
            if measurement:
                cache_key += f":{measurement}"
            
            cached_data = await self.redis.get(cache_key)
            if cached_data:
                logger.debug("Retrieved latest telemetry from cache", device_id=device_id)
                return cached_data
            
            # Fallback to InfluxDB
            result = await self.influxdb.get_latest_telemetry(device_id, measurement)
            
            # Cache the result
            if result:
                await self.redis.set(cache_key, result, expire=300)  # 5 minutes
            
            return result
            
        except Exception as e:
            logger.error("Failed to get latest telemetry", 
                        error=str(e), device_id=device_id)
            raise
    
    async def get_aggregated_telemetry(
        self, 
        device_id: str, 
        start_time: str, 
        end_time: str,
        measurement: str,
        aggregation: str = "mean",
        window: str = "1h"
    ) -> Dict[str, Any]:
        """Get aggregated telemetry data"""
        try:
            result = await self.influxdb.get_aggregated_telemetry(
                device_id=device_id,
                start_time=start_time,
                end_time=end_time,
                measurement=measurement,
                aggregation=aggregation,
                window=window
            )
            
            return result
            
        except Exception as e:
            logger.error("Failed to get aggregated telemetry", 
                        error=str(e), device_id=device_id)
            raise
    
    async def delete_telemetry(self, device_id: str, start_time: str, end_time: str) -> int:
        """Delete telemetry data for a device within time range"""
        try:
            # Delete from InfluxDB
            deleted_count = await self.influxdb.delete_telemetry(device_id, start_time, end_time)
            
            # Clear related cache entries
            await self._clear_device_cache(device_id)
            
            return deleted_count
            
        except Exception as e:
            logger.error("Failed to delete telemetry data", 
                        error=str(e), device_id=device_id)
            raise
    
    async def get_device_alerts(
        self, 
        device_id: str, 
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        severity: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get alerts for a specific device"""
        try:
            # Build query for alerts
            alerts_key = f"alerts:{device_id}"
            
            # Get alerts from Redis (stored as list)
            alerts_data = await self.redis.lrange(alerts_key, 0, -1)
            
            # Filter alerts based on criteria
            filtered_alerts = []
            for alert_data in alerts_data:
                if isinstance(alert_data, dict):
                    # Apply time filter
                    if start_time or end_time:
                        alert_time = datetime.fromisoformat(alert_data.get('created_at', ''))
                        if start_time and alert_time < datetime.fromisoformat(start_time.replace('Z', '+00:00')):
                            continue
                        if end_time and alert_time > datetime.fromisoformat(end_time.replace('Z', '+00:00')):
                            continue
                    
                    # Apply severity filter
                    if severity and alert_data.get('severity') != severity:
                        continue
                    
                    filtered_alerts.append(alert_data)
            
            logger.info("Retrieved device alerts", 
                       device_id=device_id, count=len(filtered_alerts))
            
            return filtered_alerts
            
        except Exception as e:
            logger.error("Failed to get device alerts", 
                        error=str(e), device_id=device_id)
            raise
    
    async def _enrich_telemetry(self, telemetry: TelemetryData) -> TelemetryData:
        """Enrich telemetry data with additional information"""
        try:
            # Add processing timestamp
            if not telemetry.metadata:
                telemetry.metadata = {}
            telemetry.metadata['processed_at'] = datetime.utcnow().isoformat()
            
            # Add device location from cache if available
            if not telemetry.location:
                device_info = await self.redis.get(f"device:{telemetry.device_id}")
                if device_info and isinstance(device_info, dict):
                    telemetry.location = device_info.get('location')
            
            return telemetry
            
        except Exception as e:
            logger.error("Failed to enrich telemetry data", error=str(e))
            return telemetry
    
    async def _check_alerts(self, telemetry: TelemetryData):
        """Check telemetry data against alert rules"""
        try:
            # Get alert rules for this device and measurement
            rules = await self._get_alert_rules(telemetry.device_id, telemetry.measurement)
            
            for rule in rules:
                if await self._evaluate_alert_rule(rule, telemetry):
                    await self._trigger_alert(rule, telemetry)
            
        except Exception as e:
            logger.error("Failed to check alerts", error=str(e))
    
    async def _get_alert_rules(self, device_id: UUID, measurement: str) -> List[AlertRule]:
        """Get alert rules for device and measurement"""
        try:
            # Check cache first
            cache_key = f"alert_rules:{device_id}:{measurement}"
            cached_rules = await self.redis.get(cache_key)
            if cached_rules:
                return [AlertRule(**rule) for rule in cached_rules]
            
            # Load default rules based on measurement type
            default_rules = self._get_default_alert_rules(device_id, measurement)
            
            # Cache the rules
            if default_rules:
                rules_data = [rule.dict() for rule in default_rules]
                await self.redis.set(cache_key, rules_data, expire=3600)  # 1 hour
            
            return default_rules
            
        except Exception as e:
            logger.error("Failed to get alert rules", error=str(e))
            return []
    
    def _get_default_alert_rules(self, device_id: UUID, measurement: str) -> List[AlertRule]:
        """Get default alert rules based on measurement type"""
        rules = []
        
        if measurement == "temperature":
            rules.extend([
                AlertRule(
                    id=UUID("00000000-0000-0000-0000-000000000001"),
                    device_id=device_id,
                    measurement=measurement,
                    condition="gt",
                    threshold=settings.temperature_high_threshold,
                    severity="high",
                    message="Temperature too high: {value}°C"
                ),
                AlertRule(
                    id=UUID("00000000-0000-0000-0000-000000000002"),
                    device_id=device_id,
                    measurement=measurement,
                    condition="lt",
                    threshold=settings.temperature_low_threshold,
                    severity="medium",
                    message="Temperature too low: {value}°C"
                )
            ])
        elif measurement == "humidity":
            rules.extend([
                AlertRule(
                    id=UUID("00000000-0000-0000-0000-000000000003"),
                    device_id=device_id,
                    measurement=measurement,
                    condition="gt",
                    threshold=settings.humidity_high_threshold,
                    severity="medium",
                    message="Humidity too high: {value}%"
                ),
                AlertRule(
                    id=UUID("00000000-0000-0000-0000-000000000004"),
                    device_id=device_id,
                    measurement=measurement,
                    condition="lt",
                    threshold=settings.humidity_low_threshold,
                    severity="low",
                    message="Humidity too low: {value}%"
                )
            ])
        elif measurement == "battery":
            rules.extend([
                AlertRule(
                    id=UUID("00000000-0000-0000-0000-000000000005"),
                    device_id=device_id,
                    measurement=measurement,
                    condition="lt",
                    threshold=settings.battery_low_threshold,
                    severity="medium",
                    message="Battery low: {value}%"
                ),
                AlertRule(
                    id=UUID("00000000-0000-0000-0000-000000000006"),
                    device_id=device_id,
                    measurement=measurement,
                    condition="lt",
                    threshold=settings.battery_critical_threshold,
                    severity="critical",
                    message="Battery critical: {value}%"
                )
            ])
        
        return rules
    
    async def _evaluate_alert_rule(self, rule: AlertRule, telemetry: TelemetryData) -> bool:
        """Evaluate if telemetry data triggers an alert rule"""
        try:
            value = telemetry.value
            threshold = rule.threshold
            
            if rule.condition == "gt":
                return value > threshold
            elif rule.condition == "lt":
                return value < threshold
            elif rule.condition == "gte":
                return value >= threshold
            elif rule.condition == "lte":
                return value <= threshold
            elif rule.condition == "eq":
                return value == threshold
            elif rule.condition == "ne":
                return value != threshold
            
            return False
            
        except Exception as e:
            logger.error("Failed to evaluate alert rule", error=str(e))
            return False
    
    async def _trigger_alert(self, rule: AlertRule, telemetry: TelemetryData):
        """Trigger an alert"""
        try:
            # Create alert instance
            alert = Alert(
                id=UUID("00000000-0000-0000-0000-000000000000"),  # Generate proper UUID
                rule_id=rule.id,
                device_id=telemetry.device_id,
                measurement=telemetry.measurement,
                value=telemetry.value,
                threshold=rule.threshold,
                condition=rule.condition,
                severity=rule.severity,
                message=rule.message.format(value=telemetry.value)
            )
            
            # Store alert
            alerts_key = f"alerts:{telemetry.device_id}"
            await self.redis.lpush(alerts_key, alert.dict())
            
            # Set expiration for alerts list (30 days)
            await self.redis.expire(alerts_key, 30 * 24 * 3600)
            
            # Publish alert event
            await self.redis.publish(settings.redis_alerts_channel, {
                "type": "alert_triggered",
                "alert": alert.dict(),
                "telemetry": telemetry.dict()
            })
            
            logger.warning("Alert triggered", 
                          device_id=str(telemetry.device_id),
                          measurement=telemetry.measurement,
                          severity=rule.severity,
                          message=alert.message)
            
        except Exception as e:
            logger.error("Failed to trigger alert", error=str(e))
    
    async def _cache_latest_value(self, telemetry: TelemetryData):
        """Cache latest telemetry value"""
        try:
            cache_key = f"latest:{telemetry.device_id}:{telemetry.measurement}"
            cache_data = {
                "timestamp": telemetry.timestamp.isoformat(),
                "value": telemetry.value,
                "unit": telemetry.unit,
                "location": telemetry.location
            }
            
            await self.redis.set(cache_key, cache_data, expire=3600)  # 1 hour
            
        except Exception as e:
            logger.error("Failed to cache latest value", error=str(e))
    
    async def _publish_telemetry_event(self, telemetry: TelemetryData):
        """Publish telemetry event to message broker"""
        try:
            event = {
                "type": "telemetry_received",
                "device_id": str(telemetry.device_id),
                "measurement": telemetry.measurement,
                "value": telemetry.value,
                "unit": telemetry.unit,
                "timestamp": telemetry.timestamp.isoformat(),
                "location": telemetry.location
            }
            
            await self.redis.publish(settings.redis_telemetry_channel, event)
            
        except Exception as e:
            logger.error("Failed to publish telemetry event", error=str(e))
    
    async def _publish_batch_event(self, telemetry_batch: List[TelemetryData]):
        """Publish batch telemetry event"""
        try:
            event = {
                "type": "telemetry_batch_received",
                "count": len(telemetry_batch),
                "devices": list(set(str(t.device_id) for t in telemetry_batch)),
                "measurements": list(set(t.measurement for t in telemetry_batch)),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self.redis.publish(settings.redis_telemetry_channel, event)
            
        except Exception as e:
            logger.error("Failed to publish batch event", error=str(e))
    
    async def _clear_device_cache(self, device_id: str):
        """Clear all cache entries for a device"""
        try:
            pattern = f"*:{device_id}*"
            keys = await self.redis.keys(pattern)
            
            if keys:
                for key in keys:
                    await self.redis.delete(key)
                
                logger.info("Cleared device cache", device_id=device_id, keys_count=len(keys))
            
        except Exception as e:
            logger.error("Failed to clear device cache", error=str(e))