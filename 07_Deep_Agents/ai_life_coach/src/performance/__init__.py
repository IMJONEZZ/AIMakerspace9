"""
Performance optimization module for AI Life Coach.

This module provides comprehensive performance optimization utilities:

- **profiler**: Performance profiling and bottleneck identification
- **cache**: Intelligent caching with TTL and LRU strategies
- **parallel**: Parallel execution for subagents and tools
- **memory_optimizer**: Optimized memory access patterns
- **tool_optimizer**: Tool invocation optimization

Quick Start:
    >>> from src.performance import get_profiler, get_cache_manager
    >>>
    >>> # Profile a section of code
    >>> with profile("my_operation"):
    ...     result = expensive_function()
    >>>
    >>> # Use caching
    >>> cache = get_cache_manager()
    >>> cache.set_profile(user_id, profile)
    >>> cached = cache.get_profile(user_id)
    >>>
    >>> # Execute specialists in parallel
    >>> from src.performance.parallel import parallel_specialists
    >>> results = parallel_specialists(specialists, context)
"""

from .profiler import (
    PerformanceProfiler,
    ToolPerformanceTracker,
    MemoryAccessOptimizer,
    get_profiler,
    reset_profiler,
    profile,
    timed,
    run_cprofile,
    print_performance_report,
    save_performance_report,
)

from .cache import (
    TimedCache,
    MemoryCacheManager,
    CacheWarmer,
    get_cache_manager,
    reset_cache_manager,
    cached_profile,
    cached_goals,
    cached_tool,
    lru_cached,
    hash_args,
    invalidate_user_cache,
    clear_all_caches,
)

from .parallel import (
    ParallelExecutor,
    AsyncToolExecutor,
    ParallelResult,
    parallel_map,
    parallel_specialists,
    BatchProcessor,
    optimize_specialist_delegation,
)

from .memory_optimizer import (
    OptimizedMemoryManager,
    LazyLoader,
    PrefetchManager,
    create_optimized_memory_manager,
)

from .tool_optimizer import (
    ToolInvocationOptimizer,
    BatchToolInvoker,
    RedundantCallDetector,
    optimized_tool,
    optimize_tool_call,
    get_tool_optimizer,
)

__all__ = [
    # Profiler
    "PerformanceProfiler",
    "ToolPerformanceTracker",
    "MemoryAccessOptimizer",
    "get_profiler",
    "reset_profiler",
    "profile",
    "timed",
    "run_cprofile",
    "print_performance_report",
    "save_performance_report",
    # Cache
    "TimedCache",
    "MemoryCacheManager",
    "CacheWarmer",
    "get_cache_manager",
    "reset_cache_manager",
    "cached_profile",
    "cached_goals",
    "cached_tool",
    "lru_cached",
    "hash_args",
    "invalidate_user_cache",
    "clear_all_caches",
    # Parallel
    "ParallelExecutor",
    "AsyncToolExecutor",
    "ParallelResult",
    "parallel_map",
    "parallel_specialists",
    "BatchProcessor",
    "optimize_specialist_delegation",
    # Memory Optimizer
    "OptimizedMemoryManager",
    "LazyLoader",
    "PrefetchManager",
    "create_optimized_memory_manager",
    # Tool Optimizer
    "ToolInvocationOptimizer",
    "BatchToolInvoker",
    "RedundantCallDetector",
    "optimized_tool",
    "optimize_tool_call",
    "get_tool_optimizer",
]
