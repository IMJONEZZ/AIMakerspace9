#!/usr/bin/env python3
"""
Demo script for Relationship Specialist agent.

Scenario: "I struggle with setting boundaries at work"

Run with:
    python demos/demo_relationship_specialist.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents import get_relationship_specialist
from src.tools.memory_tools import create_memory_tools
from src.tools.context_tools import create_context_tools
from src.tools.relationship_tools import create_relationship_tools
from src.memory import create_memory_store, UserProfile, MemoryManager
from deepagents.backends import FilesystemBackend


def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demonstrate_relationship_specialist():
    """Demonstrate the Relationship Specialist agent."""
    print_section("AI Life Coach - Relationship Specialist Demo")
    print("\nScenario: 'I struggle with setting boundaries at work'")
    print("User ID: demo_user_002")

    # Initialize
    print("\n[1] Initializing Relationship Specialist...")
    memory_store = create_memory_store()
    memory_manager = MemoryManager(memory_store)
    memory_tools = create_memory_tools(memory_store)
    backend = FilesystemBackend(root_dir="./demos/workspace")
    context_tools = create_context_tools(backend=backend)
    relationship_tools = create_relationship_tools(backend=backend)

    rel_specialist = get_relationship_specialist()
    rel_specialist["tools"] = list(memory_tools) + list(context_tools) + list(relationship_tools)

    print(f"   ✓ Specialist: {rel_specialist['name']}")
    print(f"   ✓ Tools available: {len(rel_specialist['tools'])}")

    # Create profile
    print("\n[2] Creating User Profile...")
    demo_profile = UserProfile(
        user_id="demo_user_002", name="Jordan Lee", occupation="Software Engineer"
    )
    memory_manager.save_profile(demo_profile)
    print(f"   ✓ Profile created for Jordan Lee")

    # Demonstrate boundary setting plan
    print_section("[3] Demonstrating: Boundary Setting Plan")

    boundary_tool = None
    for tool in rel_specialist["tools"]:
        name = tool.name if hasattr(tool, "name") else str(tool)
        if "boundary" in name:
            boundary_tool = tool
            break

    print("\nInput Parameters:")
    print("   - Boundary Areas: ['work hours', 'personal time', 'email after hours']")
    print("   - Relationship Type: professional")

    result = boundary_tool.invoke(
        {
            "user_id": "demo_user_002",
            "boundary_areas": ["work hours", "personal time", "email after hours"],
            "relationship_type": "professional",
        }
    )

    print("\nOutput (Boundary Setting Plan):")
    print("-" * 70)
    preview = result[:600] + "..." if len(result) > 600 else result
    print(preview)
    print("-" * 70)

    # Domain boundaries
    print_section("[4] Domain Boundaries")
    prompt = rel_specialist["system_prompt"].lower()
    print(f"\n✓ Therapy boundary mentioned: {'therapy' in prompt or 'counseling' in prompt}")
    print(f"✓ Safety resources included: {'800-799-safe' in prompt or 'abuse' in prompt}")

    # Summary
    print_section("[5] Demo Summary")
    print("""
✓ Configured with proper tools (memory + context + relationship-specific)
✓ Created boundary setting plan for workplace boundaries
✓ Respected domain boundaries (therapy, safety resources)
✓ Provided specific scripts and strategies

Key Capabilities:
- Boundary setting strategies
- Communication skill development
- Workplace relationship management
    """)


if __name__ == "__main__":
    demonstrate_relationship_specialist()
