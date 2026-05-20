"""
Headless browser scraper using Playwright for JavaScript-rendered content
"""
from typing import List, Dict, Any, Optional
import logging
import asyncio
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError

from scraper.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class HeadlessScraper(BaseScraper):
    """Scraper that uses Playwright to handle JavaScript-rendered content"""
    
    def __init__(
        self,
        base_url: str,
        source_type: str,
        headless: bool = True,
        timeout: int = 30000,
        wait_for_selector: str = "body"
    ):
        """
        Initialize headless scraper
        
        Args:
            base_url: Base URL for the documentation
            source_type: Type of source (e.g., "IBM GDP Docs")
            headless: Whether to run browser in headless mode
            timeout: Page load timeout in milliseconds
            wait_for_selector: CSS selector to wait for before extracting content
        """
        super().__init__(base_url=base_url, source_type=source_type)
        self.headless = headless
        self.timeout = timeout
        self.wait_for_selector = wait_for_selector
        self.browser: Optional[Browser] = None
        self.playwright = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize_browser()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close_browser()
    
    async def initialize_browser(self):
        """Initialize Playwright browser"""
        try:
            logger.info("Initializing Playwright browser...")
            self.playwright = await async_playwright().start()
            
            # Launch Chromium browser
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--disable-gpu'
                ]
            )
            
            logger.info("Playwright browser initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Playwright browser: {str(e)}")
            raise
    
    async def close_browser(self):
        """Close Playwright browser"""
        try:
            if self.browser:
                await self.browser.close()
                logger.info("Browser closed")
            
            if self.playwright:
                await self.playwright.stop()
                logger.info("Playwright stopped")
                
        except Exception as e:
            logger.error(f"Error closing browser: {str(e)}")
    
    async def fetch_url(self, url: str) -> str:
        """
        Fetch URL content using Playwright
        
        Args:
            url: URL to fetch
            
        Returns:
            HTML content
        """
        if not self.browser:
            await self.initialize_browser()
        
        page: Optional[Page] = None
        
        try:
            logger.info(f"Fetching with Playwright: {url}")
            
            # Create new page
            page = await self.browser.new_page()
            
            # Set user agent
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            # Navigate to URL
            response = await page.goto(url, timeout=self.timeout, wait_until='networkidle')
            
            if not response or response.status >= 400:
                logger.warning(f"Failed to load {url}: Status {response.status if response else 'None'}")
                return ""
            
            # Wait for content to load
            try:
                await page.wait_for_selector(self.wait_for_selector, timeout=10000)
            except PlaywrightTimeoutError:
                logger.warning(f"Timeout waiting for selector '{self.wait_for_selector}' on {url}")
            
            # Additional wait for dynamic content
            await page.wait_for_timeout(2000)
            
            # Get page content
            html = await page.content()
            
            logger.info(f"Successfully fetched {len(html)} bytes from {url}")
            
            return html
            
        except PlaywrightTimeoutError:
            logger.error(f"Timeout fetching {url}")
            return ""
            
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return ""
            
        finally:
            if page:
                await page.close()
    
    async def scrape_urls(
        self,
        urls: List[str],
        max_depth: int = 1,
        follow_links: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Scrape multiple URLs using Playwright
        
        Args:
            urls: List of URLs to scrape
            max_depth: Maximum depth for link following
            follow_links: Whether to follow links
            
        Returns:
            List of scraped documents
        """
        if not self.browser:
            await self.initialize_browser()
        
        documents = []
        visited = set()
        
        for depth in range(max_depth + 1):
            if depth == 0:
                current_urls = urls
            else:
                if not follow_links:
                    break
                
                # Extract links from previous depth
                current_urls = []
                for doc in documents:
                    for link in doc.get('links', []):
                        if link not in visited and self.is_valid_url(link):
                            current_urls.append(link)
                
                if not current_urls:
                    break
            
            logger.info(f"Scraping depth {depth}: {len(current_urls)} URLs")
            
            for url in current_urls:
                if url in visited:
                    continue
                
                visited.add(url)
                
                try:
                    # Fetch with Playwright
                    html = await self.fetch_url(url)
                    
                    if not html:
                        continue
                    
                    # Parse HTML
                    doc = self.parse_html(html, url)
                    
                    if doc and doc.get('content'):
                        documents.append(doc)
                    
                    # Rate limiting
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error scraping {url}: {str(e)}")
                    continue
        
        logger.info(f"Scraped {len(documents)} documents")
        
        return documents
    
    def parse_html(self, html: str, url: str) -> Dict[str, Any]:
        """
        Parse HTML content - to be overridden by subclasses
        
        Args:
            html: HTML content
            url: Source URL
            
        Returns:
            Parsed document
        """
        # Default implementation - subclasses should override
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe']):
            element.decompose()
        
        # Extract title
        title = "Untitled"
        if soup.title:
            title = soup.title.get_text(strip=True)
        elif soup.h1:
            title = soup.h1.get_text(strip=True)
        
        # Extract content
        content = ""
        if soup.body:
            content = soup.body.get_text(separator='\n', strip=True)
            content = '\n'.join(line.strip() for line in content.split('\n') if line.strip())
        
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
                "source_type": self.source_type
            }
        }


# Made with Bob
