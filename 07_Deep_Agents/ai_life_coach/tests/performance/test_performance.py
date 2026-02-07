"""
Performance test suite for AI Life Coach.

This module provides comprehensive performance tests to:
1. Measure baseline performance
2. Verify optimization improvements
3. Ensure performance targets are met
"""

import time
import unittest
from typing import Any, Dict, List
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from performance import (
    get_profiler,
    reset_profiler,
    profile,
    get_cache_manager,
    reset_cache_manager,
    parallel_map,
    parallel_specialists,
    OptimizedMemoryManager,
    create_optimized_memory_manager,
    ToolInvocationOptimizer,
)


class TestPerformanceTargets(unittest.TestCase):
    """Test that performance targets are met."""

    def setUp(self):
        """Reset profiler and cache before each test."""
        reset_profiler()
        reset_cache_manager()
        self.profiler = get_profiler()

    def test_cache_response_time(self):
        """
        Test that cached operations complete quickly.

        Target: Cache operations should complete in < 1ms
        """
        cache = get_cache_manager()

        # Warm up
        cache.set_profile("user_1", {"name": "Test User"})
        cache.get_profile("user_1")

        # Measure cached read
        start = time.perf_counter()
        for _ in range(100):
            cache.get_profile("user_1")
        elapsed = time.perf_counter() - start

        avg_time = (elapsed / 100) * 1000  # Convert to ms

        print(f"\nCache read avg time: {avg_time:.3f}ms")
        self.assertLess(avg_time, 1.0, "Cache read should be < 1ms")

    def test_parallel_execution_speedup(self):
        """
        Test that parallel execution provides speedup.

        Target: Parallel execution should be faster than sequential
        """

        def slow_task(x):
            time.sleep(0.1)  # 100ms sleep
            return x * 2

        items = list(range(4))

        # Sequential execution
        start = time.perf_counter()
        seq_results = [slow_task(x) for x in items]
        seq_time = time.perf_counter() - start

        # Parallel execution
        start = time.perf_counter()
        par_results = parallel_map(slow_task, items, max_workers=4)
        par_time = time.perf_counter() - start

        print(f"\nSequential: {seq_time:.3f}s, Parallel: {par_time:.3f}s")
        print(f"Speedup: {seq_time / par_time:.2f}x")

        # Parallel should be faster (at least 2x with 4 workers)
        self.assertLess(par_time, seq_time * 0.6, "Parallel should be significantly faster")
        self.assertEqual(seq_results, par_results, "Results should be identical")


class TestCachingEffectiveness(unittest.TestCase):
    """Test caching functionality and effectiveness."""

    def setUp(self):
        reset_cache_manager()
        self.cache = get_cache_manager()

    def test_profile_caching(self):
        """Test that profiles are cached correctly."""
        profile = {"user_id": "test_123", "name": "Test User"}

        # First set
        self.cache.set_profile("test_123", profile)

        # Should retrieve from cache
        cached = self.cache.get_profile("test_123")
        self.assertEqual(cached, profile)

        # Stats should show hit
        stats = self.cache.get_all_stats()
        self.assertGreater(stats["profile_cache"]["hits"], 0)

    def test_cache_invalidation(self):
        """Test cache invalidation."""
        profile = {"user_id": "test_123", "name": "Test User"}

        self.cache.set_profile("test_123", profile)
        self.assertIsNotNone(self.cache.get_profile("test_123"))

        self.cache.invalidate_user("test_123")
        self.assertIsNone(self.cache.get_profile("test_123"))

    def test_goals_caching(self):
        """Test that goals are cached correctly."""
        goals = [
            {"goal_id": "g1", "title": "Goal 1"},
            {"goal_id": "g2", "title": "Goal 2"},
        ]

        self.cache.set_goals("user_1", goals)
        cached = self.cache.get_goals("user_1")

        self.assertEqual(cached, goals)

    def test_tool_result_caching(self):
        """Test that tool results are cached."""
        result = {"calculation": 42, "data": "test"}

        self.cache.set_tool_result("test_tool", "arg_hash_123", result)
        cached = self.cache.get_tool_result("test_tool", "arg_hash_123")

        self.assertEqual(cached, result)


class TestProfiler(unittest.TestCase):
    """Test profiling functionality."""

    def setUp(self):
        reset_profiler()
        self.profiler = get_profiler()

    def test_section_profiling(self):
        """Test that sections are profiled correctly."""
        with profile("test_section"):
            time.sleep(0.01)

        summary = self.profiler.get_summary()
        self.assertIn("test_section", summary)
        self.assertEqual(summary["test_section"]["count"], 1)

    def test_multiple_calls(self):
        """Test profiling multiple calls."""
        for _ in range(5):
            with profile("repeated_section"):
                time.sleep(0.001)

        summary = self.profiler.get_summary()
        self.assertEqual(summary["repeated_section"]["count"], 5)

    def test_top_slowest(self):
        """Test getting slowest sections."""
        # Profile sections with different durations
        with profile("fast_section"):
            time.sleep(0.001)

        with profile("slow_section"):
            time.sleep(0.05)

        slowest = self.profiler.get_top_slowest(2)
        self.assertEqual(slowest[0][0], "slow_section")

    def test_report_generation(self):
        """Test that performance report is generated."""
        with profile("test_op"):
            time.sleep(0.01)

        report = self.profiler.generate_report()
        self.assertIn("AI LIFE COACH - PERFORMANCE PROFILE REPORT", report)
        self.assertIn("test_op", report)


class TestParallelExecution(unittest.TestCase):
    """Test parallel execution utilities."""

    def test_parallel_map(self):
        """Test parallel map function."""

        def square(x):
            return x * x

        items = [1, 2, 3, 4, 5]
        results = parallel_map(square, items, max_workers=2)

        # Results may be out of order due to parallel execution
        expected = [1, 4, 9, 16, 25]
        self.assertEqual(sorted(results), sorted(expected))

    def test_parallel_specialists(self):
        """Test parallel specialist execution."""

        def career_func(**ctx):
            return {"advice": "Career advice", "domain": "career"}

        def finance_func(**ctx):
            return {"advice": "Finance advice", "domain": "finance"}

        specialists = {
            "career": career_func,
            "finance": finance_func,
        }

        context = {"user_id": "test_123"}

        results = parallel_specialists(specialists, context, max_workers=2, timeout=5.0)

        self.assertIn("career", results)
        self.assertIn("finance", results)
        self.assertEqual(results["career"]["domain"], "career")
        self.assertEqual(results["finance"]["domain"], "finance")


class TestToolOptimization(unittest.TestCase):
    """Test tool invocation optimization."""

    def setUp(self):
        self.optimizer = ToolInvocationOptimizer()
        reset_cache_manager()

    def test_tool_caching(self):
        """Test that tool results are cached."""
        call_count = [0]

        def test_tool(x):
            call_count[0] += 1
            return x * 2

        # First call
        result1 = self.optimizer.invoke_with_cache(test_tool, 5)
        self.assertEqual(result1, 10)
        self.assertEqual(call_count[0], 1)

        # Second call with same args - should use cache
        result2 = self.optimizer.invoke_with_cache(test_tool, 5)
        self.assertEqual(result2, 10)
        self.assertEqual(call_count[0], 1)  # No additional call


class TestMemoryOptimization(unittest.TestCase):
    """Test memory access optimizations."""

    def test_lazy_loader(self):
        """Test lazy loading functionality."""
        from performance.memory_optimizer import LazyLoader

        call_count = [0]

        def loader():
            call_count[0] += 1
            return [1, 2, 3, 4, 5]

        lazy = LazyLoader(loader)

        # Loader should not be called yet
        self.assertEqual(call_count[0], 0)

        # Access data
        data = lazy.data
        self.assertEqual(call_count[0], 1)
        self.assertEqual(data, [1, 2, 3, 4, 5])

        # Second access should not reload
        data2 = lazy.data
        self.assertEqual(call_count[0], 1)
        self.assertEqual(list(lazy), [1, 2, 3, 4, 5])


def run_performance_benchmark():
    """
    Run performance benchmarks and print results.

    This is a comprehensive benchmark that measures:
    - Cache performance
    - Parallel execution speedup
    - Tool optimization effectiveness
    """
    print("\n" + "=" * 70)
    print("AI LIFE COACH - PERFORMANCE BENCHMARK")
    print("=" * 70)

    reset_profiler()
    reset_cache_manager()

    profiler = get_profiler()
    cache = get_cache_manager()

    results = {
        "cache_read_ms": 0,
        "cache_hit_rate": 0,
        "parallel_speedup": 0,
        "tool_call_reduction": 0,
    }

    # Benchmark 1: Cache Performance
    print("\n1. Cache Performance")
    print("-" * 40)

    # Set up cache
    cache.set_profile("benchmark_user", {"name": "Benchmark", "data": "x" * 1000})

    # Warm up
    cache.get_profile("benchmark_user")

    # Measure 1000 reads
    start = time.perf_counter()
    for _ in range(1000):
        cache.get_profile("benchmark_user")
    elapsed = time.perf_counter() - start

    avg_ms = (elapsed / 1000) * 1000
    results["cache_read_ms"] = avg_ms

    stats = cache.get_all_stats()
    results["cache_hit_rate"] = stats["profile_cache"]["hit_rate_percent"]

    print(f"  Average cache read time: {avg_ms:.4f}ms")
    print(f"  Cache hit rate: {results['cache_hit_rate']:.1f}%")
    print(f"  Target: < 1ms read time - {'PASS' if avg_ms < 1.0 else 'FAIL'}")

    # Benchmark 2: Parallel Execution Speedup
    print("\n2. Parallel Execution Speedup")
    print("-" * 40)

    # Use I/O-bound task simulation (more realistic for agent systems)
    def io_task(n):
        # Simulate I/O-bound work (like API calls or file operations)
        time.sleep(0.05)  # 50ms sleep
        return n * 2

    items = list(range(8))

    # Sequential
    start = time.perf_counter()
    seq_results = [io_task(x) for x in items]
    seq_time = time.perf_counter() - start

    # Parallel
    start = time.perf_counter()
    par_results = parallel_map(io_task, items, max_workers=4)
    par_time = time.perf_counter() - start

    speedup = seq_time / par_time if par_time > 0 else 0
    results["parallel_speedup"] = speedup

    print(f"  Task type: I/O-bound (simulating API calls)")
    print(f"  Items processed: {len(items)}")
    print(f"  Sequential time: {seq_time:.3f}s")
    print(f"  Parallel time: {par_time:.3f}s")
    print(f"  Speedup: {speedup:.2f}x")
    print(f"  Target: > 2x speedup - {'PASS' if speedup > 2.0 else 'FAIL'}")
    if speedup < 2.0:
        print("  Note: Speedup depends on workload type and available cores")

    # Benchmark 3: Tool Call Optimization
    print("\n3. Tool Call Optimization")
    print("-" * 40)

    optimizer = ToolInvocationOptimizer()
    call_count = [0]

    def expensive_tool(x):
        call_count[0] += 1
        time.sleep(0.01)  # Simulate work
        return x * 2

    # Without caching (simulate)
    for i in range(10):
        expensive_tool(5)
    calls_without_cache = call_count[0]

    # With caching
    call_count[0] = 0
    for i in range(10):
        optimizer.invoke_with_cache(expensive_tool, 5)
    calls_with_cache = call_count[0]

    reduction = (1 - (calls_with_cache / calls_without_cache)) * 100
    results["tool_call_reduction"] = reduction

    print(f"  Calls without cache: {calls_without_cache}")
    print(f"  Calls with cache: {calls_with_cache}")
    print(f"  Reduction: {reduction:.0f}%")
    print(f"  Target: > 80% reduction - {'PASS' if reduction > 80 else 'FAIL'}")

    # Summary
    print("\n" + "=" * 70)
    print("BENCHMARK SUMMARY")
    print("=" * 70)

    all_pass = (
        results["cache_read_ms"] < 1.0
        and results["parallel_speedup"] > 2.0
        and results["tool_call_reduction"] > 80
    )

    print(
        f"  Cache read time: {results['cache_read_ms']:.4f}ms - "
        f"{'PASS' if results['cache_read_ms'] < 1.0 else 'FAIL'}"
    )
    print(
        f"  Parallel speedup: {results['parallel_speedup']:.2f}x - "
        f"{'PASS' if results['parallel_speedup'] > 2.0 else 'FAIL'}"
    )
    print(
        f"  Tool call reduction: {results['tool_call_reduction']:.0f}% - "
        f"{'PASS' if results['tool_call_reduction'] > 80 else 'FAIL'}"
    )
    print(f"\n  Overall: {'ALL TESTS PASSED' if all_pass else 'SOME TESTS FAILED'}")

    return results


def run_all_tests():
    """Run all performance tests."""
    # Run unit tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestPerformanceTargets))
    suite.addTests(loader.loadTestsFromTestCase(TestCachingEffectiveness))
    suite.addTests(loader.loadTestsFromTestCase(TestProfiler))
    suite.addTests(loader.loadTestsFromTestCase(TestParallelExecution))
    suite.addTests(loader.loadTestsFromTestCase(TestToolOptimization))
    suite.addTests(loader.loadTestsFromTestCase(TestMemoryOptimization))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Run benchmarks
    benchmark_results = run_performance_benchmark()

    return result.wasSuccessful(), benchmark_results


if __name__ == "__main__":
    success, benchmark = run_all_tests()
    sys.exit(0 if success else 1)
