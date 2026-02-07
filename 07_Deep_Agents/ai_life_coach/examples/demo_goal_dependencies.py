#!/usr/bin/env python3
"""
Demonstration of Goal Dependency Mapping System (Bead #19).

This script showcases the key features of the goal dependency mapping system:
- Building dependency graphs
- Detecting cycles and conflicts
- Critical path analysis
- Impact simulation
- Text-based visualization

Run with: python examples/demo_goal_dependencies.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.goal_dependency_tools import (
    GoalNode,
    DependencyEdge,
    GoalDependencyGraph,
    visualize_dependency_graph_text,
)


def demo_basic_dependency_graph():
    """Demonstrate building and analyzing a basic dependency graph."""
    print("=" * 80)
    print("DEMO 1: Basic Goal Dependency Graph")
    print("=" * 80)

    # Create a dependency graph
    graph = GoalDependencyGraph()

    # Add goals with estimated effort
    goals = [
        GoalNode(
            id="g1",
            domain="career",
            title="Get promotion to Senior Engineer",
            priority=8,
            estimated_effort=40.0,  # hours
        ),
        GoalNode(
            id="g2",
            domain="finance",
            title="Save $50,000 for down payment",
            priority=7,
            estimated_effort=60.0,
        ),
        GoalNode(
            id="g3",
            domain="finance",
            title="Buy first house",
            priority=6,
            estimated_effort=20.0,
        ),
    ]

    for goal in goals:
        graph.add_goal(goal)

    # Add dependencies
    edges = [
        DependencyEdge(
            from_goal_id="g1",
            to_goal_id="g2",
            relationship_type="enables",
            strength=0.9,
            reason="Higher salary enables faster savings",
        ),
        DependencyEdge(
            from_goal_id="g2",
            to_goal_id="g3",
            relationship_type="requires",
            strength=1.0,
            reason="Need down payment to buy house",
        ),
    ]

    for edge in edges:
        graph.add_dependency(edge)

    # Visualize the graph
    print("\nDependency Graph Visualization:")
    print(visualize_dependency_graph_text(graph))

    # Detect cycles
    cycles = graph.detect_cycles()
    if not cycles:
        print("✓ No circular dependencies detected")
    else:
        print(f"⚠ Warning: {len(cycles)} circular dependency(ies) found")

    # Topological sort
    try:
        order = graph.topological_sort()
        print("\nRecommended Execution Order:")
        for i, goal_id in enumerate(order, 1):
            print(f"  {i}. {graph.nodes[goal_id].title}")
    except ValueError as e:
        print(f"\nError: {e}")

    # Find critical path
    try:
        critical_path, total_effort = graph.find_critical_path()
        print(f"\n🎯 Critical Path (Longest dependency chain):")
        print(" → ".join([graph.nodes[gid].title for gid in critical_path]))
        print(f"   Total estimated effort: {total_effort:.1f} hours")
    except ValueError as e:
        print(f"\nError finding critical path: {e}")


def demo_impact_simulation():
    """Demonstrate impact propagation through the graph."""
    print("\n" + "=" * 80)
    print("DEMO 2: Impact Propagation Simulation")
    print("=" * 80)

    # Create a more complex graph
    graph = GoalDependencyGraph()

    goals = [
        GoalNode(id="g1", domain="career", title="Get promotion"),
        GoalNode(id="g2", domain="finance", title="Save $50k"),
        GoalNode(id="g3", domain="wellness", title="Exercise daily"),
        GoalNode(id="g4", domain="career", title="Learn new skills"),
    ]

    for goal in goals:
        graph.add_goal(goal)

    edges = [
        DependencyEdge(from_goal_id="g1", to_goal_id="g2", relationship_type="enables"),
        DependencyEdge(from_goal_id="g1", to_goal_id="g3", relationship_type="conflicts"),
        DependencyEdge(from_goal_id="g4", to_goal_id="g1", relationship_type="requires"),
    ]

    for edge in edges:
        graph.add_dependency(edge)

    print("\nGraph Structure:")
    print("  Learn new skills (g4) → Requires → Get promotion (g1)")
    print("  Get promotion (g1) → Enables → Save $50k (g2)")
    print("  Get promotion (g1) → Conflicts → Exercise daily (g3)")

    # Simulate success of getting promotion
    print("\n" + "─" * 80)
    print("Simulating: Get promotion (g1) → SUCCESS")
    print("─" * 80)

    affected = graph.simulate_impact("g1", "success")

    if affected["positively_affected"]:
        print("\n✓ Positively Affected Goals:")
        for impact in affected["positively_affected"]:
            print(f"  • {impact['title']}")
            print(f"    Impact: {impact['reason']}")

    if affected["negatively_affected"]:
        print("\n⚠ Negatively Affected Goals:")
        for impact in affected["negatively_affected"]:
            print(f"  • {impact['title']}")
            print(f"    Impact: {impact['reason']}")

    # Simulate failure of learning new skills
    print("\n" + "─" * 80)
    print("Simulating: Learn new skills (g4) → FAILURE")
    print("─" * 80)

    affected = graph.simulate_impact("g4", "failure")

    if affected["blocked"]:
        print("\n🚫 Blocked Goals:")
        for impact in affected["blocked"]:
            print(f"  • {impact['title']}")
            print(f"    Impact: {impact['reason']}")

    if affected["negatively_affected"]:
        print("\n⚠ Negatively Affected Goals:")
        for impact in affected["negatively_affected"]:
            print(f"  • {impact['title']}")
            print(f"    Impact: {impact['reason']}")


def demo_cycle_detection():
    """Demonstrate cycle detection and resolution."""
    print("\n" + "=" * 80)
    print("DEMO 3: Circular Dependency Detection")
    print("=" * 80)

    graph = GoalDependencyGraph()

    goals = [
        GoalNode(id="g1", domain="career", title="Get promotion"),
        GoalNode(id="g2", domain="finance", title="Save money"),
        GoalNode(id="g3", domain="wellness", title="Exercise daily"),
    ]

    for goal in goals:
        graph.add_goal(goal)

    # Create a circular dependency
    edges = [
        DependencyEdge(from_goal_id="g1", to_goal_id="g2", relationship_type="requires"),
        DependencyEdge(from_goal_id="g2", to_goal_id="g3", relationship_type="requires"),
        DependencyEdge(from_goal_id="g3", to_goal_id="g1", relationship_type="requires"),
    ]

    for edge in edges:
        graph.add_dependency(edge)

    print("\nCreated circular dependency:")
    print("  Get promotion → Requires → Save money")
    print("  Save money → Requires → Exercise daily")
    print("  Exercise daily → Requires → Get promotion")
    print("  (This creates an impossible circular dependency!)")

    # Detect cycles
    cycles = graph.detect_cycles()

    if cycles:
        print(f"\n⚠ Detected {len(cycles)} circular dependency(ies):")
        for i, cycle in enumerate(cycles, 1):
            goal_titles = " → ".join(
                [graph.nodes[gid].title for gid in cycle if gid in graph.nodes]
            )
            print(f"  Cycle {i}: {goal_titles} → (back to start)")

        # Try topological sort (should fail)
        try:
            order = graph.topological_sort()
        except ValueError as e:
            print(f"\n❌ Topological sort failed: {e}")
    else:
        print("\n✓ No circular dependencies detected")


def demo_cross_domain_dependencies():
    """Demonstrate cross-domain dependency mapping."""
    print("\n" + "=" * 80)
    print("DEMO 4: Cross-Domain Goal Dependencies")
    print("=" * 80)

    graph = GoalDependencyGraph()

    goals = [
        # Career domain
        GoalNode(
            id="c1",
            domain="career",
            title="Get promotion",
            priority=8,
        ),
        GoalNode(
            id="c2",
            domain="career",
            title="Learn leadership skills",
            priority=7,
        ),
        # Finance domain
        GoalNode(
            id="f1",
            domain="finance",
            title="Build emergency fund",
            priority=9,
        ),
        GoalNode(
            id="f2",
            domain="finance",
            title="Invest for retirement",
            priority=6,
        ),
        # Wellness domain
        GoalNode(
            id="w1",
            domain="wellness",
            title="Improve sleep quality",
            priority=7,
        ),
    ]

    for goal in goals:
        graph.add_goal(goal)

    edges = [
        # Within-domain dependencies
        DependencyEdge(from_goal_id="c2", to_goal_id="c1", relationship_type="requires"),
        DependencyEdge(from_goal_id="f1", to_goal_id="f2", relationship_type="requires"),
        # Cross-domain dependencies
        DependencyEdge(
            from_goal_id="c1",
            to_goal_id="f2",
            relationship_type="enables",
            reason="Higher income enables larger investments",
        ),
        DependencyEdge(
            from_goal_id="w1",
            to_goal_id="c1",
            relationship_type="supports",
            reason="Better sleep supports better work performance",
        ),
    ]

    for edge in edges:
        graph.add_dependency(edge)

    print(visualize_dependency_graph_text(graph))


def main():
    """Run all demonstrations."""
    print("\n╔" + "═" * 78 + "╗")
    print("║" + " GOAL DEPENDENCY MAPPING SYSTEM - DEMONSTRATION ".center(78) + "║")
    print("╚" + "═" * 78 + "╝")

    demo_basic_dependency_graph()
    demo_impact_simulation()
    demo_cycle_detection()
    demo_cross_domain_dependencies()

    print("\n" + "=" * 80)
    print("Demonstration Complete!")
    print("=" * 80)
    print("\nKey Features Demonstrated:")
    print("  ✓ Building dependency graphs with multiple relationship types")
    print("  ✓ Cycle detection and topological sorting")
    print("  ✓ Critical path analysis for goal achievement timing")
    print("  ✓ Impact propagation simulation (success/failure scenarios)")
    print("  ✓ Text-based visualization of dependency graphs")
    print("  ✓ Cross-domain goal relationship mapping")
    print("\nFor more information, see:")
    print("  - src/tools/goal_dependency_tools.py")
    print("  - tests/test_goal_dependency_tools.py")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
