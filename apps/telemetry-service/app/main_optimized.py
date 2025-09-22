"""
Optimized Telemetry Service - Fast startup with lazy initialization
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import List, Optional

import structlog
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database.influxdb_optimized import OptimizedInfluxDBClient
from app.database.redis_client import RedisClient
from app.models.telemetry import TelemetryData, TelemetryQuery, TelemetryResponse
from app.services.telemetry_service import TelemetryService
from app.services.message_consumer import MessageConsumer
from app.middleware.logging import setup_logging

# Setup structured logging
setup_logging()
logger = structlog.get_logger(__name__)

settings = get_settings()

# Global clients - initialized lazily
influxdb_client: Optional[OptimizedInfluxDBClient] = None
redis_client: Optional[RedisClient] = None
telemetry_service: Optional[TelemetryService] = None
message_consumer: Optional[MessageConsumer] = None

# Connection status flags
_influxdb_ready = False
_redis_ready = False
_services_initialized = False


async def initialize_connections():
    """Initialize database connections with retries and timeouts"""
    global influxdb_client, redis_client, _influxdb_ready, _redis_ready

    # Initialize Redis first (faster)
    if not _redis_ready:
        try:
            redis_client = RedisClient(
                host=settings.redis_host,
                port=settings.redis_port,
                password=settings.redis_password,
                db=settings.redis_db,
                timeout=2  # Reduced timeout
            )
            await asyncio.wait_for(redis_client.connect(), timeout=5.0)
            _redis_ready = True
            logger.info("Redis connected successfully")
        except Exception as e:
            logger.warning("Redis connection failed, will retry later", error=str(e))

    # Initialize InfluxDB with timeout
    if not _influxdb_ready:
        try:
            influxdb_client = OptimizedInfluxDBClient(
                url=settings.influxdb_url,
                token=settings.influxdb_token,
                org=settings.influxdb_org,
                bucket=settings.influxdb_bucket,
                timeout=3000  # Reduced timeout
            )
            await asyncio.wait_for(influxdb_client.connect(), timeout=5.0)
            _influxdb_ready = True
            logger.info("InfluxDB connected successfully")
        except Exception as e:
            logger.warning("InfluxDB connection failed, will retry later", error=str(e))


async def initialize_services():
    """Initialize services after connections are ready"""
    global telemetry_service, message_consumer, _services_initialized

    if _services_initialized:
        return

    if _redis_ready and _influxdb_ready:
        try:
            # Initialize services
            telemetry_service = TelemetryService(influxdb_client, redis_client)

            # Start message consumer in background
            message_consumer = MessageConsumer(redis_client, telemetry_service)
            asyncio.create_task(message_consumer.start_consuming())

            _services_initialized = True
            logger.info("Services initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize services", error=str(e))


async def ensure_connections():
    """Ensure connections are ready, initialize if needed"""
    if not (_influxdb_ready and _redis_ready):
        await initialize_connections()

    if not _services_initialized and _influxdb_ready and _redis_ready:
        await initialize_services()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - non-blocking startup"""
    logger.info("Starting Telemetry Service...")

    # Start connection initialization in background
    asyncio.create_task(initialize_connections())

    # Don't wait for connections during startup - let the service start quickly
    logger.info("Telemetry Service started (connections initializing in background)")

    yield

    # Cleanup on shutdown
    logger.info("Shutting down Telemetry Service...")

    if message_consumer:
        try:
            await message_consumer.stop_consuming()
        except Exception as e:
            logger.error("Error stopping message consumer", error=str(e))

    if influxdb_client:
        try:
            await influxdb_client.close()
        except Exception as e:
            logger.error("Error closing InfluxDB", error=str(e))

    if redis_client:
        try:
            await redis_client.close()
        except Exception as e:
            logger.error("Error closing Redis", error=str(e))

    logger.info("Telemetry Service shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Telemetry Service",
    description="IoT Telemetry Data Management Service (Optimized)",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def get_telemetry_service() -> TelemetryService:
    """Dependency to get telemetry service instance with lazy initialization"""
    await ensure_connections()

    if telemetry_service is None:
        raise HTTPException(
            status_code=503,
            detail="Telemetry service not ready - connections still initializing"
        )
    return telemetry_service


@app.get("/health")
async def health_check():
    """Health check endpoint - always responds quickly"""
    status = "starting"
    details = {
        "service": "telemetry-service",
        "version": "1.0.0",
        "redis_ready": _redis_ready,
        "influxdb_ready": _influxdb_ready,
        "services_ready": _services_initialized
    }

    if _redis_ready and _influxdb_ready and _services_initialized:
        status = "healthy"
        # Quick ping without blocking
        try:
            if redis_client:
                await asyncio.wait_for(redis_client.ping(), timeout=1.0)
            if influxdb_client:
                await asyncio.wait_for(influxdb_client.ping(), timeout=2.0)
        except Exception as e:
            status = "degraded"
            details["error"] = str(e)
    elif _redis_ready or _influxdb_ready:
        status = "initializing"

    return {
        "status": status,
        **details,
        "timestamp": "2024-01-01T00:00:00Z"
    }


@app.get("/ready")
async def readiness_check():
    """Readiness check - indicates if service can handle requests"""
    if not (_redis_ready and _influxdb_ready and _services_initialized):
        raise HTTPException(
            status_code=503,
            detail="Service not ready - still initializing connections"
        )

    return {
        "status": "ready",
        "service": "telemetry-service",
        "connections": {
            "redis": _redis_ready,
            "influxdb": _influxdb_ready,
            "services": _services_initialized
        }
    }


@app.post("/api/v1/telemetry", response_model=dict)
async def store_telemetry(
    telemetry_data: TelemetryData,
    background_tasks: BackgroundTasks,
    service: TelemetryService = Depends(get_telemetry_service)
):
    """Store telemetry data"""
    try:
        logger.info("Received telemetry data", device_id=str(telemetry_data.device_id))

        # Store data asynchronously
        background_tasks.add_task(service.store_telemetry, telemetry_data)

        return {
            "status": "accepted",
            "message": "Telemetry data queued for processing",
            "device_id": str(telemetry_data.device_id),
            "timestamp": telemetry_data.timestamp
        }
    except Exception as e:
        logger.error("Failed to store telemetry data", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to store telemetry data")


@app.post("/api/v1/telemetry/batch", response_model=dict)
async def store_telemetry_batch(
    telemetry_batch: List[TelemetryData],
    background_tasks: BackgroundTasks,
    service: TelemetryService = Depends(get_telemetry_service)
):
    """Store multiple telemetry data points"""
    try:
        logger.info("Received telemetry batch", count=len(telemetry_batch))

        # Store batch asynchronously
        background_tasks.add_task(service.store_telemetry_batch, telemetry_batch)

        return {
            "status": "accepted",
            "message": f"Batch of {len(telemetry_batch)} telemetry records queued for processing",
            "count": len(telemetry_batch)
        }
    except Exception as e:
        logger.error("Failed to store telemetry batch", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to store telemetry batch")


@app.get("/api/v1/telemetry/{device_id}", response_model=TelemetryResponse)
async def get_device_telemetry(
    device_id: str,
    start_time: str = Query(..., description="Start time in RFC3339 format"),
    end_time: str = Query(..., description="End time in RFC3339 format"),
    measurement: str = Query(None, description="Filter by measurement type"),
    limit: int = Query(1000, ge=1, le=10000, description="Maximum number of records"),
    service: TelemetryService = Depends(get_telemetry_service)
):
    """Get telemetry data for a specific device"""
    try:
        logger.info("Querying telemetry data", device_id=device_id)

        query = TelemetryQuery(
            device_id=device_id,
            start_time=start_time,
            end_time=end_time,
            measurement=measurement,
            limit=limit
        )

        result = await service.query_telemetry(query)
        return result

    except Exception as e:
        logger.error("Failed to query telemetry data", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to query telemetry data")


@app.get("/api/v1/telemetry/{device_id}/latest", response_model=dict)
async def get_latest_telemetry(
    device_id: str,
    measurement: str = Query(None, description="Filter by measurement type"),
    service: TelemetryService = Depends(get_telemetry_service)
):
    """Get latest telemetry data for a device"""
    try:
        logger.info("Querying latest telemetry", device_id=device_id)

        result = await service.get_latest_telemetry(device_id, measurement)
        return result

    except Exception as e:
        logger.error("Failed to get latest telemetry", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get latest telemetry")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error("Unhandled exception", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "path": request.url.path
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main_optimized:app",
        host="0.0.0.0",
        port=8082,
        reload=settings.debug,
        log_level="info"
    )
