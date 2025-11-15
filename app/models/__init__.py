"""Data models for the Job Hunter Bot."""

from .job import JobAnalysis, JobAnalysisRequest, JobAnalysisResponse
from .cv import CVAnalysis, CVAnalysisRequest, CVAnalysisResponse, CVOptimizationRequest
from .discord import DiscordMessage, DiscordWebhookRequest
from .common import ErrorResponse, HealthResponse, MetricsResponse

__all__ = [
    "JobAnalysis",
    "JobAnalysisRequest", 
    "JobAnalysisResponse",
    "CVAnalysis",
    "CVAnalysisRequest",
    "CVAnalysisResponse",
    "CVOptimizationRequest",
    "DiscordMessage",
    "DiscordWebhookRequest",
    "ErrorResponse",
    "HealthResponse",
    "MetricsResponse",
]