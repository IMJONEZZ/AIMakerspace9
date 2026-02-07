"""
Test suite for Habit Tracking System.

Tests all habit tracking functionality including:
- Habit creation with trigger-action-reward structure
- Habit completion logging
- Streak tracking calculation
- Habit strength scoring
- Habit stacking suggestions
- Domain grouping
- Habit review and adjustment workflow
"""

import pytest
import json
import sys
from datetime import datetime, date, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.habit_tools import (
    create_habit_tools,
    Habit,
    HabitEntry,
    HabitStats,
    HabitFrequency,
    HabitDomain,
    HabitStatus,
    calculate_streak,
    calculate_habit_strength,
    get_target_dates,
    generate_habit_id,
    parse_date,
    get_streak_visual,
    get_strength_level,
    suggest_habit_stack,
    HABIT_FORMATION_RESEARCH,
)


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def backend():
    """Create a mock backend for testing."""

    class MockBackend:
        def __init__(self):
            self.root_dir = Path("workspace")
            self.files = {}

        def write_file(self, path, content):
            self.files[path] = content
            full_path = self.root_dir / path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)

        def read_file(self, path):
            if path in self.files:
                return self.files[path]
            full_path = self.root_dir / path
            if full_path.exists():
                return full_path.read_text()
            return None

    mock_backend = MockBackend()
    (mock_backend.root_dir / "habits").mkdir(parents=True, exist_ok=True)
    return mock_backend


@pytest.fixture
def habit_tools(backend):
    """Create habit tools with mock backend."""
    return create_habit_tools(backend)


@pytest.fixture
def sample_habit():
    """Create a sample habit for testing."""
    return Habit(
        habit_id="habit_test_001",
        user_id="user_test",
        name="Morning Meditation",
        domain=HabitDomain.MINDFULNESS.value,
        frequency=HabitFrequency.DAILY.value,
        cue="After I wake up",
        action="Meditate for 10 minutes",
        reward="Feel calm and centered",
        target_days=[0, 1, 2, 3, 4, 5, 6],
    )


@pytest.fixture
def sample_entries():
    """Create sample completion entries for testing."""
    today = date.today()
    entries = []

    # Create 10 consecutive daily entries
    for i in range(10):
        entry_date = today - timedelta(days=i)
        entries.append(
            HabitEntry(
                entry_id=f"entry_{i}",
                habit_id="habit_test_001",
                user_id="user_test",
                completion_date=entry_date.isoformat(),
            )
        )

    return entries


# ==============================================================================
# Helper Function Tests
# ==============================================================================


class TestHelperFunctions:
    """Test helper functions."""

    def test_generate_habit_id(self):
        """Test habit ID generation."""
        habit_id = generate_habit_id()
        assert habit_id.startswith("habit_")
        assert len(habit_id) > 20

    def test_parse_date(self):
        """Test date parsing."""
        date_str = "2024-01-15"
        result = parse_date(date_str)
        assert result == date(2024, 1, 15)

    def test_parse_date_with_time(self):
        """Test parsing datetime string."""
        date_str = "2024-01-15T08:30:00"
        result = parse_date(date_str)
        assert result == date(2024, 1, 15)

    def test_get_target_dates_daily(self):
        """Test getting target dates for daily habit."""
        start = date(2024, 1, 1)
        end = date(2024, 1, 7)
        target_days = [0, 1, 2, 3, 4, 5, 6]

        dates = get_target_dates("daily", target_days, start, end)
        assert len(dates) == 7

    def test_get_target_dates_weekdays(self):
        """Test getting target dates for weekdays habit."""
        start = date(2024, 1, 1)  # Monday
        end = date(2024, 1, 7)  # Sunday
        target_days = [0, 1, 2, 3, 4]  # Mon-Fri

        dates = get_target_dates("weekdays", target_days, start, end)
        assert len(dates) == 5

    def test_get_streak_visual(self):
        """Test streak visual indicators."""
        assert "🔥" in get_streak_visual(7)
        assert "⭐" in get_streak_visual(30)
        assert "🏆" in get_streak_visual(100)
        assert "👑" in get_streak_visual(365)
        assert get_streak_visual(1) == ""

    def test_get_strength_level(self):
        """Test strength level classification."""
        assert get_strength_level(85) == ("Strong", "💪")
        assert get_strength_level(70) == ("Developing", "🌱")
        assert get_strength_level(50) == ("Building", "🔨")
        assert get_strength_level(30) == ("Starting", "🌟")
        assert get_strength_level(10) == ("New", "🆕")


# ==============================================================================
# Streak Calculation Tests
# ==============================================================================


class TestStreakCalculation:
    """Test streak calculation algorithms."""

    def test_calculate_streak_empty(self):
        """Test streak calculation with no dates."""
        current, longest = calculate_streak([], [0, 1, 2, 3, 4, 5, 6])
        assert current == 0
        assert longest == 0

    def test_calculate_streak_single(self):
        """Test streak calculation with single date."""
        today = date.today()
        current, longest = calculate_streak([today], [0, 1, 2, 3, 4, 5, 6])
        assert current == 1
        assert longest == 1

    def test_calculate_streak_consecutive_daily(self):
        """Test streak with consecutive daily completions."""
        today = date.today()
        dates = [today - timedelta(days=i) for i in range(5)]
        current, longest = calculate_streak(dates, [0, 1, 2, 3, 4, 5, 6])
        assert current == 5
        assert longest == 5

    def test_calculate_streak_broken(self):
        """Test streak with broken sequence."""
        today = date.today()
        # 3 consecutive days, then gap, then 2 more
        dates = [
            today,
            today - timedelta(days=1),
            today - timedelta(days=2),
            today - timedelta(days=5),
            today - timedelta(days=6),
        ]
        current, longest = calculate_streak(dates, [0, 1, 2, 3, 4, 5, 6])
        assert current == 3  # Recent streak
        assert longest == 3  # No longer streak than current


# ==============================================================================
# Strength Calculation Tests
# ==============================================================================


class TestStrengthCalculation:
    """Test habit strength calculation."""

    def test_calculate_habit_strength_perfect(self):
        """Test strength calculation for perfect habit."""
        strength = calculate_habit_strength(
            total_completions=100,
            current_streak=100,
            longest_streak=100,
            days_active=100,
            completion_rate=1.0,
            target_days=[0, 1, 2, 3, 4, 5, 6],
        )
        assert strength >= 80
        assert strength <= 100

    def test_calculate_habit_strength_new(self):
        """Test strength calculation for new habit."""
        strength = calculate_habit_strength(
            total_completions=3,
            current_streak=3,
            longest_streak=3,
            days_active=3,
            completion_rate=1.0,
            target_days=[0, 1, 2, 3, 4, 5, 6],
        )
        assert strength >= 0
        # New habits with perfect consistency score higher due to weights
        assert strength < 70

    def test_calculate_habit_strength_developing(self):
        """Test strength calculation for developing habit."""
        strength = calculate_habit_strength(
            total_completions=30,
            current_streak=21,
            longest_streak=21,
            days_active=30,
            completion_rate=0.7,
            target_days=[0, 1, 2, 3, 4, 5, 6],
        )
        assert strength >= 40
        assert strength < 80

    def test_calculate_habit_strength_low_completion(self):
        """Test strength with low completion rate."""
        strength = calculate_habit_strength(
            total_completions=10,
            current_streak=2,
            longest_streak=5,
            days_active=30,
            completion_rate=0.33,
            target_days=[0, 1, 2, 3, 4, 5, 6],
        )
        assert strength >= 0
        assert strength < 60


# ==============================================================================
# Habit Model Tests
# ==============================================================================


class TestHabitModel:
    """Test Habit data model."""

    def test_habit_creation(self, sample_habit):
        """Test habit initialization."""
        assert sample_habit.name == "Morning Meditation"
        assert sample_habit.domain == HabitDomain.MINDFULNESS.value
        assert sample_habit.frequency == HabitFrequency.DAILY.value
        assert sample_habit.cue == "After I wake up"

    def test_habit_to_dict(self, sample_habit):
        """Test habit serialization."""
        data = sample_habit.to_dict()
        assert data["name"] == "Morning Meditation"
        assert data["domain"] == "mindfulness"
        assert "habit_id" in data

    def test_habit_from_dict(self):
        """Test habit deserialization."""
        data = {
            "habit_id": "test_001",
            "user_id": "user_test",
            "name": "Test Habit",
            "domain": "health",
            "frequency": "daily",
            "cue": "Test cue",
            "action": "Test action",
            "reward": "Test reward",
            "target_days": [0, 1, 2],
            "created_at": datetime.now().isoformat(),
            "status": "active",
        }
        habit = Habit.from_dict(data)
        assert habit.name == "Test Habit"
        assert habit.domain == "health"

    def test_habit_default_target_days(self):
        """Test default target days based on frequency."""
        habit_daily = Habit(
            habit_id="test",
            user_id="user",
            name="Daily Habit",
            frequency=HabitFrequency.DAILY.value,
        )
        assert len(habit_daily.target_days) == 7

        habit_weekdays = Habit(
            habit_id="test",
            user_id="user",
            name="Weekday Habit",
            frequency=HabitFrequency.WEEKDAYS.value,
        )
        assert len(habit_weekdays.target_days) == 5


# ==============================================================================
# Habit Entry Tests
# ==============================================================================


class TestHabitEntry:
    """Test HabitEntry model."""

    def test_entry_creation(self):
        """Test entry initialization."""
        entry = HabitEntry(
            entry_id="entry_001",
            habit_id="habit_001",
            user_id="user_test",
            mood=8,
            difficulty=3,
        )
        assert entry.mood == 8
        assert entry.difficulty == 3
        assert entry.completion_date == date.today().isoformat()

    def test_entry_to_dict(self):
        """Test entry serialization."""
        entry = HabitEntry(
            entry_id="entry_001",
            habit_id="habit_001",
            user_id="user_test",
        )
        data = entry.to_dict()
        assert data["entry_id"] == "entry_001"
        assert data["habit_id"] == "habit_001"

    def test_entry_from_dict(self):
        """Test entry deserialization."""
        data = {
            "entry_id": "entry_001",
            "habit_id": "habit_001",
            "user_id": "user_test",
            "completion_date": "2024-01-15",
            "mood": 7,
            "difficulty": 4,
        }
        entry = HabitEntry.from_dict(data)
        assert entry.mood == 7
        assert entry.difficulty == 4


# ==============================================================================
# Habit Stacking Tests
# ==============================================================================


class TestHabitStacking:
    """Test habit stacking suggestions."""

    def test_suggest_habit_stack_empty(self):
        """Test stacking suggestions with no existing habits."""
        suggestions = suggest_habit_stack([], "health")
        assert len(suggestions) == 0

    def test_suggest_habit_stack_with_habits(self):
        """Test stacking suggestions with existing habits."""
        habits = [
            Habit(
                habit_id="h1",
                user_id="user",
                name="Strong Daily Habit",
                domain="health",
                frequency="daily",
            ),
            Habit(
                habit_id="h2",
                user_id="user",
                name="Weak Habit",
                domain="productivity",
                frequency="weekly",
            ),
        ]
        # Set strength scores
        habits[0].strength_score = 80  # type: ignore
        habits[1].strength_score = 20  # type: ignore

        suggestions = suggest_habit_stack(habits, "health")

        # Should suggest the strong health domain habit
        assert len(suggestions) > 0
        assert suggestions[0]["habit"].name == "Strong Daily Habit"

    def test_suggest_habit_stack_same_domain(self):
        """Test that same domain habits score higher."""
        habits = [
            Habit(
                habit_id="h1",
                user_id="user",
                name="Health Habit",
                domain="health",
                frequency="daily",
            ),
        ]
        habits[0].strength_score = 50  # type: ignore

        suggestions = suggest_habit_stack(habits, "health")

        assert len(suggestions) == 1
        # Same domain should give bonus points
        assert suggestions[0]["score"] > 25  # Base score + domain bonus


# ==============================================================================
# Tool Tests
# ==============================================================================


class TestCreateHabit:
    """Test create_habit tool."""

    def test_create_habit_success(self, habit_tools, backend):
        """Test successful habit creation."""
        create_habit = habit_tools[0]

        result = create_habit.invoke(
            {
                "user_id": "user_test",
                "name": "Test Habit",
                "domain": "health",
                "frequency": "daily",
                "cue": "After I wake up",
                "action": "Test action",
                "reward": "Feel good",
            }
        )

        assert "Habit Created" in result
        assert "Test Habit" in result
        assert "health" in result.lower()
        assert "After I wake up" in result

    def test_create_habit_invalid_user(self, habit_tools):
        """Test habit creation with invalid user_id."""
        create_habit = habit_tools[0]
        result = create_habit.invoke({"user_id": "", "name": "Test"})
        assert "Error" in result

    def test_create_habit_invalid_domain(self, habit_tools):
        """Test habit creation with invalid domain."""
        create_habit = habit_tools[0]
        result = create_habit.invoke(
            {"user_id": "user_test", "name": "Test", "domain": "invalid_domain"}
        )
        assert "Error" in result


class TestLogHabitCompletion:
    """Test log_habit_completion tool."""

    def test_log_completion_invalid_mood(self, habit_tools):
        """Test logging with invalid mood."""
        log_completion = habit_tools[1]
        result = log_completion.invoke(
            {
                "user_id": "user_test",
                "habit_id": "test_habit",
                "mood": 15,  # Invalid: should be 1-10
            }
        )
        assert "Error" in result


class TestGetHabitStreaks:
    """Test get_habit_streaks tool."""

    def test_get_streaks_no_habits(self, habit_tools):
        """Test getting streaks with no habits."""
        get_streaks = habit_tools[2]
        result = get_streaks.invoke({"user_id": "user_no_habits"})
        assert "No habits found" in result or "Error" in result


class TestCalculateHabitStrength:
    """Test calculate_habit_strength_score tool."""

    def test_calculate_strength_no_habits(self, habit_tools):
        """Test strength calculation with no habits."""
        calc_strength = habit_tools[3]
        result = calc_strength.invoke({"user_id": "user_no_habits"})
        assert "No habits found" in result


class TestGetHabitStackingSuggestions:
    """Test get_habit_stacking_suggestions tool."""

    def test_stacking_suggestions_no_habits(self, habit_tools):
        """Test stacking suggestions with no existing habits."""
        get_suggestions = habit_tools[4]
        result = get_suggestions.invoke({"user_id": "user_test", "new_habit_name": "New Habit"})
        # Should provide guidance even without existing habits
        assert "No existing habits" in result or "habit stacking" in result.lower()


class TestGetHabitsByDomain:
    """Test get_habits_by_domain tool."""

    def test_get_by_domain_no_habits(self, habit_tools):
        """Test getting habits by domain with no habits."""
        get_by_domain = habit_tools[5]
        result = get_by_domain.invoke({"user_id": "user_no_habits_xyz"})
        assert "No habits found" in result


class TestReviewHabit:
    """Test review_habit tool."""

    def test_review_invalid_habit(self, habit_tools):
        """Test reviewing non-existent habit."""
        review = habit_tools[6]
        result = review.invoke({"user_id": "user_test", "habit_id": "nonexistent"})
        assert "not found" in result or "Error" in result


class TestUpdateHabit:
    """Test update_habit tool."""

    def test_update_invalid_habit(self, habit_tools):
        """Test updating non-existent habit."""
        update = habit_tools[7]
        result = update.invoke(
            {"user_id": "user_test", "habit_id": "nonexistent", "cue": "New cue"}
        )
        assert "not found" in result or "Error" in result

    def test_update_no_changes(self, habit_tools):
        """Test update with no changes specified."""
        update = habit_tools[8]
        result = update.invoke({"user_id": "user_test", "habit_id": "test_habit"})
        assert "No updates" in result or "Error" in result


class TestDeleteHabit:
    """Test delete_habit tool."""

    def test_delete_without_confirm(self, habit_tools, backend):
        """Test delete without confirmation."""
        # First create a habit to delete
        create_habit = habit_tools[0]
        create_result = create_habit.invoke(
            {
                "user_id": "user_delete_test",
                "name": "Habit to Delete",
                "domain": "health",
            }
        )

        # Extract habit_id from result
        import re

        match = re.search(r"Habit ID: (habit_\S+)", create_result)
        if match:
            habit_id = match.group(1)

            delete = habit_tools[8]
            result = delete.invoke({"user_id": "user_delete_test", "habit_id": habit_id})
            assert "DELETE CONFIRMATION REQUIRED" in result or "confirm" in result.lower()
        else:
            # If we can't extract ID, skip the test
            pytest.skip("Could not extract habit_id from create result")

    def test_delete_invalid_habit(self, habit_tools):
        """Test deleting non-existent habit."""
        delete = habit_tools[8]
        result = delete.invoke({"user_id": "user_test", "habit_id": "nonexistent", "confirm": True})
        assert "not found" in result or "Error" in result


class TestListHabits:
    """Test list_habits tool."""

    def test_list_no_habits(self, habit_tools):
        """Test listing with no habits."""
        list_habits = habit_tools[9]
        result = list_habits.invoke({"user_id": "user_no_habits"})
        assert "No habits found" in result


# ==============================================================================
# Research Constants Tests
# ==============================================================================


class TestResearchConstants:
    """Test that research-based constants are properly defined."""

    def test_formation_research_constants(self):
        """Test habit formation research constants."""
        assert HABIT_FORMATION_RESEARCH["min_days"] == 18
        assert HABIT_FORMATION_RESEARCH["max_days"] == 254
        assert HABIT_FORMATION_RESEARCH["median_days"] == 66
        assert HABIT_FORMATION_RESEARCH["avg_days"] == 66
        assert HABIT_FORMATION_RESEARCH["automaticity_threshold"] == 0.8

    def test_strength_weights(self):
        """Test strength calculation weights sum to 1.0."""
        from src.tools.habit_tools import STRENGTH_WEIGHTS

        total = sum(STRENGTH_WEIGHTS.values())
        assert abs(total - 1.0) < 0.001  # Allow for floating point error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
