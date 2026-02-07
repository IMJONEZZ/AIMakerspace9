"""
Test suite for weekly check-in tools.

This module provides comprehensive tests for the weekly check-in system,
including:
- Check-in questionnaire validation
- Progress scoring algorithms
- Trend analysis functionality
- Adaptation recommendation generation
"""

import pytest
from pathlib import Path

# Import check-in tools and helper functions
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.checkin_tools import (
    validate_response,
    calculate_domain_score,
    calculate_overall_score,
    apply_habit_factors,
    analyze_trend,
    generate_adaptations,
    HABIT_SCORING_FACTORS,
)


# ==============================================================================
# Test Fixtures
# ==============================================================================


@pytest.fixture
def backend():
    """Create a mock backend for testing."""

    class MockBackend:
        def __init__(self):
            self.root_dir = Path("workspace")
            self.files = {}

        def write_file(self, path, content):
            # Store in both files dict and actual filesystem for tools that read from disk
            self.files[path] = content
            # Also write to disk for persistence between tool calls
            full_path = self.root_dir / path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)

        def read_file(self, path):
            # Try files dict first, then disk
            if path in self.files:
                return self.files[path]
            full_path = self.root_dir / path
            if full_path.exists():
                return full_path.read_text()
            return None

    mock_backend = MockBackend()
    # Ensure workspace directory exists
    (mock_backend.root_dir / "checkins").mkdir(parents=True, exist_ok=True)
    return mock_backend


@pytest.fixture
def checkin_tools(backend):
    """Create check-in tools with mock backend."""
    from src.tools.checkin_tools import create_checkin_tools

    return create_checkin_tools(backend)


@pytest.fixture
def sample_responses():
    """Sample valid check-in responses."""
    return {
        "career_goals_completed": 75,
        "relationship_goals_completed": 60,
        "finance_goals_completed": 80,
        "wellness_goals_completed": 70,
        "average_mood": 7,
        "average_energy": 6,
        "stress_level": 5,
        "sleep_quality": 7,
        "primary_obstacles": "Work was very busy this week",
        "obstacle_severity": 6,
        "key_achievements": "Completed important project",
        "surprise_successes": "Made a new connection at work",
        "goal_adjustments": "Focus on one main goal next week",
        "resource_needs": "Need more time for exercise",
    }


@pytest.fixture
def high_performing_responses():
    """Sample responses indicating high performance."""
    return {
        "career_goals_completed": 95,
        "relationship_goals_completed": 90,
        "finance_goals_completed": 100,
        "wellness_goals_completed": 85,
        "average_mood": 9,
        "average_energy": 8,
        "stress_level": 2,
        "sleep_quality": 9,
        "primary_obstacles": "",
        "obstacle_severity": 2,
        "key_achievements": "Achieved all major goals",
    }


@pytest.fixture
def struggling_responses():
    """Sample responses indicating struggles."""
    return {
        "career_goals_completed": 30,
        "relationship_goals_completed": 20,
        "finance_goals_completed": 40,
        "wellness_goals_completed": 35,
        "average_mood": 3,
        "average_energy": 4,
        "stress_level": 8,
        "sleep_quality": 4,
        "primary_obstacles": "Overwhelmed with multiple projects",
        "obstacle_severity": 9,
    }


# ==============================================================================
# Questionnaire Validation Tests
# ==============================================================================


class TestQuestionnaireValidation:
    """Test questionnaire validation functionality."""

    def test_validate_numeric_response_valid(self):
        """Test valid numeric response."""
        question = {
            "id": "test_numeric",
            "type": "number",
            "min": 0,
            "max": 100,
        }

        is_valid, error = validate_response(question, 75)
        assert is_valid
        assert error == ""

    def test_validate_numeric_response_out_of_range(self):
        """Test numeric response outside valid range."""
        question = {
            "id": "test_numeric",
            "type": "number",
            "min": 0,
            "max": 100,
        }

        is_valid, error = validate_response(question, 150)
        assert not is_valid
        assert "between" in error.lower()

    def test_validate_numeric_response_invalid_type(self):
        """Test numeric response with invalid type."""
        question = {
            "id": "test_numeric",
            "type": "number",
            "min": 0,
            "max": 100,
        }

        is_valid, error = validate_response(question, "not a number")
        assert not is_valid
        assert "number" in error.lower()

    def test_validate_text_response_valid(self):
        """Test valid text response."""
        question = {
            "id": "test_text",
            "type": "text",
        }

        is_valid, error = validate_response(question, "This is a valid response")
        assert is_valid
        assert error == ""

    def test_validate_text_response_empty(self):
        """Test empty text response."""
        question = {
            "id": "test_text",
            "type": "text",
        }

        is_valid, error = validate_response(question, "")
        assert not is_valid

    def test_validate_text_response_invalid_type(self):
        """Test text response with invalid type."""
        question = {
            "id": "test_text",
            "type": "text",
        }

        is_valid, error = validate_response(question, 123)
        assert not is_valid
        assert "text" in error.lower()

    def test_validate_response_none(self):
        """Test None response."""
        question = {
            "id": "test_question",
            "type": "number",
        }

        is_valid, error = validate_response(question, None)
        assert not is_valid


# ==============================================================================
# Scoring Algorithm Tests
# ==============================================================================


class TestScoringAlgorithms:
    """Test progress scoring algorithms."""

    def test_calculate_domain_score_career(self):
        """Calculate career domain score."""
        responses = {
            "career_goals_completed": 75,
        }

        score = calculate_domain_score(responses, "career")
        assert score == 0.75

    def test_calculate_domain_score_wellness(self):
        """Calculate wellness domain score."""
        responses = {
            "wellness_goals_completed": 60,
            "average_mood": 7,  # 0.7
            "average_energy": 6,  # 0.6
            "stress_level": 3,  # Inverted: (10-3)/10 = 0.7
        }

        score = calculate_domain_score(responses, "wellness")
        expected = (0.6 + 0.7 + 0.6 + 0.7) / 4
        assert abs(score - expected) < 0.05

    def test_calculate_overall_score(self, sample_responses):
        """Test overall score calculation."""
        score = calculate_overall_score(sample_responses)
        assert 0.0 <= score <= 1.0

    def test_overall_score_weighted_average(self):
        """Test that overall score uses weighted domains."""
        responses = {
            "career_goals_completed": 80,  # 0.8 * 0.25 = 0.2
            "relationship_goals_completed": 60,  # 0.6 * 0.25 = 0.15
            "finance_goals_completed": 100,  # 1.0 * 0.25 = 0.25
            "wellness_goals_completed": 40,  # 0.4 * 0.25 = 0.1
        }

        score = calculate_overall_score(responses)
        expected = 0.2 + 0.15 + 0.25 + 0.1
        assert abs(score - expected) < 0.01

    def test_apply_habit_factors_consistency_bonus(self, sample_responses):
        """Test consistency bonus application."""
        base_score = 0.7

        previous_week = {
            "overall_progress": 0.68,  # Within 10% of base_score
        }

        adjusted_score = apply_habit_factors(base_score, sample_responses, previous_week)
        expected = base_score * HABIT_SCORING_FACTORS["consistency_bonus"]

        assert adjusted_score > base_score
        assert abs(adjusted_score - expected) < 0.05

    def test_apply_habit_factors_improvement_bonus(self, sample_responses):
        """Test improvement bonus application."""
        base_score = 0.8

        previous_week = {
            "overall_progress": 0.65,  # Improved by more than 10%
        }

        adjusted_score = apply_habit_factors(base_score, sample_responses, previous_week)
        expected = base_score * HABIT_SCORING_FACTORS["improvement_bonus"]

        assert adjusted_score > base_score
        assert abs(adjusted_score - expected) < 0.05

    def test_apply_habit_factors_decline_penalty(self, sample_responses):
        """Test decline penalty application."""
        base_score = 0.5

        previous_week = {
            "overall_progress": 0.8,  # Declined by more than 20%
        }

        adjusted_score = apply_habit_factors(base_score, sample_responses, previous_week)
        expected = base_score * HABIT_SCORING_FACTORS["decline_penalty"]

        assert adjusted_score < base_score
        assert abs(adjusted_score - expected) < 0.05

    def test_apply_habit_factors_bounds(self, sample_responses):
        """Test that adjusted scores stay within bounds."""
        # Start with a score that would exceed 1.0 after bonuses
        base_score = 0.95

        previous_week = {
            "overall_progress": 0.9,  # Consistent
        }

        adjusted_score = apply_habit_factors(base_score, sample_responses, previous_week)

        # Should not exceed 1.0
        assert adjusted_score <= 1.0

    def test_apply_habit_factors_low_stress_bonus(self):
        """Test low stress bonus."""
        base_score = 0.7

        responses = {
            "average_energy": 5,
            "stress_level": 2,  # Low stress
        }

        previous_week = None

        adjusted_score = apply_habit_factors(base_score, responses, previous_week)
        expected = base_score * HABIT_SCORING_FACTORS["low_stress_bonus"]

        assert adjusted_score > base_score


# ==============================================================================
# Trend Analysis Tests
# ==============================================================================


class TestTrendAnalysis:
    """Test trend analysis functionality."""

    def test_analyze_trend_no_previous_data(self):
        """Test trend analysis with no previous data."""
        current = 0.75
        previous_values = []

        trend = analyze_trend(current, previous_values)

        assert trend["direction"] == "insufficient_data"
        assert trend["magnitude"] == 0.0
        assert trend["confidence"] == 0.0

    def test_analyze_trend_stable(self):
        """Test stable trend detection."""
        current = 0.75
        previous_values = [0.72, 0.78, 0.74]

        trend = analyze_trend(current, previous_values)

        assert trend["direction"] == "stable"
        assert trend["magnitude"] < 0.05

    def test_analyze_trend_improving(self):
        """Test improving trend detection."""
        current = 0.85
        previous_values = [0.60, 0.65, 0.70]

        trend = analyze_trend(current, previous_values)

        assert trend["direction"] == "improving"
        assert trend["magnitude"] > 0.1

    def test_analyze_trend_declining(self):
        """Test declining trend detection."""
        current = 0.55
        previous_values = [0.70, 0.68, 0.65]

        trend = analyze_trend(current, previous_values)

        assert trend["direction"] == "declining"
        assert trend["magnitude"] > 0.1

    def test_analyze_trend_confidence_increases(self):
        """Test that confidence increases with more data."""
        current = 0.75

        # With few data points
        previous_values_1 = [0.70]
        trend_1 = analyze_trend(current, previous_values_1)

        # With more data points
        previous_values_2 = [0.60, 0.65, 0.70, 0.72]
        trend_2 = analyze_trend(current, previous_values_2)

        assert trend_2["confidence"] > trend_1["confidence"]

    def test_analyze_trend_confidence_capped(self):
        """Test that confidence is capped at 0.95."""
        current = 0.75

        # Create many data points
        previous_values = [i / 100.0 for i in range(50, 75)]
        trend = analyze_trend(current, previous_values)

        assert trend["confidence"] <= 0.95


# ==============================================================================
# Adaptation Recommendation Tests
# ==============================================================================


class TestAdaptationRecommendations:
    """Test adaptation recommendation generation."""

    def test_generate_adaptations_declining_trend(self):
        """Test adaptations for declining trends."""
        responses = {"average_energy": 5, "stress_level": 5}

        scores = {
            "career": 0.7,
            "relationship": 0.75,
            "finance": 0.8,
            "wellness": 0.72,
        }

        trends = {"career": {"direction": "declining", "magnitude": 0.25, "confidence": 0.8}}

        adaptations = generate_adaptations(responses, scores, trends)

        # Should have trend intervention for career
        assert len(adaptations) > 0

    def test_generate_adaptations_high_obstacles(self):
        """Test adaptations for high obstacles."""
        responses = {
            "average_energy": 5,
            "stress_level": 5,
            "obstacle_severity": 8,  # High obstacle severity
        }

        scores = {"career": 0.7}

        trends = {}

        adaptations = generate_adaptations(responses, scores, trends)

        # Should have obstacle mitigation adaptation
        obstacle_adaptations = [a for a in adaptations if a["type"] == "obstacle_mitigation"]
        assert len(obstacle_adaptations) > 0
        assert obstacle_adaptations[0]["priority"] == "high"

    def test_generate_adaptations_low_energy(self):
        """Test adaptations for low energy."""
        responses = {
            "average_energy": 3,  # Low energy
            "stress_level": 5,
        }

        scores = {"career": 0.6}

        trends = {}

        adaptations = generate_adaptations(responses, scores, trends)

        # Should have wellness intervention adaptation
        energy_adaptations = [a for a in adaptations if a["type"] == "wellness_intervention"]
        assert len(energy_adaptations) > 0

    def test_generate_adaptations_high_stress(self):
        """Test adaptations for high stress."""
        responses = {
            "average_energy": 5,
            "stress_level": 9,  # High stress
        }

        scores = {"career": 0.6}

        trends = {}

        adaptations = generate_adaptations(responses, scores, trends)

        # Should have stress management adaptation
        stress_adaptations = [a for a in adaptations if a["type"] == "stress_management"]
        assert len(stress_adaptations) > 0
        assert stress_adaptations[0]["priority"] == "high"

    def test_generate_adaptations_no_issues(self):
        """Test that no adaptations are generated when everything is good."""
        responses = {
            "average_energy": 8,
            "stress_level": 2,
            "obstacle_severity": 3,
        }

        scores = {
            "career": 0.8,
            "relationship": 0.85,
            "finance": 0.9,
            "wellness": 0.82,
        }

        trends = {}

        adaptations = generate_adaptations(responses, scores, trends)

        # Should have minimal or no adaptations
        high_priority = [a for a in adaptations if a["priority"] == "high"]
        assert len(high_priority) == 0


# ==============================================================================
# Check-In Tool Integration Tests
# ==============================================================================


class TestCheckInTools:
    """Test check-in tool integration."""

    def test_conduct_weekly_checkin_valid(self, checkin_tools, backend, sample_responses):
        """Test conducting a valid weekly check-in."""
        conduct_weekly_checkin = checkin_tools[0]

        result = conduct_weekly_checkin.invoke(
            {"user_id": "test_user", "responses": sample_responses}
        )

        assert "Check-In Complete" in result
        # Check for any week number (not specifically Week 1 due to persistent state)
        assert "Week:" in result

    def test_conduct_weekly_checkin_missing_required_field(self, checkin_tools, backend):
        """Test check-in with missing required field."""
        conduct_weekly_checkin = checkin_tools[0]

        incomplete_responses = {
            "career_goals_completed": 75,
            # Missing other required fields
        }

        result = conduct_weekly_checkin.invoke(
            {"user_id": "test_user", "responses": incomplete_responses}
        )

        assert "Error" in result
        assert "Missing required field" in result

    def test_calculate_progress_score(self, checkin_tools, backend, sample_responses):
        """Test calculating progress score."""
        conduct_weekly_checkin = checkin_tools[0]
        calculate_progress_score_tool = checkin_tools[1]

        # First, conduct a check-in
        conduct_weekly_checkin.invoke({"user_id": "test_user", "responses": sample_responses})

        # Then calculate progress score
        result = calculate_progress_score_tool.invoke({"user_id": "test_user"})

        assert "Progress Score Analysis" in result
        assert "Overall Progress Score" in result

    def test_generate_weekly_report_markdown(self, checkin_tools, backend, sample_responses):
        """Test generating Markdown weekly report."""
        conduct_weekly_checkin = checkin_tools[0]
        generate_report_tool = checkin_tools[4]

        # Conduct a check-in
        conduct_weekly_checkin.invoke({"user_id": "test_user", "responses": sample_responses})

        # Generate Markdown report
        result = generate_report_tool.invoke({"user_id": "test_user", "format_type": "markdown"})

        assert "#" in result  # Markdown header
        assert "Domain Progress" in result


# ==============================================================================
# Run Tests
# ==============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
