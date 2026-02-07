"""
Test suite for the AI Life Coach memory system.

Tests all namespace operations, data models, and CRUD functionality.
"""

import pytest
from uuid import uuid4

# Import the memory module components
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from memory import (
    # Namespace functions
    get_profile_namespace,
    get_goals_namespace,
    get_progress_namespace,
    get_preferences_namespace,
    get_coaching_patterns_namespace,
    # Data models
    UserProfile,
    Goal,
    Milestone,
    Setback,
    UserPreferences,
    CoachingPattern,
    # Factory functions
    create_memory_store,
    create_memory_manager,
    # Memory manager
    MemoryManager,
)


# ==============================================================================
# Namespace Function Tests
# ==============================================================================


def test_profile_namespace():
    """Test profile namespace generation."""
    user_id = "test_user_123"
    namespace = get_profile_namespace(user_id)
    assert namespace == (user_id, "profile")
    assert len(namespace) == 2


def test_goals_namespace():
    """Test goals namespace generation."""
    user_id = "test_user_123"
    namespace = get_goals_namespace(user_id)
    assert namespace == (user_id, "goals")


def test_progress_namespace():
    """Test progress namespace generation."""
    user_id = "test_user_123"
    namespace = get_progress_namespace(user_id)
    assert namespace == (user_id, "progress")


def test_preferences_namespace():
    """Test preferences namespace generation."""
    user_id = "test_user_123"
    namespace = get_preferences_namespace(user_id)
    assert namespace == (user_id, "preferences")


def test_coaching_patterns_namespace():
    """Test coaching patterns namespace generation."""
    namespace = get_coaching_patterns_namespace()
    assert namespace == ("coaching", "patterns")
    # This should be a cross-user namespace without user_id


# ==============================================================================
# Data Model Tests
# ==============================================================================


def test_user_profile_creation():
    """Test UserProfile creation and serialization."""
    profile = UserProfile(
        user_id="user_123",
        name="Alex Johnson",
        age=35,
        occupation="Software Engineer",
        relationship_status="Single",
        values=["growth", "balance", "autonomy"],
    )

    assert profile.user_id == "user_123"
    assert profile.name == "Alex Johnson"
    assert profile.age == 35
    assert len(profile.values) == 3

    # Test serialization
    profile_dict = profile.to_dict()
    assert profile_dict["user_id"] == "user_123"
    assert profile_dict["name"] == "Alex Johnson"

    # Test deserialization
    profile_restored = UserProfile.from_dict(profile_dict)
    assert profile_restored.user_id == profile.user_id
    assert profile_restored.name == profile.name


def test_goal_creation():
    """Test Goal creation and serialization."""
    goal = Goal(
        title="Learn Python",
        description="Complete a 6-month Python course",
        domain="career",
        priority=4,
        status="in_progress",
        timeframe="medium",
    )

    assert goal.title == "Learn Python"
    assert goal.domain == "career"
    assert goal.priority == 4
    assert goal.goal_id is not None

    # Test serialization
    goal_dict = goal.to_dict()
    assert goal_dict["title"] == "Learn Python"
    assert goal_dict["goal_id"] is not None

    # Test deserialization
    goal_restored = Goal.from_dict(goal_dict)
    assert goal_restored.title == goal.title
    assert goal_restored.goal_id == goal.goal_id


def test_milestone_creation():
    """Test Milestone creation and serialization."""
    milestone = Milestone(
        title="Completed Python Course",
        description="Finished 6-month intensive course",
        domain="career",
        significance="major",
    )

    assert milestone.title == "Completed Python Course"
    assert milestone.domain == "career"
    assert milestone.milestone_id is not None

    # Test serialization
    milestone_dict = milestone.to_dict()
    assert milestone_dict["title"] == "Completed Python Course"
    assert milestone_dict["milestone_id"] is not None

    # Test deserialization
    milestone_restored = Milestone.from_dict(milestone_dict)
    assert milestone_restored.title == milestone.title
    assert milestone_restored.milestone_id == milestone.milestone_id


def test_setback_creation():
    """Test Setback creation and serialization."""
    setback = Setback(
        description="Missed several study sessions",
        domain="career",
        resolved=True,
        resolution_notes="Created a stricter schedule and accountability partner",
    )

    assert setback.description == "Missed several study sessions"
    assert setback.resolved is True
    assert setback.setback_id is not None

    # Test serialization
    setback_dict = setback.to_dict()
    assert setback_dict["description"] == "Missed several study sessions"
    assert setback_dict["resolved"] is True

    # Test deserialization
    setback_restored = Setback.from_dict(setback_dict)
    assert setback_restored.description == setback.description
    assert setback_restored.resolved is True


def test_user_preferences_creation():
    """Test UserPreferences creation and serialization."""
    preferences = UserPreferences(
        user_id="user_123",
        communication_style="detailed",
        coaching_approach="collaborative",
        preferred_checkin_frequency="weekly",
    )

    assert preferences.user_id == "user_123"
    assert preferences.communication_style == "detailed"
    assert preferences.coaching_approach == "collaborative"

    # Test serialization
    prefs_dict = preferences.to_dict()
    assert prefs_dict["user_id"] == "user_123"
    assert prefs_dict["communication_style"] == "detailed"

    # Test deserialization
    prefs_restored = UserPreferences.from_dict(prefs_dict)
    assert prefs_restored.user_id == preferences.user_id
    assert prefs_restored.communication_style == preferences.communication_style


def test_coaching_pattern_creation():
    """Test CoachingPattern creation and serialization."""
    pattern = CoachingPattern(
        title="Micro-commitments for goal achievement",
        description="Breaking large goals into tiny, manageable daily actions",
        category="strategy",
        effectiveness_score=0.85,
        usage_count=42,
    )

    assert pattern.title == "Micro-commitments for goal achievement"
    assert pattern.category == "strategy"
    assert pattern.effectiveness_score == 0.85

    # Test serialization
    pattern_dict = pattern.to_dict()
    assert pattern_dict["title"] == "Micro-commitments for goal achievement"
    assert pattern_dict["effectiveness_score"] == 0.85

    # Test deserialization
    pattern_restored = CoachingPattern.from_dict(pattern_dict)
    assert pattern_restored.title == pattern.title
    assert pattern_restored.effectiveness_score == pattern.effectiveness_score


# ==============================================================================
# Memory Store Factory Tests
# ==============================================================================


def test_create_in_memory_store():
    """Test creating an InMemoryStore."""
    try:
        store = create_memory_store("in_memory")
        assert store is not None
        # Store should be usable (no errors on basic operations)
    except ValueError as e:
        pytest.skip(f"LangGraph not available: {e}")


def test_create_invalid_store_type():
    """Test that invalid store types raise ValueError."""
    with pytest.raises(ValueError):
        create_memory_store("invalid_type")


# ==============================================================================
# Memory Manager Tests
# ==============================================================================


def test_memory_manager_initialization():
    """Test MemoryManager initialization."""
    try:
        store = create_memory_store("in_memory")
        manager = MemoryManager(store)
        assert manager.store is store
    except ValueError:
        pytest.skip("LangGraph not available")


def test_memory_manager_requires_store():
    """Test that MemoryManager raises error with None store."""
    with pytest.raises(ValueError):
        MemoryManager(None)


# ==============================================================================
# Profile CRUD Tests
# ==============================================================================


def test_save_and_get_profile():
    """Test saving and retrieving a user profile."""
    try:
        store = create_memory_store("in_memory")
        manager = MemoryManager(store)

        user_id = "test_user_profile"
        profile = UserProfile(
            user_id=user_id,
            name="Test User",
            age=30,
            occupation="Engineer",
        )

        # Save profile
        manager.save_profile(profile)

        # Retrieve profile
        retrieved = manager.get_profile(user_id)
        assert retrieved is not None
        assert retrieved.name == "Test User"
        assert retrieved.age == 30

    except ValueError:
        pytest.skip("LangGraph not available")


def test_profile_exists():
    """Test checking if a profile exists."""
    try:
        store = create_memory_store("in_memory")
        manager = MemoryManager(store)

        user_id = "test_user_exists"
        assert not manager.profile_exists(user_id)

        # Create and save profile
        profile = UserProfile(user_id=user_id, name="Exist User")
        manager.save_profile(profile)

        assert manager.profile_exists(user_id)

    except ValueError:
        pytest.skip("LangGraph not available")


def test_get_nonexistent_profile():
    """Test retrieving a non-existent profile returns None."""
    try:
        store = create_memory_store("in_memory")
        manager = MemoryManager(store)

        retrieved = manager.get_profile("nonexistent_user")
        assert retrieved is None

    except ValueError:
        pytest.skip("LangGraph not available")


# ==============================================================================
# Goal CRUD Tests
# ==============================================================================


def test_save_and_get_goal():
    """Test saving and retrieving a single goal."""
    try:
        store = create_memory_store("in_memory")
        manager = MemoryManager(store)

        user_id = "test_user_goals"
        goal = Goal(
            title="Read 10 Books",
            description="Complete reading challenge for the year",
            domain="wellness",
        )

        # Save goal
        manager.save_goal(user_id, goal)

        # Retrieve goal
        retrieved = manager.get_goal(user_id, goal.goal_id)
        assert retrieved is not None
        assert retrieved.title == "Read 10 Books"
        assert retrieved.domain == "wellness"

    except ValueError:
        pytest.skip("LangGraph not available")


def test_get_goals_by_user():
    """Test retrieving all goals for a user."""
    try:
        store = create_memory_store("in_memory")
        manager = MemoryManager(store)

        user_id = "test_user_multi_goals"

        # Create multiple goals
        goal1 = Goal(title="Goal 1", domain="career")
        goal2 = Goal(title="Goal 2", domain="wellness")
        goal3 = Goal(title="Goal 3", domain="finance")

        manager.save_goal(user_id, goal1)
        manager.save_goal(user_id, goal2)
        manager.save_goal(user_id, goal3)

        # Retrieve all goals
        goals = manager.get_goals(user_id)
        assert len(goals) == 3

    except ValueError:
        pytest.skip("LangGraph not available")


def test_get_goals_by_domain():
    """Test retrieving goals filtered by domain."""
    try:
        store = create_memory_store("in_memory")
        manager = MemoryManager(store)

        user_id = "test_user_domain_goals"

        # Create goals across domains
        goal1 = Goal(title="Career Goal", domain="career")
        goal2 = Goal(title="Wellness Goal", domain="wellness")
        goal3 = Goal(title="Another Career Goal", domain="career")

        manager.save_goal(user_id, goal1)
        manager.save_goal(user_id, goal2)
        manager.save_goal(user_id, goal3)

        # Filter by career domain
        career_goals = manager.get_goals_by_domain(user_id, "career")
        assert len(career_goals) == 2

        # Filter by wellness domain
        wellness_goals = manager.get_goals_by_domain(user_id, "wellness")
        assert len(wellness_goals) == 1

    except ValueError:
        pytest.skip("LangGraph not available")


def test_delete_goal():
    """Test deleting a goal."""
    try:
        store = create_memory_store("in_memory")
        manager = MemoryManager(store)

        user_id = "test_user_delete_goal"
        goal = Goal(title="Delete Me", domain="career")

        manager.save_goal(user_id, goal)

        # Verify exists
        assert manager.get_goal(user_id, goal.goal_id) is not None

        # Delete
        result = manager.delete_goal(user_id, goal.goal_id)
        assert result is True

        # Verify deleted
        assert manager.get_goal(user_id, goal.goal_id) is None

    except ValueError:
        pytest.skip("LangGraph not available")


def test_save_goal_empty_user_id():
    """Test that saving a goal with empty user_id raises ValueError."""
    try:
        store = create_memory_store("in_memory")
        manager = MemoryManager(store)

        goal = Goal(title="No User", domain="career")

        with pytest.raises(ValueError):
            manager.save_goal("", goal)

    except ValueError:
        pytest.skip("LangGraph not available")


# ==============================================================================
# Progress CRUD Tests
# ==============================================================================


def test_add_and_get_milestones():
    """Test adding and retrieving milestones."""
    try:
        store = create_memory_store("in_memory")
        manager = MemoryManager(store)

        user_id = "test_user_milestones"

        milestone1 = Milestone(title="First Achievement", domain="career")
        milestone2 = Milestone(title="Second Achievement", domain="wellness")

        manager.add_milestone(user_id, milestone1)
        manager.add_milestone(user_id, milestone2)

        milestones = manager.get_milestones(user_id)
        assert len(milestones) == 2

    except ValueError:
        pytest.skip("LangGraph not available")


def test_add_and_get_setbacks():
    """Test adding and retrieving setbacks."""
    try:
        store = create_memory_store("in_memory")
        manager = MemoryManager(store)

        user_id = "test_user_setbacks"

        setback1 = Setback(description="First Challenge", domain="career")
        setback2 = Setback(
            description="Second Challenge",
            domain="wellness",
            resolved=True,
        )

        manager.add_setback(user_id, setback1)
        manager.add_setback(user_id, setback2)

        setbacks = manager.get_setbacks(user_id)
        assert len(setbacks) == 2

    except ValueError:
        pytest.skip("LangGraph not available")


# ==============================================================================
# Preferences CRUD Tests
# ==============================================================================


def test_save_and_get_preferences():
    """Test saving and retrieving user preferences."""
    try:
        store = create_memory_store("in_memory")
        manager = MemoryManager(store)

        user_id = "test_user_prefs"
        preferences = UserPreferences(
            user_id=user_id,
            communication_style="concise",
            coaching_approach="direct",
        )

        manager.save_preferences(preferences)

        retrieved = manager.get_preferences(user_id)
        assert retrieved is not None
        assert retrieved.communication_style == "concise"
        assert retrieved.coaching_approach == "direct"

    except ValueError:
        pytest.skip("LangGraph not available")


def test_update_single_preference():
    """Test updating a single preference field."""
    try:
        store = create_memory_store("in_memory")
        manager = MemoryManager(store)

        user_id = "test_user_update_pref"
        preferences = UserPreferences(
            user_id=user_id,
            communication_style="balanced",
        )
        manager.save_preferences(preferences)

        # Update single field
        manager.update_preference_key(user_id, "communication_style", "detailed")

        # Verify update
        retrieved = manager.get_preferences(user_id)
        assert retrieved is not None
        assert retrieved.communication_style == "detailed"

    except ValueError:
        pytest.skip("LangGraph not available")


# ==============================================================================
# Coaching Patterns Tests
# ==============================================================================


def test_save_and_get_pattern():
    """Test saving and retrieving a coaching pattern."""
    try:
        store = create_memory_store("in_memory")
        manager = MemoryManager(store)

        pattern = CoachingPattern(
            title="Effective Strategy",
            description="Test strategy pattern",
            category="strategy",
        )

        manager.save_pattern(pattern)

        retrieved = manager.get_pattern(pattern.pattern_id)
        assert retrieved is not None
        assert retrieved.title == "Effective Strategy"

    except ValueError:
        pytest.skip("LangGraph not available")


def test_get_patterns_by_domain():
    """Test retrieving patterns filtered by domain."""
    try:
        store = create_memory_store("in_memory")
        manager = MemoryManager(store)

        pattern1 = CoachingPattern(
            title="Career Strategy",
            category="strategy",
            related_domains=["career"],
        )
        pattern2 = CoachingPattern(
            title="Wellness Strategy",
            category="strategy",
            related_domains=["wellness"],
        )

        manager.save_pattern(pattern1)
        manager.save_pattern(pattern2)

        career_patterns = manager.get_patterns_by_domain("career")
        assert len(career_patterns) == 1
        assert career_patterns[0].title == "Career Strategy"

    except ValueError:
        pytest.skip("LangGraph not available")


def test_increment_pattern_usage():
    """Test incrementing pattern usage count."""
    try:
        store = create_memory_store("in_memory")
        manager = MemoryManager(store)

        pattern = CoachingPattern(
            title="Popular Pattern",
            category="strategy",
            usage_count=5,
        )

        manager.save_pattern(pattern)

        # Increment
        manager.increment_pattern_usage(pattern.pattern_id)

        # Verify increment
        retrieved = manager.get_pattern(pattern.pattern_id)
        assert retrieved is not None
        assert retrieved.usage_count == 6

    except ValueError:
        pytest.skip("LangGraph not available")


# ==============================================================================
# Integration Tests
# ==============================================================================


def test_get_user_summary():
    """Test getting comprehensive user summary."""
    try:
        store = create_memory_store("in_memory")
        manager = MemoryManager(store)

        user_id = "test_user_summary"

        # Set up profile
        profile = UserProfile(user_id=user_id, name="Summary User")
        manager.save_profile(profile)

        # Add a goal
        goal = Goal(title="Summary Goal", domain="career")
        manager.save_goal(user_id, goal)

        # Add a milestone
        milestone = Milestone(title="Summary Milestone", domain="career")
        manager.add_milestone(user_id, milestone)

        # Set preferences
        prefs = UserPreferences(user_id=user_id)
        manager.save_preferences(prefs)

        # Get summary
        summary = manager.get_user_summary(user_id)
        assert summary["profile"] is not None
        assert len(summary["goals"]) == 1
        assert len(summary["milestones"]) == 1

    except ValueError:
        pytest.skip("LangGraph not available")


def test_delete_user_data():
    """Test deleting all user data."""
    try:
        store = create_memory_store("in_memory")
        manager = MemoryManager(store)

        user_id = "test_user_delete"

        # Set up various data
        profile = UserProfile(user_id=user_id, name="Delete User")
        manager.save_profile(profile)

        goal = Goal(title="Delete Goal", domain="career")
        manager.save_goal(user_id, goal)

        milestone = Milestone(title="Delete Milestone", domain="career")
        manager.add_milestone(user_id, milestone)

        # Delete all data
        result = manager.delete_user_data(user_id)
        assert result is True

        # Verify deletion
        assert manager.get_profile(user_id) is None
        assert len(manager.get_goals(user_id)) == 0
        assert len(manager.get_milestones(user_id)) == 0

    except ValueError:
        pytest.skip("LangGraph not available")


# ==============================================================================
# Main Test Runner
# ==============================================================================

if __name__ == "__main__":
    # Run tests with pytest if available, otherwise use simple runner
    try:
        import subprocess

        print("Running tests with pytest...")
        result = subprocess.run(
            ["python", "-m", "pytest", __file__, "-v"],
            capture_output=False,
        )
        exit(result.returncode)
    except ImportError:
        print("pytest not available. Running basic test suite...")

        # Simple test runner
        tests = [
            test_profile_namespace,
            test_goals_namespace,
            test_progress_namespace,
            test_preferences_namespace,
            test_coaching_patterns_namespace,
            test_user_profile_creation,
            test_goal_creation,
            test_milestone_creation,
            test_setback_creation,
            test_user_preferences_creation,
            test_coaching_pattern_creation,
        ]

        passed = 0
        failed = 0

        for test in tests:
            try:
                test()
                print(f"✓ {test.__name__}")
                passed += 1
            except Exception as e:
                print(f"✗ {test.__name__}: {e}")
                failed += 1

        print(f"\n{passed} passed, {failed} failed")
        exit(0 if failed == 0 else 1)
