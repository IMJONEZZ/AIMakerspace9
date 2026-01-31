"""
Test Scenarios for Multi-Agent Wellness System

This file contains comprehensive test scenarios including:
1. Multi-turn conversations demonstrating memory persistence
2. Cross-agent learning demonstrations
3. Various user profiles and conditions
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import create_wellness_system


def test_scenario_1_weight_loss_with_injury():
    """
    Test Scenario 1: User with injury wants to lose weight

    Demonstrates:
    - Router correctly routing to exercise agent
    - Exercise agent considering injury in recommendations
    - Cross-agent learning (nutrition agent learns about the injury)
    """
    print("\n" + "=" * 80)
    print("TEST SCENARIO 1: Weight Loss with Knee Injury")
    print("=" * 80)

    system = create_wellness_system()

    # Set up user profile with injury
    user_id = "test_user_1"
    system.set_user_profile(
        user_id,
        {
            "name": "Alex",
            "age": 32,
            "goals": ["lose weight", "improve fitness"],
            "conditions": ["knee injury"],
        },
    )

    print(f"\n👤 User Profile: {system.get_user_profile(user_id)}")

    # Turn 1: Ask about exercise
    print("\n--- Turn 1 ---")
    query1 = "I want to lose weight but I have a knee injury. What exercises can I do?"
    print(f"User: {query1}")

    result1 = system.handle_query(user_id, query1)
    print(f"\nAgent: {result1['agent_used']}")
    print(f"Response: {result1['response']}")

    # Turn 2: Ask about nutrition (should remember the injury context)
    print("\n--- Turn 2 ---")
    query2 = "What should I eat to support my weight loss?"
    print(f"User: {query2}")

    result2 = system.handle_query(user_id, query2)
    print(f"\nAgent: {result2['agent_used']}")
    print(f"Response: {result2['response']}")

    # Check if nutrition response considers the knee injury
    print("\n✓ Cross-Agent Learning Check:")
    if "injury" in result2["response"].lower() or "knee" in result2["response"].lower():
        print("  ✅ Nutrition agent learned about the knee injury from Exercise agent!")
    else:
        print("  ⚠️  Nutrition agent may not have learned about the knee injury")

    # Show system stats
    print("\n📊 System Statistics:")
    stats = system.get_system_stats()
    for agent, agent_stats in stats["episodes"].items():
        print(f"  {agent}: {agent_stats['total']} episodes")


def test_scenario_2_comprehensive_wellness():
    """
    Test Scenario 2: Comprehensive wellness journey

    Demonstrates:
    - Multi-domain queries (exercise, nutrition, sleep)
    - Memory persistence across conversation
    - Personalized recommendations based on profile
    """
    print("\n" + "=" * 80)
    print("TEST SCENARIO 2: Comprehensive Wellness Journey")
    print("=" * 80)

    system = create_wellness_system()

    # Set up user profile
    user_id = "test_user_2"
    system.set_user_profile(
        user_id,
        {
            "name": "Jordan",
            "age": 28,
            "goals": ["improve overall health", "reduce stress"],
            "conditions": [],
        },
    )

    print(f"\n👤 User Profile: {system.get_user_profile(user_id)}")

    # Multi-turn conversation
    queries = [
        "What's a good morning routine for energy?",
        "I'm not sleeping well, what should I do?",
        "What exercises can help reduce stress?",
    ]

    responses = system.multi_turn_conversation(user_id, queries)

    print("\n✓ Summary:")
    agents_used = set(r["agent_used"] for r in responses)
    print(f"  Agents used: {', '.join(agents_used)}")
    print(f"  Total turns: {len(responses)}")


def test_scenario_3_cross_agent_learning_demo():
    """
    Test Scenario 3: Explicit cross-agent learning demonstration

    Demonstrates:
    - Episode storage and retrieval
    - Cross-agent episode access
    - Knowledge transfer between agents
    """
    print("\n" + "=" * 80)
    print("TEST SCENARIO 3: Cross-Agent Learning Demonstration")
    print("=" * 80)

    system = create_wellness_system()

    # User with asthma
    user_id = "test_user_3"
    system.set_user_profile(
        user_id,
        {
            "name": "Casey",
            "age": 45,
            "goals": ["improve cardiovascular health"],
            "conditions": ["asthma"],
        },
    )

    print(f"\n👤 User Profile: {system.get_user_profile(user_id)}")

    # Exercise agent handles asthma-appropriate workout
    print("\n--- Step 1: Exercise Agent learns about asthma-friendly workouts ---")
    query1 = "I have asthma. What exercises are safe for me?"
    print(f"User: {query1}")

    result1 = system.handle_query(user_id, query1)
    print(f"\nAgent: {result1['agent_used']}")
    print(f"Response: {result1['response']}")

    # Check the stored episode
    print("\n--- Step 2: Checking stored episodes ---")
    from src import AGENT_EXERCISE

    exercise_episodes = system.memory.get_agent_episodes(AGENT_EXERCISE, limit=3)
    print(f"Exercise Agent Episodes: {len(exercise_episodes)}")
    for i, ep in enumerate(exercise_episodes[-1:], 1):
        print(f"  {i}. Situation: {ep.get('situation', 'N/A')[:80]}...")

    # Search cross-agent episodes for asthma context
    print("\n--- Step 3: Cross-Agent Episode Discovery ---")
    cross_episodes = system.memory.get_cross_agent_episodes(
        query="asthma exercise", limit_per_agent=1
    )
    print(f"Cross-agent episodes found for 'asthma exercise':")
    for agent, eps in cross_episodes.items():
        print(f"  {agent}: {len(eps)} episode(s)")

    # Nutrition agent should be able to access this context
    print("\n--- Step 4: Nutrition Agent accessing cross-agent knowledge ---")
    query2 = "What diet plan supports cardiovascular health?"
    print(f"User: {query2}")

    result2 = system.handle_query(user_id, query2)
    print(f"\nAgent: {result2['agent_used']}")
    print(f"Response: {result2['response']}")

    # Check if response considers asthma
    print("\n✓ Cross-Agent Learning Verification:")
    if "asthma" in result2["response"].lower():
        print("  ✅ Nutrition agent accessed asthma information from Exercise agent!")
    else:
        print("  ℹ️  Nutrition agent response doesn't explicitly mention asthma")


def test_scenario_4_multiple_users():
    """
    Test Scenario 4: Multiple users with different profiles

    Demonstrates:
    - User profile isolation
    - Personalized recommendations for each user
    - System handling multiple concurrent users
    """
    print("\n" + "=" * 80)
    print("TEST SCENARIO 4: Multiple Users with Different Profiles")
    print("=" * 80)

    system = create_wellness_system()

    # Set up different users
    users = {
        "user_alice": {
            "name": "Alice",
            "age": 25,
            "goals": ["build muscle"],
            "conditions": [],
        },
        "user_bob": {
            "name": "Bob",
            "age": 55,
            "goals": ["maintain mobility"],
            "conditions": ["arthritis", "high blood pressure"],
        },
    }

    for user_id, profile in users.items():
        system.set_user_profile(user_id, profile)
        print(f"\n👤 {profile['name']} ({user_id}):")
        for key, value in profile.items():
            if isinstance(value, list):
                print(f"  {key}: {', '.join(str(v) for v in value)}")
            else:
                print(f"  {key}: {value}")

    # Ask same question to both users
    query = "What exercises do you recommend for me?"

    print("\n--- Same Query, Different Responses ---")
    for user_id in users.keys():
        print(f"\n{user_id} asks: {query}")
        result = system.handle_query(user_id, query)
        print(f"Routed to: {result['agent_used']}")
        print(f"Response preview: {result['response'][:150]}...")

    # Verify profile isolation
    print("\n✓ Profile Isolation Verification:")
    alice_profile = system.get_user_profile("user_alice")
    bob_profile = system.get_user_profile("user_bob")

    assert alice_profile["name"] == "Alice"
    assert bob_profile["name"] == "Bob"
    print("  ✅ User profiles are properly isolated!")


def test_scenario_5_memory_persistence():
    """
    Test Scenario 5: Memory persistence across sessions

    Demonstrates:
    - Short-term memory (thread_id) for conversation history
    - Long-term memory (user profile and episodes)
    """
    print("\n" + "=" * 80)
    print("TEST SCENARIO 5: Memory Persistence")
    print("=" * 80)

    system = create_wellness_system()

    user_id = "test_user_5"
    thread_id_1 = "session_morning"
    thread_id_2 = "session_evening"

    # Session 1 (morning)
    print("\n--- Session 1: Morning ---")
    system.set_user_profile(
        user_id,
        {
            "name": "Taylor",
            "age": 30,
            "goals": ["reduce stress"],
            "conditions": [],
        },
    )

    query_morning = "I'm feeling stressed. What can I do?"
    print(f"User: {query_morning}")

    result_morning = system.handle_query(user_id, query_morning, thread_id_1)
    print(f"Response: {result_morning['response'][:150]}...")

    # Session 2 (evening) - different thread, same user
    print("\n--- Session 2: Evening (Different Thread) ---")
    query_evening = "What should I eat tonight?"
    print(f"User: {query_evening}")

    result_evening = system.handle_query(user_id, query_evening, thread_id_2)
    print(f"Response: {result_evening['response'][:150]}...")

    # Verify long-term memory (profile) persists
    print("\n✓ Memory Persistence Verification:")
    profile = system.get_user_profile(user_id)
    assert profile["name"] == "Taylor"
    print(f"  ✅ Long-term memory: Profile persisted (Name: {profile['name']})")

    # Check episodes
    stats = system.get_system_stats()
    total_episodes = sum(
        agent_stats["total"] for agent_stats in stats["episodes"].values()
    )
    print(f"  ✅ Long-term memory: {total_episodes} episodes stored")


def run_all_tests():
    """Run all test scenarios."""
    print("\n" + "=" * 80)
    print("RUNNING ALL TEST SCENARIOS")
    print("=" * 80)

    try:
        test_scenario_1_weight_loss_with_injury()
        input("\nPress Enter to continue to next scenario...")

        test_scenario_2_comprehensive_wellness()
        input("\nPress Enter to continue to next scenario...")

        test_scenario_3_cross_agent_learning_demo()
        input("\nPress Enter to continue to next scenario...")

        test_scenario_4_multiple_users()
        input("\nPress Enter to continue to next scenario...")

        test_scenario_5_memory_persistence()

        print("\n" + "=" * 80)
        print("ALL TEST SCENARIOS COMPLETED SUCCESSFULLY! ✅")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
