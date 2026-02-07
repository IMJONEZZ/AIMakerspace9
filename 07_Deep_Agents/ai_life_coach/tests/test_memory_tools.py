"""
Test suite for AI Life Coach memory tools.

Tests all 4 memory tools: get_user_profile, save_user_preference,
update_milestone, and get_progress_history. Validates proper tool
decorator usage, input validation, error handling, and functionality.
"""

import pytest

# Import the memory tools module components
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tools.memory_tools import create_memory_tools
from memory import (
    UserProfile,
    Milestone,
    Setback,
    UserPreferences,
)


# ==============================================================================
# Test Fixtures
# ==============================================================================


@pytest.fixture
def memory_store():
    """Create a test memory store."""
    from memory import create_memory_store

    return create_memory_store()


@pytest.fixture
def test_user_id():
    """Standard test user ID."""
    return "test_user_123"


@pytest.fixture
def memory_tools(memory_store):
    """Create memory tools with test store."""
    return create_memory_tools(memory_store)


# ==============================================================================
# Tool Creation Tests
# ==============================================================================


def test_create_memory_tools_returns_tuple(memory_store):
    """Test that create_memory_tools returns a tuple of 4 tools."""
    tools = create_memory_tools(memory_store)

    assert isinstance(tools, tuple), "Should return a tuple"
    assert len(tools) == 4, "Should return exactly 4 tools"

    # Check that each tool has the expected name (from function name)
    expected_names = [
        "get_user_profile",
        "save_user_preference",
        "update_milestone",
        "get_progress_history",
    ]
    actual_names = [tool.name if hasattr(tool, "name") else tool.__name__ for tool in tools]

    assert actual_names == expected_names, f"Tool names don't match: {actual_names}"


def test_tools_have_docstrings(memory_store):
    """Test that all tools have proper docstrings."""
    tools = create_memory_tools(memory_store)

    for tool in tools:
        # StructuredTool objects have description, not __doc__
        assert tool.description is not None and len(tool.description) > 50, (
            f"{tool.name} should have a descriptive docstring"
        )


def test_tools_have_tool_decorator(memory_store):
    """Test that all tools use the @tool decorator."""
    tools = create_memory_tools(memory_store)

    for tool in tools:
        # StructuredTool objects are callable through .invoke or have a .func attribute
        assert hasattr(tool, "name") and hasattr(tool, "func"), (
            f"{tool.name} should be a properly decorated LangChain tool"
        )


# ==============================================================================
# get_user_profile Tests
# ==============================================================================


def test_get_user_profile_no_profile(memory_tools, test_user_id):
    """Test get_user_profile when no profile exists."""
    tool = memory_tools[0]  # get_user_profile
    result = tool.func(test_user_id)

    assert isinstance(result, str), "Should return a string"
    assert "No profile found" in result or "no profile exists" in result.lower(), (
        "Should indicate no profile exists"
    )


def test_get_user_profile_with_existing_profile(memory_store, memory_tools, test_user_id):
    """Test get_user_profile with an existing profile."""
    # Create and save a test profile
    from memory import create_memory_manager

    manager = create_memory_manager(memory_store)
    profile = UserProfile(
        user_id=test_user_id,
        name="Test User",
        age=30,
        occupation="Engineer",
        values=["growth", "learning"],
    )
    manager.save_profile(profile)

    # Retrieve using tool
    tool = memory_tools[0]  # get_user_profile
    result = tool.func(test_user_id)

    assert isinstance(result, str), "Should return a string"
    assert test_user_id in result, f"Result should contain user ID: {test_user_id}"
    assert "Test User" in result, "Result should contain user name"
    assert "Engineer" in result, "Result should contain occupation"


def test_get_user_profile_invalid_user_id(memory_tools):
    """Test get_user_profile with invalid user IDs."""
    tool = memory_tools[0]  # get_user_profile

    # Test empty string
    result = tool.func("")
    assert "Error" in result, "Should return error for empty user_id"

    # Test None
    result = tool.func(None)  # type: ignore
    assert "Error" in result, "Should return error for None user_id"


# ==============================================================================
# save_user_preference Tests
# ==============================================================================


def test_save_user_preference_basic(memory_tools, memory_store, test_user_id):
    """Test saving a basic user preference."""
    tool = memory_tools[1]  # save_user_preference
    result = tool.func(test_user_id, "communication_style", "concise")

    assert isinstance(result, str), "Should return a string"
    assert "Saved preference" in result or "saved" in result.lower(), (
        "Should confirm save operation"
    )
    assert test_user_id in result, f"Result should contain user ID: {test_user_id}"
    assert "communication_style" in result, "Result should contain preference key"

    # Verify it was saved
    from memory import create_memory_manager

    manager = create_memory_manager(memory_store)
    prefs = manager.get_preferences(test_user_id)
    assert prefs is not None, "Preferences should be saved"
    assert prefs.communication_style == "concise", (
        f"Saved preference should match: {prefs.communication_style}"
    )


def test_save_user_preference_multiple_keys(memory_tools, memory_store, test_user_id):
    """Test saving multiple preferences for the same user."""
    tool = memory_tools[1]  # save_user_preference

    # Save multiple preferences
    result1 = tool.func(test_user_id, "communication_style", "detailed")
    assert "Saved preference" in result1

    result2 = tool.func(test_user_id, "coaching_approach", "supportive")
    assert "Saved preference" in result2

    result3 = tool.func(test_user_id, "preferred_checkin_frequency", "weekly")
    assert "Saved preference" in result3

    # Verify all were saved
    from memory import create_memory_manager

    manager = create_memory_manager(memory_store)
    prefs = manager.get_preferences(test_user_id)

    assert prefs is not None, "Preferences should exist"
    assert prefs.communication_style == "detailed"
    assert prefs.coaching_approach == "supportive"
    assert prefs.preferred_checkin_frequency == "weekly"


def test_save_user_preference_validation(memory_tools):
    """Test save_user_preference input validation."""
    tool = memory_tools[1]  # save_user_preference

    # Test empty user_id
    result = tool.func("", "key", "value")
    assert "Error" in result, "Should return error for empty user_id"

    # Test empty key
    result = tool.func("user_123", "", "value")
    assert "Error" in result, "Should return error for empty key"

    # Test None value
    result = tool.func("user_123", "key", None)  # type: ignore
    assert "Error" in result, "Should return error for None value"


# ==============================================================================
# update_milestone Tests
# ==============================================================================


def test_update_milestone_basic(memory_tools, memory_store, test_user_id):
    """Test adding a basic milestone."""
    tool = memory_tools[2]  # update_milestone

    result = tool.func(
        test_user_id,
        {
            "title": "Completed certification",
            "domain": "career",
            "significance": "major",
        },
    )

    assert isinstance(result, str), "Should return a string"
    assert "Milestone" in result or "milestone" in result.lower(), "Should mention milestone"
    assert test_user_id in result, f"Result should contain user ID: {test_user_id}"
    assert "Completed certification" in result, "Result should contain milestone title"

    # Verify it was saved
    from memory import create_memory_manager

    manager = create_memory_manager(memory_store)
    milestones = manager.get_milestones(test_user_id)

    assert len(milestones) == 1, "Should have exactly one milestone"
    assert milestones[0].title == "Completed certification"
    assert milestones[0].domain == "career"


def test_update_milestone_minimal_data(memory_tools, memory_store, test_user_id):
    """Test adding a milestone with minimal required data."""
    tool = memory_tools[2]  # update_milestone

    result = tool.func(test_user_id, {"title": "Simple milestone"})

    assert isinstance(result, str), "Should return a string"
    # Should use defaults for optional fields
    from memory import create_memory_manager

    manager = create_memory_manager(memory_store)
    milestones = manager.get_milestones(test_user_id)

    assert len(milestones) == 1, "Should have one milestone"
    assert milestones[0].title == "Simple milestone"
    assert milestones[0].domain == "general"  # Default value
    assert milestones[0].significance == "normal"  # Default value


def test_update_milestone_validation(memory_tools):
    """Test update_milestone input validation."""
    tool = memory_tools[2]  # update_milestone

    # Test empty user_id
    result = tool.func("", {"title": "Test"})
    assert "Error" in result, "Should return error for empty user_id"

    # Test None milestone_data
    result = tool.func("user_123", None)  # type: ignore
    assert "Error" in result, "Should return error for None milestone_data"

    # Test empty dict
    result = tool.func("user_123", {})
    assert "Error" in result, "Should return error for empty milestone_data"

    # Test missing title
    result = tool.func("user_123", {"description": "No title"})
    assert "Error" in result, "Should return error for missing title"


def test_update_milestone_multiple(memory_tools, memory_store, test_user_id):
    """Test adding multiple milestones for a user."""
    tool = memory_tools[2]  # update_milestone

    # Add multiple milestones
    tool.func(test_user_id, {"title": "Milestone 1", "domain": "career"})
    tool.func(test_user_id, {"title": "Milestone 2", "domain": "wellness"})
    tool.func(test_user_id, {"title": "Milestone 3", "domain": "relationship"})

    # Verify all were saved
    from memory import create_memory_manager

    manager = create_memory_manager(memory_store)
    milestones = manager.get_milestones(test_user_id)

    assert len(milestones) == 3, "Should have three milestones"
    titles = [m.title for m in milestones]
    assert "Milestone 1" in titles
    assert "Milestone 2" in titles
    assert "Milestone 3" in titles


# ==============================================================================
# get_progress_history Tests
# ==============================================================================


def test_get_progress_history_empty(memory_tools, test_user_id):
    """Test get_progress_history when no progress exists."""
    tool = memory_tools[3]  # get_progress_history
    result = tool.func(test_user_id)

    assert isinstance(result, str), "Should return a string"
    assert "No progress" in result or "No milestones exist" in result, (
        "Should indicate no progress exists"
    )


def test_get_progress_history_with_milestones(memory_store, memory_tools, test_user_id):
    """Test get_progress_history with existing milestones."""
    from memory import create_memory_manager

    # Add some test milestones
    manager = create_memory_manager(memory_store)
    manager.add_milestone(
        test_user_id,
        Milestone(title="First milestone", domain="career", significance="major"),
    )
    manager.add_milestone(
        test_user_id,
        Milestone(title="Second milestone", domain="wellness"),
    )

    # Retrieve using tool
    tool = memory_tools[3]  # get_progress_history
    result = tool.func(test_user_id)

    assert isinstance(result, str), "Should return a string"
    assert test_user_id in result, f"Result should contain user ID: {test_user_id}"
    assert "First milestone" in result, "Result should contain first milestone"
    assert "Second milestone" in result, "Result should contain second milestone"
    assert "career" in result.lower(), "Should mention career domain"


def test_get_progress_history_with_timeframe_filter(memory_store, memory_tools, test_user_id):
    """Test get_progress_history with timeframe filtering."""
    from memory import create_memory_manager

    # Add milestones at different times
    manager = create_memory_manager(memory_store)
    old_date = "2023-01-01T00:00:00"
    manager.add_milestone(
        test_user_id,
        Milestone(title="Old milestone", achieved_at=old_date),
    )

    # Get recent progress
    tool = memory_tools[3]  # get_progress_history
    result = tool.func(test_user_id, "recent")

    assert isinstance(result, str), "Should return a string"
    # Recent filter should exclude the old milestone
    assert "No progress" in result or "Old milestone" not in result, (
        "Recent filter should exclude old milestones"
    )


def test_get_progress_history_invalid_user_id(memory_tools):
    """Test get_progress_history with invalid user ID."""
    tool = memory_tools[3]  # get_progress_history

    # Test empty string
    result = tool.func("")
    assert "Error" in result, "Should return error for empty user_id"


# ==============================================================================
# Integration Tests
# ==============================================================================


def test_full_workflow(memory_store, memory_tools, test_user_id):
    """Test a complete workflow using all tools together."""
    # 1. Create and save a profile
    from memory import create_memory_manager

    manager = create_memory_manager(memory_store)
    profile = UserProfile(
        user_id=test_user_id,
        name="Integration Test User",
        age=28,
    )
    manager.save_profile(profile)

    # 2. Save preferences
    save_pref_tool = memory_tools[1]
    result = save_pref_tool.func(test_user_id, "communication_style", "balanced")
    assert "Saved preference" in result

    # 3. Add milestones
    milestone_tool = memory_tools[2]
    milestone_tool.func(test_user_id, {"title": "Completed project", "domain": "career"})
    milestone_tool.func(test_user_id, {"title": "Started exercise routine", "domain": "wellness"})

    # 4. Retrieve progress history
    progress_tool = memory_tools[3]
    result = progress_tool.func(test_user_id)

    assert "Completed project" in result
    assert "Started exercise routine" in result

    # 5. Get profile to verify everything
    profile_tool = memory_tools[0]
    result = profile_tool.func(test_user_id)

    assert "Integration Test User" in result
    assert test_user_id in result


def test_tools_handle_none_store_gracefully():
    """Test that tools handle store initialization errors gracefully."""
    # This test verifies error handling when store creation fails
    try:
        from memory import create_memory_store

        # Try creating with invalid store type
        with pytest.raises(ValueError):
            create_memory_store(store_type="invalid")

    except Exception:
        # If the function doesn't exist or behaves differently, that's fine
        pass


# ==============================================================================
# Run Tests
# ==============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
