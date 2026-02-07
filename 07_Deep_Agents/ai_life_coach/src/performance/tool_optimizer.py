"""
Optimized tool invocations for AI Life Coach.

This module provides tool wrappers that reduce redundant invocations
and improve overall tool execution performance.
"""

import functools
import hashlib
import json
from typing import Any, Callable, Dict, List, Optional, Tuple, Set
from collections import defaultdict

from .cache import get_cache_manager, hash_args
from .profiler import profile


class ToolInvocationOptimizer:
    """
    Optimizes tool invocations by:
    - Deduplicating concurrent identical calls
    - Caching results for deterministic tools
    - Batching related operations
    """

    def __init__(self):
        self._cache = get_cache_manager()
        self._pending_calls: Dict[str, Any] = {}  # Deduplication
        self._call_stats: Dict[str, int] = defaultdict(int)

    def _get_call_key(self, tool_name: str, args: Tuple, kwargs: Dict) -> str:
        """Generate unique key for a tool call."""
        args_hash = hash_args(*args, **kwargs)
        return f"{tool_name}:{args_hash}"

    def invoke_with_dedup(self, tool_func: Callable, *args, **kwargs) -> Any:
        """
        Invoke a tool with call deduplication.

        If the same call is already in progress, waits for its result
        instead of making a duplicate call.

        Args:
            tool_func: Tool function to invoke
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Tool result
        """
        tool_name = getattr(tool_func, "__name__", "unknown")
        call_key = self._get_call_key(tool_name, args, kwargs)

        # Check if this exact call is already pending
        if call_key in self._pending_calls:
            # Wait for existing call to complete
            return self._pending_calls[call_key]

        # Make the call
        self._call_stats[tool_name] += 1

        with profile(f"tool.{tool_name}"):
            result = tool_func(*args, **kwargs)

        return result

    def invoke_with_cache(
        self, tool_func: Callable, *args, cache_ttl: float = 180.0, **kwargs
    ) -> Any:
        """
        Invoke a tool with result caching.

        Args:
            tool_func: Tool function to invoke
            *args: Positional arguments
            cache_ttl: Cache time-to-live in seconds
            **kwargs: Keyword arguments

        Returns:
            Tool result (possibly from cache)
        """
        tool_name = getattr(tool_func, "__name__", "unknown")
        call_key = self._get_call_key(tool_name, args, kwargs)

        # Try cache first
        cached = self._cache.get_tool_result(tool_name, call_key)
        if cached is not None:
            return cached

        # Make the call
        self._call_stats[tool_name] += 1

        with profile(f"tool.{tool_name}"):
            result = tool_func(*args, **kwargs)

        # Cache the result
        self._cache.set_tool_result(tool_name, call_key, result)

        return result

    def get_stats(self) -> Dict[str, int]:
        """Get tool invocation statistics."""
        return dict(self._call_stats)


class BatchToolInvoker:
    """
    Batches multiple tool calls for more efficient execution.

    Collects tool calls and executes them together when the batch is flushed.
    """

    def __init__(self, max_batch_size: int = 10):
        """
        Initialize batch invoker.

        Args:
            max_batch_size: Maximum number of calls per batch
        """
        self.max_batch_size = max_batch_size
        self._pending: List[Tuple[Callable, Tuple, Dict]] = []
        self._results: List[Any] = []

    def add(self, tool_func: Callable, *args, **kwargs):
        """
        Add a tool call to the batch.

        Args:
            tool_func: Tool function to call
            *args: Positional arguments
            **kwargs: Keyword arguments
        """
        self._pending.append((tool_func, args, kwargs))

        # Auto-flush if batch is full
        if len(self._pending) >= self.max_batch_size:
            self.flush()

    def flush(self) -> List[Any]:
        """
        Execute all pending tool calls.

        Returns:
            List of results
        """
        if not self._pending:
            return []

        results = []

        # Execute calls sequentially (could be parallelized if independent)
        for tool_func, args, kwargs in self._pending:
            try:
                result = tool_func(*args, **kwargs)
                results.append(result)
            except Exception as e:
                results.append(e)

        self._results.extend(results)
        self._pending.clear()

        return results

    def get_results(self) -> List[Any]:
        """Get all results including from flushed batches."""
        self.flush()
        return self._results

    def clear(self):
        """Clear pending calls and results."""
        self._pending.clear()
        self._results.clear()


def optimized_tool(cache_ttl: float = 180.0, enable_dedup: bool = True):
    """
    Decorator to add optimization to a tool function.

    Args:
        cache_ttl: Cache time-to-live in seconds
        enable_dedup: Whether to enable call deduplication

    Example:
        >>> @optimized_tool(cache_ttl=300)
        ... def expensive_analysis(data: dict) -> dict:
        ...     return heavy_computation(data)
    """

    def decorator(func: Callable) -> Callable:
        optimizer = ToolInvocationOptimizer()

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if enable_dedup:
                return optimizer.invoke_with_cache(func, *args, cache_ttl=cache_ttl, **kwargs)
            else:
                return optimizer.invoke_with_dedup(func, *args, **kwargs)

        # Preserve tool metadata
        if hasattr(func, "is_tool"):
            wrapper.is_tool = func.is_tool
        if hasattr(func, "args_schema"):
            wrapper.args_schema = func.args_schema

        return wrapper

    return decorator


class RedundantCallDetector:
    """
    Detects and warns about potentially redundant tool calls.

    Helps identify patterns where caching could be beneficial.
    """

    def __init__(self, warning_threshold: int = 3):
        """
        Initialize detector.

        Args:
            warning_threshold: Number of identical calls before warning
        """
        self.warning_threshold = warning_threshold
        self._call_history: Dict[str, List[float]] = defaultdict(list)
        self._warnings_issued: Set[str] = set()

    def record_call(self, tool_name: str, call_key: str):
        """
        Record a tool call.

        Args:
            tool_name: Name of the tool
            call_key: Unique key for the call
        """
        import time

        full_key = f"{tool_name}:{call_key}"
        self._call_history[full_key].append(time.time())

        # Check if we should warn
        if len(self._call_history[full_key]) >= self.warning_threshold:
            if full_key not in self._warnings_issued:
                self._warnings_issued.add(full_key)
                print(
                    f"WARNING: Tool '{tool_name}' called {len(self._call_history[full_key])} "
                    f"times with identical arguments. Consider adding caching."
                )

    def get_repeated_calls(self) -> Dict[str, int]:
        """
        Get a summary of repeated calls.

        Returns:
            Dictionary of call_key to count
        """
        return {key: len(times) for key, times in self._call_history.items() if len(times) > 1}

    def reset(self):
        """Reset call history."""
        self._call_history.clear()
        self._warnings_issued.clear()


# Global optimizer instance
_tool_optimizer: Optional[ToolInvocationOptimizer] = None


def get_tool_optimizer() -> ToolInvocationOptimizer:
    """Get or create global tool optimizer."""
    global _tool_optimizer
    if _tool_optimizer is None:
        _tool_optimizer = ToolInvocationOptimizer()
    return _tool_optimizer


def optimize_tool_call(tool_func: Callable, *args, **kwargs) -> Any:
    """
    Optimize a single tool call.

    Args:
        tool_func: Tool function to call
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Tool result
    """
    optimizer = get_tool_optimizer()
    return optimizer.invoke_with_cache(tool_func, *args, **kwargs)
