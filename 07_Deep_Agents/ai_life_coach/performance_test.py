#!/usr/bin/env python3
"""
Performance Test Suite for AI Life Coach

This script establishes baseline performance metrics and identifies bottlenecks.
It profiles agent execution times, tool calls, and memory access patterns.
"""

import time
import cProfile
import pstats
import io
import json
import statistics
from contextlib import contextmanager
from typing import Dict, List, Any, Tuple
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.main import create_life_coach
from src.performance import get_profiler, reset_profiler, profile, run_cprofile


class PerformanceTestSuite:
    """Comprehensive performance testing for AI Life Coach system."""

    def __init__(self):
        self.results = {}
        self.coach = None

    def setup(self):
        """Initialize the AI Life Coach system."""
        print("🔧 Initializing AI Life Coach system...")
        start_time = time.perf_counter()

        try:
            self.coach = create_life_coach()
            setup_time = time.perf_counter() - start_time
            print(f"✅ System initialized in {setup_time:.2f}s")
            self.results["setup_time"] = setup_time
        except Exception as e:
            print(f"❌ Failed to initialize system: {e}")
            raise

    def test_simple_query(self) -> Dict[str, Any]:
        """Test performance of simple queries."""
        print("\n📊 Testing simple query performance...")

        simple_queries = [
            "Hello! Can you introduce yourself?",
            "What can you help me with?",
            "How do you work?",
            "Tell me about your capabilities.",
            "What are your main features?",
        ]

        query_times = []

        for i, query in enumerate(simple_queries, 1):
            print(f"  Query {i}/{len(simple_queries)}: {query[:40]}...")

            start_time = time.perf_counter()
            try:
                result = self.coach.invoke({"messages": [{"role": "user", "content": query}]})
                query_time = time.perf_counter() - start_time
                query_times.append(query_time)

                # Extract response content
                if result and "messages" in result and result["messages"]:
                    response_length = len(result["messages"][-1].get("content", ""))
                else:
                    response_length = 0

                print(f"    ⏱️  {query_time:.2f}s ({response_length} chars)")

            except Exception as e:
                print(f"    ❌ Failed: {e}")
                query_times.append(float("inf"))  # Mark as failed

        # Calculate statistics
        valid_times = [t for t in query_times if t != float("inf")]

        return {
            "total_queries": len(simple_queries),
            "successful_queries": len(valid_times),
            "failed_queries": len(query_times) - len(valid_times),
            "times": valid_times,
            "avg_time": statistics.mean(valid_times) if valid_times else 0,
            "min_time": min(valid_times) if valid_times else 0,
            "max_time": max(valid_times) if valid_times else 0,
            "median_time": statistics.median(valid_times) if valid_times else 0,
            "target_met": statistics.mean(valid_times) < 30.0 if valid_times else False,
        }

    def test_complex_query(self) -> Dict[str, Any]:
        """Test performance of complex multi-domain queries."""
        print("\n📊 Testing complex query performance...")

        complex_queries = [
            "I need help with my career development and financial planning. Can you create a comprehensive plan?",
            "I'm struggling with work-life balance, relationships, and my wellness. What should I prioritize?",
            "Help me create a 6-month plan covering career growth, financial stability, and relationship improvement.",
            "I want to switch careers, improve my finances, and work on my health. Where do I start?",
            "Analyze my current situation and create integrated recommendations for all life domains.",
        ]

        query_times = []

        for i, query in enumerate(complex_queries, 1):
            print(f"  Complex Query {i}/{len(complex_queries)}: {query[:50]}...")

            start_time = time.perf_counter()
            try:
                result = self.coach.invoke({"messages": [{"role": "user", "content": query}]})
                query_time = time.perf_counter() - start_time
                query_times.append(query_time)

                print(f"    ⏱️  {query_time:.2f}s")

            except Exception as e:
                print(f"    ❌ Failed: {e}")
                query_times.append(float("inf"))

        valid_times = [t for t in query_times if t != float("inf")]

        return {
            "total_queries": len(complex_queries),
            "successful_queries": len(valid_times),
            "failed_queries": len(query_times) - len(valid_times),
            "times": valid_times,
            "avg_time": statistics.mean(valid_times) if valid_times else 0,
            "min_time": min(valid_times) if valid_times else 0,
            "max_time": max(valid_times) if valid_times else 0,
            "median_time": statistics.median(valid_times) if valid_times else 0,
        }

    def test_memory_performance(self) -> Dict[str, Any]:
        """Test memory access performance."""
        print("\n📊 Testing memory access performance...")

        # Test user profile access
        memory_times = []

        # Test multiple profile lookups
        for i in range(10):
            start_time = time.perf_counter()
            try:
                # This would typically access user memory
                result = self.coach.invoke(
                    {
                        "messages": [
                            {
                                "role": "user",
                                "content": f"Can you remember my name is TestUser{i} and I like programming?",
                            }
                        ]
                    }
                )
                memory_time = time.perf_counter() - start_time
                memory_times.append(memory_time)
                print(f"    Memory test {i + 1}/10: {memory_time:.3f}s")
            except Exception as e:
                print(f"    ❌ Memory test {i + 1} failed: {e}")

        valid_times = [t for t in memory_times if t != float("inf")]

        return {
            "access_tests": len(memory_times),
            "successful_access": len(valid_times),
            "avg_access_time": statistics.mean(valid_times) if valid_times else 0,
            "min_access_time": min(valid_times) if valid_times else 0,
            "max_access_time": max(valid_times) if valid_times else 0,
        }

    def test_tool_call_performance(self) -> Dict[str, Any]:
        """Test individual tool call performance."""
        print("\n📊 Testing tool call performance...")

        tool_queries = [
            "Create a career development plan for me.",  # Should trigger career tools
            "Help me create a budget.",  # Should trigger finance tools
            "Give me relationship advice.",  # Should trigger relationship tools
            "Create a wellness plan for me.",  # Should trigger wellness tools
            "Set some goals for the next month.",  # Should trigger planning tools
        ]

        tool_times = []

        for i, query in enumerate(tool_queries, 1):
            print(f"  Tool test {i}/{len(tool_queries)}: {query[:40]}...")

            start_time = time.perf_counter()
            try:
                result = self.coach.invoke({"messages": [{"role": "user", "content": query}]})
                tool_time = time.perf_counter() - start_time
                tool_times.append(tool_time)
                print(f"    ⏱️  {tool_time:.2f}s")

            except Exception as e:
                print(f"    ❌ Failed: {e}")
                tool_times.append(float("inf"))

        valid_times = [t for t in tool_times if t != float("inf")]

        return {
            "tool_tests": len(tool_queries),
            "successful_tool_calls": len(valid_times),
            "avg_tool_time": statistics.mean(valid_times) if valid_times else 0,
            "min_tool_time": min(valid_times) if valid_times else 0,
            "max_tool_time": max(valid_times) if valid_times else 0,
        }

    def run_detailed_profiling(self) -> str:
        """Run detailed profiling on a representative query."""
        print("\n🔍 Running detailed profiling...")

        test_query = "I need help with career planning and financial advice."

        result, profile_stats = run_cprofile(
            self.coach.invoke, {"messages": [{"role": "user", "content": test_query}]}
        )

        return profile_stats

    def run_all_tests(self) -> Dict[str, Any]:
        """Run complete performance test suite."""
        print("🚀 Starting AI Life Coach Performance Test Suite")
        print("=" * 60)

        reset_profiler()

        # Run all tests
        self.setup()

        with profile("simple_queries"):
            self.results["simple_queries"] = self.test_simple_query()

        with profile("complex_queries"):
            self.results["complex_queries"] = self.test_complex_query()

        with profile("memory_performance"):
            self.results["memory_performance"] = self.test_memory_performance()

        with profile("tool_call_performance"):
            self.results["tool_call_performance"] = self.test_tool_call_performance()

        with profile("detailed_profiling"):
            self.results["detailed_profile"] = self.run_detailed_profiling()

        # Generate performance summary
        summary = self.generate_summary()
        self.results["summary"] = summary

        return self.results

    def generate_summary(self) -> Dict[str, Any]:
        """Generate performance summary and recommendations."""
        simple = self.results.get("simple_queries", {})
        complex = self.results.get("complex_queries", {})
        memory = self.results.get("memory_performance", {})
        tools = self.results.get("tool_call_performance", {})

        summary = {
            "performance_targets_met": True,
            "bottlenecks": [],
            "recommendations": [],
            "key_metrics": {},
        }

        # Check simple query target (< 30 seconds)
        if simple.get("avg_time", 0) > 30:
            summary["performance_targets_met"] = False
            summary["bottlenecks"].append("Simple queries exceed 30s target")
            summary["recommendations"].append("Optimize response generation for simple queries")

        # Check complex query performance
        if complex.get("avg_time", 0) > 120:  # 2 minutes for complex queries
            summary["performance_targets_met"] = False
            summary["bottlenecks"].append("Complex queries take too long")
            summary["recommendations"].append(
                "Implement parallel subagent execution for complex queries"
            )

        # Check memory performance
        if memory.get("avg_access_time", 0) > 0.1:  # 100ms for memory access
            summary["bottlenecks"].append("Memory access is slow")
            summary["recommendations"].append("Implement better caching strategies")

        # Check tool call performance
        if tools.get("avg_tool_time", 0) > 5:  # 5s for tool calls
            summary["bottlenecks"].append("Tool calls are slow")
            summary["recommendations"].append(
                "Optimize tool implementation and reduce redundant calls"
            )

        # Key metrics
        summary["key_metrics"] = {
            "setup_time_s": self.results.get("setup_time", 0),
            "simple_query_avg_s": simple.get("avg_time", 0),
            "simple_query_success_rate": simple.get("successful_queries", 0)
            / max(simple.get("total_queries", 1), 1),
            "complex_query_avg_s": complex.get("avg_time", 0),
            "complex_query_success_rate": complex.get("successful_queries", 0)
            / max(complex.get("total_queries", 1), 1),
            "memory_avg_access_ms": memory.get("avg_access_time", 0) * 1000,
            "tool_call_avg_s": tools.get("avg_tool_time", 0),
            "tool_call_success_rate": tools.get("successful_tool_calls", 0)
            / max(tools.get("tool_tests", 1), 1),
        }

        return summary

    def save_report(self, filepath: str = "performance_test_report.json"):
        """Save detailed performance report."""
        with open(filepath, "w") as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"\n📄 Performance report saved to: {filepath}")

    def print_summary(self):
        """Print performance test summary."""
        summary = self.results.get("summary", {})
        key_metrics = summary.get("key_metrics", {})

        print("\n" + "=" * 60)
        print("🎯 PERFORMANCE TEST SUMMARY")
        print("=" * 60)

        print(f"✅ Performance Targets Met: {summary.get('performance_targets_met', False)}")

        print(f"\n📊 Key Metrics:")
        print(f"  • Setup Time: {key_metrics.get('setup_time_s', 0):.2f}s")
        print(f"  • Simple Query Avg: {key_metrics.get('simple_query_avg_s', 0):.2f}s")
        print(f"  • Simple Query Success: {key_metrics.get('simple_query_success_rate', 0):.1%}")
        print(f"  • Complex Query Avg: {key_metrics.get('complex_query_avg_s', 0):.2f}s")
        print(f"  • Complex Query Success: {key_metrics.get('complex_query_success_rate', 0):.1%}")
        print(f"  • Memory Access Avg: {key_metrics.get('memory_avg_access_ms', 0):.1f}ms")
        print(f"  • Tool Call Avg: {key_metrics.get('tool_call_avg_s', 0):.2f}s")
        print(f"  • Tool Call Success: {key_metrics.get('tool_call_success_rate', 0):.1%}")

        bottlenecks = summary.get("bottlenecks", [])
        if bottlenecks:
            print(f"\n⚠️  Bottlenecks Identified:")
            for bottleneck in bottlenecks:
                print(f"  • {bottleneck}")

        recommendations = summary.get("recommendations", [])
        if recommendations:
            print(f"\n💡 Recommendations:")
            for rec in recommendations:
                print(f"  • {rec}")

        print("=" * 60)


def main():
    """Main entry point for performance testing."""
    test_suite = PerformanceTestSuite()

    try:
        results = test_suite.run_all_tests()
        test_suite.print_summary()
        test_suite.save_report()

        # Print performance profiler report
        profiler = get_profiler()
        print("\n" + profiler.generate_report())

    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
