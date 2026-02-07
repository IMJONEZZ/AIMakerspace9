"""
Simple test for cross-domain integration tools.
"""

import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import and initialize config first
from src.config import config, get_backend

# Initialize config for tests
try:
    _backend = get_backend()
except RuntimeError:
    # Config not initialized, initialize it
    config.initialize_environment()
    _backend = get_backend()

# Import the tools to test after config is initialized
from src.tools.cross_domain_tools import (
    create_cross_domain_tools,
    GoalNode,
    DependencyEdge,
    GoalDependencyGraph,
    suggest_conflict_resolution,
)

# Test data
SAMPLE_USER_ID = "test_user_123"
SAMPLE_GOALS = [
    {"id": "g1", "domain": "career", "title": "Get promoted", "priority": 8},
    {"id": "g2", "domain": "finance", "title": "Save $50k", "priority": 7},
    {"id": "g3", "domain": "wellness", "title": "Exercise daily", "priority": 6},
]
SAMPLE_DEPENDENCIES = [
    {
        "from_goal_id": "g1",
        "to_goal_id": "g2",
        "relationship_type": "enables",
        "strength": 0.9,
    }
]

print("=" * 60)
print("Testing Cross-Domain Integration Tools")
print("=" * 60)

# Test 1: Create tools
print("\nTest 1: Creating cross-domain tools...")
try:
    build_tool, analyze_tool, conflict_tool, priority_tool, plan_tool = create_cross_domain_tools(_backend)
    print("✓ Tools created successfully")
except Exception as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

# Test 2: Build dependency graph
print("\nTest 2: Building goal dependency graph...")
try:
    result = build_tool.invoke({
        "user_id": SAMPLE_USER_ID,
        "goals": SAMPLE_GOALS,
        "dependencies": SAMPLE_DEPENDENCIES,
    })
    assert "Goal Dependency Graph" in result
    print("✓ Dependency graph built successfully")
except Exception as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

# Test 3: Analyze cross-domain impacts
print("\nTest 3: Analyzing cross-domain impacts...")
try:
    result = analyze_tool.invoke({"user_id": SAMPLE_USER_ID})
    assert "Cross-Domain Impact Analysis" in result
    print("✓ Cross-domain impacts analyzed successfully")
except Exception as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

# Test 4: Detect conflicts
print("\nTest 4: Detecting goal conflicts...")
try:
    result = conflict_tool.invoke({"user_id": SAMPLE_USER_ID})
    assert "Conflict Detection Report" in result
    print("✓ Conflicts detected successfully")
except Exception as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

# Test 5: Recommend priority adjustments
print("\nTest 5: Recommending priority adjustments...")
try:
    result = priority_tool.invoke({"user_id": SAMPLE_USER_ID})
    assert "Priority Adjustment Recommendations" in result
    print("✓ Priority adjustments recommended successfully")
except Exception as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

# Test 6: Generate integration plan
print("\nTest 6: Generating integration plan...")
try:
    result = plan_tool.invoke({"user_id": SAMPLE_USER_ID})
    assert "Integrated Life Plan" in result
    print("✓ Integration plan generated successfully")
except Exception as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

# Test 7: Test graph data structures
print("\nTest 7: Testing graph data structures...")
try:
    graph = GoalDependencyGraph()
    
    # Add nodes
    node1 = GoalNode("g1", "career", "Goal 1", priority=8)
    node2 = GoalNode("g2", "finance", "Goal 2", priority=7)
    graph.add_goal(node1)
    graph.add_goal(node2)
    
    # Add edge
    edge = DependencyEdge("g1", "g2", "enables", 0.9, "Test")
    graph.add_dependency(edge)
    
    # Test retrieval
    deps = graph.get_dependencies("g2")
    assert len(deps) == 1
    
    # Test cycle detection
    cycles = graph.detect_cycles()
    assert len(cycles) == 0
    
    print("✓ Graph data structures work correctly")
except Exception as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

# Test 8: Test cycle detection
print("\nTest 8: Testing cycle detection...")
try:
    graph = GoalDependencyGraph()
    graph.add_goal(GoalNode("g1", "career", "Goal 1"))
    graph.add_goal(GoalNode("g2", "finance", "Goal 2"))
    
    # Create a cycle
    graph.add_dependency(DependencyEdge("g1", "g2", "enables"))
    graph.add_dependency(DependencyEdge("g2", "g1", "requires"))
    
    cycles = graph.detect_cycles()
    assert len(cycles) == 1
    
    print("✓ Cycle detection works correctly")
except Exception as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

# Test 9: Test topological sort
print("\nTest 9: Testing topological sort...")
try:
    graph = GoalDependencyGraph()
    graph.add_goal(GoalNode("g1", "career", "Goal 1"))
    graph.add_goal(GoalNode("g2", "finance", "Goal 2"))
    graph.add_goal(GoalNode("g3", "wellness", "Goal 3"))
    
    # Add dependencies: g1 -> g2 -> g3
    graph.add_dependency(DependencyEdge("g1", "g2", "enables"))
    graph.add_dependency(DependencyEdge("g2", "g3", "requires"))
    
    order = graph.topological_sort()
    assert len(order) == 3
    assert order.index("g1") < order.index("g2")
    assert order.index("g2") < order.index("g3")
    
    print("✓ Topological sort works correctly")
except Exception as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

# Test 10: Test conflict resolution suggestions
print("\nTest 10: Testing conflict resolution suggestions...")
try:
    goal1 = GoalNode("g1", "career", "Get promoted", priority=8)
    goal2 = GoalNode("g2", "wellness", "Exercise daily", priority=6)
    edge = DependencyEdge("g1", "g2", "conflicts", 0.8, "Time conflict")
    
    resolutions = suggest_conflict_resolution(goal1, goal2, edge)
    assert len(resolutions) > 0
    
    print("✓ Conflict resolution suggestions generated")
except Exception as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("All tests passed!")
print("=" * 60)
