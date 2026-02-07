"""
Demo script for Goal Dependency Visualization Tools.

This script demonstrates all the visualization capabilities:
- ASCII graph rendering in multiple formats
- Interactive exploration commands
- Critical path highlighting
- What-if analysis scenarios
- Comprehensive dependency reporting

Run with: python demo_viz_tools.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.tools.viz_tools import (
    ASCIIGraphRenderer,
    InteractiveExplorer,
    WhatIfAnalyzer,
    generate_dependency_report,
)
from src.tools.goal_dependency_tools import (
    GoalNode,
    DependencyEdge,
    GoalDependencyGraph,
)


def create_example_graph():
    """Create an example goal dependency graph."""
    print("Creating example goal dependency graph...")

    graph = GoalDependencyGraph()

    # Create goals across multiple domains
    goals = [
        GoalNode(
            id="career_1",
            domain="career",
            title="Get promoted to Senior Engineer",
            priority=8,
            status="in_progress",
            estimated_effort=40.0,
        ),
        GoalNode(
            id="career_2",
            domain="career",
            title="Complete advanced certification",
            priority=7,
            status="pending",
            estimated_effort=30.0,
        ),
        GoalNode(
            id="finance_1",
            domain="finance",
            title="Save $10k for emergency fund",
            priority=9,
            status="pending",
            estimated_effort=20.0,
        ),
        GoalNode(
            id="finance_2",
            domain="finance",
            title="Save $50k house downpayment",
            priority=9,
            status="pending",
            estimated_effort=60.0,
        ),
        GoalNode(
            id="wellness_1",
            domain="wellness",
            title="Establish daily exercise routine",
            priority=7,
            status="pending",
            estimated_effort=15.0,
        ),
        GoalNode(
            id="wellness_2",
            domain="wellness",
            title="Improve sleep quality to 7+ hours",
            priority=6,
            status="pending",
            estimated_effort=10.0,
        ),
    ]

    for goal in goals:
        graph.add_goal(goal)

    # Create dependencies
    dependencies = [
        DependencyEdge(
            from_goal_id="career_1",
            to_goal_id="finance_2",
            relationship_type="enables",
            strength=0.9,
            reason="Higher salary enables faster house savings",
        ),
        DependencyEdge(
            from_goal_id="career_2",
            to_goal_id="career_1",
            relationship_type="requires",
            strength=0.8,
            reason="Certification required for promotion eligibility",
        ),
        DependencyEdge(
            from_goal_id="finance_1",
            to_goal_id="finance_2",
            relationship_type="supports",
            strength=0.5,
            reason="Emergency fund foundation supports house savings",
        ),
        DependencyEdge(
            from_goal_id="wellness_1",
            to_goal_id="career_1",
            relationship_type="supports",
            strength=0.6,
            reason="Exercise improves energy and focus for work performance",
        ),
        DependencyEdge(
            from_goal_id="wellness_2",
            to_goal_id="career_1",
            relationship_type="supports",
            strength=0.7,
            reason="Better sleep improves cognitive function and productivity",
        ),
    ]

    for dep in dependencies:
        graph.add_dependency(dep)

    print(f"✓ Created graph with {len(graph.nodes)} goals and {len(graph.edges)} dependencies")
    return graph


def demo_ascii_rendering():
    """Demonstrate ASCII graph rendering in different formats."""
    print("\n" + "=" * 80)
    print("DEMO: ASCII GRAPH RENDERING")
    print("=" * 80)

    graph = create_example_graph()
    renderer = ASCIIGraphRenderer(graph)

    # Tree format
    print("\n1. TREE FORMAT:")
    print("-" * 80)
    print(renderer.render_tree())

    # Matrix format
    print("\n2. MATRIX FORMAT:")
    print("-" * 80)
    print(renderer.render_matrix())

    # Linear flow format
    print("\n3. LINEAR FLOW FORMAT:")
    print("-" * 80)
    print(renderer.render_linear_flow())

    # With critical path highlighted
    print("\n4. TREE FORMAT WITH CRITICAL PATH HIGHLIGHTED:")
    print("-" * 80)
    print(renderer.render_tree(show_critical_path=True))


def demo_interactive_exploration():
    """Demonstrate interactive exploration commands."""
    print("\n" + "=" * 80)
    print("DEMO: INTERACTIVE EXPLORATION")
    print("=" * 80)

    graph = create_example_graph()
    explorer = InteractiveExplorer(graph)

    commands = [
        "help",
        "show",
        "expand career_1",
        "path",
        "stats",
    ]

    for cmd in commands:
        print(f"\nCommand: {cmd}")
        print("-" * 80)
        result = explorer.execute_command(cmd)
        print(result)


def demo_what_if_analysis():
    """Demonstrate what-if analysis scenarios."""
    print("\n" + "=" * 80)
    print("DEMO: WHAT-IF ANALYSIS")
    print("=" * 80)

    graph = create_example_graph()
    analyzer = WhatIfAnalyzer(graph)

    # Scenario 1: Add a new goal
    print("\n1. WHAT-IF: ADD NEW GOAL")
    print("-" * 80)
    new_goal = {
        "id": "wellness_3",
        "domain": "wellness",
        "title": "Run a marathon",
        "priority": 5,
        "estimated_effort": 100.0,
    }
    print(analyzer.simulate_add_goal(new_goal))

    # Scenario 2: Remove an existing goal
    print("\n\n2. WHAT-IF: REMOVE GOAL")
    print("-" * 80)
    print(analyzer.simulate_remove_goal("career_2"))


def demo_dependency_report():
    """Demonstrate comprehensive dependency report generation."""
    print("\n" + "=" * 80)
    print("DEMO: DEPENDENCY REPORT GENERATION")
    print("=" * 80)

    graph = create_example_graph()
    report = generate_dependency_report(graph, "demo_user", include_visualizations=True)

    print(report)


def main():
    """Run all demos."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " GOAL DEPENDENCY VISUALIZATION TOOLS - DEMONSTRATION ".center(78) + "║")
    print("╚" + "=" * 78 + "╝")

    try:
        demo_ascii_rendering()
        demo_interactive_exploration()
        demo_what_if_analysis()
        demo_dependency_report()

        print("\n")
        print("╔" + "=" * 78 + "╗")
        print("║" + " DEMONSTRATION COMPLETE ".center(78) + "║")
        print("╚" + "=" * 78 + "╝")

    except Exception as e:
        print(f"\n❌ Error during demonstration: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
