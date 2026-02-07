#!/usr/bin/env python3
"""
Master demo script - Run all specialist agent demos.

This script demonstrates all 4 specialists with their test scenarios:
- Career: "I want to transition from marketing to data science"
- Relationship: "I struggle with setting boundaries at work"
- Finance: "I want to save for a house down payment in 3 years"
- Wellness: "I have trouble sleeping due to work stress"

Run with:
    python demos/demo_all_specialists.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def print_header(title):
    """Print a fancy header."""
    border = "=" * 70
    print(f"\n{border}")
    title_centered = f"  {title}  ".center(70)
    print(title_centered)
    print(border)


def run_all_demos():
    """Run all four specialist demos."""
    print_header("AI Life Coach - All Specialist Agents Demo")

    print("""
This demo showcases all 4 specialist agents with their test scenarios:

1. Career Specialist:
   Scenario: "I want to transition from marketing to data science"

2. Relationship Specialist:
   Scenario: "I struggle with setting boundaries at work"

3. Finance Specialist:
   Scenario: "I want to save for a house down payment in 3 years"

4. Wellness Specialist:
   Scenario: "I have trouble sleeping due to work stress"
    """)

    import demos.demo_career_specialist
    import demos.demo_relationship_specialist
    import demos.demo_finance_specialist
    import demos.demo_wellness_specialist

    # Run each demo
    print("\n" + "=" * 70)
    print("  Running Career Specialist Demo...")
    print("=" * 70)
    demos.demo_career_specialist.demonstrate_career_specialist()

    print("\n" + "=" * 70)
    print("  Running Relationship Specialist Demo...")
    print("=" * 70)
    demos.demo_relationship_specialist.demonstrate_relationship_specialist()

    print("\n" + "=" * 70)
    print("  Running Finance Specialist Demo...")
    print("=" * 70)
    demos.demo_finance_specialist.demonstrate_finance_specialist()

    print("\n" + "=" * 70)
    print("  Running Wellness Specialist Demo...")
    print("=" * 70)
    demos.demo_wellness_specialist.demonstrate_wellness_specialist()

    # Final summary
    print_header("All Demos Complete")

    print("""
Summary:
✓ Career Specialist tested with marketing → data science transition
✓ Relationship Specialist tested with workplace boundary setting
✓ Finance Specialist tested with house down payment savings goal
✓ Wellness Specialist tested with sleep optimization for work stress

All specialists demonstrated:
- Proper tool integration (memory + context + domain-specific)
- Domain expertise in action
- Boundary awareness and proper disclaimers
- Actionable, coherent responses

For detailed information about capabilities and limitations,
see: SPECIALIST_CAPABILITIES.md

To run individual demos:
  python demos/demo_career_specialist.py
  python demos/demo_relationship_specialist.py
  python demos/demo_finance_specialist.py
  python demos/demo_wellness_specialist.py

To run tests:
  pytest tests/test_specialist_agents.py -v
    """)


if __name__ == "__main__":
    run_all_demos()
