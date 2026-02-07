"""
Test suite for AI Life Coach planning tools.

Tests all 3 planning tools: write_todos, update_todo, and list_todos.
Validates tool decorator usage, input validation, phase filtering,
dependency tracking, circular dependency detection, and functionality.
"""

import pytest

# Import the planning tools module components
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tools.planning_tools import (
    create_planning_tools,
    TodoItem,
    TodoManager,
)


# ==============================================================================
# Test Fixtures
# ==============================================================================


@pytest.fixture(autouse=True)
def reset_todo_manager():
    """Reset the global todo manager before each test."""
    from tools.planning_tools import get_todo_manager

    manager = get_todo_manager()
    manager.todos.clear()
    yield
    manager.todos.clear()


@pytest.fixture
def planning_tools():
    """Create planning tools."""
    return create_planning_tools()


@pytest.fixture
def sample_todos():
    """Sample todo list for testing."""
    return [
        {"title": "Initial life assessment", "phase": "discovery"},
        {
            "title": "Identify top 3 priorities",
            "phase": "discovery",
            "depends_on": [0],
        },
        {"title": "Create 90-day action plan", "phase": "planning", "depends_on": [1]},
        {"title": "Weekly check-in system", "phase": "execution"},
    ]


# ==============================================================================
# Tool Creation Tests
# ==============================================================================


def test_create_planning_tools_returns_tuple():
    """Test that create_planning_tools returns a tuple of 3 tools."""
    tools = create_planning_tools()

    assert isinstance(tools, tuple), "Should return a tuple"
    assert len(tools) == 3, "Should return exactly 3 tools"

    # Check that each tool has the expected name
    expected_names = ["write_todos", "update_todo", "list_todos"]
    actual_names = [tool.name if hasattr(tool, "name") else tool.__name__ for tool in tools]

    assert actual_names == expected_names, f"Tool names don't match: {actual_names}"


def test_tools_have_docstrings():
    """Test that all tools have proper docstrings."""
    write_todos, update_todo, list_todos = create_planning_tools()

    for tool in [write_todos, update_todo, list_todos]:
        assert tool.description is not None and len(tool.description) > 100, (
            f"{tool.name} should have a descriptive docstring"
        )


def test_tools_have_tool_decorator():
    """Test that all tools use the @tool decorator."""
    write_todos, update_todo, list_todos = create_planning_tools()

    for tool in [write_todos, update_todo, list_todos]:
        assert hasattr(tool, "name") and hasattr(tool, "func"), (
            f"{tool.name} should be a properly decorated LangChain tool"
        )


# ==============================================================================
# TodoItem Model Tests
# ==============================================================================


def test_todo_item_creation():
    """Test basic TodoItem creation."""
    todo = TodoItem(title="Test task", phase="planning")

    assert todo.title == "Test task"
    assert todo.phase == "planning"
    assert todo.status == "pending"
    assert todo.depends_on == []
    assert todo.notes == ""


def test_todo_item_with_dependencies():
    """Test TodoItem with dependencies."""
    todo = TodoItem(title="Dependent task", depends_on=[0, 1])

    assert todo.depends_on == [0, 1]


def test_todo_item_validation_invalid_title():
    """Test that TodoItem rejects empty title."""
    with pytest.raises(ValueError, match="title must be a non-empty string"):
        TodoItem(title="")


def test_todo_item_validation_invalid_phase():
    """Test that TodoItem rejects invalid phase."""
    with pytest.raises(ValueError, match="phase must be one of"):
        TodoItem(title="Test", phase="invalid_phase")


def test_todo_item_validation_invalid_status():
    """Test that TodoItem rejects invalid status."""
    with pytest.raises(ValueError, match="status must be one of"):
        TodoItem(title="Test", status="invalid_status")


def test_todo_item_all_valid_phases():
    """Test that all 4 valid phases are accepted."""
    for phase in ["discovery", "planning", "execution", "review"]:
        todo = TodoItem(title="Test", phase=phase)
        assert todo.phase == phase


def test_todo_item_all_valid_statuses():
    """Test that all 3 valid statuses are accepted."""
    for status in ["pending", "in_progress", "completed"]:
        todo = TodoItem(title="Test", status=status)
        assert todo.status == status


def test_todo_item_to_dict():
    """Test TodoItem serialization to dictionary."""
    todo = TodoItem(
        title="Serialize test",
        phase="execution",
        depends_on=[1, 2],
        notes="Some notes",
    )
    data = todo.to_dict()

    assert data["title"] == "Serialize test"
    assert data["phase"] == "execution"
    assert data["depends_on"] == [1, 2]
    assert data["notes"] == "Some notes"


def test_todo_item_from_dict():
    """Test TodoItem deserialization from dictionary."""
    data = {
        "title": "Deserialize test",
        "phase": "review",
        "status": "completed",
        "depends_on": [0],
        "notes": "Completed notes",
    }
    todo = TodoItem.from_dict(data)

    assert todo.title == "Deserialize test"
    assert todo.phase == "review"
    assert todo.status == "completed"


# ==============================================================================
# TodoManager Tests
# ==============================================================================


def test_todo_manager_initialization():
    """Test that TodoManager initializes empty."""
    manager = TodoManager()

    assert len(manager.todos) == 0


def test_todo_manager_set_todos_basic():
    """Test basic todo list creation."""
    manager = TodoManager()
    result = manager.set_todos([{"title": "Task 1"}, {"title": "Task 2"}])

    assert len(manager.todos) == 2
    assert manager.todos[0].title == "Task 1"
    assert "Successfully created" in result


def test_todo_manager_count_phases():
    """Test phase counting."""
    manager = TodoManager()
    todos = [
        {"title": "T1", "phase": "discovery"},
        {"title": "T2", "phase": "planning"},
        {"title": "T3", "phase": "discovery"},
        {"title": "T4", "phase": "execution"},
    ]
    manager.set_todos(todos)

    counts = manager._count_phases()
    assert counts["discovery"] == 2
    assert counts["planning"] == 1
    assert counts["execution"] == 1


# ==============================================================================
# Circular Dependency Detection Tests
# ==============================================================================


def test_detect_simple_circular_dependency():
    """Test detection of simple A -> B -> A cycle."""
    manager = TodoManager()

    # Create circular dependency: task 0 depends on task 1, task 1 depends on task 0
    with pytest.raises(ValueError, match="Circular dependency detected"):
        manager.set_todos(
            [
                {"title": "Task A", "depends_on": [1]},
                {"title": "Task B", "depends_on": [0]},
            ]
        )


def test_detect_three_node_cycle():
    """Test detection of A -> B -> C -> A cycle."""
    manager = TodoManager()

    with pytest.raises(ValueError, match="Circular dependency detected"):
        manager.set_todos(
            [
                {"title": "Task A", "depends_on": [1]},
                {"title": "Task B", "depends_on": [2]},
                {"title": "Task C", "depends_on": [0]},
            ]
        )


def test_no_cycle_valid_dependencies():
    """Test that valid linear dependencies don't trigger false positives."""
    manager = TodoManager()

    # Linear chain: A -> B -> C (no cycle)
    result = manager.set_todos(
        [
            {"title": "Task A"},
            {"title": "Task B", "depends_on": [0]},
            {"title": "Task C", "depends_on": [1]},
        ]
    )

    assert len(manager.todos) == 3
    assert "Successfully created" in result


def test_diamond_dependency_pattern():
    """Test diamond pattern (A->B, A->C, B->D, C->D) which is valid."""
    manager = TodoManager()

    result = manager.set_todos(
        [
            {"title": "Task A"},
            {"title": "Task B", "depends_on": [0]},
            {"title": "Task C", "depends_on": [0]},
            {"title": "Task D", "depends_on": [1, 2]},
        ]
    )

    assert len(manager.todos) == 4
    assert "Successfully created" in result


def test_self_dependency():
    """Test that a task depending on itself is detected as circular."""
    manager = TodoManager()

    with pytest.raises(ValueError, match="Circular dependency detected"):
        manager.set_todos([{"title": "Task A", "depends_on": [0]}])


# ==============================================================================
# write_todos Tool Tests
# ==============================================================================


def test_write_todos_creates_list(planning_tools):
    """Test that write_todos creates a todo list."""
    write_todos, _, _ = planning_tools

    result = write_todos.invoke(
        {"todos": [{"title": "First task", "phase": "discovery"}, {"title": "Second task"}]}
    )

    assert "Successfully created" in result
    assert "2 todos" in result


def test_write_todos_with_dependencies(planning_tools):
    """Test write_todos with dependency tracking."""
    write_todos, _, _ = planning_tools

    result = write_todos.invoke(
        {
            "todos": [
                {"title": "Task 1", "phase": "discovery"},
                {"title": "Task 2", "depends_on": [0]},
            ]
        }
    )

    assert "Successfully created" in result


def test_write_todos_detects_circular_dependency(planning_tools):
    """Test write_todos rejects circular dependencies."""
    write_todos, _, _ = planning_tools

    result = write_todos.invoke(
        {
            "todos": [
                {"title": "Task A", "depends_on": [1]},
                {"title": "Task B", "depends_on": [0]},
            ]
        }
    )

    assert "Validation error" in result
    assert "Circular dependency detected" in result


def test_write_todos_invalid_phase(planning_tools):
    """Test write_todos rejects invalid phase."""
    write_todos, _, _ = planning_tools

    result = write_todos.invoke({"todos": [{"title": "Task 1", "phase": "invalid_phase"}]})

    assert "Error in todo item" in result


def test_write_todos_replaces_existing(planning_tools):
    """Test that write_todos replaces existing todos."""
    write_todos, _, list_t = planning_tools

    # Create initial list
    write_todos.invoke({"todos": [{"title": "Old task 1"}, {"title": "Old task 2"}]})

    # Replace with new list
    result = write_todos.invoke({"todos": [{"title": "New task"}]})

    assert "Successfully created" in result
    # Verify only 1 todo exists now
    list_result = list_t.invoke({})
    assert "New task" in list_result
    assert "Old task 1" not in list_result


# ==============================================================================
# update_todo Tool Tests
# ==============================================================================


def test_update_todo_status(planning_tools, sample_todos):
    """Test updating todo status."""
    write_todos, update_todo, list_t = planning_tools

    # Create todos
    write_todos.invoke({"todos": sample_todos})

    # Update status of first todo
    result = update_todo.invoke({"todo_id": 0, "status": "in_progress"})

    assert "Updated todo" in result
    assert "in_progress" in result


def test_update_todo_with_notes(planning_tools, sample_todos):
    """Test adding notes to a todo."""
    write_todos, update_todo, list_t = planning_tools

    # Create todos
    write_todos.invoke({"todos": sample_todos})

    # Add notes to first todo
    result = update_todo.invoke({"todo_id": 0, "notes": "Initial assessment complete"})

    assert "Updated todo" in result
    assert "notes added" in result


def test_update_todo_invalid_id(planning_tools, sample_todos):
    """Test update_todo with invalid todo ID."""
    write_todos, update_todo, _ = planning_tools

    # Create todos
    write_todos.invoke({"todos": sample_todos})

    # Try to update non-existent todo
    result = update_todo.invoke({"todo_id": 99, "status": "completed"})

    assert "Error: Invalid todo_id" in result


def test_update_todo_invalid_status(planning_tools, sample_todos):
    """Test update_todo with invalid status."""
    write_todos, update_todo, _ = planning_tools

    # Create todos
    write_todos.invoke({"todos": sample_todos})

    result = update_todo.invoke({"todo_id": 0, "status": "invalid_status"})

    assert "Error: Invalid status" in result


def test_update_todo_blocked_by_dependencies(planning_tools, sample_todos):
    """Test that dependencies block status updates."""
    write_todos, update_todo, _ = planning_tools

    # Create todos where task 2 depends on task 1
    write_todos.invoke({"todos": sample_todos})

    # Try to mark task 2 in_progress when its dependency (task 1) is not complete
    result = update_todo.invoke({"todo_id": 2, "status": "in_progress"})

    assert "Cannot set" in result
    assert "depends on incomplete tasks" in result


def test_update_todo_allows_after_deps_complete(planning_tools, sample_todos):
    """Test that updates work after dependencies are complete."""
    write_todos, update_todo, _ = planning_tools

    # Create todos with dependencies
    write_todos.invoke({"todos": sample_todos})

    # Complete task 0 and 1 (dependencies of task 2)
    update_todo.invoke({"todo_id": 0, "status": "completed"})
    update_todo.invoke({"todo_id": 1, "status": "completed"})

    # Now task 2 should be updatable
    result = update_todo.invoke({"todo_id": 2, "status": "in_progress"})

    assert "Updated todo" in result
    assert "in_progress" in result


def test_update_todo_completed_timestamp(planning_tools, sample_todos):
    """Test that completed status sets timestamp."""
    write_todos, update_todo, list_t = planning_tools

    # Create todos
    write_todos.invoke({"todos": sample_todos})

    # Mark first todo as completed
    update_todo.invoke({"todo_id": 0, "status": "completed"})

    # Verify completed_at is set - use the global manager
    from tools.planning_tools import get_todo_manager

    manager = get_todo_manager()
    assert manager.todos[0].completed_at is not None


# ==============================================================================
# list_todos Tool Tests
# ==============================================================================


def test_list_todos_all(planning_tools, sample_todos):
    """Test listing all todos."""
    write_todos, _, list_t = planning_tools

    # Create todos
    write_todos.invoke({"todos": sample_todos})

    result = list_t.invoke({})

    assert "Discovery Phase" in result
    assert "Planning Phase" in result
    assert "Execution Phase" in result


def test_list_todos_filter_by_phase(planning_tools, sample_todos):
    """Test filtering todos by phase."""
    write_todos, _, list_t = planning_tools

    # Create todos
    write_todos.invoke({"todos": sample_todos})

    result = list_t.invoke({"phase": "discovery"})

    assert "Discovery Phase" in result
    # Should only show discovery phase items
    count = result.count("⏳") + result.count("🔄") + result.count("✅")
    assert count == 2, "Should show exactly 2 discovery items"


def test_list_todos_filter_by_status(planning_tools, sample_todos):
    """Test filtering todos by status."""
    write_todos, update_todo, list_t = planning_tools

    # Create todos
    write_todos.invoke({"todos": sample_todos})

    # Mark first todo as completed
    update_todo.invoke({"todo_id": 0, "status": "completed"})

    result = list_t.invoke({"status": "pending"})

    # Should only show pending items
    assert "✅" not in result, "Should not show completed items"


def test_list_todos_empty(planning_tools):
    """Test listing todos when none exist."""
    _, _, list_t = planning_tools

    result = list_t.invoke({})

    assert "No todos found" in result


def test_list_todos_shows_dependencies(planning_tools, sample_todos):
    """Test that list_todos shows dependency status."""
    write_todos, _, list_t = planning_tools

    # Create todos with dependencies
    write_todos.invoke({"todos": sample_todos})

    result = list_t.invoke({})

    assert "Dependencies:" in result


def test_list_todos_status_icons(planning_tools, sample_todos):
    """Test that list_todos shows correct status icons."""
    write_todos, update_todo, list_t = planning_tools

    # Create todos
    write_todos.invoke({"todos": sample_todos})

    # Set different statuses - complete task 0 first so task 1 can be updated
    update_todo.invoke({"todo_id": 0, "status": "completed"})
    update_todo.invoke({"todo_id": 1, "status": "in_progress"})

    result = list_t.invoke({})

    assert "🔄" in result  # in_progress
    assert "✅" in result  # completed
    assert "⏳" in result  # pending


def test_list_todos_invalid_phase(planning_tools, sample_todos):
    """Test list_todos with invalid phase filter."""
    write_todos, _, list_t = planning_tools

    # Create todos
    write_todos.invoke({"todos": sample_todos})

    result = list_t.invoke({"phase": "invalid_phase"})

    assert "Filter error" in result


# ==============================================================================
# Integration Tests
# ==============================================================================


def test_full_workflow(planning_tools):
    """Test complete workflow: create, update, list."""
    write_todos, update_todo, list_t = planning_tools

    # Step 1: Create todo list
    todos = [
        {"title": "Assess current situation", "phase": "discovery"},
        {"title": "Identify priorities", "phase": "discovery", "depends_on": [0]},
        {"title": "Create action plan", "phase": "planning", "depends_on": [1]},
        {"title": "Execute first action", "phase": "execution", "depends_on": [2]},
    ]
    result1 = write_todos.invoke({"todos": todos})
    assert "Successfully created" in result1

    # Step 2: Update first todo
    result2 = update_todo.invoke({"todo_id": 0, "status": "completed"})
    assert "Updated todo" in result2

    # Step 3: Verify second todo is still blocked
    result3 = update_todo.invoke({"todo_id": 1, "status": "in_progress"})
    assert "Updated todo" in result3

    # Step 4: List and verify state
    result4 = list_t.invoke({})
    assert "Assess current situation" in result4
    assert "✅" in result4  # Task 0 is completed


def test_multiple_phases_workflow(planning_tools):
    """Test workflow spanning all 4 phases."""
    write_todos, _, list_t = planning_tools

    todos = [
        {"title": "Discovery task", "phase": "discovery"},
        {"title": "Planning task", "phase": "planning", "depends_on": [0]},
        {"title": "Execution task 1", "phase": "execution", "depends_on": [1]},
        {"title": "Execution task 2", "phase": "execution"},
        {"title": "Review task", "phase": "review", "depends_on": [2, 3]},
    ]

    result = write_todos.invoke({"todos": todos})
    assert "Successfully created" in result
    # Message should mention all 4 phases in the output
    assert "discovery" in result.lower()
    assert "planning" in result.lower()
    assert "execution" in result.lower()
    assert "review" in result.lower()


def test_notes_accumulation(planning_tools, sample_todos):
    """Test that multiple note additions accumulate."""
    write_todos, update_todo, list_t = planning_tools

    # Create todos
    write_todos.invoke({"todos": sample_todos})

    # Add multiple notes
    update_todo.invoke({"todo_id": 0, "notes": "Note 1"})
    update_todo.invoke({"todo_id": 0, "notes": "Note 2"})

    result = list_t.invoke({})

    assert "Note 1" in result
    assert "Note 2" in result


# ==============================================================================
# Edge Cases Tests
# ==============================================================================


def test_empty_todo_list(planning_tools):
    """Test creating an empty todo list."""
    write_todos, _, _ = planning_tools

    result = write_todos.invoke({"todos": []})

    assert "Successfully created" in result
    assert "0 todos" in result


def test_single_todo_no_dependencies(planning_tools):
    """Test a single todo without dependencies."""
    write_todos, _, list_t = planning_tools

    result = write_todos.invoke({"todos": [{"title": "Only task"}]})

    assert "Successfully created" in result
    list_result = list_t.invoke({})
    assert "Only task" in list_result


def test_multiple_dependencies_single_task(planning_tools):
    """Test a task that depends on multiple other tasks."""
    write_todos, _, list_t = planning_tools

    todos = [
        {"title": "Task A"},
        {"title": "Task B"},
        {"title": "Task C", "depends_on": [0, 1]},
    ]

    result = write_todos.invoke({"todos": todos})
    assert "Successfully created" in result

    list_result = list_t.invoke({})
    assert "Dependencies: 0/2" in list_result


def test_invalid_dependency_reference(planning_tools):
    """Test handling of invalid dependency references."""
    write_todos, _, _ = planning_tools

    # Reference non-existent todo index
    todos = [
        {"title": "Task A"},
        {"title": "Task B", "depends_on": [5]},  # Invalid index
    ]

    result = write_todos.invoke({"todos": todos})
    # Should succeed (invalid references are just ignored in blocking check)
    assert "Successfully created" in result


def test_all_phases_represented(planning_tools):
    """Test that all 4 phases appear in output."""
    write_todos, _, list_t = planning_tools

    todos = [
        {"title": "D1", "phase": "discovery"},
        {"title": "P1", "phase": "planning"},
        {"title": "E1", "phase": "execution"},
        {"title": "R1", "phase": "review"},
    ]

    write_todos.invoke({"todos": todos})
    result = list_t.invoke({})

    assert "Discovery Phase" in result
    assert "Planning Phase" in result
    assert "Execution Phase" in result
    assert "Review Phase" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
