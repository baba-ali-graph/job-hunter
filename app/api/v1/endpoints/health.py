"""Health check API endpoints."""

import time
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_client_ip
from app.core.config import settings
from app.core.logging import get_logger, RequestLogger
from app.models.common import HealthResponse, MetricsResponse

logger = get_logger(__name__)
request_logger = RequestLogger()
router = APIRouter()

# Global metrics (in production, use proper metrics collection)
_metrics = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "average_response_time": 0.0,
    "active_connections": 0
}

_start_time = time.time()


@router.get(
    "/",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check the health status of the service"
)
async def health_check(
    client_ip: str = Depends(get_client_ip)
) -> HealthResponse:
    """Health check endpoint."""
    start_time = time.time()
    
    try:
        # Calculate uptime
        uptime = time.time() - _start_time
        
        # Update metrics
        _metrics["total_requests"] += 1
        _metrics["successful_requests"] += 1
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Log request
        request_logger.log_request(
            method="GET",
            url="/api/v1/health/",
            status_code=200,
            response_time=processing_time,
            client_ip=client_ip
        )
        
        return HealthResponse(
            status="healthy",
            version=settings.app_version,
            uptime=uptime
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        request_logger.log_error(
            method="GET",
            url="/api/v1/health/",
            error=e,
            client_ip=client_ip
        )
        
        logger.error("Health check failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "HEALTH_CHECK_FAILED",
                    "message": "Health check failed",
                    "details": {"error": str(e)},
                    "timestamp": time.time(),
                    "request_id": f"req_{int(time.time())}"
                }
            }
        )


@router.get(
    "/ready",
    response_model=Dict[str, str],
    summary="Readiness Check",
    description="Check if the service is ready to accept requests"
)
async def readiness_check(
    client_ip: str = Depends(get_client_ip)
) -> Dict[str, str]:
    """Readiness check endpoint."""
    start_time = time.time()
    
    try:
        # Check if all required services are available
        # For now, just return ready status
        processing_time = time.time() - start_time
        
        request_logger.log_request(
            method="GET",
            url="/api/v1/health/ready",
            status_code=200,
            response_time=processing_time,
            client_ip=client_ip
        )
        
        return {"status": "ready"}
        
    except Exception as e:
        processing_time = time.time() - start_time
        request_logger.log_error(
            method="GET",
            url="/api/v1/health/ready",
            error=e,
            client_ip=client_ip
        )
        
        logger.error("Readiness check failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": {
                    "code": "READINESS_CHECK_FAILED",
                    "message": "Service not ready",
                    "details": {"error": str(e)},
                    "timestamp": time.time(),
                    "request_id": f"req_{int(time.time())}"
                }
            }
        )


@router.get(
    "/live",
    response_model=Dict[str, str],
    summary="Liveness Check",
    description="Check if the service is alive"
)
async def liveness_check(
    client_ip: str = Depends(get_client_ip)
) -> Dict[str, str]:
    """Liveness check endpoint."""
    start_time = time.time()
    
    try:
        # Simple liveness check
        processing_time = time.time() - start_time
        
        request_logger.log_request(
            method="GET",
            url="/api/v1/health/live",
            status_code=200,
            response_time=processing_time,
            client_ip=client_ip
        )
        
        return {"status": "alive"}
        
    except Exception as e:
        processing_time = time.time() - start_time
        request_logger.log_error(
            method="GET",
            url="/api/v1/health/live",
            error=e,
            client_ip=client_ip
        )
        
        logger.error("Liveness check failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "LIVENESS_CHECK_FAILED",
                    "message": "Service not alive",
                    "details": {"error": str(e)},
                    "timestamp": time.time(),
                    "request_id": f"req_{int(time.time())}"
                }
            }
        )


@router.get(
    "/metrics",
    response_model=MetricsResponse,
    summary="Service Metrics",
    description="Get service metrics and statistics"
)
async def get_metrics(
    client_ip: str = Depends(get_client_ip)
) -> MetricsResponse:
    """Get service metrics."""
    start_time = time.time()
    
    try:
        # Calculate uptime
        uptime = time.time() - _start_time
        
        # Update metrics
        _metrics["total_requests"] += 1
        _metrics["successful_requests"] += 1
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Log request
        request_logger.log_request(
            method="GET",
            url="/api/v1/health/metrics",
            status_code=200,
            response_time=processing_time,
            client_ip=client_ip
        )
        
        return MetricsResponse(
            metrics={
                **_metrics,
                "uptime_seconds": uptime,
                "service_version": settings.app_version,
                "environment": "development" if settings.debug else "production"
            }
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        request_logger.log_error(
            method="GET",
            url="/api/v1/health/metrics",
            error=e,
            client_ip=client_ip
        )
        
        logger.error("Failed to get metrics", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "METRICS_ERROR",
                    "message": "Failed to get metrics",
                    "details": {"error": str(e)},
                    "timestamp": time.time(),
                    "request_id": f"req_{int(time.time())}"
                }
            }
        )


def update_metrics(success: bool, response_time: float) -> None:
    """Update global metrics."""
    _metrics["total_requests"] += 1
    if success:
        _metrics["successful_requests"] += 1
    else:
        _metrics["failed_requests"] += 1
    
    # Update average response time (simple moving average)
    current_avg = _metrics["average_response_time"]
    total_requests = _metrics["total_requests"]
    _metrics["average_response_time"] = (current_avg * (total_requests - 1) + response_time) / total_requests