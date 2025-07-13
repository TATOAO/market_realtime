"""
Redis Cache Manager for Real-time Market Data

This module provides a Redis-based caching layer for real-time order book data,
enabling fast access to recent data and reducing database load.
"""

import json
import logging
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
import redis.asyncio as redis
from redis.exceptions import RedisError

from ..config import settings

# Configure logging
logger = logging.getLogger(__name__)


class RedisCacheManager:
    """
    Redis cache manager for real-time market data.
    
    This class provides methods for:
    - Caching recent order book data
    - Managing real-time data with TTL
    - Fast retrieval of cached data
    - Cache invalidation and cleanup
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize the Redis cache manager.
        
        Args:
            redis_url: Redis connection string. If not provided,
                      will use REDIS_URL environment variable.
        """
        self.redis_url = redis_url or settings.redis_url
        if not self.redis_url:
            raise ValueError("Redis URL must be provided or set in REDIS_URL environment variable")
        
        self.redis_client: Optional[redis.Redis] = None
        self._connection_lock = None
    
    async def initialize(self) -> None:
        """Initialize the Redis connection."""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            
            # Test connection
            await self.redis_client.ping()
            logger.info("Redis cache connection initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Redis cache: {e}")
            raise
    
    async def close(self) -> None:
        """Close the Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis cache connection closed")
    
    async def health_check(self) -> bool:
        """
        Check if Redis cache is healthy and accessible.
        
        Returns:
            bool: True if cache is healthy, False otherwise
        """
        try:
            if not self.redis_client:
                return False
            await self.redis_client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis cache health check failed: {e}")
            return False
    
    # Order book caching methods
    async def cache_order_book_data(self, symbol: str, data: Dict[str, Any], 
                                   ttl_seconds: int = 3600) -> bool:
        """
        Cache order book data for a symbol.
        
        Args:
            symbol: Stock symbol
            data: Order book data dictionary
            ttl_seconds: Time to live in seconds (default: 1 hour)
            
        Returns:
            bool: True if cached successfully, False otherwise
        """
        try:
            if not self.redis_client:
                return False
            
            # Create cache key
            cache_key = f"orderbook:{symbol}:latest"
            history_key = f"orderbook:{symbol}:history"
            
            # Cache latest data
            await self.redis_client.setex(
                cache_key,
                ttl_seconds,
                json.dumps(data, default=str)
            )
            
            # Add to history (keep last 100 entries)
            await self.redis_client.lpush(history_key, json.dumps(data, default=str))
            await self.redis_client.ltrim(history_key, 0, 99)
            await self.redis_client.expire(history_key, ttl_seconds)
            
            logger.debug(f"Cached order book data for {symbol}")
            return True
        except Exception as e:
            logger.error(f"Error caching order book data for {symbol}: {e}")
            return False
    
    async def get_cached_order_book_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get cached order book data for a symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Cached order book data or None if not found
        """
        try:
            if not self.redis_client:
                return None
            
            cache_key = f"orderbook:{symbol}:latest"
            data = await self.redis_client.get(cache_key)
            
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Error retrieving cached order book data for {symbol}: {e}")
            return None
    
    async def get_cached_order_book_history(self, symbol: str, 
                                           limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get cached order book history for a symbol.
        
        Args:
            symbol: Stock symbol
            limit: Maximum number of historical entries to return
            
        Returns:
            List of cached order book data entries
        """
        try:
            if not self.redis_client:
                return []
            
            history_key = f"orderbook:{symbol}:history"
            data_list = await self.redis_client.lrange(history_key, 0, limit - 1)
            
            result = []
            for data_str in data_list:
                try:
                    result.append(json.loads(data_str))
                except json.JSONDecodeError:
                    continue
            
            return result
        except Exception as e:
            logger.error(f"Error retrieving cached order book history for {symbol}: {e}")
            return []
    
    async def get_cached_order_book_data_today(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Get all cached order book data for a symbol from today.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            List of cached order book data from today
        """
        try:
            if not self.redis_client:
                return []
            
            history_key = f"orderbook:{symbol}:history"
            data_list = await self.redis_client.lrange(history_key, 0, -1)
            
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            result = []
            
            for data_str in data_list:
                try:
                    data = json.loads(data_str)
                    # Check if data is from today
                    if 'time' in data:
                        data_time = datetime.fromisoformat(data['time'].replace('Z', '+00:00'))
                        if data_time >= today_start:
                            result.append(data)
                except (json.JSONDecodeError, ValueError):
                    continue
            
            return result
        except Exception as e:
            logger.error(f"Error retrieving today's cached order book data for {symbol}: {e}")
            return []
    
    async def invalidate_order_book_cache(self, symbol: str) -> bool:
        """
        Invalidate cached order book data for a symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            bool: True if invalidated successfully, False otherwise
        """
        try:
            if not self.redis_client:
                return False
            
            cache_key = f"orderbook:{symbol}:latest"
            history_key = f"orderbook:{symbol}:history"
            
            await self.redis_client.delete(cache_key, history_key)
            logger.info(f"Invalidated order book cache for {symbol}")
            return True
        except Exception as e:
            logger.error(f"Error invalidating order book cache for {symbol}: {e}")
            return False
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        try:
            if not self.redis_client:
                return {}
            
            info = await self.redis_client.info()
            return {
                'connected_clients': info.get('connected_clients', 0),
                'used_memory_human': info.get('used_memory_human', '0B'),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'uptime_in_seconds': info.get('uptime_in_seconds', 0)
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}
    
    async def clear_all_order_book_cache(self) -> bool:
        """
        Clear all order book cache data.
        
        Returns:
            bool: True if cleared successfully, False otherwise
        """
        try:
            if not self.redis_client:
                return False
            
            # Get all order book keys
            pattern = "orderbook:*"
            keys = await self.redis_client.keys(pattern)
            
            if keys:
                await self.redis_client.delete(*keys)
                logger.info(f"Cleared {len(keys)} order book cache keys")
            
            return True
        except Exception as e:
            logger.error(f"Error clearing order book cache: {e}")
            return False
    
    # Utility methods for cache management
    async def set_cache_value(self, key: str, value: Any, ttl_seconds: int = 3600) -> bool:
        """
        Set a generic cache value.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time to live in seconds
            
        Returns:
            bool: True if set successfully, False otherwise
        """
        try:
            if not self.redis_client:
                return False
            
            await self.redis_client.setex(
                key,
                ttl_seconds,
                json.dumps(value, default=str)
            )
            return True
        except Exception as e:
            logger.error(f"Error setting cache value for {key}: {e}")
            return False
    
    async def get_cache_value(self, key: str) -> Optional[Any]:
        """
        Get a generic cache value.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        try:
            if not self.redis_client:
                return None
            
            data = await self.redis_client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Error getting cache value for {key}: {e}")
            return None
    
    async def delete_cache_value(self, key: str) -> bool:
        """
        Delete a cache value.
        
        Args:
            key: Cache key
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            if not self.redis_client:
                return False
            
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error deleting cache value for {key}: {e}")
            return False


# Global cache manager instance
_cache_manager: Optional[RedisCacheManager] = None


async def get_cache_manager() -> RedisCacheManager:
    """
    Get the global cache manager instance.
    
    Returns:
        RedisCacheManager: Global cache manager instance
    """
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = RedisCacheManager()
        await _cache_manager.initialize()
    return _cache_manager


async def close_cache_manager() -> None:
    """Close the global cache manager."""
    global _cache_manager
    if _cache_manager:
        await _cache_manager.close()
        _cache_manager = None 