"""
Caching system with Redis support (falls back to in-memory cache).
"""
import json
import time
from typing import Any, Optional, Dict
from functools import wraps
import hashlib

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("⚠️  Redis not available, using in-memory cache")


class CacheService:
    """Caching service with Redis or in-memory fallback."""
    
    def __init__(self, redis_url: Optional[str] = None, default_ttl: int = 3600):
        """
        Initialize cache service.
        
        Args:
            redis_url: Redis connection URL (optional)
            default_ttl: Default time-to-live in seconds
        """
        self.default_ttl = default_ttl
        self.redis_client = None
        self.memory_cache: Dict[str, tuple] = {}  # {key: (value, expiry_time)}
        
        if REDIS_AVAILABLE and redis_url:
            try:
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                self.redis_client.ping()
                print("✅ Redis cache connected")
            except Exception as e:
                print(f"⚠️  Redis connection failed: {e}, using in-memory cache")
                self.redis_client = None
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from arguments."""
        key_parts = [prefix] + [str(arg) for arg in args]
        if kwargs:
            key_parts.append(json.dumps(kwargs, sort_keys=True))
        
        key_string = ":".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Set cache value.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None = default)
        """
        ttl = ttl or self.default_ttl
        
        if self.redis_client:
            try:
                serialized = json.dumps(value)
                self.redis_client.setex(key, ttl, serialized)
            except Exception as e:
                print(f"Redis set error: {e}")
        else:
            # In-memory cache
            expiry = time.time() + ttl
            self.memory_cache[key] = (value, expiry)
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get cache value.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        if self.redis_client:
            try:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            except Exception as e:
                print(f"Redis get error: {e}")
                return None
        else:
            # In-memory cache
            if key in self.memory_cache:
                value, expiry = self.memory_cache[key]
                if time.time() < expiry:
                    return value
                else:
                    # Expired
                    del self.memory_cache[key]
        
        return None
    
    def delete(self, key: str):
        """Delete cache entry."""
        if self.redis_client:
            try:
                self.redis_client.delete(key)
            except Exception as e:
                print(f"Redis delete error: {e}")
        else:
            self.memory_cache.pop(key, None)
    
    def clear(self, pattern: Optional[str] = None):
        """
        Clear cache entries.
        
        Args:
            pattern: Optional pattern to match keys (Redis only)
        """
        if self.redis_client:
            try:
                if pattern:
                    keys = self.redis_client.keys(pattern)
                    if keys:
                        self.redis_client.delete(*keys)
                else:
                    self.redis_client.flushdb()
            except Exception as e:
                print(f"Redis clear error: {e}")
        else:
            if pattern:
                # Simple pattern matching for in-memory
                keys_to_delete = [k for k in self.memory_cache.keys() if pattern in k]
                for key in keys_to_delete:
                    del self.memory_cache[key]
            else:
                self.memory_cache.clear()
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if self.redis_client:
            try:
                return self.redis_client.exists(key) > 0
            except Exception as e:
                print(f"Redis exists error: {e}")
                return False
        else:
            if key in self.memory_cache:
                _, expiry = self.memory_cache[key]
                return time.time() < expiry
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if self.redis_client:
            try:
                info = self.redis_client.info('stats')
                return {
                    'type': 'redis',
                    'total_keys': self.redis_client.dbsize(),
                    'hits': info.get('keyspace_hits', 0),
                    'misses': info.get('keyspace_misses', 0)
                }
            except Exception as e:
                print(f"Redis stats error: {e}")
                return {'type': 'redis', 'error': str(e)}
        else:
            # Clean expired entries
            current_time = time.time()
            expired = [k for k, (_, exp) in self.memory_cache.items() if exp < current_time]
            for key in expired:
                del self.memory_cache[key]
            
            return {
                'type': 'memory',
                'total_keys': len(self.memory_cache)
            }


def cached(ttl: int = 3600, key_prefix: str = "cache"):
    """
    Decorator for caching function results.
    
    Args:
        ttl: Time-to-live in seconds
        key_prefix: Prefix for cache keys
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get cache instance (assumes it's available globally)
            cache = kwargs.pop('_cache', None)
            if not cache:
                return await func(*args, **kwargs)
            
            # Generate cache key
            cache_key = cache._generate_key(key_prefix, func.__name__, *args, **kwargs)
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            if result:
                cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


# Global cache instance
cache_service = CacheService()


# Cache helpers
def cache_gemini_response(user_id: int, prompt: str, response: str, ttl: int = 1800):
    """Cache Gemini AI response."""
    key = f"gemini:{user_id}:{hashlib.md5(prompt.encode()).hexdigest()}"
    cache_service.set(key, response, ttl)


def get_cached_gemini_response(user_id: int, prompt: str) -> Optional[str]:
    """Get cached Gemini response."""
    key = f"gemini:{user_id}:{hashlib.md5(prompt.encode()).hexdigest()}"
    return cache_service.get(key)


def cache_translation(text: str, target_lang: str, translation: str, ttl: int = 86400):
    """Cache translation result."""
    key = f"translation:{target_lang}:{hashlib.md5(text.encode()).hexdigest()}"
    cache_service.set(key, translation, ttl)


def get_cached_translation(text: str, target_lang: str) -> Optional[str]:
    """Get cached translation."""
    key = f"translation:{target_lang}:{hashlib.md5(text.encode()).hexdigest()}"
    return cache_service.get(key)


def cache_user_preferences(user_id: int, preferences: Dict, ttl: int = 3600):
    """Cache user preferences."""
    key = f"prefs:{user_id}"
    cache_service.set(key, preferences, ttl)


def get_cached_user_preferences(user_id: int) -> Optional[Dict]:
    """Get cached user preferences."""
    key = f"prefs:{user_id}"
    return cache_service.get(key)


def clear_user_cache(user_id: int):
    """Clear all cache for a user."""
    cache_service.clear(f"*:{user_id}:*")
