#!/usr/bin/env python3
"""
Demo script for Finance Coach Specialist.

This script demonstrates the finance coaching capabilities including:
- Budget analysis (50/30/20 rule)
- Debt payoff strategies (avalanche vs. snowball)
- Emergency fund planning
- Financial goal setting
- Expense optimization analysis
- Savings timeline calculation

Usage:
    python demo_finance_coach.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.config import config
from deepagents.backends import FilesystemBackend
from src.tools.finance_tools import create_finance_tools


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def main():
    """Run the finance coach demonstrations."""
    print_section("AI Life Coach - Finance Specialist Demo")

    # Initialize environment
    config.initialize_environment()

    # Create backend and finance tools
    backend = FilesystemBackend(root_dir="workspace/demo_finance")
    (
        create_budget_analyzer,
        generate_debt_payoff_plan,
        calculate_emergency_fund_target,
        set_financial_goal,
        analyze_expense_optimization,
        calculate_savings_timeline,
    ) = create_finance_tools(backend=backend)

    user_id = "demo_user"

    # ========================================================================
    # Scenario 1: Budget Analysis
    # ========================================================================
    print_section("Scenario 1: Budget Analysis (50/30/20 Rule)")

    result = create_budget_analyzer.invoke(
        {
            "user_id": user_id,
            "monthly_income": 5000,
            "expenses": {
                "rent": 1500,  # needs
                "groceries": 400,  # needs
                "utilities": 200,  # needs
                "transportation": 300,  # needs
                "dining_out": 400,  # wants
                "entertainment": 250,  # wants
                "streaming": 40,  # wants
            },
            "budget_framework": "50/30/20",
        }
    )
    print(result)

    # ========================================================================
    # Scenario 2: Emergency Fund Planning
    # ========================================================================
    print_section("Scenario 2: Emergency Fund Calculation")

    result = calculate_emergency_fund_target.invoke(
        {
            "user_id": user_id,
            "monthly_essential_expenses": 2400,  # rent + groceries + utilities
            "dependents": 1,
            "job_stability": "average",
        }
    )
    print(result)

    # ========================================================================
    # Scenario 3: Debt Payoff Strategy
    # ========================================================================
    print_section("Scenario 3: Debt Payoff Strategy Comparison")

    result = generate_debt_payoff_plan.invoke(
        {
            "user_id": user_id,
            "debts": [
                {"name": "Credit Card", "balance": 5000, "interest_rate": 18.5},
                {"name": "Personal Loan", "balance": 8000, "interest_rate": 12.0},
                {"name": "Car Loan", "balance": 15000, "interest_rate": 5.0},
            ],
            "strategy": "compare",  # Show both methods
            "monthly_payment": 800,
        }
    )
    print(result)

    # ========================================================================
    # Scenario 4: Financial Goal Setting
    # ========================================================================
    print_section("Scenario 4: Setting a Financial Goal")

    result = set_financial_goal.invoke(
        {
            "user_id": user_id,
            "goal_name": "House Down Payment",
            "target_amount": 60000,
            "target_date": "2027-12-31",
            "current_savings": 10000,
            "category": "major_purchase",
        }
    )
    print(result)

    # ========================================================================
    # Scenario 5: Expense Optimization
    # ========================================================================
    print_section("Scenario 5: Expense Optimization Analysis")

    result = analyze_expense_optimization.invoke(
        {
            "user_id": user_id,
            "expenses": {
                "rent": 1500,
                "groceries": 400,
                "utilities": 200,
                "netflix": 15.99,
                "spotify": 10.99,
                "gym membership": 50,
                "dining_out": 400,
                "food delivery": 150,  # UberEats/DoorDash
            },
            "monthly_income": 5000,
        }
    )
    print(result)

    # ========================================================================
    # Scenario 6: Savings Timeline
    # ========================================================================
    print_section("Scenario 6: Savings Timeline Calculator")

    result = calculate_savings_timeline.invoke(
        {
            "user_id": user_id,
            "goal_amount": 50000,  # Remaining for house down payment
            "monthly_contribution": 800,
            "current_savings": 10000,
            "annual_return_rate": 5.0,  # Conservative investment return
        }
    )
    print(result)

    # ========================================================================
    # Summary
    # ========================================================================
    print_section("Demo Complete")

    print("""
The Finance Coach Specialist demonstrated the following capabilities:

1. ✓ Budget Analysis - Analyzed spending against 50/30/20 framework
2. ✓ Emergency Fund Planning - Calculated personalized emergency fund target
3. ✓ Debt Payoff Strategies - Compared avalanche vs. snowball methods
4. ✓ Financial Goal Setting - Created SMART goal for house down payment
5. ✓ Expense Optimization - Identified savings opportunities in subscriptions/dining
6. ✓ Savings Timeline - Calculated time to reach goal with compound growth

All financial data has been saved to the workspace for reference.

**Important Notes:**
- This is educational information only, not professional financial advice
- All tools include disclaimers about seeking professional guidance
- Budget recommendations can be adjusted based on individual circumstances
- Debt payoff strategies should align with user's psychological preferences

**Next Steps:**
- Review the saved financial plans in workspace/demo_finance/
- Consider integrating with memory tools for persistent user profiles
- Add more sophisticated investment education resources
- Implement retirement planning calculators (401k, IRA projections)
""")


if __name__ == "__main__":
    main()
