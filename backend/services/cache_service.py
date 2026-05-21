"""
Redis Cache Service for caching search results and API responses
"""
import redis
import json
import logging
from typing import Optional, Any
import hashlib
from app.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Service for Redis caching operations"""
    
    def __init__(self):
        """Initialize Redis cache service"""
        self.enabled = settings.REDIS_ENABLED
        self.ttl = settings.CACHE_TTL
        self.redis_client = None
        
        if self.enabled:
            self._connect()
    
    def _connect(self):
        """Connect to Redis server"""
        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                username=settings.REDIS_USER,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Test connection
            self.redis_client.ping()
            logger.info(f"Successfully connected to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}")
            
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            self.enabled = False
            self.redis_client = None
        except Exception as e:
            logger.error(f"Error initializing Redis: {str(e)}")
            self.enabled = False
            self.redis_client = None
    
    def _generate_key(self, prefix: str, data: str) -> str:
        """
        Generate cache key from prefix and data
        
        Args:
            prefix: Key prefix (e.g., 'search', 'llm')
            data: Data to hash
            
        Returns:
            Cache key
        """
        # Create hash of the data for consistent key generation
        data_hash = hashlib.md5(data.encode()).hexdigest()
        return f"{prefix}:{data_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        if not self.enabled or not self.redis_client:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                logger.debug(f"Cache hit for key: {key}")
                return json.loads(value)
            else:
                logger.debug(f"Cache miss for key: {key}")
                return None
                
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding cached value for key {key}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error getting from cache: {str(e)}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (uses default if not provided)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            ttl = ttl or self.ttl
            serialized = json.dumps(value)
            self.redis_client.setex(key, ttl, serialized)
            logger.debug(f"Cached value for key: {key} (TTL: {ttl}s)")
            return True
            
        except (TypeError, json.JSONEncodeError) as e:
            logger.error(f"Error serializing value for key {key}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error setting cache: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete value from cache
        
        Args:
            key: Cache key
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            self.redis_client.delete(key)
            logger.debug(f"Deleted cache key: {key}")
            return True
        except Exception as e:
            logger.error(f"Error deleting from cache: {str(e)}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching pattern
        
        Args:
            pattern: Key pattern (e.g., 'search:*')
            
        Returns:
            Number of keys deleted
        """
        if not self.enabled or not self.redis_client:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                deleted = self.redis_client.delete(*keys)
                logger.info(f"Cleared {deleted} keys matching pattern: {pattern}")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Error clearing cache pattern: {str(e)}")
            return 0
    
    def get_stats(self) -> dict:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache stats
        """
        if not self.enabled or not self.redis_client:
            return {"enabled": False}
        
        try:
            info = self.redis_client.info()
            return {
                "enabled": True,
                "connected": True,
                "used_memory": info.get("used_memory_human", "N/A"),
                "total_keys": self.redis_client.dbsize(),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0),
                    info.get("keyspace_misses", 0)
                )
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return {"enabled": True, "connected": False, "error": str(e)}
    
    def _calculate_hit_rate(self, hits: int, misses: int) -> float:
        """Calculate cache hit rate percentage"""
        total = hits + misses
        if total == 0:
            return 0.0
        return round((hits / total) * 100, 2)
    
    def health_check(self) -> bool:
        """
        Check if Redis is healthy
        
        Returns:
            True if healthy, False otherwise
        """
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            return self.redis_client.ping()
        except Exception as e:
            logger.error(f"Redis health check failed: {str(e)}")
            return False


# Global instance
cache_service = CacheService()

# Made with Bob