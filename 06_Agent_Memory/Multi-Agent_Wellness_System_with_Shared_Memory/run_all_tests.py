#!/usr/bin/env python3
"""
Comprehensive test runner for Multi-Agent Wellness System.
Runs all verification tests in sequence and provides a summary.
"""

import sys
import subprocess
from pathlib import Path


def run_test(test_name, test_file):
    """Run a single test and return the result."""
    print(f"\n{'=' * 60}")
    print(f"Running: {test_name}")
    print("=" * 60)

    result = subprocess.run(
        ["uv", "run", "python", test_file],
        capture_output=False,
    )

    return result.returncode == 0


def main():
    """Run all tests and provide summary."""
    print("=" * 60)
    print("Multi-Agent Wellness System - Test Suite")
    print("=" * 60)

    # Define tests
    tests = [
        ("System Health Check", "test_health_check.py"),
        ("Dashboard Load Test", "test_dashboard.py"),
        ("Cross-Agent Learning Test", "test_cross_agent.py"),
    ]

    results = {}

    # Run each test
    for test_name, test_file in tests:
        test_path = Path(__file__).parent / test_file
        if not test_path.exists():
            print(f"\n✗ Test file not found: {test_file}")
            results[test_name] = False
            continue

        success = run_test(test_name, str(test_path))
        results[test_name] = success

    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    for test_name, success in results.items():
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{test_name}: {status}")

    # Overall result
    all_passed = all(results.values())

    print("\n" + "=" * 60)
    if all_passed:
        print("Overall: ✓ ALL TESTS PASSED")
    else:
        print("Overall: ✗ SOME TESTS FAILED")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
