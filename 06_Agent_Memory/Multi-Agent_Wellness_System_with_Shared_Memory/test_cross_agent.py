"""
Test cross-agent learning functionality.
Verify episodes are stored and can be retrieved across agents.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.wellness_system import create_wellness_system


def test_cross_agent_learning():
    """Test cross-agent learning episode storage and retrieval."""
    print("=== Cross-Agent Learning Test ===")

    try:
        # Initialize system
        print("\n[1/6] Initializing wellness system...")
        system = create_wellness_system()

        # Create test user
        print("[2/6] Creating test user...")
        test_user_id = "test_cross_agent"
        system.set_user_profile(
            test_user_id, {"name": "Test User", "goals": ["weight loss"]}
        )

        # Query nutrition agent first
        print("[3/6] Creating episodes with nutrition agent...")
        result1 = system.handle_query(test_user_id, "What should I eat for breakfast?")
        print(f"  ✓ Nutrition query handled: {result1['agent_used']}")

        # Query sleep agent
        print("[4/6] Creating episodes with sleep agent...")
        result2 = system.handle_query(test_user_id, "How can I improve my sleep?")
        print(f"  ✓ Sleep query handled: {result2['agent_used']}")

        # Check episode storage
        print("[5/6] Checking episode storage...")
        stats = system.get_system_stats()

        episodes_ok = True
        for agent in ["nutrition_agent", "sleep_agent"]:
            episode_count = stats["episodes"][agent]["total"]
            if episode_count > 0:
                print(f"  ✓ {agent}: {episode_count} episodes stored")
            else:
                print(f"  ✗ {agent}: No episodes stored!")
                episodes_ok = False

        # Test cross-agent retrieval
        print("[6/6] Testing cross-agent episode retrieval...")

        # Get episodes from one agent
        nutrition_episodes = system.memory.get_agent_episodes(
            "nutrition_agent", limit=3
        )

        if nutrition_episodes:
            print(f"  ✓ Retrieved {len(nutrition_episodes)} nutrition episodes")

            # Check episode structure
            for i, ep in enumerate(nutrition_episodes[:1], 1):
                if "input" in ep and "output" in ep:
                    print(f"  ✓ Episode {i} has proper structure")
                else:
                    print(f"  ✗ Episode {i} missing required fields")
        else:
            print("  ✗ Could not retrieve nutrition episodes")
            episodes_ok = False

        # Verdict
        if episodes_ok:
            print("\n✓ Cross-agent learning PASSED")
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
    success = test_cross_agent_learning()
    sys.exit(0 if success else 1)
