"""Text processing utilities."""

import re
from typing import Dict, List, Optional, Tuple

import nltk
from textblob import TextBlob

from app.core.logging import get_logger

logger = get_logger(__name__)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')


class TextProcessor:
    """Text processing utility class."""
    
    def __init__(self):
        self.stop_words = set(nltk.corpus.stopwords.words('english'))
        self.skill_keywords = {
            'programming': ['python', 'javascript', 'java', 'c++', 'c#', 'go', 'rust', 'php', 'ruby'],
            'frameworks': ['django', 'flask', 'fastapi', 'react', 'angular', 'vue', 'spring', 'express'],
            'databases': ['postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'sqlite'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform'],
            'tools': ['git', 'jenkins', 'ci/cd', 'linux', 'bash', 'powershell']
        }
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        return text.strip()
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract technical skills from text."""
        text_lower = text.lower()
        found_skills = []
        
        for category, skills in self.skill_keywords.items():
            for skill in skills:
                if skill in text_lower:
                    found_skills.append(skill.title())
        
        # Remove duplicates and return
        return list(set(found_skills))
    
    def extract_experience_years(self, text: str) -> Optional[int]:
        """Extract required experience years from text."""
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'(\d+)\+?\s*years?\s*(?:in\s*)?(?:the\s*)?field',
            r'minimum\s*(?:of\s*)?(\d+)\s*years?',
            r'at\s*least\s*(\d+)\s*years?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return int(match.group(1))
        
        return None
    
    def extract_education(self, text: str) -> Optional[str]:
        """Extract education requirements from text."""
        education_patterns = [
            r'bachelor\'?s?\s*(?:degree|in)',
            r'master\'?s?\s*(?:degree|in)',
            r'phd\s*(?:in|degree)',
            r'associate\'?s?\s*(?:degree|in)',
            r'high\s*school\s*diploma'
        ]
        
        for pattern in education_patterns:
            match = re.search(pattern, text.lower())
            if match:
                return match.group(0).title()
        
        return None
    
    def extract_salary_range(self, text: str) -> Optional[Dict[str, any]]:
        """Extract salary range from text."""
        # Look for salary patterns
        salary_patterns = [
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*-\s*\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*-\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:per\s*year|annually)',
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*to\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:per\s*year|annually)'
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, text.lower())
            if match:
                min_salary = int(match.group(1).replace(',', ''))
                max_salary = int(match.group(2).replace(',', ''))
                return {
                    'min': min_salary,
                    'max': max_salary,
                    'currency': 'USD'
                }
        
        return None
    
    def extract_location(self, text: str) -> Optional[str]:
        """Extract job location from text."""
        # Look for location patterns
        location_patterns = [
            r'(?:location|based\s*in|office\s*in):\s*([^,\n]+)',
            r'(?:remote|work\s*from\s*home)',
            r'(?:hybrid|flexible\s*work)'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text.lower())
            if match:
                if 'remote' in match.group(0) or 'work from home' in match.group(0):
                    return 'Remote'
                elif 'hybrid' in match.group(0) or 'flexible' in match.group(0):
                    return 'Hybrid'
                else:
                    return match.group(1).strip()
        
        return None
    
    def analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment of text."""
        blob = TextBlob(text)
        return blob.sentiment.polarity
    
    def extract_key_phrases(self, text: str, max_phrases: int = 10) -> List[str]:
        """Extract key phrases from text."""
        blob = TextBlob(text)
        phrases = blob.noun_phrases
        
        # Filter out common phrases and sort by frequency
        filtered_phrases = []
        for phrase in phrases:
            if len(phrase.split()) >= 2 and phrase not in self.stop_words:
                filtered_phrases.append(phrase)
        
        return filtered_phrases[:max_phrases]
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts."""
        # Simple word-based similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        if len(union) == 0:
            return 0.0
        
        return len(intersection) / len(union)
    
    def extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information from text."""
        contact_info = {}
        
        # Email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact_info['email'] = email_match.group(0)
        
        # Phone
        phone_pattern = r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            contact_info['phone'] = phone_match.group(0)
        
        return contact_info