"""Discord integration data models."""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl


class DiscordEmbed(BaseModel):
    """Discord embed model."""
    
    title: Optional[str] = Field(None, description="Embed title")
    description: Optional[str] = Field(None, description="Embed description")
    color: Optional[int] = Field(None, description="Embed color (hex)")
    fields: List[Dict[str, str]] = Field(default_factory=list, description="Embed fields")
    footer: Optional[Dict[str, str]] = Field(None, description="Embed footer")
    timestamp: Optional[str] = Field(None, description="Embed timestamp")


class DiscordMessage(BaseModel):
    """Discord message model."""
    
    content: Optional[str] = Field(None, description="Message content")
    username: Optional[str] = Field(None, description="Bot username")
    avatar_url: Optional[HttpUrl] = Field(None, description="Bot avatar URL")
    embeds: List[DiscordEmbed] = Field(default_factory=list, description="Message embeds")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "content": "Job Analysis Complete! 🎯",
                "username": "Job Hunter Bot",
                "avatar_url": "https://example.com/bot-avatar.png",
                "embeds": [
                    {
                        "title": "Senior Python Developer",
                        "description": "Tech Corp - San Francisco, CA",
                        "color": 0x00ff00,
                        "fields": [
                            {
                                "name": "Required Skills",
                                "value": "Python, FastAPI, PostgreSQL",
                                "inline": True
                            },
                            {
                                "name": "Experience",
                                "value": "3+ years",
                                "inline": True
                            }
                        ],
                        "footer": {
                            "text": "Job Hunter Bot"
                        },
                        "timestamp": "2024-12-01T10:00:00Z"
                    }
                ]
            }
        }


class DiscordWebhookRequest(BaseModel):
    """Discord webhook request model."""
    
    webhook_url: HttpUrl = Field(..., description="Discord webhook URL")
    message: DiscordMessage = Field(..., description="Message to send")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "webhook_url": "https://discord.com/api/webhooks/123456789/abcdef",
                "message": {
                    "content": "Job Analysis Complete! 🎯",
                    "username": "Job Hunter Bot",
                    "embeds": [
                        {
                            "title": "Senior Python Developer",
                            "description": "Tech Corp - San Francisco, CA",
                            "color": 0x00ff00,
                            "fields": [
                                {
                                    "name": "Required Skills",
                                    "value": "Python, FastAPI, PostgreSQL",
                                    "inline": True
                                }
                            ]
                        }
                    ]
                }
            }
        }


class DiscordWebhookResponse(BaseModel):
    """Discord webhook response model."""
    
    success: bool = Field(True, description="Webhook success status")
    message_id: Optional[str] = Field(None, description="Discord message ID")
    response_time: float = Field(..., description="Response time in seconds")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "success": True,
                "message_id": "1234567890123456789",
                "response_time": 0.5
            }
        }