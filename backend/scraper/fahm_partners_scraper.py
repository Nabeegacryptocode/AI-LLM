"""
FAHM Partners Website Scraper
Scrapes content from fahmpartners.com including services, about pages, and blog posts
"""
import asyncio
import logging
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Page, Browser
import re

from scraper.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class FAHMPartnersScraper(BaseScraper):
    """Scraper for FAHM Partners website"""
    
    def __init__(self):
        super().__init__(
            base_url="https://www.fahmpartners.com",
            source_type="FAHM Partners"
        )
        self.max_pages = 50  # Limit to prevent excessive scraping
        
    async def scrape(self) -> List[Dict[str, any]]:
        """
        Scrape FAHM Partners website
        
        Returns:
            List of document dictionaries
        """
        logger.info("Starting FAHM Partners website scrape")
        documents = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                # Define pages to scrape
                pages_to_scrape = [
                    # Homepage
                    "/",
                    
                    # Core Services
                    "/cybersecurity-solutions",
                    "/enterprise-asset-management",
                    "/supply-chain-solutions",
                    "/environmental-social-governance",
                    "/custom-enterprise-solutions",
                    "/cloud-computing",
                    "/mobile-applications",
                    "/blockchain",
                    "/ui-ux-design",
                    "/data-ai",
                    "/talent-solutions",
                    "/mro-inventory-optimization",
                    "/storage-power-hardware-solutions",
                    
                    # About
                    "/about",
                    "/technology-partners",
                    "/events",
                    "/approach",
                    "/process",
                    
                    # Resources
                    "/blogs",
                    "/careers",
                    "/contact",
                ]
                
                # Scrape each page
                for url_path in pages_to_scrape:
                    if len(documents) >= self.max_pages:
                        logger.info(f"Reached max pages limit ({self.max_pages})")
                        break
                        
                    full_url = urljoin(self.base_url, url_path)
                    
                    if full_url in self.visited_urls:
                        continue
                        
                    logger.info(f"Scraping: {full_url}")
                    
                    try:
                        doc = await self._scrape_page(page, full_url)
                        if doc:
                            documents.append(doc)
                            self.visited_urls.add(full_url)
                            
                        # Small delay to be respectful
                        await asyncio.sleep(1)
                        
                    except Exception as e:
                        logger.error(f"Error scraping {full_url}: {str(e)}")
                        continue
                
                # Try to find and scrape blog posts
                blog_docs = await self._scrape_blog_posts(page)
                documents.extend(blog_docs)
                
            finally:
                await browser.close()
        
        logger.info(f"Scraped {len(documents)} documents from FAHM Partners")
        return documents
    
    async def _scrape_page(self, page: Page, url: str) -> Optional[Dict[str, any]]:
        """
        Scrape a single page
        
        Args:
            page: Playwright page object
            url: URL to scrape
            
        Returns:
            Document dictionary or None
        """
        try:
            # Navigate to page
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            # Wait for content to load
            await page.wait_for_timeout(2000)
            
            # Get page content
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract title
            title = await page.title()
            if not title:
                title_tag = soup.find('h1')
                title = title_tag.get_text(strip=True) if title_tag else urlparse(url).path.strip('/').replace('-', ' ').title()
            
            # Remove script, style, nav, footer elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()
            
            # Extract main content
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main|body'))
            
            if main_content:
                text = main_content.get_text(separator='\n', strip=True)
            else:
                text = soup.get_text(separator='\n', strip=True)
            
            # Clean up text
            text = self._clean_text(text)
            
            # Skip if content is too short
            if len(text) < 100:
                logger.warning(f"Skipping {url} - content too short")
                return None
            
            # Extract metadata
            meta_description = soup.find('meta', attrs={'name': 'description'})
            description = meta_description.get('content', '') if meta_description else ''
            
            # Create document
            doc = {
                'title': title,
                'content': text,
                'url': url,
                'source': 'FAHM Partners',
                'metadata': {
                    'description': description,
                    'url': url,
                    'source': 'fahmpartners.com'
                }
            }
            
            logger.info(f"Scraped: {title} ({len(text)} chars)")
            return doc
            
        except Exception as e:
            logger.error(f"Error scraping page {url}: {str(e)}")
            return None
    
    async def _scrape_blog_posts(self, page: Page) -> List[Dict[str, any]]:
        """
        Scrape blog posts from the blog section
        
        Args:
            page: Playwright page object
            
        Returns:
            List of blog post documents
        """
        documents = []
        blog_url = urljoin(self.base_url, "/blogs")
        
        try:
            logger.info(f"Scraping blog posts from: {blog_url}")
            await page.goto(blog_url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(2000)
            
            # Get all blog post links
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Find blog post links (adjust selectors based on actual site structure)
            blog_links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                # Look for blog post patterns
                if '/blog/' in href or '/post/' in href or (href.startswith('/') and 'blog' in href.lower()):
                    full_url = urljoin(self.base_url, href)
                    if full_url not in self.visited_urls and full_url not in blog_links:
                        blog_links.append(full_url)
            
            # Limit blog posts
            blog_links = blog_links[:10]  # Scrape up to 10 blog posts
            
            logger.info(f"Found {len(blog_links)} blog posts to scrape")
            
            # Scrape each blog post
            for blog_url in blog_links:
                if len(documents) >= 10:
                    break
                    
                try:
                    doc = await self._scrape_page(page, blog_url)
                    if doc:
                        doc['metadata']['type'] = 'blog_post'
                        documents.append(doc)
                        self.visited_urls.add(blog_url)
                        
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error scraping blog post {blog_url}: {str(e)}")
                    continue
            
        except Exception as e:
            logger.error(f"Error scraping blog posts: {str(e)}")
        
        return documents
    
    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        # Remove common navigation/footer text
        lines = text.split('\n')
        cleaned_lines = []
        
        skip_patterns = [
            r'^(home|about|services|contact|careers|blog)$',
            r'^©.*\d{4}',
            r'^all rights reserved',
            r'^privacy policy',
            r'^terms',
        ]
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Skip navigation/footer lines
            skip = False
            for pattern in skip_patterns:
                if re.match(pattern, line.lower()):
                    skip = True
                    break
            
            if not skip:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)


# Made with Bob
