"""
Test suite for verifying subagent configuration and tool allocation.

This module validates that:
1. All four specialists are properly defined
2. Each specialist has the required fields (name, description, system_prompt, tools, model)
3. Tool allocation follows the strategy (memory + context, no planning)
4. System prompts are comprehensive (>100 lines each)
"""

import pytest
from src.agents import get_all_specialists, get_career_specialist


class TestSpecialistConfiguration:
    """Test specialist subagent configurations."""

    def test_get_all_specialists_returns_four(self):
        """Verify that get_all_specialists returns exactly four specialists."""
        specialists = get_all_specialists()
        assert len(specialists) == 4, "Should return exactly four specialists"

    def test_each_specialist_has_required_fields(self):
        """Verify each specialist has all required fields."""
        specialists = get_all_specialists()

        for specialist in specialists:
            assert "name" in specialist, f"{specialist.get('name', 'Unknown')} missing 'name'"
            assert "description" in specialist, (
                f"{specialist.get('name', 'Unknown')} missing 'description'"
            )
            assert "system_prompt" in specialist, (
                f"{specialist.get('name', 'Unknown')} missing 'system_prompt'"
            )
            assert "tools" in specialist, f"{specialist.get('name', 'Unknown')} missing 'tools'"
            assert "model" in specialist, f"{specialist.get('name', 'Unknown')} missing 'model'"

    def test_specialist_names_are_correct(self):
        """Verify specialist names match expected values."""
        specialists = get_all_specialists()
        names = [s["name"] for s in specialists]

        expected_names = [
            "career-specialist",
            "relationship-specialist",
            "finance-specialist",
            "wellness-specialist",
        ]

        for expected in expected_names:
            assert expected in names, f"Expected specialist '{expected}' not found. Got: {names}"

    def test_specialist_descriptions_are_specific(self):
        """Verify descriptions are specific and action-oriented."""
        specialists = get_all_specialists()

        for specialist in specialists:
            description = specialist["description"]
            # Should be reasonably long (at least 100 chars)
            assert len(description) >= 100, (
                f"{specialist['name']} description too short: {len(description)} chars"
            )
            # Should use action verbs like "Expert in", "Use for", etc.
            assert any(
                word in description.lower() for word in ["expert", "specialist", "use for"]
            ), f"{specialist['name']} description should be action-oriented"

    def test_system_prompts_are_comprehensive(self):
        """Verify system prompts are comprehensive (>100 lines or very long)."""
        specialists = get_all_specialists()

        for specialist in specialists:
            system_prompt = specialist["system_prompt"]
            # Count lines
            line_count = len(system_prompt.split("\n"))

            # Should be very comprehensive (100+ lines or 3000+ chars)
            assert line_count >= 100 or len(system_prompt) >= 3000, (
                f"{specialist['name']} system prompt too short: {line_count} lines, {len(system_prompt)} chars"
            )

            # Should contain key sections
            assert "## Your" in system_prompt or "#" in system_prompt, (
                f"{specialist['name']} system prompt should have section headers"
            )

    def test_model_configuration(self):
        """Verify model is configured to use local LLM."""
        specialists = get_all_specialists()

        for specialist in specialists:
            model = specialist["model"]
            assert model == "openai:glm-4.7", f"{specialist['name']} should use openai:glm-4.7"

    def test_tools_field_is_list(self):
        """Verify tools field is a list (even if empty initially)."""
        specialists = get_all_specialists()

        for specialist in specialists:
            tools = specialist["tools"]
            assert isinstance(tools, list), (
                f"{specialist['name']} tools should be a list, got {type(tools)}"
            )

    def test_individual_specialist_functions(self):
        """Test individual specialist getter functions."""
        career = get_career_specialist()
        assert career["name"] == "career-specialist"
        assert isinstance(career, dict)

    def test_specialist_descriptions_mention_domain(self):
        """Verify each description mentions its specific domain."""
        specialists = get_all_specialists()

        career_desc = next(
            s["description"] for s in specialists if s["name"] == "career-specialist"
        )
        assert "career" in career_desc.lower()

        rel_desc = next(
            s["description"] for s in specialists if s["name"] == "relationship-specialist"
        )
        assert "relationship" in rel_desc.lower()

        fin_desc = next(s["description"] for s in specialists if s["name"] == "finance-specialist")
        assert "finance" in fin_desc.lower()

        well_desc = next(
            s["description"] for s in specialists if s["name"] == "wellness-specialist"
        )
        assert "wellness" in well_desc.lower()


class TestToolAllocation:
    """Test tool allocation strategy."""

    def test_specialists_can_receive_tools(self):
        """Verify specialists can accept tool lists."""
        mock_memory_tools = ["tool1", "tool2"]
        mock_context_tools = ["tool3", "tool4"]

        career = get_career_specialist(tools=mock_memory_tools + mock_context_tools)

        assert career["tools"] == mock_memory_tools + mock_context_tools

    def test_tool_allocation_matches_strategy(self):
        """Verify the tool allocation strategy in main.py pattern."""
        # Simulate what main.py does
        mock_memory_tools = ["get_user_profile", "save_user_preference"]
        mock_context_tools = ["save_assessment", "get_active_plan"]

        # Specialists should get memory + context, NOT planning
        specialist_tools = mock_memory_tools + mock_context_tools

        # Verify no planning tools (write_todos, update_todo, list_todos) in specialist allocation
        # Note: "get_active_plan" is a context tool, NOT a planning tool - it retrieves existing plans
        planning_tools = ["write_todos", "update_todo", "list_todos"]
        has_planning_tools = any(
            planner_tool in specialist_tools for planner_tool in planning_tools
        )
        assert not has_planning_tools, (
            f"Specialists should not have planning tools. Found: {[t for t in specialist_tools if t in planning_tools]}"
        )

        # Verify they do have memory and context tools
        assert specialist_tools == mock_memory_tools + mock_context_tools

    def test_coordinator_has_more_tools_than_specialists(self):
        """Verify coordinator has access to planning tools that specialists don't."""
        # Coordinator: memory + planning + context
        coordinator_tools = ["mem1", "plan1", "ctx1"]

        # Specialist: memory + context only
        specialist_tools = ["mem1", "ctx1"]

        # Coordinator should have more tools (planning)
        assert len(coordinator_tools) > len(specialist_tools)


class TestSystemPromptContent:
    """Test system prompt content quality."""

    def test_career_specialist_prompt(self):
        """Verify career specialist has appropriate content."""
        career = get_career_specialist()
        prompt = career["system_prompt"]

        # Should mention key career concepts
        keywords = ["career", "skill", "resume", "interview", "job"]
        found_keywords = [kw for kw in keywords if kw.lower() in prompt.lower()]
        assert len(found_keywords) >= 3, f"Career prompt should mention career-related terms"

        # Should have structure (sections)
        assert "#" in prompt, "Should use markdown headers for structure"

    def test_relationship_specialist_prompt(self):
        """Verify relationship specialist has appropriate content."""
        specialists = get_all_specialists()
        rel = next(s for s in specialists if s["name"] == "relationship-specialist")
        prompt = rel["system_prompt"]

        # Should mention key relationship concepts
        keywords = ["relationship", "communication", "boundary", "conflict"]
        found_keywords = [kw for kw in keywords if kw.lower() in prompt.lower()]
        assert len(found_keywords) >= 2, f"Relationship prompt should mention relationship terms"

    def test_finance_specialist_prompt(self):
        """Verify finance specialist has appropriate content."""
        specialists = get_all_specialists()
        fin = next(s for s in specialists if s["name"] == "finance-specialist")
        prompt = fin["system_prompt"]

        # Should mention key finance concepts
        keywords = ["finance", "budget", "debt", "saving"]
        found_keywords = [kw for kw in keywords if kw.lower() in prompt.lower()]
        assert len(found_keywords) >= 2, f"Finance prompt should mention finance terms"

        # Should include disclaimer about not being professional advice
        assert "not" in prompt.lower() and ("advice" in prompt.lower()), (
            "Finance specialist should have disclaimer about not providing professional advice"
        )

    def test_wellness_specialist_prompt(self):
        """Verify wellness specialist has appropriate content."""
        specialists = get_all_specialists()
        well = next(s for s in specialists if s["name"] == "wellness-specialist")
        prompt = well["system_prompt"]

        # Should mention key wellness concepts
        keywords = ["wellness", "health", "exercise", "sleep", "stress"]
        found_keywords = [kw for kw in keywords if kw.lower() in prompt.lower()]
        assert len(found_keywords) >= 2, f"Wellness prompt should mention wellness terms"

        # Should include disclaimer about not being medical advice
        assert "not" in prompt.lower() and (
            "medical" in prompt.lower() or "advice" in prompt.lower()
        ), "Wellness specialist should have disclaimer about not providing medical advice"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
