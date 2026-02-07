"""
Integration of performance optimizations with AI Life Coach.

This module provides the bridge between the performance optimization
utilities and the main AI Life Coach system.
"""

from typing import Any, Dict, List, Optional
import functools

# Import performance utilities
from .profiler import get_profiler, profile, timed
from .cache import get_cache_manager, cached_profile, cached_goals
from .memory_optimizer import (
    OptimizedMemoryManager,
    create_optimized_memory_manager,
    LazyLoader,
)
from .parallel import parallel_specialists, optimize_specialist_delegation
from .tool_optimizer import get_tool_optimizer, optimized_tool


def optimize_life_coach_system(store: Any) -> Dict[str, Any]:
    """
    Optimize the AI Life Coach system with all performance improvements.

    Args:
        store: LangGraph Store instance

    Returns:
        Dictionary with optimized components:
        - memory_manager: OptimizedMemoryManager instance
        - cache_manager: Cache manager for direct access
        - profiler: Profiler for monitoring
    """
    # Create optimized memory manager
    memory_manager = create_optimized_memory_manager(store)

    # Get cache manager
    cache_manager = get_cache_manager()

    # Get profiler
    profiler = get_profiler()

    return {
        "memory_manager": memory_manager,
        "cache_manager": cache_manager,
        "profiler": profiler,
    }


def wrap_tools_with_performance_tracking(tools: List[Callable]) -> List[Callable]:
    """
    Wrap tools with performance tracking.

    Args:
        tools: List of tool functions

    Returns:
        List of wrapped tools with profiling
    """
    wrapped = []
    optimizer = get_tool_optimizer()

    for tool in tools:
        # Wrap with performance optimization
        wrapped_tool = optimizer.wrap_tool(tool)
        wrapped.append(wrapped_tool)

    return wrapped


def create_optimized_specialist_delegation(
    specialist_funcs: Dict[str, Callable], use_parallel: bool = True, parallel_threshold: int = 2
) -> Callable:
    """
    Create an optimized specialist delegation function.

    Args:
        specialist_funcs: Dictionary of specialist functions
        use_parallel: Whether to use parallel execution
        parallel_threshold: Minimum specialists to trigger parallel

    Returns:
        Function that executes specialists optimally
    """

    def delegate(context: Dict[str, Any]) -> Dict[str, Any]:
        if use_parallel and len(specialist_funcs) >= parallel_threshold:
            return parallel_specialists(
                specialist_funcs, context, max_workers=min(len(specialist_funcs), 4), timeout=30.0
            )
        else:
            # Sequential execution
            results = {}
            for name, func in specialist_funcs.items():
                with profile(f"specialist.{name}"):
                    try:
                        results[name] = func(**context)
                    except Exception as e:
                        results[name] = e
            return results

    return delegate


class PerformanceConfig:
    """
    Configuration for performance optimizations.

    Allows fine-tuning of caching, parallelization, and profiling.
    """

    def __init__(
        self,
        enable_caching: bool = True,
        enable_parallel: bool = True,
        enable_profiling: bool = True,
        profile_cache_ttl: float = 600.0,
        goals_cache_ttl: float = 300.0,
        tool_cache_ttl: float = 180.0,
        max_parallel_workers: int = 4,
        parallel_threshold: int = 2,
    ):
        self.enable_caching = enable_caching
        self.enable_parallel = enable_parallel
        self.enable_profiling = enable_profiling
        self.profile_cache_ttl = profile_cache_ttl
        self.goals_cache_ttl = goals_cache_ttl
        self.tool_cache_ttl = tool_cache_ttl
        self.max_parallel_workers = max_parallel_workers
        self.parallel_threshold = parallel_threshold

    @classmethod
    def development(cls) -> "PerformanceConfig":
        """Configuration optimized for development."""
        return cls(
            enable_caching=True,
            enable_parallel=True,
            enable_profiling=True,
            profile_cache_ttl=60.0,  # Shorter for development
            goals_cache_ttl=30.0,
            tool_cache_ttl=30.0,
            max_parallel_workers=2,
            parallel_threshold=2,
        )

    @classmethod
    def production(cls) -> "PerformanceConfig":
        """Configuration optimized for production."""
        return cls(
            enable_caching=True,
            enable_parallel=True,
            enable_profiling=False,  # Disable in production for performance
            profile_cache_ttl=600.0,
            goals_cache_ttl=300.0,
            tool_cache_ttl=180.0,
            max_parallel_workers=4,
            parallel_threshold=2,
        )

    @classmethod
    def testing(cls) -> "PerformanceConfig":
        """Configuration optimized for testing."""
        return cls(
            enable_caching=False,  # Disable for consistent tests
            enable_parallel=False,  # Sequential for deterministic tests
            enable_profiling=True,
            profile_cache_ttl=0.0,
            goals_cache_ttl=0.0,
            tool_cache_ttl=0.0,
            max_parallel_workers=1,
            parallel_threshold=999,  # Never parallel in tests
        )


# Global performance configuration
_perf_config: Optional[PerformanceConfig] = None


def set_performance_config(config: PerformanceConfig):
    """Set the global performance configuration."""
    global _perf_config
    _perf_config = config


def get_performance_config() -> PerformanceConfig:
    """Get the global performance configuration."""
    global _perf_config
    if _perf_config is None:
        _perf_config = PerformanceConfig()
    return _perf_config


def print_performance_summary():
    """Print a summary of performance optimizations."""
    config = get_performance_config()
    cache = get_cache_manager()
    profiler = get_profiler()

    print("\n" + "=" * 60)
    print("AI LIFE COACH - PERFORMANCE OPTIMIZATION SUMMARY")
    print("=" * 60)

    print("\nConfiguration:")
    print(f"  Caching: {'Enabled' if config.enable_caching else 'Disabled'}")
    print(f"  Parallel Execution: {'Enabled' if config.enable_parallel else 'Disabled'}")
    print(f"  Profiling: {'Enabled' if config.enable_profiling else 'Disabled'}")
    print(f"  Max Parallel Workers: {config.max_parallel_workers}")

    print("\nCache Statistics:")
    stats = cache.get_all_stats()
    for cache_name, cache_stats in stats.items():
        print(f"  {cache_name}:")
        print(f"    Size: {cache_stats['size']}/{cache_stats['max_size']}")
        print(f"    Hit Rate: {cache_stats['hit_rate_percent']:.1f}%")

    print("\nProfiler Statistics:")
    summary = profiler.get_summary()
    if summary:
        total_time = sum(s["total_time"] for s in summary.values())
        print(f"  Total Profiled Time: {total_time:.3f}s")
        print(f"  Profiled Sections: {len(summary)}")
    else:
        print("  No profiling data collected")

    print("=" * 60)
