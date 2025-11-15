"""Job analysis API endpoints."""

import time
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from app.api.dependencies import check_rate_limit, get_client_ip
from app.core.exceptions import JobAnalysisError, ValidationError
from app.core.logging import get_logger, RequestLogger
from app.models.common import ErrorResponse
from app.models.job import JobAnalysisRequest, JobAnalysisResponse
from app.services.job_analyzer import JobAnalyzer

logger = get_logger(__name__)
request_logger = RequestLogger()
router = APIRouter()


@router.post(
    "/analyze",
    response_model=JobAnalysisResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        422: {"model": ErrorResponse, "description": "Validation Error"},
        429: {"model": ErrorResponse, "description": "Rate Limit Exceeded"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
    summary="Analyze Job Posting",
    description="Analyze a job posting from URL or raw text and extract key information"
)
async def analyze_job(
    request: JobAnalysisRequest,
    _: None = Depends(check_rate_limit),
    client_ip: str = Depends(get_client_ip)
) -> JobAnalysisResponse:
    """Analyze a job posting."""
    start_time = time.time()
    
    try:
        # Validate request
        if not request.job_url and not request.job_description:
            raise ValidationError("Either job_url or job_description must be provided")
        
        # Initialize job analyzer
        job_analyzer = JobAnalyzer()
        
        # Analyze the job
        job_analysis = await job_analyzer.analyze_job(request)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Log successful request
        request_logger.log_request(
            method="POST",
            url="/api/v1/jobs/analyze",
            status_code=200,
            response_time=processing_time,
            client_ip=client_ip,
            job_id=job_analysis.job_id
        )
        
        return JobAnalysisResponse(
            success=True,
            data=job_analysis,
            processing_time=processing_time
        )
        
    except ValidationError as e:
        processing_time = time.time() - start_time
        request_logger.log_error(
            method="POST",
            url="/api/v1/jobs/analyze",
            error=e,
            client_ip=client_ip
        )
        
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "code": e.error_code,
                    "message": e.message,
                    "details": e.details,
                    "timestamp": time.time(),
                    "request_id": f"req_{int(time.time())}"
                }
            }
        )
        
    except JobAnalysisError as e:
        processing_time = time.time() - start_time
        request_logger.log_error(
            method="POST",
            url="/api/v1/jobs/analyze",
            error=e,
            client_ip=client_ip
        )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": e.error_code,
                    "message": e.message,
                    "details": e.details,
                    "timestamp": time.time(),
                    "request_id": f"req_{int(time.time())}"
                }
            }
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        request_logger.log_error(
            method="POST",
            url="/api/v1/jobs/analyze",
            error=e,
            client_ip=client_ip
        )
        
        logger.error("Unexpected error in job analysis", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                    "details": {"error": str(e)},
                    "timestamp": time.time(),
                    "request_id": f"req_{int(time.time())}"
                }
            }
        )


@router.get(
    "/{job_id}",
    response_model=JobAnalysisResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Job Not Found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
    summary="Get Job Analysis",
    description="Retrieve job analysis results by job ID"
)
async def get_job_analysis(
    job_id: str,
    client_ip: str = Depends(get_client_ip)
) -> JobAnalysisResponse:
    """Get job analysis by ID."""
    start_time = time.time()
    
    try:
        # For now, return a mock response
        # In a real implementation, you would fetch from database
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "JOB_NOT_FOUND",
                    "message": f"Job analysis with ID {job_id} not found",
                    "details": {"job_id": job_id},
                    "timestamp": time.time(),
                    "request_id": f"req_{int(time.time())}"
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        request_logger.log_error(
            method="GET",
            url=f"/api/v1/jobs/{job_id}",
            error=e,
            client_ip=client_ip
        )
        
        logger.error("Unexpected error getting job analysis", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                    "details": {"error": str(e)},
                    "timestamp": time.time(),
                    "request_id": f"req_{int(time.time())}"
                }
            }
        )


@router.get(
    "/",
    response_model=List[Dict[str, Any]],
    summary="List Job Analyses",
    description="List all job analyses (paginated)"
)
async def list_job_analyses(
    skip: int = 0,
    limit: int = 10,
    client_ip: str = Depends(get_client_ip)
) -> List[Dict[str, Any]]:
    """List job analyses."""
    start_time = time.time()
    
    try:
        # For now, return empty list
        # In a real implementation, you would fetch from database
        processing_time = time.time() - start_time
        
        request_logger.log_request(
            method="GET",
            url="/api/v1/jobs/",
            status_code=200,
            response_time=processing_time,
            client_ip=client_ip
        )
        
        return []
        
    except Exception as e:
        processing_time = time.time() - start_time
        request_logger.log_error(
            method="GET",
            url="/api/v1/jobs/",
            error=e,
            client_ip=client_ip
        )
        
        logger.error("Unexpected error listing job analyses", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                    "details": {"error": str(e)},
                    "timestamp": time.time(),
                    "request_id": f"req_{int(time.time())}"
                }
            }
        )