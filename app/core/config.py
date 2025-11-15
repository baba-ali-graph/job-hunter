"""Application configuration settings."""

import os
from typing import List, Optional

from pydantic import BaseModel, validator


class Settings(BaseModel):
    """Application settings."""
    
    # Application
    app_name: str = "Job Hunter Bot"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # API Configuration
    api_v1_prefix: str = "/api/v1"
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    
    # Rate Limiting
    rate_limit_requests: int = 10
    rate_limit_window: int = 60  # seconds
    
    # File Upload
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: List[str] = ["pdf", "docx", "doc"]
    
    # External Services
    discord_webhook_timeout: int = 30
    discord_retry_attempts: int = 3
    discord_retry_delay: int = 1
    
    # Job Analysis
    job_analysis_timeout: int = 30
    max_job_description_length: int = 50000
    
    # CV Analysis
    cv_analysis_timeout: int = 60
    supported_languages: List[str] = ["en", "es", "fr", "de"]
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Database (for future use)
    database_url: Optional[str] = None
    
    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 9090
    
    @validator("debug", pre=True)
    def validate_debug(cls, v):
        """Validate debug setting."""
        return str(v).lower() in ("true", "1", "yes", "on")
    
    @validator("allowed_file_types", pre=True)
    def validate_file_types(cls, v):
        """Validate allowed file types."""
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",")]
        return v
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


# Global settings instance
settings = Settings()