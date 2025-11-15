"""Test configuration and fixtures."""

import asyncio
import tempfile
from typing import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_job_description() -> str:
    """Sample job description for testing."""
    return """
    We are looking for a Senior Python Developer to join our team.
    
    Requirements:
    - 3+ years of Python experience
    - Experience with FastAPI, Django, or Flask
    - Knowledge of PostgreSQL, MySQL, or MongoDB
    - Bachelor's degree in Computer Science or related field
    - Strong problem-solving skills
    - Experience with Docker and AWS
    
    Responsibilities:
    - Develop and maintain web applications
    - Collaborate with cross-functional teams
    - Write clean, maintainable code
    - Participate in code reviews
    
    Benefits:
    - Competitive salary: $80,000 - $120,000
    - Remote work option
    - Health insurance
    - Professional development opportunities
    
    Location: San Francisco, CA (Remote OK)
    """


@pytest.fixture
def sample_job_url() -> str:
    """Sample job URL for testing."""
    return "https://example.com/job/123"


@pytest.fixture
def sample_cv_content() -> bytes:
    """Sample CV content for testing."""
    return b"""
    John Doe
    Software Engineer
    john.doe@example.com
    +1-555-123-4567
    
    Experience:
    Software Engineer at Tech Corp (2020-2023)
    - Developed web applications using Python and FastAPI
    - Led team of 5 developers
    - Implemented CI/CD pipelines
    
    Skills:
    - Python, JavaScript, SQL
    - FastAPI, Django, React
    - PostgreSQL, MongoDB
    - Docker, AWS
    - Git, Linux
    
    Education:
    Bachelor's in Computer Science, University of Tech (2019)
    
    Certifications:
    - AWS Certified Developer
    - Python Professional Certification
    """


@pytest.fixture
def sample_discord_webhook_url() -> str:
    """Sample Discord webhook URL for testing."""
    return "https://discord.com/api/webhooks/123456789/abcdef"


@pytest.fixture
def temp_file() -> Generator[str, None, None]:
    """Create temporary file for testing."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp_file:
        tmp_file.write(b"Test content")
        tmp_file.flush()
        yield tmp_file.name


@pytest.fixture
def mock_job_analysis():
    """Mock job analysis data."""
    return {
        "job_id": "test_job_123",
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
        "description": "We are looking for a Senior Python Developer...",
        "url": "https://example.com/job/123",
        "analysis": {
            "sentiment_score": 0.8,
            "culture_fit": "high",
            "growth_potential": "medium"
        },
        "created_at": "2024-12-01T10:00:00Z"
    }


@pytest.fixture
def mock_cv_analysis():
    """Mock CV analysis data."""
    return {
        "cv_id": "test_cv_123",
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


@pytest.fixture
def mock_cv_optimization():
    """Mock CV optimization data."""
    return {
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