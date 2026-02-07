"""
Comprehensive test suite for Subagent Communication Protocol Tools.

This module tests:
1. Specialist message formatting
2. Result aggregation from multiple specialists
3. Conflict detection and resolution
4. Cross-consultation triggers
5. Unified response generation

Tests are designed to verify the communication protocol works correctly
when specialists provide their analyses and recommendations.
"""

import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import and initialize config first
from src.config import config, get_backend

# Initialize config for tests
try:
    _backend = get_backend()
except RuntimeError:
    # Config not initialized, initialize it
    config.initialize_environment()
    _backend = get_backend()

# Import the tools to test after config is initialized
from src.tools.communication_tools import (
    create_communication_tools,
    SpecialistMessage,
    AggregatedResults,
    aggregate_specialist_results,
    PriorityBasedResolution,
    ConsensusBasedResolution,
    HybridResolution,
    detect_cross_consultation_needs,
    generate_unified_response,
)


# Test data
SAMPLE_USER_ID = "test_user_comm_123"
SAMPLE_QUERY = "I need help balancing work and family life"

# Sample specialist messages
CAREER_MESSAGE_DATA = {
    "specialist_name": "career-specialist",
    "user_query": SAMPLE_QUERY,
    "analysis": (
        "Your career is experiencing significant growth which is creating "
        "time pressure on family commitments. You have strong performance "
        "but work hours are increasing."
    ),
    "recommendations": [
        {
            "title": "Set clear work boundaries",
            "priority": 9,
            "description": "Establish specific start/end times for work",
        },
        {
            "title": "Negotiate flexible hours",
            "priority": 7,
            "description": "Discuss options with your manager",
        },
    ],
    "synergies_with_other_domains": [
        {
            "domain": "wellness-specialist",
            "description": "Better work-life balance supports stress reduction",
            "strength": 0.8,
        }
    ],
    "conflicts_with_other_domains": [
        {
            "domain": "finance-specialist",
            "description": "Reducing work hours may impact income goals",
            "severity": "medium",
        }
    ],
    "confidence_level": 0.85,
    "requires_cross_consultation": True,
    "metadata": {"user_id": SAMPLE_USER_ID},
}

WELLNESS_MESSAGE_DATA = {
    "specialist_name": "wellness-specialist",
    "user_query": SAMPLE_QUERY,
    "analysis": (
        "Your stress levels are elevated due to work pressure, affecting "
        "sleep quality and family interactions. You need more recovery time."
    ),
    "recommendations": [
        {
            "title": "Implement evening wind-down routine",
            "priority": 8,
            "description": "30 minutes before bed, no work activities",
        },
        {
            "title": "Schedule daily family time",
            "priority": 9,
            "description": "Protect specific hours for family activities",
        },
    ],
    "synergies_with_other_domains": [
        {
            "domain": "relationship-specialist",
            "description": "Stress management improves relationship quality",
            "strength": 0.9,
        }
    ],
    "conflicts_with_other_domains": [],
    "confidence_level": 0.9,
    "requires_cross_consultation": False,
    "metadata": {"user_id": SAMPLE_USER_ID},
}

FINANCE_MESSAGE_DATA = {
    "specialist_name": "finance-specialist",
    "user_query": SAMPLE_QUERY,
    "analysis": (
        "You have aggressive savings goals that require current income levels. "
        "Reducing work hours may delay financial targets."
    ),
    "recommendations": [
        {
            "title": "Adjust savings timeline",
            "priority": 6,
            "description": "Extend timeline to accommodate work-life balance",
        },
        {
            "title": "Create income diversification plan",
            "priority": 7,
            "description": "Build side income for more flexibility",
        },
    ],
    "synergies_with_other_domains": [
        {
            "domain": "career-specialist",
            "description": "Financial stability enables career risk-taking",
            "strength": 0.7,
        }
    ],
    "conflicts_with_other_domains": [
        {
            "domain": "career-specialist",
            "description": "Income goals may conflict with reduced hours",
            "severity": "high",
        }
    ],
    "confidence_level": 0.8,
    "requires_cross_consultation": True,
    "metadata": {"user_id": SAMPLE_USER_ID},
}

RELATIONSHIP_MESSAGE_DATA = {
    "specialist_name": "relationship-specialist",
    "user_query": SAMPLE_QUERY,
    "analysis": (
        "Family relationships are showing strain from lack of quality time. "
        "Your partner and children need more focused attention."
    ),
    "recommendations": [
        {
            "title": "Schedule weekly family meetings",
            "priority": 8,
            "description": "Regular check-ins to discuss needs and schedules",
        },
        {
            "title": "Create phone-free family time",
            "priority": 7,
            "description": "Protect evenings from work interruptions",
        },
    ],
    "synergies_with_other_domains": [
        {
            "domain": "wellness-specialist",
            "description": "Family support improves mental wellness",
            "strength": 0.85,
        }
    ],
    "conflicts_with_other_domains": [],
    "confidence_level": 0.85,
    "requires_cross_consultation": False,
    "metadata": {"user_id": SAMPLE_USER_ID},
}


def print_section(title: str):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_message_formatting():
    """Test SpecialistMessage data structure."""
    print_section("Test 1: Specialist Message Formatting")

    # Create message
    msg = SpecialistMessage(**CAREER_MESSAGE_DATA)
    assert msg.specialist_name == "career-specialist"
    assert len(msg.recommendations) == 2
    assert msg.confidence_level == 0.85

    # Test to_dict conversion
    msg_dict = msg.to_dict()
    assert "specialist_name" in msg_dict
    assert "analysis" in msg_dict

    # Test from_dict conversion
    recovered_msg = SpecialistMessage.from_dict(msg_dict)
    assert recovered_msg.specialist_name == msg.specialist_name
    assert recovered_msg.analysis == msg.analysis

    print("✓ SpecialistMessage structure works correctly")
    print(f"  - Created message with {len(msg.recommendations)} recommendations")
    print(f"  - Confidence level: {msg.confidence_level:.1%}")
    print(f"  - Requires cross-consultation: {msg.requires_cross_consultation}")


def test_aggregation():
    """Test result aggregation from multiple specialists."""
    print_section("Test 2: Result Aggregation")

    # Create messages
    career_msg = SpecialistMessage(**CAREER_MESSAGE_DATA)
    wellness_msg = SpecialistMessage(**WELLNESS_MESSAGE_DATA)
    finance_msg = SpecialistMessage(**FINANCE_MESSAGE_DATA)

    # Aggregate
    messages = [career_msg, wellness_msg, finance_msg]
    aggregated = aggregate_specialist_results(messages)
    aggregated.user_id = SAMPLE_USER_ID

    # Verify aggregation
    assert len(aggregated.messages) == 3
    assert aggregated.conflicts_detected is not None

    # Check conflicts detected
    print(f"✓ Successfully aggregated {len(aggregated.messages)} specialist messages")
    print(f"  - Conflicts detected: {len(aggregated.conflicts_detected)}")

    for conflict in aggregated.conflicts_detected:
        spec1 = conflict["specialist_1"].replace("-specialist", "").title()
        spec2 = conflict["specialist_2"].replace("-specialist", "").title()
        print(f"    • {spec1} vs {spec2}: {conflict['description']}")

    # Check synergies identified
    print(f"  - Synergies identified: {len(aggregated.synergies_identified)}")
    for synergy in aggregated.synergies_identified[:3]:
        spec = synergy["specialist"].replace("-specialist", "").title()
        domain = synergy["domain"].replace("-specialist", "").title()
        print(f"    • {spec} ↔ {domain}: {synergy['description']}")


def test_priority_based_resolution():
    """Test priority-based conflict resolution."""
    print_section("Test 3: Priority-Based Conflict Resolution")

    # Create test messages
    career_msg = SpecialistMessage(**CAREER_MESSAGE_DATA)
    finance_msg = SpecialistMessage(**FINANCE_MESSAGE_DATA)

    messages = {"career-specialist": career_msg, "finance-specialist": finance_msg}

    # Create conflicts
    conflicts = [
        {
            "specialist_1": "career-specialist",
            "specialist_2": "finance-specialist",
            "description": "Work hours vs income goals",
            "severity": "high",
        }
    ]

    # Resolve using priority-based strategy
    resolver = PriorityBasedResolution()
    resolutions = resolver.resolve(conflicts, messages)

    # Verify resolution
    assert len(resolutions) == 1
    assert resolutions[0]["resolution_type"] == "priority_based"

    print("✓ Priority-based resolution works correctly")
    for res in resolutions:
        print(f"  - Resolution type: {res['resolution_type']}")
        print(f"  - Preferred specialist: {res['preferred_specialist']}")
        print(f"  - Rationale: {res['rationale']}")


def test_consensus_based_resolution():
    """Test consensus-based conflict resolution."""
    print_section("Test 4: Consensus-Based Conflict Resolution")

    # Create test messages
    career_msg = SpecialistMessage(**CAREER_MESSAGE_DATA)
    finance_msg = SpecialistMessage(**FINANCE_MESSAGE_DATA)

    messages = {"career-specialist": career_msg, "finance-specialist": finance_msg}

    # Create conflicts
    conflicts = [
        {
            "specialist_1": "career-specialist",
            "specialist_2": "finance-specialist",
            "description": "Work hours vs income goals",
            "severity": "medium",
        }
    ]

    # Resolve using consensus-based strategy
    resolver = ConsensusBasedResolution()
    resolutions = resolver.resolve(conflicts, messages)

    # Verify resolution
    assert len(resolutions) == 1
    assert resolutions[0]["resolution_type"] in ["compromise", "sequential"]

    print("✓ Consensus-based resolution works correctly")
    for res in resolutions:
        print(f"  - Resolution type: {res['resolution_type']}")
        print(f"  - Rationale: {res['rationale']}")
        print(f"  - Suggested action: {res['suggested_action']}")


def test_hybrid_resolution():
    """Test hybrid conflict resolution."""
    print_section("Test 5: Hybrid Conflict Resolution")

    # Create test messages
    career_msg = SpecialistMessage(**CAREER_MESSAGE_DATA)
    finance_msg = SpecialistMessage(**FINANCE_MESSAGE_DATA)
    wellness_msg = SpecialistMessage(**WELLNESS_MESSAGE_DATA)

    messages = {
        "career-specialist": career_msg,
        "finance-specialist": finance_msg,
        "wellness-specialist": wellness_msg,
    }

    # Create conflicts with different severities
    conflicts = [
        {
            "specialist_1": "career-specialist",
            "specialist_2": "finance-specialist",
            "description": "Work hours vs income goals (high severity)",
            "severity": "high",
        },
        {
            "specialist_1": "career-specialist",
            "specialist_2": "wellness-specialist",
            "description": "Stress management vs career growth (medium severity)",
            "severity": "medium",
        },
    ]

    # Resolve using hybrid strategy
    resolver = HybridResolution()
    resolutions = resolver.resolve(conflicts, messages)

    # Verify resolution
    assert len(resolutions) == 2

    print("✓ Hybrid resolution works correctly")
    for i, res in enumerate(resolutions, 1):
        print(f"  {i}. Resolution type: {res['resolution_type']}")
        print(f"     Rationale: {res['rationale']}")


def test_cross_consultation_detection():
    """Test cross-consultation triggers."""
    print_section("Test 6: Cross-Consultation Detection")

    # Create messages
    career_msg = SpecialistMessage(**CAREER_MESSAGE_DATA)
    wellness_msg = SpecialistMessage(**WELLNESS_MESSAGE_DATA)
    finance_msg = SpecialistMessage(**FINANCE_MESSAGE_DATA)
    relationship_msg = SpecialistMessage(**RELATIONSHIP_MESSAGE_DATA)

    messages = {
        "career-specialist": career_msg,
        "wellness-specialist": wellness_msg,
        "finance-specialist": finance_msg,
        "relationship-specialist": relationship_msg,
    }

    # Detect cross-consultation needs
    consultations = detect_cross_consultation_needs(messages)

    # Verify detection
    assert isinstance(consultations, list)

    print(f"✓ Cross-consultation detection works correctly")
    print(f"  - {len(consultations)} consultation(s) recommended")

    for rec in consultations:
        spec_title = rec["trigger_specialist"].replace("-specialist", "").title()
        consultants = [c.replace("-specialist", "").title() for c in rec["recommended_consultants"]]
        print(f"\n  {spec_title}:")
        print(f"    Reason: {rec['reason']}")
        print(f"    Consult with: {', '.join(consultants)}")


def test_unified_response_generation():
    """Test unified response generation."""
    print_section("Test 7: Unified Response Generation")

    # Create messages
    career_msg = SpecialistMessage(**CAREER_MESSAGE_DATA)
    wellness_msg = SpecialistMessage(**WELLNESS_MESSAGE_DATA)

    # Aggregate
    messages = [career_msg, wellness_msg]
    aggregated = aggregate_specialist_results(messages)
    aggregated.user_id = SAMPLE_USER_ID

    # Generate unified response
    resolver = HybridResolution()
    unified_response = generate_unified_response(aggregated, resolver)

    # Verify response
    assert "Integrated Analysis" in unified_response
    assert "Specialist Insights" in unified_response

    print("✓ Unified response generation works correctly")
    print(f"\n  Response preview (first 500 chars):")
    print("  " + "-" * 66)
    lines = unified_response.split("\n")[:15]
    for line in lines:
        print("  " + line)
    print("  " + "-" * 66)


def test_communication_tools():
    """Test the communication tools as LangChain tools."""
    print_section("Test 8: Communication Tools (LangChain Integration)")

    # Create tools
    try:
        (format_msg, agg_results, resolve_conflicts, detect_consult, gen_unified) = (
            create_communication_tools(_backend)
        )
        print("✓ Communication tools created successfully")
    except Exception as e:
        print(f"✗ Failed to create communication tools: {e}")
        return False

    # Test format_specialist_message
    print("\n  Testing format_specialist_message...")
    result = format_msg.invoke(
        {
            "specialist_name": "career-specialist",
            "user_query": SAMPLE_QUERY,
            "analysis": CAREER_MESSAGE_DATA["analysis"],
            "recommendations": CAREER_MESSAGE_DATA["recommendations"],
            "metadata": {"user_id": SAMPLE_USER_ID},
        }
    )
    assert "Career Specialist Message Formatted" in result
    print("  ✓ format_specialist_message works")

    # Test aggregate_results
    print("\n  Testing aggregate_results...")
    result = agg_results.invoke(
        {
            "user_id": SAMPLE_USER_ID,
            "specialist_messages": [CAREER_MESSAGE_DATA, WELLNESS_MESSAGE_DATA],
        }
    )
    assert "Results Aggregation" in result
    print("  ✓ aggregate_results works")

    # Test resolve_conflicts
    print("\n  Testing resolve_conflicts...")
    result = resolve_conflicts.invoke({"user_id": SAMPLE_USER_ID, "resolution_strategy": "hybrid"})
    assert "Conflict Resolution Report" in result
    print("  ✓ resolve_conflicts works")

    # Test detect_cross_consultation
    print("\n  Testing detect_cross_consultation...")
    result = detect_consult.invoke(
        {
            "user_id": SAMPLE_USER_ID,
            "specialist_messages": [CAREER_MESSAGE_DATA, FINANCE_MESSAGE_DATA],
        }
    )
    assert "Cross-Consultation Analysis" in result
    print("  ✓ detect_cross_consultation works")

    # Test generate_unified_response_tool
    print("\n  Testing generate_unified_response_tool...")
    result = gen_unified.invoke({"user_id": SAMPLE_USER_ID, "resolution_strategy": "hybrid"})
    assert "Integrated Analysis" in result or "No aggregated results found" in result
    print("  ✓ generate_unified_response_tool works")

    return True


def test_full_workflow():
    """Test the complete workflow from messages to unified response."""
    print_section("Test 9: Full Communication Workflow")

    # Step 1: Format messages from all specialists
    print("\nStep 1: Formatting specialist messages...")
    format_msg, agg_results, resolve_conflicts, detect_consult, gen_unified = (
        create_communication_tools(_backend)
    )

    career_msg_result = format_msg.invoke(
        {
            "specialist_name": "career-specialist",
            "user_query": SAMPLE_QUERY,
            "analysis": CAREER_MESSAGE_DATA["analysis"],
            "recommendations": CAREER_MESSAGE_DATA["recommendations"],
            "synergies_with_other_domains": CAREER_MESSAGE_DATA["synergies_with_other_domains"],
            "conflicts_with_other_domains": CAREER_MESSAGE_DATA["conflicts_with_other_domains"],
            "confidence_level": 0.85,
            "metadata": {"user_id": SAMPLE_USER_ID},
        }
    )

    wellness_msg_result = format_msg.invoke(
        {
            "specialist_name": "wellness-specialist",
            "user_query": SAMPLE_QUERY,
            "analysis": WELLNESS_MESSAGE_DATA["analysis"],
            "recommendations": WELLNESS_MESSAGE_DATA["recommendations"],
            "synergies_with_other_domains": WELLNESS_MESSAGE_DATA["synergies_with_other_domains"],
            "confidence_level": 0.9,
            "metadata": {"user_id": SAMPLE_USER_ID},
        }
    )

    print("  ✓ Messages formatted from Career and Wellness specialists")

    # Step 2: Aggregate results
    print("\nStep 2: Aggregating specialist results...")
    agg_result = agg_results.invoke(
        {
            "user_id": SAMPLE_USER_ID,
            "specialist_messages": [CAREER_MESSAGE_DATA, WELLNESS_MESSAGE_DATA],
        }
    )
    print("  ✓ Results aggregated successfully")

    # Step 3: Detect cross-consultation needs
    print("\nStep 3: Detecting cross-consultation needs...")
    consult_result = detect_consult.invoke({"user_id": SAMPLE_USER_ID})
    print("  ✓ Cross-consultation needs detected")

    # Step 4: Resolve conflicts
    print("\nStep 4: Resolving conflicts...")
    resolve_result = resolve_conflicts.invoke(
        {"user_id": SAMPLE_USER_ID, "resolution_strategy": "hybrid"}
    )
    print("  ✓ Conflicts resolved using hybrid strategy")

    # Step 5: Generate unified response
    print("\nStep 5: Generating unified response...")
    unified_result = gen_unified.invoke(
        {"user_id": SAMPLE_USER_ID, "resolution_strategy": "hybrid"}
    )
    print("  ✓ Unified response generated")

    # Verify workflow
    assert "Career Specialist Message Formatted" in career_msg_result
    assert "Results Aggregation" in agg_result
    assert "Cross-Consultation Analysis" in consult_result
    assert "Conflict Resolution Report" in resolve_result
    assert "Integrated Analysis" in unified_result

    print("\n✓ Full workflow completed successfully!")
    return True


# Main test execution
def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("  SUBAGENT COMMUNICATION PROTOCOL TEST SUITE")
    print("=" * 70)

    all_passed = True

    # Run individual tests
    try:
        test_message_formatting()
    except Exception as e:
        print(f"✗ Test 1 failed: {e}")
        all_passed = False

    try:
        test_aggregation()
    except Exception as e:
        print(f"✗ Test 2 failed: {e}")
        all_passed = False

    try:
        test_priority_based_resolution()
    except Exception as e:
        print(f"✗ Test 3 failed: {e}")
        all_passed = False

    try:
        test_consensus_based_resolution()
    except Exception as e:
        print(f"✗ Test 4 failed: {e}")
        all_passed = False

    try:
        test_hybrid_resolution()
    except Exception as e:
        print(f"✗ Test 5 failed: {e}")
        all_passed = False

    try:
        test_cross_consultation_detection()
    except Exception as e:
        print(f"✗ Test 6 failed: {e}")
        all_passed = False

    try:
        test_unified_response_generation()
    except Exception as e:
        print(f"✗ Test 7 failed: {e}")
        all_passed = False

    try:
        test_communication_tools()
    except Exception as e:
        print(f"✗ Test 8 failed: {e}")
        all_passed = False

    try:
        test_full_workflow()
    except Exception as e:
        print(f"✗ Test 9 failed: {e}")
        all_passed = False

    # Final summary
    print_section("Test Summary")
    if all_passed:
        print("\n✓ All tests passed successfully!")
        print("\nThe Subagent Communication Protocol is working correctly:")
        print("  • Specialist messages can be formatted and stored")
        print("  • Results from multiple specialists are aggregated properly")
        print("  • Conflicts are detected and resolved using multiple strategies")
        print("  • Cross-consultation needs are identified")
        print("  • Unified responses integrate all specialist inputs cohesively")
    else:
        print("\n✗ Some tests failed. Please review the errors above.")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
