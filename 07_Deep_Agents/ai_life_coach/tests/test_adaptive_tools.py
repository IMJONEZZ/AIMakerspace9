"""
Test suite for adaptive recommendation engine tools.

This module provides comprehensive tests for the adaptive learning system,
including:
- Recommendation response tracking
- Effectiveness scoring algorithms
- Preference pattern learning
- Adaptation trigger detection
- Personalized alternative strategy generation
"""

import pytest
from pathlib import Path

# Import adaptive tools and helper functions
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.adaptive_tools import (
    calculate_task_completion_rate,
    detect_declining_trend,
    calculate_effectiveness_score,
    extract_preference_pattern,
    generate_alternative_strategy,
)


# ==============================================================================
# Helper Function Tests
# ==============================================================================


def test_calculate_task_completion_rate():
    """Test task completion rate calculation."""
    # Test with normal responses
    responses = {
        "career_goals_completed": 75,
        "relationship_goals_completed": 60,
        "finance_goals_completed": 80,
        "wellness_goals_completed": 70,
    }
    rate = calculate_task_completion_rate(responses)
    expected = (75 + 60 + 80 + 70) / 400
    assert rate == pytest.approx(expected, rel=0.01)

    # Test with all zeros
    zero_responses = {
        "career_goals_completed": 0,
        "relationship_goals_completed": 0,
        "finance_goals_completed": 0,
        "wellness_goals_completed": 0,
    }
    rate = calculate_task_completion_rate(zero_responses)
    assert rate == 0.0

    # Test with all 100s
    perfect_responses = {
        "career_goals_completed": 100,
        "relationship_goals_completed": 100,
        "finance_goals_completed": 100,
        "wellness_goals_completed": 100,
    }
    rate = calculate_task_completion_rate(perfect_responses)
    assert rate == 1.0


def test_detect_declining_trend():
    """Test declining trend detection."""
    # Test no previous values
    assert detect_declining_trend(5, [], -2) is False

    # Test stable values
    assert detect_declining_trend(5, [5, 5, 5], -2) is False

    # Test declining beyond threshold
    assert detect_declining_trend(3, [5, 5, 5], -2) is True

    # Test decline within threshold (should not trigger)
    assert detect_declining_trend(4, [5, 5, 5], -2) is False

    # Test improving values
    assert detect_declining_trend(7, [5, 5, 5], -2) is False


def test_calculate_effectiveness_score():
    """Test effectiveness score calculation."""
    # Test with all perfect scores
    score = calculate_effectiveness_score(
        completion_rate=1.0,
        user_satisfaction=1.0,
        consistency_bonus=1.5,
        context_alignment=1.0,
        time_efficiency=1.0,
    )
    assert score == 100.0

    # Test with all low scores
    score = calculate_effectiveness_score(
        completion_rate=0.3,
        user_satisfaction=0.4,
        consistency_bonus=0.8,
        context_alignment=0.5,
        time_efficiency=0.6,
    )
    assert 0 <= score <= 100

    # Test with missing satisfaction
    score = calculate_effectiveness_score(
        completion_rate=0.8,
        user_satisfaction=None,
        consistency_bonus=1.0,
        context_alignment=0.8,
        time_efficiency=0.7,
    )
    assert 40 <= score <= 100

    # Test that weights are applied correctly
    high_completion_score = calculate_effectiveness_score(
        completion_rate=1.0,
        user_satisfaction=0.5,
        consistency_bonus=1.0,
        context_alignment=0.5,
        time_efficiency=0.5,
    )

    low_completion_score = calculate_effectiveness_score(
        completion_rate=0.3,
        user_satisfaction=1.0,
        consistency_bonus=1.0,
        context_alignment=1.0,
        time_efficiency=1.0,
    )

    # High completion should produce higher score (40% weight)
    assert high_completion_score > low_completion_score


def test_extract_preference_pattern():
    """Test preference pattern extraction."""
    # Test with complete data
    recommendation_data = {
        "type": "exercise",
        "suggested_time": "morning",
        "suggested_day": "monday",
        "estimated_duration": 30,
        "steps_count": 5,
    }

    response_data = {
        "completed": True,
        "satisfaction_score": 8,
        "notes": "Felt good after morning exercise",
    }

    pattern = extract_preference_pattern(recommendation_data, response_data)

    assert pattern is not None
    assert pattern["category"] == "exercise"
    assert pattern["outcome"] is True
    assert pattern["user_rating"] == 8

    # Task size should be medium (30 min duration)
    assert pattern["task_size"] == "medium"

    # Task complexity should be moderate (5 steps)
    assert pattern["task_complexity"] == "moderate"


def test_generate_alternative_strategy():
    """Test alternative strategy generation."""
    # Test consecutive missed tasks trigger
    strategies = generate_alternative_strategy("consecutive_missed_tasks", {})
    assert "strategies" in strategies
    assert len(strategies["strategies"]) > 0
    assert "task_breakdown" in [s["type"] for s in strategies["strategies"]]
    assert "time_shift" in [s["type"] for s in strategies["strategies"]]

    # Test declining mood trigger
    strategies = generate_alternative_strategy("declining_mood", {})
    assert "mood_first" in [s["type"] for s in strategies["strategies"]]
    assert "gentle_scaling" in [s["type"] for s in strategies["strategies"]]

    # Test declining energy trigger
    strategies = generate_alternative_strategy("declining_energy", {})
    assert "energy_matching" in [s["type"] for s in strategies["strategies"]]
    assert "micro_rest_periods" in [s["type"] for s in strategies["strategies"]]

    # Test with failed recommendation context
    failed_rec = {"title": "Complete project report"}
    strategies = generate_alternative_strategy("consecutive_missed_tasks", {}, failed_rec)
    assert all("based_on" in s for s in strategies["strategies"])  # All should have context


# ==============================================================================
# Tool Integration Tests
# ==============================================================================


@pytest.fixture
def backend():
    """Create a mock backend for testing."""

    class MockBackend:
        def __init__(self):
            self.root_dir = Path("workspace")
            self.files = {}

        def write_file(self, path, content):
            # Store in both files dict and actual filesystem
            self.files[path] = content
            full_path = self.root_dir / path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)

        def read_file(self, path):
            # Return from files dict if available
            if path in self.files:
                return self.files[path]
            # Otherwise read from disk
            full_path = self.root_dir / path
            if full_path.exists():
                return full_path.read_text()
            raise FileNotFoundError(f"File not found: {path}")

    mock_backend = MockBackend()

    # Initialize config
    try:
        from src.config import config

        config.initialize_environment()
    except Exception:
        pass  # Config already initialized or not available

    yield mock_backend


@pytest.fixture
def adaptive_tools(backend):
    """Create adaptive tools with mock backend."""
    from src.tools.adaptive_tools import create_adaptive_tools

    return create_adaptive_tools(backend)


def test_track_recommendation_response_basic(backend, adaptive_tools):
    """Test basic recommendation response tracking."""
    track_recommendation_response = adaptive_tools[0]

    user_id = "test_user_adaptive"
    result = track_recommendation_response.invoke(
        {
            "user_id": user_id,
            "recommendation_id": "test_rec_001",
            "completed": True,
            "satisfaction_score": 8,
            "actual_duration_minutes": 30,
        }
    )

    assert "Recommendation Response Tracked" in result
    assert "test_rec_001" in result
    assert "✓ Completed" in result

    # Verify file was created
    pref_path = f"adaptive/{user_id}/preferences/profile.json"
    assert backend.read_file(pref_path) is not None


def test_track_recommendation_response_multiple(backend, adaptive_tools):
    """Test tracking multiple responses to build learning data."""
    track_recommendation_response = adaptive_tools[0]

    user_id = "test_user_multiple"

    # Track 5 responses
    for i in range(5):
        track_recommendation_response.invoke(
            {
                "user_id": user_id,
                "recommendation_id": f"test_rec_{i:03d}",
                "completed": i % 2 == 0,  # Alternate completion
                "satisfaction_score": 7 if i % 2 == 0 else 4,
            }
        )

    # Last response should show learning insights
    result = track_recommendation_response.invoke(
        {
            "user_id": user_id,
            "recommendation_id": "test_rec_005",
            "completed": True,
            "satisfaction_score": 9,
        }
    )

    assert "Learning Insights" in result
    assert "Total recommendations tracked:" in result


def test_calculate_recommendation_effectiveness_basic(backend, adaptive_tools):
    """Test basic effectiveness score calculation."""
    track_recommendation_response = adaptive_tools[0]
    calculate_recommendation_effectiveness = adaptive_tools[1]

    user_id = "test_user_effectiveness"

    # Track some responses first
    for i in range(5):
        track_recommendation_response.invoke(
            {
                "user_id": user_id,
                "recommendation_id": f"effectiveness_test_{i}",
                "completed": i < 3,  # First 3 completed
                "satisfaction_score": 8 if i < 3 else 5,
            }
        )

    # Calculate effectiveness
    result = calculate_recommendation_effectiveness.invoke({"user_id": user_id})

    assert "Recommendation Effectiveness Analysis" in result
    assert "Overall Score:" in result

    # Score should be between 0 and 100
    import re

    score_match = re.search(r"Overall Score: (\d+\.?\d*)/100", result)
    assert score_match is not None

    score = float(score_match.group(1))
    assert 0 <= score <= 100


def test_learn_user_preferences_with_data(backend, adaptive_tools):
    """Test preference learning with sufficient data."""
    track_recommendation_response = adaptive_tools[0]
    learn_user_preferences = adaptive_tools[2]

    user_id = "test_user_learn_prefs"

    # Track responses with different durations
    track_recommendation_response.invoke(
        {
            "user_id": user_id,
            "recommendation_id": "short_task",
            "completed": True,
            "satisfaction_score": 9,
            "actual_duration_minutes": 10,  # Small
        }
    )

    track_recommendation_response.invoke(
        {
            "user_id": user_id,
            "recommendation_id": "medium_task",
            "completed": True,
            "satisfaction_score": 8,
            "actual_duration_minutes": 45,  # Medium
        }
    )

    track_recommendation_response.invoke(
        {
            "user_id": user_id,
            "recommendation_id": "another_short",
            "completed": True,
            "satisfaction_score": 9,
            "actual_duration_minutes": 12,  # Small
        }
    )

    result = learn_user_preferences.invoke({"user_id": user_id})

    assert "User Preference Learning Complete" in result
    assert "Learned Preferences:" in result


def test_generate_personalized_alternatives_basic(backend, adaptive_tools):
    """Test basic alternative strategy generation."""
    generate_personalized_alternatives = adaptive_tools[4]

    user_id = "test_user_alternatives"

    result = generate_personalized_alternatives.invoke(
        {
            "user_id": user_id,
            "trigger_type": "consecutive_missed_tasks",
        }
    )

    assert "Personalized Alternative Strategies" in result
    assert "Recommended Strategies" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
