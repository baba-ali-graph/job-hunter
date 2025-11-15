"""Custom exceptions for the Job Hunter Bot."""

from typing import Any, Dict, Optional


class JobHunterException(Exception):
    """Base exception for Job Hunter Bot."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(JobHunterException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details={"field": field, **kwargs}
        )


class JobAnalysisError(JobHunterException):
    """Raised when job analysis fails."""
    
    def __init__(self, message: str, job_url: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="JOB_ANALYSIS_ERROR",
            details={"job_url": job_url, **kwargs}
        )


class CVAnalysisError(JobHunterException):
    """Raised when CV analysis fails."""
    
    def __init__(self, message: str, file_name: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="CV_ANALYSIS_ERROR",
            details={"file_name": file_name, **kwargs}
        )


class DiscordWebhookError(JobHunterException):
    """Raised when Discord webhook fails."""
    
    def __init__(self, message: str, webhook_url: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="DISCORD_WEBHOOK_ERROR",
            details={"webhook_url": webhook_url, **kwargs}
        )


class FileProcessingError(JobHunterException):
    """Raised when file processing fails."""
    
    def __init__(self, message: str, file_type: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="FILE_PROCESSING_ERROR",
            details={"file_type": file_type, **kwargs}
        )


class RateLimitError(JobHunterException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str, retry_after: Optional[int] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_ERROR",
            details={"retry_after": retry_after, **kwargs}
        )


class ExternalServiceError(JobHunterException):
    """Raised when external service fails."""
    
    def __init__(self, message: str, service: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            details={"service": service, **kwargs}
        )