"""Logging configuration for the Job Hunter Bot."""

import logging
import sys
from typing import Any, Dict

import structlog
from structlog.stdlib import LoggerFactory

from app.core.config import settings


def configure_logging() -> None:
    """Configure structured logging."""
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper()),
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
    
    if settings.log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())
    
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


class RequestLogger:
    """Logger for HTTP requests."""
    
    def __init__(self):
        self.logger = get_logger("request")
    
    def log_request(
        self,
        method: str,
        url: str,
        status_code: int,
        response_time: float,
        **kwargs: Any,
    ) -> None:
        """Log HTTP request details."""
        self.logger.info(
            "HTTP request",
            method=method,
            url=url,
            status_code=status_code,
            response_time_ms=round(response_time * 1000, 2),
            **kwargs,
        )
    
    def log_error(
        self,
        method: str,
        url: str,
        error: Exception,
        **kwargs: Any,
    ) -> None:
        """Log HTTP request error."""
        self.logger.error(
            "HTTP request error",
            method=method,
            url=url,
            error=str(error),
            error_type=type(error).__name__,
            **kwargs,
        )