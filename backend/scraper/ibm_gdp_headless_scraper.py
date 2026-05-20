"""
Playwright-based scraper for IBM Guardium Data Protection documentation
"""
from typing import Dict, Any
import logging
from bs4 import BeautifulSoup

from scraper.headless_scraper import HeadlessScraper
from scraper.ibm_gdp_scraper import IBM_GDP_SECTIONS

logger = logging.getLogger(__name__)


class IBMGDPHeadlessScraper(HeadlessScraper):
    """Playwright-based scraper for IBM GDP documentation"""
    
    def __init__(self):
        """Initialize IBM GDP headless scraper"""
        super().__init__(
            base_url="https://www.ibm.com/docs/en/gdp/11.5.0",
            source_type="IBM GDP Docs",
            headless=True,
            timeout=30000,
            wait_for_selector=".body, .content, main, article"
        )
    
    def parse_html(self, html: str, url: str) -> Dict[str, Any]:
        """
        Parse IBM GDP documentation HTML
        
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
        
        # Remove navigation, sidebar, and other UI elements
        for element in soup.find_all(['div'], class_=['navigation', 'sidebar', 'toc', 'breadcrumb-nav', 'page-nav']):
            element.decompose()
        
        # Extract title
        title = self._extract_gdp_title(soup)
        
        # Extract main content
        content = self._extract_gdp_content(soup)
        
        # Extract breadcrumbs for context
        breadcrumbs = self._extract_breadcrumbs(soup)
        
        # Extract links
        links = self._extract_links(soup, url)
        
        return {
            "title": title,
            "content": content,
            "url": url,
            "links": links,
            "source_type": self.source_type,
            "breadcrumbs": breadcrumbs,
            "metadata": {
                "title": title,
                "url": url,
                "source_type": self.source_type,
                "breadcrumbs": " > ".join(breadcrumbs) if breadcrumbs else "",
                "product": "IBM Guardium Data Protection",
                "version": "11.5.0"
            }
        }
    
    def _extract_gdp_title(self, soup: BeautifulSoup) -> str:
        """Extract title from IBM GDP docs"""
        title_selectors = [
            ('h1', {'class': 'title'}),
            ('h1', {'class': 'topictitle1'}),
            ('h1', {}),
            ('title', {})
        ]
        
        for tag, attrs in title_selectors:
            element = soup.find(tag, attrs)
            if element:
                title = element.get_text(strip=True)
                title = title.replace(' - IBM Documentation', '')
                title = title.replace(' | IBM', '')
                return title
        
        return "Untitled"
    
    def _extract_gdp_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from IBM GDP docs"""
        content_selectors = [
            ('div', {'class': 'body'}),
            ('div', {'class': 'section'}),
            ('main', {}),
            ('article', {}),
            ('div', {'class': 'content'}),
            ('div', {'id': 'content'}),
            ('div', {'class': 'main-content'}),
            ('div', {'role': 'main'})
        ]
        
        for tag, attrs in content_selectors:
            main_content = soup.find(tag, attrs)
            if main_content:
                text = main_content.get_text(separator='\n', strip=True)
                text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
                if len(text) > 100:  # Ensure we got meaningful content
                    return text
        
        # Fallback to body
        if soup.body:
            text = soup.body.get_text(separator='\n', strip=True)
            text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
            return text
        
        return ""
    
    def _extract_breadcrumbs(self, soup: BeautifulSoup) -> list:
        """Extract breadcrumb navigation"""
        breadcrumbs = []
        
        breadcrumb_selectors = [
            ('nav', {'aria-label': 'Breadcrumb'}),
            ('ol', {'class': 'breadcrumb'}),
            ('div', {'class': 'breadcrumbs'}),
            ('ul', {'class': 'breadcrumb'})
        ]
        
        for tag, attrs in breadcrumb_selectors:
            breadcrumb_nav = soup.find(tag, attrs)
            if breadcrumb_nav:
                for link in breadcrumb_nav.find_all('a'):
                    text = link.get_text(strip=True)
                    if text:
                        breadcrumbs.append(text)
                break
        
        return breadcrumbs


# Export sections for convenience
__all__ = ['IBMGDPHeadlessScraper', 'IBM_GDP_SECTIONS']

# Made with Bob
