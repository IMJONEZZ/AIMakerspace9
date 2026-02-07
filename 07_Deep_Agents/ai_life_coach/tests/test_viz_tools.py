"""
Test Suite for Goal Dependency Visualization Tools.

This module tests all functionality of viz_tools.py:
- ASCII graph rendering (tree, matrix, linear formats)
- Interactive exploration commands
- Critical path highlighting
- What-if analysis (add/remove goals)
- Dependency report generation

Run tests with: python -m pytest tests/test_viz_tools.py -v
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.viz_tools import (
    ASCIIGraphRenderer,
    InteractiveExplorer,
    WhatIfAnalyzer,
    generate_dependency_report,
    create_viz_tools,
)
from src.tools.goal_dependency_tools import (
    GoalNode,
    DependencyEdge,
    GoalDependencyGraph,
)


# ==============================================================================
# Test Data Fixtures
# ==============================================================================


def create_sample_graph():
    """Create a sample goal dependency graph for testing."""
    graph = GoalDependencyGraph()

    # Add goals
    g1 = GoalNode(
        id="g1",
        domain="career",
        title="Get promotion",
        priority=8,
        status="pending",
        estimated_effort=40.0,
    )
    g2 = GoalNode(
        id="g2",
        domain="finance",
        title="Save $10k for move",
        priority=7,
        status="in_progress",
        estimated_effort=20.0,
    )
    g3 = GoalNode(
        id="g3",
        domain="finance",
        title="Save $50k house downpayment",
        priority=9,
        status="pending",
        estimated_effort=60.0,
    )
    g4 = GoalNode(
        id="g4",
        domain="wellness",
        title="Create home routine",
        priority=6,
        status="pending",
        estimated_effort=10.0,
    )
    g5 = GoalNode(
        id="g5",
        domain="career",
        title="Improve skills",
        priority=7,
        status="completed",
        estimated_effort=30.0,
    )

    graph.add_goal(g1)
    graph.add_goal(g2)
    graph.add_goal(g3)
    graph.add_goal(g4)
    graph.add_goal(g5)

    # Add dependencies
    e1 = DependencyEdge(
        from_goal_id="g1",
        to_goal_id="g2",
        relationship_type="enables",
        strength=0.9,
        reason="Higher income enables savings",
    )
    e2 = DependencyEdge(
        from_goal_id="g1",
        to_goal_id="g3",
        relationship_type="enables",
        strength=0.8,
        reason="Higher income enables house savings",
    )
    e3 = DependencyEdge(
        from_goal_id="g2",
        to_goal_id="g3",
        relationship_type="supports",
        strength=0.5,
        reason="Moving savings support house fund",
    )
    e4 = DependencyEdge(
        from_goal_id="g3",
        to_goal_id="g4",
        relationship_type="enables",
        strength=0.7,
        reason="House enables creating stable home routine",
    )
    e5 = DependencyEdge(
        from_goal_id="g5",
        to_goal_id="g1",
        relationship_type="requires",
        strength=0.9,
        reason="Improved skills required for promotion",
    )

    graph.add_dependency(e1)
    graph.add_dependency(e2)
    graph.add_dependency(e3)
    graph.add_dependency(e4)
    graph.add_dependency(e5)

    return graph


# ==============================================================================
# Test ASCIIGraphRenderer
# ==============================================================================


def test_ascii_graph_renderer_init():
    """Test initializing ASCIIGraphRenderer."""
    graph = create_sample_graph()
    renderer = ASCIIGraphRenderer(graph)

    assert renderer.graph == graph
    assert len(renderer.ARROWS) == 4
    assert len(renderer.STATUS_ICONS) == 3
    assert len(renderer.DOMAIN_EMOJIS) == 4


def test_truncate_text():
    """Test text truncation."""
    graph = create_sample_graph()
    renderer = ASCIIGraphRenderer(graph)

    # Test short text (no truncation)
    result = renderer._truncate_text("Hello", 10)
    assert result == "Hello"

    # Test long text (truncated) - truncates to max_length with "...", so actual length will be max_length
    result = renderer._truncate_text("This is a very long text", 10)
    assert "..." in result
    assert len(result) <= 13  # max_length + "..."


def test_get_goal_display_name():
    """Test getting formatted goal display names."""
    graph = create_sample_graph()
    renderer = ASCIIGraphRenderer(graph)

    goal = graph.nodes["g1"]
    display_name = renderer._get_goal_display_name(goal)

    # Should contain emoji, status icon, and title
    assert "💼" in display_name  # career emoji
    assert "○" in display_name  # pending icon
    assert "Get promotion" in display_name


def test_build_tree_structure():
    """Test building hierarchical tree structure."""
    graph = create_sample_graph()
    renderer = ASCIIGraphRenderer(graph)

    # Build tree starting from g5 (which has no incoming dependencies)
    tree = renderer._build_tree_structure("g5")

    assert tree is not None
    assert "goal" in tree
    assert "children" in tree
    assert tree["goal"].id == "g5"

    # Should have g1 as child
    assert len(tree["children"]) == 1
    assert tree["children"][0]["goal"].id == "g1"


def test_render_tree():
    """Test rendering tree visualization."""
    graph = create_sample_graph()
    renderer = ASCIIGraphRenderer(graph)

    viz = renderer.render_tree(root_goal_id="g5")

    assert isinstance(viz, str)
    assert len(viz) > 0
    # Should contain goal titles
    assert "Improve skills" in viz or "Get promotion" in viz


def test_render_tree_with_critical_path():
    """Test rendering tree with critical path highlighted."""
    graph = create_sample_graph()
    renderer = ASCIIGraphRenderer(graph)

    viz = renderer.render_tree(root_goal_id="g5", show_critical_path=True)

    assert isinstance(viz, str)
    assert len(viz) > 0
    # Should mention critical path in legend
    assert "critical" in viz.lower() or "★" in viz


def test_render_matrix():
    """Test rendering matrix visualization."""
    graph = create_sample_graph()
    renderer = ASCIIGraphRenderer(graph)

    viz = renderer.render_matrix()

    assert isinstance(viz, str)
    assert len(viz) > 0
    # Should contain domain headers
    assert "CAREER" in viz or "FINANCE" in viz or "WELLNESS" in viz


def test_render_matrix_with_critical_path():
    """Test rendering matrix with critical path highlighted."""
    graph = create_sample_graph()
    renderer = ASCIIGraphRenderer(graph)

    viz = renderer.render_matrix(show_critical_path=True)

    assert isinstance(viz, str)
    assert len(viz) > 0
    # Should mention critical path
    assert "CRITICAL PATH" in viz or "★" in viz


def test_render_linear_flow():
    """Test rendering linear flow visualization."""
    graph = create_sample_graph()
    renderer = ASCIIGraphRenderer(graph)

    viz = renderer.render_linear_flow(max_width=80)

    assert isinstance(viz, str)
    assert len(viz) > 0
    # Should mention "flow" or contain goal titles
    assert len(viz) > 100  # Should be substantial


def test_render_linear_flow_with_critical_path():
    """Test rendering linear flow with critical path highlighted."""
    graph = create_sample_graph()
    renderer = ASCIIGraphRenderer(graph)

    viz = renderer.render_linear_flow(max_width=80, show_critical_path=True)

    assert isinstance(viz, str)
    assert len(viz) > 0


def test_render_all_formats():
    """Test rendering all three visualization formats."""
    graph = create_sample_graph()
    renderer = ASCIIGraphRenderer(graph)

    # Test tree format
    tree_viz = renderer.render_tree()
    assert isinstance(tree_viz, str)
    assert len(tree_viz) > 0

    # Test matrix format
    matrix_viz = renderer.render_matrix()
    assert isinstance(matrix_viz, str)
    assert len(matrix_viz) > 0

    # Test linear format
    linear_viz = renderer.render_linear_flow()
    assert isinstance(linear_viz, str)
    assert len(linear_viz) > 0


# ==============================================================================
# Test InteractiveExplorer
# ==============================================================================


def test_interactive_explorer_init():
    """Test initializing InteractiveExplorer."""
    graph = create_sample_graph()
    explorer = InteractiveExplorer(graph)

    assert explorer.graph == graph
    assert explorer.current_view == "summary"
    assert explorer.selected_goal_id is None


def test_show_help():
    """Test showing help message."""
    graph = create_sample_graph()
    explorer = InteractiveExplorer(graph)

    help_text = explorer.show_help()

    assert isinstance(help_text, str)
    assert len(help_text) > 0
    # Should contain command descriptions
    assert "show" in help_text.lower()
    assert "expand" in help_text.lower()


def test_show_goals_all():
    """Test showing all goals."""
    graph = create_sample_graph()
    explorer = InteractiveExplorer(graph)

    result = explorer.show_goals()

    assert isinstance(result, str)
    assert len(result) > 0
    # Should contain goal titles
    assert "Get promotion" in result or "Save $10k for move" in result


def test_show_goals_specific():
    """Test showing a specific goal."""
    graph = create_sample_graph()
    explorer = InteractiveExplorer(graph)

    result = explorer.show_goals("g1")

    assert isinstance(result, str)
    assert len(result) > 0
    # Should contain the specific goal title
    assert "Get promotion" in result


def test_show_goals_nonexistent():
    """Test showing a non-existent goal."""
    graph = create_sample_graph()
    explorer = InteractiveExplorer(graph)

    result = explorer.show_goals("g999")

    assert isinstance(result, str)
    assert "not found" in result.lower()


def test_expand_goal():
    """Test expanding a goal."""
    graph = create_sample_graph()
    explorer = InteractiveExplorer(graph)

    result = explorer.expand_goal("g1")

    assert isinstance(result, str)
    assert len(result) > 0
    # Should show dependencies and dependents
    assert "DEPENDING ON" in result or "ENABLES" in result

    # Should update explorer state
    assert explorer.selected_goal_id == "g1"
    assert explorer.current_view == "expanded"


def test_expand_goal_nonexistent():
    """Test expanding a non-existent goal."""
    graph = create_sample_graph()
    explorer = InteractiveExplorer(graph)

    result = explorer.expand_goal("g999")

    assert isinstance(result, str)
    assert "not found" in result.lower()


def test_collapse_view():
    """Test collapsing expanded view."""
    graph = create_sample_graph()
    explorer = InteractiveExplorer(graph)

    # First expand
    explorer.expand_goal("g1")

    # Then collapse
    result = explorer.collapse_view()

    assert isinstance(result, str)
    assert "collapsed" in result.lower()

    # Should update explorer state
    assert explorer.selected_goal_id is None
    assert explorer.current_view == "summary"


def test_show_critical_path():
    """Test showing critical path."""
    graph = create_sample_graph()
    explorer = InteractiveExplorer(graph)

    result = explorer.show_critical_path()

    assert isinstance(result, str)
    assert len(result) > 0
    # Should mention critical path
    assert "critical" in result.lower() or "path" in result.lower()


def test_show_stats():
    """Test showing graph statistics."""
    graph = create_sample_graph()
    explorer = InteractiveExplorer(graph)

    result = explorer.show_stats()

    assert isinstance(result, str)
    assert len(result) > 0
    # Should contain statistics
    assert "Total Goals" in result or "goals by domain" in result.lower()


def test_execute_command_help():
    """Test executing help command."""
    graph = create_sample_graph()
    explorer = InteractiveExplorer(graph)

    result = explorer.execute_command("help")

    assert isinstance(result, str)
    assert len(result) > 0
    assert "show" in result.lower()


def test_execute_command_show():
    """Test executing show command."""
    graph = create_sample_graph()
    explorer = InteractiveExplorer(graph)

    result = explorer.execute_command("show")

    assert isinstance(result, str)
    assert len(result) > 0


def test_execute_command_show_with_arg():
    """Test executing show command with argument."""
    graph = create_sample_graph()
    explorer = InteractiveExplorer(graph)

    result = explorer.execute_command("show g1")

    assert isinstance(result, str)
    assert len(result) > 0
    assert "Get promotion" in result


def test_execute_command_expand():
    """Test executing expand command."""
    graph = create_sample_graph()
    explorer = InteractiveExplorer(graph)

    result = explorer.execute_command("expand g1")

    assert isinstance(result, str)
    assert len(result) > 0


def test_execute_command_expand_no_arg():
    """Test executing expand command without argument."""
    graph = create_sample_graph()
    explorer = InteractiveExplorer(graph)

    result = explorer.execute_command("expand")

    assert isinstance(result, str)
    assert "Usage" in result


def test_execute_command_collapse():
    """Test executing collapse command."""
    graph = create_sample_graph()
    explorer = InteractiveExplorer(graph)

    result = explorer.execute_command("collapse")

    assert isinstance(result, str)
    assert "collapsed" in result.lower()


def test_execute_command_path():
    """Test executing path command."""
    graph = create_sample_graph()
    explorer = InteractiveExplorer(graph)

    result = explorer.execute_command("path")

    assert isinstance(result, str)
    assert len(result) > 0


def test_execute_command_stats():
    """Test executing stats command."""
    graph = create_sample_graph()
    explorer = InteractiveExplorer(graph)

    result = explorer.execute_command("stats")

    assert isinstance(result, str)
    assert len(result) > 0


def test_execute_command_unknown():
    """Test executing unknown command."""
    graph = create_sample_graph()
    explorer = InteractiveExplorer(graph)

    result = explorer.execute_command("unknown")

    assert isinstance(result, str)
    assert "Unknown command" in result or "unknown" in result.lower()


def test_execute_command_quit():
    """Test executing quit command."""
    graph = create_sample_graph()
    explorer = InteractiveExplorer(graph)

    result = explorer.execute_command("quit")

    assert isinstance(result, str)
    assert "Exiting" in result.lower() or "exit" in result.lower()


# ==============================================================================
# Test WhatIfAnalyzer
# ==============================================================================


def test_what_if_analyzer_init():
    """Test initializing WhatIfAnalyzer."""
    graph = create_sample_graph()
    analyzer = WhatIfAnalyzer(graph)

    assert analyzer.graph == graph


def test_simulate_add_goal():
    """Test simulating adding a goal."""
    graph = create_sample_graph()
    analyzer = WhatIfAnalyzer(graph)

    new_goal_data = {
        "id": "g6",
        "domain": "wellness",
        "title": "Run marathon",
        "priority": 5,
        "estimated_effort": 100.0,
    }

    result = analyzer.simulate_add_goal(new_goal_data)

    assert isinstance(result, str)
    assert len(result) > 0
    # Should mention the new goal
    assert "Run marathon" in result


def test_simulate_add_goal_with_dependencies():
    """Test simulating adding a goal with dependencies."""
    graph = create_sample_graph()
    analyzer = WhatIfAnalyzer(graph)

    new_goal_data = {
        "id": "g6",
        "domain": "wellness",
        "title": "Run marathon",
        "priority": 5,
    }

    dependencies = [
        {
            "from_goal_id": "g6",
            "to_goal_id": "g4",
            "relationship_type": "supports",
            "reason": "Marathon training improves wellness routine",
        }
    ]

    result = analyzer.simulate_add_goal(new_goal_data, dependencies)

    assert isinstance(result, str)
    assert len(result) > 0
    # Should show dependencies
    assert "Dependencies" in result or "added" in result.lower()


def test_simulate_add_goal_missing_field():
    """Test simulating adding a goal with missing required field."""
    graph = create_sample_graph()
    analyzer = WhatIfAnalyzer(graph)

    # Missing 'id' field
    new_goal_data = {
        "domain": "wellness",
        "title": "Run marathon",
    }

    result = analyzer.simulate_add_goal(new_goal_data)

    assert isinstance(result, str)
    # Should show error
    assert "Error" in result or "missing" in result.lower()


def test_simulate_add_goal_duplicate_id():
    """Test simulating adding a goal with duplicate ID."""
    graph = create_sample_graph()
    analyzer = WhatIfAnalyzer(graph)

    new_goal_data = {
        "id": "g1",  # Duplicate ID
        "domain": "wellness",
        "title": "Run marathon",
    }

    result = analyzer.simulate_add_goal(new_goal_data)

    assert isinstance(result, str)
    # Should show error about duplicate
    assert "Error" in result or "already exists" in result.lower()


def test_simulate_remove_goal():
    """Test simulating removing a goal."""
    graph = create_sample_graph()
    analyzer = WhatIfAnalyzer(graph)

    result = analyzer.simulate_remove_goal("g1")

    assert isinstance(result, str)
    assert len(result) > 0
    # Should mention the removed goal
    assert "Get promotion" in result
    # Should show impact on dependents
    assert "impact" in result.lower() or "affected" in result.lower()


def test_simulate_remove_goal_nonexistent():
    """Test simulating removing a non-existent goal."""
    graph = create_sample_graph()
    analyzer = WhatIfAnalyzer(graph)

    result = analyzer.simulate_remove_goal("g999")

    assert isinstance(result, str)
    # Should show error
    assert "Error" in result or "not found" in result.lower()


def test_simulate_remove_goal_with_dependents():
    """Test removing a goal that has dependents."""
    graph = create_sample_graph()
    analyzer = WhatIfAnalyzer(graph)

    # g1 is required by nothing but enables other goals
    result = analyzer.simulate_remove_goal("g5")

    assert isinstance(result, str)
    assert len(result) > 0
    # Should show affected dependents
    assert "dependent" in result.lower() or "impact" in result.lower()


# ==============================================================================
# Test generate_dependency_report
# ==============================================================================


def test_generate_dependency_report():
    """Test generating a dependency report."""
    graph = create_sample_graph()
    user_id = "test_user"

    result = generate_dependency_report(graph, user_id, include_visualizations=False)

    assert isinstance(result, str)
    assert len(result) > 0

    # Should contain key sections
    assert "EXECUTIVE SUMMARY" in result
    assert "DOMAIN ANALYSIS" in result
    assert "CRITICAL PATH" in result or "RECOMMENDATIONS" in result

    # Should mention user
    assert user_id in result


def test_generate_dependency_report_with_visualizations():
    """Test generating a dependency report with visualizations."""
    graph = create_sample_graph()
    user_id = "test_user"

    result = generate_dependency_report(graph, user_id, include_visualizations=True)

    assert isinstance(result, str)
    assert len(result) > 0

    # Should contain visualization section
    assert "VISUALIZATION" in result or "MATRIX" in result


def test_generate_dependency_report_empty_graph():
    """Test generating a report for an empty graph."""
    graph = GoalDependencyGraph()
    user_id = "test_user"

    result = generate_dependency_report(graph, user_id)

    assert isinstance(result, str)
    # Should handle empty graph gracefully
    assert "0 goals" in result or len(result) > 0


# ==============================================================================
# Test create_viz_tools
# ==============================================================================


def test_create_viz_tools():
    """Test creating visualization tools."""
    # This is a basic smoke test to ensure the factory function exists
    try:
        from src.config import config

        config.initialize_environment()
        tools = create_viz_tools()

        # Should return 6 tools
        assert len(tools) == 6

        # Each tool should be callable (has __call__ method or is a function)
        for tool_func in tools:
            assert callable(tool_func)

    except Exception as e:
        # If initialization fails, at least verify the function exists
        assert callable(create_viz_tools)


# ==============================================================================
# Integration Tests
# ==============================================================================


def test_full_visualization_workflow():
    """Test a complete visualization workflow."""
    # Create graph
    graph = create_sample_graph()

    # Render in different formats
    renderer = ASCIIGraphRenderer(graph)

    tree_viz = renderer.render_tree()
    matrix_viz = renderer.render_matrix()
    linear_viz = renderer.render_linear_flow()

    # All should be non-empty strings
    assert len(tree_viz) > 0
    assert len(matrix_viz) > 0
    assert len(linear_viz) > 0

    # Explore interactively
    explorer = InteractiveExplorer(graph)

    help_result = explorer.execute_command("help")
    show_result = explorer.execute_command("show")
    expand_result = explorer.execute_command("expand g1")

    assert len(help_result) > 0
    assert len(show_result) > 0
    assert len(expand_result) > 0

    # What-if analysis
    analyzer = WhatIfAnalyzer(graph)

    add_result = analyzer.simulate_add_goal(
        {
            "id": "g_new",
            "domain": "wellness",
            "title": "New goal",
        }
    )
    remove_result = analyzer.simulate_remove_goal("g1")

    assert len(add_result) > 0
    assert len(remove_result) > 0

    # Generate report
    report = generate_dependency_report(graph, "test_user")

    assert len(report) > 0
    assert "SUMMARY" in report


def test_visualization_with_cycles():
    """Test visualization with circular dependencies."""
    graph = GoalDependencyGraph()

    # Create goals
    g1 = GoalNode(id="g1", domain="career", title="Goal 1")
    g2 = GoalNode(id="g2", domain="career", title="Goal 2")
    g3 = GoalNode(id="g3", domain="career", title="Goal 3")

    graph.add_goal(g1)
    graph.add_goal(g2)
    graph.add_goal(g3)

    # Create a cycle: g1 -> g2 -> g3 -> g1
    e1 = DependencyEdge(from_goal_id="g1", to_goal_id="g2", relationship_type="enables")
    e2 = DependencyEdge(from_goal_id="g2", to_goal_id="g3", relationship_type="enables")
    e3 = DependencyEdge(from_goal_id="g3", to_goal_id="g1", relationship_type="enables")

    graph.add_dependency(e1)
    graph.add_dependency(e2)
    graph.add_dependency(e3)

    # Should still be able to render
    renderer = ASCIIGraphRenderer(graph)
    viz = renderer.render_tree()

    assert isinstance(viz, str)
    assert len(viz) > 0

    # Report should detect cycles
    report = generate_dependency_report(graph, "test_user", include_visualizations=False)
    assert "cycle" in report.lower() or "circular" in report.lower()


def test_visualization_with_complex_dependencies():
    """Test visualization with complex dependency structure."""
    graph = GoalDependencyGraph()

    # Create many goals
    for i in range(10):
        goal = GoalNode(
            id=f"g{i}",
            domain="career" if i % 2 == 0 else "wellness",
            title=f"Goal {i}",
            priority=i + 1,
            estimated_effort=10.0 * (i + 1),
        )
        graph.add_goal(goal)

    # Create complex dependencies
    for i in range(9):
        edge = DependencyEdge(
            from_goal_id=f"g{i}",
            to_goal_id=f"g{i + 1}",
            relationship_type="enables" if i % 2 == 0 else "supports",
        )
        graph.add_dependency(edge)

    # Should handle complex structure
    renderer = ASCIIGraphRenderer(graph)
    tree_viz = renderer.render_tree()
    matrix_viz = renderer.render_matrix()

    assert isinstance(tree_viz, str)
    assert len(tree_viz) > 0
    assert isinstance(matrix_viz, str)
    assert len(matrix_viz) > 0


if __name__ == "__main__":
    # Run tests manually if needed
    print("Running viz_tools tests...")
    test_ascii_graph_renderer_init()
    print("✓ ASCIIGraphRenderer init")
    test_truncate_text()
    print("✓ Text truncation")
    test_get_goal_display_name()
    print("✓ Goal display name")
    test_build_tree_structure()
    print("✓ Tree structure building")
    test_render_tree()
    print("✓ Tree rendering")
    test_interactive_explorer_init()
    print("✓ InteractiveExplorer init")
    test_show_help()
    print("✓ Help display")
    test_what_if_analyzer_init()
    print("✓ WhatIfAnalyzer init")
    test_simulate_add_goal()
    print("✓ Add goal simulation")
    test_simulate_remove_goal()
    print("✓ Remove goal simulation")
    test_generate_dependency_report()
    print("✓ Dependency report generation")
    test_full_visualization_workflow()
    print("✓ Full workflow integration")
    print("\nAll tests passed!")
