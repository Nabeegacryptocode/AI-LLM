"""
Playwright-based scraper for IBM MaaS360 product pages
"""
from typing import Dict, Any
import logging
from bs4 import BeautifulSoup

from scraper.headless_scraper import HeadlessScraper

logger = logging.getLogger(__name__)


class IBMMaaS360HeadlessScraper(HeadlessScraper):
    """Playwright-based scraper for IBM MaaS360"""
    
    def __init__(self):
        """Initialize IBM MaaS360 headless scraper"""
        super().__init__(
            base_url="https://www.ibm.com/products/maas360",
            source_type="IBM MaaS360",
            headless=True,
            timeout=30000,
            wait_for_selector="main, article, .content, body"
        )
    
    def parse_html(self, html: str, url: str) -> Dict[str, Any]:
        """
        Parse IBM MaaS360 HTML
        
        Args:
            html: HTML content
            url: Source URL
            
        Returns:
            Parsed document
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe']):
            element.decompose()
        
        # Remove navigation and UI elements
        for element in soup.find_all(['div'], class_=['navigation', 'sidebar', 'toc', 'breadcrumb-nav', 'page-nav', 'cookie-banner']):
            element.decompose()
        
        # Extract title
        title = self._extract_title(soup)
        
        # Extract main content
        content = self._extract_content(soup)
        
        # Extract links
        links = self._extract_links(soup, url)
        
        return {
            "title": title,
            "content": content,
            "url": url,
            "links": links,
            "source_type": self.source_type,
            "metadata": {
                "title": title,
                "url": url,
                "source_type": self.source_type,
                "product": "IBM MaaS360",
                "category": self._extract_category(url)
            }
        }
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract title from page"""
        title_selectors = [
            ('h1', {}),
            ('h2', {'class': 'title'}),
            ('title', {})
        ]
        
        for tag, attrs in title_selectors:
            element = soup.find(tag, attrs)
            if element:
                title = element.get_text(strip=True)
                title = title.replace(' | IBM', '')
                title = title.replace(' - IBM', '')
                if title and len(title) > 3:
                    return title
        
        return "IBM MaaS360"
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from page"""
        content_selectors = [
            ('main', {}),
            ('article', {}),
            ('div', {'class': 'content'}),
            ('div', {'id': 'content'}),
            ('div', {'class': 'main-content'}),
            ('div', {'role': 'main'}),
            ('section', {})
        ]
        
        for tag, attrs in content_selectors:
            main_content = soup.find(tag, attrs)
            if main_content:
                text = main_content.get_text(separator='\n', strip=True)
                text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
                if len(text) > 100:
                    return text
        
        # Fallback to body
        if soup.body:
            text = soup.body.get_text(separator='\n', strip=True)
            text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
            return text
        
        return ""
    
    def _extract_category(self, url: str) -> str:
        """Extract category from URL"""
        if '/features' in url:
            return 'Features'
        elif '/pricing' in url:
            return 'Pricing'
        elif '/resources' in url:
            return 'Resources'
        elif '/support' in url:
            return 'Support'
        else:
            return 'Overview'


# Made with Bob
