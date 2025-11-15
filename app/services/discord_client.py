"""Discord webhook client service."""

import asyncio
from typing import Optional

import httpx

from app.core.exceptions import DiscordWebhookError
from app.core.logging import get_logger
from app.models.discord import DiscordWebhookRequest, DiscordWebhookResponse
from app.models.job import JobAnalysis
from app.models.cv import CVAnalysis, CVOptimizationResponse

logger = get_logger(__name__)


class DiscordClient:
    """Discord webhook client."""
    
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = 1  # Initial delay in seconds
    
    async def send_webhook(self, request: DiscordWebhookRequest) -> DiscordWebhookResponse:
        """Send message to Discord webhook."""
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        str(request.webhook_url),
                        json=request.message.dict(),
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    if response.status_code == 204:
                        logger.info("Discord webhook sent successfully", attempt=attempt + 1)
                        return DiscordWebhookResponse(
                            success=True,
                            message_id=None,  # Discord doesn't return message ID for webhooks
                            response_time=0.0  # TODO: Implement actual timing
                        )
                    else:
                        logger.warning(
                            "Discord webhook returned non-204 status",
                            status_code=response.status_code,
                            attempt=attempt + 1
                        )
                        
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(self.retry_delay * (2 ** attempt))
                            continue
                        else:
                            raise DiscordWebhookError(
                                f"Discord webhook failed with status {response.status_code}",
                                webhook_url=str(request.webhook_url)
                            )
                            
            except httpx.TimeoutException:
                logger.warning("Discord webhook timeout", attempt=attempt + 1)
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                    continue
                else:
                    raise DiscordWebhookError(
                        "Discord webhook timeout after all retries",
                        webhook_url=str(request.webhook_url)
                    )
                    
            except Exception as e:
                logger.error("Discord webhook error", error=str(e), attempt=attempt + 1)
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                    continue
                else:
                    raise DiscordWebhookError(
                        f"Discord webhook failed: {str(e)}",
                        webhook_url=str(request.webhook_url)
                    )
        
        # This should never be reached, but just in case
        raise DiscordWebhookError(
            "Discord webhook failed after all retries",
            webhook_url=str(request.webhook_url)
        )
    
    async def send_job_analysis(self, webhook_url: str, job_analysis: JobAnalysis) -> DiscordWebhookResponse:
        """Send job analysis results to Discord."""
        from app.models.discord import DiscordMessage, DiscordEmbed
        
        # Create Discord message
        message = DiscordMessage(
            content="🎯 **Job Analysis Complete!**",
            username="Job Hunter Bot",
            embeds=[
                DiscordEmbed(
                    title=f"📋 {job_analysis.title}",
                    description=f"**Company:** {job_analysis.company or 'Unknown'}\n"
                               f"**Location:** {job_analysis.location or 'Not specified'}\n"
                               f"**Remote:** {'✅ Yes' if job_analysis.remote_option else '❌ No'}",
                    color=0x00ff00,  # Green
                    fields=[
                        {
                            "name": "🔧 Required Skills",
                            "value": ", ".join(job_analysis.requirements.skills[:5]) or "Not specified",
                            "inline": True
                        },
                        {
                            "name": "📅 Experience",
                            "value": f"{job_analysis.requirements.experience_years or 'Not'} years",
                            "inline": True
                        },
                        {
                            "name": "🎓 Education",
                            "value": job_analysis.requirements.education or "Not specified",
                            "inline": True
                        }
                    ],
                    footer={
                        "text": "Job Hunter Bot"
                    }
                )
            ]
        )
        
        # Add salary information if available
        if job_analysis.salary_range:
            salary_text = f"${job_analysis.salary_range.min:,} - ${job_analysis.salary_range.max:,}"
            message.embeds[0].fields.append({
                "name": "💰 Salary Range",
                "value": salary_text,
                "inline": True
            })
        
        # Add analysis insights
        if job_analysis.analysis:
            sentiment = job_analysis.analysis.get('sentiment_score', 0)
            sentiment_emoji = "😊" if sentiment > 0.1 else "😐" if sentiment > -0.1 else "😞"
            
            message.embeds[0].fields.append({
                "name": "📊 Analysis",
                "value": f"{sentiment_emoji} Sentiment: {sentiment:.2f}\n"
                        f"🎯 Culture Fit: {job_analysis.analysis.get('culture_fit', 'Unknown')}\n"
                        f"📈 Growth Potential: {job_analysis.analysis.get('growth_potential', 'Unknown')}",
                "inline": False
            })
        
        # Create webhook request
        webhook_request = DiscordWebhookRequest(
            webhook_url=webhook_url,
            message=message
        )
        
        return await self.send_webhook(webhook_request)
    
    async def send_cv_optimization(self, webhook_url: str, cv_optimization: CVOptimizationResponse) -> DiscordWebhookResponse:
        """Send CV optimization results to Discord."""
        from app.models.discord import DiscordMessage, DiscordEmbed
        
        # Create Discord message
        message = DiscordMessage(
            content="📝 **CV Optimization Complete!**",
            username="Job Hunter Bot",
            embeds=[
                DiscordEmbed(
                    title="🎯 CV Analysis Results",
                    description=f"**Job Match Score:** {cv_optimization.job_match_score:.1%}",
                    color=0x00ff00 if cv_optimization.job_match_score > 0.7 else 0xffaa00 if cv_optimization.job_match_score > 0.4 else 0xff0000,
                    fields=[
                        {
                            "name": "✅ Strengths",
                            "value": "\n".join([f"• {strength}" for strength in cv_optimization.strengths[:3]]) or "None identified",
                            "inline": False
                        }
                    ],
                    footer={
                        "text": "Job Hunter Bot"
                    }
                )
            ]
        )
        
        # Add improvement suggestions
        if cv_optimization.improvements:
            improvements_text = "\n".join([
                f"• **{imp.category.title()}:** {imp.suggestion} ({imp.priority} priority)"
                for imp in cv_optimization.improvements[:3]
            ])
            message.embeds[0].fields.append({
                "name": "💡 Improvement Suggestions",
                "value": improvements_text,
                "inline": False
            })
        
        # Add missing requirements
        if cv_optimization.missing_requirements:
            missing_text = "\n".join([f"• {req}" for req in cv_optimization.missing_requirements[:5]])
            message.embeds[0].fields.append({
                "name": "❌ Missing Requirements",
                "value": missing_text,
                "inline": False
            })
        
        # Create webhook request
        webhook_request = DiscordWebhookRequest(
            webhook_url=webhook_url,
            message=message
        )
        
        return await self.send_webhook(webhook_request)
    
    async def send_error_notification(self, webhook_url: str, error_message: str, error_type: str) -> DiscordWebhookResponse:
        """Send error notification to Discord."""
        from app.models.discord import DiscordMessage, DiscordEmbed
        
        message = DiscordMessage(
            content="⚠️ **Error Notification**",
            username="Job Hunter Bot",
            embeds=[
                DiscordEmbed(
                    title="🚨 Service Error",
                    description=f"**Error Type:** {error_type}\n**Message:** {error_message}",
                    color=0xff0000,  # Red
                    footer={
                        "text": "Job Hunter Bot - Error Alert"
                    }
                )
            ]
        )
        
        webhook_request = DiscordWebhookRequest(
            webhook_url=webhook_url,
            message=message
        )
        
        return await self.send_webhook(webhook_request)