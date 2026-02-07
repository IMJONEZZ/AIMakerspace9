"""
Demo of Subagent Communication Protocol for AI Life Coach.

This script demonstrates how the communication protocol works between
specialist subagents and the coordinator agent.

It shows:
1. Formatting specialist messages in standardized format
2. Aggregating results from multiple specialists
3. Detecting and resolving conflicts between recommendations
4. Identifying cross-consultation needs
5. Generating unified responses

This is a standalone demo that doesn't require the full AI Life Coach system.
"""

import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import and initialize config
from src.config import config, get_backend

config.initialize_environment()
backend = get_backend()

# Import communication tools
from src.tools.communication_tools import (
    create_communication_tools,
    SpecialistMessage,
)


def main():
    """Run the communication protocol demo."""
    print("\n" + "=" * 70)
    print("  AI LIFE COACH - SUBAGENT COMMUNICATION PROTOCOL DEMO")
    print("=" * 70)

    # Create communication tools
    format_msg, agg_results, resolve_conflicts, detect_consult, gen_unified = (
        create_communication_tools(backend)
    )

    # Scenario: User wants to balance career advancement with family life
    user_query = (
        "I've just been offered a promotion that would increase my salary by 30% "
        "but requires longer hours and some travel. I'm worried about the impact "
        "on my family life and stress levels. What should I do?"
    )

    user_id = "demo_user_001"

    print(f"\nUser Query:\n  {user_query}\n")
    print("=" * 70)

    # ========================================================================
    # STEP 1: Specialists provide their analyses
    # ========================================================================

    print("\n[STEP 1] SPECIALISTS PROVIDING ANALYSES")
    print("-" * 70)

    # Career Specialist analysis
    career_analysis = format_msg.invoke(
        {
            "specialist_name": "career-specialist",
            "user_query": user_query,
            "analysis": (
                "This promotion represents a significant career advancement opportunity. "
                "The 30% salary increase provides financial benefits and positions you well "
                "for future growth. However, the longer hours and travel requirements will "
                "reduce availability for family time. This is a classic career-life balance "
                "decision that requires careful consideration of priorities."
            ),
            "recommendations": [
                {
                    "title": "Negotiate flexible work arrangements",
                    "priority": 9,
                    "description": "Discuss options for remote work, adjusted hours, or reduced travel frequency",
                },
                {
                    "title": "Establish clear work boundaries",
                    "priority": 8,
                    "description": "Set specific start/end times and protected family time",
                },
                {
                    "title": "Create a 6-month trial period",
                    "priority": 7,
                    "description": "Accept promotion with agreement to review impact after 6 months",
                },
            ],
            "synergies_with_other_domains": [
                {
                    "domain": "finance-specialist",
                    "description": "Higher income enables better financial security and goal achievement",
                    "strength": 0.9,
                }
            ],
            "conflicts_with_other_domains": [
                {
                    "domain": "relationship-specialist",
                    "description": "Reduced availability may strain family relationships",
                    "severity": "high",
                },
                {
                    "domain": "wellness-specialist",
                    "description": "Increased work hours may elevate stress and reduce recovery time",
                    "severity": "medium",
                },
            ],
            "confidence_level": 0.85,
            "requires_cross_consultation": True,
            "metadata": {"user_id": user_id},
        }
    )

    print("\nCareer Specialist Response:")
    print(career_analysis[:600] + "..." if len(career_analysis) > 600 else career_analysis)

    # Relationship Specialist analysis
    relationship_analysis = format_msg.invoke(
        {
            "specialist_name": "relationship-specialist",
            "user_query": user_query,
            "analysis": (
                "Family relationships thrive on quality time and consistent presence. "
                "The demands of this new role could impact your partner and children if not "
                "managed carefully. However, the financial benefits might relieve other "
                "stressors and provide resources for family activities."
            ),
            "recommendations": [
                {
                    "title": "Schedule protected family time",
                    "priority": 10,
                    "description": "Block specific hours/days that are sacred family time with no work interruptions",
                },
                {
                    "title": "Communicate openly with family",
                    "priority": 9,
                    "description": "Discuss the opportunity and concerns honestly with your partner",
                },
                {
                    "title": "Create family rituals",
                    "priority": 8,
                    "description": "Establish daily or weekly traditions that maintain connection",
                },
            ],
            "synergies_with_other_domains": [
                {
                    "domain": "wellness-specialist",
                    "description": "Strong family support improves overall wellbeing and stress management",
                    "strength": 0.95,
                }
            ],
            "conflicts_with_other_domains": [],
            "confidence_level": 0.9,
            "requires_cross_consultation": True,
            "metadata": {"user_id": user_id},
        }
    )

    print("\n\nRelationship Specialist Response:")
    print(
        relationship_analysis[:600] + "..."
        if len(relationship_analysis) > 600
        else relationship_analysis
    )

    # Wellness Specialist analysis
    wellness_analysis = format_msg.invoke(
        {
            "specialist_name": "wellness-specialist",
            "user_query": user_query,
            "analysis": (
                "Increased work demands and travel can significantly impact stress levels, "
                "sleep quality, and overall wellbeing. Without proper boundaries and self-care, "
                "you risk burnout which would negatively impact both career performance and "
                "family relationships."
            ),
            "recommendations": [
                {
                    "title": "Implement stress management routine",
                    "priority": 9,
                    "description": "Daily practices like meditation, exercise, or journaling to manage stress",
                },
                {
                    "title": "Protect sleep schedule",
                    "priority": 10,
                    "description": "Ensure consistent bedtime and wake time regardless of work demands",
                },
                {
                    "title": "Schedule recovery periods",
                    "priority": 8,
                    "description": "Build in buffer days after travel for rest and reconnection",
                },
            ],
            "synergies_with_other_domains": [
                {
                    "domain": "career-specialist",
                    "description": "Good stress management supports sustained high performance",
                    "strength": 0.85,
                }
            ],
            "conflicts_with_other_domains": [
                {
                    "domain": "career-specialist",
                    "description": "Wellness needs may conflict with demanding work schedule requirements",
                    "severity": "medium",
                }
            ],
            "confidence_level": 0.88,
            "requires_cross_consultation": False,
            "metadata": {"user_id": user_id},
        }
    )

    print("\n\nWellness Specialist Response:")
    print(wellness_analysis[:600] + "..." if len(wellness_analysis) > 600 else wellness_analysis)

    # ========================================================================
    # STEP 2: Aggregate results from all specialists
    # ========================================================================

    print("\n\n[STEP 2] AGGREGATING SPECIALIST RESULTS")
    print("-" * 70)

    aggregation = agg_results.invoke(
        {
            "user_id": user_id,
            "specialist_messages": [
                {
                    "specialist_name": "career-specialist",
                    "user_query": user_query,
                    "analysis": career_analysis,
                    "recommendations": [
                        {"title": "Negotiate flexible work arrangements", "priority": 9},
                        {"title": "Establish clear work boundaries", "priority": 8},
                        {"title": "Create a 6-month trial period", "priority": 7},
                    ],
                    "synergies_with_other_domains": [
                        {
                            "domain": "finance-specialist",
                            "description": "Higher income enables financial security",
                            "strength": 0.9,
                        }
                    ],
                    "conflicts_with_other_domains": [
                        {
                            "domain": "relationship-specialist",
                            "description": "Reduced family availability",
                            "severity": "high",
                        },
                        {
                            "domain": "wellness-specialist",
                            "description": "Increased stress levels",
                            "severity": "medium",
                        },
                    ],
                    "confidence_level": 0.85,
                },
                {
                    "specialist_name": "relationship-specialist",
                    "user_query": user_query,
                    "analysis": relationship_analysis,
                    "recommendations": [
                        {"title": "Schedule protected family time", "priority": 10},
                        {"title": "Communicate openly with family", "priority": 9},
                        {"title": "Create family rituals", "priority": 8},
                    ],
                    "synergies_with_other_domains": [
                        {
                            "domain": "wellness-specialist",
                            "description": "Family support improves wellbeing",
                            "strength": 0.95,
                        }
                    ],
                    "conflicts_with_other_domains": [],
                    "confidence_level": 0.9,
                },
                {
                    "specialist_name": "wellness-specialist",
                    "user_query": user_query,
                    "analysis": wellness_analysis,
                    "recommendations": [
                        {"title": "Implement stress management routine", "priority": 9},
                        {"title": "Protect sleep schedule", "priority": 10},
                        {"title": "Schedule recovery periods", "priority": 8},
                    ],
                    "synergies_with_other_domains": [
                        {
                            "domain": "career-specialist",
                            "description": "Stress management supports performance",
                            "strength": 0.85,
                        }
                    ],
                    "conflicts_with_other_domains": [
                        {
                            "domain": "career-specialist",
                            "description": "Wellness needs vs work schedule",
                            "severity": "medium",
                        }
                    ],
                    "confidence_level": 0.88,
                },
            ],
        }
    )

    print(aggregation)

    # ========================================================================
    # STEP 3: Detect cross-consultation needs
    # ========================================================================

    print("\n[STEP 3] DETECTING CROSS-CONSULTATION NEEDS")
    print("-" * 70)

    consultation = detect_consult.invoke({"user_id": user_id})

    print(consultation)

    # ========================================================================
    # STEP 4: Resolve conflicts
    # ========================================================================

    print("\n[STEP 4] RESOLVING CONFLICTS")
    print("-" * 70)

    resolution = resolve_conflicts.invoke({"user_id": user_id, "resolution_strategy": "hybrid"})

    print(resolution)

    # ========================================================================
    # STEP 5: Generate unified response
    # ========================================================================

    print("\n[STEP 5] GENERATING UNIFIED RESPONSE")
    print("-" * 70)

    unified = gen_unified.invoke({"user_id": user_id, "resolution_strategy": "hybrid"})

    print(unified)

    # ========================================================================
    # SUMMARY
    # ========================================================================

    print("\n" + "=" * 70)
    print("  DEMO SUMMARY")
    print("=" * 70)

    print("""
The Subagent Communication Protocol successfully:

1. ✓ Formatted standardized messages from 3 specialists
2. ✓ Aggregated results identifying conflicts and synergies
3. ✓ Detected cross-consultation needs between specialists
4. ✓ Resolved conflicts using hybrid strategy (priority + consensus)
5. ✓ Generated cohesive unified response integrating all insights

This demonstrates how the AI Life Coach coordinator can:
- Collect structured input from multiple domain specialists
- Identify when recommendations conflict or complement each other
- Apply intelligent resolution strategies to handle disagreements
- Present users with integrated, actionable guidance

All communication is logged and can be reviewed for transparency.
Files are saved to workspace directory for persistence across sessions.
""")


if __name__ == "__main__":
    main()
