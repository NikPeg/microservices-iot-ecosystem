"""
Optimized InfluxDB client with non-blocking initialization
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional

import structlog
from influxdb_client import InfluxDBClient as InfluxClient, Point
from influxdb_client.client.write_api import ASYNCHRONOUS
from influxdb_client.client.exceptions import InfluxDBError
from fastapi import HTTPException

from app.models.telemetry import TelemetryData, TelemetryQuery

logger = structlog.get_logger(__name__)


class OptimizedInfluxDBClient:
    """Optimized InfluxDB client with lazy connection and connection pooling"""

    def __init__(self, url: str, token: str, org: str, bucket: str, timeout: int = 5000):
        self.url = url
        self.token = token
        self.org = org
        self.bucket = bucket
        self.timeout = timeout
        self.client = None
        self.write_api = None
        self.query_api = None
        self.delete_api = None
        self._connection_lock = asyncio.Lock()
        self._connected = False

    async def connect(self):
        """Connect to InfluxDB with timeout and retry logic"""
        async with self._connection_lock:
            if self._connected:
                return

            try:
                # Create client with reduced timeout
                self.client = InfluxClient(
                    url=self.url,
                    token=self.token,
                    org=self.org,
                    timeout=self.timeout
                )

                # Initialize APIs
                self.write_api = self.client.write_api(write_options=ASYNCHRONOUS)
                self.query_api = self.client.query_api()
                self.delete_api = self.client.delete_api()

                # Quick health check with timeout
                await asyncio.wait_for(self._quick_ping(), timeout=3.0)

                self._connected = True
                logger.info("Connected to InfluxDB", url=self.url, org=self.org, bucket=self.bucket)

            except asyncio.TimeoutError:
                logger.warning("InfluxDB connection timeout - will retry later")
                raise
            except Exception as e:
                logger.warning("Failed to connect to InfluxDB - will retry later", error=str(e))
                raise

    async def _quick_ping(self):
        """Quick ping without blocking"""
        try:
            health = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.health()
            )
            if health.status != "pass":
                raise InfluxDBError("InfluxDB health check failed")
            return True
        except Exception as e:
            logger.debug("InfluxDB ping failed", error=str(e))
            raise

    async def ensure_connected(self):
        """Ensure connection is established"""
        if not self._connected:
            await self.connect()

    async def close(self):
        """Close InfluxDB connection"""
        if self.client:
            self.client.close()
            self._connected = False
            logger.info("Closed InfluxDB connection")

    async def ping(self):
        """Test InfluxDB connection"""
        await self.ensure_connected()
        return await self._quick_ping()

    async def write_telemetry(self, telemetry: TelemetryData):
        """Write single telemetry data point"""
        await self.ensure_connected()

        try:
            point = self._create_point(telemetry)
            # Use asyncio.create_task for non-blocking write
            asyncio.create_task(self._write_point_async(point))
            logger.debug("Queued telemetry data", device_id=str(telemetry.device_id), measurement=telemetry.measurement)

        except Exception as e:
            logger.error("Failed to write telemetry data", error=str(e), device_id=str(telemetry.device_id))
            raise

    async def _write_point_async(self, point):
        """Async wrapper for writing points"""
        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.write_api.write(bucket=self.bucket, record=point)
            )
        except Exception as e:
            logger.error("Background write failed", error=str(e))

    async def write_telemetry_batch(self, telemetry_batch: List[TelemetryData]):
        """Write batch of telemetry data points"""
        await self.ensure_connected()

        try:
            points = [self._create_point(telemetry) for telemetry in telemetry_batch]
            # Use asyncio.create_task for non-blocking batch write
            asyncio.create_task(self._write_batch_async(points))
            logger.info("Queued telemetry batch", count=len(telemetry_batch))

        except Exception as e:
            logger.error("Failed to write telemetry batch", error=str(e), count=len(telemetry_batch))
            raise

    async def _write_batch_async(self, points):
        """Async wrapper for writing point batches"""
        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.write_api.write(bucket=self.bucket, record=points)
            )
        except Exception as e:
            logger.error("Background batch write failed", error=str(e))

    def _create_point(self, telemetry: TelemetryData) -> Point:
        """Create InfluxDB point from telemetry data"""
        point = Point(telemetry.measurement) \
            .tag("device_id", str(telemetry.device_id)) \
            .tag("unit", telemetry.unit) \
            .field("value", telemetry.value) \
            .time(telemetry.timestamp)

        # Add location tag if available
        if telemetry.location:
            point = point.tag("location", telemetry.location)

        # Add custom tags
        if telemetry.tags:
            for key, value in telemetry.tags.items():
                point = point.tag(key, str(value))

        # Add metadata as fields
        if telemetry.metadata:
            for key, value in telemetry.metadata.items():
                if isinstance(value, (int, float, bool)):
                    point = point.field(f"meta_{key}", value)
                else:
                    point = point.field(f"meta_{key}", str(value))

        return point

    async def query_telemetry(self, query: TelemetryQuery) -> Dict[str, Any]:
        """Query telemetry data"""
        await self.ensure_connected()

        try:
            # Build Flux query
            flux_query = self._build_flux_query(query)

            # Execute query with timeout
            result = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.query_api.query(flux_query, org=self.org)
                ),
                timeout=10.0
            )

            # Process results
            data_points = []
            for table in result:
                for record in table.records:
                    data_points.append({
                        "timestamp": record.get_time().isoformat(),
                        "device_id": record.values.get("device_id"),
                        "measurement": record.get_measurement(),
                        "value": record.get_value(),
                        "unit": record.values.get("unit"),
                        "location": record.values.get("location"),
                        **{k: v for k, v in record.values.items() if k.startswith("meta_")}
                    })

            logger.info("Queried telemetry data", device_id=query.device_id, count=len(data_points))

            return {
                "device_id": query.device_id,
                "measurement": query.measurement,
                "start_time": query.start_time,
                "end_time": query.end_time,
                "count": len(data_points),
                "data": data_points
            }

        except asyncio.TimeoutError:
            logger.error("Query timeout", device_id=query.device_id)
            raise HTTPException(status_code=504, detail="Query timeout")
        except Exception as e:
            logger.error("Failed to query telemetry data", error=str(e), device_id=query.device_id)
            raise

    def _build_flux_query(self, query: TelemetryQuery) -> str:
        """Build Flux query from query parameters"""
        flux_query = f'''
        from(bucket: "{self.bucket}")
          |> range(start: {query.start_time}, stop: {query.end_time})
          |> filter(fn: (r) => r["device_id"] == "{query.device_id}")
        '''

        if query.measurement:
            flux_query += f'  |> filter(fn: (r) => r["_measurement"] == "{query.measurement}")\n'

        flux_query += f'  |> limit(n: {query.limit})'

        if query.offset > 0:
            flux_query += f'  |> drop(columns: ["_start", "_stop"])\n  |> skip(n: {query.offset})'

        return flux_query

    async def get_latest_telemetry(self, device_id: str, measurement: Optional[str] = None) -> Dict[str, Any]:
        """Get latest telemetry data for a device"""
        await self.ensure_connected()

        try:
            flux_query = f'''
            from(bucket: "{self.bucket}")
              |> range(start: -24h)
              |> filter(fn: (r) => r["device_id"] == "{device_id}")
            '''

            if measurement:
                flux_query += f'  |> filter(fn: (r) => r["_measurement"] == "{measurement}")\n'

            flux_query += '  |> last()'

            result = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.query_api.query(flux_query, org=self.org)
                ),
                timeout=5.0
            )

            latest_data = {}
            for table in result:
                for record in table.records:
                    measurement_name = record.get_measurement()
                    latest_data[measurement_name] = {
                        "timestamp": record.get_time().isoformat(),
                        "value": record.get_value(),
                        "unit": record.values.get("unit"),
                        "location": record.values.get("location")
                    }

            logger.info("Retrieved latest telemetry", device_id=device_id, measurements=len(latest_data))
            return latest_data

        except asyncio.TimeoutError:
            logger.error("Latest telemetry query timeout", device_id=device_id)
            raise HTTPException(status_code=504, detail="Query timeout")
        except Exception as e:
            logger.error("Failed to get latest telemetry", error=str(e), device_id=device_id)
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
        await self.ensure_connected()

        try:
            # Validate aggregation function
            valid_aggregations = ["mean", "max", "min", "sum", "count", "median"]
            if aggregation not in valid_aggregations:
                raise ValueError(f"Invalid aggregation: {aggregation}")

            flux_query = f'''
            from(bucket: "{self.bucket}")
              |> range(start: {start_time}, stop: {end_time})
              |> filter(fn: (r) => r["device_id"] == "{device_id}")
              |> filter(fn: (r) => r["_measurement"] == "{measurement}")
              |> filter(fn: (r) => r["_field"] == "value")
              |> aggregateWindow(every: {window}, fn: {aggregation}, createEmpty: false)
            '''

            result = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.query_api.query(flux_query, org=self.org)
                ),
                timeout=10.0
            )

            data_points = []
            for table in result:
                for record in table.records:
                    data_points.append({
                        "timestamp": record.get_time().isoformat(),
                        "value": record.get_value()
                    })

            logger.info("Retrieved aggregated telemetry",
                       device_id=device_id, measurement=measurement,
                       aggregation=aggregation, count=len(data_points))

            return {
                "device_id": device_id,
                "measurement": measurement,
                "aggregation": aggregation,
                "window": window,
                "start_time": start_time,
                "end_time": end_time,
                "count": len(data_points),
                "data": data_points
            }

        except asyncio.TimeoutError:
            logger.error("Aggregated telemetry query timeout", device_id=device_id)
            raise HTTPException(status_code=504, detail="Query timeout")
        except Exception as e:
            logger.error("Failed to get aggregated telemetry", error=str(e),
                        device_id=device_id, measurement=measurement)
            raise

    async def delete_telemetry(self, device_id: str, start_time: str, end_time: str) -> int:
        """Delete telemetry data for a device within time range"""
        await self.ensure_connected()

        try:
            # Convert time strings to datetime objects
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))

            # Delete data
            await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.delete_api.delete(
                        start=start_dt,
                        stop=end_dt,
                        predicate=f'device_id="{device_id}"',
                        bucket=self.bucket,
                        org=self.org
                    )
                ),
                timeout=10.0
            )

            logger.info("Deleted telemetry data", device_id=device_id,
                       start_time=start_time, end_time=end_time)

            # Return estimated count (InfluxDB doesn't return actual count)
            return 1  # Placeholder

        except asyncio.TimeoutError:
            logger.error("Delete telemetry timeout", device_id=device_id)
            raise HTTPException(status_code=504, detail="Delete timeout")
        except Exception as e:
            logger.error("Failed to delete telemetry data", error=str(e), device_id=device_id)
            raise
