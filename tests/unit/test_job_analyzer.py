"""Unit tests for job analyzer service."""

import pytest
from unittest.mock import AsyncMock, patch

from app.models.job import JobAnalysisRequest
from app.services.job_analyzer import JobAnalyzer
from app.core.exceptions import JobAnalysisError, ValidationError


class TestJobAnalyzer:
    """Test cases for JobAnalyzer service."""
    
    @pytest.fixture
    def job_analyzer(self):
        """Create JobAnalyzer instance."""
        return JobAnalyzer()
    
    @pytest.fixture
    def sample_request(self, sample_job_description):
        """Sample job analysis request."""
        return JobAnalysisRequest(job_description=sample_job_description)
    
    @pytest.mark.asyncio
    async def test_analyze_job_with_description(self, job_analyzer, sample_request):
        """Test job analysis with description."""
        result = await job_analyzer.analyze_job(sample_request)
        
        assert result.job_id is not None
        assert result.title is not None
        assert result.description == sample_request.job_description
        assert len(result.requirements.skills) > 0
        assert result.requirements.experience_years is not None
        assert result.analysis is not None
    
    @pytest.mark.asyncio
    async def test_analyze_job_with_url(self, job_analyzer, sample_job_url):
        """Test job analysis with URL."""
        request = JobAnalysisRequest(job_url=sample_job_url)
        
        with patch.object(job_analyzer.web_scraper, 'scrape_job_posting') as mock_scrape:
            mock_scrape.return_value = {
                'title': 'Test Job',
                'company': 'Test Company',
                'description': 'Test job description',
                'url': sample_job_url
            }
            
            result = await job_analyzer.analyze_job(request)
            
            assert result.job_id is not None
            assert result.title == 'Test Job'
            assert result.company == 'Test Company'
            assert result.url == sample_job_url
    
    @pytest.mark.asyncio
    async def test_analyze_job_no_input(self, job_analyzer):
        """Test job analysis with no input."""
        request = JobAnalysisRequest()
        
        with pytest.raises(ValidationError) as exc_info:
            await job_analyzer.analyze_job(request)
        
        assert "Either job_url or job_description must be provided" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_extract_skills(self, job_analyzer):
        """Test skill extraction."""
        text = "We need Python, JavaScript, and PostgreSQL experience"
        skills = job_analyzer.text_processor.extract_skills(text)
        
        assert "Python" in skills
        assert "JavaScript" in skills
        assert "Postgresql" in skills
    
    @pytest.mark.asyncio
    async def test_extract_experience_years(self, job_analyzer):
        """Test experience years extraction."""
        text = "Minimum 3 years of experience required"
        years = job_analyzer.text_processor.extract_experience_years(text)
        
        assert years == 3
    
    @pytest.mark.asyncio
    async def test_extract_education(self, job_analyzer):
        """Test education extraction."""
        text = "Bachelor's degree in Computer Science required"
        education = job_analyzer.text_processor.extract_education(text)
        
        assert "Bachelor's" in education
    
    @pytest.mark.asyncio
    async def test_extract_salary_range(self, job_analyzer):
        """Test salary range extraction."""
        text = "Salary range: $80,000 - $120,000 per year"
        salary = job_analyzer.text_processor.extract_salary_range(text)
        
        assert salary is not None
        assert salary['min'] == 80000
        assert salary['max'] == 120000
        assert salary['currency'] == 'USD'
    
    @pytest.mark.asyncio
    async def test_extract_location(self, job_analyzer):
        """Test location extraction."""
        text = "Location: San Francisco, CA"
        location = job_analyzer.text_processor.extract_location(text)
        
        assert location is not None
        assert "San Francisco" in location
    
    @pytest.mark.asyncio
    async def test_analyze_sentiment(self, job_analyzer):
        """Test sentiment analysis."""
        positive_text = "Great opportunity with excellent benefits"
        negative_text = "Terrible working conditions and low pay"
        
        positive_sentiment = job_analyzer.text_processor.analyze_sentiment(positive_text)
        negative_sentiment = job_analyzer.text_processor.analyze_sentiment(negative_text)
        
        assert positive_sentiment > 0
        assert negative_sentiment < 0
    
    @pytest.mark.asyncio
    async def test_analyze_culture_indicators(self, job_analyzer):
        """Test culture indicators analysis."""
        positive_text = "We value collaboration, teamwork, and diversity"
        negative_text = "Fast-paced environment with tight deadlines"
        
        positive_culture = job_analyzer._analyze_culture_indicators(positive_text)
        negative_culture = job_analyzer._analyze_culture_indicators(negative_text)
        
        assert positive_culture == 'high'
        assert negative_culture == 'low'
    
    @pytest.mark.asyncio
    async def test_analyze_growth_indicators(self, job_analyzer):
        """Test growth indicators analysis."""
        high_growth_text = "Career development, promotion opportunities, mentoring program"
        low_growth_text = "No mention of growth or development"
        
        high_growth = job_analyzer._analyze_growth_indicators(high_growth_text)
        low_growth = job_analyzer._analyze_growth_indicators(low_growth_text)
        
        assert high_growth == 'high'
        assert low_growth == 'low'
    
    @pytest.mark.asyncio
    async def test_calculate_readability(self, job_analyzer):
        """Test readability calculation."""
        simple_text = "This is a simple sentence. It has short words."
        complex_text = "This is a very complex sentence with many long words and complicated structures that make it difficult to read and understand."
        
        simple_readability = job_analyzer._calculate_readability(simple_text)
        complex_readability = job_analyzer._calculate_readability(complex_text)
        
        assert simple_readability > complex_readability
        assert 0 <= simple_readability <= 1
        assert 0 <= complex_readability <= 1