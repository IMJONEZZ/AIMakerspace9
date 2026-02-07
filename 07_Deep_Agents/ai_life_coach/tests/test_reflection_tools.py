"""
Test suite for Reflection Prompt Tools.

Tests cover:
- Dynamic prompt selection based on context
- Milestone and setback trigger prompts
- Reflection saving with sentiment analysis
- Historical reflection retrieval
- Insights extraction from multiple reflections
"""

import json
from datetime import date, timedelta
from pathlib import Path
import tempfile
import shutil

import pytest


# Import reflection tools
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tools.reflection_tools import (
    create_reflection_tools,
    REFLECTION_PROMPT_LIBRARY,
    MILESTONE_PROMPTS,
    SETBACK_PROMPTS,
    select_prompts_by_context,
    trigger_milestone_prompts,
    trigger_setback_prompts,
    analyze_reflection_sentiment,
    extract_insights_from_history,
)


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace directory for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    # Cleanup
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


@pytest.fixture
def mock_backend(temp_workspace):
    """Create a simple mock backend for testing."""

    class MockBackend:
        def __init__(self, root_dir):
            self.root_dir = str(root_dir)

        def write_file(self, path: str, content: str):
            file_path = Path(self.root_dir) / path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)

        def read_file(self, path: str) -> str:
            file_path = Path(self.root_dir) / path
            return file_path.read_text()

    backend = MockBackend(temp_workspace)
    # Override get_backend to use our mock
    import tools.reflection_tools as rt_module

    original_get_backend = rt_module.get_backend

    def mock_get_backend():
        return backend

    rt_module.get_backend = mock_get_backend
    yield backend
    # Restore original
    rt_module.get_backend = original_get_backend


@pytest.fixture
def reflection_tools(mock_backend):
    """Create reflection tools with mock backend."""
    return create_reflection_tools(backend=mock_backend)


# ==============================================================================
# Unit Tests: Prompt Library
# ==============================================================================


def test_reflection_prompt_library_structure():
    """Test that the reflection prompt library is properly structured."""
    assert isinstance(REFLECTION_PROMPT_LIBRARY, dict)
    assert set(REFLECTION_PROMPT_LIBRARY.keys()) == {
        "celebration",
        "challenge",
        "learning",
        "planning",
    }

    # Check each category has prompts
    for category, prompts in REFLECTION_PROMPT_LIBRARY.items():
        assert isinstance(prompts, list)
        assert len(prompts) >= 10, f"Category {category} should have at least 10 prompts"

        # Check each prompt has required fields
        for prompt in prompts:
            assert "id" in prompt
            assert "prompt" in prompt
            assert "theme" in prompt
            assert "depth" in prompt


def test_milestone_prompts_structure():
    """Test that milestone prompts are properly structured."""
    assert isinstance(MILESTONE_PROMPTS, dict)
    assert set(MILESTONE_PROMPTS.keys()) == {
        "goal_achieved",
        "major_breakthrough",
        "streak_completed",
    }

    for milestone_type, prompts in MILESTONE_PROMPTS.items():
        assert isinstance(prompts, list)
        assert len(prompts) >= 3
        for prompt in prompts:
            assert isinstance(prompt, str)
            assert len(prompt) > 10


def test_setback_prompts_structure():
    """Test that setback prompts are properly structured."""
    assert isinstance(SETBACK_PROMPTS, dict)
    assert set(SETBACK_PROMPTS.keys()) == {"setback_occurred", "pattern_recurring"}

    for setback_type, prompts in SETBACK_PROMPTS.items():
        assert isinstance(prompts, list)
        assert len(prompts) >= 3
        for prompt in prompts:
            assert isinstance(prompt, str)
            assert len(prompt) > 10


# ==============================================================================
# Unit Tests: Dynamic Prompt Selection
# ==============================================================================


def test_select_prompts_by_context_basic():
    """Test basic prompt selection with minimal context."""
    selected = select_prompts_by_context()

    # Should return prompts for all categories
    assert set(selected.keys()) == {"celebration", "challenge", "learning", "planning"}

    # Each category should have some prompts
    for category, prompts in selected.items():
        assert len(prompts) > 0


def test_select_prompts_with_high_mood_and_progress():
    """Test prompt selection when mood is high and progress is good."""
    selected = select_prompts_by_context(
        mood_state={"happiness": 8, "stress": 2, "energy": 7, "motivation": 9}, progress_score=0.8
    )

    # Should have more celebration prompts when mood is high
    assert len(selected["celebration"]) >= 2
    assert len(selected["challenge"]) <= 2


def test_select_prompts_with_low_mood_and_progress():
    """Test prompt selection when mood is low and progress is poor."""
    selected = select_prompts_by_context(
        mood_state={"happiness": 3, "stress": 8, "energy": 2, "motivation": 4}, progress_score=0.3
    )

    # Should have more challenge and learning prompts when mood is low
    assert len(selected["challenge"]) >= 2
    # Still should have some celebration prompts for balance
    assert len(selected["celebration"]) >= 1


def test_select_prompts_with_challenges_and_wins():
    """Test prompt selection with specific challenges and wins."""
    selected = select_prompts_by_context(
        challenges=["procrastination", "time management"], wins=["completed project"]
    )

    # Should still return all categories
    assert set(selected.keys()) == {"celebration", "challenge", "learning", "planning"}


# ==============================================================================
# Unit Tests: Milestone and Setback Triggers
# ==============================================================================


def test_trigger_milestone_prompts_goal_achieved():
    """Test milestone prompts for goal achievement."""
    prompts = trigger_milestone_prompts("goal_achieved", {"goal_name": "Learn Python"})

    assert len(prompts) > 0
    assert all(isinstance(p, str) for p in prompts)
    # Should customize with goal name
    assert any("Learn Python" in p for p in prompts)


def test_trigger_milestone_prompts_major_breakthrough():
    """Test milestone prompts for major breakthrough."""
    prompts = trigger_milestone_prompts("major_breakthrough")

    assert len(prompts) > 0
    assert any("breakthrough" in p.lower() or "shifted" in p.lower() for p in prompts)


def test_trigger_milestone_prompts_invalid_type():
    """Test milestone prompts with invalid type."""
    prompts = trigger_milestone_prompts("invalid_type")

    assert prompts == []


def test_trigger_setback_prompts_setback_occurred():
    """Test setback prompts for general setback."""
    prompts = trigger_setback_prompts("setback_occurred", {"challenge_name": "Missed deadline"})

    assert len(prompts) > 0
    assert any("Missed deadline" in p for p in prompts)


def test_trigger_setback_prompts_pattern_recurring():
    """Test setback prompts for recurring pattern."""
    prompts = trigger_setback_prompts("pattern_recurring", {"pattern_name": "Procrastination"})

    assert len(prompts) > 0
    assert any("pattern" in p.lower() for p in prompts)


def test_trigger_setback_prompts_invalid_type():
    """Test setback prompts with invalid type."""
    prompts = trigger_setback_prompts("invalid_type")

    assert prompts == []


# ==============================================================================
# Unit Tests: Sentiment Analysis
# ==============================================================================


def test_analyze_reflection_sentiment_growth_positive():
    """Test sentiment analysis of growth-positive reflection."""
    text = "I learned so much about myself this week. I grew stronger and more capable through the challenges."

    result = analyze_reflection_sentiment(text)

    assert "sentiment" in result
    assert "confidence" in result
    assert result["growth_indicators"] > 0


def test_analyze_reflection_sentiment_challenging():
    """Test sentiment analysis of challenging reflection."""
    text = (
        "This week was really difficult and hard. I struggled with obstacles and felt overwhelmed."
    )

    result = analyze_reflection_sentiment(text)

    assert "sentiment" in result
    assert result["challenge_indicators"] > 0


def test_analyze_reflection_sentiment_neutral():
    """Test sentiment analysis of neutral reflection."""
    text = "I did several things this week. Some went well and others didn't."

    result = analyze_reflection_sentiment(text)

    assert "sentiment" in result
    # Should have low confidence for neutral text


def test_analyze_reflection_sentiment_empty():
    """Test sentiment analysis with empty input."""
    result = analyze_reflection_sentiment("")

    assert result["sentiment"] == "neutral"
    assert result["confidence"] == 0.0


def test_analyze_reflection_sentiment_growth_through_challenge():
    """Test sentiment analysis of reflection with both growth and challenge."""
    text = "It was a difficult week, but I learned so much from the challenges. I grew stronger and more resilient."

    result = analyze_reflection_sentiment(text)

    assert result["growth_indicators"] > 0
    assert result["challenge_indicators"] > 0


# ==============================================================================
# Unit Tests: Insights Extraction
# ==============================================================================


def test_extract_insights_from_history_empty():
    """Test insights extraction with no reflections."""
    insights = extract_insights_from_history([])

    assert insights["total_reflections"] == 0
    assert insights["recurring_themes"] == []
    assert insights["growth_trajectory"] is None


def test_extract_insights_from_history_single():
    """Test insights extraction with one reflection."""
    reflections = [
        {
            "themes": ["growth", "career"],
            "sentiment_analysis": {"sentiment": "growth_positive"},
        }
    ]

    insights = extract_insights_from_history(reflections)

    assert insights["total_reflections"] == 1
    assert len(insights["recurring_themes"]) > 0
    # Should be insufficient for trajectory analysis
    assert insights["growth_trajectory"] == "insufficient_data"


def test_extract_insights_from_history_multiple():
    """Test insights extraction with multiple reflections."""
    reflections = [
        {
            "themes": ["growth", "career"],
            "sentiment_analysis": {"sentiment": "growth_positive"},
        },
        {
            "themes": ["relationships", "wellness"],
            "sentiment_analysis": {"sentiment": "growth_positive"},
        },
        {
            "themes": ["growth", "resilience"],
            "sentiment_analysis": {"sentiment": "challenging"},
        },
    ]

    insights = extract_insights_from_history(reflections)

    assert insights["total_reflections"] == 3
    assert len(insights["recurring_themes"]) > 0
    # Should have a trajectory analysis
    assert insights["growth_trajectory"] is not None


def test_extract_insights_recurring_themes():
    """Test that recurring themes are correctly identified."""
    reflections = [
        {"themes": ["growth", "career"], "sentiment_analysis": {}},
        {"themes": ["growth", "wellness"], "sentiment_analysis": {}},
        {"themes": ["career", "relationships"], "sentiment_analysis": {}},
    ]

    insights = extract_insights_from_history(reflections)

    # Growth should appear twice
    growth_theme = [t for t in insights["recurring_themes"] if t["theme"] == "growth"]
    assert len(growth_theme) > 0
    assert growth_theme[0]["occurrences"] >= 2


# ==============================================================================
# Integration Tests: Tool Functions
# ==============================================================================


def test_generate_weekly_reflection_prompts(reflection_tools):
    """Test generate_weekly_reflection_prompts tool."""
    (
        generate_prompts,
        _save_response,
        _get_history,
        _extract_insights,
        _trigger_milestone,
        _trigger_setback,
    ) = reflection_tools

    result = generate_prompts.invoke(
        {
            "user_id": "test_user",
            "mood_state": {"happiness": 7, "stress": 3},
            "progress_score": 0.75,
        }
    )

    assert isinstance(result, str)
    assert "Weekly Reflection Prompts" in result
    assert "Celebration" in result
    assert "Challenge" in result
    assert "Learning" in result
    assert "Planning" in result


def test_generate_weekly_reflection_prompts_with_challenges(reflection_tools):
    """Test generate prompts with specific challenges."""
    (
        generate_prompts,
        _save_response,
        _get_history,
        _extract_insights,
        _trigger_milestone,
        _trigger_setback,
    ) = reflection_tools

    result = generate_prompts(
        user_id="test_user",
        mood_state={"happiness": 4, "stress": 7},
        progress_score=0.35,
        challenges=["procrastination", "time management"],
    )

    assert isinstance(result, str)
    assert "Context Used for Selection" in result


def test_save_reflection_response(reflection_tools, mock_backend):
    """Test save_reflection_response tool."""
    (
        _generate_prompts,
        save_response,
        _get_history,
        _extract_insights,
        _trigger_milestone,
        _trigger_setback,
    ) = reflection_tools

    result = save_response(
        user_id="test_user",
        prompt_category="celebration",
        prompt_text="What achievement are you proud of?",
        response_text="I completed my project ahead of schedule and learned a lot about time management.",
    )

    assert isinstance(result, str)
    assert "Reflection Saved" in result
    assert "Sentiment Analysis" in result

    # Verify file was created
    reflections_dir = Path(mock_backend.root_dir) / "reflections" / "test_user"
    assert reflections_dir.exists()
    reflection_files = list(reflections_dir.glob("reflection_*.json"))
    assert len(reflection_files) > 0


def test_save_reflection_response_with_themes(reflection_tools):
    """Test that themes are correctly extracted from reflections."""
    (
        _generate_prompts,
        save_response,
        _get_history,
        _extract_insights,
        _trigger_milestone,
        _trigger_setback,
    ) = reflection_tools

    result = save_response(
        user_id="test_user",
        prompt_category="learning",
        prompt_text="What did you learn?",
        response_text="I learned a lot about my career and developed new skills for professional growth.",
    )

    assert isinstance(result, str)
    # Should detect career-related themes
    assert "Themes Identified" in result


def test_get_reflection_history(reflection_tools, mock_backend):
    """Test get_reflection_history tool."""
    (
        _generate_prompts,
        save_response,
        get_history,
        _extract_insights,
        _trigger_milestone,
        _trigger_setback,
    ) = reflection_tools

    # First, save some reflections
    save_response(
        user_id="test_user",
        prompt_category="celebration",
        prompt_text="Prompt 1",
        response_text="Response 1 with growth and learning.",
    )

    save_response(
        user_id="test_user",
        prompt_category="challenge",
        prompt_text="Prompt 2",
        response_text="Response 2 with difficult challenges.",
    )

    # Now get history
    result = get_history(user_id="test_user", days=30)

    assert isinstance(result, str)
    assert "Reflection History" in result
    # Should show both saved reflections
    assert "Celebration" in result
    assert "Challenge" in result


def test_get_reflection_history_with_category_filter(reflection_tools):
    """Test get_reflection_history with category filter."""
    (
        _generate_prompts,
        save_response,
        get_history,
        _extract_insights,
        _trigger_milestone,
        _trigger_setback,
    ) = reflection_tools

    # Save reflections in different categories
    save_response(
        user_id="test_user",
        prompt_category="celebration",
        prompt_text="Prompt 1",
        response_text="Response 1.",
    )

    save_response(
        user_id="test_user",
        prompt_category="learning",
        prompt_text="Prompt 2",
        response_text="Response 2.",
    )

    # Get history filtered to one category
    result = get_history(user_id="test_user", days=30, category_filter="celebration")

    assert isinstance(result, str)
    assert "Filtered by category: celebration" in result


def test_extract_insights_from_reflections_tool(reflection_tools):
    """Test extract_insights_from_reflections tool."""
    (
        _generate_prompts,
        save_response,
        get_history,
        extract_insights,
        _trigger_milestone,
        _trigger_setback,
    ) = reflection_tools

    # Save multiple reflections
    for i in range(5):
        save_response(
            user_id="test_user",
            prompt_category="learning" if i % 2 == 0 else "challenge",
            prompt_text=f"Prompt {i}",
            response_text=f"I learned about growth and career development in reflection {i}.",
        )

    # Extract insights
    result = extract_insights(user_id="test_user", days=30)

    assert isinstance(result, str)
    assert "Reflection Insights" in result
    assert "Recurring Themes" in result
    assert "Emotional Patterns" in result


def test_trigger_milestone_reflection_tool(reflection_tools):
    """Test trigger_milestone_reflection tool."""
    (
        _generate_prompts,
        save_response,
        get_history,
        extract_insights,
        trigger_milestone,
        _trigger_setback,
    ) = reflection_tools

    result = trigger_milestone.invoke({
        user_id="test_user", milestone_type="goal_achieved", context={"goal_name": "Learn Python"}
    )

    assert isinstance(result, str)
    assert "Milestone Reflection" in result
    assert "Learn Python" in result


def test_trigger_milestone_reflection_invalid_type(reflection_tools):
    """Test trigger_milestone_reflection with invalid type."""
    (
        _generate_prompts,
        save_response,
        get_history,
        extract_insights,
        trigger_milestone,
        _trigger_setback,
    ) = reflection_tools

    result = trigger_milestone.invoke({user_id="test_user", milestone_type="invalid_type")

    assert isinstance(result, str)
    assert "Error" in result


def test_trigger_setback_reflection_tool(reflection_tools):
    """Test trigger_setback_reflection tool."""
    (
        _generate_prompts,
        save_response,
        get_history,
        extract_insights,
        _trigger_milestone,
        trigger_setback,
    ) = reflection_tools

    result = trigger_setback.invoke({
        user_id="test_user",
        setback_type="setback_occurred",
        context={"challenge_name": "Missed deadline"},
    )

    assert isinstance(result, str)
    assert "Setback Reflection" in result
    assert "Missed deadline" in result


def test_trigger_setback_reflection_invalid_type(reflection_tools):
    """Test trigger_setback_reflection with invalid type."""
    (
        _generate_prompts,
        save_response,
        get_history,
        extract_insights,
        _trigger_milestone,
        trigger_setback,
    ) = reflection_tools

    result = trigger_setback.invoke({user_id="test_user", setback_type="invalid_type")

    assert isinstance(result, str)
    assert "Error" in result


# ==============================================================================
# Edge Cases and Error Handling
# ==============================================================================


def test_generate_prompts_invalid_user_id(reflection_tools):
    """Test generate prompts with invalid user ID."""
    (
        generate_prompts,
        _save_response,
        _get_history,
        _extract_insights,
        _trigger_milestone,
        _trigger_setback,
    ) = reflection_tools

    result = generate_prompts(user_id="", mood_state={"happiness": 7})

    assert isinstance(result, str)
    assert "Error" in result


def test_save_response_invalid_user_id(reflection_tools):
    """Test save response with invalid user ID."""
    (
        _generate_prompts,
        save_response,
        _get_history,
        _extract_insights,
        _trigger_milestone,
        _trigger_setback,
    ) = reflection_tools

    result = save_response(
        user_id="", prompt_category="celebration", prompt_text="Test", response_text="Test"
    )

    assert isinstance(result, str)
    assert "Error" in result


def test_save_response_empty_response(reflection_tools):
    """Test save response with empty reflection text."""
    (
        _generate_prompts,
        save_response,
        _get_history,
        _extract_insights,
        _trigger_milestone,
        _trigger_setback,
    ) = reflection_tools

    result = save_response(
        user_id="test_user", prompt_category="celebration", prompt_text="Test", response_text=""
    )

    assert isinstance(result, str)
    assert "Error" in result


def test_get_history_no_reflections(reflection_tools):
    """Test get history when no reflections exist."""
    (
        _generate_prompts,
        save_response,
        get_history,
        _extract_insights,
        _trigger_milestone,
        _trigger_setback,
    ) = reflection_tools

    result = get_history(user_id="nonexistent_user", days=30)

    assert isinstance(result, str)
    assert "No reflection entries found" in result


def test_extract_insights_insufficient_reflections(reflection_tools):
    """Test extract insights with insufficient reflections."""
    (
        _generate_prompts,
        save_response,
        get_history,
        extract_insights,
        _trigger_milestone,
        _trigger_setback,
    ) = reflection_tools

    # Save only one reflection
    save_response(
        user_id="test_user",
        prompt_category="celebration",
        prompt_text="Test",
        response_text="Test reflection",
    )

    result = extract_insights(user_id="test_user", days=30)

    assert isinstance(result, str)
    # Should indicate insufficient data
    assert "at least 2" in result.lower() or "insufficient" in result.lower()


# ==============================================================================
# Run Tests
# ==============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
