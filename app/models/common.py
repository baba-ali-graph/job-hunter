"""Common data models."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: Dict[str, Any] = Field(
        ...,
        description="Error details including code, message, and additional information"
    )
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid input provided",
                    "details": {
                        "field": "job_url",
                        "value": "invalid-url",
                        "suggestion": "Please provide a valid job posting URL"
                    },
                    "timestamp": "2024-12-01T10:00:00Z",
                    "request_id": "req_123456"
                }
            }
        }


class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: str = Field(..., description="Service health status")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(..., description="Application version")
    uptime: float = Field(..., description="Service uptime in seconds")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2024-12-01T10:00:00Z",
                "version": "1.0.0",
                "uptime": 3600.5
            }
        }


class MetricsResponse(BaseModel):
    """Metrics response model."""
    
    metrics: Dict[str, Any] = Field(..., description="Service metrics")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "metrics": {
                    "total_requests": 1000,
                    "successful_requests": 950,
                    "failed_requests": 50,
                    "average_response_time": 1.5,
                    "active_connections": 10
                },
                "timestamp": "2024-12-01T10:00:00Z"
            }
        }