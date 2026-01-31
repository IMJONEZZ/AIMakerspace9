"""
Simple Demo Script for Multi-Agent Wellness System

This script demonstrates the basic functionality of the wellness system.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import create_wellness_system


def main():
    """Run the demo."""
    print("=" * 60)
    print("Multi-Agent Wellness System Demo")
    print("=" * 60)

    # Initialize the system
    print("\nInitializing wellness system...")
    system = create_wellness_system()

    # Demo user setup
    demo_user_id = "demo_user_1"
    print(f"\nSetting up demo user: {demo_user_id}")
    system.set_user_profile(
        demo_user_id,
        {
            "name": "Demo User",
            "age": 35,
            "goals": ["lose weight", "improve overall fitness"],
            "conditions": ["knee injury"],
        },
    )

    # Example queries
    queries = [
        "I want to lose weight but I have a knee injury. What exercises can I do?",
        "What should I eat to support my weight loss goals?",
        "I'm having trouble sleeping well. Any tips?",
    ]

    # Process queries
    print("\n" + "=" * 60)
    print("Processing Queries")
    print("=" * 60)

    for i, query in enumerate(queries, 1):
        print(f"\n--- Query {i} ---")
        print(f"User: {query}")

        result = system.handle_query(demo_user_id, query)

        print(f"\nAgent: {result['agent_used']}")
        print(f"Reasoning: {result['routing_reasoning']}")
        print(f"\nResponse:")
        print(result["response"])

    # Show system statistics
    print("\n" + "=" * 60)
    print("System Statistics")
    print("=" * 60)

    stats = system.get_system_stats()
    print(f"\nMemory Stats:")
    for key, value in stats["memory"].items():
        print(f"  {key}: {value}")

    print(f"\nEpisode Stats:")
    for agent, agent_stats in stats["episodes"].items():
        print(f"  {agent}:")
        for stat_key, stat_value in agent_stats.items():
            print(f"    {stat_key}: {stat_value}")

    print("\nDemo complete!")


if __name__ == "__main__":
    main()
