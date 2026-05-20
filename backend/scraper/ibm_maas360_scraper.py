"""
Scraper for IBM MaaS360 product pages
"""
from typing import List, Dict, Any
import logging
from bs4 import BeautifulSoup

from scraper.base_scraper import BaseScraper
from scraper.document_processor import DocumentProcessor

logger = logging.getLogger(__name__)


class IBMMaaS360Scraper(BaseScraper):
    """Scraper for IBM MaaS360 product information"""
    
    def __init__(self):
        """Initialize IBM MaaS360 scraper"""
        super().__init__(
            base_url="https://www.ibm.com/products/maas360",
            source_type="IBM MaaS360"
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
                "product": "IBM MaaS360"
            }
        }
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract title"""
        title_selectors = [
            ('h1', {}),
            ('title', {})
        ]
        
        for tag, attrs in title_selectors:
            element = soup.find(tag, attrs)
            if element:
                title = element.get_text(strip=True)
                title = title.replace(' | IBM', '')
                return title
        
        return "IBM MaaS360"
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main content"""
        content_selectors = [
            ('main', {}),
            ('article', {}),
            ('div', {'class': 'content'}),
            ('div', {'id': 'content'}),
            ('div', {'role': 'main'})
        ]
        
        for tag, attrs in content_selectors:
            main_content = soup.find(tag, attrs)
            if main_content:
                text = main_content.get_text(separator='\n', strip=True)
                text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
                if len(text) > 100:
                    return text
        
        if soup.body:
            text = soup.body.get_text(separator='\n', strip=True)
            text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
            return text
        
        return ""
    
    async def scrape_product_pages(
        self,
        max_pages: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Scrape IBM MaaS360 product pages
        
        Args:
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of scraped documents
        """
        logger.info(f"Scraping IBM MaaS360 product pages")
        
        documents = await self.scrape_urls(
            urls=[self.base_url],
            max_depth=2,
            follow_links=True
        )
        
        documents = documents[:max_pages]
        
        logger.info(f"Scraped {len(documents)} pages from IBM MaaS360")
        
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


# Made with Bob
