"""CV analysis API endpoints."""

import time
from typing import Dict, List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.api.dependencies import check_rate_limit, get_client_ip
from app.core.config import settings
from app.core.exceptions import CVAnalysisError, FileProcessingError, ValidationError
from app.core.logging import get_logger, RequestLogger
from app.models.common import ErrorResponse
from app.models.cv import CVAnalysisRequest, CVAnalysisResponse, CVOptimizationRequest, CVOptimizationResponse
from app.services.cv_analyzer import CVAnalyzer

logger = get_logger(__name__)
request_logger = RequestLogger()
router = APIRouter()


@router.post(
    "/analyze",
    response_model=CVAnalysisResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        422: {"model": ErrorResponse, "description": "Validation Error"},
        429: {"model": ErrorResponse, "description": "Rate Limit Exceeded"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
    summary="Analyze CV",
    description="Analyze a CV file and extract key information"
)
async def analyze_cv(
    file: UploadFile = File(..., description="CV file (PDF or DOCX)"),
    request_obj: Depends(check_rate_limit),
    client_ip: str = Depends(get_client_ip)
) -> CVAnalysisResponse:
    """Analyze a CV file."""
    start_time = time.time()
    
    try:
        # Validate file
        if not file.filename:
            raise ValidationError("No file provided")
        
        # Check file type
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in settings.allowed_file_types:
            raise ValidationError(
                f"Unsupported file type. Allowed types: {', '.join(settings.allowed_file_types)}",
                field="file"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Validate file size
        if len(file_content) > settings.max_file_size:
            raise ValidationError(
                f"File too large. Maximum size: {settings.max_file_size} bytes",
                field="file"
            )
        
        # Create CV analysis request
        cv_request = CVAnalysisRequest(
            file_name=file.filename,
            file_content=file_content,
            file_type=file_extension
        )
        
        # Initialize CV analyzer
        cv_analyzer = CVAnalyzer()
        
        # Analyze the CV
        cv_analysis = await cv_analyzer.analyze_cv(cv_request)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Log successful request
        request_logger.log_request(
            method="POST",
            url="/api/v1/cv/analyze",
            status_code=200,
            response_time=processing_time,
            client_ip=client_ip,
            cv_id=cv_analysis.cv_id
        )
        
        return CVAnalysisResponse(
            success=True,
            data=cv_analysis,
            processing_time=processing_time
        )
        
    except ValidationError as e:
        processing_time = time.time() - start_time
        request_logger.log_error(
            method="POST",
            url="/api/v1/cv/analyze",
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
        
    except (CVAnalysisError, FileProcessingError) as e:
        processing_time = time.time() - start_time
        request_logger.log_error(
            method="POST",
            url="/api/v1/cv/analyze",
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
            url="/api/v1/cv/analyze",
            error=e,
            client_ip=client_ip
        )
        
        logger.error("Unexpected error in CV analysis", error=str(e))
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


@router.post(
    "/optimize",
    response_model=CVOptimizationResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        422: {"model": ErrorResponse, "description": "Validation Error"},
        429: {"model": ErrorResponse, "description": "Rate Limit Exceeded"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
    summary="Optimize CV",
    description="Optimize CV for a specific job and get improvement suggestions"
)
async def optimize_cv(
    request: CVOptimizationRequest,
    request_obj: Depends(check_rate_limit),
    client_ip: str = Depends(get_client_ip)
) -> CVOptimizationResponse:
    """Optimize CV for a specific job."""
    start_time = time.time()
    
    try:
        # Initialize CV analyzer
        cv_analyzer = CVAnalyzer()
        
        # Optimize the CV
        optimization_result = await cv_analyzer.optimize_cv(request)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Log successful request
        request_logger.log_request(
            method="POST",
            url="/api/v1/cv/optimize",
            status_code=200,
            response_time=processing_time,
            client_ip=client_ip,
            cv_id=request.cv_analysis.cv_id
        )
        
        return optimization_result
        
    except ValidationError as e:
        processing_time = time.time() - start_time
        request_logger.log_error(
            method="POST",
            url="/api/v1/cv/optimize",
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
        
    except CVAnalysisError as e:
        processing_time = time.time() - start_time
        request_logger.log_error(
            method="POST",
            url="/api/v1/cv/optimize",
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
            url="/api/v1/cv/optimize",
            error=e,
            client_ip=client_ip
        )
        
        logger.error("Unexpected error in CV optimization", error=str(e))
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
    "/{cv_id}",
    response_model=CVAnalysisResponse,
    responses={
        404: {"model": ErrorResponse, "description": "CV Not Found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
    summary="Get CV Analysis",
    description="Retrieve CV analysis results by CV ID"
)
async def get_cv_analysis(
    cv_id: str,
    client_ip: str = Depends(get_client_ip)
) -> CVAnalysisResponse:
    """Get CV analysis by ID."""
    start_time = time.time()
    
    try:
        # For now, return a mock response
        # In a real implementation, you would fetch from database
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "CV_NOT_FOUND",
                    "message": f"CV analysis with ID {cv_id} not found",
                    "details": {"cv_id": cv_id},
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
            url=f"/api/v1/cv/{cv_id}",
            error=e,
            client_ip=client_ip
        )
        
        logger.error("Unexpected error getting CV analysis", error=str(e))
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
    response_model=List[Dict[str, any]],
    summary="List CV Analyses",
    description="List all CV analyses (paginated)"
)
async def list_cv_analyses(
    skip: int = 0,
    limit: int = 10,
    client_ip: str = Depends(get_client_ip)
) -> List[Dict[str, any]]:
    """List CV analyses."""
    start_time = time.time()
    
    try:
        # For now, return empty list
        # In a real implementation, you would fetch from database
        processing_time = time.time() - start_time
        
        request_logger.log_request(
            method="GET",
            url="/api/v1/cv/",
            status_code=200,
            response_time=processing_time,
            client_ip=client_ip
        )
        
        return []
        
    except Exception as e:
        processing_time = time.time() - start_time
        request_logger.log_error(
            method="GET",
            url="/api/v1/cv/",
            error=e,
            client_ip=client_ip
        )
        
        logger.error("Unexpected error listing CV analyses", error=str(e))
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