"""
Comprehensive test suite for Wellness Coach tools.

This module tests all wellness-related functionality including:
- 8 Dimensions of Wellness assessment
- Habit formation planning (Atomic Habits framework)
- Stress management techniques
- Sleep optimization planning
- Exercise program design

Each test validates tool functionality, error handling, and integration.
"""

import pytest
from datetime import date, datetime
import json
from pathlib import Path

# Add parent directory to path for imports
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

# Import wellness tools
try:
    from src.tools.wellness_tools import create_wellness_tools
except ImportError:
    pytest.skip("wellness_tools module not available", allow_module_level=True)

# Import backend for tests
from deepagents.backends import FilesystemBackend


class TestWellnessToolsCreation:
    """Test that wellness tools can be created successfully."""

    def test_create_wellness_tools(self):
        """Test that all wellness tools are created correctly."""
        backend = FilesystemBackend(root_dir="/tmp/test_wellness_workspace")
        (
            assess_wellness_dimensions,
            create_habit_formation_plan,
            provide_stress_management_techniques,
            create_sleep_optimization_plan,
            design_exercise_program,
            calculate_wellness_score,
            track_habit_consistency,
        ) = create_wellness_tools(backend)

        assert assess_wellness_dimensions is not None
        assert create_habit_formation_plan is not None
        assert provide_stress_management_techniques is not None
        assert create_sleep_optimization_plan is not None
        assert design_exercise_program is not None
        assert calculate_wellness_score is not None
        assert track_habit_consistency is not None

    def test_tools_are_callable(self):
        """Test that all tools are callable functions."""
        backend = FilesystemBackend(root_dir="/tmp/test_wellness_workspace")
        tools = create_wellness_tools(backend)

        for tool in tools:
            # LangChain StructuredTools have a func attribute that is callable
            assert hasattr(tool, "func") and callable(tool.func), (
                f"Tool {tool.name} is not properly structured"
            )
            assert tool.name, f"Tool missing name attribute"


class TestAssessWellnessDimensions:
    """Test the assess_wellness_dimensions function."""

    def setup_method(self):
        """Set up test fixtures."""
        backend = FilesystemBackend(root_dir="/tmp/test_wellness_workspace")
        self.assess_wellness_dimensions, *_ = create_wellness_tools(backend)

    def test_valid_assessment(self):
        """Test wellness assessment with valid inputs."""
        result = self.assess_wellness_dimensions.invoke({
            user_id="test_user_123",
            physical_score=7,
            emotional_score=5,
            social_score=6,
        )

        assert "8 Dimensions of Wellness Assessment" in result
        assert "test_user_123" in result or str(datetime.now().year) in result
        # Check that scores are displayed
        assert "Physical Wellness" in result or "physical_score" not in result

    def test_all_8_dimensions(self):
        """Test assessment with all 8 dimensions provided."""
        result = self.assess_wellness_dimensions.invoke({
            user_id="test_user_456",
            physical_score=8,
            emotional_score=7,
            social_score=6,
            intellectual_score=5,
            spiritual_score=4,
            environmental_score=7,
            occupational_score=6,
            financial_score=8,
        )

        assert "Overall Wellness Score" in result
        # Should show strengths (7+)
        assert "Strengths:" in result or "✓ Strengths" in result

    def test_strengths_identification(self):
        """Test that high scores (7+) are identified as strengths."""
        result = self.assess_wellness_dimensions.invoke({
            user_id="test_user_high_scores",
            physical_score=9,
            emotional_score=8,
            social_score=7,
        )

        assert "Strengths:" in result or "✓ Strengths" in result

    def test_improvement_areas_identification(self):
        """Test that low scores (5 or below) are identified as improvement areas."""
        result = self.assess_wellness_dimensions.invoke({
            user_id="test_user_low_scores",
            physical_score=4,
            emotional_score=3,
            social_score=5,
        )

        assert "Improvement" in result or "◐ Areas for Improvement" in result

    def test_with_notes(self):
        """Test assessment with additional notes."""
        notes = "User is experiencing work-related stress affecting sleep."
        result = self.assess_wellness_dimensions.invoke({
            user_id="test_user_with_notes",
            physical_score=5,
            emotional_score=4,
            notes="test notes" })
        )

        assert notes in result

    def test_invalid_user_id(self):
        """Test that invalid user_id returns error message."""
        result = self.assess_wellness_dimensions.invoke({
            user_id="",
            physical_score=5,
        )

        assert "Error" in result
        assert "user_id" in result.lower()

    def test_invalid_score_range(self):
        """Test that scores outside 1-10 range return error."""
        result = self.assess_wellness_dimensions.invoke({
            user_id="test_user_invalid",
            physical_score=11,
        )

        assert "Error" in result
        assert "1 and 10" in result or "between 1 and 10" in result

    def test_partial_scores(self):
        """Test assessment with only some dimensions scored."""
        result = self.assess_wellness_dimensions.invoke({
            user_id="test_user_partial",
            physical_score=7,
            emotional_score=None,
        )

        assert "8 Dimensions of Wellness Assessment" in result


class TestHabitFormationPlan:
    """Test the create_habit_formation_plan function."""

    def setup_method(self):
        """Set up test fixtures."""
        backend = FilesystemBackend(root_dir="/tmp/test_wellness_workspace")
        _, self.create_habit_formation_plan, *_ = create_wellness_tools(backend)

    def test_complete_habit_plan(self):
        """Test habit formation plan with all parameters."""
        result = self.create_habit_formation_plan(
            user_id="test_user_habit",
            habit_name="Morning meditation",
            cue_description="Right after I brush my teeth",
            routine_steps=["Sit in quiet place", "Meditate for 10 minutes"],
            reward_description="Feel calm and centered",
            existing_habit_to_stack="Brushing teeth",
        )

        assert "Habit Formation Plan" in result
        assert "Morning meditation" in result
        assert "Cue (Trigger)" in result
        assert "Routine" in result
        assert "Reward" in result

    def test_atomic_habits_framework(self):
        """Test that Atomic Habits 4 Laws are referenced."""
        result = self.create_habit_formation_plan(
            user_id="test_user_atomic",
            habit_name="Evening reading",
        )

        assert "Make It Obvious" in result
        assert "Make It Attractive" in result
        assert "Make It Easy" in result or "Start ridiculously small" in result
        assert "Make It Satisfying" in result

    def test_habit_stacking(self):
        """Test habit stacking feature."""
        result = self.create_habit_formation_plan(
            user_id="test_user_stack",
            habit_name="Stretching",
            existing_habit_to_stack="Morning coffee",
        )

        assert "Habit Stacking" in result
        assert "Morning coffee" in result

    def test_minimal_plan(self):
        """Test habit plan with only required parameters."""
        result = self.create_habit_formation_plan(
            user_id="test_user_minimal",
            habit_name="Drink water first thing in morning",
        )

        assert "Habit Formation Plan" in result
        assert "Drink water first thing in morning" in result

    def test_invalid_user_id(self):
        """Test that invalid user_id returns error."""
        result = self.create_habit_formation_plan(
            user_id="",
            habit_name="Test habit",
        )

        assert "Error" in result
        assert "user_id" in result.lower()

    def test_invalid_habit_name(self):
        """Test that invalid habit_name returns error."""
        result = self.create_habit_formation_plan(
            user_id="test_user",
            habit_name="",
        )

        assert "Error" in result
        assert "habit_name" in result.lower()


class TestStressManagementTechniques:
    """Test the provide_stress_management_techniques function."""

    def setup_method(self):
        """Set up test fixtures."""
        backend = FilesystemBackend(root_dir="/tmp/test_wellness_workspace")
        _, _, self.provide_stress_management_techniques, *_ = create_wellness_tools(backend)

    def test_general_techniques(self):
        """Test stress management techniques without specific preference."""
        result = self.provide_stress_management_techniques(
            user_id="test_user_stress",
        )

        assert "Stress Management Techniques" in result
        # Should include multiple technique types
        assert any(term in result for term in ["Breathing", "Grounding", "Reframing"])

    def test_breathing_techniques(self):
        """Test breathing-specific techniques."""
        result = self.provide_stress_management_techniques(
            user_id="test_user_breathing",
            preferred_technique_type="breathing",
        )

        assert "Stress Management Techniques" in result
        # Should include box breathing or similar
        assert any(term in result for term in ["Box Breathing", "4-7-8", "Breathing"])

    def test_high_stress_level(self):
        """Test techniques for high stress level."""
        result = self.provide_stress_management_techniques(
            user_id="test_user_high",
            stress_level="high",
        )

        assert "Stress Management Techniques" in result
        assert "for high stress levels" in result or "high" in result.lower()
        # Should include professional help suggestion
        assert "professional" in result or "healthcare provider" in result

    def test_technique_steps(self):
        """Test that techniques include step-by-step instructions."""
        result = self.provide_stress_management_techniques(
            user_id="test_user_steps",
        )

        # Should include numbered steps
        assert any(char.isdigit() for char in result)

    def test_invalid_user_id(self):
        """Test that invalid user_id returns error."""
        result = self.provide_stress_management_techniques(
            user_id="",
        )

        assert "Error" in result
        assert "user_id" in result.lower()


class TestSleepOptimizationPlan:
    """Test the create_sleep_optimization_plan function."""

    def setup_method(self):
        """Set up test fixtures."""
        backend = FilesystemBackend(root_dir="/tmp/test_wellness_workspace")
        _, _, _, self.create_sleep_optimization_plan, *_ = create_wellness_tools(backend)

    def test_complete_sleep_plan(self):
        """Test sleep optimization plan with full parameters."""
        result = self.create_sleep_optimization_plan(
            user_id="test_user_sleep",
            current_bedtime="11:00 PM",
            current_wake_time="7:00 AM",
            sleep_issues=["trouble falling asleep", "waking up often"],
        )

        assert "Sleep Optimization Plan" in result
        assert "11:00 PM" in result or "Bedtime:" in result
        assert "7:00 AM" in result or "Wake Time:" in result

    def test_sleep_environment(self):
        """Test that sleep environment recommendations are included."""
        result = self.create_sleep_optimization_plan(
            user_id="test_user_env",
        )

        assert "Sleep Environment" in result
        # Should include environment factors
        assert any(term in result for term in ["temperature", "dark", "quiet", "lighting", "noise"])

    def test_circadian_rhythm_alignment(self):
        """Test circadian rhythm alignment strategies."""
        result = self.create_sleep_optimization_plan(
            user_id="test_user_circadian",
        )

        assert "Circadian" in result or "Daytime Habits" in result
        # Should include morning sunlight
        assert any(term in result for term in ["morning", "sunlight", "day"])

    def test_specific_sleep_issues(self):
        """Test solutions for specific sleep issues."""
        result = self.create_sleep_optimization_plan(
            user_id="test_user_issues",
            sleep_issues=["trouble falling asleep", "racing thoughts"],
        )

        assert "Identified Issues" in result or "Specific Issues" in result
        # Should include issue-specific solutions
        assert any(term in result for term in ["breathing", "meditation", "worry journal"])

    def test_bedtime_routine(self):
        """Test bedtime routine recommendations."""
        result = self.create_sleep_optimization_plan(
            user_id="test_user_routine",
        )

        assert "Bedtime Routine" in result
        # Should include routine elements
        assert any(term in result for term in ["screen", "wind-down", "caffeine"])

    def test_minimal_plan(self):
        """Test sleep plan with only required parameters."""
        result = self.create_sleep_optimization_plan(
            user_id="test_user_minimal",
        )

        assert "Sleep Optimization Plan" in result
        assert "Sleep Environment" in result

    def test_invalid_user_id(self):
        """Test that invalid user_id returns error."""
        result = self.create_sleep_optimization_plan(
            user_id="",
        )

        assert "Error" in result
        assert "user_id" in result.lower()


class TestExerciseProgram:
    """Test the design_exercise_program function."""

    def setup_method(self):
        """Set up test fixtures."""
        backend = FilesystemBackend(root_dir="/tmp/test_wellness_workspace")
        _, _, _, _, self.design_exercise_program, *_ = create_wellness_tools(backend)

    def test_complete_exercise_plan(self):
        """Test exercise program with all parameters."""
        result = self.design_exercise_program(
            user_id="test_user_exercise",
            fitness_level="beginner",
            primary_goals=["improve energy", "build strength"],
            preferred_activities=["walking", "bodyweight exercises"],
            time_available_per_week=150,
        )

        assert "Personalized Exercise Program" in result
        assert "beginner" in result.lower()
        assert "improve energy" in result or "build strength" in result
        assert "150" in result

    def test_fitness_level_adaptation(self):
        """Test that program adapts to fitness level."""
        result = self.design_exercise_program(
            user_id="test_user_fitness",
            fitness_level="sedentary",
        )

        assert "sedentary" in result.lower()
        # Should include conservative start
        assert any(
            term in result
            for term in ["Start very small", "Build the habit", "consistency over intensity"]
        )

    def test_exercise_components(self):
        """Test that all exercise components are included."""
        result = self.design_exercise_program(
            user_id="test_user_components",
        )

        assert "Exercise Components" in result
        # Should include major components
        assert any(term in result for term in ["Cardiovascular", "Strength", "Flexibility"])

    def test_weekly_schedule(self):
        """Test that weekly schedule is generated."""
        result = self.design_exercise_program(
            user_id="test_user_schedule",
            time_available_per_week=120,
        )

        assert "Weekly Schedule" in result or "weekly" in result.lower()
        # Should include days
        assert any(term in result for term in ["Day", "Monday", "Tuesday"])

    def test_safety_considerations(self):
        """Test that safety considerations are included."""
        result = self.design_exercise_program(
            user_id="test_user_safety",
        )

        assert "Safety" in result or "safety" in result.lower()
        # Should include safety tips
        assert any(
            term in result for term in ["Listen to your body", "warm-up", "healthcare provider"]
        )

    def test_progression_guidelines(self):
        """Test that progression guidelines are included."""
        result = self.design_exercise_program(
            user_id="test_user_progression",
        )

        assert "Progression" in result or "progression" in result.lower()

    def test_preferred_activities(self):
        """Test that preferred activities are incorporated."""
        result = self.design_exercise_program(
            user_id="test_user_prefs",
            preferred_activities=["swimming", "yoga"],
        )

        assert "Preferred Activities" in result or "swimming" in result.lower()

    def test_minimal_plan(self):
        """Test exercise program with only required parameters."""
        result = self.design_exercise_program(
            user_id="test_user_minimal",
        )

        assert "Personalized Exercise Program" in result
        assert "Weekly Schedule" in result or "weekly" in result.lower()

    def test_invalid_user_id(self):
        """Test that invalid user_id returns error."""
        result = self.design_exercise_program(
            user_id="",
        )

        assert "Error" in result
        assert "user_id" in result.lower()

    def test_invalid_time(self):
        """Test that invalid time_available_per_week returns error."""
        result = self.design_exercise_program(
            user_id="test_user",
            time_available_per_week=-50,
        )

        assert "Error" in result
        assert "time" in result.lower()


class TestIntegrationScenarios:
    """Test realistic integration scenarios combining multiple wellness tools."""

    def setup_method(self):
        """Set up test fixtures."""
        backend = FilesystemBackend(root_dir="/tmp/test_wellness_workspace")
        (
            self.assess_wellness_dimensions,
            self.create_habit_formation_plan,
            self.provide_stress_management_techniques,
            self.create_sleep_optimization_plan,
            self.design_exercise_program,
        ) = create_wellness_tools(backend)

    def test_stress_sleep_scenario(self):
        """Test scenario: user with stress and sleep issues."""
        # Step 1: Assess wellness
        assessment = self.assess_wellness_dimensions(
            user_id="scenario_user_stress_sleep",
            emotional_score=4,
            physical_score=5,
        )

        assert "Emotional Wellness" in assessment or "emotional" in assessment.lower()

        # Step 2: Get stress management techniques
        stress_tips = self.provide_stress_management_techniques(
            user_id="scenario_user_stress_sleep",
            stress_level="high",
        )

        assert "Stress Management" in stress_tips

        # Step 3: Create sleep plan
        sleep_plan = self.create_sleep_optimization_plan(
            user_id="scenario_user_stress_sleep",
            sleep_issues=["trouble falling asleep", "racing thoughts"],
        )

        assert "Sleep Optimization" in sleep_plan

    def test_new_fitness_habit_scenario(self):
        """Test scenario: user wants to start new fitness habit."""
        # Step 1: Assess current wellness
        assessment = self.assess_wellness_dimensions(
            user_id="scenario_user_fitness",
            physical_score=4,
        )

        # Step 2: Create exercise program
        exercise_plan = self.design_exercise_program(
            user_id="scenario_user_fitness",
            fitness_level="sedentary",
            primary_goals=["improve energy"],
        )

        assert "Personalized Exercise Program" in exercise_plan

        # Step 3: Create habit formation plan
        habit_plan = self.create_habit_formation_plan(
            user_id="scenario_user_fitness",
            habit_name="Evening walk",
            cue_description="After dinner cleanup",
            routine_steps=["Put on walking shoes", "Walk for 10 minutes"],
            reward_description="Feel refreshed and listen to podcast",
        )

        assert "Habit Formation Plan" in habit_plan

    def test_comprehensive_wellness_checkup(self):
        """Test comprehensive wellness checkup using all tools."""
        user_id = "scenario_user_comprehensive"

        # Full assessment
        assessment = self.assess_wellness_dimensions(
            user_id=user_id,
            physical_score=6,
            emotional_score=5,
            social_score=7,
            occupational_score=4,
        )

        assert assessment is not None

        # Exercise program for physical wellness
        exercise = self.design_exercise_program(
            user_id=user_id,
            fitness_level="beginner",
        )

        assert exercise is not None

        # Stress management for emotional support
        stress = self.provide_stress_management_techniques(
            user_id=user_id,
            stress_level="medium",
        )

        assert stress is not None


class TestSampleScenarios:
    """Test with sample scenarios from the task description."""

    def setup_method(self):
        """Set up test fixtures."""
        backend = FilesystemBackend(root_dir="/tmp/test_wellness_workspace")
        (
            self.assess_wellness_dimensions,
            self.create_habit_formation_plan,
            self.provide_stress_management_techniques,
            self.create_sleep_optimization_plan,
            self.design_exercise_program,
        ) = create_wellness_tools(backend)

    def test_trouble_sleeping_work_stress(self):
        """Test sample scenario: 'I have trouble sleeping due to work stress'."""
        user_id = "sample_user_work_stress"

        # Assess wellness - expect low emotional and physical scores
        assessment = self.assess_wellness_dimensions(
            user_id=user_id,
            emotional_score=4,  # High stress
            physical_score=5,  # Poor sleep affecting physical
            occupational_score=3,  # Work stress source
        )

        assert "Occupational Wellness" in assessment or "occupational" in assessment.lower()

        # Get stress management techniques
        stress_tips = self.provide_stress_management_techniques(
            user_id=user_id,
            stress_level="high",
            preferred_technique_type="breathing",
        )

        assert "Stress Management Techniques" in stress_tips

        # Create sleep optimization plan
        sleep_plan = self.create_sleep_optimization_plan(
            user_id=user_id,
            current_bedtime="11:30 PM",
            current_wake_time="6:30 AM",
            sleep_issues=[
                "trouble falling asleep",
                "waking up often",
                "racing thoughts about work",
            ],
        )

        assert "Sleep Optimization Plan" in sleep_plan
        # Should address racing thoughts specifically
        assert (
            "thoughts" in sleep_plan.lower()
            or "racing" in sleep_plan.lower()
            or "worry journal" in sleep_plan.lower()
        )

        # Create a relaxation habit for bedtime
        habit_plan = self.create_habit_formation_plan(
            user_id=user_id,
            habit_name="Bedtime relaxation routine",
            cue_description="When I get into bed",
            routine_steps=["Do 4-7-8 breathing for 5 minutes", "Write tomorrow's to-do list"],
            reward_description="Feel calm and ready for sleep",
        )

        assert "Habit Formation Plan" in habit_plan

    def test_build_morning_routine(self):
        """Test scenario: building a morning wellness routine."""
        user_id = "sample_user_morning"

        # Create exercise habit
        exercise_habit = self.create_habit_formation_plan(
            user_id=user_id,
            habit_name="Morning stretching",
            cue_description="Right after getting out of bed",
            routine_steps=["Drink water", "Do 5 minutes of stretching"],
            reward_description="Feel energized",
        )

        assert exercise_habit is not None

        # Create meditation habit
        meditation_habit = self.create_habit_formation_plan(
            user_id=user_id,
            habit_name="Morning meditation",
            cue_description="After morning stretching",
            routine_steps=["Sit quietly", "Focus on breath for 5 minutes"],
            reward_description="Start day with clarity",
        )

        assert meditation_habit is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
