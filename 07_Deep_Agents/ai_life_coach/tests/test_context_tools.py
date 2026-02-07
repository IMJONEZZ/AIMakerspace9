"""
Test suite for context management tools.

Tests all 6 context tools:
- save_assessment
- get_active_plan
- save_weekly_progress
- list_user_assessments
- read_assessment
- save_curated_resource

Run with: pytest tests/test_context_tools.py -v
"""

import pytest
import json
from pathlib import Path
from datetime import date, datetime
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import configuration and tools
from src.config import config


class TestContextTools:
    """Test suite for context management tools."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, tmp_path):
        """Set up test environment before each test."""
        # Initialize config with temporary workspace
        original_workspace = config.memory.workspace_dir

        try:
            # Set workspace to tmp_path for testing
            config.memory.workspace_dir = tmp_path / "workspace"
            config.initialize_environment()

            # Import and create tools using factory function
            from src.tools.context_tools import create_context_tools

            # Pass the backend explicitly to avoid initialization issues
            (
                save_assessment,
                get_active_plan,
                save_weekly_progress,
                list_user_assessments,
                read_assessment,
                save_curated_resource,
            ) = create_context_tools(backend=config.backend)

            self.tools = {
                "save_assessment": save_assessment,
                "get_active_plan": get_active_plan,
                "save_weekly_progress": save_weekly_progress,
                "list_user_assessments": list_user_assessments,
                "read_assessment": read_assessment,
                "save_curated_resource": save_curated_resource,
            }

            yield self.tools

        finally:
            # Restore original workspace and clean up
            config.memory.workspace_dir = original_workspace

    # ========================================================================
    # Test save_assessment
    # ========================================================================

def test_save_assessment_valid(self, setup_teardown):
        """Test saving a valid assessment."""
        tools = setup_teardown

        result = tools["save_assessment"].invoke({
            "user_id": "user_123",
            "assessment_data": {
                "energy_level": 7,
                "stress_level": 4,
                "sleep_quality": "good",
                "mood": "positive"
            }
        })

        assert "Assessment saved for user 'user_123'" in result
        assert "assessments/user_123/" in result

    def test_save_assessment_invalid_user_id(self, setup_teardown):
        """Test saving assessment with invalid user_id."""
        tools = setup_teardown

        result = tools["save_assessment"]("", {"energy_level": 7})
        assert "Error: user_id must be a non-empty string" in result

    def test_save_assessment_invalid_data(self, setup_teardown):
        """Test saving assessment with invalid data."""
        tools = setup_teardown

        result = tools["save_assessment"]("user_123", {})
        assert "Error: assessment_data must be a non-empty dictionary" in result

    def test_save_assessment_creates_json_file(self, setup_teardown):
        """Test that save_assessment creates a valid JSON file."""
        tools = setup_teardown

        tools["save_assessment"](
            "user_456", {"energy_level": 8, "stress_level": 3, "mood": "energetic"}
        )

        # Verify file was created
        workspace = config.memory.workspace_dir
        assessments_dir = workspace / "assessments" / "user_456"
        assert assessments_dir.exists()

        # Find and read the JSON file
        json_files = list(assessments_dir.glob("*.json"))
        assert len(json_files) == 1

        with open(json_files[0]) as f:
            data = json.load(f)

        assert data["user_id"] == "user_456"
        assert data["energy_level"] == 8
        assert "timestamp" in data

    # ========================================================================
    # Test get_active_plan
    # ========================================================================

    def test_get_active_plan_no_directory(self, setup_teardown):
        """Test getting plan when no directory exists."""
        tools = setup_teardown

        result = tools["get_active_plan"]("user_789")
        assert "No plan directory found for user 'user_789'" in result

    def test_get_active_plan_no_files(self, setup_teardown):
        """Test getting plan when directory exists but no files."""
        tools = setup_teardown

        # Create empty plans directory
        workspace = config.memory.workspace_dir
        plans_dir = workspace / "plans" / "user_789"
        plans_dir.mkdir(parents=True)

        result = tools["get_active_plan"]("user_789")
        assert "No plan files found for user 'user_789'" in result

    def test_get_active_plan_returns_content(self, setup_teardown):
        """Test that get_active_plan returns plan content."""
        tools = setup_teardown

        # Create a test plan file
        workspace = config.memory.workspace_dir
        plans_dir = workspace / "plans" / "user_999"
        plans_dir.mkdir(parents=True)

        plan_file = plans_dir / "90_day_plan.md"
        plan_content = "# 90-Day Wellness Plan\n\nThis is a test plan."
        plan_file.write_text(plan_content)

        result = tools["get_active_plan"]("user_999")
        assert "Active Plan for user 'user_999'" in result
        assert plan_content in result

    def test_get_active_plan_invalid_user_id(self, setup_teardown):
        """Test getting plan with invalid user_id."""
        tools = setup_teardown

        result = tools["get_active_plan"]("")
        assert "Error: user_id must be a non-empty string" in result

    # ========================================================================
    # Test save_weekly_progress
    # ========================================================================

    def test_save_weekly_progress_valid(self, setup_teardown):
        """Test saving valid weekly progress."""
        tools = setup_teardown

        result = tools["save_weekly_progress"](
            "user_123",
            {
                "week_number": 1,
                "completion_rate": 0.85,
                "achievements": ["Started routine", "Exercised 3 times"],
                "challenges": ["Difficulty waking up early"],
            },
        )

        assert "Weekly progress saved for user 'user_123'" in result
        assert "Week: 1" in result

    def test_save_weekly_progress_missing_week_number(self, setup_teardown):
        """Test saving weekly progress without week number."""
        tools = setup_teardown

        result = tools["save_weekly_progress"]("user_123", {"completion_rate": 0.85})
        assert "Error: week_data must contain 'week_number' field" in result

    def test_save_weekly_progress_invalid_user_id(self, setup_teardown):
        """Test saving weekly progress with invalid user_id."""
        tools = setup_teardown

        result = tools["save_weekly_progress"]("", {"week_number": 1})
        assert "Error: user_id must be a non-empty string" in result

    def test_save_weekly_progress_creates_json_file(self, setup_teardown):
        """Test that save_weekly_progress creates a valid JSON file."""
        tools = setup_teardown

        tools["save_weekly_progress"]("user_456", {"week_number": 2, "completion_rate": 0.90})

        # Verify file was created
        workspace = config.memory.workspace_dir
        progress_file = workspace / "progress" / "user_456" / "week_2_summary.json"
        assert progress_file.exists()

        with open(progress_file) as f:
            data = json.load(f)

        assert data["user_id"] == "user_456"
        assert data["week_number"] == 2
        assert "timestamp" in data

    # ========================================================================
    # Test list_user_assessments
    # ========================================================================

    def test_list_user_assessments_empty(self, setup_teardown):
        """Test listing assessments when none exist."""
        tools = setup_teardown

        result = tools["list_user_assessments"]("user_789")
        assert "No assessment directory found for user 'user_789'" in result

    def test_list_user_assessments_with_files(self, setup_teardown):
        """Test listing assessments with multiple files."""
        tools = setup_teardown

        # Create two assessment files
        workspace = config.memory.workspace_dir
        assessments_dir = workspace / "assessments" / "user_999"
        assessments_dir.mkdir(parents=True)

        # Create first assessment
        today1 = date.today()
        file1 = assessments_dir / f"{today1}_assessment.json"
        with open(file1, "w") as f:
            json.dump(
                {"user_id": "user_999", "date": str(today1), "energy_level": 7, "stress_level": 4},
                f,
            )

        # Create second assessment (different date)
        today2 = date(2026, 1, 20) if today1 != date(2026, 1, 20) else date(2026, 1, 21)
        file2 = assessments_dir / f"{today2}_assessment.json"
        with open(file2, "w") as f:
            json.dump(
                {"user_id": "user_999", "date": str(today2), "energy_level": 8, "stress_level": 3},
                f,
            )

        result = tools["list_user_assessments"]("user_999")
        assert "Assessments for user 'user_999'" in result
        assert f"Total: 2 assessments" in result

    def test_list_user_assessments_invalid_user_id(self, setup_teardown):
        """Test listing assessments with invalid user_id."""
        tools = setup_teardown

        result = tools["list_user_assessments"]("")
        assert "Error: user_id must be a non-empty string" in result

    # ========================================================================
    # Test read_assessment
    # ========================================================================

    def test_read_assessment_valid(self, setup_teardown):
        """Test reading a valid assessment."""
        tools = setup_teardown

        # Create an assessment file first
        workspace = config.memory.workspace_dir
        assessments_dir = workspace / "assessments" / "user_123"
        assessments_dir.mkdir(parents=True)

        today = date.today()
        file_path = assessments_dir / f"{today}_assessment.json"
        test_data = {
            "user_id": "user_123",
            "date": str(today),
            "energy_level": 7,
            "stress_level": 4,
            "mood": "positive",
            "notes": "Feeling good!",
        }

        with open(file_path, "w") as f:
            json.dump(test_data, f)

        result = tools["read_assessment"]("user_123", str(today))
        assert f"Assessment for user 'user_123' on {today}" in result
        assert "energy_level: 7" in result
        assert "mood: positive" in result

    def test_read_assessment_not_found(self, setup_teardown):
        """Test reading an assessment that doesn't exist."""
        tools = setup_teardown

        result = tools["read_assessment"]("user_123", "2099-01-01")
        assert "No assessment found for user 'user_123' on date" in result

    def test_read_assessment_invalid_date_format(self, setup_teardown):
        """Test reading assessment with invalid date format."""
        tools = setup_teardown

        result = tools["read_assessment"]("user_123", "01-01-2026")
        assert "Error: assessment_date must be in YYYY-MM-DD format" in result

    def test_read_assessment_invalid_user_id(self, setup_teardown):
        """Test reading assessment with invalid user_id."""
        tools = setup_teardown

        result = tools["read_assessment"]("", "2026-01-01")
        assert "Error: user_id must be a non-empty string" in result

    # ========================================================================
    # Test save_curated_resource
    # ========================================================================

    def test_save_curated_resource_valid(self, setup_teardown):
        """Test saving a valid curated resource."""
        tools = setup_teardown

        result = tools["save_curated_resource"](
            "Morning Routine Guide", "wellness_tips", "Start your day with meditation and exercise."
        )

        assert "Resource saved to general resources" in result
        assert "Title: Morning Routine Guide" in result

    def test_save_curated_resource_for_user(self, setup_teardown):
        """Test saving a resource for a specific user."""
        tools = setup_teardown

        result = tools["save_curated_resource"](
            "Career Growth Tips",
            "career_advice",
            "Focus on skill development and networking.",
            user_id="user_123",
        )

        assert "Resource saved to user 'user_123'" in result
        assert "Title: Career Growth Tips" in result

    def test_save_curated_resource_invalid_title(self, setup_teardown):
        """Test saving resource with invalid title."""
        tools = setup_teardown

        result = tools["save_curated_resource"]("", "category", "content")
        assert "Error: title must be a non-empty string" in result

    def test_save_curated_resource_invalid_content(self, setup_teardown):
        """Test saving resource with invalid content."""
        tools = setup_teardown

        result = tools["save_curated_resource"]("Title", "category", "")
        assert "Error: content must be a non-empty string" in result

    def test_save_curated_resource_creates_markdown_file(self, setup_teardown):
        """Test that save_curated_resource creates a valid Markdown file."""
        tools = setup_teardown

        tools["save_curated_resource"]("Test Guide", "test_category", "This is test content.")

        # Verify file was created
        workspace = config.memory.workspace_dir
        resources_dir = workspace / "resources" / "curated_articles" / "test_category"
        assert resources_dir.exists()

        # Find and read the Markdown file
        md_files = list(resources_dir.glob("*.md"))
        assert len(md_files) == 1

        content = md_files[0].read_text()
        assert "# Test Guide" in content
        assert "**Category**: test_category" in content
        assert "This is test content." in content

    # ========================================================================
    # Integration Tests
    # ========================================================================

    def test_full_assessment_workflow(self, setup_teardown):
        """Test complete workflow: save, list, read assessments."""
        tools = setup_teardown

        user_id = "integration_test_user"
        today = date.today()

        # Save an assessment
        save_result = tools["save_assessment"](
            user_id, {"energy_level": 7, "stress_level": 3, "mood": "optimistic"}
        )
        assert "Assessment saved" in save_result

        # List assessments
        list_result = tools["list_user_assessments"](user_id)
        assert f"Total: 1 assessment" in list_result

        # Read the specific assessment
        read_result = tools["read_assessment"](user_id, str(today))
        assert f"Assessment for user '{user_id}' on {today}" in read_result
        assert "energy_level: 7" in read_result

    def test_full_progress_tracking_workflow(self, setup_teardown):
        """Test complete progress tracking workflow."""
        tools = setup_teardown

        user_id = "progress_test_user"

        # Save progress for week 1
        result1 = tools["save_weekly_progress"](
            user_id,
            {
                "week_number": 1,
                "completion_rate": 0.75,
                "achievements": ["Started exercising"],
                "challenges": ["Sleep issues"],
            },
        )
        assert "Weekly progress saved" in result1

        # Save progress for week 2
        result2 = tools["save_weekly_progress"](
            user_id,
            {
                "week_number": 2,
                "completion_rate": 0.85,
                "achievements": ["Improved sleep", "Consistent exercise"],
                "challenges": [],
            },
        )
        assert "Weekly progress saved" in result2

        # Verify both files exist
        workspace = config.memory.workspace_dir
        progress_dir = workspace / "progress" / user_id
        assert (progress_dir / "week_1_summary.json").exists()
        assert (progress_dir / "week_2_summary.json").exists()


if __name__ == "__main__":
    # Run tests with pytest
    import subprocess

    result = subprocess.run(["pytest", __file__, "-v"], cwd=str(Path(__file__).parent.parent))

    exit(result.returncode)
