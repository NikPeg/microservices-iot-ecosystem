"""
Telemetry Service - FastAPI application for IoT telemetry data management
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import List

import structlog
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app

from app.config import get_settings
from app.database.influxdb import InfluxDBClient
from app.database.redis_client import RedisClient
from app.models.telemetry import TelemetryData, TelemetryQuery, TelemetryResponse
from app.services.telemetry_service import TelemetryService
from app.services.message_consumer import MessageConsumer
from app.middleware.logging import setup_logging

# Setup structured logging
setup_logging()
logger = structlog.get_logger(__name__)

settings = get_settings()

# Global clients
influxdb_client = None
redis_client = None
telemetry_service = None
message_consumer = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global influxdb_client, redis_client, telemetry_service, message_consumer
    
    logger.info("Starting Telemetry Service...")
    
    try:
        # Initialize database clients
        influxdb_client = InfluxDBClient(
            url=settings.influxdb_url,
            token=settings.influxdb_token,
            org=settings.influxdb_org,
            bucket=settings.influxdb_bucket
        )
        await influxdb_client.connect()
        logger.info("Connected to InfluxDB")
        
        redis_client = RedisClient(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password,
            db=settings.redis_db
        )
        await redis_client.connect()
        logger.info("Connected to Redis")
        
        # Initialize services
        telemetry_service = TelemetryService(influxdb_client, redis_client)
        
        # Start message consumer
        message_consumer = MessageConsumer(redis_client, telemetry_service)
        consumer_task = asyncio.create_task(message_consumer.start_consuming())
        logger.info("Started message consumer")
        
        yield
        
    except Exception as e:
        logger.error("Failed to initialize services", error=str(e))
        raise
    finally:
        logger.info("Shutting down Telemetry Service...")
        
        # Stop message consumer
        if message_consumer:
            await message_consumer.stop_consuming()
            consumer_task.cancel()
            try:
                await consumer_task
            except asyncio.CancelledError:
                pass
        
        # Close database connections
        if influxdb_client:
            await influxdb_client.close()
        if redis_client:
            await redis_client.close()
        
        logger.info("Telemetry Service shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Telemetry Service",
    description="IoT Telemetry Data Management Service",
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

# Add Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


def get_telemetry_service() -> TelemetryService:
    """Dependency to get telemetry service instance"""
    if telemetry_service is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    return telemetry_service


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check InfluxDB connection
        if influxdb_client:
            await influxdb_client.ping()
        
        # Check Redis connection
        if redis_client:
            await redis_client.ping()
        
        return {
            "status": "healthy",
            "service": "telemetry-service",
            "version": "1.0.0",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unhealthy")


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


@app.get("/api/v1/telemetry/{device_id}/aggregated", response_model=dict)
async def get_aggregated_telemetry(
    device_id: str,
    start_time: str = Query(..., description="Start time in RFC3339 format"),
    end_time: str = Query(..., description="End time in RFC3339 format"),
    measurement: str = Query(..., description="Measurement type"),
    aggregation: str = Query("mean", description="Aggregation function (mean, max, min, sum)"),
    window: str = Query("1h", description="Time window for aggregation"),
    service: TelemetryService = Depends(get_telemetry_service)
):
    """Get aggregated telemetry data"""
    try:
        logger.info("Querying aggregated telemetry", device_id=device_id, aggregation=aggregation)
        
        result = await service.get_aggregated_telemetry(
            device_id=device_id,
            start_time=start_time,
            end_time=end_time,
            measurement=measurement,
            aggregation=aggregation,
            window=window
        )
        return result
        
    except Exception as e:
        logger.error("Failed to get aggregated telemetry", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get aggregated telemetry")


@app.get("/api/v1/devices/{device_id}/alerts", response_model=List[dict])
async def get_device_alerts(
    device_id: str,
    start_time: str = Query(None, description="Start time in RFC3339 format"),
    end_time: str = Query(None, description="End time in RFC3339 format"),
    severity: str = Query(None, description="Filter by alert severity"),
    service: TelemetryService = Depends(get_telemetry_service)
):
    """Get alerts for a specific device"""
    try:
        logger.info("Querying device alerts", device_id=device_id)
        
        alerts = await service.get_device_alerts(
            device_id=device_id,
            start_time=start_time,
            end_time=end_time,
            severity=severity
        )
        return alerts
        
    except Exception as e:
        logger.error("Failed to get device alerts", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get device alerts")


@app.delete("/api/v1/telemetry/{device_id}")
async def delete_device_telemetry(
    device_id: str,
    start_time: str = Query(..., description="Start time in RFC3339 format"),
    end_time: str = Query(..., description="End time in RFC3339 format"),
    service: TelemetryService = Depends(get_telemetry_service)
):
    """Delete telemetry data for a device within time range"""
    try:
        logger.info("Deleting telemetry data", device_id=device_id)
        
        deleted_count = await service.delete_telemetry(device_id, start_time, end_time)
        
        return {
            "status": "success",
            "message": f"Deleted {deleted_count} telemetry records",
            "device_id": device_id,
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        logger.error("Failed to delete telemetry data", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to delete telemetry data")


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
        "app.main:app",
        host="0.0.0.0",
        port=8082,
        reload=settings.debug,
        log_level="info"
    )