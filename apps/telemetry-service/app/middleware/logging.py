"""
Logging middleware and configuration
"""

import logging
import sys
from typing import Any, Dict

import structlog


def setup_logging(log_level: str = "INFO", log_format: str = "json") -> None:
    """Setup structured logging configuration"""

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper(), logging.INFO),
    )

    # Configure structlog
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if log_format.lower() == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


class LoggingMiddleware:
    """Middleware for request/response logging"""

    def __init__(self, app):
        self.app = app
        self.logger = structlog.get_logger(__name__)

    async def __call__(self, scope: Dict[str, Any], receive, send):
        """Process request with logging"""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Extract request info
        method = scope.get("method", "")
        path = scope.get("path", "")

        self.logger.info("Request started", method=method, path=path)

        # Process request
        try:
            await self.app(scope, receive, send)
            self.logger.info("Request completed", method=method, path=path)
        except Exception as e:
            self.logger.error("Request failed", method=method, path=path, error=str(e))
            raise
