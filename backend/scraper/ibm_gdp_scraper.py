"""
Scraper for IBM Guardium Data Protection (GDP) documentation
"""
from typing import List, Dict, Any
import logging
from bs4 import BeautifulSoup

from scraper.base_scraper import BaseScraper
from scraper.document_processor import DocumentProcessor

logger = logging.getLogger(__name__)


class IBMGDPScraper(BaseScraper):
    """Scraper for IBM Guardium Data Protection documentation"""
    
    def __init__(self):
        """Initialize IBM GDP scraper"""
        super().__init__(
            base_url="https://www.ibm.com/docs/en/gdp/11.5.0",
            source_type="IBM GDP Docs"
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
                return text
        
        if soup.body:
            text = soup.body.get_text(separator='\n', strip=True)
            text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
            return text
        
        return ""
    
    def _extract_breadcrumbs(self, soup: BeautifulSoup) -> List[str]:
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
    
    async def scrape_section(
        self,
        section_url: str,
        max_pages: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Scrape a section of IBM GDP documentation
        
        Args:
            section_url: Starting URL for the section
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of scraped documents
        """
        logger.info(f"Scraping IBM GDP section: {section_url}")
        
        documents = await self.scrape_urls(
            urls=[section_url],
            max_depth=2,
            follow_links=True
        )
        
        documents = documents[:max_pages]
        
        logger.info(f"Scraped {len(documents)} pages from IBM GDP")
        
        return documents
    
    def process_documents(
        self,
        documents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Process scraped documents into chunks
        
        Args:
            documents: List of scraped documents
            
        Returns:
            List of processed document chunks
        """
        all_chunks = []
        
        valid_documents = [doc for doc in documents if doc.get('content', '').strip()]
        
        if len(valid_documents) < len(documents):
            logger.warning(f"Filtered out {len(documents) - len(valid_documents)} documents with empty content")
        
        for doc in valid_documents:
            chunks = DocumentProcessor.create_chunks_with_metadata(
                document={
                    'content': doc['content'],
                    'metadata': doc['metadata']
                }
            )
            
            all_chunks.extend(chunks)
        
        logger.info(f"Created {len(all_chunks)} chunks from {len(valid_documents)} documents")
        
        return all_chunks


# Predefined IBM GDP documentation sections
IBM_GDP_SECTIONS = {
    "overview": "https://www.ibm.com/docs/en/gdp/11.5.0?topic=guardium-overview",
    "installation": "https://www.ibm.com/docs/en/gdp/11.5.0?topic=guardium-installing",
    "configuration": "https://www.ibm.com/docs/en/gdp/11.5.0?topic=guardium-configuring",
    "administration": "https://www.ibm.com/docs/en/gdp/11.5.0?topic=guardium-administering",
    "monitoring": "https://www.ibm.com/docs/en/gdp/11.5.0?topic=guardium-monitoring",
    "policies": "https://www.ibm.com/docs/en/gdp/11.5.0?topic=guardium-policies",
    "reports": "https://www.ibm.com/docs/en/gdp/11.5.0?topic=guardium-reports",
    "troubleshooting": "https://www.ibm.com/docs/en/gdp/11.5.0?topic=guardium-troubleshooting",
    "api": "https://www.ibm.com/docs/en/gdp/11.5.0?topic=guardium-api",
    "security": "https://www.ibm.com/docs/en/gdp/11.5.0?topic=guardium-security"
}

# Made with Bob
