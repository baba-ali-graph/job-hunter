"""Unit tests for CV analyzer service."""

import pytest
from unittest.mock import patch

from app.models.cv import CVAnalysisRequest, CVOptimizationRequest
from app.services.cv_analyzer import CVAnalyzer
from app.core.exceptions import CVAnalysisError, ValidationError


class TestCVAnalyzer:
    """Test cases for CVAnalyzer service."""
    
    @pytest.fixture
    def cv_analyzer(self):
        """Create CVAnalyzer instance."""
        return CVAnalyzer()
    
    @pytest.fixture
    def sample_cv_request(self, sample_cv_content):
        """Sample CV analysis request."""
        return CVAnalysisRequest(
            file_name="test_cv.pdf",
            file_content=sample_cv_content,
            file_type="pdf"
        )
    
    @pytest.mark.asyncio
    async def test_analyze_cv_success(self, cv_analyzer, sample_cv_request):
        """Test successful CV analysis."""
        result = await cv_analyzer.analyze_cv(sample_cv_request)
        
        assert result.cv_id is not None
        assert result.file_name == "test_cv.pdf"
        assert len(result.sections) > 0
        assert len(result.skills.technical) > 0
        assert len(result.experience) > 0
        assert result.contact_info is not None
    
    @pytest.mark.asyncio
    async def test_analyze_cv_empty_content(self, cv_analyzer):
        """Test CV analysis with empty content."""
        request = CVAnalysisRequest(
            file_name="empty.pdf",
            file_content=b"",
            file_type="pdf"
        )
        
        with pytest.raises(CVAnalysisError) as exc_info:
            await cv_analyzer.analyze_cv(request)
        
        assert "No text content found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_optimize_cv(self, cv_analyzer, mock_cv_analysis, mock_job_analysis):
        """Test CV optimization."""
        cv_analysis = mock_cv_analysis
        job_requirements = mock_job_analysis["requirements"]
        
        request = CVOptimizationRequest(
            cv_analysis=cv_analysis,
            job_requirements=job_requirements
        )
        
        result = await cv_analyzer.optimize_cv(request)
        
        assert result.success is True
        assert 0 <= result.job_match_score <= 1
        assert len(result.strengths) > 0
        assert len(result.improvements) > 0
        assert len(result.missing_requirements) > 0
    
    def test_extract_sections(self, cv_analyzer):
        """Test section extraction."""
        text = """
        Experience:
        Software Engineer at Tech Corp (2020-2023)
        
        Education:
        Bachelor's in Computer Science
        
        Skills:
        Python, JavaScript, SQL
        """
        
        sections = cv_analyzer._extract_sections(text)
        
        assert len(sections) > 0
        section_names = [section.name for section in sections]
        assert "Experience" in section_names
        assert "Education" in section_names
        assert "Skills" in section_names
    
    def test_extract_soft_skills(self, cv_analyzer):
        """Test soft skills extraction."""
        text = "Strong leadership and communication skills, excellent teamwork"
        
        soft_skills = cv_analyzer._extract_soft_skills(text)
        
        assert "Leadership" in soft_skills
        assert "Communication" in soft_skills
        assert "Teamwork" in soft_skills
    
    def test_extract_experience(self, cv_analyzer):
        """Test experience extraction."""
        text = """
        Software Engineer at Tech Corp (2020-2023)
        - Developed web applications
        - Led team of 5 developers
        
        Junior Developer at Startup Inc (2019-2020)
        - Built REST APIs
        - Worked with databases
        """
        
        experience = cv_analyzer._extract_experience(text)
        
        assert len(experience) > 0
        assert experience[0].company == "Tech Corp"
        assert "2020-2023" in experience[0].duration
    
    def test_extract_education(self, cv_analyzer):
        """Test education extraction."""
        text = """
        Education:
        Bachelor's in Computer Science, University of Tech (2019)
        Master's in Software Engineering, Tech Institute (2021)
        """
        
        education = cv_analyzer._extract_education(text)
        
        assert len(education) > 0
        assert "Bachelor" in education[0]
    
    def test_extract_languages(self, cv_analyzer):
        """Test language extraction."""
        text = "Languages: English (native), Spanish (fluent), French (basic)"
        
        languages = cv_analyzer._extract_languages(text)
        
        assert "English" in languages
        assert "Spanish" in languages
        assert "French" in languages
    
    def test_extract_certifications(self, cv_analyzer):
        """Test certification extraction."""
        text = "Certifications: AWS Certified Developer, PMP, Scrum Master"
        
        certifications = cv_analyzer._extract_certifications(text)
        
        assert len(certifications) > 0
        assert "Aws" in certifications or "Certified" in certifications
    
    def test_calculate_total_experience(self, cv_analyzer):
        """Test total experience calculation."""
        experience = [
            type('Experience', (), {'company': 'Company A', 'duration': '2020-2022'})(),
            type('Experience', (), {'company': 'Company B', 'duration': '2018-2020'})()
        ]
        
        total_years = cv_analyzer._calculate_total_experience(experience)
        
        assert total_years > 0
    
    def test_calculate_match_score(self, cv_analyzer, mock_cv_analysis, mock_job_analysis):
        """Test job match score calculation."""
        cv_analysis = mock_cv_analysis
        job_requirements = mock_job_analysis["requirements"]
        
        match_score = cv_analyzer._calculate_match_score(cv_analysis, job_requirements)
        
        assert 0 <= match_score <= 1
    
    def test_identify_strengths(self, cv_analyzer, mock_cv_analysis, mock_job_analysis):
        """Test strength identification."""
        cv_analysis = mock_cv_analysis
        job_requirements = mock_job_analysis["requirements"]
        
        strengths = cv_analyzer._identify_strengths(cv_analysis, job_requirements)
        
        assert len(strengths) > 0
        assert all(isinstance(strength, str) for strength in strengths)
    
    def test_generate_improvements(self, cv_analyzer, mock_cv_analysis, mock_job_analysis):
        """Test improvement generation."""
        cv_analysis = mock_cv_analysis
        job_requirements = mock_job_analysis["requirements"]
        
        improvements = cv_analyzer._generate_improvements(cv_analysis, job_requirements)
        
        assert len(improvements) > 0
        assert all(hasattr(imp, 'category') for imp in improvements)
        assert all(hasattr(imp, 'suggestion') for imp in improvements)
        assert all(hasattr(imp, 'priority') for imp in improvements)
    
    def test_identify_missing_requirements(self, cv_analyzer, mock_cv_analysis, mock_job_analysis):
        """Test missing requirements identification."""
        cv_analysis = mock_cv_analysis
        job_requirements = mock_job_analysis["requirements"]
        
        missing = cv_analyzer._identify_missing_requirements(cv_analysis, job_requirements)
        
        assert isinstance(missing, list)
        assert all(isinstance(req, str) for req in missing)