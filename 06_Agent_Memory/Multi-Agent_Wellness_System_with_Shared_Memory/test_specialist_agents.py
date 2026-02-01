"""
Test each specialist agent independently.
This ensures all three agents can handle queries correctly.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.wellness_system import create_wellness_system


def test_specialist_agents():
    """Test all three specialist agents independently."""
    print("=== Specialist Agent Test ===")

    try:
        # Initialize system
        print("\n[1/4] Initializing wellness system...")
        system = create_wellness_system()

        # Create test user
        print("[2/4] Creating test user...")
        test_user_id = "test_specialist_agents"
        system.set_user_profile(
            test_user_id, {"name": "Test User", "goals": ["wellness"]}
        )

        # Test each agent with domain-specific queries
        test_cases = [
            ("exercise", "I need a workout plan for weight loss"),
            ("nutrition", "What foods help with muscle recovery?"),
            ("sleep", "How can I improve my sleep quality?"),
        ]

        print("[3/4] Testing each specialist agent...")
        all_passed = True

        for expected_agent, query in test_cases:
            print(f"\n  Testing {expected_agent.upper()} agent...")
            print(f"  Query: {query}")

            try:
                result = system.handle_query(test_user_id, query)

                # Check routing
                actual_agent = result["agent_used"]
                if actual_agent == expected_agent:
                    print(f"  ✓ Routed correctly to {actual_agent}")
                else:
                    print(f"  ✗ Expected {expected_agent}, got {actual_agent}")
                    all_passed = False

                # Check response was generated
                if result["success"]:
                    print(f"  ✓ Response generated successfully")
                else:
                    print(f"  ✗ Response generation failed")
                    all_passed = False

            except Exception as e:
                print(f"  ✗ FAILED: {e}")
                all_passed = False

        # Get final stats
        print("\n[4/4] Checking episode storage...")
        stats = system.get_system_stats()

        for agent in ["exercise_agent", "nutrition_agent", "sleep_agent"]:
            episode_count = stats["episodes"][agent]["total"]
            if episode_count > 0:
                print(f"  ✓ {agent}: {episode_count} episodes stored")
            else:
                print(f"  ✗ {agent}: No episodes stored!")
                all_passed = False

        # Final verdict
        if all_passed:
            print("\n✓ All specialist agents PASSED")
            return True
        else:
            print("\n✗ Some tests FAILED")
            return False

    except Exception as e:
        print(f"\n✗ Test suite FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_specialist_agents()
    sys.exit(0 if success else 1)
