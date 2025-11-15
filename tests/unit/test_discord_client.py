"""Unit tests for Discord client service."""

import pytest
from unittest.mock import AsyncMock, patch

from app.models.discord import DiscordWebhookRequest, DiscordMessage, DiscordEmbed
from app.services.discord_client import DiscordClient
from app.core.exceptions import DiscordWebhookError


class TestDiscordClient:
    """Test cases for DiscordClient service."""
    
    @pytest.fixture
    def discord_client(self):
        """Create DiscordClient instance."""
        return DiscordClient()
    
    @pytest.fixture
    def sample_webhook_request(self, sample_discord_webhook_url):
        """Sample Discord webhook request."""
        message = DiscordMessage(
            content="Test message",
            username="Test Bot"
        )
        return DiscordWebhookRequest(
            webhook_url=sample_discord_webhook_url,
            message=message
        )
    
    @pytest.mark.asyncio
    async def test_send_webhook_success(self, discord_client, sample_webhook_request):
        """Test successful webhook sending."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 204
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            result = await discord_client.send_webhook(sample_webhook_request)
            
            assert result.success is True
            assert result.response_time >= 0
    
    @pytest.mark.asyncio
    async def test_send_webhook_failure(self, discord_client, sample_webhook_request):
        """Test webhook sending failure."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 400
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            with pytest.raises(DiscordWebhookError):
                await discord_client.send_webhook(sample_webhook_request)
    
    @pytest.mark.asyncio
    async def test_send_webhook_timeout(self, discord_client, sample_webhook_request):
        """Test webhook sending timeout."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.side_effect = Exception("Timeout")
            
            with pytest.raises(DiscordWebhookError):
                await discord_client.send_webhook(sample_webhook_request)
    
    @pytest.mark.asyncio
    async def test_send_job_analysis(self, discord_client, sample_discord_webhook_url, mock_job_analysis):
        """Test sending job analysis to Discord."""
        from app.models.job import JobAnalysis
        
        job_analysis = JobAnalysis(**mock_job_analysis)
        
        with patch.object(discord_client, 'send_webhook') as mock_send:
            mock_send.return_value = AsyncMock(success=True)
            
            result = await discord_client.send_job_analysis(sample_discord_webhook_url, job_analysis)
            
            assert result.success is True
            mock_send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_cv_optimization(self, discord_client, sample_discord_webhook_url, mock_cv_optimization):
        """Test sending CV optimization to Discord."""
        from app.models.cv import CVOptimizationResponse
        
        cv_optimization = CVOptimizationResponse(**mock_cv_optimization)
        
        with patch.object(discord_client, 'send_webhook') as mock_send:
            mock_send.return_value = AsyncMock(success=True)
            
            result = await discord_client.send_cv_optimization(sample_discord_webhook_url, cv_optimization)
            
            assert result.success is True
            mock_send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_error_notification(self, discord_client, sample_discord_webhook_url):
        """Test sending error notification to Discord."""
        with patch.object(discord_client, 'send_webhook') as mock_send:
            mock_send.return_value = AsyncMock(success=True)
            
            result = await discord_client.send_error_notification(
                sample_discord_webhook_url,
                "Test error message",
                "TestError"
            )
            
            assert result.success is True
            mock_send.assert_called_once()
    
    def test_create_job_analysis_message(self, discord_client, mock_job_analysis):
        """Test job analysis message creation."""
        from app.models.job import JobAnalysis
        
        job_analysis = JobAnalysis(**mock_job_analysis)
        
        # This would be called internally by send_job_analysis
        # We can test the message structure by checking the webhook call
        with patch.object(discord_client, 'send_webhook') as mock_send:
            discord_client.send_job_analysis("https://discord.com/api/webhooks/123/abc", job_analysis)
            
            # Check that send_webhook was called with proper message structure
            call_args = mock_send.call_args[0][0]
            assert call_args.webhook_url == "https://discord.com/api/webhooks/123/abc"
            assert call_args.message.content is not None
            assert len(call_args.message.embeds) > 0
    
    def test_create_cv_optimization_message(self, discord_client, mock_cv_optimization):
        """Test CV optimization message creation."""
        from app.models.cv import CVOptimizationResponse
        
        cv_optimization = CVOptimizationResponse(**mock_cv_optimization)
        
        with patch.object(discord_client, 'send_webhook') as mock_send:
            discord_client.send_cv_optimization("https://discord.com/api/webhooks/123/abc", cv_optimization)
            
            # Check that send_webhook was called with proper message structure
            call_args = mock_send.call_args[0][0]
            assert call_args.webhook_url == "https://discord.com/api/webhooks/123/abc"
            assert call_args.message.content is not None
            assert len(call_args.message.embeds) > 0
    
    def test_create_error_notification_message(self, discord_client):
        """Test error notification message creation."""
        with patch.object(discord_client, 'send_webhook') as mock_send:
            discord_client.send_error_notification(
                "https://discord.com/api/webhooks/123/abc",
                "Test error",
                "TestError"
            )
            
            # Check that send_webhook was called with proper message structure
            call_args = mock_send.call_args[0][0]
            assert call_args.webhook_url == "https://discord.com/api/webhooks/123/abc"
            assert call_args.message.content is not None
            assert len(call_args.message.embeds) > 0