"""
Demo script for Relationship Coach Specialist.

This demonstrates the relationship coaching tools in action with real-world scenarios.
Run: python -m demo_relationship_coach
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.tools.relationship_tools import create_relationship_tools
from src.config import get_backend, config


def demo_communication_style_analysis():
    """Demo: Analyze communication style."""
    print("\n" + "=" * 70)
    print("DEMO 1: Communication Style Analysis")
    print("=" * 70)

    backend = get_backend()
    tools = create_relationship_tools(backend=backend)
    analyze_communication_style = tools[0]

    scenario = "I struggle with saying 'no' to my coworkers when they ask for help"

    print(f"\nScenario: {scenario}")
    print("\nAnalyzing communication patterns...")

    result = analyze_communication_style.invoke(
        {
            "user_id": "demo_user",
            "scenario_descriptions": [
                "I often say 'yes' when I want to say 'no'",
                "When people criticize me, I shut down",
                "I rarely express my true feelings to others",
            ],
            "relationship_context": "workplace",
        }
    )

    print("\n" + result)


def demo_boundary_setting():
    """Demo: Create boundary setting plan."""
    print("\n" + "=" * 70)
    print("DEMO 2: Boundary Setting Plan")
    print("=" * 70)

    backend = get_backend()
    tools = create_relationship_tools(backend=backend)
    create_boundary_setting_plan = tools[1]

    print("\nScenario: 'I struggle with setting boundaries at work'")

    result = create_boundary_setting_plan.invoke(
        {
            "user_id": "demo_user",
            "boundary_areas": ["work hours", "emotional energy"],
            "relationship_type": "workplace",
        }
    )

    print("\n" + result)


def demo_dear_man_technique():
    """Demo: Apply DEAR MAN technique for conflict resolution."""
    print("\n" + "=" * 70)
    print("DEMO 3: DEAR MAN Conflict Resolution")
    print("=" * 70)

    backend = get_backend()
    tools = create_relationship_tools(backend=backend)
    apply_dear_man_technique = tools[2]

    print("\nScenario: Conflict with partner about personal space")

    result = apply_dear_man_technique.invoke(
        {
            "user_id": "demo_user",
            "situation_description": "My partner always checks my phone without asking",
            "goal": "To establish privacy and trust",
        }
    )

    print("\n" + result)


def demo_relationship_quality_assessment():
    """Demo: Assess relationship quality."""
    print("\n" + "=" * 70)
    print("DEMO 4: Relationship Quality Assessment")
    print("=" * 70)

    backend = get_backend()
    tools = create_relationship_tools(backend=backend)
    assess_relationship_quality = tools[3]

    print("\nScenario: Evaluating current relationship health")

    result = assess_relationship_quality.invoke(
        {
            "user_id": "demo_user",
            "relationship_type": "romantic",
            "ratings": {
                "trust": 5,
                "communication": 4,
                "support": 7,
                "growth": 6,
                "intimacy": 5,
                "conflict_resolution": 3,
            },
        }
    )

    print("\n" + result)


def demo_social_connection_plan():
    """Demo: Develop social connection plan."""
    print("\n" + "=" * 70)
    print("DEMO 5: Social Connection Plan")
    print("=" * 70)

    backend = get_backend()
    tools = create_relationship_tools(backend=backend)
    develop_social_connection_plan = tools[4]

    print("\nScenario: Moving to a new city, want to make friends")

    result = develop_social_connection_plan.invoke(
        {
            "user_id": "demo_user",
            "current_situation": "I just moved to a new city and don't know anyone. I work from home so I rarely see people.",
            "goals": ["make new friends", "improve conversation skills"],
        }
    )

    print("\n" + result)


def main():
    """Run all demos."""
    print("\n" + "=" * 70)
    print("AI Life Coach - Relationship Coach Specialist Demo")
    print("=" * 70)

    try:
        # Initialize environment
        config.initialize_environment()

        # Run each demo
        demo_communication_style_analysis()
        input("\nPress Enter to continue to next demo...")

        demo_boundary_setting()
        input("\nPress Enter to continue to next demo...")

        demo_dear_man_technique()
        input("\nPress Enter to continue to next demo...")

        demo_relationship_quality_assessment()
        input("\nPress Enter to continue to next demo...")

        demo_social_connection_plan()

        print("\n" + "=" * 70)
        print("Demo Complete!")
        print("=" * 70)
        print("\nAll relationship coaching tools demonstrated successfully.")
        print("These tools are integrated with the Relationship Specialist subagent.")

    except Exception as e:
        print(f"\nError running demo: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
