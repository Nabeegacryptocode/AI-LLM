"""
Web Search Service for fallback when documentation doesn't have answers
Supports both Google Cloud Discovery Engine and DuckDuckGo fallback
Includes Redis caching for improved performance
"""
import aiohttp
import logging
from typing import List, Dict, Any, Optional
import json
import subprocess
import os
import hashlib

try:
    from google.auth.transport.requests import Request
    from google.oauth2 import service_account
    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False

from services.cache_service import cache_service

logger = logging.getLogger(__name__)


class WebSearchService:
    """Service for web search fallback with Google Discovery Engine"""
    
    def __init__(
        self,
        project_id: str = "fahmllm",
        location: str = "global",
        collection_id: str = "default_collection",
        engine_id: str = "fahmllm_1779391932485",
        serving_config: str = "default_search",
        service_account_key_path: Optional[str] = None,
        max_extractive_answers: int = 1
    ):
        """
        Initialize web search service
        
        Args:
            project_id: Google Cloud project ID
            location: Discovery Engine location
            collection_id: Collection ID
            engine_id: Engine ID
            serving_config: Serving configuration name
            service_account_key_path: Path to service account JSON key file
        """
        # Google Discovery Engine settings
        self.project_id = project_id
        self.location = location
        self.collection_id = collection_id
        self.engine_id = engine_id
        self.serving_config = serving_config
        self.service_account_key_path = service_account_key_path or os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        self.max_extractive_answers = max_extractive_answers
        
        # Build Discovery Engine API URL
        self.discovery_api_url = (
            f"https://discoveryengine.googleapis.com/v1alpha/"
            f"projects/{project_id}/locations/{location}/"
            f"collections/{collection_id}/engines/{engine_id}/"
            f"servingConfigs/{serving_config}:search"
        )
        
        # DuckDuckGo fallback
        self.duckduckgo_api_url = "https://api.duckduckgo.com/"
        self.timeout = 30
        self.use_discovery_engine = True
        
        # Check authentication availability
        self._check_auth_availability()
    
    def _check_auth_availability(self):
        """Check if any authentication method is available"""
        has_gcloud = self._check_gcloud_available()
        has_service_account = self.service_account_key_path and os.path.exists(self.service_account_key_path)
        
        if not has_gcloud and not has_service_account and not GOOGLE_AUTH_AVAILABLE:
            logger.warning(
                "No Google Cloud authentication available. "
                "Discovery Engine will not work. Install google-auth: pip install google-auth"
            )
            self.use_discovery_engine = False
    
    def _check_gcloud_available(self) -> bool:
        """Check if gcloud CLI is available"""
        try:
            result = subprocess.run(
                ["gcloud", "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    async def _get_access_token(self) -> Optional[str]:
        """
        Get Google Cloud access token using available authentication method
        Tries in order: service account, gcloud CLI
        
        Returns:
            Access token or None if failed
        """
        # Try service account first (for production)
        if self.service_account_key_path and os.path.exists(self.service_account_key_path):
            token = await self._get_service_account_token()
            if token:
                return token
        
        # Fall back to gcloud CLI (for development)
        return await self._get_gcloud_token()
    
    async def _get_service_account_token(self) -> Optional[str]:
        """
        Get access token using service account credentials
        
        Returns:
            Access token or None if failed
        """
        if not GOOGLE_AUTH_AVAILABLE:
            logger.warning("google-auth library not installed")
            return None
        
        # Check if file exists first
        if not self.service_account_key_path:
            logger.debug("No service account key path configured")
            return None
            
        if not os.path.exists(self.service_account_key_path):
            logger.debug(f"Service account key file not found: {self.service_account_key_path}")
            return None
        
        try:
            # Validate JSON file before attempting to load
            with open(self.service_account_key_path, 'r', encoding='utf-8') as f:
                try:
                    json.load(f)
                except json.JSONDecodeError as json_err:
                    logger.error(f"Invalid JSON in service account key file: {json_err}")
                    return None
            
            # Load credentials
            credentials = service_account.Credentials.from_service_account_file(
                self.service_account_key_path,
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
            
            # Refresh the token
            request = Request()
            credentials.refresh(request)
            
            logger.debug("Successfully obtained service account access token")
            return credentials.token
            
        except FileNotFoundError:
            logger.error(f"Service account key file not found: {self.service_account_key_path}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in service account key file at {self.service_account_key_path}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error getting service account token: {str(e)}")
            return None
    
    async def _get_gcloud_token(self) -> Optional[str]:
        """
        Get access token using gcloud CLI
        
        Returns:
            Access token or None if failed
        """
        try:
            result = subprocess.run(
                ["gcloud", "auth", "print-access-token"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                token = result.stdout.strip()
                logger.debug("Successfully obtained gcloud CLI access token")
                return token
            else:
                logger.debug(f"gcloud auth failed: {result.stderr}")
                return None
        except FileNotFoundError:
            logger.debug("gcloud CLI not found")
            return None
        except subprocess.TimeoutExpired:
            logger.warning("gcloud auth timeout")
            return None
        except Exception as e:
            logger.error(f"Error getting gcloud token: {str(e)}")
            return None
    
    async def _search_discovery_engine(
        self,
        query: str,
        page_size: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search using Google Cloud Discovery Engine
        
        Args:
            query: Search query
            page_size: Number of results to return
            
        Returns:
            List of search results
        """
        try:
            # Get access token
            access_token = await self._get_access_token()
            if not access_token:
                logger.info("No access token available, using DuckDuckGo fallback")
                return []
            
            # Prepare request payload
            payload = {
                "query": query,
                "pageSize": page_size,
                "queryExpansionSpec": {
                    "condition": "AUTO"
                },
                "spellCorrectionSpec": {
                    "mode": "AUTO"
                },
                "languageCode": "en-US",
                "contentSearchSpec": {
                    "extractiveContentSpec": {
                        "maxExtractiveAnswerCount": self.max_extractive_answers
                    }
                },
                "userInfo": {
                    "timeZone": "America/New_York"
                }
            }
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            logger.info(f"Searching Discovery Engine for: {query[:100]}...")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.discovery_api_url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = self._parse_discovery_engine_results(data)
                        logger.info(f"Found {len(results)} Discovery Engine results")
                        return results
                    else:
                        error_text = await response.text()
                        logger.warning(
                            f"Discovery Engine search failed with status {response.status}: {error_text}"
                        )
                        return []
                        
        except Exception as e:
            logger.error(f"Error searching Discovery Engine: {str(e)}")
            return []
    
    def _parse_discovery_engine_results(
        self,
        data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Parse Google Discovery Engine API response
        
        Args:
            data: API response data
            
        Returns:
            List of parsed results
        """
        results = []
        
        # Extract results from response
        search_results = data.get('results', [])
        
        for item in search_results:
            document = item.get('document', {})
            struct_data = document.get('structData', {})
            derived_struct_data = document.get('derivedStructData', {})
            
            # Extract relevant fields
            result = {
                'id': document.get('id', ''),
                'title': struct_data.get('title', derived_struct_data.get('title', 'Untitled')),
                'content': struct_data.get('snippet', derived_struct_data.get('snippets', [''])[0] if derived_struct_data.get('snippets') else ''),
                'url': derived_struct_data.get('link', struct_data.get('url', '')),
                'source': 'Google Discovery Engine',
                'score': item.get('relevanceScore', 0.0)
            }
            
            # Add additional metadata if available
            if 'extractive_answers' in derived_struct_data:
                result['extractive_answers'] = derived_struct_data['extractive_answers']
            
            results.append(result)
        
        return results
    
    async def _search_duckduckgo(
        self,
        query: str,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Fallback search using DuckDuckGo
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of search results
        """
        try:
            logger.info(f"Using DuckDuckGo fallback for: {query[:100]}...")
            
            params = {
                'q': query,
                'format': 'json',
                'no_html': 1,
                'skip_disambig': 1
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.duckduckgo_api_url,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = self._parse_duckduckgo_results(data, max_results)
                        logger.info(f"Found {len(results)} DuckDuckGo results")
                        return results
                    else:
                        logger.warning(f"DuckDuckGo search failed with status {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error performing DuckDuckGo search: {str(e)}")
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
                'source': 'DuckDuckGo',
                'score': 1.0
            })
        
        # Get related topics
        related_topics = data.get('RelatedTopics', [])
        for topic in related_topics[:max_results - len(results)]:
            if isinstance(topic, dict) and 'Text' in topic:
                results.append({
                    'title': topic.get('Text', '')[:100],
                    'content': topic.get('Text', ''),
                    'url': topic.get('FirstURL', ''),
                    'source': 'DuckDuckGo',
                    'score': 0.8
                })
        
        return results[:max_results]
    
    async def search(
        self,
        query: str,
        max_results: int = 5,
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search for information using Discovery Engine with DuckDuckGo fallback
        Includes Redis caching for improved performance
        
        Args:
            query: Search query
            max_results: Maximum number of results
            use_cache: Whether to use cache (default: True)
            
        Returns:
            List of search results
        """
        # Generate cache key
        cache_key = self._generate_cache_key(query, max_results)
        
        # Try to get from cache first
        if use_cache:
            cached_results = cache_service.get(cache_key)
            if cached_results:
                logger.info(f"Returning cached results for query: {query[:50]}...")
                return cached_results
        
        results = []
        
        # Try Google Discovery Engine first
        if self.use_discovery_engine:
            results = await self._search_discovery_engine(query, max_results)
        
        # Fallback to DuckDuckGo if no results or Discovery Engine disabled
        if not results:
            logger.info("Falling back to DuckDuckGo search")
            results = await self._search_duckduckgo(query, max_results)
        
        # Cache the results
        if results and use_cache:
            cache_service.set(cache_key, results, ttl=3600)  # Cache for 1 hour
            logger.debug(f"Cached search results for query: {query[:50]}...")
        
        return results
    
    def _generate_cache_key(self, query: str, max_results: int) -> str:
        """
        Generate cache key for search query
        
        Args:
            query: Search query
            max_results: Maximum results
            
        Returns:
            Cache key
        """
        # Create a hash of query and params for consistent caching
        cache_data = f"{query}:{max_results}"
        query_hash = hashlib.md5(cache_data.encode()).hexdigest()
        return f"search:{query_hash}"
    
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
Relevance Score: {result.get('score', 'N/A')}

Content:
{result['content']}

---
""")
        
        return "\n".join(context_parts)
    
    def disable_discovery_engine(self):
        """Disable Discovery Engine and use only DuckDuckGo"""
        self.use_discovery_engine = False
        logger.info("Discovery Engine disabled, using DuckDuckGo only")
    
    def enable_discovery_engine(self):
        """Enable Discovery Engine"""
        self.use_discovery_engine = True
        logger.info("Discovery Engine enabled")


# Global instance
web_search_service = WebSearchService()

# Made with Bob
