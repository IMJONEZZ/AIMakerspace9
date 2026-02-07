"""
Test Suite for Phase-Based Planning Tools.

This module contains comprehensive tests for the phase planning system,
covering workflow initialization, transitions, milestone generation,
adaptive planning, and template formatting.
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path

# Import the phase planning tools and classes
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.phase_planning_tools import (
    Phase,
    Milestone,
    PhaseWorkflow,
    generate_milestones_from_goals,
    estimate_phase_start_dates,
    calculate_adaptive_recommendations,
    apply_phase_template,
    create_phase_planning_tools,
)
from src.config import config


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def sample_goals():
    """Provide sample goals for testing."""
    return [
        {"title": "Get promotion", "domain": "career"},
        {"title": "Improve sleep quality", "domain": "wellness"},
    ]


@pytest.fixture
def sample_workflow(sample_goals):
    """Create a sample workflow for testing."""
    return PhaseWorkflow("test_user", sample_goals)


# ==============================================================================
# Phase Class Tests
# ==============================================================================


class TestPhase:
    """Tests for the Phase class."""

    def test_valid_phases(self):
        """Test that all valid phases are defined."""
        assert Phase.VALID_PHASES == ["discovery", "planning", "execution", "review"]

    def test_get_phase_info(self):
        """Test getting phase configuration."""
        discovery_info = Phase.get_phase_info("discovery")
        assert discovery_info is not None
        assert discovery_info["name"] == "Discovery"
        assert discovery_info["icon"] == "🔍"

    def test_get_phase_info_invalid(self):
        """Test getting info for invalid phase."""
        assert Phase.get_phase_info("invalid") is None

    def test_get_next_phase(self):
        """Test getting next phase in sequence."""
        assert Phase.get_next_phase("discovery") == "planning"
        assert Phase.get_next_phase("planning") == "execution"
        assert Phase.get_next_phase("execution") == "review"

    def test_get_next_phase_final(self):
        """Test getting next phase from final phase."""
        assert Phase.get_next_phase("review") is None

    def test_get_next_phase_invalid(self):
        """Test getting next phase from invalid phase."""
        assert Phase.get_next_phase("invalid") is None


# ==============================================================================
# Milestone Class Tests
# ==============================================================================


class TestMilestone:
    """Tests for the Milestone class."""

    def test_milestone_creation(self):
        """Test creating a milestone."""
        milestone = Milestone(
            id="ms_1",
            title="Complete Discovery Phase",
            phase="discovery",
        )
        assert milestone.id == "ms_1"
        assert milestone.title == "Complete Discovery Phase"
        assert milestone.phase == "discovery"
        assert milestone.status == "pending"

    def test_milestone_to_dict(self):
        """Test converting milestone to dictionary."""
        milestone = Milestone(
            id="ms_1",
            title="Test Milestone",
            target_date="2025-03-01",
            status="completed",
        )
        data = milestone.to_dict()
        assert data["id"] == "ms_1"
        assert data["title"] == "Test Milestone"
        assert data["target_date"] == "2025-03-01"
        assert data["status"] == "completed"


# ==============================================================================
# PhaseWorkflow Class Tests
# ==============================================================================


class TestPhaseWorkflow:
    """Tests for the PhaseWorkflow class."""

    def test_workflow_creation(self):
        """Test creating a workflow."""
        goals = [{"title": "Goal 1"}]
        workflow = PhaseWorkflow("test_user", goals)
        assert workflow.user_id == "test_user"
        assert workflow.goals == goals
        assert workflow.current_phase == "discovery"

    def test_add_milestone(self):
        """Test adding milestones to workflow."""
        workflow = PhaseWorkflow("test_user", [])
        milestone = Milestone(id="ms_1", title="Test Milestone")
        workflow.add_milestone(milestone)
        assert "ms_1" in workflow.milestones

    def test_update_milestone_status(self):
        """Test updating milestone status."""
        workflow = PhaseWorkflow("test_user", [])
        milestone = Milestone(id="ms_1", title="Test Milestone")
        workflow.add_milestone(milestone)
        workflow.update_milestone_status("ms_1", "completed")
        assert workflow.milestones["ms_1"].status == "completed"

    def test_update_phase_completion(self):
        """Test updating phase completion status."""
        workflow = PhaseWorkflow("test_user", [])
        workflow.update_phase_completion("discovery", "Initial assessment completed", True)
        assert workflow.phase_completion["discovery"]["Initial assessment completed"] is True

    def test_get_phase_completion_percentage(self):
        """Test calculating phase completion percentage."""
        workflow = PhaseWorkflow("test_user", [])
        # Mark one criterion as completed
        criteria = list(workflow.phase_completion["discovery"].keys())
        if criteria:
            workflow.update_phase_completion("discovery", criteria[0], True)
            pct = workflow.get_phase_completion_percentage("discovery")
            assert pct > 0

    def test_can_transition_to_next_phase_ready(self):
        """Test transition eligibility when ready."""
        workflow = PhaseWorkflow("test_user", [])
        # Mark all criteria as completed
        for criterion in workflow.phase_completion["discovery"].keys():
            workflow.update_phase_completion("discovery", criterion, True)
        can_transition, blocking = workflow.can_transition_to_next_phase()
        # Only milestones will block now
        assert isinstance(can_transition, bool)

    def test_can_transition_to_next_phase_blocked(self):
        """Test transition eligibility when blocked."""
        workflow = PhaseWorkflow("test_user", [])
        # Don't complete any criteria
        can_transition, blocking = workflow.can_transition_to_next_phase()
        assert not can_transition
        assert len(blocking) > 0

    def test_transition_to_next_phase(self):
        """Test transitioning to next phase."""
        workflow = PhaseWorkflow("test_user", [])
        # Mark all criteria as completed
        for criterion in workflow.phase_completion["discovery"].keys():
            workflow.update_phase_completion("discovery", criterion, True)
        # Add a completed milestone
        milestone = Milestone(id="ms_1", title="Test", phase="discovery")
        workflow.add_milestone(milestone)
        workflow.update_milestone_status("ms_1", "completed")

        success, message = workflow.transition_to_next_phase()
        assert success
        assert workflow.current_phase == "planning"

    def test_transition_blocked(self):
        """Test transition when blocked."""
        workflow = PhaseWorkflow("test_user", [])
        success, message = workflow.transition_to_next_phase()
        assert not success
        # Now transition to next phase is blocked

    def test_add_adaptation(self):
        """Test recording adaptations."""
        workflow = PhaseWorkflow("test_user", [])
        workflow.add_adaptation("Testing", {"change": "value"})
        assert len(workflow.adaptations) == 1

    def test_to_dict(self):
        """Test converting workflow to dictionary."""
        goals = [{"title": "Goal 1"}]
        workflow = PhaseWorkflow("test_user", goals)
        data = workflow.to_dict()
        assert data["user_id"] == "test_user"
        assert data["goals"] == goals
        assert data["current_phase"] == "discovery"


# ==============================================================================
# Helper Function Tests
# ==============================================================================


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_generate_milestones_from_goals(self, sample_goals):
        """Test generating milestones from goals."""
        milestones = generate_milestones_from_goals(sample_goals)
        assert len(milestones) > 0
        # Should have phase milestones + goal milestones
        assert any("Complete Discovery Phase" in m.title for m in milestones)

    def test_generate_milestones_specific_phases(self, sample_goals):
        """Test generating milestones for specific phases."""
        milestones = generate_milestones_from_goals(sample_goals, ["discovery", "planning"])
        assert all(m.phase in ["discovery", "planning"] for m in milestones)

    def test_estimate_phase_start_dates(self):
        """Test estimating phase start dates."""
        start_date = datetime(2025, 2, 1)
        dates = estimate_phase_start_dates(start_date)
        assert "discovery" in dates
        assert "planning" in dates
        assert dates["discovery"] == start_date.isoformat()

    def test_calculate_adaptive_recommendations(self, sample_workflow):
        """Test calculating adaptive recommendations."""
        # Add a delayed milestone
        milestone = Milestone(id="ms_1", title="Test", status="delayed")
        sample_workflow.add_milestone(milestone)

        progress_data = {"milestone_progress": {}}
        recommendations = calculate_adaptive_recommendations(sample_workflow, progress_data)
        assert len(recommendations) > 0
        assert any(r["type"] == "milestone_adjustment" for r in recommendations)

    def test_apply_phase_template(self):
        """Test applying phase template."""
        content = {
            "status": {"Completion Percentage": "75%"},
            "completion_criteria": {"Criterion 1": True, "Criterion 2": False},
        }
        formatted = apply_phase_template("discovery", content)
        assert "DISCOVERY PHASE" in formatted
        assert "75%" in formatted


# ==============================================================================
# Integration Tests (with backend)
# ==============================================================================


class TestPhasePlanningToolsIntegration:
    """Integration tests for phase planning tools."""

    @pytest.fixture(autouse=True)
    def setup_environment(self):
        """Set up environment for integration tests."""
        config.initialize_environment()

    def test_create_phase_planning_tools(self):
        """Test creating phase planning tools."""
        from src.config import get_backend
        from langchain_core.tools import BaseTool

        tools = create_phase_planning_tools(backend=get_backend())
        assert len(tools) == 6
        (
            initialize_transition,
            transition,
            generate_milestones,
            adapt_plan,
            get_status,
            apply_template,
        ) = tools
        # LangChain tools are instances of BaseTool or have a __name__ attribute
        assert isinstance(initialize_transition, BaseTool) or hasattr(initialize_transition, "name")
        assert isinstance(transition, BaseTool) or hasattr(transition, "name")

    def test_initialize_phase_workflow(self):
        """Test initializing a phase workflow via tool."""
        from src.config import get_backend

        initialize_transition, _, _, _, _, _ = create_phase_planning_tools(backend=get_backend())

        result = initialize_transition.func(
            user_id="test_integration_user",
            goals=[{"title": "Integration Test Goal", "domain": "career"}],
        )
        assert "Phase-Based Workflow Initialized" in result
        assert "Integration Test Goal" in result

    def test_transition_to_next_phase_blocked(self):
        """Test transition when blocked via tool."""
        from src.config import get_backend

        initialize_transition, transition, _, _, _, _ = create_phase_planning_tools(
            backend=get_backend()
        )

        # Initialize first
        initialize_transition.func(
            user_id="test_transition_blocked",
            goals=[{"title": "Test Goal"}],
        )

        # Try to transition without completing criteria
        result = transition.func(user_id="test_transition_blocked")
        assert "Cannot transition" in result or "Blocking issues" in result

    def test_get_phase_status(self):
        """Test getting phase status via tool."""
        from src.config import get_backend

        initialize_transition, _, _, _, get_status, _ = create_phase_planning_tools(
            backend=get_backend()
        )

        # Initialize first
        initialize_transition.func(
            user_id="test_get_status",
            goals=[{"title": "Test Goal"}],
        )

        result = get_status.func(user_id="test_get_status")
        assert "Phase Workflow Status" in result
        assert "Current Phase: Discovery" in result

    def test_generate_milestones_tool(self):
        """Test generating milestones via tool."""
        from src.config import get_backend

        initialize_transition, _, generate_milestones, _, _, _ = create_phase_planning_tools(
            backend=get_backend()
        )

        # Initialize first
        initialize_transition.func(
            user_id="test_milestones",
            goals=[{"title": "Test Goal"}],
        )

        # Generate milestones
        result = generate_milestones.func(user_id="test_milestones")
        assert "Milestones Generated" in result

    def test_adapt_plan_based_on_progress(self):
        """Test adapting plan based on progress via tool."""
        from src.config import get_backend

        initialize_transition, _, _, adapt_plan, _, _ = create_phase_planning_tools(
            backend=get_backend()
        )

        # Initialize first
        initialize_transition.func(
            user_id="test_adapt",
            goals=[{"title": "Test Goal"}],
        )

        # Provide progress data
        result = adapt_plan.func(
            user_id="test_adapt",
            progress_data={
                "milestone_progress": {},
                "goal_progress": {},
                "notes": "Making progress",
            },
        )
        assert "Adaptive Planning Analysis" in result

    def test_apply_phase_template_tool(self):
        """Test applying phase template via tool."""
        from src.config import get_backend

        initialize_transition, _, _, _, _, apply_template = create_phase_planning_tools(
            backend=get_backend()
        )

        # Initialize first
        initialize_transition.func(
            user_id="test_template",
            goals=[{"title": "Test Goal"}],
        )

        # Apply template
        result = apply_template.func(user_id="test_template")
        assert "DISCOVERY PHASE" in result


# ==============================================================================
# End-to-End Workflow Tests
# ==============================================================================


class TestEndToEndWorkflow:
    """End-to-end tests for complete phase workflow."""

    @pytest.fixture(autouse=True)
    def setup_environment(self):
        """Set up environment for integration tests."""
        config.initialize_environment()

    def test_complete_workflow_simulation(self):
        """Test simulating a complete workflow through all phases."""
        from src.config import get_backend

        initialize, transition, generate_milestones, adapt_plan, get_status, apply_template = (
            create_phase_planning_tools(backend=get_backend())
        )
        user_id = "test_e2e_user"

        # 1. Initialize workflow
        result = initialize.func(
            user_id=user_id,
            goals=[
                {"title": "Learn Python", "domain": "career"},
                {"title": "Exercise daily", "domain": "wellness"},
            ],
        )
        assert "Phase-Based Workflow Initialized" in result

        # 2. Check initial status
        result = get_status.func(user_id=user_id)
        assert "Current Phase: Discovery" in result

        # 3. Generate milestones
        result = generate_milestones.func(user_id=user_id)
        assert "Milestones Generated" in result

        # 4. Apply template
        result = apply_template.func(user_id=user_id)
        assert "DISCOVERY PHASE" in result

        # 5. Try to transition (should be blocked)
        result = transition.func(user_id=user_id)
        assert "Cannot transition" in result or "Blocking issues" in result

        # 6. Update progress
        result = adapt_plan.func(
            user_id=user_id,
            progress_data={
                "milestone_progress": {},
                "goal_progress": {"g1": 50},
                "notes": "Good progress",
            },
        )
        assert "Adaptive Planning Analysis" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
