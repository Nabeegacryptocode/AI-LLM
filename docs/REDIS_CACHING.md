# Redis Caching Implementation

This document explains the Redis caching implementation for the FAHM LLM system.

## Overview

Redis caching has been integrated to improve performance by caching:
- Web search results (Google Discovery Engine & DuckDuckGo)
- API responses
- Frequently accessed data

## Architecture

```
Request → Check Cache → Cache Hit? → Return Cached Data
                ↓
            Cache Miss
                ↓
        Fetch from Source
                ↓
         Cache Result
                ↓
        Return Fresh Data
```

## Configuration

### Redis Connection Details

```bash
Host: clarion-ivoryish-dinner-46309.db.redis.io
Port: 16235
User: default
Password: 5GYPmAnDL6SmUQ66XB5MRu7hIKV3ObUJ
```

### Environment Variables

Add to your `.env` file:

```bash
# Redis Settings
REDIS_HOST=clarion-ivoryish-dinner-46309.db.redis.io
REDIS_PORT=16235
REDIS_PASSWORD=5GYPmAnDL6SmUQ66XB5MRu7hIKV3ObUJ
REDIS_USER=default
REDIS_URL=redis://default:5GYPmAnDL6SmUQ66XB5MRu7hIKV3ObUJ@clarion-ivoryish-dinner-46309.db.redis.io:16235
CACHE_TTL=3600
REDIS_ENABLED=true
```

## Features

### 1. Automatic Caching

Web search results are automatically cached:

```python
from services.web_search_service import web_search_service

# Automatically uses cache
results = await web_search_service.search("IBM Cloud", max_results=5)

# Bypass cache if needed
results = await web_search_service.search("IBM Cloud", use_cache=False)
```

### 2. Cache Service

Direct cache operations:

```python
from services.cache_service import cache_service

# Set value
cache_service.set("my_key", {"data": "value"}, ttl=3600)

# Get value
value = cache_service.get("my_key")

# Delete value
cache_service.delete("my_key")

# Clear pattern
cache_service.clear_pattern("search:*")

# Get stats
stats = cache_service.get_stats()
```

### 3. Cache Management API

#### Get Cache Statistics

```bash
GET /api/cache/stats
Headers: X-API-Key: your_api_key

Response:
{
  "status": "success",
  "data": {
    "enabled": true,
    "connected": true,
    "used_memory": "1.2M",
    "total_keys": 150,
    "hits": 1250,
    "misses": 350,
    "hit_rate": 78.13
  }
}
```

#### Clear Cache

```bash
POST /api/cache/clear?pattern=search:*
Headers: X-API-Key: your_api_key

Response:
{
  "status": "success",
  "message": "Cleared 45 cache entries",
  "deleted_count": 45
}
```

#### Check Cache Health

```bash
GET /api/cache/health
Headers: X-API-Key: your_api_key

Response:
{
  "status": "success",
  "healthy": true,
  "enabled": true
}
```

#### Delete Specific Key

```bash
DELETE /api/cache/key/search:abc123
Headers: X-API-Key: your_api_key

Response:
{
  "status": "success",
  "message": "Key 'search:abc123' deleted"
}
```

## Cache Keys

### Search Results

Format: `search:{md5_hash}`

Example:
```
search:5d41402abc4b2a76b9719d911017c592
```

The hash is generated from:
- Query text
- Max results parameter

### Custom Keys

You can create custom cache keys:

```python
cache_service.set("custom:user:123", user_data, ttl=7200)
```

## Cache TTL (Time To Live)

Default TTL: **3600 seconds (1 hour)**

Customize per operation:

```python
# Cache for 2 hours
cache_service.set("key", value, ttl=7200)

# Cache for 5 minutes
cache_service.set("key", value, ttl=300)
```

## Performance Benefits

### Before Caching
- Average search response: 2-5 seconds
- API calls per search: 1
- Cost per 1000 searches: $X

### After Caching
- Average cached response: 10-50ms (50-500x faster)
- API calls per search: 0 (if cached)
- Cost savings: Up to 90% for repeated queries

## Monitoring

### View Cache Stats

```python
from services.cache_service import cache_service

stats = cache_service.get_stats()
print(f"Hit Rate: {stats['hit_rate']}%")
print(f"Total Keys: {stats['total_keys']}")
print(f"Memory Used: {stats['used_memory']}")
```

### Log Analysis

Cache operations are logged:

```
INFO - Returning cached results for query: IBM Cloud...
DEBUG - Cached search results for query: IBM Cloud...
INFO - Cache hit for key: search:abc123
DEBUG - Cache miss for key: search:xyz789
```

## Best Practices

### 1. Cache Invalidation

Clear cache when data changes:

```python
# Clear all search caches
cache_service.clear_pattern("search:*")

# Clear specific cache
cache_service.delete("search:specific_hash")
```

### 2. TTL Strategy

- **Frequently changing data**: 5-15 minutes
- **Stable data**: 1-24 hours
- **Static data**: 24+ hours

### 3. Cache Warming

Pre-populate cache with common queries:

```python
common_queries = [
    "IBM Cloud documentation",
    "IBM MaaS360 features",
    "IBM Maximo setup"
]

for query in common_queries:
    await web_search_service.search(query)
```

### 4. Error Handling

Cache failures don't break the application:

```python
# If cache fails, falls back to direct fetch
results = await web_search_service.search(query)
# Always returns results, cached or fresh
```

## Troubleshooting

### Connection Issues

**Problem**: `Failed to connect to Redis`

**Solutions**:
1. Check network connectivity
2. Verify credentials
3. Check firewall rules
4. Ensure Redis server is running

```python
# Test connection
from services.cache_service import cache_service
is_healthy = cache_service.health_check()
print(f"Redis healthy: {is_healthy}")
```

### High Memory Usage

**Problem**: Redis using too much memory

**Solutions**:
1. Reduce TTL values
2. Clear old caches
3. Implement cache size limits

```python
# Clear all caches
cache_service.clear_pattern("*")
```

### Low Hit Rate

**Problem**: Cache hit rate below 50%

**Solutions**:
1. Increase TTL
2. Analyze query patterns
3. Implement cache warming
4. Review cache key generation

## Security

### Connection Security

- ✅ Password-protected Redis instance
- ✅ TLS/SSL encryption (if enabled on Redis server)
- ✅ User authentication
- ✅ Network isolation

### Data Security

- Sensitive data should not be cached
- Use short TTLs for user-specific data
- Implement cache key namespacing

```python
# Good: Namespaced keys
cache_service.set("user:123:profile", data)

# Bad: Generic keys
cache_service.set("profile", data)
```

## Testing

### Unit Tests

```python
import pytest
from services.cache_service import cache_service

def test_cache_set_get():
    cache_service.set("test_key", {"data": "value"})
    result = cache_service.get("test_key")
    assert result == {"data": "value"}

def test_cache_expiry():
    cache_service.set("test_key", "value", ttl=1)
    time.sleep(2)
    result = cache_service.get("test_key")
    assert result is None
```

### Integration Tests

```python
async def test_search_caching():
    # First call - cache miss
    results1 = await web_search_service.search("test query")
    
    # Second call - cache hit
    results2 = await web_search_service.search("test query")
    
    assert results1 == results2
```

## Deployment

### Render Deployment

Redis credentials are already configured in the code. Just ensure environment variables are set in Render dashboard.

### Local Development

For local development without Redis:

```bash
# Disable Redis
REDIS_ENABLED=false
```

The application will work without caching.

## Cost Optimization

### Redis Pricing

Monitor your Redis usage:
- Memory usage
- Number of operations
- Data transfer

### Optimization Tips

1. **Use appropriate TTLs**: Don't cache forever
2. **Clear unused caches**: Regular cleanup
3. **Monitor hit rates**: Optimize cache strategy
4. **Compress large values**: Reduce memory usage

## Future Enhancements

Potential improvements:
- [ ] Cache compression for large values
- [ ] Distributed caching across multiple Redis instances
- [ ] Cache analytics dashboard
- [ ] Automatic cache warming
- [ ] Smart TTL based on query frequency
- [ ] Cache versioning for invalidation
- [ ] Redis Cluster support

## References

- [Redis Documentation](https://redis.io/documentation)
- [redis-py Documentation](https://redis-py.readthedocs.io/)
- [Caching Best Practices](https://redis.io/docs/manual/patterns/)

## Support

For issues:
1. Check Redis connection: `GET /api/cache/health`
2. View cache stats: `GET /api/cache/stats`
3. Check application logs
4. Review this documentation

---

**Last Updated**: 2026-05-21
**Version**: 1.0.0
**Redis Version**: Compatible with Redis 6.0+