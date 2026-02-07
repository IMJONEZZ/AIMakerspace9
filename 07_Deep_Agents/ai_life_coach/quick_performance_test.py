#!/usr/bin/env python3
"""
Quick Performance Test for AI Life Coach

Simplified test to establish baseline performance metrics.
"""

import time
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_initialization():
    """Test system initialization time."""
    print("🔧 Testing system initialization...")

    start_time = time.perf_counter()
    try:
        from src.main import create_life_coach

        coach = create_life_coach()
        init_time = time.perf_counter() - start_time
        print(f"✅ System initialized in {init_time:.2f}s")
        return coach, init_time
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return None, 0


def test_simple_query(coach):
    """Test a simple query performance."""
    print("\n📊 Testing simple query...")

    query = "Hello! Can you introduce yourself briefly?"

    start_time = time.perf_counter()
    try:
        result = coach.invoke({"messages": [{"role": "user", "content": query}]})
        query_time = time.perf_counter() - start_time

        # Extract response length
        if result and "messages" in result and result["messages"]:
            response_length = len(result["messages"][-1].get("content", ""))
        else:
            response_length = 0

        print(f"✅ Query completed in {query_time:.2f}s ({response_length} chars)")
        return query_time, response_length
    except Exception as e:
        print(f"❌ Query failed: {e}")
        return 0, 0


def test_tool_query(coach):
    """Test a tool-based query."""
    print("\n📊 Testing tool-based query...")

    query = "Can you help me create a simple goal?"

    start_time = time.perf_counter()
    try:
        result = coach.invoke({"messages": [{"role": "user", "content": query}]})
        query_time = time.perf_counter() - start_time

        if result and "messages" in result and result["messages"]:
            response_length = len(result["messages"][-1].get("content", ""))
        else:
            response_length = 0

        print(f"✅ Tool query completed in {query_time:.2f}s ({response_length} chars)")
        return query_time, response_length
    except Exception as e:
        print(f"❌ Tool query failed: {e}")
        return 0, 0


def main():
    """Run quick performance test."""
    print("🚀 Quick Performance Test - AI Life Coach")
    print("=" * 50)

    # Test initialization
    coach, init_time = test_initialization()

    if not coach:
        print("❌ Cannot continue without successful initialization")
        return

    # Test queries
    simple_time, simple_length = test_simple_query(coach)
    tool_time, tool_length = test_tool_query(coach)

    # Summary
    print("\n" + "=" * 50)
    print("📋 PERFORMANCE SUMMARY")
    print("=" * 50)
    print(f"Initialization Time: {init_time:.2f}s")
    print(f"Simple Query Time: {simple_time:.2f}s")
    print(f"Tool Query Time: {tool_time:.2f}s")
    print(f"Simple Query Target (<30s): {'✅ PASS' if simple_time < 30 else '❌ FAIL'}")
    print(f"Tool Query Target (<5s): {'✅ PASS' if tool_time < 5 else '❌ FAIL'}")

    # Save results
    results = {
        "timestamp": time.time(),
        "initialization_time": init_time,
        "simple_query": {
            "time": simple_time,
            "response_length": simple_length,
            "target_met": simple_time < 30,
        },
        "tool_query": {
            "time": tool_time,
            "response_length": tool_length,
            "target_met": tool_time < 5,
        },
    }

    with open("quick_performance_report.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n📄 Results saved to: quick_performance_report.json")


if __name__ == "__main__":
    main()
