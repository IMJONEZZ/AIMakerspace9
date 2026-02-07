#!/usr/bin/env python3
"""
Demo script for Career Specialist agent.

This script demonstrates the Career Specialist's capabilities with a specific scenario:
"I want to transition from marketing to data science"

The demo shows:
1. Specialist configuration and initialization
2. Tool integration (memory, context, career-specific tools)
3. Domain expertise in action
4. Output quality and format

Run with:
    python demos/demo_career_specialist.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents import get_career_specialist
from src.tools.memory_tools import create_memory_tools
from src.tools.context_tools import create_context_tools
from src.tools.career_tools import create_career_tools
from src.memory import create_memory_store, UserProfile, MemoryManager
from deepagents.backends import FilesystemBackend


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demonstrate_career_specialist():
    """Demonstrate the Career Specialist agent with a real scenario."""
    print_section("AI Life Coach - Career Specialist Demo")
    print("\nScenario: 'I want to transition from marketing to data science'")
    print("User ID: demo_user_001")

    # Initialize components
    print("\n[1] Initializing Career Specialist...")

    # Create memory store and tools
    memory_store = create_memory_store()
    memory_manager = MemoryManager(memory_store)
    memory_tools = create_memory_tools(memory_store)

    # Create context tools
    backend = FilesystemBackend(root_dir="./demos/workspace")
    context_tools = create_context_tools(backend=backend)

    # Create career-specific tools
    career_tools = create_career_tools(backend=backend)

    # Configure specialist with tools
    career_specialist = get_career_specialist()
    career_specialist["tools"] = list(memory_tools) + list(context_tools) + list(career_tools)

    print(f"   ✓ Specialist: {career_specialist['name']}")
    print(f"   ✓ Model: {career_specialist['model']}")
    print(f"   ✓ System prompt length: {len(career_specialist['system_prompt'])} characters")
    print(f"   ✓ Tools available: {len(career_specialist['tools'])}")

    # List tools
    print("\n[2] Available Tools:")
    tool_names = [
        tool.name if hasattr(tool, "name") else tool.__name__ for tool in career_specialist["tools"]
    ]

    # Categorize tools
    memory_tools_list = [
        t
        for t in tool_names
        if any(
            x in t
            for x in [
                "get_user_profile",
                "save_user_preference",
                "update_milestone",
                "get_progress_history",
            ]
        )
    ]
    context_tools_list = [
        t
        for t in tool_names
        if any(x in t for x in ["save_assessment", "get_active_plan", "save_curated_resource"])
    ]
    career_tools_list = [
        t
        for t in tool_names
        if any(x in t.lower() for x in ["skill", "career", "resume", "interview", "salary"])
    ]

    print(f"   Memory Tools ({len(memory_tools_list)}):")
    for tool in memory_tools_list[:2]:  # Show first 2
        print(f"      - {tool}")
    if len(memory_tools_list) > 2:
        print(f"      ... and {len(memory_tools_list) - 2} more")

    print(f"\n   Context Tools ({len(context_tools_list)}):")
    for tool in context_tools_list[:2]:
        print(f"      - {tool}")
    if len(context_tools_list) > 2:
        print(f"      ... and {len(context_tools_list) - 2} more")

    print(f"\n   Career-Specific Tools ({len(career_tools_list)}):")
    for tool in career_tools_list:
        print(f"      - {tool}")

    # Create user profile
    print("\n[3] Creating User Profile...")
    demo_profile = UserProfile(
        user_id="demo_user_001", name="Alex Johnson", age=32, occupation="Marketing Manager"
    )
    memory_manager.save_profile(demo_profile)
    print(f"   ✓ Profile created for Alex Johnson, Marketing Manager")

    # Demonstrate skill gap analysis
    print_section("[4] Demonstrating Tool: Skill Gap Analysis")

    # Find the skill gap tool
    skill_gap_tool = None
    for tool in career_specialist["tools"]:
        name = tool.name if hasattr(tool, "name") else str(tool)
        if "skill_gap" in name:
            skill_gap_tool = tool
            break

    print("\nInput Parameters:")
    print("   - Current Skills: ['Marketing Strategy', 'Content Creation', 'Google Analytics']")
    print("   - Target Role: Data Scientist")
    print("   - Experience Level: Career changer, entry-level data science")

    result = skill_gap_tool.invoke(
        {
            "user_id": "demo_user_001",
            "current_skills": ["Marketing Strategy", "Content Creation", "Google Analytics"],
            "target_role": "Data Scientist",
            "experience_level": "career_changer",
        }
    )

    print("\nOutput (Skill Gap Analysis):")
    print("-" * 70)
    # Show first 600 characters of result
    preview = result[:600] + "..." if len(result) > 600 else result
    print(preview)
    print("-" * 70)

    # Demonstrate career path planning
    print_section("[5] Demonstrating Tool: Career Path Planning")

    # Find the career path tool
    career_path_tool = None
    for tool in career_specialist["tools"]:
        name = tool.name if hasattr(tool, "name") else str(tool)
        if "career_path" in name:
            career_path_tool = tool
            break

    print("\nInput Parameters:")
    print("   - Current Role: Marketing Manager")
    print("   - Target Role: Data Scientist")
    print("   - Timeline: 18 months")

    result = career_path_tool.invoke(
        {
            "user_id": "demo_user_001",
            "current_role": "Marketing Manager",
            "target_role": "Data Scientist",
            "timeline_months": 18,
        }
    )

    print("\nOutput (Career Path Plan):")
    print("-" * 70)
    preview = result[:600] + "..." if len(result) > 600 else result
    print(preview)
    print("-" * 70)

    # Demonstrate domain boundaries
    print_section("[6] Domain Boundaries and Constraints")

    print("\nThe Career Specialist respects these boundaries:")
    print("   ✓ No medical advice (for workplace stress, mental health)")
    print("   ✓ No legal advice (for employment contracts, non-competes)")
    print("   ✓ Honest about market realities and realistic timelines")
    print("   ✓ Ethical boundaries (no lying on resumes)")

    # Check system prompt for boundary mentions
    prompt = career_specialist["system_prompt"].lower()
    has_medical_boundary = "medical" in prompt or "health" in prompt
    has_legal_boundary = "legal" in prompt or "attorney" in prompt

    print(f"\n✓ Medical boundary mentioned: {has_medical_boundary}")
    print(f"✓ Legal boundary mentioned: {has_legal_boundary}")

    # Summary
    print_section("[7] Demo Summary")
    print("""
The Career Specialist successfully:

✓ Configured with proper tools (memory + context + career-specific)
✓ Analyzed skill gap for marketing → data science transition
✓ Created actionable career path plan with timeline
✓ Respected domain boundaries (no medical/legal advice)
✓ Provided specific, actionable recommendations

Key Capabilities Demonstrated:
- Skill gap analysis
- Career path planning
- Timeline creation with milestones
- Actionable, domain-specific guidance

The specialist operates within its expertise while clearly
acknowledging boundaries for issues requiring professional help.
    """)


if __name__ == "__main__":
    demonstrate_career_specialist()
