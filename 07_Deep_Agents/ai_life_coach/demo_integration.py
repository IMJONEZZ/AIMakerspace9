"""
Demonstration of Result Integration Tools.

This script demonstrates the end-to-end functionality of the integration system:
1. Specialist output harmonization
2. Cross-domain insight synthesis
3. Prioritized action list generation
4. Unified response creation

Run with: python demo_integration.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime

# Import integration tools
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


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def demonstrate_integration():
    """Demonstrate the complete integration workflow."""

    # ==============================================================================
    # Step 1: Create sample specialist messages
    # ==============================================================================

    print_section("Step 1: Sample Specialist Messages")

    specialist_messages = {
        "career-specialist": {
            "specialist_name": "career-specialist",
            "timestamp": datetime.now().isoformat(),
            "analysis": (
                "Career assessment shows strong technical skills in Python and data analysis. "
                "Current role allows for growth but lacks clear advancement path. "
                "Key opportunity: transitioning to data science with 6-12 month timeline."
            ),
            "recommendations": [
                {"title": "Complete data science certification", "priority": 9},
                {"title": "Build portfolio of data projects", "priority": 8},
                {"title": "Apply for internal transfer to analytics team", "priority": 7},
            ],
            "confidence_level": 0.85,
        },
        "wellness-specialist": {
            "specialist_name": "wellness-specialist",
            "timestamp": datetime.now().isoformat(),
            "analysis": (
                "Wellness assessment reveals adequate physical health but suboptimal sleep quality. "
                "Average 6 hours/night with frequent interruptions. "
                "Stress levels elevated, particularly during work periods."
            ),
            "recommendations": [
                {"title": "Establish consistent bedtime routine (10:30 PM)", "priority": 9},
                {"title": "Limit screen exposure after 9 PM", "priority": 8},
                {"title": "Practice evening meditation for stress reduction", "priority": 7},
            ],
            "confidence_level": 0.9,
        },
        "finance-specialist": {
            "specialist_name": "finance-specialist",
            "timestamp": datetime.now().isoformat(),
            "analysis": (
                "Financial analysis shows stable income with opportunity for increased savings. "
                "Current emergency fund covers 3 months expenses (target: 6 months). "
                "Good debt management, but limited investment portfolio."
            ),
            "recommendations": [
                {"title": "Increase emergency fund to 6 months expenses", "priority": 8},
                {"title": "Open low-cost index fund investment account", "priority": 7},
                {"title": "Review and optimize recurring expenses", "priority": 6},
            ],
            "confidence_level": 0.88,
        },
    }

    for specialist, data in specialist_messages.items():
        print(f"\n{specialist.replace('-', ' ').title()}:")
        print(f"  Confidence: {data['confidence_level']:.1%}")
        print(f"  Recommendations: {len(data['recommendations'])}")

    # ==============================================================================
    # Step 2: Harmonize specialist outputs
    # ==============================================================================

    print_section("Step 2: Specialist Output Harmonization")

    harmonizer = SpecialistOutputHarmonizer()
    harmonized_recommendations = harmonizer.harmonize_recommendations(specialist_messages)

    print(f"\nTotal recommendations (after harmonization): {len(harmonized_recommendations)}")
    print("\nTop Recommendations:")
    for i, rec in enumerate(harmonized_recommendations[:5], 1):
        source = rec.get("source_specialist", "").replace("-specialist", "").title()
        priority = rec.get("priority", 0)
        print(f"  {i}. {rec['title']} (from {source}, Priority: {priority})")

    # ==============================================================================
    # Step 3: Resolve conflicts
    # ==============================================================================

    print_section("Step 3: Conflict Resolution")

    conflicts = [
        {
            "specialist_1": "career-specialist",
            "specialist_2": "wellness-specialist",
            "description": (
                "Career advancement requires additional study time "
                "vs wellness need for adequate sleep and rest"
            ),
            "severity": "medium",
        }
    ]

    resolver = AdvancedConflictResolver()
    resolved_conflicts, _ = resolver.resolve_all_conflicts(conflicts, specialist_messages)

    print(f"\nConflicts detected: {len(conflicts)}")
    print("Resolved:")
    for resolution in resolved_conflicts:
        strategy = resolution.get("strategy", "N/A").replace("_", " ").title()
        rationale = resolution.get("rationale", "")
        print(f"  • Strategy: {strategy}")
        print(f"    Rationale: {rationale}")

    # ==============================================================================
    # Step 4: Synthesize cross-domain insights
    # ==============================================================================

    print_section("Step 4: Cross-Domain Insight Synthesis")

    synthesizer = CrossDomainSynthesizer()
    integrated_insights = synthesizer.synthesize_insights(
        specialist_messages, harmonized_recommendations
    )

    print(f"\nIntegrated insights generated: {len(integrated_insights)}")
    for i, insight in enumerate(integrated_insights[:5], 1):
        domains = ", ".join(list(insight.domains_affected))
        print(f"\n{i}. {insight.title}")
        print(f"   Domains: {domains}")
        print(
            f"   Confidence: {insight.confidence_score:.1%} | Strength: {insight.strength_score:.1%}"
        )
        print(f"   Description: {insight.description[:100]}...")

    # ==============================================================================
    # Step 5: Generate prioritized actions
    # ==============================================================================

    print_section("Step 5: Prioritized Action List Generation")

    user_goals = ["advance career", "improve health and wellness"]

    prioritizer = ActionPrioritizer()
    prioritized_actions = prioritizer.generate_prioritized_actions(integrated_insights, user_goals)

    print(f"\nUser Goals: {', '.join(user_goals)}")
    print(f"Total actions generated: {len(prioritized_actions)}")

    # Group by urgency
    actions_by_urgency = {}
    for action in prioritized_actions:
        urgency = action.urgency_level
        if urgency not in actions_by_urgency:
            actions_by_urgency[urgency] = []
        actions_by_urgency[urgency].append(action)

    for urgency in ["immediate", "short_term", "medium_term", "long_term"]:
        if urgency not in actions_by_urgency:
            continue

        urgency_title = urgency.replace("_", " ").title()
        print(f"\n{urgency_title} Actions:")
        for i, action in enumerate(actions_by_urgency[urgency], 1):
            print(f"  {i}. {action.description}")
            print(
                f"     Priority: {action.priority_score:.1f}/10, Effort: {action.effort_estimate}"
            )

    # ==============================================================================
    # Step 6: Create unified response
    # ==============================================================================

    print_section("Step 6: Unified Response Generation")

    engine = ResultIntegrationEngine()

    synergies_identified = [
        {
            "specialist": "career-specialist",
            "domain": "wellness-specialist",
            "description": "Better sleep quality improves cognitive performance and learning efficiency for skill development",
            "strength": 0.85,
        },
        {
            "specialist": "career-specialist",
            "domain": "finance-specialist",
            "description": "Career advancement leads to higher income potential for increased savings and investments",
            "strength": 0.8,
        },
    ]

    unified_response = engine.integrate_results(
        user_id="demo_user",
        query_timestamp=datetime.now().isoformat(),
        messages=specialist_messages,
        conflicts_detected=conflicts,
        synergies_identified=synergies_identified,
        user_goals=user_goals,
    )

    print(f"\nSpecialists Consulted: {len(unified_response.specialists_consulted)}")
    print(f"Integrated Insights: {len(unified_response.integrated_insights)}")
    print(f"Prioritized Actions: {len(unified_response.prioritized_actions)}")
    print(f"Overall Confidence: {unified_response.overall_confidence:.1%}")

    # ==============================================================================
    # Summary
    # ==============================================================================

    print_section("Integration Complete")

    print("\n✓ Successfully demonstrated:")
    print("  1. Specialist output harmonization")
    print("  2. Conflict resolution strategies")
    print("  3. Cross-domain insight synthesis")
    print("  4. Prioritized action list generation")
    print("  5. Unified response creation")

    print("\nKey Benefits:")
    print("  • Harmonized recommendations from multiple specialists")
    print("  • Resolved conflicts between competing advice")
    print("  • Integrated insights connecting different life domains")
    print("  • Prioritized, actionable steps with urgency levels")
    print("  • Coherent, user-friendly unified response")

    return unified_response


if __name__ == "__main__":
    try:
        result = demonstrate_integration()
        print("\n" + "=" * 70)
        print("Demo completed successfully!")
        print("=" * 70)
    except Exception as e:
        print(f"\n✗ Demo failed: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
