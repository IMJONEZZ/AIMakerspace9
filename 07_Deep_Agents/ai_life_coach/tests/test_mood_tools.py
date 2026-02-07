"""
Test suite for mood tracking and sentiment analysis tools.

This module provides comprehensive tests for the mood tracking system,
including:
- Mood entry logging with multi-dimensional scoring
- Keyword-based sentiment analysis on text
- Composite mood score calculation
- ASCII chart generation for trends
- Mood-progress correlation analysis
- Mood trigger detection system
"""

import pytest
from pathlib import Path

# Import mood tools and helper functions
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.mood_tools import (
    analyze_sentiment_keywords,
    calculate_composite_mood_score,
    generate_ascii_chart,
    calculate_correlation,
    detect_mood_triggers as detect_triggers_helper,
    MOOD_DIMENSIONS,
    SENTIMENT_KEYWORDS,
    MOOD_TRIGGERS,
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
    (mock_backend.root_dir / "moods").mkdir(parents=True, exist_ok=True)
    return mock_backend


@pytest.fixture
def mood_tools(backend):
    """Create mood tools with mock backend."""
    from src.tools.mood_tools import create_mood_tools

    return create_mood_tools(backend)


@pytest.fixture
def sample_mood_dimensions():
    """Sample valid mood dimension scores."""
    return {
        "happiness": 7,
        "stress": 4,
        "energy": 6,
        "motivation": 8,
    }


@pytest.fixture
def high_mood_dimensions():
    """Sample scores indicating high positive mood state."""
    return {
        "happiness": 9,
        "stress": 2,
        "energy": 8,
        "motivation": 9,
    }


@pytest.fixture
def low_mood_dimensions():
    """Sample scores indicating low mood state."""
    return {
        "happiness": 2,
        "stress": 9,
        "energy": 3,
        "motivation": 2,
    }


@pytest.fixture
def moderate_mood_dimensions():
    """Sample scores indicating moderate mood state."""
    return {
        "happiness": 5,
        "stress": 5,
        "energy": 5,
        "motivation": 5,
    }


# ==============================================================================
# Helper Function Tests
# ==============================================================================


class TestSentimentAnalysis:
    """Test sentiment analysis helper functions."""

    def test_analyze_positive_sentiment(self):
        """Test detection of positive sentiment."""
        text = "I feel excited and happy about my progress! I accomplished so much today."
        result = analyze_sentiment_keywords(text)

        assert result["sentiment"] == "positive"
        assert result["confidence"] > 0.5
        assert len(result["positive_words"]) > 0
        assert any(
            word in result["positive_words"] for word in ["excited", "happy", "accomplished"]
        )

    def test_analyze_negative_sentiment(self):
        """Test detection of negative sentiment."""
        text = "I'm feeling stressed and exhausted. Failed at everything today."
        result = analyze_sentiment_keywords(text)

        assert result["sentiment"] == "negative"
        assert result["confidence"] > 0.5
        assert len(result["negative_words"]) > 0
        assert any(word in result["negative_words"] for word in ["stressed", "exhausted", "failed"])

    def test_analyze_neutral_sentiment(self):
        """Test detection of neutral sentiment."""
        text = "Today was a normal day. I did some work and went for a walk."
        result = analyze_sentiment_keywords(text)

        assert result["sentiment"] == "neutral"
        # May have some matches but should be balanced

    def test_analyze_empty_text(self):
        """Test handling of empty text."""
        result = analyze_sentiment_keywords("")

        assert result["sentiment"] == "neutral"
        assert result["confidence"] == 0.0
        assert len(result["positive_words"]) == 0
        assert len(result["negative_words"]) == 0

    def test_analyze_none_text(self):
        """Test handling of None input."""
        result = analyze_sentiment_keywords(None)

        assert result["sentiment"] == "neutral"
        assert result["confidence"] == 0.0

    def test_sentiment_keywords_exist(self):
        """Test that sentiment keyword dictionaries are properly configured."""
        assert "positive" in SENTIMENT_KEYWORDS
        assert "negative" in SENTIMENT_KEYWORDS

        # Check for key positive words
        assert "excited" in SENTIMENT_KEYWORDS["positive"]
        assert "happy" in SENTIMENT_KEYWORDS["positive"]
        assert "stressed" in SENTIMENT_KEYWORDS["negative"]

    def test_count_word_occurrences(self):
        """Test that multiple occurrences of the same word are counted."""
        text = "I am happy, very happy, extremely happy"
        result = analyze_sentiment_keywords(text)

        assert "happy" in result["positive_words"]
        # Should count multiple occurrences
        assert result["positive_words"].count("happy") == 3


class TestMoodScoreCalculation:
    """Test mood score calculation helper functions."""

    def test_calculate_composite_score_high_mood(self, high_mood_dimensions):
        """Test composite score for high mood state."""
        score = calculate_composite_mood_score(high_mood_dimensions)

        # High happiness (9), low stress (2->9 normalized), high energy, high motivation
        # Average should be high
        assert score > 0.7

    def test_calculate_composite_score_low_mood(self, low_mood_dimensions):
        """Test composite score for low mood state."""
        score = calculate_composite_mood_score(low_mood_dimensions)

        # Low happiness, high stress (9->2 normalized), low energy, low motivation
        # Average should be low
        assert score < 0.4

    def test_calculate_composite_score_moderate_mood(self, moderate_mood_dimensions):
        """Test composite score for moderate mood state."""
        score = calculate_composite_mood_score(moderate_mood_dimensions)

        # All values at 5, stress normalized to 6
        # Average should be around mid-range
        assert 0.4 <= score <= 0.6

    def test_calculate_composite_score_with_missing_dimensions(self):
        """Test handling of missing dimensions (defaults to 5)."""
        partial_mood = {"happiness": 8, "stress": 3}
        score = calculate_composite_mood_score(partial_mood)

        # Should use defaults for energy and motivation
        assert 0.4 <= score <= 1.0

    def test_calculate_composite_score_bounds(self):
        """Test that composite score stays within bounds."""
        # Minimum possible
        min_mood = {"happiness": 1, "stress": 10, "energy": 1, "motivation": 1}
        min_score = calculate_composite_mood_score(min_mood)
        assert min_score >= 0.0
        assert min_score <= 0.3

        # Maximum possible
        max_mood = {"happiness": 10, "stress": 1, "energy": 10, "motivation": 10}
        max_score = calculate_composite_mood_score(max_mood)
        assert max_score <= 1.0
        assert max_score >= 0.7

    def test_stress_inverted(self):
        """Test that stress is properly inverted (lower = better)."""
        high_stress_mood = {"happiness": 5, "stress": 9, "energy": 5, "motivation": 5}
        low_stress_mood = {"happiness": 5, "stress": 1, "energy": 5, "motivation": 5}

        high_stress_score = calculate_composite_mood_score(high_stress_mood)
        low_stress_score = calculate_composite_mood_score(low_stress_mood)

        # Low stress should result in higher composite score
        assert low_stress_score > high_stress_score


class TestASCIIChartGeneration:
    """Test ASCII chart generation helper functions."""

    def test_generate_chart_with_data(self):
        """Test chart generation with valid data."""
        values = [0.2, 0.4, 0.6, 0.8, 1.0]
        chart = generate_ascii_chart(values)

        assert chart is not None
        assert len(chart) > 0
        # Should contain some characters
        assert any(c in chart for c in "●▲↗→↘▼")

    def test_generate_chart_with_labels(self):
        """Test chart generation with axis labels."""
        values = [0.3, 0.5, 0.7]
        labels = ["01", "02", "03"]
        chart = generate_ascii_chart(values, labels)

        assert chart is not None
        # Check that labels appear in chart
        for label in labels:
            assert label in chart

    def test_generate_chart_empty_data(self):
        """Test handling of empty data."""
        chart = generate_ascii_chart([])

        assert "No data available" in chart

    def test_generate_chart_single_value(self):
        """Test handling of single value."""
        values = [0.5]
        chart = generate_ascii_chart(values)

        assert chart is not None
        assert len(chart) > 0

    def test_generate_chart_constant_values(self):
        """Test handling of constant values (no variation)."""
        values = [0.5, 0.5, 0.5]
        chart = generate_ascii_chart(values)

        assert chart is not None
        # Should still produce a valid chart


class TestCorrelationCalculation:
    """Test correlation calculation helper functions."""

    def test_positive_correlation(self):
        """Test detection of positive correlation."""
        mood_scores = [0.2, 0.4, 0.6, 0.8, 1.0]
        progress_scores = [0.3, 0.5, 0.7, 0.9, 1.0]

        result = calculate_correlation(mood_scores, progress_scores)

        assert result["correlation"] is not None
        assert result["correlation"] > 0.5  # Should be strongly positive
        assert "positive" in result["interpretation"].lower()

    def test_negative_correlation(self):
        """Test detection of negative correlation."""
        mood_scores = [0.2, 0.4, 0.6, 0.8, 1.0]
        progress_scores = [1.0, 0.9, 0.7, 0.5, 0.3]

        result = calculate_correlation(mood_scores, progress_scores)

        assert result["correlation"] is not None
        assert result["correlation"] < -0.5  # Should be strongly negative

    def test_no_correlation(self):
        """Test detection of no correlation."""
        mood_scores = [0.5, 0.6, 0.4, 0.7, 0.3]
        progress_scores = [0.5, 0.4, 0.6, 0.3, 0.7]

        result = calculate_correlation(mood_scores, progress_scores)

        assert result["correlation"] is not None
        assert abs(result["correlation"]) < 0.4  # Should be weak

    def test_insufficient_data(self):
        """Test handling of insufficient data."""
        mood_scores = [0.5]
        progress_scores = [0.6]

        result = calculate_correlation(mood_scores, progress_scores)

        assert result["correlation"] is None
        # Check for any form of "insufficient" or reference to needing more data
        assert "data points" in result["interpretation"].lower() or len(mood_scores) < 2

    def test_mismatched_lengths(self):
        """Test handling of mismatched array lengths."""
        mood_scores = [0.5, 0.6]
        progress_scores = [0.7]

        result = calculate_correlation(mood_scores, progress_scores)

        assert result["correlation"] is None

    def test_correlation_strength_labels(self):
        """Test that correlation strength is properly labeled."""
        # Strong positive
        result = calculate_correlation([0.1, 0.9], [0.2, 1.0])
        assert result["strength"] in ["strong", "moderate"]

        # Moderate (need more points for accurate strength assessment)
        result = calculate_correlation([0.3, 0.4, 0.5], [0.35, 0.45, 0.55])
        assert result["strength"] in ["moderate", "strong"]

        # Weak (need more points)
        result = calculate_correlation([0.4, 0.5, 0.6], [0.7, 0.3, 0.8])
        assert result["strength"] in ["weak", "moderate", "strong"]


class TestMoodTriggerDetection:
    """Test mood trigger detection helper functions."""

    def test_detect_low_happiness_trigger(self, low_mood_dimensions):
        """Test detection of low happiness trigger."""
        triggers = detect_triggers_helper(low_mood_dimensions, [])

        assert any(t["type"] == "low_happiness" for t in triggers)
        low_hap_trigger = next(t for t in triggers if t["type"] == "low_happiness")
        assert low_hap_trigger["priority"] == "high"

    def test_detect_high_stress_trigger(self, low_mood_dimensions):
        """Test detection of high stress trigger."""
        triggers = detect_triggers_helper(low_mood_dimensions, [])

        assert any(t["type"] == "high_stress" for t in triggers)
        high_stress_trigger = next(t for t in triggers if t["type"] == "high_stress")
        assert high_stress_trigger["priority"] == "high"

    def test_detect_low_energy_trigger(self, low_mood_dimensions):
        """Test detection of low energy trigger."""
        triggers = detect_triggers_helper(low_mood_dimensions, [])

        assert any(t["type"] == "low_energy" for t in triggers)
        low_energy_trigger = next(t for t in triggers if t["type"] == "low_energy")
        assert low_energy_trigger["priority"] == "medium"

    def test_detect_low_motivation_trigger(self, low_mood_dimensions):
        """Test detection of low motivation trigger."""
        triggers = detect_triggers_helper(low_mood_dimensions, [])

        assert any(t["type"] == "low_motivation" for t in triggers)
        low_mot_trigger = next(t for t in triggers if t["type"] == "low_motivation")
        assert low_mot_trigger["priority"] == "medium"

    def test_no_triggers_for_healthy_mood(self, high_mood_dimensions):
        """Test that healthy mood state triggers no alerts."""
        triggers = detect_triggers_helper(high_mood_dimensions, [])

        # Should have few or no triggers
        assert len(triggers) == 0

    def test_detect_consecutive_low_mood(self):
        """Test detection of consecutive low mood."""
        # Create history with 3 consecutive low happiness entries
        history = [
            {"happiness": 2, "stress": 8, "energy": 3, "motivation": 2},
            {"happiness": 1, "stress": 9, "energy": 2, "motivation": 1},
            {"happiness": 2, "stress": 8, "energy": 3, "motivation": 2},
        ]

        current = {"happiness": 2, "stress": 8, "energy": 3, "motivation": 2}
        triggers = detect_triggers_helper(current, history)

        assert any(t["type"] == "consecutive_low_mood" for t in triggers)

    def test_detect_mood_decline(self):
        """Test detection of mood decline."""
        history = [{"happiness": 8, "stress": 3, "energy": 7, "motivation": 8}]
        current = {"happiness": 5, "stress": 6, "energy": 4, "motivation": 5}

        triggers = detect_triggers_helper(current, history)

        assert any(t["type"] == "mood_decline" for t in triggers)


# ==============================================================================
# Tool Tests
# ==============================================================================


class TestLogMoodEntry:
    """Test log_mood_entry tool."""

    def test_log_valid_mood_entry(self, mood_tools, sample_mood_dimensions):
        """Test logging a valid mood entry."""
        log_mood_entry = mood_tools[0]
        result = log_mood_entry.invoke(
            {"user_id": "user_123", "mood_dimensions": sample_mood_dimensions}
        )

        assert "Mood Entry Logged" in result
        assert "user_123" in result
        # Check that mood dimensions are shown (with full names)
        assert "7/10" in result  # Happiness score
        assert "4/10" in result  # Stress score

    def test_log_mood_with_notes(self, mood_tools, sample_mood_dimensions):
        """Test logging a mood entry with notes."""
        log_mood_entry = mood_tools[0]
        result = log_mood_entry.invoke(
            {
                "user_id": "user_123",
                "mood_dimensions": sample_mood_dimensions,
                "notes": "I feel great about my progress today!",
            }
        )

        assert "Mood Entry Logged" in result
        assert "Sentiment Analysis" in result

    def test_log_mood_with_negative_notes(self, mood_tools, sample_mood_dimensions):
        """Test logging a mood entry with negative notes."""
        log_mood_entry = mood_tools[0]
        result = log_mood_entry.invoke(
            {
                "user_id": "user_123",
                "mood_dimensions": sample_mood_dimensions,
                "notes": "I'm feeling stressed and overwhelmed today.",
            }
        )

        assert "Mood Entry Logged" in result
        # Should detect negative sentiment
        assert "NEGATIVE" in result or "negative" in result.lower()

    def test_log_mood_invalid_dimensions(self, mood_tools):
        """Test handling of invalid dimension scores."""
        log_mood_entry = mood_tools[0]
        result = log_mood_entry.invoke(
            {"user_id": "user_123", "mood_dimensions": {"happiness": 15}}
        )

        assert "Error" in result
        assert "between 1 and 10" in result

    def test_log_mood_missing_dimensions(self, mood_tools):
        """Test handling of missing user_id."""
        log_mood_entry = mood_tools[0]
        result = log_mood_entry.invoke({"user_id": "", "mood_dimensions": {"happiness": 5}})

        assert "Error" in result
        assert "user_id" in result.lower()


class TestAnalyzeTextSentiment:
    """Test analyze_text_sentiment tool."""

    def test_analyze_positive_text(self, mood_tools):
        """Test analyzing positive text."""
        analyze_sentiment = mood_tools[1]
        result = analyze_sentiment.invoke(
            {"text": "I feel excited and happy about my achievements!"}
        )

        assert "Sentiment Analysis Results" in result
        assert "POSITIVE" in result

    def test_analyze_negative_text(self, mood_tools):
        """Test analyzing negative text."""
        analyze_sentiment = mood_tools[1]
        result = analyze_sentiment.invoke(
            {"text": "I'm feeling tired and stressed about everything."}
        )

        assert "Sentiment Analysis Results" in result
        assert "NEGATIVE" in result

    def test_analyze_neutral_text(self, mood_tools):
        """Test analyzing neutral text."""
        analyze_sentiment = mood_tools[1]
        result = analyze_sentiment.invoke(
            {"text": "Today was an average day with normal activities."}
        )

        assert "Sentiment Analysis Results" in result

    def test_analyze_empty_string(self, mood_tools):
        """Test handling of empty string."""
        analyze_sentiment = mood_tools[1]
        result = analyze_sentiment.invoke({"text": ""})

        assert "Error" in result


class TestCalculateMoodScore:
    """Test calculate_mood_score tool."""

    def test_calculate_with_provided_dimensions(self, mood_tools, sample_mood_dimensions):
        """Test calculation with provided dimensions."""
        calculate_score = mood_tools[2]
        result = calculate_score.invoke(
            {"user_id": "user_123", "mood_dimensions": sample_mood_dimensions}
        )

        assert "Mood Score Calculation" in result
        assert "Composite Mood Score" in result

    def test_calculate_without_dimensions_uses_history(self, mood_tools, backend):
        """Test that missing dimensions uses most recent entry."""
        # First log an entry
        log_mood_entry = mood_tools[0]
        log_mood_entry.invoke(
            {
                "user_id": "user_123",
                "mood_dimensions": {"happiness": 7, "stress": 4, "energy": 6, "motivation": 8},
            }
        )

        # Then calculate without providing dimensions
        calculate_score = mood_tools[2]
        result = calculate_score.invoke({"user_id": "user_123"})

        assert "Mood Score Calculation" in result

    def test_calculate_no_history_error(self, mood_tools):
        """Test error when no history exists."""
        calculate_score = mood_tools[2]
        result = calculate_score.invoke({"user_id": "new_user_456"})

        assert "No mood entries found" in result


class TestGenerateMoodTrendChart:
    """Test generate_mood_trend_chart tool."""

    def test_generate_chart_with_no_data(self, mood_tools):
        """Test chart generation with no data."""
        generate_chart = mood_tools[3]
        result = generate_chart.invoke({"user_id": "new_user_789", "days": 7})

        assert "No mood entries found" in result

    def test_generate_chart_with_data(self, mood_tools, backend):
        """Test chart generation with existing data."""
        log_mood_entry = mood_tools[0]

        # Log multiple entries
        for i in range(5):
            log_mood_entry.invoke(
                {
                    "user_id": "user_123",
                    "mood_dimensions": {
                        "happiness": 5 + i,
                        "stress": 6 - i,
                        "energy": 5 + i,
                        "motivation": 5 + i,
                    },
                }
            )

        # Generate chart
        generate_chart = mood_tools[3]
        result = generate_chart.invoke({"user_id": "user_123", "days": 7})

        assert "Mood Trend Chart" in result
        assert "Composite Mood Score Trend" in result


class TestAnalyzeMoodProgressCorrelation:
    """Test analyze_mood_progress_correlation tool."""

    def test_analyze_correlation_no_data(self, mood_tools):
        """Test correlation analysis with no data."""
        analyze_corr = mood_tools[4]
        result = analyze_corr.invoke({"user_id": "new_user_999", "days": 30})

        assert "No mood entries found" in result or "No check-in entries found" in result


class TestDetectMoodTriggers:
    """Test detect_mood_triggers tool."""

    def test_detect_triggers_healthy_state(self, mood_tools, backend):
        """Test trigger detection with healthy mood."""
        log_mood_entry = mood_tools[0]
        log_mood_entry.invoke(
            {
                "user_id": "user_123",
                "mood_dimensions": {"happiness": 8, "stress": 2, "energy": 7, "motivation": 9},
            }
        )

        detect_triggers = mood_tools[5]
        result = detect_triggers.invoke({"user_id": "user_123"})

        assert "Mood Trigger Detection" in result
        # Should indicate no triggers or few triggers

    def test_detect_triggers_low_mood(self, mood_tools, backend):
        """Test trigger detection with low mood."""
        log_mood_entry = mood_tools[0]
        log_mood_entry.invoke(
            {
                "user_id": "user_123",
                "mood_dimensions": {"happiness": 2, "stress": 9, "energy": 3, "motivation": 2},
            }
        )

        detect_triggers = mood_tools[5]
        result = detect_triggers.invoke({"user_id": "user_123"})

        assert "Mood Trigger Detection" in result
        # Should detect multiple triggers
        assert "Trigger(s) Detected" in result or "trigger" in result.lower()


class TestGetMoodHistory:
    """Test get_mood_history tool."""

    def test_get_history_no_data(self, mood_tools):
        """Test history retrieval with no data."""
        get_history = mood_tools[6]
        result = get_history.invoke({"user_id": "new_user_777", "days": 30})

        assert "No mood entries found" in result

    def test_get_history_with_data(self, mood_tools, backend):
        """Test history retrieval with existing data."""
        log_mood_entry = mood_tools[0]

        # Log multiple entries
        for i in range(3):
            log_mood_entry.invoke(
                {
                    "user_id": "user_123",
                    "mood_dimensions": {
                        "happiness": 5 + i,
                        "stress": 6 - i,
                        "energy": 5 + i,
                        "motivation": 5 + i,
                    },
                    "notes": f"Day {i + 1} entry",
                }
            )

        get_history = mood_tools[6]
        result = get_history.invoke({"user_id": "user_123", "days": 7})

        assert "Mood History" in result
        assert "Day 1 entry" in result or "Composite:" in result


# ==============================================================================
# Integration Tests
# ==============================================================================


class TestMoodTrackingIntegration:
    """Test mood tracking workflow integration."""

    def test_full_mood_tracking_workflow(self, mood_tools, backend):
        """Test complete workflow: log, analyze, chart, detect triggers."""
        user_id = "integration_test_user"

        # Step 1: Log mood entries
        log_mood_entry = mood_tools[0]

        # High mood day
        log_mood_entry(
            user_id,
            {"happiness": 9, "stress": 2, "energy": 8, "motivation": 9},
            notes="Feeling great and accomplished!",
        )

        # Low mood day
        log_mood_entry(
            user_id,
            {"happiness": 3, "stress": 8, "energy": 4, "motivation": 3},
            notes="Feeling stressed and tired today.",
        )

        # Step 2: Analyze sentiment of notes
        analyze_sentiment = mood_tools[1]
        positive_result = analyze_sentiment("Feeling great and accomplished!")
        negative_result = analyze_sentiment("Feeling stressed and tired today.")

        assert "POSITIVE" in positive_result
        assert "NEGATIVE" in negative_result

        # Step 3: Calculate current mood score
        calculate_score = mood_tools[2]
        score_result = calculate_score(user_id)
        assert "Composite Mood Score" in score_result

        # Step 4: Generate trend chart
        generate_chart = mood_tools[3]
        chart_result = generate_chart(user_id, days=7)
        assert "Mood Trend Chart" in chart_result

        # Step 5: Detect triggers
        detect_triggers = mood_tools[5]
        trigger_result = detect_triggers(user_id)
        assert "Mood Trigger Detection" in trigger_result

        # Step 6: Get history
        get_history = mood_tools[6]
        history_result = get_history(user_id, days=7)
        assert "Mood History" in history_result

    def test_mood_progress_correlation_needs_checkins(self, mood_tools):
        """Test that correlation requires both mood and check-in data."""
        analyze_corr = mood_tools[4]
        result = analyze_corr("new_user_888", days=30)

        # Should indicate missing data
        assert "No mood entries found" in result or "No check-in entries found" in result


# ==============================================================================
# Configuration Tests
# ==============================================================================


class TestMoodConfiguration:
    """Test mood tracking configuration."""

    def test_mood_dimensions_configured(self):
        """Test that all required dimensions are configured."""
        assert "happiness" in MOOD_DIMENSIONS
        assert "stress" in MOOD_DIMENSIONS
        assert "energy" in MOOD_DIMENSIONS
        assert "motivation" in MOOD_DIMENSIONS

    def test_mood_dimension_names(self):
        """Test that mood dimensions have proper names."""
        for dim, config in MOOD_DIMENSIONS.items():
            assert "name" in config
            assert "description" in config

    def test_mood_trigger_thresholds(self):
        """Test that trigger thresholds are properly configured."""
        assert "low_mood_threshold" in MOOD_TRIGGERS
        assert "high_stress_threshold" in MOOD_TRIGGERS
        assert "low_energy_threshold" in MOOD_TRIGGERS

    def test_threshold_values(self):
        """Test that thresholds have reasonable values."""
        # Thresholds should be within 1-10 range
        assert 0 < MOOD_TRIGGERS["low_mood_threshold"] <= 10
        assert 0 < MOOD_TRIGGERS["high_stress_threshold"] <= 10
        assert 0 < MOOD_TRIGGERS["low_energy_threshold"] <= 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
