"""
Tests for Career Coach tools.

This module tests all career-specific tools including skill gap analysis,
career path planning, resume optimization, interview preparation, and
salary benchmark research.
"""

import pytest
import json
from pathlib import Path
from datetime import date, datetime

# Add parent directory to path for imports
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.career_tools import create_career_tools
from deepagents.backends import FilesystemBackend


class TestCareerTools:
    """Test suite for career coach tools."""

    def setup_method(self):
        """Setup test fixtures before each test."""
        # Create a mock FilesystemBackend
        self.backend = FilesystemBackend(root_dir="/tmp/test_career_workspace")
        # Create career tools with mock backend
        self.career_tools = create_career_tools(backend=self.backend)

    # ========================================================================
    # Test analyze_skill_gap
    # ========================================================================

    def test_analyze_skill_gap_basic(self):
        """Test basic skill gap analysis functionality."""
        analyze_skill_gap = self.career_tools[0]
        result = analyze_skill_gap.invoke(
            {
                "user_id": "test_user",
                "current_skills": ["Python", "SQL"],
                "target_role": "Data Scientist",
            }
        )

        assert isinstance(result, str)
        assert "Skill Gap Analysis" in result
        assert "Data Scientist" in result

    def test_analyze_skill_gap_with_experience_level(self):
        """Test skill gap analysis with experience level."""
        analyze_skill_gap = self.career_tools[0]
        result = analyze_skill_gap.invoke(
            {
                "user_id": "test_user",
                "current_skills": ["Marketing", "Content Writing"],
                "target_role": "Data Scientist",
                "experience_level": "entry",
            }
        )

        assert isinstance(result, str)
        assert "Data Scientist" in result
        assert "entry" in result.lower()

    def test_analyze_skill_gap_invalid_user_id(self):
        """Test skill gap analysis with invalid user ID."""
        analyze_skill_gap = self.career_tools[0]
        result = analyze_skill_gap.invoke(
            {"user_id": "", "current_skills": ["Python"], "target_role": "Data Scientist"}
        )

        assert "Error" in result
        assert "user_id must be a non-empty string" in result

    def test_analyze_skill_gap_invalid_skills(self):
        """Test skill gap analysis with invalid skills."""
        analyze_skill_gap = self.career_tools[0]
        result = analyze_skill_gap.invoke(
            {"user_id": "test_user", "current_skills": [], "target_role": "Data Scientist"}
        )

        assert "Error" in result
        assert "current_skills must be a non-empty list" in result

    def test_analyze_skill_gap_invalid_target_role(self):
        """Test skill gap analysis with invalid target role."""
        analyze_skill_gap = self.career_tools[0]
        result = analyze_skill_gap.invoke(
            {"user_id": "test_user", "current_skills": ["Python"], "target_role": ""}
        )

        assert "Error" in result
        assert "target_role must be a non-empty string" in result

    # ========================================================================
    # Test create_career_path_plan
    # ========================================================================

    def test_create_career_path_plan_basic(self):
        """Test basic career path plan creation."""
        create_career_path_plan = self.career_tools[1]
        result = create_career_path_plan.invoke(
            {
                "user_id": "test_user",
                "current_role": "Marketing Coordinator",
                "target_role": "Data Scientist",
                "timeline_years": 3,
            }
        )

        assert isinstance(result, str)
        assert "Career Path Plan Created" in result
        assert "Marketing Coordinator" in result
        assert "Data Scientist" in result

    def test_create_career_path_plan_one_year(self):
        """Test career path plan with 1 year timeline."""
        create_career_path_plan = self.career_tools[1]
        result = create_career_path_plan.invoke(
            {
                "user_id": "test_user",
                "current_role": "Analyst",
                "target_role": "Senior Analyst",
                "timeline_years": 1,
            }
        )

        assert isinstance(result, str)
        assert "Career Path Plan Created" in result

    def test_create_career_path_plan_five_years(self):
        """Test career path plan with 5 year timeline."""
        create_career_path_plan = self.career_tools[1]
        result = create_career_path_plan.invoke(
            {
                "user_id": "test_user",
                "current_role": "Junior Developer",
                "target_role": "Engineering Manager",
                "timeline_years": 5,
            }
        )

        assert isinstance(result, str)
        assert "Career Path Plan Created" in result

    def test_create_career_path_plan_invalid_user_id(self):
        """Test career path plan with invalid user ID."""
        create_career_path_plan = self.career_tools[1]
        result = create_career_path_plan.invoke(
            {"user_id": "", "current_role": "Analyst", "target_role": "Senior Analyst"}
        )

        assert "Error" in result
        assert "user_id must be a non-empty string" in result

    def test_create_career_path_plan_invalid_current_role(self):
        """Test career path plan with invalid current role."""
        create_career_path_plan = self.career_tools[1]
        result = create_career_path_plan.invoke(
            {"user_id": "test_user", "current_role": "", "target_role": "Senior Analyst"}
        )

        assert "Error" in result
        assert "current_role must be a non-empty string" in result

    def test_create_career_path_plan_invalid_target_role(self):
        """Test career path plan with invalid target role."""
        create_career_path_plan = self.career_tools[1]
        result = create_career_path_plan.invoke(
            {"user_id": "test_user", "current_role": "Analyst", "target_role": ""}
        )

        assert "Error" in result
        assert "target_role must be a non-empty string" in result

    def test_create_career_path_plan_invalid_timeline(self):
        """Test career path plan with invalid timeline."""
        create_career_path_plan = self.career_tools[1]
        result = create_career_path_plan.invoke(
            {
                "user_id": "test_user",
                "current_role": "Analyst",
                "target_role": "Senior Analyst",
                "timeline_years": 15,
            }
        )

        assert "Error" in result
        assert "timeline_years must be between 1 and 10" in result

    # ========================================================================
    # Test optimize_resume
    # ========================================================================

    def test_optimize_resume_basic(self):
        """Test basic resume optimization."""
        optimize_resume = self.career_tools[2]
        result = optimize_resume.invoke({"user_id": "test_user", "target_role": "Data Scientist"})

        assert isinstance(result, str)
        assert "Resume Optimization" in result
        assert "Data Scientist" in result

    def test_optimize_resume_with_experience(self):
        """Test resume optimization with experience summary."""
        optimize_resume = self.career_tools[2]
        result = optimize_resume.invoke(
            {
                "user_id": "test_user",
                "target_role": "Data Scientist",
                "current_experience_summary": "5 years in marketing",
            }
        )

        assert isinstance(result, str)
        assert "Resume Optimization" in result
        assert "5 years in marketing" in result

    def test_optimize_resume_invalid_user_id(self):
        """Test resume optimization with invalid user ID."""
        optimize_resume = self.career_tools[2]
        result = optimize_resume.invoke({"user_id": "", "target_role": "Data Scientist"})

        assert "Error" in result
        assert "user_id must be a non-empty string" in result

    def test_optimize_resume_invalid_target_role(self):
        """Test resume optimization with invalid target role."""
        optimize_resume = self.career_tools[2]
        result = optimize_resume.invoke({"user_id": "test_user", "target_role": ""})

        assert "Error" in result
        assert "target_role must be a non-empty string" in result

    # ========================================================================
    # Test generate_interview_prep
    # ========================================================================

    def test_generate_interview_prep_basic(self):
        """Test basic interview preparation generation."""
        generate_interview_prep = self.career_tools[3]
        result = generate_interview_prep.invoke(
            {"user_id": "test_user", "target_role": "Data Scientist"}
        )

        assert isinstance(result, str)
        assert "Interview Preparation Guide" in result
        assert "Data Scientist" in result

    def test_generate_interview_prep_with_company_type(self):
        """Test interview preparation with company type."""
        generate_interview_prep = self.career_tools[3]
        result = generate_interview_prep.invoke(
            {"user_id": "test_user", "target_role": "Data Scientist", "company_type": "tech"}
        )

        assert isinstance(result, str)
        assert "Interview Preparation Guide" in result

    def test_generate_interview_prep_invalid_user_id(self):
        """Test interview preparation with invalid user ID."""
        generate_interview_prep = self.career_tools[3]
        result = generate_interview_prep.invoke({"user_id": "", "target_role": "Data Scientist"})

        assert "Error" in result
        assert "user_id must be a non-empty string" in result

    def test_generate_interview_prep_invalid_target_role(self):
        """Test interview preparation with invalid target role."""
        generate_interview_prep = self.career_tools[3]
        result = generate_interview_prep.invoke({"user_id": "test_user", "target_role": ""})

        assert "Error" in result
        assert "target_role must be a non-empty string" in result

    # ========================================================================
    # Test research_salary_benchmarks
    # ========================================================================

    def test_research_salary_benchmarks_basic(self):
        """Test basic salary benchmark research."""
        research_salary_benchmarks = self.career_tools[4]
        result = research_salary_benchmarks.invoke(
            {"user_id": "test_user", "target_role": "Data Scientist"}
        )

        assert isinstance(result, str)
        assert "Salary Benchmark" in result
        assert "Data Scientist" in result

    def test_research_salary_benchmarks_with_location(self):
        """Test salary benchmark research with location."""
        research_salary_benchmarks = self.career_tools[4]
        result = research_salary_benchmarks.invoke(
            {"user_id": "test_user", "target_role": "Data Scientist", "location": "San Francisco"}
        )

        assert isinstance(result, str)
        assert "Salary Benchmark" in result
        assert "San Francisco" in result

    def test_research_salary_benchmarks_with_experience(self):
        """Test salary benchmark research with experience level."""
        research_salary_benchmarks = self.career_tools[4]
        result = research_salary_benchmarks.invoke(
            {"user_id": "test_user", "target_role": "Data Scientist", "experience_level": "senior"}
        )

        assert isinstance(result, str)
        assert "Salary Benchmark" in result
        assert "Senior" in result

    def test_research_salary_benchmarks_invalid_user_id(self):
        """Test salary benchmark research with invalid user ID."""
        research_salary_benchmarks = self.career_tools[4]
        result = research_salary_benchmarks.invoke({"user_id": "", "target_role": "Data Scientist"})

        assert "Error" in result
        assert "user_id must be a non-empty string" in result

    def test_research_salary_benchmarks_invalid_target_role(self):
        """Test salary benchmark research with invalid target role."""
        research_salary_benchmarks = self.career_tools[4]
        result = research_salary_benchmarks.invoke({"user_id": "test_user", "target_role": ""})

        assert "Error" in result
        assert "target_role must be a non-empty string" in result


class TestCareerToolsIntegration:
    """Integration tests for career tools working together."""

    def setup_method(self):
        """Setup test fixtures before each test."""
        # Create a mock FilesystemBackend
        self.backend = FilesystemBackend(root_dir="/tmp/test_career_integration")
        # Create career tools with mock backend
        self.career_tools = create_career_tools(backend=self.backend)

    def test_complete_career_coaching_workflow(self):
        """Test a complete career coaching workflow using multiple tools."""
        user_id = "integration_test_user"
        current_skills = ["Marketing", "Content Writing"]
        target_role = "Data Scientist"

        # Step 1: Analyze skill gaps
        analyze_skill_gap = self.career_tools[0]
        gap_result = analyze_skill_gap.invoke(
            {"user_id": user_id, "current_skills": current_skills, "target_role": target_role}
        )
        assert "Skill Gap Analysis" in gap_result

        # Step 2: Create career path plan
        create_career_path_plan = self.career_tools[1]
        plan_result = create_career_path_plan.invoke(
            {
                "user_id": user_id,
                "current_role": "Marketing Coordinator",
                "target_role": target_role,
                "timeline_years": 3,
            }
        )
        assert "Career Path Plan Created" in plan_result

        # Step 3: Get resume optimization advice
        optimize_resume = self.career_tools[2]
        resume_result = optimize_resume.invoke({"user_id": user_id, "target_role": target_role})
        assert "Resume Optimization" in resume_result

        # Step 4: Get interview preparation
        generate_interview_prep = self.career_tools[3]
        prep_result = generate_interview_prep.invoke(
            {"user_id": user_id, "target_role": target_role}
        )
        assert "Interview Preparation Guide" in prep_result

        # Step 5: Get salary benchmarks
        research_salary_benchmarks = self.career_tools[4]
        salary_result = research_salary_benchmarks.invoke(
            {"user_id": user_id, "target_role": target_role}
        )
        assert "Salary Benchmark" in salary_result

    def test_career_transition_scenario(self):
        """Test a realistic career transition scenario."""
        user_id = "transition_user"

        # User wants to transition from marketing to data science
        gap_result = self.career_tools[0].invoke(
            {
                "user_id": user_id,
                "current_skills": ["Marketing", "Social Media", "Content Creation"],
                "target_role": "Data Scientist",
                "experience_level": "entry",
            }
        )
        assert "Data Scientist" in gap_result

        # Create a 3-year transition plan
        plan_result = self.career_tools[1].invoke(
            {
                "user_id": user_id,
                "current_role": "Marketing Manager",
                "target_role": "Data Scientist",
                "timeline_years": 3,
            }
        )
        assert "Career Path Plan Created" in plan_result

        # Get tailored resume advice
        resume_result = self.career_tools[2].invoke(
            {
                "user_id": user_id,
                "target_role": "Data Scientist",
                "current_experience_summary": "7 years in marketing, transitioning to data science",
            }
        )
        assert "Resume Optimization" in resume_result


# Test fixtures for pytest
@pytest.fixture
def career_tools():
    """Fixture providing career tools instance."""
    backend = FilesystemBackend(root_dir="/tmp/test_career_fixture")
    return create_career_tools(backend=backend)


def test_import_module():
    """Test that the career tools module can be imported."""
    from src.tools.career_tools import create_career_tools

    assert callable(create_career_tools)


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
