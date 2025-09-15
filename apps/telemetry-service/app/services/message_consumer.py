"""
Message consumer for processing Redis pub/sub messages
"""

import asyncio
from typing import Dict, Any

import structlog

from app.config import get_settings
from app.database.redis_client import RedisClient
from app.services.telemetry_service import TelemetryService
from app.models.telemetry import TelemetryData

logger = structlog.get_logger(__name__)
settings = get_settings()


class MessageConsumer:
    """Consumer for processing messages from Redis pub/sub"""
    
    def __init__(self, redis_client: RedisClient, telemetry_service: TelemetryService):
        self.redis = redis_client
        self.telemetry_service = telemetry_service
        self._running = False
        self._tasks = []
        
    async def start_consuming(self):
        """Start consuming messages from Redis channels"""
        try:
            self._running = True
            
            # Subscribe to channels
            await self.redis.subscribe(
                settings.redis_telemetry_channel, 
                self._handle_telemetry_message
            )
            
            await self.redis.subscribe(
                settings.redis_device_events_channel,
                self._handle_device_event
            )
            
            logger.info("Started message consumer", 
                       channels=[settings.redis_telemetry_channel, settings.redis_device_events_channel])
            
            # Start listening for messages
            listen_task = asyncio.create_task(self.redis.listen())
            self._tasks.append(listen_task)
            
            # Start periodic cleanup task
            cleanup_task = asyncio.create_task(self._periodic_cleanup())
            self._tasks.append(cleanup_task)
            
            # Wait for tasks to complete
            await asyncio.gather(*self._tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error("Error in message consumer", error=str(e))
            raise
    
    async def stop_consuming(self):
        """Stop consuming messages"""
        try:
            self._running = False
            
            # Unsubscribe from channels
            await self.redis.unsubscribe(settings.redis_telemetry_channel)
            await self.redis.unsubscribe(settings.redis_device_events_channel)
            
            # Cancel all tasks
            for task in self._tasks:
                task.cancel()
            
            # Wait for tasks to finish
            if self._tasks:
                await asyncio.gather(*self._tasks, return_exceptions=True)
            
            logger.info("Stopped message consumer")
            
        except Exception as e:
            logger.error("Error stopping message consumer", error=str(e))
    
    async def _handle_telemetry_message(self, message: Dict[str, Any]):
        """Handle telemetry messages"""
        try:
            message_type = message.get("type")
            
            if message_type == "telemetry_data":
                await self._process_telemetry_data(message)
            elif message_type == "telemetry_batch":
                await self._process_telemetry_batch(message)
            elif message_type == "device_heartbeat":
                await self._process_device_heartbeat(message)
            else:
                logger.warning("Unknown telemetry message type", type=message_type)
                
        except Exception as e:
            logger.error("Error handling telemetry message", error=str(e), message=message)
    
    async def _handle_device_event(self, message: Dict[str, Any]):
        """Handle device events"""
        try:
            message_type = message.get("type")
            
            if message_type == "device_registered":
                await self._process_device_registered(message)
            elif message_type == "device_status_changed":
                await self._process_device_status_changed(message)
            elif message_type == "device_command_executed":
                await self._process_device_command_executed(message)
            else:
                logger.warning("Unknown device event type", type=message_type)
                
        except Exception as e:
            logger.error("Error handling device event", error=str(e), message=message)
    
    async def _process_telemetry_data(self, message: Dict[str, Any]):
        """Process single telemetry data message"""
        try:
            telemetry_data = message.get("data")
            if not telemetry_data:
                logger.warning("No telemetry data in message")
                return
            
            # Convert to TelemetryData model
            telemetry = TelemetryData(**telemetry_data)
            
            # Store telemetry data
            await self.telemetry_service.store_telemetry(telemetry)
            
            logger.debug("Processed telemetry data message", 
                        device_id=str(telemetry.device_id),
                        measurement=telemetry.measurement)
            
        except Exception as e:
            logger.error("Error processing telemetry data", error=str(e))
    
    async def _process_telemetry_batch(self, message: Dict[str, Any]):
        """Process batch telemetry data message"""
        try:
            batch_data = message.get("data", [])
            if not batch_data:
                logger.warning("No batch data in message")
                return
            
            # Convert to TelemetryData models
            telemetry_batch = []
            for item in batch_data:
                telemetry = TelemetryData(**item)
                telemetry_batch.append(telemetry)
            
            # Store telemetry batch
            await self.telemetry_service.store_telemetry_batch(telemetry_batch)
            
            logger.debug("Processed telemetry batch message", count=len(telemetry_batch))
            
        except Exception as e:
            logger.error("Error processing telemetry batch", error=str(e))
    
    async def _process_device_heartbeat(self, message: Dict[str, Any]):
        """Process device heartbeat message"""
        try:
            device_id = message.get("device_id")
            timestamp = message.get("timestamp")
            
            if not device_id:
                logger.warning("No device_id in heartbeat message")
                return
            
            # Update device last seen timestamp
            device_key = f"device:{device_id}"
            device_info = await self.redis.get(device_key) or {}
            device_info["last_seen"] = timestamp
            device_info["status"] = "online"
            
            await self.redis.set(device_key, device_info, expire=3600)  # 1 hour
            
            logger.debug("Processed device heartbeat", device_id=device_id)
            
        except Exception as e:
            logger.error("Error processing device heartbeat", error=str(e))
    
    async def _process_device_registered(self, message: Dict[str, Any]):
        """Process device registration event"""
        try:
            device_data = message.get("device")
            if not device_data:
                logger.warning("No device data in registration message")
                return
            
            device_id = device_data.get("id")
            if not device_id:
                logger.warning("No device ID in registration message")
                return
            
            # Cache device information
            device_key = f"device:{device_id}"
            await self.redis.set(device_key, device_data, expire=86400)  # 24 hours
            
            logger.info("Processed device registration", device_id=device_id)
            
        except Exception as e:
            logger.error("Error processing device registration", error=str(e))
    
    async def _process_device_status_changed(self, message: Dict[str, Any]):
        """Process device status change event"""
        try:
            device_id = message.get("device_id")
            new_status = message.get("status")
            timestamp = message.get("timestamp")
            
            if not device_id or not new_status:
                logger.warning("Missing device_id or status in status change message")
                return
            
            # Update device status in cache
            device_key = f"device:{device_id}"
            device_info = await self.redis.get(device_key) or {}
            device_info["status"] = new_status
            device_info["status_changed_at"] = timestamp
            
            await self.redis.set(device_key, device_info, expire=3600)  # 1 hour
            
            # If device went offline, create an alert
            if new_status == "offline":
                await self._create_offline_alert(device_id, timestamp)
            
            logger.info("Processed device status change", 
                       device_id=device_id, status=new_status)
            
        except Exception as e:
            logger.error("Error processing device status change", error=str(e))
    
    async def _process_device_command_executed(self, message: Dict[str, Any]):
        """Process device command execution event"""
        try:
            device_id = message.get("device_id")
            command_id = message.get("command_id")
            command_type = message.get("command_type")
            status = message.get("status")
            timestamp = message.get("timestamp")
            
            if not device_id or not command_id:
                logger.warning("Missing device_id or command_id in command execution message")
                return
            
            # Store command execution info
            command_key = f"command_execution:{device_id}:{command_id}"
            execution_info = {
                "device_id": device_id,
                "command_id": command_id,
                "command_type": command_type,
                "status": status,
                "executed_at": timestamp
            }
            
            await self.redis.set(command_key, execution_info, expire=86400)  # 24 hours
            
            logger.info("Processed command execution", 
                       device_id=device_id, command_id=command_id, status=status)
            
        except Exception as e:
            logger.error("Error processing command execution", error=str(e))
    
    async def _create_offline_alert(self, device_id: str, timestamp: str):
        """Create alert when device goes offline"""
        try:
            alert_data = {
                "id": "offline-alert",
                "device_id": device_id,
                "type": "device_offline",
                "severity": "medium",
                "message": f"Device {device_id} went offline",
                "timestamp": timestamp,
                "status": "active"
            }
            
            # Store alert
            alerts_key = f"alerts:{device_id}"
            await self.redis.lpush(alerts_key, alert_data)
            await self.redis.expire(alerts_key, 30 * 24 * 3600)  # 30 days
            
            # Publish alert event
            await self.redis.publish(settings.redis_alerts_channel, {
                "type": "device_offline_alert",
                "alert": alert_data
            })
            
            logger.warning("Created offline alert", device_id=device_id)
            
        except Exception as e:
            logger.error("Error creating offline alert", error=str(e))
    
    async def _periodic_cleanup(self):
        """Periodic cleanup of expired data"""
        while self._running:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                if not self._running:
                    break
                
                # Clean up expired device cache entries
                await self._cleanup_expired_devices()
                
                # Clean up old alerts
                await self._cleanup_old_alerts()
                
                logger.info("Completed periodic cleanup")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in periodic cleanup", error=str(e))
    
    async def _cleanup_expired_devices(self):
        """Clean up expired device cache entries"""
        try:
            device_keys = await self.redis.keys("device:*")
            
            for key in device_keys:
                ttl = await self.redis.ttl(key)
                if ttl == -1:  # No expiration set
                    await self.redis.expire(key, 3600)  # Set 1 hour expiration
                elif ttl == -2:  # Key doesn't exist
                    continue
            
            logger.debug("Cleaned up device cache entries", count=len(device_keys))
            
        except Exception as e:
            logger.error("Error cleaning up device cache", error=str(e))
    
    async def _cleanup_old_alerts(self):
        """Clean up old alerts"""
        try:
            alert_keys = await self.redis.keys("alerts:*")
            
            for key in alert_keys:
                # Keep only last 100 alerts per device
                list_length = await self.redis.llen(key)
                if list_length > 100:
                    # Remove oldest alerts
                    for _ in range(list_length - 100):
                        await self.redis.rpop(key)
            
            logger.debug("Cleaned up old alerts", keys_count=len(alert_keys))
            
        except Exception as e:
            logger.error("Error cleaning up alerts", error=str(e))