"""
Test suite for Coordinator Agent System.

This file demonstrates and tests the coordinator's key functionality:
- Decision-making framework
- Priority weighting system
- Escalation triggers
- Cross-domain integration
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.coordinator import get_coordinator_prompt, get_coordinator


def test_coordinator_prompt_exists():
    """Test that coordinator prompt can be retrieved."""
    prompt = get_coordinator_prompt()
    assert isinstance(prompt, str)
    assert len(prompt) > 1000  # Should be a comprehensive prompt
    print("✓ Coordinator prompt retrieved successfully")
    print(f"  Prompt length: {len(prompt)} characters")


def test_coordinator_prompt_structure():
    """Test that coordinator prompt has all required sections."""
    prompt = get_coordinator_prompt()

    # Core sections that should be present
    required_sections = [
        "## Your Core Mission",
        "## Decision Framework",
        "## Priority Weighting System",
        "## Escalation Triggers",
        "## Cross-Domain Integration Framework",
        "## Subagent Coordination Rules",
        "## Safety and Ethical Boundaries",
    ]

    for section in required_sections:
        assert section in prompt, f"Missing required section: {section}"
        print(f"✓ Found section: {section}")


def test_coordinator_prompt_decision_framework():
    """Test that decision framework is well-defined."""
    prompt = get_coordinator_prompt()

    # Decision framework components
    decision_components = [
        "Phase 1: Request Analysis",
        "Domain Identification",
        "Complexity Evaluation",
        "Response Strategy Selection",
    ]

    for component in decision_components:
        assert component in prompt, f"Missing decision framework component: {component}"
        print(f"✓ Found decision framework: {component}")


def test_coordinator_prompt_priority_system():
    """Test that priority weighting system is defined."""
    prompt = get_coordinator_prompt()

    # Priority factors
    priority_factors = [
        "Urgency",
        "Impact",
        "User Preference",
        "Dependencies",
        "Resource Availability",
    ]

    for factor in priority_factors:
        assert factor in prompt, f"Missing priority factor: {factor}"
        print(f"✓ Found priority factor: {factor}")


def test_coordinator_prompt_escalation_triggers():
    """Test that escalation triggers are defined."""
    prompt = get_coordinator_prompt()

    # Escalation scenarios
    escalation_scenarios = [
        "Goal Conflicts Detected",
        "Multi-Domain Major Life Transitions",
        "Complex Resource Allocation Scenarios",
        "Cross-Domain Dependencies Detected",
    ]

    for scenario in escalation_scenarios:
        assert scenario in prompt, f"Missing escalation trigger: {scenario}"
        print(f"✓ Found escalation trigger: {scenario}")


def test_coordinator_prompt_crisis_protocol():
    """Test that crisis protocol is defined."""
    prompt = get_coordinator_prompt()

    # Crisis situations
    crises = [
        "Mental Health Crisis",
        "Domestic Violence/Abuse",
        "Legal Emergencies",
        "Medical Emergencies",
    ]

    for crisis in crises:
        assert crisis in prompt, f"Missing crisis protocol: {crisis}"
        print(f"✓ Found crisis protocol for: {crisis}")


def test_coordinator_prompt_tool_usage():
    """Test that tool usage guidelines are included."""
    prompt = get_coordinator_prompt()

    # Tool categories
    tool_categories = [
        "Memory Tools",
        "Planning Tools",
        "Context Tools",
        "Cross-Domain Tools",
        "Communication Tools",
    ]

    for category in tool_categories:
        assert category in prompt, f"Missing tool category: {category}"
        print(f"✓ Found tool usage guidelines for: {category}")


def test_coordinator_prompt_delegation_rules():
    """Test that delegation rules are clear."""
    prompt = get_coordinator_prompt()

    # Delegation patterns
    delegation_patterns = [
        "When to Delegate vs. Handle Directly",
        "DELEGATE to specialists when:",
        "HANDLE DIRECTLY when:",
        "COORDINATE (multiple specialists) when:",
    ]

    for pattern in delegation_patterns:
        assert pattern in prompt, f"Missing delegation rule: {pattern}"
        print(f"✓ Found delegation guidance: {pattern}")


def test_coordinator_prompt_integration_framework():
    """Test that cross-domain integration framework is present."""
    prompt = get_coordinator_prompt()

    # Integration tools and patterns
    integration_components = [
        "build_goal_dependency_graph",
        "analyze_cross_domain_impacts",
        "detect_goal_conflicts",
        "recommend_priority_adjustments",
        "generate_integration_plan",
    ]

    for component in integration_components:
        assert component in prompt, f"Missing integration tool: {component}"
        print(f"✓ Found integration component: {component}")


def test_coordinator_config():
    """Test that coordinator configuration can be retrieved."""
    coordinator = get_coordinator()
    assert isinstance(coordinator, dict)
    assert "name" in coordinator
    assert "description" in coordinator
    assert "system_prompt" in coordinator

    print("✓ Coordinator configuration retrieved successfully")
    print(f"  Name: {coordinator['name']}")
    print(f"  Description length: {len(coordinator['description'])} characters")


def test_coordinator_name():
    """Test that coordinator has the correct name."""
    prompt = get_coordinator_prompt()
    assert "Life Coach Coordinator" in prompt
    coordinator = get_coordinator()
    assert coordinator["name"] == "life-coach-coordinator"
    print("✓ Coordinator has correct name")


def test_coordinator_specialist_mentions():
    """Test that all four specialists are mentioned in coordinator prompt."""
    prompt = get_coordinator_prompt()

    specialists = [
        "career-specialist",
        "relationship-specialist",
        "finance-specialist",
        "wellness-specialist",
    ]

    for specialist in specialists:
        assert specialist in prompt, f"Missing mention of {specialist}"
        print(f"✓ Coordinator mentions: {specialist}")


def test_coordinator_domains():
    """Test that all four domains are mentioned."""
    prompt = get_coordinator_prompt()

    domains = ["Career", "Relationships", "Finance", "Wellness"]

    for domain in domains:
        assert domain in prompt, f"Missing mention of {domain} domain"
        print(f"✓ Coordinator covers domain: {domain}")


def test_priority_calculation_example():
    """Test that prompt includes priority calculation example."""
    prompt = get_coordinator_prompt()

    # Should show calculation formula
    assert "Priority Score" in prompt or "priority calculation" in prompt.lower()
    print("✓ Priority calculation methodology present")


def test_response_structure_example():
    """Test that prompt includes response structure example."""
    prompt = get_coordinator_prompt()

    # Should have example response structure
    assert "Executive Summary" in prompt or "Action Plan" in prompt
    print("✓ Response structure guidelines present")


def test_crisis_resources():
    """Test that crisis resources are included."""
    prompt = get_coordinator_prompt()

    # Should include hotline numbers
    crisis_resources = ["988", "800-799-SAFE", "Crisis Text Line"]

    for resource in crisis_resources:
        assert resource in prompt, f"Missing crisis resource: {resource}"
        print(f"✓ Crisis resource included: {resource}")


def test_professional_boundaries():
    """Test that professional boundaries are clearly defined."""
    prompt = get_coordinator_prompt()

    # Should clarify what is and isn't provided
    boundaries = [
        "NOT professional therapy",
        "NOT medical advice",
        "NOT legal advice",
        "educational information only",
    ]

    for boundary in boundaries:
        assert boundary.lower() in prompt.lower(), f"Missing boundary: {boundary}"
        print(f"✓ Professional boundary defined: {boundary}")


# Integration test examples
def demonstrate_decision_framework():
    """
    Demonstrate the decision framework with concrete examples.
    This function shows how the coordinator should analyze requests.
    """
    prompt = get_coordinator_prompt()
    print("\n" + "=" * 60)
    print("DEMONSTRATION: Decision Framework Examples")
    print("=" * 60)

    examples = [
        {
            "request": "I want to get promoted at work",
            "expected_strategy": "Single Specialist (career)",
            "reasoning": "Clear single-domain issue requiring expertise",
        },
        {
            "request": "I want to buy a house and advance my career",
            "expected_strategy": "Parallel Delegation or Sequential Coordination",
            "reasoning": "Multi-domain with clear interconnection (career enables house purchase)",
        },
        {
            "request": "I'm feeling overwhelmed by everything",
            "expected_strategy": "Direct Response + Potential Full Orchestration",
            "reasoning": "General guidance first, then assess what domains need attention",
        },
        {
            "request": "I want to change careers, maintain my lifestyle, and keep my relationship strong",
            "expected_strategy": "Full Orchestration",
            "reasoning": "Complex multi-domain scenario with significant interconnections",
        },
    ]

    for i, example in enumerate(examples, 1):
        print(f"\nExample {i}:")
        print(f"  Request: '{example['request']}'")
        print(f"  Expected Strategy: {example['expected_strategy']}")
        print(f"  Reasoning: {example['reasoning']}")

    print("\n✓ Decision framework examples demonstrated")


def demonstrate_priority_system():
    """
    Demonstrate the priority weighting system with a concrete example.
    """
    print("\n" + "=" * 60)
    print("DEMONSTRATION: Priority Weighting System")
    print("=" * 60)

    # Example from documentation
    goals = [
        {
            "name": "Get promoted at work",
            "urgency": 7,
            "impact": 9,
            "preference": 8,
            "dependencies": 6,
            "resources": 8,
        },
        {
            "name": "Start exercising regularly",
            "urgency": 4,
            "impact": 6,
            "preference": 7,
            "dependencies": 2,
            "resources": 9,
        },
    ]

    # Calculate priorities using the framework from prompt
    weights = {"urgency": 3, "impact": 3, "preference": 2, "dependencies": 1.5, "resources": 1}

    print("\nPriority Calculation:")
    for goal in goals:
        score = (
            goal["urgency"] * weights["urgency"]
            + goal["impact"] * weights["impact"]
            + goal["preference"] * weights["preference"]
            + goal["dependencies"] * weights["dependencies"]
            + goal["resources"] * weights["resources"]
        )
        print(f"\n{goal['name']}:")
        for factor in ["urgency", "impact", "preference", "dependencies", "resources"]:
            print(
                f"  {factor.capitalize()}: {goal[factor]} × {weights[factor]} = {goal[factor] * weights[factor]}"
            )
        print(f"  **Total Score: {score}**")

    print("\n✓ Priority system demonstrated")


if __name__ == "__main__":
    # Run all tests
    print("\n" + "=" * 60)
    print("COORDINATOR SYSTEM TEST SUITE")
    print("=" * 60 + "\n")

    test_functions = [
        ("Prompt Exists", test_coordinator_prompt_exists),
        ("Prompt Structure", test_coordinator_prompt_structure),
        ("Decision Framework", test_coordinator_prompt_decision_framework),
        ("Priority System", test_coordinator_prompt_priority_system),
        ("Escalation Triggers", test_coordinator_prompt_escalation_triggers),
        ("Crisis Protocol", test_coordinator_prompt_crisis_protocol),
        ("Tool Usage Guidelines", test_coordinator_prompt_tool_usage),
        ("Delegation Rules", test_coordinator_prompt_delegation_rules),
        ("Integration Framework", test_coordinator_prompt_integration_framework),
        ("Coordinator Config", test_coordinator_config),
        ("Coordinator Name", test_coordinator_name),
        ("Specialist Mentions", test_coordinator_specialist_mentions),
        ("Domain Coverage", test_coordinator_domains),
        ("Priority Calculation Example", test_priority_calculation_example),
        ("Response Structure", test_response_structure_example),
        ("Crisis Resources", test_crisis_resources),
        ("Professional Boundaries", test_professional_boundaries),
    ]

    passed = 0
    failed = 0

    for name, test_func in test_functions:
        try:
            print(f"\n{'=' * 60}")
            print(f"TEST: {name}")
            print("=" * 60)
            test_func()
            passed += 1
            print(f"\n✅ PASSED: {name}")
        except AssertionError as e:
            failed += 1
            print(f"\n❌ FAILED: {name}")
            print(f"   Error: {e}")

    # Run demonstrations
    demonstrate_decision_framework()
    demonstrate_priority_system()

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {passed + failed}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Coordinator system is ready.")
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")

    print("=" * 60 + "\n")
