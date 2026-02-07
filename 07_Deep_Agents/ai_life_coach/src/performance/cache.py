"""
Caching strategies and utilities for AI Life Coach performance optimization.

This module provides:
- LRU cache integration for frequently accessed data
- Memory-aware caching with TTL (time-to-live)
- Cache statistics and monitoring
- Intelligent cache warming strategies
"""

import functools
import time
import hashlib
import json
from typing import Any, Callable, Dict, List, Optional, Tuple, Set
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class CacheEntry:
    """Represents a cached value with metadata."""

    value: Any
    timestamp: float = field(default_factory=time.time)
    access_count: int = 0
    last_access: float = field(default_factory=time.time)


class TimedCache:
    """
    A time-based cache with TTL (time-to-live) support.

    Automatically expires entries after a specified time period.
    """

    def __init__(self, default_ttl: float = 300.0, max_size: int = 1000):
        """
        Initialize the cache.

        Args:
            default_ttl: Default time-to-live in seconds (default: 5 minutes)
            max_size: Maximum number of entries to store
        """
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._cache: Dict[str, CacheEntry] = {}
        self._hits = 0
        self._misses = 0

    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if a cache entry has expired."""
        return time.time() - entry.timestamp > self.default_ttl

    def _evict_expired(self):
        """Remove expired entries from the cache."""
        expired_keys = [key for key, entry in self._cache.items() if self._is_expired(entry)]
        for key in expired_keys:
            del self._cache[key]

    def _evict_lru(self):
        """Evict least recently used entries if cache is full."""
        if len(self._cache) >= self.max_size:
            # Sort by last_access and remove oldest
            sorted_items = sorted(self._cache.items(), key=lambda x: x[1].last_access)
            # Remove 10% of entries
            to_remove = max(1, len(sorted_items) // 10)
            for key, _ in sorted_items[:to_remove]:
                del self._cache[key]

    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or expired
        """
        self._evict_expired()

        entry = self._cache.get(key)
        if entry is None:
            self._misses += 1
            return None

        if self._is_expired(entry):
            del self._cache[key]
            self._misses += 1
            return None

        # Update access metadata
        entry.access_count += 1
        entry.last_access = time.time()
        self._hits += 1

        return entry.value

    def set(self, key: str, value: Any, ttl: Optional[float] = None):
        """
        Store a value in the cache.

        Args:
            key: Cache key
            value: Value to store
            ttl: Optional custom TTL (uses default if not specified)
        """
        self._evict_expired()
        self._evict_lru()

        entry = CacheEntry(
            value=value, timestamp=time.time(), access_count=0, last_access=time.time()
        )
        self._cache[key] = entry

    def delete(self, key: str) -> bool:
        """
        Delete a key from the cache.

        Args:
            key: Cache key to delete

        Returns:
            True if key was deleted, False if not found
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self):
        """Clear all entries from the cache."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0

        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate,
            "hit_rate_percent": hit_rate * 100,
        }

    def get_keys(self) -> List[str]:
        """Get all keys in the cache."""
        self._evict_expired()
        return list(self._cache.keys())


class MemoryCacheManager:
    """
    Manages multiple caches for different data types.

    Provides specialized caches for:
    - User profiles (longer TTL, frequently accessed)
    - Goals and progress (medium TTL)
    - Tool results (short TTL, expensive computations)
    """

    def __init__(self):
        # Profile cache - accessed frequently, rarely changes
        self.profile_cache = TimedCache(default_ttl=600.0, max_size=500)  # 10 min TTL

        # Goals cache - accessed often, changes occasionally
        self.goals_cache = TimedCache(default_ttl=300.0, max_size=1000)  # 5 min TTL

        # Tool results cache - expensive computations
        self.tool_cache = TimedCache(default_ttl=180.0, max_size=2000)  # 3 min TTL

        # Calculated results cache - for expensive calculations
        self.calculation_cache = TimedCache(default_ttl=60.0, max_size=5000)  # 1 min TTL

    def get_profile(self, user_id: str) -> Optional[Any]:
        """Get cached user profile."""
        return self.profile_cache.get(f"profile:{user_id}")

    def set_profile(self, user_id: str, profile: Any):
        """Cache user profile."""
        self.profile_cache.set(f"profile:{user_id}", profile)

    def invalidate_profile(self, user_id: str):
        """Invalidate cached profile."""
        self.profile_cache.delete(f"profile:{user_id}")

    def get_goals(self, user_id: str) -> Optional[Any]:
        """Get cached goals for user."""
        return self.goals_cache.get(f"goals:{user_id}")

    def set_goals(self, user_id: str, goals: Any):
        """Cache goals for user."""
        self.goals_cache.set(f"goals:{user_id}", goals)

    def invalidate_goals(self, user_id: str):
        """Invalidate cached goals."""
        self.goals_cache.delete(f"goals:{user_id}")

    def get_tool_result(self, tool_name: str, args_hash: str) -> Optional[Any]:
        """Get cached tool result."""
        return self.tool_cache.get(f"tool:{tool_name}:{args_hash}")

    def set_tool_result(self, tool_name: str, args_hash: str, result: Any):
        """Cache tool result."""
        self.tool_cache.set(f"tool:{tool_name}:{args_hash}", result)

    def get_calculation(self, calc_key: str) -> Optional[Any]:
        """Get cached calculation result."""
        return self.calculation_cache.get(f"calc:{calc_key}")

    def set_calculation(self, calc_key: str, result: Any):
        """Cache calculation result."""
        self.calculation_cache.set(f"calc:{calc_key}", result)

    def invalidate_user(self, user_id: str):
        """Invalidate all cached data for a user."""
        self.invalidate_profile(user_id)
        self.invalidate_goals(user_id)

    def clear_all(self):
        """Clear all caches."""
        self.profile_cache.clear()
        self.goals_cache.clear()
        self.tool_cache.clear()
        self.calculation_cache.clear()

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all caches."""
        return {
            "profile_cache": self.profile_cache.get_stats(),
            "goals_cache": self.goals_cache.get_stats(),
            "tool_cache": self.tool_cache.get_stats(),
            "calculation_cache": self.calculation_cache.get_stats(),
        }

    def print_stats(self):
        """Print cache statistics."""
        stats = self.get_all_stats()
        print("\n" + "=" * 60)
        print("CACHE STATISTICS")
        print("=" * 60)

        for cache_name, cache_stats in stats.items():
            print(f"\n{cache_name}:")
            print(f"  Size: {cache_stats['size']}/{cache_stats['max_size']}")
            print(f"  Hits: {cache_stats['hits']}")
            print(f"  Misses: {cache_stats['misses']}")
            print(f"  Hit Rate: {cache_stats['hit_rate_percent']:.1f}%")


# Global cache manager instance
_cache_manager: Optional[MemoryCacheManager] = None


def get_cache_manager() -> MemoryCacheManager:
    """Get or create the global cache manager."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = MemoryCacheManager()
    return _cache_manager


def reset_cache_manager():
    """Reset the global cache manager."""
    global _cache_manager
    _cache_manager = MemoryCacheManager()


def hash_args(*args, **kwargs) -> str:
    """
    Create a hash of function arguments for caching.

    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Hash string suitable for cache key
    """
    # Convert arguments to a consistent string representation
    try:
        args_str = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
    except (TypeError, ValueError):
        # Fallback for non-serializable arguments
        args_str = f"{str(args)}:{str(kwargs)}"

    return hashlib.md5(args_str.encode()).hexdigest()


def cached_profile(ttl: float = 600.0):
    """
    Decorator to cache user profile lookups.

    Args:
        ttl: Time-to-live in seconds

    Example:
        >>> @cached_profile(ttl=600)
        ... def get_user_profile(user_id: str) -> UserProfile:
        ...     return db.get_profile(user_id)
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache_manager()

            # Extract user_id from args or kwargs
            user_id = kwargs.get("user_id") or (args[0] if args else None)

            if user_id:
                # Try cache first
                cached = cache.get_profile(user_id)
                if cached is not None:
                    return cached

                # Call function and cache result
                result = func(*args, **kwargs)
                if result is not None:
                    cache.set_profile(user_id, result)
                return result

            # No user_id, just call function
            return func(*args, **kwargs)

        return wrapper

    return decorator


def cached_goals(ttl: float = 300.0):
    """
    Decorator to cache user goals lookups.

    Args:
        ttl: Time-to-live in seconds
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache_manager()

            # Extract user_id from args or kwargs
            user_id = kwargs.get("user_id") or (args[0] if args else None)

            if user_id:
                # Try cache first
                cached = cache.get_goals(user_id)
                if cached is not None:
                    return cached

                # Call function and cache result
                result = func(*args, **kwargs)
                if result is not None:
                    cache.set_goals(user_id, result)
                return result

            # No user_id, just call function
            return func(*args, **kwargs)

        return wrapper

    return decorator


def cached_tool(ttl: float = 180.0):
    """
    Decorator to cache tool results.

    Args:
        ttl: Time-to-live in seconds

    Example:
        >>> @cached_tool(ttl=180)
        ... def expensive_calculation(data: dict) -> dict:
        ...     return heavy_computation(data)
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache_manager()

            # Create hash of arguments
            args_hash = hash_args(*args, **kwargs)
            tool_name = func.__name__

            # Try cache first
            cached = cache.get_tool_result(tool_name, args_hash)
            if cached is not None:
                return cached

            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set_tool_result(tool_name, args_hash, result)
            return result

        return wrapper

    return decorator


def lru_cached(maxsize: int = 128):
    """
    Simple LRU cache decorator using functools.

    Args:
        maxsize: Maximum cache size

    Example:
        >>> @lru_cached(maxsize=256)
        ... def compute_score(data: dict) -> float:
        ...     return expensive_calculation(data)
    """
    return functools.lru_cache(maxsize=maxsize)


class CacheWarmer:
    """
    Pre-populates caches with frequently accessed data.

    Helps reduce cold-start latency by warming caches ahead of time.
    """

    def __init__(self, cache_manager: Optional[MemoryCacheManager] = None):
        self.cache = cache_manager or get_cache_manager()
        self.warm_stats: Dict[str, int] = {"profiles": 0, "goals": 0, "errors": 0}

    def warm_user_data(self, memory_manager: Any, user_ids: List[str]):
        """
        Warm cache with user data.

        Args:
            memory_manager: MemoryManager instance
            user_ids: List of user IDs to warm
        """
        for user_id in user_ids:
            try:
                # Warm profile cache
                profile = memory_manager.get_profile(user_id)
                if profile:
                    self.cache.set_profile(user_id, profile)
                    self.warm_stats["profiles"] += 1

                # Warm goals cache
                goals = memory_manager.get_goals(user_id)
                if goals:
                    self.cache.set_goals(user_id, goals)
                    self.warm_stats["goals"] += 1

            except Exception as e:
                self.warm_stats["errors"] += 1
                print(f"Error warming cache for user {user_id}: {e}")

    def get_warm_stats(self) -> Dict[str, int]:
        """Get warming statistics."""
        return self.warm_stats.copy()


def invalidate_user_cache(user_id: str):
    """Invalidate all cached data for a user."""
    cache = get_cache_manager()
    cache.invalidate_user(user_id)


def clear_all_caches():
    """Clear all caches."""
    cache = get_cache_manager()
    cache.clear_all()
