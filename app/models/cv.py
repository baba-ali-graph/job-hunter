"""CV analysis data models."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class CVSection(BaseModel):
    """CV section model."""
    
    name: str = Field(..., description="Section name")
    content: str = Field(..., description="Section content")
    confidence: float = Field(..., description="Extraction confidence score")


class CVSkills(BaseModel):
    """CV skills model."""
    
    technical: List[str] = Field(default_factory=list, description="Technical skills")
    soft: List[str] = Field(default_factory=list, description="Soft skills")
    languages: List[str] = Field(default_factory=list, description="Languages")
    certifications: List[str] = Field(default_factory=list, description="Certifications")


class CVExperience(BaseModel):
    """CV experience model."""
    
    company: str = Field(..., description="Company name")
    position: str = Field(..., description="Job position")
    duration: str = Field(..., description="Employment duration")
    description: str = Field(..., description="Job description")
    achievements: List[str] = Field(default_factory=list, description="Key achievements")


class CVImprovement(BaseModel):
    """CV improvement suggestion model."""
    
    category: str = Field(..., description="Improvement category")
    suggestion: str = Field(..., description="Improvement suggestion")
    priority: str = Field(..., description="Priority level (high/medium/low)")
    impact: str = Field(..., description="Expected impact")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "category": "skills",
                "suggestion": "Add FastAPI experience",
                "priority": "high",
                "impact": "Will increase match score by 15%"
            }
        }


class CVAnalysis(BaseModel):
    """CV analysis model."""
    
    cv_id: str = Field(..., description="Unique CV identifier")
    file_name: str = Field(..., description="Original file name")
    sections: List[CVSection] = Field(default_factory=list, description="Extracted sections")
    skills: CVSkills = Field(default_factory=CVSkills, description="Extracted skills")
    experience: List[CVExperience] = Field(default_factory=list, description="Work experience")
    education: List[str] = Field(default_factory=list, description="Education background")
    contact_info: Dict[str, str] = Field(default_factory=dict, description="Contact information")
    analysis_metadata: Dict[str, Any] = Field(default_factory=dict, description="Analysis metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "cv_id": "cv_123456",
                "file_name": "john_doe_cv.pdf",
                "sections": [
                    {
                        "name": "Experience",
                        "content": "Software Engineer at Tech Corp...",
                        "confidence": 0.95
                    }
                ],
                "skills": {
                    "technical": ["Python", "JavaScript", "SQL"],
                    "soft": ["Leadership", "Communication"],
                    "languages": ["English", "Spanish"],
                    "certifications": ["AWS Certified"]
                },
                "experience": [
                    {
                        "company": "Tech Corp",
                        "position": "Software Engineer",
                        "duration": "2020-2023",
                        "description": "Developed web applications...",
                        "achievements": ["Led team of 5 developers"]
                    }
                ],
                "education": ["Bachelor's in Computer Science"],
                "contact_info": {
                    "email": "john@example.com",
                    "phone": "+1234567890"
                },
                "analysis_metadata": {
                    "total_experience_years": 3,
                    "sections_found": 5
                },
                "created_at": "2024-12-01T10:00:00Z"
            }
        }


class CVAnalysisRequest(BaseModel):
    """CV analysis request model."""
    
    file_name: str = Field(..., description="CV file name")
    file_content: bytes = Field(..., description="CV file content")
    file_type: str = Field(..., description="File type (pdf, docx, doc)")
    
    @validator("file_type")
    def validate_file_type(cls, v):
        """Validate file type."""
        allowed_types = ["pdf", "docx", "doc"]
        if v.lower() not in allowed_types:
            raise ValueError(f"Unsupported file type. Allowed: {allowed_types}")
        return v.lower()


class CVAnalysisResponse(BaseModel):
    """CV analysis response model."""
    
    success: bool = Field(True, description="Analysis success status")
    data: CVAnalysis = Field(..., description="CV analysis results")
    processing_time: float = Field(..., description="Processing time in seconds")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "cv_id": "cv_123456",
                    "file_name": "john_doe_cv.pdf",
                    "sections": [],
                    "skills": {
                        "technical": ["Python", "JavaScript"],
                        "soft": ["Leadership"],
                        "languages": ["English"],
                        "certifications": []
                    },
                    "experience": [],
                    "education": [],
                    "contact_info": {},
                    "analysis_metadata": {},
                    "created_at": "2024-12-01T10:00:00Z"
                },
                "processing_time": 2.5
            }
        }


class CVOptimizationRequest(BaseModel):
    """CV optimization request model."""
    
    cv_analysis: CVAnalysis = Field(..., description="CV analysis results")
    job_requirements: Dict[str, Any] = Field(..., description="Target job requirements")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "cv_analysis": {
                    "cv_id": "cv_123456",
                    "file_name": "john_doe_cv.pdf",
                    "sections": [],
                    "skills": {"technical": ["Python"], "soft": [], "languages": [], "certifications": []},
                    "experience": [],
                    "education": [],
                    "contact_info": {},
                    "analysis_metadata": {},
                    "created_at": "2024-12-01T10:00:00Z"
                },
                "job_requirements": {
                    "skills": ["Python", "FastAPI"],
                    "experience_years": 3
                }
            }
        }


class CVOptimizationResponse(BaseModel):
    """CV optimization response model."""
    
    success: bool = Field(True, description="Optimization success status")
    job_match_score: float = Field(..., description="Job match score (0-1)")
    strengths: List[str] = Field(default_factory=list, description="CV strengths")
    improvements: List[CVImprovement] = Field(default_factory=list, description="Improvement suggestions")
    missing_requirements: List[str] = Field(default_factory=list, description="Missing job requirements")
    processing_time: float = Field(..., description="Processing time in seconds")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "success": True,
                "job_match_score": 0.85,
                "strengths": [
                    "Strong Python experience",
                    "Relevant project portfolio"
                ],
                "improvements": [
                    {
                        "category": "skills",
                        "suggestion": "Add FastAPI experience",
                        "priority": "high",
                        "impact": "Will increase match score by 15%"
                    }
                ],
                "missing_requirements": [
                    "Docker experience",
                    "AWS certification"
                ],
                "processing_time": 1.2
            }
        }