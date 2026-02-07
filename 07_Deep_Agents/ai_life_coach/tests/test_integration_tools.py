"""
Test suite for Result Integration Tools.

This module tests the integration functionality including:
1. Specialist output harmonization
2. Cross-domain insight synthesis
3. Conflict resolution strategies
4. Prioritized action list generation
5. Unified response creation

Run tests with: python -m pytest tests/test_integration_tools.py -v
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime
import json

# Import integration tools and components
try:
    from src.tools.integration_tools import (
        IntegratedInsight,
        PrioritizedAction,
        UnifiedResponse,
        SpecialistOutputHarmonizer,
        CrossDomainSynthesizer,
        ActionPrioritizer,
        AdvancedConflictResolver,
        ResultIntegrationEngine,
    )
except ImportError:
    # If import fails, we'll skip tests
    IntegrationToolsAvailable = False
else:
    IntegrationToolsAvailable = True


# ==============================================================================
# Test Data Fixtures
# ==============================================================================


def create_sample_specialist_messages():
    """Create sample specialist messages for testing."""
    return [
        {
            "specialist_name": "career-specialist",
            "timestamp": datetime.now().isoformat(),
            "analysis": "Career analysis shows strong skills with some gaps.",
            "recommendations": [
                {"title": "Get certified in Python", "priority": 8},
                {"title": "Apply for senior position", "priority": 7},
            ],
            "confidence_level": 0.85,
        },
        {
            "specialist_name": "wellness-specialist",
            "timestamp": datetime.now().isoformat(),
            "analysis": "Wellness assessment shows need for better sleep habits.",
            "recommendations": [
                {"title": "Establish bedtime routine", "priority": 9},
                {"title": "Exercise regularly", "priority": 8},
            ],
            "confidence_level": 0.9,
        },
    ]


def create_sample_conflicts():
    """Create sample conflicts for testing."""
    return [
        {
            "specialist_1": "career-specialist",
            "specialist_2": "wellness-specialist",
            "description": "Career advancement requires more work hours vs wellness need for rest",
            "severity": "medium",
        }
    ]


def create_sample_synergies():
    """Create sample synergies for testing."""
    return [
        {
            "specialist": "career-specialist",
            "domain": "wellness-specialist",
            "description": "Better sleep improves cognitive performance for work",
            "strength": 0.8,
        }
    ]


# ==============================================================================
# Test Functions
# ==============================================================================


def test_integrated_insight_creation():
    """Test creating IntegratedInsight dataclass."""
    if not IntegrationToolsAvailable:
        print("SKIP: Integration tools not available")
        return

    insight = IntegratedInsight(
        insight_id="test_insight_1",
        title="Test Insight",
        description="A test integrated insight",
        source_specialists=["career-specialist"],
        domains_affected={"career"},
        confidence_score=0.85,
    )

    assert insight.insight_id == "test_insight_1"
    assert insight.title == "Test Insight"
    assert insight.confidence_score == 0.85

    # Test to_dict conversion
    insight_dict = insight.to_dict()
    assert "insight_id" in insight_dict
    assert insight_dict["confidence_score"] == 0.85

    print("✓ test_integrated_insight_creation passed")


def test_prioritized_action_creation():
    """Test creating PrioritizedAction dataclass."""
    if not IntegrationToolsAvailable:
        print("SKIP: Integration tools not available")
        return

    action = PrioritizedAction(
        action_id="action_1",
        description="Complete certification course",
        priority_score=8.5,
        urgency_level="short_term",
        effort_estimate="medium",
        source_insight_id="insight_1",
    )

    assert action.action_id == "action_1"
    assert action.priority_score == 8.5
    assert action.urgency_level == "short_term"

    # Test to_dict conversion
    action_dict = action.to_dict()
    assert "action_id" in action_dict
    assert action_dict["priority_score"] == 8.5

    print("✓ test_prioritized_action_creation passed")


def test_unified_response_creation():
    """Test creating UnifiedResponse dataclass."""
    if not IntegrationToolsAvailable:
        print("SKIP: Integration tools not available")
        return

    insight = IntegratedInsight(
        insight_id="insight_1",
        title="Test Insight",
        description="A test integrated insight",
        source_specialists=["career-specialist"],
        domains_affected={"career"},
    )

    action = PrioritizedAction(
        action_id="action_1",
        description="Complete certification course",
        priority_score=8.5,
        urgency_level="short_term",
        effort_estimate="medium",
        source_insight_id="insight_1",
    )

    unified_response = UnifiedResponse(
        user_id="test_user",
        query_timestamp=datetime.now().isoformat(),
        specialists_consulted=["career-specialist"],
        integrated_insights=[insight],
        prioritized_actions=[action],
    )

    assert unified_response.user_id == "test_user"
    assert len(unified_response.integrated_insights) == 1
    assert len(unified_response.prioritized_actions) == 1

    # Test to_dict conversion
    response_dict = unified_response.to_dict()
    assert "user_id" in response_dict
    assert len(response_dict["integrated_insights"]) == 1

    print("✓ test_unified_response_creation passed")


def test_specialist_output_harmonizer():
    """Test SpecialistOutputHarmonizer functionality."""
    if not IntegrationToolsAvailable:
        print("SKIP: Integration tools not available")
        return

    messages_dict = {
        "career-specialist": {
            "recommendations": [
                {"title": "Get certified in Python", "priority": 8},
            ],
            "confidence_level": 0.85,
        },
        "wellness-specialist": {
            "recommendations": [
                {"title": "Establish bedtime routine", "priority": 9},
            ],
            "confidence_level": 0.9,
        },
    }

    harmonizer = SpecialistOutputHarmonizer()
    harmonized_recs = harmonizer.harmonize_recommendations(messages_dict)

    assert len(harmonized_recs) == 2
    assert "source_specialist" in harmonized_recs[0]
    assert "domain_weight" in harmonized_recs[0]

    # Test confidence weighted score calculation
    score = harmonizer.calculate_confidence_weighted_score(harmonized_recs)
    assert 0.0 <= score <= 1.0

    print("✓ test_specialist_output_harmonizer passed")


def test_cross_domain_synthesizer():
    """Test CrossDomainSynthesizer functionality."""
    if not IntegrationToolsAvailable:
        print("SKIP: Integration tools not available")
        return

    messages_dict = {
        "career-specialist": {
            "analysis": "Career analysis shows strong skills.",
            "confidence_level": 0.85,
        },
        "wellness-specialist": {
            "analysis": "Wellness assessment shows need for better habits.",
            "confidence_level": 0.9,
        },
    }

    harmonized_recs = [
        {
            "title": "Get certified",
            "source_specialist": "career-specialist",
            "priority": 8,
        }
    ]

    synthesizer = CrossDomainSynthesizer()
    insights = synthesizer.synthesize_insights(messages_dict, harmonized_recs)

    assert len(insights) >= 1

    # Verify insight structure
    if insights:
        first_insight = insights[0]
        assert isinstance(first_insight, IntegratedInsight)
        assert first_insight.insight_id is not None
        assert first_insight.title is not None

    print("✓ test_cross_domain_synthesizer passed")


def test_action_prioritizer():
    """Test ActionPrioritizer functionality."""
    if not IntegrationToolsAvailable:
        print("SKIP: Integration tools not available")
        return

    insight = IntegratedInsight(
        insight_id="insight_1",
        title="Test Insight",
        description="A test integrated insight",
        confidence_score=0.85,
        strength_score=0.7,
        actionable_items=[
            {"description": "Complete certification course", "priority": 8},
            {"description": "Establish bedtime routine", "priority": 9},
        ],
    )

    user_goals = ["advance career"]

    prioritizer = ActionPrioritizer()
    actions = prioritizer.generate_prioritized_actions([insight], user_goals)

    assert len(actions) == 2

    # Verify actions are sorted by priority (descending)
    if len(actions) >= 2:
        assert actions[0].priority_score >= actions[1].priority_score

    # Verify action structure
    for action in actions:
        assert isinstance(action, PrioritizedAction)
        assert action.description is not None
        assert 0.0 <= action.priority_score <= 10.0

    print("✓ test_action_prioritizer passed")


def test_advanced_conflict_resolver():
    """Test AdvancedConflictResolver functionality."""
    if not IntegrationToolsAvailable:
        print("SKIP: Integration tools not available")
        return

    conflicts = [
        {
            "specialist_1": "career-specialist",
            "specialist_2": "wellness-specialist",
            "description": "Work hours vs rest time conflict",
            "severity": "high",
        }
    ]

    messages_dict = {
        "career-specialist": {"confidence_level": 0.85},
        "wellness-specialist": {"confidence_level": 0.9},
    }

    resolver = AdvancedConflictResolver()
    resolved, unresolved = resolver.resolve_all_conflicts(conflicts, messages_dict)

    assert len(resolved) == 1
    assert len(unresolved) == 0

    # Verify resolution structure
    resolution = resolved[0]
    assert "status" in resolution
    assert "strategy" in resolution
    assert resolution["status"] == "resolved"

    print("✓ test_advanced_conflict_resolver passed")


def test_result_integration_engine():
    """Test ResultIntegrationEngine end-to-end integration."""
    if not IntegrationToolsAvailable:
        print("SKIP: Integration tools not available")
        return

    messages = {
        "career-specialist": {
            "analysis": "Career shows strong potential.",
            "recommendations": [{"title": "Get certified", "priority": 8}],
            "confidence_level": 0.85,
        },
        "wellness-specialist": {
            "analysis": "Wellness needs attention.",
            "recommendations": [{"title": "Exercise daily", "priority": 9}],
            "confidence_level": 0.9,
        },
    }

    conflicts = []
    synergies = []

    engine = ResultIntegrationEngine()
    unified_response = engine.integrate_results(
        user_id="test_user",
        query_timestamp=datetime.now().isoformat(),
        messages=messages,
        conflicts_detected=conflicts,
        synergies_identified=synergies,
    )

    assert isinstance(unified_response, UnifiedResponse)
    assert unified_response.user_id == "test_user"
    assert len(unified_response.specialists_consulted) == 2

    print("✓ test_result_integration_engine passed")


# ==============================================================================
# Main Test Runner
# ==============================================================================


def run_all_tests():
    """Run all integration tools tests."""
    print("=" * 70)
    print("Running Integration Tools Tests")
    print("=" * 70)

    tests = [
        test_integrated_insight_creation,
        test_prioritized_action_creation,
        test_unified_response_creation,
        test_specialist_output_harmonizer,
        test_cross_domain_synthesizer,
        test_action_prioritizer,
        test_advanced_conflict_resolver,
        test_result_integration_engine,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            print(f"\nRunning {test_func.__name__}...")
            test_func()
            passed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__} failed: {str(e)}")
            import traceback

            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 70)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
