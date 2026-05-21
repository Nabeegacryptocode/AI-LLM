"""
Cache Management API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging

from services.cache_service import cache_service
from app.utils.auth import verify_api_key

router = APIRouter(prefix="/cache", tags=["cache"])
logger = logging.getLogger(__name__)


@router.get("/stats", dependencies=[Depends(verify_api_key)])
async def get_cache_stats() -> Dict[str, Any]:
    """
    Get cache statistics
    
    Returns:
        Cache statistics including hit rate, memory usage, etc.
    """
    try:
        stats = cache_service.get_stats()
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear", dependencies=[Depends(verify_api_key)])
async def clear_cache(pattern: str = "*") -> Dict[str, Any]:
    """
    Clear cache entries matching pattern
    
    Args:
        pattern: Key pattern to clear (default: "*" for all)
        
    Returns:
        Number of keys cleared
    """
    try:
        deleted = cache_service.clear_pattern(pattern)
        return {
            "status": "success",
            "message": f"Cleared {deleted} cache entries",
            "deleted_count": deleted
        }
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", dependencies=[Depends(verify_api_key)])
async def cache_health() -> Dict[str, Any]:
    """
    Check cache health
    
    Returns:
        Cache health status
    """
    try:
        is_healthy = cache_service.health_check()
        return {
            "status": "success",
            "healthy": is_healthy,
            "enabled": cache_service.enabled
        }
    except Exception as e:
        logger.error(f"Error checking cache health: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/key/{key}", dependencies=[Depends(verify_api_key)])
async def delete_cache_key(key: str) -> Dict[str, Any]:
    """
    Delete specific cache key
    
    Args:
        key: Cache key to delete
        
    Returns:
        Success status
    """
    try:
        success = cache_service.delete(key)
        return {
            "status": "success" if success else "failed",
            "message": f"Key '{key}' deleted" if success else f"Key '{key}' not found or error occurred"
        }
    except Exception as e:
        logger.error(f"Error deleting cache key: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Made with Bob