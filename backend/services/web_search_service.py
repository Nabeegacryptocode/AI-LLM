"""
Web Search Service for fallback when documentation doesn't have answers
"""
import aiohttp
import logging
from typing import List, Dict, Any, Optional
import json

logger = logging.getLogger(__name__)


class WebSearchService:
    """Service for web search fallback"""
    
    def __init__(self):
        """Initialize web search service"""
        self.search_api_url = "https://api.duckduckgo.com/"
        self.timeout = 10
    
    async def search(
        self,
        query: str,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search the web for information
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of search results
        """
        try:
            logger.info(f"Performing web search for: {query[:100]}...")
            
            # Use DuckDuckGo Instant Answer API (no API key required)
            params = {
                'q': query,
                'format': 'json',
                'no_html': 1,
                'skip_disambig': 1
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.search_api_url,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = self._parse_duckduckgo_results(data, max_results)
                        logger.info(f"Found {len(results)} web search results")
                        return results
                    else:
                        logger.warning(f"Web search failed with status {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error performing web search: {str(e)}")
            return []
    
    def _parse_duckduckgo_results(
        self,
        data: Dict[str, Any],
        max_results: int
    ) -> List[Dict[str, Any]]:
        """
        Parse DuckDuckGo API response
        
        Args:
            data: API response data
            max_results: Maximum results to return
            
        Returns:
            List of parsed results
        """
        results = []
        
        # Get abstract (main answer)
        if data.get('Abstract'):
            results.append({
                'title': data.get('Heading', 'Web Search Result'),
                'content': data.get('Abstract', ''),
                'url': data.get('AbstractURL', ''),
                'source': data.get('AbstractSource', 'Web Search')
            })
        
        # Get related topics
        related_topics = data.get('RelatedTopics', [])
        for topic in related_topics[:max_results - len(results)]:
            if isinstance(topic, dict) and 'Text' in topic:
                results.append({
                    'title': topic.get('Text', '')[:100],
                    'content': topic.get('Text', ''),
                    'url': topic.get('FirstURL', ''),
                    'source': 'Web Search'
                })
        
        return results[:max_results]
    
    async def search_and_summarize(
        self,
        query: str,
        max_results: int = 3
    ) -> str:
        """
        Search web and create a summary context
        
        Args:
            query: Search query
            max_results: Maximum results to include
            
        Returns:
            Formatted context string
        """
        results = await self.search(query, max_results)
        
        if not results:
            return ""
        
        context_parts = ["Web Search Results:\n"]
        
        for i, result in enumerate(results, 1):
            context_parts.append(f"""
Result {i}: {result['title']}
Source: {result['source']}
URL: {result['url']}

Content:
{result['content']}

---
""")
        
        return "\n".join(context_parts)


# Global instance
web_search_service = WebSearchService()

# Made with Bob
