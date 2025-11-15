"""Discord integration API endpoints."""

import time
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import check_rate_limit, get_client_ip
from app.core.exceptions import DiscordWebhookError, ValidationError
from app.core.logging import get_logger, RequestLogger
from app.models.common import ErrorResponse
from app.models.discord import DiscordWebhookRequest, DiscordWebhookResponse
from app.services.discord_client import DiscordClient

logger = get_logger(__name__)
request_logger = RequestLogger()
router = APIRouter()


@router.post(
    "/webhook",
    response_model=DiscordWebhookResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        422: {"model": ErrorResponse, "description": "Validation Error"},
        429: {"model": ErrorResponse, "description": "Rate Limit Exceeded"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
    summary="Send Discord Webhook",
    description="Send a message to Discord webhook"
)
async def send_discord_webhook(
    request: DiscordWebhookRequest,
    _: None = Depends(check_rate_limit),
    client_ip: str = Depends(get_client_ip)
) -> DiscordWebhookResponse:
    """Send message to Discord webhook."""
    start_time = time.time()
    
    try:
        # Initialize Discord client
        discord_client = DiscordClient()
        
        # Send webhook
        response = await discord_client.send_webhook(request)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Log successful request
        request_logger.log_request(
            method="POST",
            url="/api/v1/discord/webhook",
            status_code=200,
            response_time=processing_time,
            client_ip=client_ip,
            webhook_url=str(request.webhook_url)
        )
        
        return response
        
    except ValidationError as e:
        processing_time = time.time() - start_time
        request_logger.log_error(
            method="POST",
            url="/api/v1/discord/webhook",
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
        
    except DiscordWebhookError as e:
        processing_time = time.time() - start_time
        request_logger.log_error(
            method="POST",
            url="/api/v1/discord/webhook",
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
            url="/api/v1/discord/webhook",
            error=e,
            client_ip=client_ip
        )
        
        logger.error("Unexpected error sending Discord webhook", error=str(e))
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
    "/job-analysis",
    response_model=DiscordWebhookResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        422: {"model": ErrorResponse, "description": "Validation Error"},
        429: {"model": ErrorResponse, "description": "Rate Limit Exceeded"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
    summary="Send Job Analysis to Discord",
    description="Send job analysis results to Discord webhook"
)
async def send_job_analysis_to_discord(
    webhook_url: str,
    job_analysis_data: Dict[str, Any],
    _: None = Depends(check_rate_limit),
    client_ip: str = Depends(get_client_ip)
) -> DiscordWebhookResponse:
    """Send job analysis results to Discord."""
    start_time = time.time()
    
    try:
        # Validate webhook URL
        if not webhook_url.startswith("https://discord.com/api/webhooks/"):
            raise ValidationError("Invalid Discord webhook URL")
        
        # Initialize Discord client
        discord_client = DiscordClient()
        
        # Create job analysis object from data
        from app.models.job import JobAnalysis
        job_analysis = JobAnalysis(**job_analysis_data)
        
        # Send job analysis to Discord
        response = await discord_client.send_job_analysis(webhook_url, job_analysis)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Log successful request
        request_logger.log_request(
            method="POST",
            url="/api/v1/discord/job-analysis",
            status_code=200,
            response_time=processing_time,
            client_ip=client_ip,
            webhook_url=webhook_url
        )
        
        return response
        
    except ValidationError as e:
        processing_time = time.time() - start_time
        request_logger.log_error(
            method="POST",
            url="/api/v1/discord/job-analysis",
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
        
    except DiscordWebhookError as e:
        processing_time = time.time() - start_time
        request_logger.log_error(
            method="POST",
            url="/api/v1/discord/job-analysis",
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
            url="/api/v1/discord/job-analysis",
            error=e,
            client_ip=client_ip
        )
        
        logger.error("Unexpected error sending job analysis to Discord", error=str(e))
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
    "/cv-optimization",
    response_model=DiscordWebhookResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        422: {"model": ErrorResponse, "description": "Validation Error"},
        429: {"model": ErrorResponse, "description": "Rate Limit Exceeded"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
    summary="Send CV Optimization to Discord",
    description="Send CV optimization results to Discord webhook"
)
async def send_cv_optimization_to_discord(
    webhook_url: str,
    cv_optimization_data: Dict[str, Any],
    _: None = Depends(check_rate_limit),
    client_ip: str = Depends(get_client_ip)
) -> DiscordWebhookResponse:
    """Send CV optimization results to Discord."""
    start_time = time.time()
    
    try:
        # Validate webhook URL
        if not webhook_url.startswith("https://discord.com/api/webhooks/"):
            raise ValidationError("Invalid Discord webhook URL")
        
        # Initialize Discord client
        discord_client = DiscordClient()
        
        # Create CV optimization response object from data
        from app.models.cv import CVOptimizationResponse
        cv_optimization = CVOptimizationResponse(**cv_optimization_data)
        
        # Send CV optimization to Discord
        response = await discord_client.send_cv_optimization(webhook_url, cv_optimization)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Log successful request
        request_logger.log_request(
            method="POST",
            url="/api/v1/discord/cv-optimization",
            status_code=200,
            response_time=processing_time,
            client_ip=client_ip,
            webhook_url=webhook_url
        )
        
        return response
        
    except ValidationError as e:
        processing_time = time.time() - start_time
        request_logger.log_error(
            method="POST",
            url="/api/v1/discord/cv-optimization",
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
        
    except DiscordWebhookError as e:
        processing_time = time.time() - start_time
        request_logger.log_error(
            method="POST",
            url="/api/v1/discord/cv-optimization",
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
            url="/api/v1/discord/cv-optimization",
            error=e,
            client_ip=client_ip
        )
        
        logger.error("Unexpected error sending CV optimization to Discord", error=str(e))
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