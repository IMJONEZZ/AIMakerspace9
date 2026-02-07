#!/usr/bin/env python3
"""
Demo script for Wellness Specialist agent.

Scenario: "I have trouble sleeping due to work stress"

Run with:
    python demos/demo_wellness_specialist.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents import get_wellness_specialist
from src.tools.memory_tools import create_memory_tools
from src.tools.context_tools import create_context_tools
from src.tools.wellness_tools import create_wellness_tools
from src.memory import create_memory_store, UserProfile, MemoryManager
from deepagents.backends import FilesystemBackend


def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demonstrate_wellness_specialist():
    """Demonstrate the Wellness Specialist agent."""
    print_section("AI Life Coach - Wellness Specialist Demo")
    print("\nScenario: 'I have trouble sleeping due to work stress'")
    print("User ID: demo_user_004")

    # Initialize
    print("\n[1] Initializing Wellness Specialist...")
    memory_store = create_memory_store()
    memory_manager = MemoryManager(memory_store)
    memory_tools = create_memory_tools(memory_store)
    backend = FilesystemBackend(root_dir="./demos/workspace")
    context_tools = create_context_tools(backend=backend)
    wellness_tools = create_wellness_tools(backend=backend)

    well_specialist = get_wellness_specialist()
    well_specialist["tools"] = list(memory_tools) + list(context_tools) + list(wellness_tools)

    print(f"   ✓ Specialist: {well_specialist['name']}")
    print(f"   ✓ Tools available: {len(well_specialist['tools'])}")

    # Create profile
    print("\n[2] Creating User Profile...")
    demo_profile = UserProfile(
        user_id="demo_user_004", name="Morgan Davis", occupation="Senior Developer"
    )
    memory_manager.save_profile(demo_profile)
    print(f"   ✓ Profile created for Morgan Davis")

    # Demonstrate sleep optimization
    print_section("[3] Demonstrating: Sleep Optimization Plan")

    sleep_tool = None
    for tool in well_specialist["tools"]:
        name = tool.name if hasattr(tool, "name") else str(tool)
        if "sleep" in name:
            sleep_tool = tool
            break

    print("\nInput Parameters:")
    print("   - Sleep Issue: Trouble falling asleep due to work stress")
    print("   - Typical Bedtime: 11:00 PM")
    print("   - Wake Time: 6:30 AM")

    result = sleep_tool.invoke(
        {
            "user_id": "demo_user_004",
            "sleep_issue": "trouble falling asleep due to work stress",
            "typical_bedtime": "23:00",
            "wake_time": "06:30",
        }
    )

    print("\nOutput (Sleep Optimization Plan):")
    print("-" * 70)
    preview = result[:600] + "..." if len(result) > 600 else result
    print(preview)
    print("-" * 70)

    # Demonstrate stress management
    print_section("[4] Demonstrating: Stress Management Techniques")

    stress_tool = None
    for tool in well_specialist["tools"]:
        name = tool.name if hasattr(tool, "name") else str(tool)
        if "stress" in name:
            stress_tool = tool
            break

    print("\nInput Parameters:")
    print("   - Stress Type: Work-related stress")
    print("   - Symptoms: Racing thoughts, tension")

    result = stress_tool.invoke(
        {
            "user_id": "demo_user_004",
            "stress_type": "work_stress",
            "symptoms": ["racing thoughts", "muscle tension"],
            "time_available_minutes": 10,
        }
    )

    print("\nOutput (Stress Management Techniques):")
    print("-" * 70)
    preview = result[:600] + "..." if len(result) > 600 else result
    print(preview)
    print("-" * 70)

    # Domain boundaries
    print_section("[5] Domain Boundaries")
    prompt = well_specialist["system_prompt"].lower()
    print(
        f"\n✓ Medical disclaimer included: {'not medical advice' in prompt or 'general wellness guidance only' in prompt}"
    )
    print(
        f"✓ Referral to professional included: {'medical professional' in prompt or 'healthcare provider' in prompt}"
    )
    print(f"✓ Crisis resources included: {'988' in prompt or 'suicide prevention' in prompt}")

    # Summary
    print_section("[6] Demo Summary")
    print("""
✓ Configured with proper tools (memory + context + wellness-specific)
✓ Created sleep optimization plan for work stress
✓ Provided stress management techniques
✓ Included proper medical disclaimers and crisis resources

Key Capabilities:
- Sleep hygiene and optimization
- Stress management strategies (immediate + ongoing)
- Habit formation support
- Work-life balance guidance

Important:
- General wellness guidance only (not medical advice)
- Crisis resources provided for severe distress
    """)


if __name__ == "__main__":
    demonstrate_wellness_specialist()
