"""Job analysis service."""

import uuid
from datetime import datetime
from typing import Dict, List, Optional

from app.core.exceptions import JobAnalysisError, ValidationError
from app.core.logging import get_logger
from app.models.job import JobAnalysis, JobAnalysisRequest, SalaryRange, JobRequirements
from app.utils.text_processing import TextProcessor
from app.utils.web_scraping import WebScraper

logger = get_logger(__name__)


class JobAnalyzer:
    """Job analysis service."""
    
    def __init__(self):
        self.text_processor = TextProcessor()
        self.web_scraper = WebScraper()
    
    async def analyze_job(self, request: JobAnalysisRequest) -> JobAnalysis:
        """Analyze a job posting."""
        try:
            # Get job content
            if request.job_url:
                job_data = await self.web_scraper.scrape_job_posting(str(request.job_url))
                job_description = job_data['description']
                job_title = job_data['title']
                company_name = job_data['company']
                job_url = request.job_url
            elif request.job_description:
                job_description = request.job_description
                job_title = self._extract_title_from_description(job_description)
                company_name = None
                job_url = None
            else:
                raise ValidationError("Either job_url or job_description must be provided")
            
            # Generate job ID
            job_id = str(uuid.uuid4())
            
            # Analyze the job description
            analysis_results = await self._analyze_job_description(job_description)
            
            # Create job analysis object
            job_analysis = JobAnalysis(
                job_id=job_id,
                title=job_title or "Unknown Position",
                company=company_name,
                location=analysis_results.get('location'),
                remote_option=analysis_results.get('remote_option', False),
                salary_range=analysis_results.get('salary_range'),
                requirements=JobRequirements(
                    skills=analysis_results.get('skills', []),
                    experience_years=analysis_results.get('experience_years'),
                    education=analysis_results.get('education'),
                    certifications=analysis_results.get('certifications', []),
                    languages=analysis_results.get('languages', [])
                ),
                description=job_description,
                url=job_url,
                analysis=analysis_results.get('analysis', {}),
                created_at=datetime.utcnow()
            )
            
            logger.info("Job analysis completed", job_id=job_id, title=job_title)
            return job_analysis
            
        except Exception as e:
            logger.error("Job analysis failed", error=str(e))
            if isinstance(e, (JobAnalysisError, ValidationError)):
                raise
            else:
                raise JobAnalysisError(f"Job analysis failed: {str(e)}")
    
    async def _analyze_job_description(self, description: str) -> Dict[str, any]:
        """Analyze job description text."""
        # Clean the text
        clean_text = self.text_processor.clean_text(description)
        
        # Extract various components
        skills = self.text_processor.extract_skills(clean_text)
        experience_years = self.text_processor.extract_experience_years(clean_text)
        education = self.text_processor.extract_education(clean_text)
        salary_range = self.text_processor.extract_salary_range(clean_text)
        location = self.text_processor.extract_location(clean_text)
        
        # Analyze sentiment and other metrics
        sentiment_score = self.text_processor.analyze_sentiment(clean_text)
        key_phrases = self.text_processor.extract_key_phrases(clean_text)
        
        # Determine remote option
        remote_option = any(keyword in clean_text.lower() for keyword in [
            'remote', 'work from home', 'wfh', 'telecommute', 'virtual'
        ])
        
        # Analyze culture and growth indicators
        culture_indicators = self._analyze_culture_indicators(clean_text)
        growth_indicators = self._analyze_growth_indicators(clean_text)
        
        return {
            'skills': skills,
            'experience_years': experience_years,
            'education': education,
            'salary_range': salary_range,
            'location': location,
            'remote_option': remote_option,
            'certifications': [],  # TODO: Implement certification extraction
            'languages': [],  # TODO: Implement language extraction
            'analysis': {
                'sentiment_score': sentiment_score,
                'culture_fit': culture_indicators,
                'growth_potential': growth_indicators,
                'key_phrases': key_phrases[:5],  # Top 5 phrases
                'word_count': len(clean_text.split()),
                'readability_score': self._calculate_readability(clean_text)
            }
        }
    
    def _extract_title_from_description(self, description: str) -> Optional[str]:
        """Extract job title from description."""
        # Look for common title patterns
        import re
        
        title_patterns = [
            r'position:\s*([^\n]+)',
            r'role:\s*([^\n]+)',
            r'we\s+are\s+looking\s+for\s+a\s+([^\n]+)',
            r'seeking\s+a\s+([^\n]+)',
            r'hiring\s+a\s+([^\n]+)'
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, description.lower())
            if match:
                return match.group(1).strip().title()
        
        return None
    
    def _analyze_culture_indicators(self, text: str) -> str:
        """Analyze culture indicators in job description."""
        positive_indicators = [
            'collaborative', 'teamwork', 'diverse', 'inclusive', 'flexible',
            'work-life balance', 'growth', 'learning', 'innovation', 'creative'
        ]
        
        negative_indicators = [
            'fast-paced', 'high-pressure', 'demanding', 'overtime', 'weekend',
            'on-call', 'tight deadlines', 'stressful'
        ]
        
        text_lower = text.lower()
        positive_count = sum(1 for indicator in positive_indicators if indicator in text_lower)
        negative_count = sum(1 for indicator in negative_indicators if indicator in text_lower)
        
        if positive_count > negative_count:
            return 'high'
        elif positive_count == negative_count:
            return 'medium'
        else:
            return 'low'
    
    def _analyze_growth_indicators(self, text: str) -> str:
        """Analyze growth potential indicators."""
        growth_indicators = [
            'career development', 'promotion', 'advancement', 'leadership',
            'mentoring', 'training', 'certification', 'skill development',
            'growth opportunity', 'career path'
        ]
        
        text_lower = text.lower()
        growth_count = sum(1 for indicator in growth_indicators if indicator in text_lower)
        
        if growth_count >= 3:
            return 'high'
        elif growth_count >= 1:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_readability(self, text: str) -> float:
        """Calculate readability score (simplified)."""
        # Simple readability based on average sentence length
        sentences = text.split('.')
        if not sentences:
            return 0.0
        
        total_words = len(text.split())
        avg_sentence_length = total_words / len(sentences)
        
        # Normalize to 0-1 scale (simplified)
        if avg_sentence_length <= 10:
            return 1.0
        elif avg_sentence_length <= 20:
            return 0.7
        elif avg_sentence_length <= 30:
            return 0.4
        else:
            return 0.1