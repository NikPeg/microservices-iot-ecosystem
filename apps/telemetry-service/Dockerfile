# Multi-stage build for Telemetry Service
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Create logs directory
RUN mkdir -p logs && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8082

# Health check using curl
HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=5 \
    CMD curl -f http://localhost:8082/health || exit 1

# Environment variables with defaults
ENV PYTHONPATH=/app \
    INFLUXDB_URL=http://influxdb:8086 \
    INFLUXDB_TOKEN=telemetry-token \
    INFLUXDB_ORG=smart-home \
    INFLUXDB_BUCKET=telemetry \
    REDIS_HOST=redis \
    REDIS_PORT=6379 \
    LOG_LEVEL=INFO

# Run the optimized application
CMD ["python", "-m", "uvicorn", "app.main_optimized:app", "--host", "0.0.0.0", "--port", "8082", "--timeout-keep-alive", "5"]
