"""
Demonstration of Weekly Check-In System for AI Life Coach.

This script demonstrates the complete weekly check-in workflow including:
1. Conducting a comprehensive weekly check-in
2. Calculating progress scores with research-based algorithms
3. Analyzing week-over-week trends
4. Generating adaptation recommendations
5. Creating detailed weekly reports

Based on research in:
- Habit formation psychology (66-day average for automaticity, not 21 days)
- Weekly progress tracking best practices (PPP methodology)
- OKR scoring and measurement frameworks
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.tools.checkin_tools import create_checkin_tools
from src.config import config, get_backend


def demo_weekly_checkin():
    """Demonstrate the weekly check-in system."""

    # Initialize environment
    config.initialize_environment()

    # Create check-in tools
    print("Creating weekly check-in tools...")
    backend = get_backend()
    (
        conduct_weekly_checkin,
        calculate_progress_score,
        analyze_weekly_trends,
        generate_adaptation_recommendations,
        generate_weekly_report,
    ) = create_checkin_tools(backend)

    print("✓ Tools created successfully!\n")

    # Demo 1: Week 1 Check-In
    print("=" * 70)
    print("DEMO 1: Week 1 Check-In - Starting a New Journey")
    print("=" * 70)

    week_1_responses = {
        "career_goals_completed": 50,
        "relationship_goals_completed": 60,
        "finance_goals_completed": 70,
        "wellness_goals_completed": 65,
        "average_mood": 5,
        "average_energy": 5,
        "stress_level": 6,
        "sleep_quality": 6,
        "primary_obstacles": "Getting started with new routine",
        "obstacle_severity": 5,
        "key_achievements": "Set up my goals and created a plan",
    }

    result_1 = conduct_weekly_checkin.invoke(
        {"user_id": "demo_user", "responses": week_1_responses}
    )
    print(result_1)
    print()

    # Demo 2: Week 2 Check-In (Progress Made)
    print("=" * 70)
    print("DEMO 2: Week 2 Check-In - Building Momentum")
    print("=" * 70)

    week_2_responses = {
        "career_goals_completed": 75,
        "relationship_goals_completed": 70,
        "finance_goals_completed": 80,
        "wellness_goals_completed": 75,
        "average_mood": 7,
        "average_energy": 6,
        "stress_level": 4,
        "sleep_quality": 7,
        "primary_obstacles": "Minor time management issues",
        "obstacle_severity": 3,
        "key_achievements": "Completed first major goal milestone",
    }

    result_2 = conduct_weekly_checkin.invoke(
        {"user_id": "demo_user", "responses": week_2_responses}
    )
    print(result_2)
    print()

    # Demo 3: Calculate Progress Score
    print("=" * 70)
    print("DEMO 3: Calculating Detailed Progress Score")
    print("=" * 70)

    score_result = calculate_progress_score.invoke({"user_id": "demo_user"})
    print(score_result)
    print()

    # Demo 4: Analyze Trends
    print("=" * 70)
    print("DEMO 4: Week-over-Week Trend Analysis")
    print("=" * 70)

    trend_result = analyze_weekly_trends.invoke({"user_id": "demo_user", "weeks": 2})
    print(trend_result)
    print()

    # Demo 5: Generate Adaptation Recommendations
    print("=" * 70)
    print("DEMO 5: Adaptive Planning Recommendations")
    print("=" * 70)

    adaptations_result = generate_adaptation_recommendations.invoke({"user_id": "demo_user"})
    print(adaptations_result)
    print()

    # Demo 6: Generate Weekly Report (Markdown)
    print("=" * 70)
    print("DEMO 6: Generating Weekly Progress Report (Markdown)")
    print("=" * 70)

    report_result = generate_weekly_report.invoke(
        {"user_id": "demo_user", "format_type": "markdown"}
    )
    print(report_result)
    print()

    # Demo 7: Week 3 Check-In (Challenges Encountered)
    print("=" * 70)
    print("DEMO 7: Week 3 Check-In - Overcoming Challenges")
    print("=" * 70)

    week_3_responses = {
        "career_goals_completed": 60,
        "relationship_goals_completed": 55,
        "finance_goals_completed": 70,
        "wellness_goals_completed": 50,
        "average_mood": 4,
        "average_energy": 5,
        "stress_level": 8,
        "sleep_quality": 5,
        "primary_obstacles": "Unexpected work deadline and family obligations",
        "obstacle_severity": 8,
        "key_achievements": "Still managed to maintain finance goals",
    }

    result_3 = conduct_weekly_checkin.invoke(
        {"user_id": "demo_user", "responses": week_3_responses}
    )
    print(result_3)
    print()

    # Demo 8: Updated Trends with Challenges
    print("=" * 70)
    print("DEMO 8: Trend Analysis After Challenging Week")
    print("=" * 70)

    trend_result_2 = analyze_weekly_trends.invoke({"user_id": "demo_user", "weeks": 3})
    print(trend_result_2)
    print()

    # Demo 9: Adaptations for Challenging Week
    print("=" * 70)
    print("DEMO 9: Adaptations for Challenging Period")
    print("=" * 70)

    adaptations_result_2 = generate_adaptation_recommendations.invoke({"user_id": "demo_user"})
    print(adaptations_result_2)
    print()

    # Summary
    print("=" * 70)
    print("WEEKLY CHECK-IN SYSTEM DEMO COMPLETE")
    print("=" * 70)
    print()
    print("Key Features Demonstrated:")
    print("✓ Comprehensive weekly check-in questionnaire")
    print("✓ Research-based progress scoring (66-day habit formation)")
    print("✓ Week-over-week trend analysis")
    print("✓ Adaptive planning recommendations")
    print("✓ Weekly progress reports (JSON + Markdown)")
    print()
    print("The check-in system successfully:")
    print("• Tracks progress across all life domains")
    print("• Identifies patterns and trends")
    print("• Provides actionable adaptations")
    print("• Generates detailed reports for tracking")
    print()


if __name__ == "__main__":
    demo_weekly_checkin()
