"""
Comprehensive test suite for individual specialist agent functionality.

This module tests each specialist agent (Career, Relationship, Finance, Wellness)
in isolation to verify:
1. Single-domain agent functionality
2. Tool integration per specialist
3. Output quality and format
4. Domain expertise boundaries
5. Memory and context tool integration
6. Error handling scenarios

Based on multi-agent testing best practices from industry research.

Test Scenarios:
- Career: "I want to transition from marketing to data science"
- Relationship: "I struggle with setting boundaries at work"
- Finance: "I want to save for a house down payment in 3 years"
- Wellness: "I have trouble sleeping due to work stress"

Run with: pytest tests/test_specialist_agents.py -v
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from deepagents.backends import FilesystemBackend

from src.agents import (
    get_career_specialist,
    get_finance_specialist,
    get_relationship_specialist,
    get_wellness_specialist,
)
from src.memory import create_memory_store
from src.tools.career_tools import create_career_tools
from src.tools.context_tools import create_context_tools
from src.tools.finance_tools import create_finance_tools
from src.tools.memory_tools import create_memory_tools
from src.tools.relationship_tools import create_relationship_tools
from src.tools.wellness_tools import create_wellness_tools

# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def memory_store():
    """Create a test memory store for all tests."""
    return create_memory_store()


@pytest.fixture
def backend(tmp_path):
    """Create a FilesystemBackend for testing."""
    return FilesystemBackend(root_dir=str(tmp_path / "workspace"))


@pytest.fixture
def memory_tools(memory_store):
    """Create all memory tools."""
    return create_memory_tools(memory_store)


@pytest.fixture
def context_tools(backend):
    """Create all context tools."""
    return create_context_tools(backend=backend)


@pytest.fixture
def career_specialist_with_tools(memory_tools, context_tools, backend):
    """Create Career Specialist with all required tools."""
    career_specific = create_career_tools(backend=backend)
    specialist = get_career_specialist()
    specialist["tools"] = list(memory_tools) + list(context_tools) + list(career_specific)
    return specialist


@pytest.fixture
def relationship_specialist_with_tools(memory_tools, context_tools, backend):
    """Create Relationship Specialist with all required tools."""
    relationship_specific = create_relationship_tools(backend=backend)
    specialist = get_relationship_specialist()
    specialist["tools"] = list(memory_tools) + list(context_tools) + list(relationship_specific)
    return specialist


@pytest.fixture
def finance_specialist_with_tools(memory_tools, context_tools, backend):
    """Create Finance Specialist with all required tools."""
    finance_specific = create_finance_tools(backend=backend)
    specialist = get_finance_specialist()
    specialist["tools"] = list(memory_tools) + list(context_tools) + list(finance_specific)
    return specialist


@pytest.fixture
def wellness_specialist_with_tools(memory_tools, context_tools, backend):
    """Create Wellness Specialist with all required tools."""
    wellness_specific = create_wellness_tools(backend=backend)
    specialist = get_wellness_specialist()
    specialist["tools"] = list(memory_tools) + list(context_tools) + list(wellness_specific)
    return specialist


# ============================================================================
# Test Career Specialist
# ============================================================================


class TestCareerSpecialist:
    """Test suite for Career Specialist agent."""

    def test_career_specialist_configuration(self, career_specialist_with_tools):
        """Verify Career Specialist is properly configured."""
        specialist = career_specialist_with_tools

        assert specialist["name"] == "career-specialist"
        assert len(specialist["system_prompt"]) > 3000, "System prompt should be comprehensive"
        assert specialist["model"] == "openai:glm-4.7"

    def test_career_specialist_has_required_tools(
        self, career_specialist_with_tools, memory_tools, context_tools
    ):
        """Verify Career Specialist has all required tools."""
        specialist = career_specialist_with_tools

        tool_names = [
            tool.name if hasattr(tool, "name") else tool.__name__ for tool in specialist["tools"]
        ]

        # Should have memory tools
        expected_memory_tools = [
            "get_user_profile",
            "save_user_preference",
            "update_milestone",
            "get_progress_history",
        ]
        for tool_name in expected_memory_tools:
            assert any(tool_name in t for t in tool_names), f"Missing memory tool: {tool_name}"

        # Should have context tools
        expected_context_tools = ["save_assessment", "get_active_plan"]
        for tool_name in expected_context_tools:
            assert any(tool_name in t for t in tool_names), f"Missing context tool: {tool_name}"

        # Should have career-specific tools
        expected_career_tools = ["analyze_skill_gap", "create_career_path_plan"]
        for tool_name in expected_career_tools:
            assert any(tool_name in t for t in tool_names), f"Missing career tool: {tool_name}"

    def test_career_specialist_no_planning_tools(self, career_specialist_with_tools):
        """Verify Career Specialist does NOT have planning tools."""
        specialist = career_specialist_with_tools
        tool_names = [
            tool.name if hasattr(tool, "name") else tool.__name__ for tool in specialist["tools"]
        ]

        planning_tools = ["write_todos", "update_todo", "list_todos"]
        for tool_name in planning_tools:
            assert not any(tool_name in t for t in tool_names), (
                f"Career specialist should NOT have planning tool: {tool_name}"
            )

    def test_career_specialist_domain_expertise(self, career_specialist_with_tools):
        """Verify Career Specialist system prompt contains domain expertise keywords."""
        specialist = career_specialist_with_tools
        prompt = specialist["system_prompt"].lower()

        keywords = [
            "career",
            "resume",
            "interview",
            "skill gap",
            "career path",
            "negotiation",
        ]

        for keyword in keywords:
            assert keyword in prompt, f"Career specialist prompt should mention '{keyword}'"

    def test_career_specialist_domain_boundaries(self, career_specialist_with_tools):
        """Verify Career Specialist respects domain boundaries."""
        specialist = career_specialist_with_tools
        prompt = specialist["system_prompt"].lower()

        # Should acknowledge limits and recommend professionals for non-career issues
        assert "medical" in prompt or "health" in prompt, "Should acknowledge health boundaries"
        assert "legal" in prompt or "attorney" in prompt, "Should acknowledge legal boundaries"

    def test_career_specialist_tool_functionality(self, career_specialist_with_tools):
        """Test that Career Specialist tools are functional."""
        specialist = career_specialist_with_tools

        # Find the analyze_skill_gap tool
        skill_gap_tool = None
        for tool in specialist["tools"]:
            name = tool.name if hasattr(tool, "name") else str(tool)
            if "skill_gap" in name:
                skill_gap_tool = tool
                break

        assert skill_gap_tool is not None, "Career Specialist should have analyze_skill_gap tool"

        # Test the tool
        result = skill_gap_tool.invoke(
            {
                "user_id": "test_user",
                "current_skills": ["Python", "SQL"],
                "target_role": "Data Scientist",
            }
        )

        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0


# ============================================================================
# Test Relationship Specialist
# ============================================================================


class TestRelationshipSpecialist:
    """Test suite for Relationship Specialist agent."""

    def test_relationship_specialist_configuration(self, relationship_specialist_with_tools):
        """Verify Relationship Specialist is properly configured."""
        specialist = relationship_specialist_with_tools

        assert specialist["name"] == "relationship-specialist"
        assert len(specialist["system_prompt"]) > 3000, "System prompt should be comprehensive"
        assert specialist["model"] == "openai:glm-4.7"

    def test_relationship_specialist_has_required_tools(
        self, relationship_specialist_with_tools, memory_tools, context_tools
    ):
        """Verify Relationship Specialist has all required tools."""
        specialist = relationship_specialist_with_tools
        tool_names = [
            tool.name if hasattr(tool, "name") else tool.__name__ for tool in specialist["tools"]
        ]

        # Should have memory tools
        expected_memory_tools = ["get_user_profile", "save_user_preference"]
        for tool_name in expected_memory_tools:
            assert any(tool_name in t for t in tool_names), f"Missing memory tool: {tool_name}"

        # Should have context tools
        expected_context_tools = ["save_assessment"]
        for tool_name in expected_context_tools:
            assert any(tool_name in t for t in tool_names), f"Missing context tool: {tool_name}"

        # Should have relationship-specific tools
        expected_relationship_tools = [
            "analyze_communication_style",
            "create_boundary_setting_plan",
        ]
        for tool_name in expected_relationship_tools:
            assert any(tool_name in t for t in tool_names), (
                f"Missing relationship tool: {tool_name}"
            )

    def test_relationship_specialist_no_planning_tools(self, relationship_specialist_with_tools):
        """Verify Relationship Specialist does NOT have planning tools."""
        specialist = relationship_specialist_with_tools
        tool_names = [
            tool.name if hasattr(tool, "name") else tool.__name__ for tool in specialist["tools"]
        ]

        planning_tools = ["write_todos", "update_todo", "list_todos"]
        for tool_name in planning_tools:
            assert not any(tool_name in t for t in tool_names), (
                f"Relationship specialist should NOT have planning tool: {tool_name}"
            )

    def test_relationship_specialist_domain_expertise(self, relationship_specialist_with_tools):
        """Verify Relationship Specialist system prompt contains domain expertise keywords."""
        specialist = relationship_specialist_with_tools
        prompt = specialist["system_prompt"].lower()

        keywords = [
            "relationship",
            "communication",
            "boundary",
            "conflict",
            "social connection",
            "emotional intelligence",
        ]

        for keyword in keywords:
            assert keyword in prompt, f"Relationship specialist prompt should mention '{keyword}'"

    def test_relationship_specialist_domain_boundaries(self, relationship_specialist_with_tools):
        """Verify Relationship Specialist respects domain boundaries."""
        specialist = relationship_specialist_with_tools
        prompt = specialist["system_prompt"].lower()

        # Should acknowledge limits and recommend professionals for serious issues
        assert "therapy" in prompt or "counseling" in prompt, (
            "Should acknowledge therapy boundaries"
        )
        assert "safety" in prompt or "abuse" in prompt, "Should acknowledge safety boundaries"

    def test_relationship_specialist_tool_functionality(self, relationship_specialist_with_tools):
        """Test that Relationship Specialist tools are functional."""
        specialist = relationship_specialist_with_tools

        # Find the create_boundary_setting_plan tool
        boundary_tool = None
        for tool in specialist["tools"]:
            name = tool.name if hasattr(tool, "name") else str(tool)
            if "boundary" in name:
                boundary_tool = tool
                break

        assert boundary_tool is not None, (
            "Relationship Specialist should have create_boundary_setting_plan tool"
        )

        # Test the tool with correct parameters
        result = boundary_tool.invoke(
            {
                "user_id": "test_user",
                "boundary_areas": ["work hours", "personal time"],
                "relationship_type": "professional",
            }
        )

        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0


# ============================================================================
# Test Finance Specialist
# ============================================================================


class TestFinanceSpecialist:
    """Test suite for Finance Specialist agent."""

    def test_finance_specialist_configuration(self, finance_specialist_with_tools):
        """Verify Finance Specialist is properly configured."""
        specialist = finance_specialist_with_tools

        assert specialist["name"] == "finance-specialist"
        assert len(specialist["system_prompt"]) > 3000, "System prompt should be comprehensive"
        assert specialist["model"] == "openai:glm-4.7"

    def test_finance_specialist_has_required_tools(
        self, finance_specialist_with_tools, memory_tools, context_tools
    ):
        """Verify Finance Specialist has all required tools."""
        specialist = finance_specialist_with_tools
        tool_names = [
            tool.name if hasattr(tool, "name") else tool.__name__ for tool in specialist["tools"]
        ]

        # Should have memory tools
        expected_memory_tools = ["get_user_profile", "save_user_preference"]
        for tool_name in expected_memory_tools:
            assert any(tool_name in t for t in tool_names), f"Missing memory tool: {tool_name}"

        # Should have context tools
        expected_context_tools = ["save_assessment"]
        for tool_name in expected_context_tools:
            assert any(tool_name in t for t in tool_names), f"Missing context tool: {tool_name}"

        # Should have finance-specific tools
        expected_finance_tools = ["create_budget_analyzer", "calculate_emergency_fund_target"]
        for tool_name in expected_finance_tools:
            assert any(tool_name in t for t in tool_names), f"Missing finance tool: {tool_name}"

    def test_finance_specialist_no_planning_tools(self, finance_specialist_with_tools):
        """Verify Finance Specialist does NOT have planning tools."""
        specialist = finance_specialist_with_tools
        tool_names = [
            tool.name if hasattr(tool, "name") else tool.__name__ for tool in specialist["tools"]
        ]

        planning_tools = ["write_todos", "update_todo", "list_todos"]
        for tool_name in planning_tools:
            assert not any(tool_name in t for t in tool_names), (
                f"Finance specialist should NOT have planning tool: {tool_name}"
            )

    def test_finance_specialist_domain_expertise(self, finance_specialist_with_tools):
        """Verify Finance Specialist system prompt contains domain expertise keywords."""
        specialist = finance_specialist_with_tools
        prompt = specialist["system_prompt"].lower()

        keywords = [
            "budget",
            "debt",
            "emergency fund",
            "saving",
            "investment",
            "financial goal",
        ]

        for keyword in keywords:
            assert keyword in prompt, f"Finance specialist prompt should mention '{keyword}'"

    def test_finance_specialist_domain_boundaries(self, finance_specialist_with_tools):
        """Verify Finance Specialist respects domain boundaries."""
        specialist = finance_specialist_with_tools
        prompt = specialist["system_prompt"].lower()

        # Should acknowledge limits and provide disclaimers
        assert "not professional advice" in prompt or "educational information only" in prompt, (
            "Should include disclaimer about not providing professional advice"
        )
        assert "financial planner" in prompt or "cpa" in prompt, (
            "Should acknowledge when professional help is needed"
        )

    def test_finance_specialist_tool_functionality(self, finance_specialist_with_tools):
        """Test that Finance Specialist tools are functional."""
        specialist = finance_specialist_with_tools

        # Find the calculate_emergency_fund_target tool
        emergency_tool = None
        for tool in specialist["tools"]:
            name = tool.name if hasattr(tool, "name") else str(tool)
            if "emergency" in name:
                emergency_tool = tool
                break

        assert emergency_tool is not None, (
            "Finance Specialist should have calculate_emergency_fund_target tool"
        )

        # Test the tool with correct parameters
        result = emergency_tool.invoke(
            {
                "user_id": "test_user",
                "monthly_essential_expenses": 3000,
                "dependents": 0,
                "job_stability": "average",
                "home_owner": False,
            }
        )

        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0


# ============================================================================
# Test Wellness Specialist
# ============================================================================


class TestWellnessSpecialist:
    """Test suite for Wellness Specialist agent."""

    def test_wellness_specialist_configuration(self, wellness_specialist_with_tools):
        """Verify Wellness Specialist is properly configured."""
        specialist = wellness_specialist_with_tools

        assert specialist["name"] == "wellness-specialist"
        assert len(specialist["system_prompt"]) > 3000, "System prompt should be comprehensive"
        assert specialist["model"] == "openai:glm-4.7"

    def test_wellness_specialist_has_required_tools(
        self, wellness_specialist_with_tools, memory_tools, context_tools
    ):
        """Verify Wellness Specialist has all required tools."""
        specialist = wellness_specialist_with_tools
        tool_names = [
            tool.name if hasattr(tool, "name") else tool.__name__ for tool in specialist["tools"]
        ]

        # Should have memory tools
        expected_memory_tools = ["get_user_profile", "save_user_preference"]
        for tool_name in expected_memory_tools:
            assert any(tool_name in t for t in tool_names), f"Missing memory tool: {tool_name}"

        # Should have context tools
        expected_context_tools = ["save_assessment"]
        for tool_name in expected_context_tools:
            assert any(tool_name in t for t in tool_names), f"Missing context tool: {tool_name}"

        # Should have wellness-specific tools
        expected_wellness_tools = ["assess_wellness_dimensions", "create_habit_formation_plan"]
        for tool_name in expected_wellness_tools:
            assert any(tool_name in t for t in tool_names), f"Missing wellness tool: {tool_name}"

    def test_wellness_specialist_no_planning_tools(self, wellness_specialist_with_tools):
        """Verify Wellness Specialist does NOT have planning tools."""
        specialist = wellness_specialist_with_tools
        tool_names = [
            tool.name if hasattr(tool, "name") else tool.__name__ for tool in specialist["tools"]
        ]

        planning_tools = ["write_todos", "update_todo", "list_todos"]
        for tool_name in planning_tools:
            assert not any(tool_name in t for t in tool_names), (
                f"Wellness specialist should NOT have planning tool: {tool_name}"
            )

    def test_wellness_specialist_domain_expertise(self, wellness_specialist_with_tools):
        """Verify Wellness Specialist system prompt contains domain expertise keywords."""
        specialist = wellness_specialist_with_tools
        prompt = specialist["system_prompt"].lower()

        keywords = [
            "wellness",
            "fitness",
            "sleep",
            "stress management",
            "habit formation",
            "work-life balance",
        ]

        for keyword in keywords:
            assert keyword in prompt, f"Wellness specialist prompt should mention '{keyword}'"

    def test_wellness_specialist_domain_boundaries(self, wellness_specialist_with_tools):
        """Verify Wellness Specialist respects domain boundaries."""
        specialist = wellness_specialist_with_tools
        prompt = specialist["system_prompt"].lower()

        # Should acknowledge limits and provide disclaimers
        assert "not medical advice" in prompt or "general wellness guidance only" in prompt, (
            "Should include disclaimer about not providing medical advice"
        )
        assert "medical professional" in prompt or "healthcare provider" in prompt, (
            "Should acknowledge when professional medical help is needed"
        )

    def test_wellness_specialist_tool_functionality(self, wellness_specialist_with_tools):
        """Test that Wellness Specialist tools are functional."""
        specialist = wellness_specialist_with_tools

        # Find the create_sleep_optimization_plan tool
        sleep_tool = None
        for tool in specialist["tools"]:
            name = tool.name if hasattr(tool, "name") else str(tool)
            if "sleep" in name:
                sleep_tool = tool
                break

        assert sleep_tool is not None, (
            "Wellness Specialist should have create_sleep_optimization_plan tool"
        )

        # Test the tool
        result = sleep_tool.invoke(
            {"user_id": "test_user", "sleep_issue": "trouble falling asleep due to work stress"}
        )

        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0


# ============================================================================
# Test Cross-Specialist Consistency
# ============================================================================


class TestCrossSpecialistConsistency:
    """Test suite for cross-specialist consistency and boundaries."""

    def test_all_specialists_use_same_model(
        self,
        career_specialist_with_tools,
        relationship_specialist_with_tools,
        finance_specialist_with_tools,
        wellness_specialist_with_tools,
    ):
        """Verify all specialists use the same model configuration."""
        assert career_specialist_with_tools["model"] == relationship_specialist_with_tools["model"]
        assert finance_specialist_with_tools["model"] == wellness_specialist_with_tools["model"]

    def test_all_specialists_have_memory_access(
        self,
        career_specialist_with_tools,
        relationship_specialist_with_tools,
        finance_specialist_with_tools,
        wellness_specialist_with_tools,
    ):
        """Verify all specialists have access to memory tools."""
        for specialist in [
            career_specialist_with_tools,
            relationship_specialist_with_tools,
            finance_specialist_with_tools,
            wellness_specialist_with_tools,
        ]:
            tool_names = [
                tool.name if hasattr(tool, "name") else str(tool) for tool in specialist["tools"]
            ]
            assert any("get_user_profile" in t for t in tool_names), (
                f"{specialist['name']} should have get_user_profile tool"
            )

    def test_all_specialists_have_context_access(
        self,
        career_specialist_with_tools,
        relationship_specialist_with_tools,
        finance_specialist_with_tools,
        wellness_specialist_with_tools,
    ):
        """Verify all specialists have access to context tools."""
        for specialist in [
            career_specialist_with_tools,
            relationship_specialist_with_tools,
            finance_specialist_with_tools,
            wellness_specialist_with_tools,
        ]:
            tool_names = [
                tool.name if hasattr(tool, "name") else str(tool) for tool in specialist["tools"]
            ]
            assert any("save_assessment" in t for t in tool_names), (
                f"{specialist['name']} should have save_assessment tool"
            )

    def test_no_specialist_has_planning_tools(
        self,
        career_specialist_with_tools,
        relationship_specialist_with_tools,
        finance_specialist_with_tools,
        wellness_specialist_with_tools,
    ):
        """Verify NO specialist has planning tools (coordinator only)."""
        for specialist in [
            career_specialist_with_tools,
            relationship_specialist_with_tools,
            finance_specialist_with_tools,
            wellness_specialist_with_tools,
        ]:
            tool_names = [
                tool.name if hasattr(tool, "name") else str(tool) for tool in specialist["tools"]
            ]
            planning_tools = ["write_todos", "update_todo", "list_todos"]
            for planning_tool in planning_tools:
                assert not any(planning_tool in t for t in tool_names), (
                    f"{specialist['name']} should NOT have planning tool: {planning_tool}"
                )

    def test_each_specialist_has_domain_specific_tools(
        self,
        career_specialist_with_tools,
        relationship_specialist_with_tools,
        finance_specialist_with_tools,
        wellness_specialist_with_tools,
    ):
        """Verify each specialist has their domain-specific tools."""
        # Career should have career-specific tools
        career_names = [
            tool.name if hasattr(tool, "name") else str(tool)
            for tool in career_specialist_with_tools["tools"]
        ]
        assert any("career" in t.lower() or "skill_gap" in t for t in career_names), (
            "Career specialist should have career-specific tools"
        )

        # Relationship should have relationship-specific tools
        rel_names = [
            tool.name if hasattr(tool, "name") else str(tool)
            for tool in relationship_specialist_with_tools["tools"]
        ]
        assert any(
            "relationship" in t.lower() or "communication" in t or "boundary" in t
            for t in rel_names
        ), "Relationship specialist should have relationship-specific tools"

        # Finance should have finance-specific tools
        fin_names = [
            tool.name if hasattr(tool, "name") else str(tool)
            for tool in finance_specialist_with_tools["tools"]
        ]
        assert any("budget" in t.lower() or "debt" in t or "emergency" in t for t in fin_names), (
            "Finance specialist should have finance-specific tools"
        )

        # Wellness should have wellness-specific tools
        well_names = [
            tool.name if hasattr(tool, "name") else str(tool)
            for tool in wellness_specialist_with_tools["tools"]
        ]
        assert any("wellness" in t.lower() or "habit" in t or "sleep" in t for t in well_names), (
            "Wellness specialist should have wellness-specific tools"
        )


# ============================================================================
# Test Memory Integration
# ============================================================================


class TestSpecialistMemoryIntegration:
    """Test suite for memory tool integration across specialists."""

    def test_career_specialist_memory_integration(self, career_specialist_with_tools, memory_store):
        """Test Career Specialist can use memory tools."""
        specialist = career_specialist_with_tools

        # Find get_user_profile tool
        profile_tool = None
        for tool in specialist["tools"]:
            name = tool.name if hasattr(tool, "name") else str(tool)
            if "get_user_profile" in name:
                profile_tool = tool
                break

        assert profile_tool is not None, "Should have get_user_profile tool"

        # Test saving and retrieving user profile using MemoryManager
        from src.memory import MemoryManager, UserProfile

        memory_manager = MemoryManager(memory_store)
        # Create a profile with valid parameters
        test_profile = UserProfile(
            user_id="test_career", name="Test User", occupation="Marketing Manager"
        )
        memory_manager.save_profile(test_profile)

        result = profile_tool.invoke({"user_id": "test_career"})
        assert result is not None
        assert isinstance(result, str)

    def test_relationship_specialist_memory_integration(
        self, relationship_specialist_with_tools, memory_store
    ):
        """Test Relationship Specialist can use memory tools."""
        specialist = relationship_specialist_with_tools

        # Find save_user_preference tool
        pref_tool = None
        for tool in specialist["tools"]:
            name = tool.name if hasattr(tool, "name") else str(tool)
            if "save_user_preference" in name:
                pref_tool = tool
                break

        assert pref_tool is not None, "Should have save_user_preference tool"

        # Test saving preference
        result = pref_tool.invoke(
            {"user_id": "test_rel", "key": "communication_style", "value": "direct"}
        )
        assert result is not None

    def test_finance_specialist_memory_integration(
        self, finance_specialist_with_tools, memory_store
    ):
        """Test Finance Specialist can use memory tools."""
        specialist = finance_specialist_with_tools

        # Find update_milestone tool
        milestone_tool = None
        for tool in specialist["tools"]:
            name = tool.name if hasattr(tool, "name") else str(tool)
            if "update_milestone" in name:
                milestone_tool = tool
                break

        assert milestone_tool is not None, "Should have update_milestone tool"

        # Test updating milestone with correct parameters
        result = milestone_tool.invoke(
            {
                "user_id": "test_finance",
                "milestone_data": {
                    "type": "financial_goal",
                    "description": "Saved $1000 for emergency fund",
                },
            }
        )
        assert result is not None

    def test_wellness_specialist_memory_integration(
        self, wellness_specialist_with_tools, memory_store
    ):
        """Test Wellness Specialist can use memory tools."""
        specialist = wellness_specialist_with_tools

        # Find get_progress_history tool
        history_tool = None
        for tool in specialist["tools"]:
            name = tool.name if hasattr(tool, "name") else str(tool)
            if "get_progress_history" in name:
                history_tool = tool
                break

        assert history_tool is not None, "Should have get_progress_history tool"

        # Test retrieving progress history
        result = history_tool.invoke({"user_id": "test_wellness"})
        assert result is not None
        assert isinstance(result, str)


# ============================================================================
# Test Error Handling
# ============================================================================


class TestSpecialistErrorHandling:
    """Test suite for error handling in specialist agents."""

    def test_career_specialist_invalid_input_handling(self, career_specialist_with_tools):
        """Test Career Specialist handles invalid inputs gracefully."""
        specialist = career_specialist_with_tools

        # Find analyze_skill_gap tool
        skill_tool = None
        for tool in specialist["tools"]:
            name = tool.name if hasattr(tool, "name") else str(tool)
            if "skill_gap" in name:
                skill_tool = tool
                break

        # Test with empty skills list
        result = skill_tool.invoke(
            {
                "user_id": "test",
                "current_skills": [],  # Invalid
                "target_role": "Data Scientist",
            }
        )

        assert result is not None
        # Should contain error message or handle gracefully

    def test_finance_specialist_invalid_input_handling(self, finance_specialist_with_tools):
        """Test Finance Specialist handles invalid inputs gracefully."""
        specialist = finance_specialist_with_tools

        # Find budget tool
        budget_tool = None
        for tool in specialist["tools"]:
            name = tool.name if hasattr(tool, "name") else str(tool)
            if "budget" in name:
                budget_tool = tool
                break

        if budget_tool:
            # Test with negative values - use correct parameter name
            result = budget_tool.invoke(
                {
                    "user_id": "test",
                    "monthly_income": -1000,  # Invalid
                    "expenses": {},
                }
            )

            assert result is not None
            # Should contain error message or handle gracefully


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
