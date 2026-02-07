"""
Performance profiling and monitoring module for AI Life Coach.

This module provides profiling utilities to identify bottlenecks in agent execution,
tool calls, and memory access patterns.

Features:
- Agent execution profiling
- Tool call performance tracking
- Memory access pattern analysis
- Performance report generation
"""

import cProfile
import pstats
import time
import functools
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple
from collections import defaultdict
import io


class PerformanceProfiler:
    """
    Centralized performance profiler for AI Life Coach.

    Tracks execution times for:
    - Agent operations
    - Tool calls
    - Memory access
    - Subagent coordination
    """

    def __init__(self):
        self.metrics: Dict[str, List[float]] = defaultdict(list)
        self.call_counts: Dict[str, int] = defaultdict(int)
        self.start_times: Dict[str, float] = {}
        self.enabled = True

    def enable(self):
        """Enable profiling."""
        self.enabled = True

    def disable(self):
        """Disable profiling."""
        self.enabled = False

    @contextmanager
    def profile_section(self, section_name: str):
        """
        Context manager to profile a section of code.

        Args:
            section_name: Name of the section being profiled

        Example:
            >>> with profiler.profile_section("memory_access"):
            ...     result = memory_manager.get_profile(user_id)
        """
        if not self.enabled:
            yield
            return

        start_time = time.perf_counter()
        try:
            yield
        finally:
            elapsed = time.perf_counter() - start_time
            self.metrics[section_name].append(elapsed)
            self.call_counts[section_name] += 1

    def record_timing(self, section_name: str, elapsed: float):
        """Record a timing directly."""
        if self.enabled:
            self.metrics[section_name].append(elapsed)
            self.call_counts[section_name] += 1

    def get_summary(self) -> Dict[str, Dict[str, float]]:
        """
        Get performance summary statistics.

        Returns:
            Dictionary with statistics for each tracked section:
            - count: Number of calls
            - total_time: Total time spent
            - avg_time: Average time per call
            - min_time: Minimum time
            - max_time: Maximum time
        """
        summary = {}
        for section, times in self.metrics.items():
            if times:
                summary[section] = {
                    "count": len(times),
                    "total_time": sum(times),
                    "avg_time": sum(times) / len(times),
                    "min_time": min(times),
                    "max_time": max(times),
                }
        return summary

    def get_top_slowest(self, n: int = 10) -> List[Tuple[str, float]]:
        """
        Get the top N slowest sections by average time.

        Args:
            n: Number of sections to return

        Returns:
            List of (section_name, avg_time) tuples, sorted by avg_time descending
        """
        summary = self.get_summary()
        sorted_sections = sorted(
            [(name, stats["avg_time"]) for name, stats in summary.items()],
            key=lambda x: x[1],
            reverse=True,
        )
        return sorted_sections[:n]

    def reset(self):
        """Reset all metrics."""
        self.metrics.clear()
        self.call_counts.clear()
        self.start_times.clear()

    def generate_report(self) -> str:
        """
        Generate a formatted performance report.

        Returns:
            Multi-line string with performance statistics
        """
        lines = [
            "=" * 70,
            "AI LIFE COACH - PERFORMANCE PROFILE REPORT",
            f"Generated: {datetime.now().isoformat()}",
            "=" * 70,
            "",
        ]

        summary = self.get_summary()

        if not summary:
            lines.append("No performance data collected.")
            return "\n".join(lines)

        # Overall statistics
        total_calls = sum(stats["count"] for stats in summary.values())
        total_time = sum(stats["total_time"] for stats in summary.values())

        lines.extend(
            [
                f"Total Tracked Operations: {total_calls}",
                f"Total Execution Time: {total_time:.4f}s",
                "",
                "Performance by Section:",
                "-" * 70,
                f"{'Section':<40} {'Calls':>8} {'Avg (ms)':>10} {'Total (ms)':>12}",
                "-" * 70,
            ]
        )

        # Sort by total time (most impactful first)
        sorted_sections = sorted(summary.items(), key=lambda x: x[1]["total_time"], reverse=True)

        for section_name, stats in sorted_sections:
            avg_ms = stats["avg_time"] * 1000
            total_ms = stats["total_time"] * 1000
            lines.append(
                f"{section_name:<40} {stats['count']:>8} {avg_ms:>10.2f} {total_ms:>12.2f}"
            )

        lines.extend(
            [
                "-" * 70,
                "",
                "Top Bottlenecks (by average time per call):",
                "-" * 70,
            ]
        )

        for section_name, avg_time in self.get_top_slowest(5):
            lines.append(f"  {section_name}: {avg_time * 1000:.2f}ms avg")

        lines.append("=" * 70)

        return "\n".join(lines)


# Global profiler instance
_profiler: Optional[PerformanceProfiler] = None


def get_profiler() -> PerformanceProfiler:
    """Get or create the global profiler instance."""
    global _profiler
    if _profiler is None:
        _profiler = PerformanceProfiler()
    return _profiler


def reset_profiler():
    """Reset the global profiler."""
    global _profiler
    _profiler = PerformanceProfiler()


@contextmanager
def profile(section_name: str):
    """
    Convenience context manager using global profiler.

    Example:
        >>> with profile("database_query"):
        ...     results = db.query()
    """
    profiler = get_profiler()
    with profiler.profile_section(section_name):
        yield


def timed(func: Callable) -> Callable:
    """
    Decorator to time function execution.

    Args:
        func: Function to time

    Returns:
        Wrapped function that tracks execution time

    Example:
        >>> @timed
        ... def slow_function():
        ...     time.sleep(1)
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        profiler = get_profiler()
        section_name = f"{func.__module__}.{func.__name__}"

        with profiler.profile_section(section_name):
            return func(*args, **kwargs)

    return wrapper


def run_cprofile(func: Callable, *args, **kwargs) -> Tuple[Any, str]:
    """
    Run a function under cProfile and return results with stats.

    Args:
        func: Function to profile
        *args: Positional arguments for function
        **kwargs: Keyword arguments for function

    Returns:
        Tuple of (function_result, profile_stats_string)
    """
    profiler = cProfile.Profile()

    try:
        result = profiler.runcall(func, *args, **kwargs)
    except Exception as e:
        raise e
    finally:
        # Generate stats
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s)
        ps.strip_dirs()
        ps.sort_stats("cumulative")
        ps.print_stats(20)  # Top 20 functions
        stats_output = s.getvalue()

    return result, stats_output


class ToolPerformanceTracker:
    """
    Track performance of individual tools.

    Wraps tools to track their execution times and call counts.
    """

    def __init__(self, profiler: Optional[PerformanceProfiler] = None):
        self.profiler = profiler or get_profiler()
        self.tool_timings: Dict[str, List[float]] = defaultdict(list)

    def wrap_tool(self, tool_func: Callable, tool_name: Optional[str] = None) -> Callable:
        """
        Wrap a tool function to track its performance.

        Args:
            tool_func: Tool function to wrap
            tool_name: Optional name override

        Returns:
            Wrapped tool function
        """
        name = tool_name or getattr(tool_func, "__name__", "unknown_tool")

        @functools.wraps(tool_func)
        def wrapper(*args, **kwargs):
            section_name = f"tool.{name}"
            with self.profiler.profile_section(section_name):
                return tool_func(*args, **kwargs)

        # Preserve tool metadata
        if hasattr(tool_func, "is_tool"):
            wrapper.is_tool = tool_func.is_tool
        if hasattr(tool_func, "args_schema"):
            wrapper.args_schema = tool_func.args_schema

        return wrapper

    def wrap_tools(self, tools: List[Callable]) -> List[Callable]:
        """Wrap a list of tools."""
        return [self.wrap_tool(tool) for tool in tools]


class MemoryAccessOptimizer:
    """
    Optimize memory access patterns with intelligent caching.

    Tracks frequently accessed data and suggests caching strategies.
    """

    def __init__(self, profiler: Optional[PerformanceProfiler] = None):
        self.profiler = profiler or get_profiler()
        self.access_patterns: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {
                "count": 0,
                "last_access": None,
                "total_time": 0.0,
            }
        )

    def track_access(self, namespace: str, key: str, access_time: float):
        """Track a memory access."""
        access_key = f"{namespace}:{key}"
        pattern = self.access_patterns[access_key]
        pattern["count"] += 1
        pattern["last_access"] = time.time()
        pattern["total_time"] += access_time

    def get_frequently_accessed(self, min_accesses: int = 3) -> List[Tuple[str, int]]:
        """
        Get keys that are accessed frequently.

        Args:
            min_accesses: Minimum number of accesses to be considered frequent

        Returns:
            List of (access_key, count) tuples
        """
        frequent = [
            (key, data["count"])
            for key, data in self.access_patterns.items()
            if data["count"] >= min_accesses
        ]
        return sorted(frequent, key=lambda x: x[1], reverse=True)

    def get_caching_recommendations(self) -> List[Dict[str, Any]]:
        """
        Generate recommendations for what to cache.

        Returns:
            List of recommendations with priority scores
        """
        recommendations = []

        for key, data in self.access_patterns.items():
            if data["count"] >= 3:  # Accessed at least 3 times
                avg_time = data["total_time"] / data["count"]
                # Priority = frequency * avg_time
                priority = data["count"] * avg_time

                recommendations.append(
                    {
                        "key": key,
                        "access_count": data["count"],
                        "avg_access_time_ms": avg_time * 1000,
                        "priority_score": priority,
                        "recommendation": f"Cache '{key}' - accessed {data['count']} times",
                    }
                )

        return sorted(recommendations, key=lambda x: x["priority_score"], reverse=True)


def print_performance_report():
    """Print the current performance report."""
    profiler = get_profiler()
    print(profiler.generate_report())


def save_performance_report(filepath: str):
    """Save performance report to file."""
    profiler = get_profiler()
    report = profiler.generate_report()
    with open(filepath, "w") as f:
        f.write(report)
    print(f"Performance report saved to: {filepath}")
