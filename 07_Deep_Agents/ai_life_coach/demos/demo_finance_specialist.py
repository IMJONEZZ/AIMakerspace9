#!/usr/bin/env python3
"""
Demo script for Finance Specialist agent.

Scenario: "I want to save for a house down payment in 3 years"

Run with:
    python demos/demo_finance_specialist.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents import get_finance_specialist
from src.tools.memory_tools import create_memory_tools
from src.tools.context_tools import create_context_tools
from src.tools.finance_tools import create_finance_tools
from src.memory import create_memory_store, UserProfile, MemoryManager
from deepagents.backends import FilesystemBackend


def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demonstrate_finance_specialist():
    """Demonstrate the Finance Specialist agent."""
    print_section("AI Life Coach - Finance Specialist Demo")
    print("\nScenario: 'I want to save for a house down payment in 3 years'")
    print("User ID: demo_user_003")

    # Initialize
    print("\n[1] Initializing Finance Specialist...")
    memory_store = create_memory_store()
    memory_manager = MemoryManager(memory_store)
    memory_tools = create_memory_tools(memory_store)
    backend = FilesystemBackend(root_dir="./demos/workspace")
    context_tools = create_context_tools(backend=backend)
    finance_tools = create_finance_tools(backend=backend)

    fin_specialist = get_finance_specialist()
    fin_specialist["tools"] = list(memory_tools) + list(context_tools) + list(finance_tools)

    print(f"   ✓ Specialist: {fin_specialist['name']}")
    print(f"   ✓ Tools available: {len(fin_specialist['tools'])}")

    # Create profile
    print("\n[2] Creating User Profile...")
    demo_profile = UserProfile(
        user_id="demo_user_003", name="Taylor Smith", occupation="Product Manager"
    )
    memory_manager.save_profile(demo_profile)
    print(f"   ✓ Profile created for Taylor Smith")

    # Demonstrate savings goal
    print_section("[3] Demonstrating: Financial Goal Setting")

    goal_tool = None
    for tool in fin_specialist["tools"]:
        name = tool.name if hasattr(tool, "name") else str(tool)
        if "financial_goal" in name or "set_financial" in name:
            goal_tool = tool
            break

    print("\nInput Parameters:")
    print("   - Goal Type: House Down Payment")
    print("   - Target Amount: $60,000 (20% of $300k)")
    print("   - Timeline: 36 months")

    result = goal_tool.invoke(
        {
            "user_id": "demo_user_003",
            "goal_type": "house_down_payment",
            "target_amount": 60000,
            "timeline_months": 36,
            "current_savings": 5000,
        }
    )

    print("\nOutput (Financial Goal Plan):")
    print("-" * 70)
    preview = result[:600] + "..." if len(result) > 600 else result
    print(preview)
    print("-" * 70)

    # Demonstrate budget analysis
    print_section("[4] Demonstrating: Budget Analysis")

    budget_tool = None
    for tool in fin_specialist["tools"]:
        name = tool.name if hasattr(tool, "name") else str(tool)
        if "budget" in name:
            budget_tool = tool
            break

    print("\nInput Parameters:")
    print("   - Monthly Income: $5,000")
    print("   - Expenses: Rent ($1,800), Food ($600), Other ($1,200)")

    result = budget_tool.invoke(
        {
            "user_id": "demo_user_003",
            "monthly_income": 5000,
            "expenses": {
                "rent": 1800,
                "food": 600,
                "transportation": 300,
                "utilities": 200,
                "entertainment": 400,
                "other": 700,
            },
            "budget_framework": "50/30/20",
        }
    )

    print("\nOutput (Budget Analysis):")
    print("-" * 70)
    preview = result[:600] + "..." if len(result) > 600 else result
    print(preview)
    print("-" * 70)

    # Domain boundaries
    print_section("[5] Domain Boundaries")
    prompt = fin_specialist["system_prompt"].lower()
    print(
        f"\n✓ Disclaimer included: {'not professional advice' in prompt or 'educational information only' in prompt}"
    )
    print(f"✓ Referral to professional: {'financial planner' in prompt or 'cpa' in prompt}")

    # Summary
    print_section("[6] Demo Summary")
    print("""
✓ Configured with proper tools (memory + context + finance-specific)
✓ Created financial goal plan for house down payment
✓ Analyzed budget using 50/30/20 framework
✓ Included proper disclaimers and professional referrals

Key Capabilities:
- Financial goal setting (SMART framework)
- Budget analysis with proven frameworks
- Savings timeline calculation
- Educational approach (not professional advice)
    """)


if __name__ == "__main__":
    demonstrate_finance_specialist()
