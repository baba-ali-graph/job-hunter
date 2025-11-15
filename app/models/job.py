"""Job analysis data models."""

from datetime import datetime
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field, HttpUrl, validator


class SalaryRange(BaseModel):
    """Salary range model."""
    
    min: Optional[int] = Field(None, description="Minimum salary")
    max: Optional[int] = Field(None, description="Maximum salary")
    currency: str = Field("USD", description="Currency code")
    
    @validator("currency")
    def validate_currency(cls, v):
        """Validate currency code."""
        return v.upper()


class JobRequirements(BaseModel):
    """Job requirements model."""
    
    skills: List[str] = Field(default_factory=list, description="Required skills")
    experience_years: Optional[int] = Field(None, description="Required experience in years")
    education: Optional[str] = Field(None, description="Required education level")
    certifications: List[str] = Field(default_factory=list, description="Required certifications")
    languages: List[str] = Field(default_factory=list, description="Required languages")


class JobAnalysis(BaseModel):
    """Job analysis model."""
    
    job_id: str = Field(..., description="Unique job identifier")
    title: str = Field(..., description="Job title")
    company: Optional[str] = Field(None, description="Company name")
    location: Optional[str] = Field(None, description="Job location")
    remote_option: bool = Field(False, description="Remote work option available")
    salary_range: Optional[SalaryRange] = Field(None, description="Salary range")
    requirements: JobRequirements = Field(default_factory=JobRequirements)
    description: str = Field(..., description="Job description")
    url: Optional[HttpUrl] = Field(None, description="Original job posting URL")
    analysis: Dict[str, Union[str, float, int]] = Field(
        default_factory=dict, 
        description="Analysis results (sentiment, culture fit, etc.)"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "job_id": "job_123456",
                "title": "Senior Python Developer",
                "company": "Tech Corp",
                "location": "San Francisco, CA",
                "remote_option": True,
                "salary_range": {
                    "min": 80000,
                    "max": 120000,
                    "currency": "USD"
                },
                "requirements": {
                    "skills": ["Python", "FastAPI", "PostgreSQL"],
                    "experience_years": 3,
                    "education": "Bachelor's Degree",
                    "certifications": [],
                    "languages": ["English"]
                },
                "description": "We are looking for a senior Python developer...",
                "url": "https://example.com/job/123",
                "analysis": {
                    "sentiment_score": 0.8,
                    "culture_fit": "high",
                    "growth_potential": "medium"
                },
                "created_at": "2024-12-01T10:00:00Z"
            }
        }


class JobAnalysisRequest(BaseModel):
    """Job analysis request model."""
    
    job_url: Optional[HttpUrl] = Field(None, description="URL of the job posting")
    job_description: Optional[str] = Field(None, description="Raw job description text")
    
    @validator("job_description")
    def validate_description(cls, v):
        """Validate job description length."""
        if v and len(v) > 50000:
            raise ValueError("Job description too long (max 50,000 characters)")
        return v
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "job_url": "https://example.com/job/123",
                "job_description": "We are looking for a senior Python developer..."
            }
        }


class JobAnalysisResponse(BaseModel):
    """Job analysis response model."""
    
    success: bool = Field(True, description="Analysis success status")
    data: JobAnalysis = Field(..., description="Job analysis results")
    processing_time: float = Field(..., description="Processing time in seconds")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "job_id": "job_123456",
                    "title": "Senior Python Developer",
                    "company": "Tech Corp",
                    "location": "San Francisco, CA",
                    "remote_option": True,
                    "salary_range": {
                        "min": 80000,
                        "max": 120000,
                        "currency": "USD"
                    },
                    "requirements": {
                        "skills": ["Python", "FastAPI", "PostgreSQL"],
                        "experience_years": 3,
                        "education": "Bachelor's Degree",
                        "certifications": [],
                        "languages": ["English"]
                    },
                    "description": "We are looking for a senior Python developer...",
                    "url": "https://example.com/job/123",
                    "analysis": {
                        "sentiment_score": 0.8,
                        "culture_fit": "high",
                        "growth_potential": "medium"
                    },
                    "created_at": "2024-12-01T10:00:00Z"
                },
                "processing_time": 1.5
            }
        }