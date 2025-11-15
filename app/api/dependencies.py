"""API dependencies."""

from typing import Generator

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer

from app.core.config import settings
from app.core.exceptions import RateLimitError
from app.core.logging import get_logger
from app.utils.rate_limiter import RateLimiter

logger = get_logger(__name__)
security = HTTPBearer(auto_error=False)


def get_rate_limiter() -> RateLimiter:
    """Get rate limiter instance."""
    return RateLimiter(
        max_requests=settings.rate_limit_requests,
        window_seconds=settings.rate_limit_window
    )


async def check_rate_limit(
    request: Request,
    rate_limiter: RateLimiter = Depends(get_rate_limiter)
) -> None:
    """Check rate limit for request."""
    client_ip = request.client.host if request.client else "unknown"
    
    try:
        await rate_limiter.check_rate_limit(client_ip)
    except RateLimitError as e:
        logger.warning("Rate limit exceeded", client_ip=client_ip)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": {
                    "code": "RATE_LIMIT_ERROR",
                    "message": str(e),
                    "retry_after": e.details.get("retry_after")
                }
            }
        )


async def get_current_user(token: str = Depends(security)) -> dict:
    """Get current user from token (placeholder for future auth)."""
    # For now, return a placeholder user
    # In a real implementation, you would validate the JWT token here
    if not token:
        return {"user_id": "anonymous", "username": "anonymous"}
    
    return {"user_id": "user_123", "username": "test_user"}


def get_client_ip(request: Request) -> str:
    """Get client IP address."""
    # Check for forwarded headers first
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    # Check for real IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fall back to client IP
    return request.client.host if request.client else "unknown"