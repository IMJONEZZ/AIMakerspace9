#!/usr/bin/env python3
"""
Demo script for Progress Dashboard Tools.

This script demonstrates the dashboard visualization capabilities
of the AI Life Coach system with sample data.

Usage:
    python demo_dashboard.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import config, get_backend

# Initialize environment first
config.initialize_environment()

from tools.dashboard_tools import create_dashboard_tools


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def demo_main_dashboard():
    """Demo the main progress dashboard."""
    print_section("DEMO 1: Main Progress Dashboard")

    backend = get_backend()
    tools = create_dashboard_tools(backend)
    render_tool = tools[0]

    # Render weekly dashboard
    print("📊 Rendering Weekly Progress Dashboard...")
    print("\n" + "-" * 70)
    dashboard = render_tool.invoke(
        {
            "user_id": "demo_user",
            "view": "weekly",
            "include_mood": True,
            "include_goals": True,
            "include_achievements": True,
        }
    )
    print(dashboard)
    print("-" * 70)


def demo_life_satisfaction_score():
    """Demo the life satisfaction score calculation."""
    print_section("DEMO 2: Life Satisfaction Score")

    backend = get_backend()
    tools = create_dashboard_tools(backend)
    score_tool = tools[1]

    print("🎯 Calculating comprehensive life satisfaction score...")
    print()

    result = score_tool.invoke(
        {
            "user_id": "demo_user",
            "view": "weekly",
        }
    )
    print(result)


def demo_domain_progress():
    """Demo domain-specific progress bars."""
    print_section("DEMO 3: Domain Progress Bars")

    backend = get_backend()
    tools = create_dashboard_tools(backend)
    bar_tool = tools[2]

    domains = ["career", "wellness", "finance", "relationship"]

    for domain in domains:
        print(f"\n📈 Progress for {domain.upper()} domain:")
        print("-" * 60)
        result = bar_tool.invoke(
            {
                "user_id": "demo_user",
                "domain": domain,
                "view": "weekly",
                "bar_width": 30,
            }
        )
        print(result)


def demo_mood_sparkline():
    """Demo mood trend sparkline."""
    print_section("DEMO 4: Mood Trend Sparkline")

    backend = get_backend()
    tools = create_dashboard_tools(backend)
    sparkline_tool = tools[3]

    print("😊 Analyzing mood trends over time...")
    print()

    # Weekly view
    result = sparkline_tool.invoke(
        {
            "user_id": "demo_user",
            "view": "weekly",
            "width": 40,
        }
    )
    print(result)


def demo_achievements():
    """Demo recent achievements display."""
    print_section("DEMO 5: Recent Achievements")

    backend = get_backend()
    tools = create_dashboard_tools(backend)
    achievements_tool = tools[4]

    print("🏆 Displaying recent achievements...")
    print()

    result = achievements_tool.invoke(
        {
            "user_id": "demo_user",
            "limit": 5,
        }
    )
    print(result)


def demo_milestones():
    """Demo upcoming milestones."""
    print_section("DEMO 6: Upcoming Milestones")

    backend = get_backend()
    tools = create_dashboard_tools(backend)
    milestones_tool = tools[5]

    print("🎯 Displaying upcoming milestones...")
    print()

    result = milestones_tool.invoke(
        {
            "user_id": "demo_user",
            "limit": 5,
        }
    )
    print(result)


def demo_view_switching():
    """Demo view switching between daily/weekly/monthly."""
    print_section("DEMO 7: View Switching")

    backend = get_backend()
    tools = create_dashboard_tools(backend)
    switch_tool = tools[7]
    render_tool = tools[0]

    # Daily view
    print("📅 Switching to DAILY view...")
    result = switch_tool.invoke(
        {
            "user_id": "demo_user",
            "view": "daily",
            "render": True,
        }
    )
    print(result[:1500] + "\n... [truncated for display]")

    print("\n" + "-" * 70 + "\n")

    # Monthly view
    print("📅 Switching to MONTHLY view...")
    result = switch_tool.invoke(
        {
            "user_id": "demo_user",
            "view": "monthly",
            "render": True,
        }
    )
    print(result[:1500] + "\n... [truncated for display]")


def demo_export():
    """Demo report export functionality."""
    print_section("DEMO 8: Export Report")

    backend = get_backend()
    tools = create_dashboard_tools(backend)
    export_tool = tools[6]

    print("📄 Generating Markdown report...")
    print()

    result = export_tool.invoke(
        {
            "user_id": "demo_user",
            "view": "weekly",
            "format": "markdown",
            "include_charts": True,
        }
    )

    # Show first part of result
    lines = result.split("\n")
    print("\n".join(lines[:30]))
    print("\n... [report preview truncated]")
    print(f"\nFull result: {lines[0] if lines else 'Report generated'}")


def main():
    """Run all dashboard demos."""
    print("\n" + "🎯" * 35)
    print("  AI LIFE COACH - Progress Dashboard Demo")
    print("🎯" * 35)
    print("\nThis demo showcases the comprehensive progress dashboard")
    print("with ASCII-based visualizations for CLI environments.\n")

    try:
        demo_main_dashboard()
        demo_life_satisfaction_score()
        demo_domain_progress()
        demo_mood_sparkline()
        demo_achievements()
        demo_milestones()
        demo_view_switching()
        demo_export()

        print("\n" + "=" * 70)
        print("  Demo completed successfully!")
        print("=" * 70)
        print("\nKey Features Demonstrated:")
        print("  ✓ Multi-domain progress tracking")
        print("  ✓ ASCII-based visualizations")
        print("  ✓ Mood trend sparklines")
        print("  ✓ Achievement and milestone tracking")
        print("  ✓ Configurable timeframes (daily/weekly/monthly)")
        print("  ✓ Markdown report export")
        print()

    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
