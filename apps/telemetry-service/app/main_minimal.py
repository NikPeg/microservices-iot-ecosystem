"""
Minimal Telemetry Service - для диагностики проблемы
"""

import asyncio
import logging
from contextlib import asynccontextmanager

import structlog
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings

# Setup structured logging
logging.basicConfig(level=logging.INFO)
logger = structlog.get_logger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Minimal lifespan manager"""
    logger.info("Starting Minimal Telemetry Service...")

    try:
        # Минимальная инициализация без внешних зависимостей
        logger.info("Service initialized successfully")
        yield

    except Exception as e:
        logger.error("Failed to initialize service", error=str(e))
        raise
    finally:
        logger.info("Shutting down Minimal Telemetry Service...")


# Create FastAPI application
app = FastAPI(
    title="Minimal Telemetry Service",
    description="Minimal version for debugging",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {
        "status": "healthy",
        "service": "minimal-telemetry-service",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Minimal Telemetry Service is running"}


@app.get("/test")
async def test():
    """Test endpoint"""
    return {"test": "ok", "async": True}


if __name__ == "__main__":
    uvicorn.run(
        "app.main_minimal:app",
        host="0.0.0.0",
        port=8082,
        reload=False,
        log_level="info"
    )
