#!/usr/bin/env python3
"""
Demo script for Emergency Support Protocol.

This script demonstrates the crisis detection and response capabilities
of the AI Life Coach emergency support system.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Initialize environment
from src.config import config

config.initialize_environment()

from src.tools.emergency_tools import (
    create_emergency_tools,
    detect_crisis_keywords,
    CrisisLevel,
    CrisisType,
)


def demo_crisis_detection():
    """Demonstrate crisis keyword detection."""
    print("=" * 70)
    print("🚨 EMERGENCY SUPPORT PROTOCOL DEMO")
    print("=" * 70)
    print()

    # Test messages at different crisis levels
    test_messages = [
        ("I'm having a wonderful day today!", "No crisis - normal message"),
        ("I've been feeling a bit down lately", "No crisis - mild concern"),
        ("I'm feeling hopeless about everything", "Moderate - hopelessness"),
        ("I've been having thoughts of suicide", "High - suicidal ideation"),
        ("I want to kill myself tonight", "Critical - suicide plan/intent"),
        ("I'm being abused by my partner", "Critical - abuse"),
        ("I've been cutting myself to cope", "Critical - self-harm"),
    ]

    print("📊 CRISIS DETECTION TESTS")
    print("-" * 70)

    for message, description in test_messages:
        print(f"\n📝 Test: {description}")
        print(f"   Message: '{message}'")

        result = detect_crisis_keywords(message)

        if result.is_crisis:
            print(f"   ⚠️  CRISIS DETECTED!")
            print(f"   Level: {result.crisis_level.value.upper()}")
            print(f"   Types: {', '.join(ct.value for ct in result.crisis_types)}")
            print(f"   Confidence: {result.confidence_score * 100:.1f}%")
            print(f"   Immediate Action Required: {result.requires_immediate_action}")
            if result.matched_keywords:
                print(f"   Matched Keywords: {', '.join(result.matched_keywords[:3])}")
        else:
            print(f"   ✅ No crisis indicators detected")

    print()


def demo_emergency_tools():
    """Demonstrate emergency tools."""
    print()
    print("=" * 70)
    print("🔧 EMERGENCY TOOLS DEMONSTRATION")
    print("=" * 70)
    print()

    # Get initialized backend
    from src.config import get_backend

    backend = get_backend()

    # Create tools
    (
        analyze_crisis_risk,
        get_immediate_resources,
        create_safety_plan,
        get_safety_plan_template,
        schedule_followup_checkin,
        complete_followup_checkin,
        get_crisis_protocol_guidance,
        generate_crisis_response,
    ) = create_emergency_tools(backend=backend)

    # Demo 1: Analyze Crisis Risk
    print("\n1️⃣  ANALYZE CRISIS RISK")
    print("-" * 70)
    result = analyze_crisis_risk.invoke({"user_message": "I've been thinking about ending my life"})
    print(result)

    # Demo 2: Get Immediate Resources
    print("\n2️⃣  GET IMMEDIATE RESOURCES")
    print("-" * 70)
    result = get_immediate_resources.invoke({"crisis_types": ["suicide_ideation"]})
    print(result)

    # Demo 3: Generate Crisis Response
    print("\n3️⃣  GENERATE CRISIS RESPONSE")
    print("-" * 70)
    result = generate_crisis_response.invoke(
        {"crisis_level": "critical", "crisis_types": ["suicide_ideation"]}
    )
    print(result)

    # Demo 4: Get Safety Plan Template
    print("\n4️⃣  SAFETY PLAN TEMPLATE (excerpt)")
    print("-" * 70)
    result = get_safety_plan_template.invoke({})
    # Print just the first few sections
    lines = result.split("\n")[:40]
    print("\n".join(lines))
    print("\n... (template continues with all 7 sections)")

    # Demo 5: Crisis Protocol Guidance (excerpt)
    print("\n\n5️⃣  CRISIS PROTOCOL GUIDANCE (excerpt)")
    print("-" * 70)
    result = get_crisis_protocol_guidance.invoke({})
    # Print just the first part
    lines = result.split("\n")[:50]
    print("\n".join(lines))
    print("\n... (guidance continues with full protocol)")


def demo_safety_plan_creation():
    """Demonstrate safety plan creation."""
    print()
    print("=" * 70)
    print("🛡️  SAFETY PLAN CREATION DEMO")
    print("=" * 70)
    print()

    from src.config import get_backend

    backend = get_backend()

    (
        analyze_crisis_risk,
        get_immediate_resources,
        create_safety_plan,
        get_safety_plan_template,
        schedule_followup_checkin,
        complete_followup_checkin,
        get_crisis_protocol_guidance,
        generate_crisis_response,
    ) = create_emergency_tools(backend=backend)

    # Create a sample safety plan
    result = create_safety_plan.invoke(
        {
            "user_id": "demo_user",
            "warning_signs": [
                "Feeling overwhelmed at work",
                "Can't sleep at night",
                "Isolating from friends",
            ],
            "coping_strategies": [
                "Go for a 20-minute walk",
                "Listen to calming music",
                "Write in my journal",
                "Practice deep breathing",
            ],
            "social_contacts": [
                {"name": "Sarah (Best Friend)", "phone": "555-0123"},
                {"name": "Mom", "phone": "555-0456"},
            ],
            "professional_contacts": [{"name": "Dr. Johnson (Therapist)", "phone": "555-0789"}],
            "reasons_for_living": [
                "My family loves me",
                "I want to see my niece grow up",
                "My dog needs me",
                "I have goals I haven't achieved yet",
            ],
        }
    )

    print(result)


def main():
    """Run all demos."""
    try:
        demo_crisis_detection()
        demo_emergency_tools()
        demo_safety_plan_creation()

        print()
        print("=" * 70)
        print("✅ DEMO COMPLETE")
        print("=" * 70)
        print()
        print("Key Takeaways:")
        print("  • Crisis detection works at multiple severity levels")
        print("  • Immediate resources are provided based on crisis type")
        print("  • Safety plans can be personalized for each user")
        print("  • Follow-up check-ins help ensure continued support")
        print()
        print("⚠️  IMPORTANT SAFETY NOTES:")
        print("  • This system is for educational/development purposes")
        print("  • Always refer users to professional crisis resources")
        print("  • Never attempt to handle suicidal ideation without professional help")
        print("  • Call 988 or 911 for immediate emergencies")
        print()

    except Exception as e:
        print(f"\n❌ Error running demo: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
