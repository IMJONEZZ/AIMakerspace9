"""
Sample scenarios demonstrating the Career Coach Specialist.

This script demonstrates the career coaching capabilities with realistic
career transition scenarios.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.main import create_life_coach


def demo_career_transition_scenario():
    """
    Demonstrate a complete career transition scenario:
    Marketing Manager transitioning to Data Scientist
    """
    print("\n" + "=" * 80)
    print("DEMO: Career Transition - Marketing to Data Science")
    print("=" * 80)

    coach = create_life_coach()

    # Simulate a user seeking career transition guidance
    user_query = """
    I'm currently a Marketing Manager with 7 years of experience. I want to transition
    into Data Science. Here's my background:

    Current Skills:
    - Marketing strategy and analytics
    - Content creation and social media management
    - Team leadership (managing 5 people)
    - Basic Excel skills

    Target Role: Data Scientist
    Timeline: 3 years

    Can you help me:
    1. Analyze my skill gaps
    2. Create a transition plan
    3. Give me resume advice for Data Science roles
    """

    print(f"\nUser Query:\n{user_query}\n")
    print("-" * 80)
    print("AI Life Coach Response:")
    print("-" * 80)

    result = coach.invoke({"messages": [{"role": "user", "content": user_query}]})

    print(result["messages"][-1].content)
    print("\n" + "=" * 80)


def demo_interview_preparation_scenario():
    """
    Demonstrate interview preparation for a specific role.
    """
    print("\n" + "=" * 80)
    print("DEMO: Interview Preparation for Product Manager Role")
    print("=" * 80)

    coach = create_life_coach()

    user_query = """
    I have an interview coming up for a Product Manager position at a tech company.
    Can you help me prepare?

    My background:
    - 3 years as a Software Developer
    - Recently completed a product management certificate
    - Some experience with cross-functional collaboration

    I need help with:
    1. Common PM interview questions
    2. How to frame my technical background as a strength
    """

    print(f"\nUser Query:\n{user_query}\n")
    print("-" * 80)
    print("AI Life Coach Response:")
    print("-" * 80)

    result = coach.invoke({"messages": [{"role": "user", "content": user_query}]})

    print(result["messages"][-1].content)
    print("\n" + "=" * 80)


def demo_salary_negotiation_scenario():
    """
    Demonstrate salary negotiation guidance.
    """
    print("\n" + "=" * 80)
    print("DEMO: Salary Negotiation for Senior Data Scientist Role")
    print("=" * 80)

    coach = create_life_coach()

    user_query = """
    I just received an offer for a Senior Data Scientist position in San Francisco.
    The base salary is $145k. I want to negotiate but need guidance.

    My experience:
    - 5 years in data science
    - Previous salary: $130k
    - Led 3 major ML projects that generated significant revenue

    Can you help me with:
    1. Salary benchmarks for this role in SF
    2. Negotiation strategies
    """

    print(f"\nUser Query:\n{user_query}\n")
    print("-" * 80)
    print("AI Life Coach Response:")
    print("-" * 80)

    result = coach.invoke({"messages": [{"role": "user", "content": user_query}]})

    print(result["messages"][-1].content)
    print("\n" + "=" * 80)


def demo_career_advancement_scenario():
    """
    Demonstrate career advancement within current field.
    """
    print("\n" + "=" * 80)
    print("DEMO: Career Advancement - Moving to Senior Level")
    print("=" * 80)

    coach = create_life_coach()

    user_query = """
    I'm a Software Engineer with 4 years of experience. I want to advance to Senior
    Software Engineer within the next year.

    Current situation:
    - Work at a mid-sized tech company
    - Strong technical skills in Python and JavaScript
    - Experience with 2 major product launches
    - Limited formal leadership experience

    What do I need to demonstrate for a Senior role?
    """

    print(f"\nUser Query:\n{user_query}\n")
    print("-" * 80)
    print("AI Life Coach Response:")
    print("-" * 80)

    result = coach.invoke({"messages": [{"role": "user", "content": user_query}]})

    print(result["messages"][-1].content)
    print("\n" + "=" * 80)


if __name__ == "__main__":
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "CAREER COACH DEMONSTRATION" + " " * 38 + "║")
    print("╚" + "═" * 78 + "╝")

    print("\nThis demo showcases the Career Coach Specialist capabilities with")
    print("realistic career scenarios. Each scenario demonstrates different tools:")
    print("- Career transition planning")
    print("- Interview preparation")
    print("- Salary negotiation guidance")
    print("- Career advancement strategy")

    input("\nPress Enter to start the demos...")

    try:
        # Run all demo scenarios
        demo_career_transition_scenario()
        input("\nPress Enter for next demo...")

        demo_interview_preparation_scenario()
        input("\nPress Enter for next demo...")

        demo_salary_negotiation_scenario()
        input("\nPress Enter for next demo...")

        demo_career_advancement_scenario()

        print("\n" + "\u2713 All demos completed successfully!")
        print("\nThe Career Coach Specialist demonstrated:")
        print("  ✓ Skill gap analysis")
        print("  ✓ Career path planning with milestones")
        print("  ✓ Resume/CV optimization guidance")
        print("  ✓ Interview preparation strategies")
        print("  ✓ Salary benchmark research and negotiation tips")

    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nError during demo: {e}")
        import traceback

        traceback.print_exc()
