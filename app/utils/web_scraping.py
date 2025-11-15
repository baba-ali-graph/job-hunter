"""Web scraping utilities."""

import asyncio
from typing import Dict, Optional
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from app.core.exceptions import ExternalServiceError, JobAnalysisError
from app.core.logging import get_logger

logger = get_logger(__name__)


class WebScraper:
    """Web scraping utility class."""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    async def fetch_url(self, url: str) -> str:
        """Fetch content from URL."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                
                logger.info("URL fetched successfully", url=url, status_code=response.status_code)
                return response.text
                
        except httpx.TimeoutException:
            logger.error("Request timeout", url=url)
            raise ExternalServiceError(
                f"Request timeout for URL: {url}",
                service="web_scraper"
            )
        except httpx.HTTPStatusError as e:
            logger.error("HTTP error", url=url, status_code=e.response.status_code)
            raise ExternalServiceError(
                f"HTTP error {e.response.status_code} for URL: {url}",
                service="web_scraper"
            )
        except Exception as e:
            logger.error("Failed to fetch URL", url=url, error=str(e))
            raise ExternalServiceError(
                f"Failed to fetch URL: {str(e)}",
                service="web_scraper"
            )
    
    def extract_job_content(self, html: str, url: str) -> Dict[str, str]:
        """Extract job content from HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Try different selectors for job content
        job_selectors = [
            'div[class*="job"]',
            'div[class*="description"]',
            'div[class*="content"]',
            'section[class*="job"]',
            'article[class*="job"]',
            '.job-description',
            '.job-content',
            '.job-details'
        ]
        
        job_content = ""
        job_title = ""
        company_name = ""
        
        # Extract job title
        title_selectors = [
            'h1[class*="title"]',
            'h1[class*="job"]',
            '.job-title',
            '.position-title',
            'h1'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                job_title = title_elem.get_text().strip()
                break
        
        # Extract company name
        company_selectors = [
            'div[class*="company"]',
            '.company-name',
            '.employer',
            'span[class*="company"]'
        ]
        
        for selector in company_selectors:
            company_elem = soup.select_one(selector)
            if company_elem:
                company_name = company_elem.get_text().strip()
                break
        
        # Extract job description
        for selector in job_selectors:
            elements = soup.select(selector)
            if elements:
                job_content = " ".join([elem.get_text() for elem in elements])
                break
        
        # If no specific selectors work, try to get main content
        if not job_content:
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
            if main_content:
                job_content = main_content.get_text()
        
        # Clean up the text
        job_content = self._clean_text(job_content)
        
        return {
            'title': job_title,
            'company': company_name,
            'description': job_content,
            'url': url
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        import re
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        return text.strip()
    
    def is_valid_job_url(self, url: str) -> bool:
        """Check if URL is likely a job posting."""
        parsed_url = urlparse(url)
        
        # Check domain
        job_domains = [
            'linkedin.com', 'indeed.com', 'glassdoor.com',
            'monster.com', 'ziprecruiter.com', 'dice.com',
            'angel.co', 'stackoverflow.com', 'github.com'
        ]
        
        domain = parsed_url.netloc.lower()
        for job_domain in job_domains:
            if job_domain in domain:
                return True
        
        # Check path for job-related keywords
        path = parsed_url.path.lower()
        job_keywords = ['job', 'career', 'position', 'opening', 'vacancy']
        
        for keyword in job_keywords:
            if keyword in path:
                return True
        
        return False
    
    async def scrape_job_posting(self, url: str) -> Dict[str, str]:
        """Scrape job posting from URL."""
        if not self.is_valid_job_url(url):
            raise JobAnalysisError(
                f"URL does not appear to be a job posting: {url}",
                job_url=url
            )
        
        try:
            html_content = await self.fetch_url(url)
            job_data = self.extract_job_content(html_content, url)
            
            if not job_data['description']:
                raise JobAnalysisError(
                    "No job description found in the provided URL",
                    job_url=url
                )
            
            logger.info("Job posting scraped successfully", url=url)
            return job_data
            
        except Exception as e:
            logger.error("Failed to scrape job posting", url=url, error=str(e))
            raise JobAnalysisError(
                f"Failed to scrape job posting: {str(e)}",
                job_url=url
            )