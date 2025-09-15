"""
Redis client for message broker and caching
"""

import asyncio
import json
from typing import Any, Dict, List, Optional, Callable

import redis.asyncio as redis
import structlog

logger = structlog.get_logger(__name__)


class RedisClient:
    """Redis client for pub/sub messaging and caching"""
    
    def __init__(self, host: str, port: int, password: str = "", db: int = 0, timeout: int = 5):
        self.host = host
        self.port = port
        self.password = password
        self.db = db
        self.timeout = timeout
        self.client = None
        self.pubsub = None
        self._subscribers = {}
        
    async def connect(self):
        """Connect to Redis"""
        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                password=self.password if self.password else None,
                db=self.db,
                socket_timeout=self.timeout,
                socket_connect_timeout=self.timeout,
                decode_responses=True
            )
            
            # Test connection
            await self.ping()
            logger.info("Connected to Redis", host=self.host, port=self.port, db=self.db)
            
        except Exception as e:
            logger.error("Failed to connect to Redis", error=str(e))
            raise
    
    async def close(self):
        """Close Redis connection"""
        if self.pubsub:
            await self.pubsub.close()
        if self.client:
            await self.client.close()
        logger.info("Closed Redis connection")
    
    async def ping(self):
        """Test Redis connection"""
        try:
            result = await self.client.ping()
            if not result:
                raise redis.ConnectionError("Redis ping failed")
            return True
        except Exception as e:
            logger.error("Redis ping failed", error=str(e))
            raise
    
    async def publish(self, channel: str, message: Dict[str, Any]):
        """Publish message to Redis channel"""
        try:
            message_json = json.dumps(message, default=str)
            result = await self.client.publish(channel, message_json)
            logger.debug("Published message", channel=channel, subscribers=result)
            return result
        except Exception as e:
            logger.error("Failed to publish message", error=str(e), channel=channel)
            raise
    
    async def subscribe(self, channel: str, callback: Callable[[Dict[str, Any]], None]):
        """Subscribe to Redis channel with callback"""
        try:
            if not self.pubsub:
                self.pubsub = self.client.pubsub()
            
            await self.pubsub.subscribe(channel)
            self._subscribers[channel] = callback
            logger.info("Subscribed to channel", channel=channel)
            
        except Exception as e:
            logger.error("Failed to subscribe to channel", error=str(e), channel=channel)
            raise
    
    async def unsubscribe(self, channel: str):
        """Unsubscribe from Redis channel"""
        try:
            if self.pubsub:
                await self.pubsub.unsubscribe(channel)
                if channel in self._subscribers:
                    del self._subscribers[channel]
                logger.info("Unsubscribed from channel", channel=channel)
        except Exception as e:
            logger.error("Failed to unsubscribe from channel", error=str(e), channel=channel)
            raise
    
    async def listen(self):
        """Listen for messages on subscribed channels"""
        if not self.pubsub:
            logger.warning("No pubsub connection available")
            return
        
        try:
            async for message in self.pubsub.listen():
                if message['type'] == 'message':
                    channel = message['channel']
                    data = message['data']
                    
                    try:
                        # Parse JSON message
                        parsed_data = json.loads(data)
                        
                        # Call registered callback
                        if channel in self._subscribers:
                            callback = self._subscribers[channel]
                            await self._safe_callback(callback, parsed_data)
                        else:
                            logger.warning("No callback registered for channel", channel=channel)
                            
                    except json.JSONDecodeError as e:
                        logger.error("Failed to parse message JSON", error=str(e), channel=channel)
                    except Exception as e:
                        logger.error("Error processing message", error=str(e), channel=channel)
                        
        except Exception as e:
            logger.error("Error in message listener", error=str(e))
            raise
    
    async def _safe_callback(self, callback: Callable, data: Dict[str, Any]):
        """Safely execute callback with error handling"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(data)
            else:
                callback(data)
        except Exception as e:
            logger.error("Callback execution failed", error=str(e))
    
    async def set(self, key: str, value: Any, expire: Optional[int] = None):
        """Set key-value pair in Redis"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value, default=str)
            
            await self.client.set(key, value, ex=expire)
            logger.debug("Set Redis key", key=key, expire=expire)
            
        except Exception as e:
            logger.error("Failed to set Redis key", error=str(e), key=key)
            raise
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value by key from Redis"""
        try:
            value = await self.client.get(key)
            if value is None:
                return None
            
            # Try to parse as JSON
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
                
        except Exception as e:
            logger.error("Failed to get Redis key", error=str(e), key=key)
            raise
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        try:
            result = await self.client.delete(key)
            logger.debug("Deleted Redis key", key=key, existed=bool(result))
            return bool(result)
        except Exception as e:
            logger.error("Failed to delete Redis key", error=str(e), key=key)
            raise
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis"""
        try:
            result = await self.client.exists(key)
            return bool(result)
        except Exception as e:
            logger.error("Failed to check Redis key existence", error=str(e), key=key)
            raise
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration time for key"""
        try:
            result = await self.client.expire(key, seconds)
            logger.debug("Set key expiration", key=key, seconds=seconds, success=bool(result))
            return bool(result)
        except Exception as e:
            logger.error("Failed to set key expiration", error=str(e), key=key)
            raise
    
    async def ttl(self, key: str) -> int:
        """Get time to live for key"""
        try:
            result = await self.client.ttl(key)
            return result
        except Exception as e:
            logger.error("Failed to get key TTL", error=str(e), key=key)
            raise
    
    async def keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern"""
        try:
            result = await self.client.keys(pattern)
            return result
        except Exception as e:
            logger.error("Failed to get keys", error=str(e), pattern=pattern)
            raise
    
    async def flushdb(self):
        """Clear current database"""
        try:
            await self.client.flushdb()
            logger.info("Flushed Redis database", db=self.db)
        except Exception as e:
            logger.error("Failed to flush Redis database", error=str(e))
            raise
    
    async def info(self) -> Dict[str, Any]:
        """Get Redis server information"""
        try:
            result = await self.client.info()
            return result
        except Exception as e:
            logger.error("Failed to get Redis info", error=str(e))
            raise
    
    async def lpush(self, key: str, *values) -> int:
        """Push values to the left of a list"""
        try:
            serialized_values = []
            for value in values:
                if isinstance(value, (dict, list)):
                    serialized_values.append(json.dumps(value, default=str))
                else:
                    serialized_values.append(str(value))
            
            result = await self.client.lpush(key, *serialized_values)
            logger.debug("Pushed to list", key=key, count=len(values))
            return result
        except Exception as e:
            logger.error("Failed to push to list", error=str(e), key=key)
            raise
    
    async def rpop(self, key: str) -> Optional[Any]:
        """Pop value from the right of a list"""
        try:
            value = await self.client.rpop(key)
            if value is None:
                return None
            
            # Try to parse as JSON
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
                
        except Exception as e:
            logger.error("Failed to pop from list", error=str(e), key=key)
            raise
    
    async def llen(self, key: str) -> int:
        """Get length of a list"""
        try:
            result = await self.client.llen(key)
            return result
        except Exception as e:
            logger.error("Failed to get list length", error=str(e), key=key)
            raise
    
    async def lrange(self, key: str, start: int = 0, end: int = -1) -> List[Any]:
        """Get range of values from a list"""
        try:
            values = await self.client.lrange(key, start, end)
            result = []
            for value in values:
                try:
                    result.append(json.loads(value))
                except json.JSONDecodeError:
                    result.append(value)
            return result
        except Exception as e:
            logger.error("Failed to get list range", error=str(e), key=key)
            raise