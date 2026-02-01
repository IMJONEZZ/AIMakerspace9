"""
Quick health check test to verify the system builds and runs.
This is minimal output version for faster verification.
"""

import sys
from pathlib import Path

# Add parent and src to path for proper imports
sys.path.insert(0, str(Path(__file__).parent))
from src.wellness_system import create_wellness_system


def main():
    print("=== System Health Check ===")

    # Initialize system (knowledge base is loaded automatically)
    print("\n[1/3] Initializing wellness system...")
    system = create_wellness_system()

    # Create test user
    print("[2/3] Creating test user...")
    test_user_id = "test_health_check"
    system.set_user_profile(
        test_user_id, {"name": "Test User", "goals": ["weight loss"]}
    )

    # Test routing and response
    print("[3/3] Testing query routing and response...")
    test_queries = [
        "I need help with exercise",
        "What should I eat for breakfast?",
    ]

    print("\n--- Test Results ---")
    all_passed = True

    for query in test_queries:
        print(f"\nQuery: {query}")
        try:
            result = system.handle_query(test_user_id, query)
            print(f"  ✓ Agent: {result['agent_used']}")
            print(f"  ✓ Confidence: {result['confidence']:.2f}")
            print(f"  ✓ Success: {result['success']}")

            # Just show first line of response
            response_lines = result["response"].split("\n")[:2]
            print(f"  ✓ Response preview: {response_lines[0][:100]}...")

        except Exception as e:
            print(f"  ✗ FAILED: {e}")
            all_passed = False

    # Get stats
    print("\n--- System Stats ---")
    stats = system.get_system_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Final verdict
    if all_passed:
        print("\n✓ All health checks PASSED")
        return 0
    else:
        print("\n✗ Some health checks FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
