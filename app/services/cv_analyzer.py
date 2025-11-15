"""CV analysis service."""

import uuid
from datetime import datetime
from typing import Dict, List, Optional

from app.core.exceptions import CVAnalysisError, ValidationError
from app.core.logging import get_logger
from app.models.cv import (
    CVAnalysis, CVAnalysisRequest, CVOptimizationRequest, 
    CVOptimizationResponse, CVSection, CVSkills, CVExperience, CVImprovement
)
from app.utils.file_processing import FileProcessor
from app.utils.text_processing import TextProcessor

logger = get_logger(__name__)


class CVAnalyzer:
    """CV analysis service."""
    
    def __init__(self):
        self.file_processor = FileProcessor()
        self.text_processor = TextProcessor()
    
    async def analyze_cv(self, request: CVAnalysisRequest) -> CVAnalysis:
        """Analyze a CV file."""
        try:
            # Validate file size
            self.file_processor.validate_file_size(
                request.file_content, 
                10 * 1024 * 1024  # 10MB
            )
            
            # Extract text from file
            text_content = self.file_processor.extract_text(
                request.file_content, 
                request.file_type
            )
            
            if not text_content:
                raise CVAnalysisError("No text content found in CV file")
            
            # Generate CV ID
            cv_id = str(uuid.uuid4())
            
            # Analyze the CV content
            analysis_results = await self._analyze_cv_content(text_content)
            
            # Create CV analysis object
            cv_analysis = CVAnalysis(
                cv_id=cv_id,
                file_name=request.file_name,
                sections=analysis_results.get('sections', []),
                skills=CVSkills(
                    technical=analysis_results.get('technical_skills', []),
                    soft=analysis_results.get('soft_skills', []),
                    languages=analysis_results.get('languages', []),
                    certifications=analysis_results.get('certifications', [])
                ),
                experience=analysis_results.get('experience', []),
                education=analysis_results.get('education', []),
                contact_info=analysis_results.get('contact_info', {}),
                analysis_metadata=analysis_results.get('metadata', {}),
                created_at=datetime.utcnow()
            )
            
            logger.info("CV analysis completed", cv_id=cv_id, file_name=request.file_name)
            return cv_analysis
            
        except Exception as e:
            logger.error("CV analysis failed", error=str(e))
            if isinstance(e, (CVAnalysisError, ValidationError)):
                raise
            else:
                raise CVAnalysisError(f"CV analysis failed: {str(e)}")
    
    async def optimize_cv(self, request: CVOptimizationRequest) -> CVOptimizationResponse:
        """Optimize CV for a specific job."""
        try:
            cv_analysis = request.cv_analysis
            job_requirements = request.job_requirements
            
            # Calculate job match score
            match_score = self._calculate_match_score(cv_analysis, job_requirements)
            
            # Identify strengths
            strengths = self._identify_strengths(cv_analysis, job_requirements)
            
            # Generate improvement suggestions
            improvements = self._generate_improvements(cv_analysis, job_requirements)
            
            # Identify missing requirements
            missing_requirements = self._identify_missing_requirements(cv_analysis, job_requirements)
            
            return CVOptimizationResponse(
                success=True,
                job_match_score=match_score,
                strengths=strengths,
                improvements=improvements,
                missing_requirements=missing_requirements,
                processing_time=0.0  # TODO: Implement actual timing
            )
            
        except Exception as e:
            logger.error("CV optimization failed", error=str(e))
            raise CVAnalysisError(f"CV optimization failed: {str(e)}")
    
    async def _analyze_cv_content(self, text_content: str) -> Dict[str, any]:
        """Analyze CV content and extract information."""
        # Clean the text
        clean_text = self.text_processor.clean_text(text_content)
        
        # Extract sections
        sections = self._extract_sections(clean_text)
        
        # Extract skills
        technical_skills = self.text_processor.extract_skills(clean_text)
        soft_skills = self._extract_soft_skills(clean_text)
        
        # Extract experience
        experience = self._extract_experience(clean_text)
        
        # Extract education
        education = self._extract_education(clean_text)
        
        # Extract contact info
        contact_info = self.text_processor.extract_contact_info(clean_text)
        
        # Extract languages and certifications
        languages = self._extract_languages(clean_text)
        certifications = self._extract_certifications(clean_text)
        
        # Calculate metadata
        metadata = {
            'total_experience_years': self._calculate_total_experience(experience),
            'sections_found': len(sections),
            'skills_count': len(technical_skills) + len(soft_skills),
            'word_count': len(clean_text.split()),
            'readability_score': self.text_processor._calculate_readability(clean_text)
        }
        
        return {
            'sections': sections,
            'technical_skills': technical_skills,
            'soft_skills': soft_skills,
            'experience': experience,
            'education': education,
            'contact_info': contact_info,
            'languages': languages,
            'certifications': certifications,
            'metadata': metadata
        }
    
    def _extract_sections(self, text: str) -> List[CVSection]:
        """Extract CV sections."""
        import re
        
        sections = []
        section_patterns = {
            'Experience': r'(?:experience|work\s+history|employment)',
            'Education': r'(?:education|academic|qualifications)',
            'Skills': r'(?:skills|technical\s+skills|competencies)',
            'Projects': r'(?:projects|portfolio|work\s+samples)',
            'Certifications': r'(?:certifications|certificates|licenses)',
            'Languages': r'(?:languages|language\s+skills)',
            'Summary': r'(?:summary|profile|objective|about)'
        }
        
        for section_name, pattern in section_patterns.items():
            match = re.search(pattern, text.lower())
            if match:
                # Extract content after the section header
                start_pos = match.end()
                next_section = None
                
                # Find the next section
                for other_pattern in section_patterns.values():
                    if other_pattern != pattern:
                        next_match = re.search(other_pattern, text[start_pos:].lower())
                        if next_match:
                            if next_section is None or next_match.start() < next_section:
                                next_section = next_match.start()
                
                if next_section:
                    section_content = text[start_pos:start_pos + next_section].strip()
                else:
                    section_content = text[start_pos:].strip()
                
                if section_content:
                    sections.append(CVSection(
                        name=section_name,
                        content=section_content,
                        confidence=0.8  # TODO: Implement confidence calculation
                    ))
        
        return sections
    
    def _extract_soft_skills(self, text: str) -> List[str]:
        """Extract soft skills from CV."""
        soft_skills = [
            'leadership', 'communication', 'teamwork', 'problem solving',
            'time management', 'adaptability', 'creativity', 'critical thinking',
            'emotional intelligence', 'negotiation', 'presentation',
            'project management', 'mentoring', 'collaboration'
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in soft_skills:
            if skill in text_lower:
                found_skills.append(skill.title())
        
        return found_skills
    
    def _extract_experience(self, text: str) -> List[CVExperience]:
        """Extract work experience from CV."""
        import re
        
        experience = []
        
        # Look for experience patterns
        exp_patterns = [
            r'(\w+)\s+(\d{4})\s*-\s*(\d{4}|\w+)\s+(.+)',
            r'(\w+)\s+(\d{4})\s*-\s*present\s+(.+)',
            r'(\w+)\s+(\d{4})\s*-\s*current\s+(.+)'
        ]
        
        for pattern in exp_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) >= 3:
                    company = match.group(1)
                    start_year = match.group(2)
                    end_year = match.group(3) if len(match.groups()) > 3 else "Present"
                    description = match.group(-1)
                    
                    experience.append(CVExperience(
                        company=company,
                        position="",  # TODO: Extract position
                        duration=f"{start_year} - {end_year}",
                        description=description,
                        achievements=[]  # TODO: Extract achievements
                    ))
        
        return experience
    
    def _extract_education(self, text: str) -> List[str]:
        """Extract education information."""
        import re
        
        education = []
        edu_patterns = [
            r'(bachelor|master|phd|doctorate|associate|diploma|certificate)',
            r'(university|college|institute|school)',
            r'(\d{4})\s*-\s*(\d{4})\s*(.+)'
        ]
        
        # Simple extraction - look for degree keywords
        text_lower = text.lower()
        degree_keywords = ['bachelor', 'master', 'phd', 'doctorate', 'associate', 'diploma']
        
        for keyword in degree_keywords:
            if keyword in text_lower:
                education.append(keyword.title())
        
        return education
    
    def _extract_languages(self, text: str) -> List[str]:
        """Extract languages from CV."""
        languages = [
            'english', 'spanish', 'french', 'german', 'italian', 'portuguese',
            'chinese', 'japanese', 'korean', 'arabic', 'russian', 'hindi'
        ]
        
        found_languages = []
        text_lower = text.lower()
        
        for language in languages:
            if language in text_lower:
                found_languages.append(language.title())
        
        return found_languages
    
    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications from CV."""
        certifications = []
        
        # Look for certification patterns
        cert_patterns = [
            r'(aws|certified|certification|certificate|license)',
            r'(pmp|scrum|agile|itil|cisco|microsoft)'
        ]
        
        text_lower = text.lower()
        for pattern in cert_patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                certifications.append(match.group(1).title())
        
        return certifications
    
    def _calculate_total_experience(self, experience: List[CVExperience]) -> int:
        """Calculate total years of experience."""
        # Simplified calculation
        return len(experience) * 2  # Assume 2 years per position
    
    def _calculate_match_score(self, cv_analysis: CVAnalysis, job_requirements: Dict[str, any]) -> float:
        """Calculate job match score."""
        required_skills = job_requirements.get('skills', [])
        required_experience = job_requirements.get('experience_years', 0)
        
        cv_skills = cv_analysis.skills.technical + cv_analysis.skills.soft
        cv_experience = cv_analysis.analysis_metadata.get('total_experience_years', 0)
        
        # Calculate skill match
        skill_matches = sum(1 for skill in required_skills if skill.lower() in [s.lower() for s in cv_skills])
        skill_score = skill_matches / len(required_skills) if required_skills else 0
        
        # Calculate experience match
        exp_score = min(cv_experience / required_experience, 1.0) if required_experience > 0 else 1.0
        
        # Combined score
        return (skill_score * 0.7 + exp_score * 0.3)
    
    def _identify_strengths(self, cv_analysis: CVAnalysis, job_requirements: Dict[str, any]) -> List[str]:
        """Identify CV strengths."""
        strengths = []
        
        required_skills = job_requirements.get('skills', [])
        cv_skills = cv_analysis.skills.technical + cv_analysis.skills.soft
        
        # Check for matching skills
        matching_skills = [skill for skill in required_skills if skill.lower() in [s.lower() for s in cv_skills]]
        if matching_skills:
            strengths.append(f"Strong experience with {', '.join(matching_skills[:3])}")
        
        # Check experience level
        cv_experience = cv_analysis.analysis_metadata.get('total_experience_years', 0)
        required_experience = job_requirements.get('experience_years', 0)
        
        if cv_experience >= required_experience:
            strengths.append(f"Meets experience requirements ({cv_experience} years)")
        
        # Check for relevant projects/achievements
        if cv_analysis.sections:
            strengths.append("Comprehensive project portfolio")
        
        return strengths
    
    def _generate_improvements(self, cv_analysis: CVAnalysis, job_requirements: Dict[str, any]) -> List[CVImprovement]:
        """Generate improvement suggestions."""
        improvements = []
        
        required_skills = job_requirements.get('skills', [])
        cv_skills = cv_analysis.skills.technical + cv_analysis.skills.soft
        
        # Check for missing skills
        missing_skills = [skill for skill in required_skills if skill.lower() not in [s.lower() for s in cv_skills]]
        
        for skill in missing_skills[:3]:  # Top 3 missing skills
            improvements.append(CVImprovement(
                category="skills",
                suggestion=f"Add {skill} experience",
                priority="high",
                impact="Will increase match score by 15%"
            ))
        
        # Check experience level
        cv_experience = cv_analysis.analysis_metadata.get('total_experience_years', 0)
        required_experience = job_requirements.get('experience_years', 0)
        
        if cv_experience < required_experience:
            improvements.append(CVImprovement(
                category="experience",
                suggestion="Highlight relevant experience and achievements",
                priority="medium",
                impact="Will improve experience match"
            ))
        
        return improvements
    
    def _identify_missing_requirements(self, cv_analysis: CVAnalysis, job_requirements: Dict[str, any]) -> List[str]:
        """Identify missing job requirements."""
        missing = []
        
        required_skills = job_requirements.get('skills', [])
        cv_skills = cv_analysis.skills.technical + cv_analysis.skills.soft
        
        for skill in required_skills:
            if skill.lower() not in [s.lower() for s in cv_skills]:
                missing.append(skill)
        
        return missing