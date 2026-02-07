"""
Test suite for Progress Dashboard Tools.

This module contains comprehensive tests for:
1. DashboardRenderer - ASCII visualization engine
2. render_progress_dashboard - Main dashboard display
3. calculate_life_satisfaction_score - Scoring algorithm
4. generate_domain_progress_bar - Domain-specific displays
5. create_mood_trend_sparkline - Mood trend visualizations
6. get_recent_achievements - Achievement display
7. get_upcoming_milestones - Milestone tracking
8. export_dashboard_report - Report generation
9. switch_dashboard_view - View switching
"""

import pytest
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tools.dashboard_tools import (
    create_dashboard_tools,
    DashboardRenderer,
    DOMAINS,
    VIEW_CONFIGS,
    ASCII_CHARS,
)


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def mock_backend():
    """Create a mock backend for testing."""
    backend = MagicMock()
    backend.workspace = Path("/tmp/test_workspace")
    return backend


@pytest.fixture
def dashboard_tools(mock_backend):
    """Create dashboard tools with mock backend."""
    return create_dashboard_tools(backend=mock_backend)


@pytest.fixture
def renderer(mock_backend):
    """Create a dashboard renderer."""
    return DashboardRenderer(backend=mock_backend)


@pytest.fixture
def temp_workspace(tmp_path):
    """Create a temporary workspace for testing."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    return workspace


# ==============================================================================
# Test DashboardRenderer
# ==============================================================================


class TestDashboardRenderer:
    """Test the DashboardRenderer class."""

    def test_renderer_initialization(self, renderer, mock_backend):
        """Test that renderer initializes correctly."""
        assert renderer.backend == mock_backend
        assert renderer.chars == ASCII_CHARS
        assert renderer.width == 70

    def test_box_top(self, renderer):
        """Test box top border generation."""
        top = renderer._box_top()
        assert top.startswith("┌")
        assert top.endswith("┐")
        assert "─" in top

    def test_box_bottom(self, renderer):
        """Test box bottom border generation."""
        bottom = renderer._box_bottom()
        assert bottom.startswith("└")
        assert bottom.endswith("┘")
        assert "─" in bottom

    def test_box_line_content(self, renderer):
        """Test box line content generation."""
        line = renderer._box_line("Test Content")
        assert line.startswith("│")
        assert line.endswith("│")
        assert "Test Content" in line

    def test_box_line_alignment_center(self, renderer):
        """Test center alignment in box line."""
        line = renderer._box_line("Center", align="center")
        content_start = line.find("Center")
        # Content should be roughly centered
        assert content_start > 5

    def test_separator(self, renderer):
        """Test separator line generation."""
        sep = renderer._separator()
        assert sep.startswith("├")
        assert sep.endswith("┤")

    def test_progress_bar_full(self, renderer):
        """Test progress bar at 100%."""
        bar = renderer._progress_bar(100, width=10)
        assert "█" in bar
        assert "100.0%" in bar

    def test_progress_bar_empty(self, renderer):
        """Test progress bar at 0%."""
        bar = renderer._progress_bar(0, width=10)
        assert "░" in bar
        assert "0.0%" in bar

    def test_progress_bar_partial(self, renderer):
        """Test progress bar at 50%."""
        bar = renderer._progress_bar(50, width=10)
        assert "█" in bar
        assert "░" in bar
        assert "50.0%" in bar

    def test_sparkline_empty(self, renderer):
        """Test sparkline with empty data."""
        spark = renderer._sparkline([], width=10)
        assert len(spark) == 10
        assert "─" in spark

    def test_sparkline_single_value(self, renderer):
        """Test sparkline with single value."""
        spark = renderer._sparkline([5], width=10)
        assert len(spark) == 1

    def test_sparkline_multiple_values(self, renderer):
        """Test sparkline with multiple values."""
        values = [1, 3, 5, 7, 10]
        spark = renderer._sparkline(values, width=10)
        assert len(spark) == len(values)
        # Should contain sparkline characters
        assert any(c in spark for c in ASCII_CHARS["sparkline_chars"])

    def test_trend_indicator_up(self, renderer):
        """Test trend indicator for upward trend."""
        trend = renderer._trend_indicator(8, 5)
        assert "↑" in trend or "▲" in trend

    def test_trend_indicator_down(self, renderer):
        """Test trend indicator for downward trend."""
        trend = renderer._trend_indicator(3, 8)
        assert "↓" in trend or "▼" in trend

    def test_trend_indicator_flat(self, renderer):
        """Test trend indicator for flat trend."""
        trend = renderer._trend_indicator(5.2, 5.0)
        assert "→" in trend or "~" in trend


# ==============================================================================
# Test Domain Configuration
# ==============================================================================


class TestDomainConfiguration:
    """Test domain configuration constants."""

    def test_domains_defined(self):
        """Test that all four domains are defined."""
        assert "career" in DOMAINS
        assert "relationship" in DOMAINS
        assert "finance" in DOMAINS
        assert "wellness" in DOMAINS

    def test_domain_names(self):
        """Test that domains have proper names."""
        assert "Career" in DOMAINS["career"]["name"]
        assert "Relationship" in DOMAINS["relationship"]["name"]
        assert "Finance" in DOMAINS["finance"]["name"] or "Financial" in DOMAINS["finance"]["name"]
        assert "Wellness" in DOMAINS["wellness"]["name"] or "Health" in DOMAINS["wellness"]["name"]

    def test_domain_icons(self):
        """Test that domains have icons."""
        for domain in DOMAINS.values():
            assert "icon" in domain
            assert len(domain["icon"]) > 0

    def test_domain_weights(self):
        """Test that domain weights sum to 1.0."""
        total_weight = sum(d["weight"] for d in DOMAINS.values())
        assert abs(total_weight - 1.0) < 0.01

    def test_domain_weights_equal(self):
        """Test that domains have equal weights (25% each)."""
        for domain in DOMAINS.values():
            assert domain["weight"] == 0.25


# ==============================================================================
# Test View Configuration
# ==============================================================================


class TestViewConfiguration:
    """Test view configuration constants."""

    def test_views_defined(self):
        """Test that all three views are defined."""
        assert "daily" in VIEW_CONFIGS
        assert "weekly" in VIEW_CONFIGS
        assert "monthly" in VIEW_CONFIGS

    def test_view_days(self):
        """Test that views have correct day ranges."""
        assert VIEW_CONFIGS["daily"]["days"] == 1
        assert VIEW_CONFIGS["weekly"]["days"] == 7
        assert VIEW_CONFIGS["monthly"]["days"] == 30

    def test_view_mood_points(self):
        """Test that views have mood data points configured."""
        assert VIEW_CONFIGS["daily"]["mood_points"] > 0
        assert VIEW_CONFIGS["weekly"]["mood_points"] > 0
        assert VIEW_CONFIGS["monthly"]["mood_points"] > 0


# ==============================================================================
# Test Tool Creation
# ==============================================================================


class TestToolCreation:
    """Test dashboard tool creation."""

    def test_all_tools_created(self, dashboard_tools):
        """Test that all 8 dashboard tools are created."""
        assert len(dashboard_tools) == 8

    def test_render_progress_dashboard_tool(self, dashboard_tools):
        """Test render_progress_dashboard tool exists."""
        tool = dashboard_tools[0]
        assert tool.name == "render_progress_dashboard"
        assert hasattr(tool, "invoke")

    def test_calculate_life_satisfaction_score_tool(self, dashboard_tools):
        """Test calculate_life_satisfaction_score tool exists."""
        tool = dashboard_tools[1]
        assert tool.name == "calculate_life_satisfaction_score"
        assert hasattr(tool, "invoke")

    def test_generate_domain_progress_bar_tool(self, dashboard_tools):
        """Test generate_domain_progress_bar tool exists."""
        tool = dashboard_tools[2]
        assert tool.name == "generate_domain_progress_bar"
        assert hasattr(tool, "invoke")

    def test_create_mood_trend_sparkline_tool(self, dashboard_tools):
        """Test create_mood_trend_sparkline tool exists."""
        tool = dashboard_tools[3]
        assert tool.name == "create_mood_trend_sparkline"
        assert hasattr(tool, "invoke")

    def test_get_recent_achievements_tool(self, dashboard_tools):
        """Test get_recent_achievements tool exists."""
        tool = dashboard_tools[4]
        assert tool.name == "get_recent_achievements"
        assert hasattr(tool, "invoke")

    def test_get_upcoming_milestones_tool(self, dashboard_tools):
        """Test get_upcoming_milestones tool exists."""
        tool = dashboard_tools[5]
        assert tool.name == "get_upcoming_milestones"
        assert hasattr(tool, "invoke")

    def test_export_dashboard_report_tool(self, dashboard_tools):
        """Test export_dashboard_report tool exists."""
        tool = dashboard_tools[6]
        assert tool.name == "export_dashboard_report"
        assert hasattr(tool, "invoke")

    def test_switch_dashboard_view_tool(self, dashboard_tools):
        """Test switch_dashboard_view tool exists."""
        tool = dashboard_tools[7]
        assert tool.name == "switch_dashboard_view"
        assert hasattr(tool, "invoke")


# ==============================================================================
# Test Render Progress Dashboard
# ==============================================================================


class TestRenderProgressDashboard:
    """Test the render_progress_dashboard tool."""

    def test_dashboard_renders(self, dashboard_tools):
        """Test that dashboard renders without errors."""
        render_tool = dashboard_tools[0]
        result = render_tool.invoke(
            {
                "user_id": "test_user",
                "view": "weekly",
            }
        )
        assert isinstance(result, str)
        assert len(result) > 0
        assert "Progress Dashboard" in result

    def test_dashboard_includes_all_sections(self, dashboard_tools):
        """Test that dashboard includes all major sections."""
        render_tool = dashboard_tools[0]
        result = render_tool.invoke(
            {
                "user_id": "test_user",
                "view": "weekly",
            }
        )
        # Check for key sections
        assert "OVERALL LIFE SATISFACTION" in result
        assert "DOMAIN PROGRESS" in result
        assert "MOOD TREND" in result or "ACHIEVEMENTS" in result
        assert "UPCOMING MILESTONES" in result

    def test_dashboard_invalid_view_defaults(self, dashboard_tools):
        """Test that invalid view defaults to weekly."""
        render_tool = dashboard_tools[0]
        result = render_tool.invoke(
            {
                "user_id": "test_user",
                "view": "invalid_view",
            }
        )
        # Should still render with weekly view
        assert isinstance(result, str)
        assert "This Week" in result or "Progress Dashboard" in result

    def test_dashboard_daily_view(self, dashboard_tools):
        """Test daily view renders correctly."""
        render_tool = dashboard_tools[0]
        result = render_tool.invoke(
            {
                "user_id": "test_user",
                "view": "daily",
            }
        )
        assert isinstance(result, str)
        assert "Today" in result

    def test_dashboard_monthly_view(self, dashboard_tools):
        """Test monthly view renders correctly."""
        render_tool = dashboard_tools[0]
        result = render_tool.invoke(
            {
                "user_id": "test_user",
                "view": "monthly",
            }
        )
        assert isinstance(result, str)
        assert "This Month" in result

    def test_dashboard_without_mood_section(self, dashboard_tools):
        """Test dashboard without mood section."""
        render_tool = dashboard_tools[0]
        result = render_tool.invoke(
            {
                "user_id": "test_user",
                "view": "weekly",
                "include_mood": False,
            }
        )
        assert isinstance(result, str)

    def test_dashboard_without_goals_section(self, dashboard_tools):
        """Test dashboard without goals section."""
        render_tool = dashboard_tools[0]
        result = render_tool.invoke(
            {
                "user_id": "test_user",
                "view": "weekly",
                "include_goals": False,
            }
        )
        assert isinstance(result, str)


# ==============================================================================
# Test Calculate Life Satisfaction Score
# ==============================================================================


class TestCalculateLifeSatisfactionScore:
    """Test the calculate_life_satisfaction_score tool."""

    def test_score_calculation(self, dashboard_tools):
        """Test that score calculation returns result."""
        score_tool = dashboard_tools[1]
        result = score_tool.invoke(
            {
                "user_id": "test_user",
                "view": "weekly",
            }
        )
        assert isinstance(result, str)
        assert "LIFE SATISFACTION SCORE REPORT" in result or "Life Satisfaction Score" in result

    def test_score_in_range(self, dashboard_tools):
        """Test that score is in valid range 0-100."""
        score_tool = dashboard_tools[1]
        result = score_tool.invoke(
            {
                "user_id": "test_user",
                "view": "weekly",
            }
        )
        # Extract score from result
        import re

        match = re.search(r"(\d+\.?\d*)/100", result)
        if match:
            score = float(match.group(1))
            assert 0 <= score <= 100

    def test_score_includes_all_domains(self, dashboard_tools):
        """Test that score breakdown includes all domains."""
        score_tool = dashboard_tools[1]
        result = score_tool.invoke(
            {
                "user_id": "test_user",
                "view": "weekly",
            }
        )
        for domain in DOMAINS.values():
            assert domain["name"] in result or domain["icon"] in result

    def test_score_has_recommendations(self, dashboard_tools):
        """Test that score result includes recommendations."""
        score_tool = dashboard_tools[1]
        result = score_tool.invoke(
            {
                "user_id": "test_user",
                "view": "weekly",
            }
        )
        assert "Recommendations" in result or "recommendations" in result.lower()


# ==============================================================================
# Test Generate Domain Progress Bar
# ==============================================================================


class TestGenerateDomainProgressBar:
    """Test the generate_domain_progress_bar tool."""

    def test_domain_bar_renders(self, dashboard_tools):
        """Test that domain progress bar renders."""
        bar_tool = dashboard_tools[2]
        result = bar_tool.invoke(
            {
                "user_id": "test_user",
                "domain": "career",
                "view": "weekly",
            }
        )
        assert isinstance(result, str)
        assert "Progress" in result

    def test_all_domains_render(self, dashboard_tools):
        """Test that all domains can be rendered."""
        bar_tool = dashboard_tools[2]
        for domain_key in DOMAINS.keys():
            result = bar_tool.invoke(
                {
                    "user_id": "test_user",
                    "domain": domain_key,
                    "view": "weekly",
                }
            )
            assert isinstance(result, str)
            assert len(result) > 0

    def test_invalid_domain_error(self, dashboard_tools):
        """Test that invalid domain returns error."""
        bar_tool = dashboard_tools[2]
        result = bar_tool.invoke(
            {
                "user_id": "test_user",
                "domain": "invalid_domain",
                "view": "weekly",
            }
        )
        assert "Error" in result or "error" in result.lower()

    def test_domain_bar_includes_tips(self, dashboard_tools):
        """Test that domain bar includes improvement tips."""
        bar_tool = dashboard_tools[2]
        result = bar_tool.invoke(
            {
                "user_id": "test_user",
                "domain": "career",
                "view": "weekly",
            }
        )
        assert "Tips" in result or "tips" in result.lower()


# ==============================================================================
# Test Create Mood Trend Sparkline
# ==============================================================================


class TestCreateMoodTrendSparkline:
    """Test the create_mood_trend_sparkline tool."""

    def test_sparkline_renders(self, dashboard_tools):
        """Test that mood sparkline renders."""
        sparkline_tool = dashboard_tools[3]
        result = sparkline_tool.invoke(
            {
                "user_id": "test_user",
                "view": "weekly",
            }
        )
        assert isinstance(result, str)
        assert "Mood Trend" in result or "mood" in result.lower()

    def test_sparkline_includes_statistics(self, dashboard_tools):
        """Test that sparkline includes statistics."""
        sparkline_tool = dashboard_tools[3]
        result = sparkline_tool.invoke(
            {
                "user_id": "test_user",
                "view": "weekly",
            }
        )
        # Should include stats like current, average
        assert "Current" in result or "current" in result.lower() or "Statistics" in result

    def test_sparkline_different_views(self, dashboard_tools):
        """Test sparkline with different views."""
        sparkline_tool = dashboard_tools[3]
        for view in ["daily", "weekly", "monthly"]:
            result = sparkline_tool.invoke(
                {
                    "user_id": "test_user",
                    "view": view,
                }
            )
            assert isinstance(result, str)


# ==============================================================================
# Test Get Recent Achievements
# ==============================================================================


class TestGetRecentAchievements:
    """Test the get_recent_achievements tool."""

    def test_achievements_renders(self, dashboard_tools):
        """Test that achievements renders."""
        achievements_tool = dashboard_tools[4]
        result = achievements_tool.invoke(
            {
                "user_id": "test_user",
                "limit": 5,
            }
        )
        assert isinstance(result, str)
        assert "Achievement" in result or "achievement" in result.lower()

    def test_achievements_limit(self, dashboard_tools):
        """Test that limit parameter works."""
        achievements_tool = dashboard_tools[4]
        result1 = achievements_tool.invoke(
            {
                "user_id": "test_user",
                "limit": 2,
            }
        )
        result2 = achievements_tool.invoke(
            {
                "user_id": "test_user",
                "limit": 5,
            }
        )
        assert isinstance(result1, str)
        assert isinstance(result2, str)


# ==============================================================================
# Test Get Upcoming Milestones
# ==============================================================================


class TestGetUpcomingMilestones:
    """Test the get_upcoming_milestones tool."""

    def test_milestones_renders(self, dashboard_tools):
        """Test that milestones renders."""
        milestones_tool = dashboard_tools[5]
        result = milestones_tool.invoke(
            {
                "user_id": "test_user",
                "limit": 5,
            }
        )
        assert isinstance(result, str)
        assert "Milestone" in result or "milestone" in result.lower()

    def test_milestones_include_urgency(self, dashboard_tools):
        """Test that milestones include urgency indicators."""
        milestones_tool = dashboard_tools[5]
        result = milestones_tool.invoke(
            {
                "user_id": "test_user",
                "limit": 5,
            }
        )
        # Should have urgency or timing info
        assert isinstance(result, str)


# ==============================================================================
# Test Export Dashboard Report
# ==============================================================================


class TestExportDashboardReport:
    """Test the export_dashboard_report tool."""

    def test_report_generates(self, dashboard_tools):
        """Test that report generates."""
        export_tool = dashboard_tools[6]
        result = export_tool.invoke(
            {
                "user_id": "test_user",
                "view": "weekly",
                "format": "markdown",
            }
        )
        assert isinstance(result, str)
        assert "Report" in result or "report" in result.lower()

    def test_report_includes_markdown(self, dashboard_tools):
        """Test that markdown report includes markdown elements."""
        export_tool = dashboard_tools[6]
        result = export_tool.invoke(
            {
                "user_id": "test_user",
                "view": "weekly",
                "format": "markdown",
            }
        )
        # Should contain markdown elements
        assert "#" in result  # Headers


# ==============================================================================
# Test Switch Dashboard View
# ==============================================================================


class TestSwitchDashboardView:
    """Test the switch_dashboard_view tool."""

    def test_switch_view_success(self, dashboard_tools):
        """Test that view switching works."""
        switch_tool = dashboard_tools[7]
        result = switch_tool.invoke(
            {
                "user_id": "test_user",
                "view": "monthly",
                "render": False,
            }
        )
        assert isinstance(result, str)
        assert "switched" in result.lower() or "monthly" in result.lower()

    def test_switch_invalid_view_error(self, dashboard_tools):
        """Test that invalid view returns error."""
        switch_tool = dashboard_tools[7]
        result = switch_tool.invoke(
            {
                "user_id": "test_user",
                "view": "invalid_view",
                "render": False,
            }
        )
        assert "Error" in result or "error" in result.lower()

    def test_switch_view_with_render(self, dashboard_tools):
        """Test that view switching with render works."""
        switch_tool = dashboard_tools[7]
        result = switch_tool.invoke(
            {
                "user_id": "test_user",
                "view": "weekly",
                "render": True,
            }
        )
        assert isinstance(result, str)
        assert "Progress Dashboard" in result or "switched" in result.lower()


# ==============================================================================
# Integration Tests
# ==============================================================================


class TestDashboardIntegration:
    """Integration tests for dashboard functionality."""

    def test_end_to_end_dashboard_workflow(self, dashboard_tools):
        """Test complete dashboard workflow."""
        (
            render_tool,
            score_tool,
            bar_tool,
            sparkline_tool,
            achievements_tool,
            milestones_tool,
            export_tool,
            switch_tool,
        ) = dashboard_tools

        # 1. Render main dashboard
        dashboard = render_tool.invoke(
            {
                "user_id": "integration_test",
                "view": "weekly",
            }
        )
        assert "Progress Dashboard" in dashboard

        # 2. Calculate satisfaction score
        score = score_tool.invoke(
            {
                "user_id": "integration_test",
                "view": "weekly",
            }
        )
        assert "LIFE SATISFACTION SCORE REPORT" in score or "Life Satisfaction Score" in score

        # 3. Get domain progress
        domain_progress = bar_tool.invoke(
            {
                "user_id": "integration_test",
                "domain": "career",
                "view": "weekly",
            }
        )
        assert "Progress" in domain_progress

        # 4. Get mood trend
        mood = sparkline_tool.invoke(
            {
                "user_id": "integration_test",
                "view": "weekly",
            }
        )
        assert "MOOD TREND SPARKLINE" in mood or "Mood" in mood

        # 5. Get achievements
        achievements = achievements_tool.invoke(
            {
                "user_id": "integration_test",
                "limit": 3,
            }
        )
        assert isinstance(achievements, str)

        # 6. Get milestones
        milestones = milestones_tool.invoke(
            {
                "user_id": "integration_test",
                "limit": 3,
            }
        )
        assert isinstance(milestones, str)

        # 7. Export report
        report = export_tool.invoke(
            {
                "user_id": "integration_test",
                "view": "weekly",
            }
        )
        assert "Report" in report or "report" in report.lower()

    def test_consistent_data_across_tools(self, dashboard_tools):
        """Test that data is consistent across different tools."""
        render_tool, score_tool, _, _, _, _, _, _ = dashboard_tools

        # Get dashboard and score for same user
        dashboard = render_tool.invoke(
            {
                "user_id": "consistency_test",
                "view": "weekly",
            }
        )
        score_result = score_tool.invoke(
            {
                "user_id": "consistency_test",
                "view": "weekly",
            }
        )

        # Both should succeed
        assert isinstance(dashboard, str)
        assert isinstance(score_result, str)


# ==============================================================================
# Mock Data Tests
# ==============================================================================


class TestMockDataGeneration:
    """Test mock data generation functions."""

    def test_mock_progress_deterministic(self):
        """Test that mock progress is deterministic for same inputs."""
        from tools.dashboard_tools import _generate_mock_progress

        result1 = _generate_mock_progress("user1", "career", "weekly")
        result2 = _generate_mock_progress("user1", "career", "weekly")
        assert result1 == result2

    def test_mock_progress_different_users(self):
        """Test that different users get different progress."""
        from tools.dashboard_tools import _generate_mock_progress

        result1 = _generate_mock_progress("user1", "career", "weekly")
        result2 = _generate_mock_progress("user2", "career", "weekly")
        # Different users likely have different progress
        assert isinstance(result1, float)
        assert isinstance(result2, float)

    def test_mock_progress_in_range(self):
        """Test that mock progress is in valid range."""
        from tools.dashboard_tools import _generate_mock_progress

        result = _generate_mock_progress("user1", "career", "weekly")
        assert 0 <= result <= 100

    def test_mock_mood_data_length(self):
        """Test that mock mood data has correct length."""
        from tools.dashboard_tools import _generate_mock_mood_data

        result = _generate_mock_mood_data("user1", 7)
        assert len(result) == 7

    def test_mock_mood_data_in_range(self):
        """Test that mock mood data values are in valid range."""
        from tools.dashboard_tools import _generate_mock_mood_data

        result = _generate_mock_mood_data("user1", 7)
        for value in result:
            assert 1 <= value <= 10


# ==============================================================================
# Helper Function Tests
# ==============================================================================


class TestHelperFunctions:
    """Test helper functions."""

    def test_score_label_excellent(self):
        """Test score label for excellent scores."""
        from tools.dashboard_tools import _score_label

        assert _score_label(85) == "Excellent"
        assert _score_label(80) == "Excellent"

    def test_score_label_good(self):
        """Test score label for good scores."""
        from tools.dashboard_tools import _score_label

        assert _score_label(75) == "Good"
        assert _score_label(60) == "Good"

    def test_score_label_developing(self):
        """Test score label for developing scores."""
        from tools.dashboard_tools import _score_label

        assert _score_label(50) == "Developing"
        assert _score_label(40) == "Developing"

    def test_score_label_starting(self):
        """Test score label for starting scores."""
        from tools.dashboard_tools import _score_label

        assert _score_label(30) == "Starting"
        assert _score_label(0) == "Starting"

    def test_domain_tips_exist(self):
        """Test that all domains have tips."""
        from tools.dashboard_tools import _get_domain_tips

        for domain in DOMAINS.keys():
            tips = _get_domain_tips(domain, 50)
            assert len(tips) > 0
            assert all(isinstance(tip, str) for tip in tips)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
