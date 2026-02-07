"""
Test Suite for Goal Dependency Mapping Tools.

This module tests all functionality of goal_dependency_tools.py:
- Goal graph data structure
- Dependency detection algorithms
- Impact propagation simulation
- Text-based visualization
- Critical path analysis
- Conflict resolution strategies

Run tests with: python -m pytest tests/test_goal_dependency_tools.py -v
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.goal_dependency_tools import (
    GoalNode,
    DependencyEdge,
    GoalDependencyGraph,
    detect_implicit_dependencies,
    suggest_conflict_resolution,
    visualize_dependency_graph_text,
)


# ==============================================================================
# Test Data Structures
# ==============================================================================


def test_goal_node_creation():
    """Test creating a GoalNode."""
    goal = GoalNode(
        id="g1",
        domain="career",
        title="Get promotion",
        priority=8,
        status="pending",
        estimated_effort=40.0,
        deadline="2025-06-01",
    )

    assert goal.id == "g1"
    assert goal.domain == "career"
    assert goal.title == "Get promotion"
    assert goal.priority == 8
    assert goal.status == "pending"
    assert goal.estimated_effort == 40.0
    assert goal.deadline == "2025-06-01"

    # Test to_dict conversion
    goal_dict = goal.to_dict()
    assert goal_dict["id"] == "g1"
    assert goal_dict["domain"] == "career"
    assert goal_dict["title"] == "Get promotion"


def test_dependency_edge_creation():
    """Test creating a DependencyEdge."""
    edge = DependencyEdge(
        from_goal_id="g1",
        to_goal_id="g2",
        relationship_type="enables",
        strength=0.8,
        reason="Higher income enables savings",
    )

    assert edge.from_goal_id == "g1"
    assert edge.to_goal_id == "g2"
    assert edge.relationship_type == "enables"
    assert edge.strength == 0.8
    assert edge.reason == "Higher income enables savings"

    # Test to_dict conversion
    edge_dict = edge.to_dict()
    assert edge_dict["from_goal_id"] == "g1"
    assert edge_dict["relationship_type"] == "enables"


def test_goal_dependency_graph_creation():
    """Test creating a GoalDependencyGraph."""
    graph = GoalDependencyGraph()

    # Add goals
    goal1 = GoalNode(id="g1", domain="career", title="Get promotion")
    goal2 = GoalNode(id="g2", domain="finance", title="Save $50k")
    graph.add_goal(goal1)
    graph.add_goal(goal2)

    assert len(graph.nodes) == 2

    # Add dependency
    edge = DependencyEdge(
        from_goal_id="g1",
        to_goal_id="g2",
        relationship_type="enables",
        reason="Higher income enables savings",
    )
    graph.add_dependency(edge)

    assert len(graph.edges) == 1


def test_get_dependencies():
    """Test getting dependencies for a goal."""
    graph = GoalDependencyGraph()

    # Add goals
    goal1 = GoalNode(id="g1", domain="career", title="Get promotion")
    goal2 = GoalNode(id="g2", domain="finance", title="Save $50k")
    graph.add_goal(goal1)
    graph.add_goal(goal2)

    # Add dependencies
    edge1 = DependencyEdge(from_goal_id="g1", to_goal_id="g2", relationship_type="enables")
    edge2 = DependencyEdge(from_goal_id="g1", to_goal_id="g2", relationship_type="supports")
    graph.add_dependency(edge1)
    graph.add_dependency(edge2)

    # Get all dependencies for g2
    deps = graph.get_dependencies("g2")
    assert len(deps) == 2

    # Get filtered dependencies
    enables_deps = graph.get_dependencies("g2", relationship_type="enables")
    assert len(enables_deps) == 1
    assert enables_deps[0].relationship_type == "enables"


def test_get_dependents():
    """Test getting goals that depend on a goal."""
    graph = GoalDependencyGraph()

    # Add goals
    goal1 = GoalNode(id="g1", domain="career", title="Get promotion")
    goal2 = GoalNode(id="g2", domain="finance", title="Save $50k")
    goal3 = GoalNode(id="g3", domain="finance", title="Invest $20k")
    graph.add_goal(goal1)
    graph.add_goal(goal2)
    graph.add_goal(goal3)

    # Add dependencies
    edge1 = DependencyEdge(from_goal_id="g1", to_goal_id="g2", relationship_type="enables")
    edge2 = DependencyEdge(from_goal_id="g1", to_goal_id="g3", relationship_type="enables")
    graph.add_dependency(edge1)
    graph.add_dependency(edge2)

    # Get all dependents of g1
    dependents = graph.get_dependents("g1")
    assert len(dependents) == 2


def test_remove_goal():
    """Test removing a goal and its edges."""
    graph = GoalDependencyGraph()

    # Add goals
    goal1 = GoalNode(id="g1", domain="career", title="Get promotion")
    goal2 = GoalNode(id="g2", domain="finance", title="Save $50k")
    graph.add_goal(goal1)
    graph.add_goal(goal2)

    # Add dependency
    edge = DependencyEdge(from_goal_id="g1", to_goal_id="g2", relationship_type="enables")
    graph.add_dependency(edge)

    assert len(graph.nodes) == 2
    assert len(graph.edges) == 1

    # Remove goal
    graph.remove_goal("g1")

    assert len(graph.nodes) == 1
    assert len(graph.edges) == 0
    assert "g2" in graph.nodes


def test_update_goal():
    """Test updating goal attributes."""
    graph = GoalDependencyGraph()

    # Add goal
    goal1 = GoalNode(id="g1", domain="career", title="Get promotion", priority=5)
    graph.add_goal(goal1)

    assert graph.nodes["g1"].priority == 5

    # Update goal
    graph.update_goal("g1", priority=8, status="in_progress")

    assert graph.nodes["g1"].priority == 8
    assert graph.nodes["g1"].status == "in_progress"


# ==============================================================================
# Test Cycle Detection
# ==============================================================================


def test_detect_cycles_no_cycle():
    """Test cycle detection on a DAG without cycles."""
    graph = GoalDependencyGraph()

    # Add goals
    goal1 = GoalNode(id="g1", domain="career", title="Get promotion")
    goal2 = GoalNode(id="g2", domain="finance", title="Save $50k")
    goal3 = GoalNode(id="g3", domain="finance", title="Buy house")
    graph.add_goal(goal1)
    graph.add_goal(goal2)
    graph.add_goal(goal3)

    # Add dependencies (linear chain: g1 -> g2 -> g3)
    edge1 = DependencyEdge(from_goal_id="g1", to_goal_id="g2", relationship_type="enables")
    edge2 = DependencyEdge(from_goal_id="g2", to_goal_id="g3", relationship_type="enables")
    graph.add_dependency(edge1)
    graph.add_dependency(edge2)

    # Detect cycles
    cycles = graph.detect_cycles()

    assert len(cycles) == 0


def test_detect_cycles_with_cycle():
    """Test cycle detection on a graph with cycles."""
    graph = GoalDependencyGraph()

    # Add goals
    goal1 = GoalNode(id="g1", domain="career", title="Get promotion")
    goal2 = GoalNode(id="g2", domain="finance", title="Save $50k")
    goal3 = GoalNode(id="g3", domain="finance", title="Buy house")
    graph.add_goal(goal1)
    graph.add_goal(goal2)
    graph.add_goal(goal3)

    # Add dependencies (cycle: g1 -> g2 -> g3 -> g1)
    edge1 = DependencyEdge(from_goal_id="g1", to_goal_id="g2", relationship_type="requires")
    edge2 = DependencyEdge(from_goal_id="g2", to_goal_id="g3", relationship_type="requires")
    edge3 = DependencyEdge(from_goal_id="g3", to_goal_id="g1", relationship_type="requires")
    graph.add_dependency(edge1)
    graph.add_dependency(edge2)
    graph.add_dependency(edge3)

    # Detect cycles
    cycles = graph.detect_cycles()

    assert len(cycles) == 1
    # Cycle should contain all three goals (order may vary)
    assert len(cycles[0]) >= 3
    goal_ids_in_cycle = set([gid for gid in cycles[0] if gid in graph.nodes])
    assert goal_ids_in_cycle == {"g1", "g2", "g3"}


def test_detect_cycles_with_conflicts_ignored():
    """Test that conflict edges don't trigger cycle detection."""
    graph = GoalDependencyGraph()

    # Add goals
    goal1 = GoalNode(id="g1", domain="career", title="Get promotion")
    goal2 = GoalNode(id="g2", domain="finance", title="Save $50k")
    goal3 = GoalNode(id="g3", domain="wellness", title="Exercise daily")
    graph.add_goal(goal1)
    graph.add_goal(goal2)
    graph.add_goal(goal3)

    # Add dependencies (cycle with conflicts only: g1 -> g2 -> g3 --conflicts--> g1)
    edge1 = DependencyEdge(from_goal_id="g1", to_goal_id="g2", relationship_type="enables")
    edge2 = DependencyEdge(from_goal_id="g2", to_goal_id="g3", relationship_type="enables")
    edge3 = DependencyEdge(from_goal_id="g3", to_goal_id="g1", relationship_type="conflicts")
    graph.add_dependency(edge1)
    graph.add_dependency(edge2)
    graph.add_dependency(edge3)

    # Detect cycles (should be none, conflicts don't count)
    cycles = graph.detect_cycles()

    assert len(cycles) == 0


# ==============================================================================
# Test Topological Sort
# ==============================================================================


def test_topological_sort():
    """Test topological sorting of goals."""
    graph = GoalDependencyGraph()

    # Add goals
    goal1 = GoalNode(id="g1", domain="career", title="Get promotion")
    goal2 = GoalNode(id="g2", domain="finance", title="Save $50k")
    goal3 = GoalNode(id="g3", domain="finance", title="Buy house")
    graph.add_goal(goal1)
    graph.add_goal(goal2)
    graph.add_goal(goal3)

    # Add dependencies (g1 -> g2 -> g3)
    edge1 = DependencyEdge(from_goal_id="g1", to_goal_id="g2", relationship_type="enables")
    edge2 = DependencyEdge(from_goal_id="g2", to_goal_id="g3", relationship_type="requires")
    graph.add_dependency(edge1)
    graph.add_dependency(edge2)

    # Topological sort
    order = graph.topological_sort()

    assert len(order) == 3
    # g1 must come before g2, and g2 before g3
    assert order.index("g1") < order.index("g2")
    assert order.index("g2") < order.index("g3")


def test_topological_sort_with_cycle():
    """Test that topological sort raises error with cycles."""
    graph = GoalDependencyGraph()

    # Add goals
    goal1 = GoalNode(id="g1", domain="career", title="Get promotion")
    goal2 = GoalNode(id="g2", domain="finance", title="Save $50k")
    graph.add_goal(goal1)
    graph.add_goal(goal2)

    # Add circular dependency
    edge = DependencyEdge(from_goal_id="g1", to_goal_id="g2", relationship_type="requires")
    edge2 = DependencyEdge(from_goal_id="g2", to_goal_id="g1", relationship_type="requires")
    graph.add_dependency(edge)
    graph.add_dependency(edge2)

    # Should raise ValueError
    try:
        order = graph.topological_sort()
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "cycles" in str(e).lower()


# ==============================================================================
# Test Critical Path Analysis
# ==============================================================================


def test_find_critical_path():
    """Test finding critical path in dependency graph."""
    graph = GoalDependencyGraph()

    # Add goals with estimated effort
    goal1 = GoalNode(
        id="g1",
        domain="career",
        title="Get promotion",
        estimated_effort=20.0,
    )
    goal2 = GoalNode(
        id="g2",
        domain="finance",
        title="Save $50k",
        estimated_effort=30.0,
    )
    goal3 = GoalNode(
        id="g3",
        domain="finance",
        title="Buy house",
        estimated_effort=15.0,
    )
    graph.add_goal(goal1)
    graph.add_goal(goal2)
    graph.add_goal(goal3)

    # Add dependencies (g1 -> g2 -> g3)
    edge1 = DependencyEdge(from_goal_id="g1", to_goal_id="g2", relationship_type="enables")
    edge2 = DependencyEdge(from_goal_id="g2", to_goal_id="g3", relationship_type="requires")
    graph.add_dependency(edge1)
    graph.add_dependency(edge2)

    # Find critical path
    critical_path, total_effort = graph.find_critical_path()

    assert len(critical_path) == 3
    assert total_effort == 65.0  # 20 + 30 + 15
    assert "g1" in critical_path
    assert "g2" in critical_path
    assert "g3" in critical_path


def test_find_critical_path_with_branch():
    """Test finding critical path with multiple branches."""
    graph = GoalDependencyGraph()

    # Add goals
    goal1 = GoalNode(
        id="g1",
        domain="career",
        title="Get promotion",
        estimated_effort=20.0,
    )
    goal2 = GoalNode(
        id="g2",
        domain="finance",
        title="Save $50k",
        estimated_effort=30.0,
    )
    goal3 = GoalNode(
        id="g3",
        domain="wellness",
        title="Exercise daily",
        estimated_effort=10.0,  # Short branch
    )
    goal4 = GoalNode(
        id="g4",
        domain="finance",
        title="Buy house",
        estimated_effort=15.0,
    )
    graph.add_goal(goal1)
    graph.add_goal(goal2)
    graph.add_goal(goal3)
    graph.add_goal(goal4)

    # Add dependencies (g1 -> g2 and g1 -> g3, then both to g4)
    edge1 = DependencyEdge(from_goal_id="g1", to_goal_id="g2", relationship_type="enables")
    edge2 = DependencyEdge(from_goal_id="g1", to_goal_id="g3", relationship_type="supports")
    edge3 = DependencyEdge(from_goal_id="g2", to_goal_id="g4", relationship_type="requires")
    edge4 = DependencyEdge(from_goal_id="g3", to_goal_id="g4", relationship_type="supports")
    graph.add_dependency(edge1)
    graph.add_dependency(edge2)
    graph.add_dependency(edge3)
    graph.add_dependency(edge4)

    # Find critical path (should be g1 -> g2 -> g4 = 20 + 30 + 15 = 65)
    critical_path, total_effort = graph.find_critical_path()

    assert total_effort == 65.0
    # Critical path should include g1, g2, g4 (the longer branch)
    assert "g1" in critical_path
    assert "g2" in critical_path


# ==============================================================================
# Test Impact Simulation
# ==============================================================================


def test_simulate_impact_success():
    """Test simulating successful goal completion."""
    graph = GoalDependencyGraph()

    # Add goals
    goal1 = GoalNode(id="g1", domain="career", title="Get promotion")
    goal2 = GoalNode(id="g2", domain="finance", title="Save $50k")
    goal3 = GoalNode(id="g3", domain="wellness", title="Exercise daily")
    graph.add_goal(goal1)
    graph.add_goal(goal2)
    graph.add_goal(goal3)

    # Add dependencies
    edge1 = DependencyEdge(from_goal_id="g1", to_goal_id="g2", relationship_type="enables")
    edge2 = DependencyEdge(from_goal_id="g1", to_goal_id="g3", relationship_type="supports")
    graph.add_dependency(edge1)
    graph.add_dependency(edge2)

    # Simulate success
    affected = graph.simulate_impact("g1", "success")

    # Should positively affect g2 and g3
    assert len(affected["positively_affected"]) == 2
    assert "g2" in [a["goal_id"] for a in affected["positively_affected"]]
    assert "g3" in [a["goal_id"] for a in affected["positively_affected"]]
    assert len(affected["negatively_affected"]) == 0
    assert len(affected["blocked"]) == 0


def test_simulate_impact_failure():
    """Test simulating goal failure."""
    graph = GoalDependencyGraph()

    # Add goals
    goal1 = GoalNode(id="g1", domain="career", title="Get promotion")
    goal2 = GoalNode(id="g2", domain="finance", title="Save $50k")
    goal3 = GoalNode(id="g3", domain="wellness", title="Exercise daily")
    graph.add_goal(goal1)
    graph.add_goal(goal2)
    graph.add_goal(goal3)

    # Add dependencies
    edge1 = DependencyEdge(from_goal_id="g1", to_goal_id="g2", relationship_type="requires")
    edge2 = DependencyEdge(from_goal_id="g1", to_goal_id="g3", relationship_type="supports")
    graph.add_dependency(edge1)
    graph.add_dependency(edge2)

    # Simulate failure
    affected = graph.simulate_impact("g1", "failure")

    # Should block g2 (requires) and negatively affect g3 (supports)
    assert len(affected["blocked"]) == 1
    assert "g2" in [a["goal_id"] for a in affected["blocked"]]
    assert len(affected["negatively_affected"]) == 1
    assert "g3" in [a["goal_id"] for a in affected["negatively_affected"]]
    assert len(affected["positively_affected"]) == 0


def test_simulate_impact_conflicts():
    """Test simulating impact with conflicts."""
    graph = GoalDependencyGraph()

    # Add goals
    goal1 = GoalNode(id="g1", domain="career", title="Get promotion")
    goal2 = GoalNode(id="g2", domain="wellness", title="Exercise daily")
    graph.add_goal(goal1)
    graph.add_goal(goal2)

    # Add conflict
    edge = DependencyEdge(from_goal_id="g1", to_goal_id="g2", relationship_type="conflicts")
    graph.add_dependency(edge)

    # Simulate success of g1 (should conflict with g2)
    affected = graph.simulate_impact("g1", "success")

    assert len(affected["negatively_affected"]) == 1
    assert "g2" in [a["goal_id"] for a in affected["negatively_affected"]]
    assert "conflict" in affected["negatively_affected"][0]["reason"].lower()


# ==============================================================================
# Test Implicit Dependency Detection
# ==============================================================================


def test_detect_implicit_dependencies_keywords():
    """Test detecting implicit dependencies based on keyword overlap."""
    goals = [
        GoalNode(id="g1", domain="career", title="Learn Python programming"),
        GoalNode(
            id="g2",
            domain="career",
            title="Build Python projects for portfolio",
        ),
    ]

    edges = []

    suggestions = detect_implicit_dependencies(goals, edges)

    # The function should return a list (may be empty if no strong pattern detected)
    assert isinstance(suggestions, list)

    # If suggestions found, they should have the required structure
    for s in suggestions:
        assert "from_goal_id" in s
        assert "to_goal_id" in s
        assert "relationship_type" in s
        assert "confidence" in s
        assert 0 <= s["confidence"] <= 1


def test_detect_implicit_dependencies_complementary_domains():
    """Test detecting implicit dependencies based on complementary domains."""
    goals = [
        GoalNode(id="g1", domain="career", title="Get promotion"),
        GoalNode(id="g2", domain="finance", title="Save money"),
    ]

    edges = []

    suggestions = detect_implicit_dependencies(goals, edges)

    # Should suggest a relationship due to complementary domains
    assert len(suggestions) > 0


def test_detect_implicit_dependencies_no_duplicates():
    """Test that existing dependencies are not suggested."""
    goals = [
        GoalNode(id="g1", domain="career", title="Get promotion"),
        GoalNode(id="g2", domain="finance", title="Save money"),
    ]

    # Add existing dependency
    edges = [DependencyEdge(from_goal_id="g1", to_goal_id="g2", relationship_type="enables")]

    suggestions = detect_implicit_dependencies(goals, edges)

    # Should not suggest duplicate relationships
    for suggestion in suggestions:
        assert suggestion["from_goal_id"] != "g1" or suggestion["to_goal_id"] != "g2"


# ==============================================================================
# Test Conflict Resolution
# ==============================================================================


def test_suggest_conflict_resolution():
    """Test suggesting conflict resolution strategies."""
    goal1 = GoalNode(id="g1", domain="career", title="Get promotion", priority=8)
    goal2 = GoalNode(id="g2", domain="wellness", title="Exercise daily", priority=6)
    edge = DependencyEdge(
        from_goal_id="g1",
        to_goal_id="g2",
        relationship_type="conflicts",
        reason="Time competition",
    )

    resolutions = suggest_conflict_resolution(goal1, goal2, edge)

    # Should return multiple resolution strategies
    assert len(resolutions) > 0

    # All resolutions should be strings (text descriptions)
    for r in resolutions:
        assert isinstance(r, str)
        # Should be a meaningful suggestion (not empty or just whitespace)
        assert len(r.strip()) > 0


def test_suggest_conflict_resolution_with_deadlines():
    """Test conflict resolution with deadlines."""
    goal1 = GoalNode(
        id="g1",
        domain="career",
        title="Get promotion",
        priority=5,
        deadline="2025-06-01",
    )
    goal2 = GoalNode(
        id="g2",
        domain="wellness",
        title="Exercise daily",
        priority=5,
        deadline="2025-07-01",
    )
    edge = DependencyEdge(from_goal_id="g1", to_goal_id="g2", relationship_type="conflicts")

    resolutions = suggest_conflict_resolution(goal1, goal2, edge)

    # Should reference deadlines in suggestions
    assert any("deadline" in r.lower() for r in resolutions)


# ==============================================================================
# Test Visualization
# ==============================================================================


def test_visualize_dependency_graph_text_basic():
    """Test basic text-based visualization."""
    graph = GoalDependencyGraph()

    # Add goals
    goal1 = GoalNode(id="g1", domain="career", title="Get promotion", priority=8)
    goal2 = GoalNode(id="g2", domain="finance", title="Save $50k", priority=7)
    graph.add_goal(goal1)
    graph.add_goal(goal2)

    # Generate visualization
    viz = visualize_dependency_graph_text(graph)

    assert "GOAL DEPENDENCY GRAPH" in viz
    assert "CAREER DOMAIN" in viz
    assert "FINANCE DOMAIN" in viz
    assert goal1.title in viz
    assert goal2.title in viz


def test_visualize_dependency_graph_text_focused():
    """Test focused view visualization."""
    graph = GoalDependencyGraph()

    # Add goals
    goal1 = GoalNode(id="g1", domain="career", title="Get promotion")
    goal2 = GoalNode(
        id="g2",
        domain="finance",
        title="Save $50k",
    )
    goal3 = GoalNode(
        id="g3",
        domain="wellness",
        title="Exercise daily",
    )
    graph.add_goal(goal1)
    graph.add_goal(goal2)
    graph.add_goal(goal3)

    # Add dependencies
    edge1 = DependencyEdge(from_goal_id="g2", to_goal_id="g1", relationship_type="requires")
    edge2 = DependencyEdge(from_goal_id="g1", to_goal_id="g3", relationship_type="conflicts")
    graph.add_dependency(edge1)
    graph.add_dependency(edge2)

    # Generate focused visualization
    viz = visualize_dependency_graph_text(graph, focus_goal_id="g1")

    assert "Focused View" in viz
    assert goal1.title in viz
    # Should show dependencies and dependents
    assert "Dependencies" in viz or "Dependents" in viz


def test_visualize_dependency_graph_text_with_cycles():
    """Test visualization with cycle warnings."""
    graph = GoalDependencyGraph()

    # Add goals
    goal1 = GoalNode(id="g1", domain="career", title="Get promotion")
    goal2 = GoalNode(id="g2", domain="finance", title="Save $50k")
    graph.add_goal(goal1)
    graph.add_goal(goal2)

    # Add circular dependency
    edge = DependencyEdge(from_goal_id="g1", to_goal_id="g2", relationship_type="requires")
    edge2 = DependencyEdge(from_goal_id="g2", to_goal_id="g1", relationship_type="requires")
    graph.add_dependency(edge)
    graph.add_dependency(edge2)

    # Generate visualization
    viz = visualize_dependency_graph_text(graph)

    assert "CIRCULAR DEPENDENCIES" in viz
    assert "WARNING" in viz


# ==============================================================================
# Integration Tests
# ==============================================================================


def test_full_workflow():
    """Test complete workflow from graph creation to analysis."""
    # Create graph
    graph = GoalDependencyGraph()

    # Add goals with full details
    goals = [
        GoalNode(
            id="g1",
            domain="career",
            title="Get promotion",
            priority=8,
            estimated_effort=40.0,
        ),
        GoalNode(
            id="g2",
            domain="finance",
            title="Save $50k for down payment",
            priority=7,
            estimated_effort=60.0,
        ),
        GoalNode(
            id="g3",
            domain="finance",
            title="Buy house",
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
            reason="Higher income enables savings",
        ),
        DependencyEdge(
            from_goal_id="g2",
            to_goal_id="g3",
            relationship_type="requires",
            reason="Need down payment for house",
        ),
    ]
    for edge in edges:
        graph.add_dependency(edge)

    # Test cycle detection
    cycles = graph.detect_cycles()
    assert len(cycles) == 0

    # Test topological sort
    order = graph.topological_sort()
    assert len(order) == 3

    # Test critical path
    critical_path, total_effort = graph.find_critical_path()
    assert len(critical_path) > 0
    assert total_effort == 120.0

    # Test impact simulation
    affected = graph.simulate_impact("g1", "success")
    assert len(affected["positively_affected"]) > 0

    # Test visualization
    viz = visualize_dependency_graph_text(graph)
    assert "GOAL DEPENDENCY GRAPH" in viz

    # Test graph serialization
    graph_dict = graph.to_dict()
    assert "nodes" in graph_dict
    assert "edges" in graph_dict
    assert len(graph_dict["nodes"]) == 3


if __name__ == "__main__":
    # Run tests
    print("Running Goal Dependency Tools Tests...")
    print("=" * 60)

    test_goal_node_creation()
    print("✓ GoalNode creation test passed")

    test_dependency_edge_creation()
    print("✓ DependencyEdge creation test passed")

    test_goal_dependency_graph_creation()
    print("✓ GoalDependencyGraph creation test passed")

    test_get_dependencies()
    print("✓ Get dependencies test passed")

    test_get_dependents()
    print("✓ Get dependents test passed")

    test_remove_goal()
    print("✓ Remove goal test passed")

    test_update_goal()
    print("✓ Update goal test passed")

    test_detect_cycles_no_cycle()
    print("✓ Detect cycles (no cycle) test passed")

    test_detect_cycles_with_cycle()
    print("✓ Detect cycles (with cycle) test passed")

    test_detect_cycles_with_conflicts_ignored()
    print("✓ Detect cycles (conflicts ignored) test passed")

    test_topological_sort()
    print("✓ Topological sort test passed")

    test_topological_sort_with_cycle()
    print("✓ Topological sort (with cycle) test passed")

    test_find_critical_path()
    print("✓ Find critical path test passed")

    test_find_critical_path_with_branch()
    print("✓ Find critical path (with branch) test passed")

    test_simulate_impact_success()
    print("✓ Simulate impact (success) test passed")

    test_simulate_impact_failure()
    print("✓ Simulate impact (failure) test passed")

    test_simulate_impact_conflicts()
    print("✓ Simulate impact (conflicts) test passed")

    test_detect_implicit_dependencies_keywords()
    print("✓ Detect implicit dependencies (keywords) test passed")

    test_detect_implicit_dependencies_complementary_domains()
    print("✓ Detect implicit dependencies (complementary domains) test passed")

    test_detect_implicit_dependencies_no_duplicates()
    print("✓ Detect implicit dependencies (no duplicates) test passed")

    test_suggest_conflict_resolution()
    print("✓ Suggest conflict resolution test passed")

    test_suggest_conflict_resolution_with_deadlines()
    print("✓ Suggest conflict resolution (with deadlines) test passed")

    test_visualize_dependency_graph_text_basic()
    print("✓ Visualize dependency graph (basic) test passed")

    test_visualize_dependency_graph_text_focused()
    print("✓ Visualize dependency graph (focused) test passed")

    test_visualize_dependency_graph_text_with_cycles()
    print("✓ Visualize dependency graph (with cycles) test passed")

    test_full_workflow()
    print("✓ Full workflow integration test passed")

    print("=" * 60)
    print("All tests passed!")
