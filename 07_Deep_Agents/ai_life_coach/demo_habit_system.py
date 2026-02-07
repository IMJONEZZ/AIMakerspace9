"""
Demo script for Habit Tracking System.

This script demonstrates the comprehensive habit tracking capabilities
based on the Atomic Habits framework by James Clear.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.config import config
from src.tools.habit_tools import create_habit_tools


def run_demo():
    """Run the habit tracking demo."""
    print("=" * 70)
    print("AI Life Coach - Habit Tracking System Demo")
    print("Based on Atomic Habits by James Clear")
    print("=" * 70)

    # Initialize configuration
    config.initialize_environment()

    # Create habit tools with initialized backend
    from src.config import get_backend

    tools = create_habit_tools(get_backend())
    (
        create_habit,
        log_habit_completion,
        get_habit_streaks,
        calculate_habit_strength_score,
        get_habit_stacking_suggestions,
        get_habits_by_domain,
        review_habit,
        update_habit,
        delete_habit,
        list_habits,
    ) = tools

    user_id = "demo_user"

    # ================================================================
    # Part 1: Create Habits with Habit Loop Structure
    # ================================================================
    print("\n" + "=" * 70)
    print("PART 1: Creating Habits with Trigger-Action-Reward Structure")
    print("=" * 70)

    # Habit 1: Morning Meditation (Health domain)
    print("\n🧘 Creating: Morning Meditation")
    result = create_habit.invoke(
        {
            "user_id": user_id,
            "name": "Morning Meditation",
            "domain": "mindfulness",
            "frequency": "daily",
            "cue": "After I sit on my meditation cushion",
            "action": "Meditate for 10 minutes using the breath",
            "reward": "Feel calm, centered, and ready for the day",
        }
    )
    print(result)

    # Habit 2: Daily Exercise (Health domain)
    print("\n🏃 Creating: Daily Exercise")
    result = create_habit.invoke(
        {
            "user_id": user_id,
            "name": "30-Minute Exercise",
            "domain": "health",
            "frequency": "daily",
            "cue": "After I put on my workout clothes",
            "action": "Exercise for 30 minutes (cardio or strength)",
            "reward": "Feel energized and accomplished",
        }
    )
    print(result)

    # Habit 3: Reading (Personal Growth domain)
    print("\n📚 Creating: Daily Reading")
    result = create_habit.invoke(
        {
            "user_id": user_id,
            "name": "Read 10 Pages",
            "domain": "personal_growth",
            "frequency": "daily",
            "cue": "After I finish dinner",
            "action": "Read 10 pages of a book",
            "reward": "Gain knowledge and relax",
            "stack_after": "Dinner",
        }
    )
    print(result)

    # ================================================================
    # Part 2: Get Habit Stacking Suggestions
    # ================================================================
    print("\n" + "=" * 70)
    print("PART 2: Habit Stacking Suggestions")
    print("=" * 70)

    print("\n💡 Getting stacking suggestions for a new habit...")
    result = get_habit_stacking_suggestions.invoke(
        {
            "user_id": user_id,
            "new_habit_name": "Drink 8 Glasses of Water",
            "new_habit_domain": "health",
        }
    )
    print(result)

    # ================================================================
    # Part 3: List All Habits
    # ================================================================
    print("\n" + "=" * 70)
    print("PART 3: Listing All Habits")
    print("=" * 70)

    result = list_habits.invoke({"user_id": user_id})
    print(result)

    # ================================================================
    # Part 4: Get Habits by Domain
    # ================================================================
    print("\n" + "=" * 70)
    print("PART 4: Habits Organized by Domain")
    print("=" * 70)

    result = get_habits_by_domain.invoke({"user_id": user_id})
    print(result)

    # ================================================================
    # Part 5: Research-Based Information
    # ================================================================
    print("\n" + "=" * 70)
    print("PART 5: Research-Based Habit Formation Facts")
    print("=" * 70)

    from src.tools.habit_tools import HABIT_FORMATION_RESEARCH

    print(f"""
📊 Habit Formation Research (Lally et al., 2009)

The commonly cited "21 days to form a habit" is a myth originating from
Maxwell Maltz's 1960 book "Psycho-Cybernetics." 

Actual research shows:
• Minimum time: {HABIT_FORMATION_RESEARCH["min_days"]} days
• Maximum time: {HABIT_FORMATION_RESEARCH["max_days"]} days  
• Median time: {HABIT_FORMATION_RESEARCH["median_days"]} days
• Average time: {HABIT_FORMATION_RESEARCH["avg_days"]} days

Key Insights:
1. Habit formation varies widely by person and behavior
2. Consistency matters more than intensity
3. Missing once is a mistake; missing twice is the start of a new habit
4. The 21-day rule set unrealistic expectations

Source: Lally, P., et al. (2009). How are habits formed: Modelling habit 
formation in the real world. European Journal of Social Psychology.
""")

    # ================================================================
    # Part 6: Summary
    # ================================================================
    print("\n" + "=" * 70)
    print("Demo Summary")
    print("=" * 70)

    print("""
✅ Habit Tracking System Features Demonstrated:

1. ✓ Create habits with Atomic Habits framework (Cue-Action-Reward)
2. ✓ Multiple frequency options (daily, weekdays, weekends, weekly)
3. ✓ Eight life domains (health, career, relationships, finance, etc.)
4. ✓ Habit stacking suggestions based on existing habits
5. ✓ Domain-based habit organization
6. ✓ Research-based habit formation timeline

Next Steps:
- Log daily completions using log_habit_completion()
- Track streaks with get_habit_streaks()
- Monitor habit strength with calculate_habit_strength_score()
- Review and adjust habits with review_habit()
- Use habit stacking to build habit chains

Remember: "You do not rise to the level of your goals. 
          You fall to the level of your systems." - James Clear
""")


if __name__ == "__main__":
    run_demo()
