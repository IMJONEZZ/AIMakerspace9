"""
Optimized memory access patterns for AI Life Coach.

This module provides optimized memory operations with caching and
batch processing to reduce latency.
"""

import time
from typing import Any, Dict, List, Optional, Tuple, Callable
from functools import wraps

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from memory import MemoryManager, UserProfile, Goal, Milestone, Setback
except ImportError:
    # For testing without full imports
    MemoryManager = object
    UserProfile = object
    Goal = object
    Milestone = object
    Setback = object

from .cache import get_cache_manager, cached_profile, cached_goals
from .profiler import get_profiler


class OptimizedMemoryManager:
    """
    Memory manager with performance optimizations.

    Features:
    - Transparent caching for frequently accessed data
    - Batch operations for bulk reads/writes
    - Lazy loading for large datasets
    """

    def __init__(self, base_manager: MemoryManager):
        """
        Initialize optimized memory manager.

        Args:
            base_manager: Underlying MemoryManager instance
        """
        self._manager = base_manager
        self._cache = get_cache_manager()
        self._profiler = get_profiler()

    # ==================== Optimized Profile Operations ====================

    def get_profile(self, user_id: str) -> Optional[UserProfile]:
        """
        Get user profile with caching.

        Args:
            user_id: User's unique identifier

        Returns:
            UserProfile or None if not found
        """
        with self._profiler.profile_section("memory.get_profile"):
            # Try cache first
            cached = self._cache.get_profile(user_id)
            if cached is not None:
                return cached

            # Load from underlying manager
            profile = self._manager.get_profile(user_id)
            if profile:
                self._cache.set_profile(user_id, profile)

            return profile

    def save_profile(self, profile: UserProfile) -> None:
        """
        Save profile and update cache.

        Args:
            profile: UserProfile to save
        """
        with self._profiler.profile_section("memory.save_profile"):
            # Save to underlying manager
            self._manager.save_profile(profile)
            # Update cache
            self._cache.set_profile(profile.user_id, profile)

    # ==================== Optimized Goal Operations ====================

    def get_goals(self, user_id: str) -> List[Goal]:
        """
        Get all goals for user with caching.

        Args:
            user_id: User's unique identifier

        Returns:
            List of Goal objects
        """
        with self._profiler.profile_section("memory.get_goals"):
            # Try cache first
            cached = self._cache.get_goals(user_id)
            if cached is not None:
                return cached

            # Load from underlying manager
            goals = self._manager.get_goals(user_id)
            if goals:
                self._cache.set_goals(user_id, goals)

            return goals

    def get_goal(self, user_id: str, goal_id: str) -> Optional[Goal]:
        """
        Get specific goal (from cache if available).

        Args:
            user_id: User's unique identifier
            goal_id: Goal's unique identifier

        Returns:
            Goal or None if not found
        """
        with self._profiler.profile_section("memory.get_goal"):
            # Try to find in cached goals first
            cached_goals = self._cache.get_goals(user_id)
            if cached_goals:
                for goal in cached_goals:
                    if goal.goal_id == goal_id:
                        return goal

            # Fall back to direct lookup
            return self._manager.get_goal(user_id, goal_id)

    def save_goal(self, user_id: str, goal: Goal) -> None:
        """
        Save goal and invalidate cache.

        Args:
            user_id: User's unique identifier
            goal: Goal to save
        """
        with self._profiler.profile_section("memory.save_goal"):
            self._manager.save_goal(user_id, goal)
            # Invalidate goals cache to force refresh
            self._cache.invalidate_goals(user_id)

    def get_goals_by_domain(self, user_id: str, domain: str) -> List[Goal]:
        """
        Get goals filtered by domain (uses cached data).

        Args:
            user_id: User's unique identifier
            domain: Domain to filter by

        Returns:
            List of Goal objects
        """
        with self._profiler.profile_section("memory.get_goals_by_domain"):
            goals = self.get_goals(user_id)  # Uses cache
            return [goal for goal in goals if goal.domain == domain]

    # ==================== Batch Operations ====================

    def get_user_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive user summary with optimized loading.

        Args:
            user_id: User's unique identifier

        Returns:
            Dictionary with all user data
        """
        with self._profiler.profile_section("memory.get_user_summary"):
            # Load from cache or underlying manager
            profile = self.get_profile(user_id)
            goals = self.get_goals(user_id)

            # These are typically accessed less frequently, skip cache
            milestones = self._manager.get_milestones(user_id)
            setbacks = self._manager.get_setbacks(user_id)
            preferences = self._manager.get_preferences(user_id)

            return {
                "profile": profile,
                "goals": goals,
                "milestones": milestones,
                "setbacks": setbacks,
                "preferences": preferences,
            }

    def get_multiple_profiles(self, user_ids: List[str]) -> Dict[str, Optional[UserProfile]]:
        """
        Get multiple profiles efficiently.

        Args:
            user_ids: List of user IDs

        Returns:
            Dictionary mapping user_id to profile
        """
        with self._profiler.profile_section("memory.get_multiple_profiles"):
            results = {}
            for user_id in user_ids:
                results[user_id] = self.get_profile(user_id)
            return results

    # ==================== Cache Management ====================

    def invalidate_user(self, user_id: str) -> None:
        """Invalidate all cached data for a user."""
        self._cache.invalidate_user(user_id)

    def clear_cache(self) -> None:
        """Clear all caches."""
        self._cache.clear_all()

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self._cache.get_all_stats()

    # ==================== Delegate to underlying manager ====================

    def __getattr__(self, name: str) -> Any:
        """Delegate unknown attributes to underlying manager."""
        return getattr(self._manager, name)


def create_optimized_memory_manager(store: Any) -> OptimizedMemoryManager:
    """
    Create an optimized memory manager.

    Args:
        store: LangGraph Store instance

    Returns:
        OptimizedMemoryManager instance
    """
    base_manager = MemoryManager(store)
    return OptimizedMemoryManager(base_manager)


class LazyLoader:
    """
    Lazy loading wrapper for expensive data loading operations.

    Delays loading until data is actually accessed.
    """

    def __init__(self, loader_func: Callable, *args, **kwargs):
        """
        Initialize lazy loader.

        Args:
            loader_func: Function to call when data is needed
            *args: Arguments for loader function
            **kwargs: Keyword arguments for loader function
        """
        self._loader = loader_func
        self._args = args
        self._kwargs = kwargs
        self._data: Optional[Any] = None
        self._loaded = False

    @property
    def data(self) -> Any:
        """Get data, loading if necessary."""
        if not self._loaded:
            with profile("lazy_loader.load"):
                self._data = self._loader(*self._args, **self._kwargs)
                self._loaded = True
        return self._data

    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to underlying data."""
        return getattr(self.data, name)

    def __iter__(self):
        """Allow iteration over data."""
        return iter(self.data)

    def __len__(self) -> int:
        """Return length of data."""
        return len(self.data)

    def __bool__(self) -> bool:
        """Check if data exists."""
        return bool(self.data)


class PrefetchManager:
    """
    Manages prefetching of data to reduce latency.

    Prefetches likely-to-be-needed data in the background.
    """

    def __init__(self, memory_manager: OptimizedMemoryManager):
        """
        Initialize prefetch manager.

        Args:
            memory_manager: Optimized memory manager instance
        """
        self._manager = memory_manager
        self._prefetch_queue: List[Tuple[str, str]] = []  # (type, id)

    def queue_profile_prefetch(self, user_id: str):
        """Queue a profile to be prefetched."""
        self._prefetch_queue.append(("profile", user_id))

    def queue_goals_prefetch(self, user_id: str):
        """Queue goals to be prefetched."""
        self._prefetch_queue.append(("goals", user_id))

    def execute_prefetch(self, max_items: int = 10):
        """
        Execute queued prefetches.

        Args:
            max_items: Maximum number of items to prefetch
        """
        with profile("prefetch.execute"):
            items_to_prefetch = self._prefetch_queue[:max_items]
            self._prefetch_queue = self._prefetch_queue[max_items:]

            for data_type, data_id in items_to_prefetch:
                try:
                    if data_type == "profile":
                        self._manager.get_profile(data_id)
                    elif data_type == "goals":
                        self._manager.get_goals(data_id)
                except Exception:
                    # Ignore prefetch errors
                    pass

    def clear_queue(self):
        """Clear the prefetch queue."""
        self._prefetch_queue.clear()
