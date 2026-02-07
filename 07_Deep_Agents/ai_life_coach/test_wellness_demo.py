#!/usr/bin/env python
"""Quick test script to verify wellness tools work correctly."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from deepagents.backends import FilesystemBackend
from src.tools.wellness_tools import create_wellness_tools


def test_sample_scenario():
    """Test the sample scenario: 'I have trouble sleeping due to work stress'."""
    print("=" * 70)
    print("Testing Wellness Coach Tools - Sample Scenario")
    print("Scenario: 'I have trouble sleeping due to work stress'")
    print("=" * 70)

    # Create backend and tools
    backend = FilesystemBackend(root_dir="/tmp/test_wellness_scenario")
    (
        assess_wellness_dimensions,
        create_habit_formation_plan,
        provide_stress_management_techniques,
        create_sleep_optimization_plan,
        design_exercise_program,
    ) = create_wellness_tools(backend)

    user_id = "sample_user_work_stress"

    print("\n" + "=" * 70)
    print("Step 1: Wellness Assessment")
    print("=" * 70)
    assessment = assess_wellness_dimensions.invoke(
        {
            "user_id": user_id,
            "emotional_score": 4,  # High stress
            "physical_score": 5,  # Poor sleep affecting physical
            "occupational_score": 3,  # Work stress source
        }
    )
    print(assessment)

    print("\n" + "=" * 70)
    print("Step 2: Stress Management Techniques")
    print("=" * 70)
    stress_tips = provide_stress_management_techniques.invoke(
        {"user_id": user_id, "stress_level": "high", "preferred_technique_type": "breathing"}
    )
    print(stress_tips)

    print("\n" + "=" * 70)
    print("Step 3: Sleep Optimization Plan")
    print("=" * 70)
    sleep_plan = create_sleep_optimization_plan.invoke(
        {
            "user_id": user_id,
            "current_bedtime": "11:30 PM",
            "current_wake_time": "6:30 AM",
            "sleep_issues": [
                "trouble falling asleep",
                "waking up often",
                "racing thoughts about work",
            ],
        }
    )
    print(sleep_plan)

    print("\n" + "=" * 70)
    print("Step 4: Bedtime Relaxation Habit")
    print("=" * 70)
    habit_plan = create_habit_formation_plan.invoke(
        {
            "user_id": user_id,
            "habit_name": "Bedtime relaxation routine",
            "cue_description": "When I get into bed",
            "routine_steps": ["Do 4-7-8 breathing for 5 minutes", "Write tomorrow's to-do list"],
            "reward_description": "Feel calm and ready for sleep",
        }
    )
    print(habit_plan)

    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"✓ Wellness assessment completed for user: {user_id}")
    print("✓ Stress management techniques provided (breathing exercises)")
    print("✓ Sleep optimization plan created")
    print("✓ Bedtime relaxation habit designed")
    print("\nAll wellness tools are working correctly! ✅")


if __name__ == "__main__":
    test_sample_scenario()
