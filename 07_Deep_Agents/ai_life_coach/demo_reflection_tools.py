"""
Demo script for Reflection Prompt Tools.

This demonstrates the key functionality of the reflection prompt system:
1. Dynamic prompt generation based on context
2. Saving reflections with sentiment analysis
3. Retrieving reflection history
4. Extracting insights from multiple reflections
5. Milestone and setback trigger prompts
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import get_backend
from tools.reflection_tools import (
    create_reflection_tools,
    select_prompts_by_context,
    trigger_milestone_prompts,
    trigger_setback_prompts,
)


def demo_dynamic_prompt_selection():
    """Demo: Generate prompts based on different contexts."""
    print("\n" + "=" * 70)
    print("DEMO 1: Dynamic Prompt Selection")
    print("=" * 70)

    # High mood, good progress
    print("\n--- Context: High Mood + Good Progress ---")
    selected = select_prompts_by_context(
        mood_state={"happiness": 8, "stress": 2, "energy": 7, "motivation": 9},
        progress_score=0.8,
    )
    print(f"Celebration prompts: {len(selected.get('celebration', []))}")
    print(f"Challenge prompts: {len(selected.get('challenge', []))}")

    # Low mood, poor progress
    print("\n--- Context: Low Mood + Poor Progress ---")
    selected = select_prompts_by_context(
        mood_state={"happiness": 3, "stress": 8, "energy": 2, "motivation": 4},
        progress_score=0.3,
    )
    print(f"Celebration prompts: {len(selected.get('celebration', []))}")
    print(f"Challenge prompts: {len(selected.get('challenge', []))}")


def demo_milestone_triggers():
    """Demo: Generate milestone celebration prompts."""
    print("\n" + "=" * 70)
    print("DEMO 2: Milestone Trigger Prompts")
    print("=" * 70)

    # Goal achieved
    print("\n--- Milestone: Goal Achieved ---")
    prompts = trigger_milestone_prompts("goal_achieved", {"goal_name": "Learn Python"})
    print(f"Generated {len(prompts)} milestone prompts:")
    for i, prompt in enumerate(prompts[:2], 1):
        print(f"\n{i}. {prompt}")

    # Major breakthrough
    print("\n--- Milestone: Major Breakthrough ---")
    prompts = trigger_milestone_prompts("major_breakthrough", {})
    print(f"Generated {len(prompts)} milestone prompts:")
    for i, prompt in enumerate(prompts[:2], 1):
        print(f"\n{i}. {prompt}")


def demo_setback_triggers():
    """Demo: Generate setback recovery prompts."""
    print("\n" + "=" * 70)
    print("DEMO 3: Setback Trigger Prompts")
    print("=" * 70)

    # Setback occurred
    print("\n--- Setback: Missed Deadline ---")
    prompts = trigger_setback_prompts("setback_occurred", {"challenge_name": "Missed deadline"})
    print(f"Generated {len(prompts)} setback prompts:")
    for i, prompt in enumerate(prompts[:2], 1):
        print(f"\n{i}. {prompt}")

    # Recurring pattern
    print("\n--- Setback: Recurring Pattern ---")
    prompts = trigger_setback_prompts("pattern_recurring", {"pattern_name": "Procrastination"})
    print(f"Generated {len(prompts)} setback prompts:")
    for i, prompt in enumerate(prompts[:2], 1):
        print(f"\n{i}. {prompt}")


def demo_full_workflow():
    """Demo: Complete workflow with tool functions."""
    print("\n" + "=" * 70)
    print("DEMO 4: Complete Workflow with Tools")
    print("=" * 70)

    # Initialize backend and tools
    backend = get_backend()
    (
        generate_prompts,
        save_response,
        get_history,
        extract_insights,
        trigger_milestone,
        trigger_setback,
    ) = create_reflection_tools(backend=backend)

    # Generate weekly prompts
    print("\n--- Step 1: Generate Weekly Reflection Prompts ---")
    result = generate_prompts.invoke(
        {
            "user_id": "demo_user",
            "mood_state": {"happiness": 7, "stress": 4},
            "progress_score": 0.75,
        }
    )
    print(result[:500] + "...")

    # Save a reflection response
    print("\n--- Step 2: Save Reflection Response ---")
    result = save_response.invoke(
        {
            "user_id": "demo_user",
            "prompt_category": "celebration",
            "prompt_text": "What achievement are you proud of?",
            "response_text": "I completed my project ahead of schedule and learned a lot about time management. I feel proud of my growth.",
        }
    )
    print(result[:400] + "...")

    # Save another reflection
    print("\n--- Step 3: Save Another Reflection ---")
    result = save_response.invoke(
        {
            "user_id": "demo_user",
            "prompt_category": "learning",
            "prompt_text": "What did you learn this week?",
            "response_text": "I learned that I'm more resilient than I thought. Even when things got difficult, I kept going and found solutions.",
        }
    )
    print(result[:400] + "...")

    # Get reflection history
    print("\n--- Step 4: Retrieve Reflection History ---")
    result = get_history.invoke(
        {
            "user_id": "demo_user",
            "days": 30,
        }
    )
    print(result[:400] + "...")

    # Extract insights
    print("\n--- Step 5: Extract Insights from Reflections ---")
    result = extract_insights.invoke(
        {
            "user_id": "demo_user",
            "days": 30,
        }
    )
    print(result[:500] + "...")

    # Trigger milestone reflection
    print("\n--- Step 6: Trigger Milestone Reflection ---")
    result = trigger_milestone.invoke(
        {
            "user_id": "demo_user",
            "milestone_type": "goal_achieved",
            "context": {"goal_name": "Complete Python Course"},
        }
    )
    print(result[:400] + "...")

    # Trigger setback reflection
    print("\n--- Step 7: Trigger Setback Reflection ---")
    result = trigger_setback.invoke(
        {
            "user_id": "demo_user",
            "setback_type": "setback_occurred",
            "context": {"challenge_name": "Missed deadline"},
        }
    )
    print(result[:400] + "...")

    print("\n" + "=" * 70)
    print("✅ Demo Complete!")
    print("=" * 70)


def main():
    """Run all demos."""
    try:
        # Initialize environment
        from config import config

        config.initialize_environment()
        print("\n✓ Environment initialized")

        # Run demos
        demo_dynamic_prompt_selection()
        demo_milestone_triggers()
        demo_setback_triggers()
        demo_full_workflow()

    except Exception as e:
        print(f"\n❌ Error running demos: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
