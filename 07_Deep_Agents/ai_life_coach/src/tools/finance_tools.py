"""
Finance Coach tools for AI Life Coach.

This module provides LangChain tools specialized for personal finance coaching.
All tools use the @tool decorator and follow best practices for validation,
error handling, and user-friendly output.

Tools:
- create_budget_analyzer: Analyze spending against budgeting frameworks (50/30/20, zero-based)
- generate_debt_payoff_plan: Create debt payoff strategies (avalanche vs. snowball)
- calculate_emergency_fund_target: Calculate required emergency fund based on expenses
- set_financial_goal: Create SMART financial goals with milestones
- analyze_expense_optimization: Identify savings opportunities in spending patterns
- calculate_savings_timeline: Calculate timeline to achieve financial goals

Based on established personal finance frameworks:
- 50/30/20 Budgeting Rule (Elizabeth Warren)
- Debt Avalanche and Snowball Methods
- Emergency Fund Best Practices (3-6 months expenses)
- SMART Goal Setting Framework
"""

from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, List, Optional
import json

# Import LangChain components
try:
    from langchain_core.tools import tool
except ImportError:
    # Fallback for development environments without full LangChain
    def tool(func):
        """Fallback decorator when langchain_core is not available."""
        func.is_tool = True  # type: ignore
        return func


# Import backend configuration
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import get_backend


# ==============================================================================
# Finance Tool Factory
# ==============================================================================


def create_finance_tools(backend=None) -> tuple:
    """
    Create finance tools with shared FilesystemBackend instance.

    These tools enable the Finance Specialist to:
    - Analyze budgets using established frameworks (50/30/20, zero-based)
    - Generate debt payoff strategies (avalanche vs. snowball methods)
    - Calculate emergency fund targets based on individual circumstances
    - Set SMART financial goals with actionable milestones
    - Identify optimization opportunities in spending patterns
    - Calculate timelines for achieving financial goals

    Args:
        backend: Optional FilesystemBackend instance. If None, uses get_backend()

    Returns:
        Tuple of finance tools (create_budget_analyzer, generate_debt_payoff_plan,
                               calculate_emergency_fund_target, set_financial_goal,
                               analyze_expense_optimization, calculate_savings_timeline)

    Example:
        >>> from src.config import config
        >>> config.initialize_environment()
        >>> tools = create_finance_tools()
        >>> result = create_budget_analyzer(
        ...     user_id="user_123",
        ...     monthly_income=5000,
        ...     expenses={"rent": 1500, "groceries": 400, "utilities": 200}
        ... )
    """
    if backend is None:
        backend = get_backend()

    # Get the workspace directory path from backend
    workspace_path = Path(backend.root_dir) if hasattr(backend, "root_dir") else Path("workspace")

    @tool
    def create_budget_analyzer(
        user_id: str,
        monthly_income: float,
        expenses: Dict[str, float],
        budget_framework: Optional[str] = "50/30/20",
    ) -> str:
        """Analyze spending patterns against established budgeting frameworks.

        This tool performs comprehensive budget analysis using proven frameworks:
        - 50/30/20 Rule: 50% needs, 30% wants, 20% savings
        - Zero-Based Budgeting: Every dollar assigned a purpose (income = expenses + savings)

        The analysis categorizes expenses, identifies gaps vs. framework targets,
        and provides actionable recommendations.

        Args:
            user_id: The user's unique identifier
            monthly_income: Monthly take-home income (after taxes)
            expenses: Dictionary of expense categories and amounts
                     (e.g., {"rent": 1500, "groceries": 400, "entertainment": 200})
            budget_framework: Framework to use ("50/30/20" or "zero-based")

        Returns:
            Structured budget analysis with category breakdowns, gaps,
            and recommendations. Saved to financial_assessments/{user_id}/

        Raises:
            ValueError: If required parameters are invalid

        Example:
            >>> create_budget_analyzer(
            ...     "user_123",
            ...     5000,
            ...     {"rent": 1500, "groceries": 400, "utilities": 200, "dining_out": 300}
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if monthly_income <= 0 or not isinstance(monthly_income, (int, float)):
            return "Error: monthly_income must be a positive number"
        if not expenses or not isinstance(expenses, dict):
            return "Error: expenses must be a non-empty dictionary"

        try:
            # Define expense categories for classification
            needs_categories = [
                "rent",
                "mortgage",
                "utilities",
                "groceries",
                "transportation",
                "car_payment",
                "insurance",
                "healthcare",
                "childcare",
                "medications",
            ]
            wants_categories = [
                "dining_out",
                "entertainment",
                "streaming",
                "shopping",
                "subscriptions",
                "hobbies",
                "travel",
            ]

            # Categorize expenses
            needs_total = sum(
                amount
                for category, amount in expenses.items()
                if any(cat in category.lower() for cat in needs_categories)
            )
            wants_total = sum(
                amount
                for category, amount in expenses.items()
                if any(cat in category.lower() for cat in wants_categories)
            )
            other_expenses = sum(
                amount
                for category, amount in expenses.items()
                if not any(cat in category.lower() for cat in needs_categories + wants_categories)
            )

            total_expenses = sum(expenses.values())
            remaining = monthly_income - total_expenses

            # Calculate percentages
            needs_pct = (needs_total / monthly_income * 100) if monthly_income > 0 else 0
            wants_pct = (wants_total / monthly_income * 100) if monthly_income > 0 else 0
            other_pct = (other_expenses / monthly_income * 100) if monthly_income > 0 else 0
            savings_pct = (remaining / monthly_income * 100) if monthly_income > 0 else 0

            # Framework targets
            framework_targets = {
                "50/30/20": {"needs": 50, "wants": 30, "savings": 20},
                "zero-based": {"needs": 0, "wants": 0, "savings": 100},  # All income allocated
            }

            target = framework_targets.get(budget_framework, framework_targets["50/30/20"])

            # Calculate gaps
            needs_gap = needs_pct - target.get("needs", 50)
            wants_gap = wants_pct - target.get("wants", 30)
            savings_gap = savings_pct - target.get("savings", 20)

            # Generate recommendations
            recommendations = []
            if needs_gap > 5:
                recommendations.append(
                    f"⚠️ Needs spending ({needs_pct:.1f}%) exceeds {target.get('needs', 50)}% target "
                    f"by {abs(needs_gap):.1f}%. Review essential expenses for optimization."
                )
            elif needs_pct < target.get("needs", 50) - 10:
                recommendations.append(
                    f"✓ Needs spending ({needs_pct:.1f}%) is well under {target.get('needs', 50)}% target. "
                    f"This provides flexibility."
                )

            if wants_gap > 5:
                recommendations.append(
                    f"◐ Wants spending ({wants_pct:.1f}%) exceeds {target.get('wants', 30)}% target "
                    f"by {abs(wants_gap):.1f}%. Consider reducing discretionary spending."
                )

            if savings_gap < -5:
                recommendations.append(
                    f"⚠️ Savings rate ({savings_pct:.1f}%) is below {target.get('savings', 20)}% target. "
                    f"Consider increasing savings for financial security."
                )
            elif savings_pct >= 20:
                recommendations.append(
                    f"✓ Excellent! Savings rate ({savings_pct:.1f}%) meets or exceeds recommended target."
                )

            if remaining < 0:
                recommendations.append(
                    f"🚨 CRITICAL: You are spending ${abs(remaining):,.2f} more than you earn each month. "
                    f"Immediate action required to prevent debt accumulation."
                )

            # Build analysis data
            analysis = {
                "user_id": user_id,
                "monthly_income": monthly_income,
                "budget_framework": budget_framework,
                "timestamp": datetime.now().isoformat(),
                "expenses": expenses,
                "breakdown": {
                    "needs": {"amount": needs_total, "percentage": round(needs_pct, 1)},
                    "wants": {"amount": wants_total, "percentage": round(wants_pct, 1)},
                    "other": {"amount": other_expenses, "percentage": round(other_pct, 1)},
                    "savings_potential": {"amount": remaining, "percentage": round(savings_pct, 1)},
                },
                "total_expenses": total_expenses,
                "remaining": remaining,
                "framework_comparison": {
                    "needs_target": target.get("needs", 50),
                    "wants_target": target.get("wants", 30),
                    "savings_target": target.get("savings", 20),
                    "needs_gap": round(needs_gap, 1),
                    "wants_gap": round(wants_gap, 1),
                    "savings_gap": round(savings_gap, 1),
                },
                "recommendations": recommendations,
            }

            # Save to file
            json_content = json.dumps(analysis, indent=2)
            today = date.today()
            path = f"financial_assessments/{user_id}/{today}_budget_analysis.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            response_parts = [
                f"Budget Analysis ({budget_framework.upper()} Rule)",
                "=" * 60,
                f"\nMonthly Income: ${monthly_income:,.2f}",
                f"Total Expenses: ${total_expenses:,.2f}",
            ]

            if remaining >= 0:
                response_parts.append(f"Remaining for Savings: ${remaining:,.2f}")
            else:
                response_parts.append(f"⚠️ DEFICIT: ${abs(remaining):,.2f}")

            response_parts.append("\n---\nCategory Breakdown:")
            response_parts.append(f"\nNeeds (Essentials): ${needs_total:,.2f} ({needs_pct:.1f}%)")
            response_parts.append(
                f"  ✓ Target: {target.get('needs', 50)}% | Gap: {needs_gap:+.1f}%"
            )

            response_parts.append(
                f"\nWants (Discretionary): ${wants_total:,.2f} ({wants_pct:.1f}%)"
            )
            response_parts.append(
                f"  ✓ Target: {target.get('wants', 30)}% | Gap: {wants_gap:+.1f}%"
            )

            if other_expenses > 0:
                response_parts.append(
                    f"\nOther/Uncategorized: ${other_expenses:,.2f} ({other_pct:.1f}%)"
                )

            response_parts.append(f"\nSavings Potential: ${remaining:,.2f} ({savings_pct:.1f}%)")
            response_parts.append(
                f"  ✓ Target: {target.get('savings', 20)}% | Gap: {savings_gap:+.1f}%"
            )

            if recommendations:
                response_parts.append("\n---\nRecommendations:")
                for i, rec in enumerate(recommendations, 1):
                    response_parts.append(f"  {i}. {rec}")

            response_parts.append(f"\nAnalysis saved to: {path}")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error analyzing budget: {str(e)}"

    @tool
    def generate_debt_payoff_plan(
        user_id: str,
        debts: List[Dict[str, Any]],
        strategy: Optional[str] = "avalanche",
        monthly_payment: Optional[float] = None,
    ) -> str:
        """Generate debt payoff strategies using avalanche or snowball methods.

        This tool creates comprehensive debt payoff plans comparing two popular methods:
        - Avalanche: Pay highest interest rate first (mathematically optimal, saves most money)
        - Snowball: Pay smallest balance first (psychological boost, builds momentum)

        The plan includes payoff timelines, total interest paid, and monthly payment
        breakdowns for each debt.

        Args:
            user_id: The user's unique identifier
            debts: List of debt dictionaries with 'name', 'balance', and 'interest_rate'
                   (e.g., [{"name": "Credit Card", "balance": 5000, "interest_rate": 18.5}])
            strategy: Payoff strategy ("avalanche", "snowball", or "compare" for both)
            monthly_payment: Optional total monthly payment amount. If None, uses minimums

        Returns:
            Structured debt payoff plan with timeline, interest savings,
            and payment schedule. Saved to financial_plans/{user_id}/

        Raises:
            ValueError: If required parameters are invalid

        Example:
            >>> generate_debt_payoff_plan(
            ...     "user_123",
            ...     [
            ...         {"name": "Credit Card", "balance": 5000, "interest_rate": 18.5},
            ...         {"name": "Car Loan", "balance": 15000, "interest_rate": 5.0}
            ...     ],
            ...     "compare"
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not debts or not isinstance(debts, list):
            return "Error: debts must be a non-empty list"

        # Validate each debt
        for debt in debts:
            if not isinstance(debt, dict):
                return "Error: each debt must be a dictionary"
            if "name" not in debt or "balance" not in debt or "interest_rate" not in debt:
                return "Error: each debt must have 'name', 'balance', and 'interest_rate'"
            if debt["balance"] <= 0 or debt["interest_rate"] < 0:
                return "Error: balance must be positive and interest_rate must be non-negative"

        try:
            # Calculate total debt
            total_debt = sum(debt["balance"] for debt in debts)
            avg_interest_rate = (
                sum(d["balance"] * d["interest_rate"] for d in debts) / total_debt
                if total_debt > 0
                else 0
            )

            # Determine monthly payment (if not provided, use minimums)
            if monthly_payment is None:
                # Estimate minimum as 2% of balance or $25, whichever is higher
                monthly_payment = sum(max(debt["balance"] * 0.02, 25) for debt in debts)

            if monthly_payment <= 0:
                return "Error: monthly_payment must be greater than total minimum payments"

            # Helper function to calculate payoff timeline
            def calculate_payoff(method: str) -> Dict[str, Any]:
                """Calculate payoff details for a given method."""
                if method == "avalanche":
                    sorted_debts = sorted(debts, key=lambda x: -x["interest_rate"])
                else:  # snowball
                    sorted_debts = sorted(debts, key=lambda x: x["balance"])

                working_debts = [
                    {
                        "name": d["name"],
                        "balance": float(d["balance"]),
                        "interest_rate": float(d["interest_rate"]),
                    }
                    for d in sorted_debts
                ]

                total_interest = 0.0
                months = 0
                schedule = []

                while any(d["balance"] > 0 for d in working_debts):
                    months += 1
                    payment_remaining = monthly_payment

                    # Calculate minimum payments for all debts
                    min_payments = [max(d["balance"] * 0.02, 25) for d in working_debts]
                    total_min = sum(min_payments)

                    # Distribute payments
                    for i, debt in enumerate(working_debts):
                        if debt["balance"] <= 0:
                            continue

                        # Calculate monthly interest
                        monthly_interest = debt["balance"] * (debt["interest_rate"] / 100 / 12)
                        total_interest += monthly_interest

                        # Pay minimum
                        min_payment = min(min_payments[i], payment_remaining)
                        debt["balance"] += monthly_interest  # Add interest first
                        debt["balance"] -= min_payment
                        payment_remaining -= min_payment

                    # Apply extra to priority debt (first non-zero balance)
                    if payment_remaining > 0:
                        for debt in working_debts:
                            if debt["balance"] > 0:
                                extra = min(debt["balance"], payment_remaining)
                                debt["balance"] -= extra
                                payment_remaining -= extra

                    # Cap at reasonable timeline to prevent infinite loops
                    if months > 600:  # 50 years max
                        break

                return {
                    "method": method,
                    "months_to_payoff": months,
                    "years_to_payoff": months / 12,
                    "total_interest_paid": round(total_interest, 2),
                    "total_amount_paid": round(total_debt + total_interest, 2),
                }

            # Calculate both methods for comparison
            avalanche_plan = calculate_payoff("avalanche")
            snowball_plan = calculate_payoff("snowball")

            # Build plan data
            plan = {
                "user_id": user_id,
                "debts": debts,
                "total_debt": total_debt,
                "average_interest_rate": round(avg_interest_rate, 2),
                "monthly_payment": monthly_payment,
                "strategy_selected": strategy,
                "timestamp": datetime.now().isoformat(),
            }

            if strategy == "compare" or strategy == "avalanche":
                plan["avalanche_plan"] = avalanche_plan
            if strategy == "compare" or strategy == "snowball":
                plan["snowball_plan"] = snowball_plan

            # Save to file
            json_content = json.dumps(plan, indent=2)
            path = f"financial_plans/{user_id}/debt_payoff_plan.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            response_parts = [
                f"Debt Payoff Plan ({strategy.title() if strategy != 'compare' else 'Comparison'})",
                "=" * 60,
                f"\nTotal Debt: ${total_debt:,.2f}",
                f"Average Interest Rate: {avg_interest_rate:.2f}%",
                f"Monthly Payment: ${monthly_payment:,.2f}",
                "\n---\nYour Debts:",
            ]

            for i, debt in enumerate(debts, 1):
                response_parts.append(
                    f"  {i}. {debt['name']}: ${debt['balance']:,.2f} at {debt['interest_rate']}%"
                )

            if strategy == "compare":
                response_parts.append("\n---\n📊 Method Comparison:")
                response_parts.append(
                    f"\nAvalanche (Highest Interest First):"
                    f"\n  ⏱️ Time to Payoff: {avalanche_plan['years_to_payoff']:.1f} years ({avalanche_plan['months_to_payoff']} months)"
                    f"\n  💰 Total Interest: ${avalanche_plan['total_interest_paid']:,.2f}"
                    f"\n  📈 Total Paid: ${avalanche_plan['total_amount_paid']:,.2f}"
                )
                response_parts.append(
                    f"\nSnowball (Smallest Balance First):"
                    f"\n  ⏱️ Time to Payoff: {snowball_plan['years_to_payoff']:.1f} years ({snowball_plan['months_to_payoff']} months)"
                    f"\n  💰 Total Interest: ${snowball_plan['total_interest_paid']:,.2f}"
                    f"\n  📈 Total Paid: ${snowball_plan['total_amount_paid']:,.2f}"
                )

                interest_savings = (
                    snowball_plan["total_interest_paid"] - avalanche_plan["total_interest_paid"]
                )
                if interest_savings > 0:
                    response_parts.append(
                        f"\n✓ Avalanche saves ${interest_savings:,.2f} in interest compared to Snowball"
                    )
            elif strategy == "avalanche":
                response_parts.append(
                    f"\n---\nAvalanche Method Results:"
                    f"\n  ⏱️ Time to Payoff: {avalanche_plan['years_to_payoff']:.1f} years ({avalanche_plan['months_to_payoff']} months)"
                    f"\n  💰 Total Interest: ${avalanche_plan['total_interest_paid']:,.2f}"
                )
            else:  # snowball
                response_parts.append(
                    f"\n---\nSnowball Method Results:"
                    f"\n  ⏱️ Time to Payoff: {snowball_plan['years_to_payoff']:.1f} years ({snowball_plan['months_to_payoff']} months)"
                    f"\n  💰 Total Interest: ${snowball_plan['total_interest_paid']:,.2f}"
                )

            response_parts.append(f"\nPlan saved to: {path}")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error generating debt payoff plan: {str(e)}"

    @tool
    def calculate_emergency_fund_target(
        user_id: str,
        monthly_essential_expenses: float,
        dependents: Optional[int] = 0,
        job_stability: Optional[str] = "average",
        home_owner: Optional[bool] = False,
    ) -> str:
        """Calculate personalized emergency fund target based on individual circumstances.

        This tool calculates an appropriate emergency fund size using the 3-6-9 rule framework:
        - 3 months: Single income, stable job, no dependents
        - 6 months: Multiple factors (dependents, variable income)
        - 9+ months: High risk situations (self-employed, single income + dependents)

        The calculation considers essential expenses, dependents, job stability,
        home ownership (maintenance costs), and provides a building roadmap.

        Args:
            user_id: The user's unique identifier
            monthly_essential_expenses: Monthly essential expenses (rent/mortgage, food,
                                        utilities, minimum debt payments)
            dependents: Number of financial dependents (children, elderly parents)
            job_stability: Job stability level ("high", "average", or "low")
            home_owner: Whether the user owns their home (affects maintenance buffer)

        Returns:
            Emergency fund target with breakdown by month, building milestones,
            and actionable recommendations. Saved to financial_plans/{user_id}/

        Raises:
            ValueError: If required parameters are invalid

        Example:
            >>> calculate_emergency_fund_target(
            ...     "user_123",
            ...     3000,
            ...     dependents=2,
            ...     job_stability="average"
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if monthly_essential_expenses <= 0 or not isinstance(
            monthly_essential_expenses, (int, float)
        ):
            return "Error: monthly_essential_expenses must be a positive number"

        try:
            # Determine recommended months based on factors
            base_months = 3

            # Add months for dependents
            if dependents > 0:
                base_months += dependents

            # Adjust for job stability
            if job_stability.lower() == "low":
                base_months += 2
            elif job_stability.lower() == "high" and dependents == 0:
                base_months = max(3, base_months - 1)

            # Add buffer for homeowners (maintenance costs)
            if home_owner:
                base_months += 1

            # Cap at reasonable maximum
            recommended_months = min(base_months, 12)

            # Calculate emergency fund target
            emergency_target = monthly_essential_expenses * recommended_months

            # Define building milestones (starter fund, half target, full target)
            starter_fund = min(1000.00, emergency_target * 0.1)  # $1,000 or 10% of target
            half_target = emergency_target * 0.5

            # Calculate monthly savings to reach milestones
            months_to_starter = max(1, int(starter_fund / 100))  # Assuming $100/month
            months_to_half = max(1, int(half_target / 200))  # Assuming $200/month
            months_to_full = max(1, int(emergency_target / 300))  # Assuming $300/month

            # Build fund data
            fund_data = {
                "user_id": user_id,
                "monthly_essential_expenses": monthly_essential_expenses,
                "dependents": dependents,
                "job_stability": job_stability,
                "home_owner": home_owner,
                "recommended_months": recommended_months,
                "emergency_fund_target": emergency_target,
                "building_milestones": {
                    "starter_fund": {
                        "amount": starter_fund,
                        "purpose": "Initial coverage for unexpected expenses",
                    },
                    "half_target": {
                        "amount": half_target,
                        "purpose": "Moderate financial security",
                    },
                    "full_target": {
                        "amount": emergency_target,
                        "purpose": "Complete emergency coverage",
                    },
                },
                "savings_timeline": {
                    "to_starter_at_100_per_month": months_to_starter,
                    "to_half_at_200_per_month": months_to_half,
                    "to_full_at_300_per_month": months_to_full,
                },
                "timestamp": datetime.now().isoformat(),
            }

            # Save to file
            json_content = json.dumps(fund_data, indent=2)
            path = f"financial_plans/{user_id}/emergency_fund_plan.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            response_parts = [
                "Emergency Fund Calculation",
                "=" * 60,
                f"\nMonthly Essential Expenses: ${monthly_essential_expenses:,.2f}",
            ]

            # Show factors
            response_parts.append("\n---\nFactors Considered:")
            response_parts.append(f"  • Dependents: {dependents}")
            response_parts.append(f"  • Job Stability: {job_stability.title()}")
            response_parts.append(f"  • Home Owner: {'Yes' if home_owner else 'No'}")

            # Show target
            response_parts.append(
                f"\n---\n🎯 Recommended Emergency Fund:"
                f"\n  • {recommended_months} months of essential expenses"
                f"\n  • Total Target: ${emergency_target:,.2f}"
            )

            # Show building milestones
            response_parts.append("\n---\n📈 Building Milestones:")
            response_parts.append(
                f"\n  Milestone 1: Starter Fund"
                f"\n    Target: ${starter_fund:,.2f}"
                f"\n    Time at $100/month: ~{months_to_starter} months"
                f"\n    Purpose: Initial coverage for unexpected expenses"
            )
            response_parts.append(
                f"\n  Milestone 2: Half Target"
                f"\n    Target: ${half_target:,.2f}"
                f"\n    Time at $200/month: ~{months_to_half} months"
                f"\n    Purpose: Moderate financial security"
            )
            response_parts.append(
                f"\n  Milestone 3: Full Target"
                f"\n    Target: ${emergency_target:,.2f}"
                f"\n    Time at $300/month: ~{months_to_full} months"
                f"\n    Purpose: Complete emergency coverage"
            )

            # Recommendations
            response_parts.append("\n---\n💡 Recommendations:")
            response_parts.append("  1. Start with the starter fund ($1,000 or 10% of target)")
            response_parts.append("  2. Keep funds in a high-yield savings account for liquidity")
            response_parts.append("  3. Replenish immediately if used")
            response_parts.append("  4. Review annually and adjust for life changes")

            # Risk factors note
            if job_stability.lower() == "low" or dependents > 2:
                response_parts.append(
                    "\n⚠️ Note: Your situation indicates higher financial risk. "
                    "Consider building beyond the recommended target if possible."
                )

            response_parts.append(f"\nPlan saved to: {path}")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error calculating emergency fund target: {str(e)}"

    @tool
    def set_financial_goal(
        user_id: str,
        goal_name: str,
        target_amount: float,
        target_date: str,
        current_savings: Optional[float] = 0.0,
        category: Optional[str] = "general",
    ) -> str:
        """Create a SMART financial goal with milestones and action plan.

        This tool creates structured, achievable financial goals using the SMART framework:
        - Specific: Clear dollar amount and purpose
        - Measurable: Trackable progress with milestones
        - Achievable: Based on realistic savings rate
        - Relevant: Aligned with user's priorities
        - Time-bound: Specific target date

        The goal includes monthly savings requirements, progress milestones,
        and action steps to stay on track.

        Args:
            user_id: The user's unique identifier
            goal_name: Name/description of the financial goal (e.g., "House Down Payment")
            target_amount: Target amount to save (in dollars)
            target_date: Target date for achieving the goal (YYYY-MM-DD format)
            current_savings: Current amount already saved toward this goal
            category: Goal category (short-term, medium-term, long-term, emergency_fund,
                       retirement, major_purchase)

        Returns:
            SMART financial goal with monthly savings requirement, milestones,
            and action plan. Saved to financial_goals/{user_id}/

        Raises:
            ValueError: If required parameters are invalid

        Example:
            >>> set_financial_goal(
            ...     "user_123",
            ...     "House Down Payment",
            ...     60000,
            ...     "2027-12-31",
            ...     current_savings=10000,
            ...     category="major_purchase"
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not goal_name or not isinstance(goal_name, str):
            return "Error: goal_name must be a non-empty string"
        if target_amount <= 0 or not isinstance(target_amount, (int, float)):
            return "Error: target_amount must be a positive number"

        # Validate and parse date
        try:
            from datetime import datetime

            target_dt = datetime.strptime(target_date, "%Y-%m-%d")
        except ValueError:
            return "Error: target_date must be in YYYY-MM-DD format"

        try:
            # Calculate timeline
            today = datetime.now()
            remaining_days = (target_dt - today).days

            if remaining_days <= 0:
                return "Error: target_date must be in the future"

            remaining_months = max(1, int(remaining_days / 30))
            amount_needed = max(0, target_amount - current_savings)
            monthly_savings_required = amount_needed / remaining_months

            # Determine goal time horizon
            if remaining_days <= 365:
                time_horizon = "short-term"
            elif remaining_days <= 1825:  # 5 years
                time_horizon = "medium-term"
            else:
                time_horizon = "long-term"

            # Create progress milestones (25%, 50%, 75%)
            milestones = []
            for pct in [0.25, 0.5, 0.75]:
                milestone_amount = current_savings + (amount_needed * pct)
                milestone_date = today + pd_timedelta(days=int(remaining_days * pct))
                milestones.append(
                    {
                        "percentage": int(pct * 100),
                        "target_amount": round(milestone_amount, 2),
                        "target_date": milestone_date.strftime("%Y-%m-%d"),
                    }
                )

            # Generate SMART validation
            smart_check = {
                "Specific": f"✓ Goal is clearly defined: {goal_name} - ${target_amount:,.2f}",
                "Measurable": f"✓ Progress is trackable from ${current_savings:,.2f} to ${target_amount:,.2f}",
                "Achievable": f"{'✓' if monthly_savings_required < 2000 else '⚠️'} Requires ${monthly_savings_required:,.2f}/month",
                "Relevant": f"✓ Goal aligns with {time_horizon} financial planning",
                "Time-bound": f"✓ Target date: {target_date}",
            }

            # Action steps
            action_steps = [
                "Set up automatic monthly transfer to savings account",
                f"Save ${monthly_savings_required:,.2f} each month ({remaining_months} months remaining)",
                "Track progress monthly and adjust spending if needed",
                f"Review goal quarterly to ensure alignment with priorities",
            ]

            # Build goal data
            goal_data = {
                "user_id": user_id,
                "goal_name": goal_name,
                "target_amount": target_amount,
                "current_savings": current_savings,
                "amount_needed": amount_needed,
                "target_date": target_date,
                "category": category or time_horizon,
                "time_horizon": time_horizon,
                "timeline_months": remaining_months,
                "monthly_savings_required": round(monthly_savings_required, 2),
                "milestones": milestones,
                "smart_validation": smart_check,
                "action_steps": action_steps,
                "created_at": datetime.now().isoformat(),
            }

            # Save to file
            json_content = json.dumps(goal_data, indent=2)
            path = f"financial_goals/{user_id}/{goal_name.replace(' ', '_').lower()}.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            response_parts = [
                f"SMART Financial Goal: {goal_name}",
                "=" * 60,
                f"\nTarget Amount: ${target_amount:,.2f}",
                f"Current Savings: ${current_savings:,.2f}",
                f"Amount Needed: ${amount_needed:,.2f}",
                f"Target Date: {target_date}",
                f"Time Horizon: {time_horizon.title()} ({remaining_months} months)",
            ]

            response_parts.append(
                f"\n💰 Monthly Savings Required: ${monthly_savings_required:,.2f}"
            )

            # SMART validation
            response_parts.append("\n---\nSMART Goal Validation:")
            for criterion, check in smart_check.items():
                response_parts.append(f"  {criterion}: {check}")

            # Milestones
            response_parts.append("\n---\n📈 Progress Milestones:")
            for milestone in milestones:
                response_parts.append(
                    f"  • {milestone['percentage']}%: ${milestone['target_amount']:,.2f} by {milestone['target_date']}"
                )

            # Action steps
            response_parts.append("\n---\n✅ Action Steps:")
            for i, step in enumerate(action_steps, 1):
                response_parts.append(f"  {i}. {step}")

            response_parts.append(f"\nGoal saved to: {path}")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error setting financial goal: {str(e)}"

    @tool
    def analyze_expense_optimization(
        user_id: str,
        expenses: Dict[str, float],
        monthly_income: Optional[float] = None,
    ) -> str:
        """Analyze expenses and identify optimization opportunities for savings.

        This tool examines spending patterns across categories to find potential
        savings opportunities without significantly impacting lifestyle. It identifies:
        - High-cost categories for review
        - Subscription and recurring service optimization
        - Discretionary spending patterns
        - Quick wins vs. longer-term optimizations

        The analysis provides specific, actionable recommendations for reducing
        expenses while maintaining quality of life.

        Args:
            user_id: The user's unique identifier
            expenses: Dictionary of expense categories and amounts
                     (e.g., {"rent": 1500, "netflix": 15, "dining_out": 400})
            monthly_income: Optional monthly income for context

        Returns:
            Expense optimization analysis with savings opportunities,
            prioritized recommendations, and potential monthly/annual savings.
            Saved to financial_assessments/{user_id}/

        Raises:
            ValueError: If required parameters are invalid

        Example:
            >>> analyze_expense_optimization(
            ...     "user_123",
            ...     {"rent": 1500, "netflix": 15, "spotify": 10, "dining_out": 400}
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not expenses or not isinstance(expenses, dict):
            return "Error: expenses must be a non-empty dictionary"

        try:
            total_expenses = sum(expenses.values())

            # Identify potential optimization categories
            subscription_keywords = [
                "netflix",
                "spotify",
                "hulu",
                "disney",
                "apple music",
                "youtube",
                "amazon prime",
                "subscription",
            ]
            dining_keywords = [
                "restaurant",
                "dining",
                "food delivery",
                "ubereats",
                "doordash",
                "grubhub",
            ]
            utility_keywords = ["electric", "gas", "internet", "phone", "water"]

            optimizations = []
            potential_monthly_savings = 0.0

            # Analyze subscriptions
            subscription_expenses = {
                cat: amount
                for cat, amount in expenses.items()
                if any(keyword in cat.lower() for keyword in subscription_keywords)
            }
            if subscription_expenses:
                total_subs = sum(subscription_expenses.values())
                potential_savings = total_subs * 0.3  # Assume 30% can be optimized
                potential_monthly_savings += potential_savings

                optimizations.append(
                    {
                        "category": "Subscriptions & Streaming",
                        "current": total_subs,
                        "potential_savings": round(potential_savings, 2),
                        "recommendations": [
                            f"Review {len(subscription_expenses)} subscription(s) totaling ${total_subs:,.2f}/month",
                            "Consider consolidating or rotating subscriptions",
                            "Look for family plan sharing opportunities",
                            "Set calendar reminders to cancel free trials before billing",
                        ],
                    }
                )

            # Analyze dining out
            dining_expenses = {
                cat: amount
                for cat, amount in expenses.items()
                if any(keyword in cat.lower() for keyword in dining_keywords)
            }
            if dining_expenses:
                total_dining = sum(dining_expenses.values())
                potential_savings = total_dining * 0.2  # Assume 20% can be optimized
                potential_monthly_savings += potential_savings

                optimizations.append(
                    {
                        "category": "Dining Out & Food Delivery",
                        "current": total_dining,
                        "potential_savings": round(potential_savings, 2),
                        "recommendations": [
                            f"Dining out total: ${total_dining:,.2f}/month",
                            "Set a weekly dining budget (e.g., $100/week = $400/month)",
                            "Meal prep to reduce food delivery frequency",
                            "Use restaurant loyalty programs and discounts",
                        ],
                    }
                )

            # Analyze utilities
            utility_expenses = {
                cat: amount
                for cat, amount in expenses.items()
                if any(keyword in cat.lower() for keyword in utility_keywords)
            }
            if utility_expenses:
                total_utilities = sum(utility_expenses.values())
                potential_savings = total_utilities * 0.15  # Assume 15% can be optimized
                potential_monthly_savings += potential_savings

                optimizations.append(
                    {
                        "category": "Utilities & Bills",
                        "current": total_utilities,
                        "potential_savings": round(potential_savings, 2),
                        "recommendations": [
                            f"Utilities total: ${total_utilities:,.2f}/month",
                            "Compare internet/phone plans for better rates",
                            "Install smart thermostat to reduce heating/cooling costs",
                            "Review and adjust phone plan data usage",
                        ],
                    }
                )

            # Identify top 3 expense categories for review
            sorted_expenses = sorted(expenses.items(), key=lambda x: x[1], reverse=True)
            top_expenses = sorted_expenses[:3]

            # Build analysis data
            analysis = {
                "user_id": user_id,
                "expenses": expenses,
                "total_expenses": total_expenses,
                "monthly_income": monthly_income,
                "optimizations": optimizations,
                "potential_monthly_savings": round(potential_monthly_savings, 2),
                "potential_annual_savings": round(potential_monthly_savings * 12, 2),
                "top_expenses": top_expenses,
                "timestamp": datetime.now().isoformat(),
            }

            # Save to file
            json_content = json.dumps(analysis, indent=2)
            today = date.today()
            path = f"financial_assessments/{user_id}/{today}_expense_optimization.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            response_parts = [
                "Expense Optimization Analysis",
                "=" * 60,
                f"\nTotal Monthly Expenses: ${total_expenses:,.2f}",
            ]

            if monthly_income:
                income_pct = (total_expenses / monthly_income * 100) if monthly_income > 0 else 0
                response_parts.append(f"Income Used: {income_pct:.1f}% of ${monthly_income:,.2f}")

            # Top expenses
            response_parts.append("\n---\n📊 Top 3 Expense Categories:")
            for i, (category, amount) in enumerate(top_expenses, 1):
                pct = (amount / total_expenses * 100) if total_expenses > 0 else 0
                response_parts.append(f"  {i}. {category}: ${amount:,.2f} ({pct:.1f}%)")

            # Optimization opportunities
            if optimizations:
                response_parts.append("\n---\n💡 Optimization Opportunities:")
                for opt in optimizations:
                    response_parts.append(
                        f"\n{opt['category']}:"
                        f"\n  Current: ${opt['current']:,.2f}/month"
                        f"\n  Potential Savings: ${opt['potential_savings']:,.2f}/month"
                        f"\n  Recommendations:"
                    )
                    for rec in opt["recommendations"]:
                        response_parts.append(f"    • {rec}")

                response_parts.append(
                    f"\n---\n💰 Total Potential Savings:"
                    f"\n  Monthly: ${potential_monthly_savings:,.2f}"
                    f"\n  Annually: ${potential_monthly_savings * 12:,.2f}"
                )
            else:
                response_parts.append("\n✓ No obvious optimization opportunities identified.")

            response_parts.append(f"\nAnalysis saved to: {path}")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error analyzing expense optimization: {str(e)}"

    @tool
    def calculate_savings_timeline(
        user_id: str,
        goal_amount: float,
        monthly_contribution: float,
        current_savings: Optional[float] = 0.0,
        annual_return_rate: Optional[float] = 4.0,
    ) -> str:
        """Calculate timeline to achieve savings goal with compound growth.

        This tool calculates how long it will take to reach a financial goal based on
        monthly contributions and investment returns. It accounts for compound interest
        and provides a year-by-year breakdown of savings growth.

        Args:
            user_id: The user's unique identifier
            goal_amount: Target savings amount (in dollars)
            monthly_contribution: Amount to save each month
            current_savings: Current amount already saved (default: 0)
            annual_return_rate: Expected annual investment return rate (default: 4.0%)

        Returns:
            Savings timeline with months/years to goal, total contributions,
            investment earnings, and year-by-year breakdown. Saved to financial_plans/{user_id}/

        Raises:
            ValueError: If required parameters are invalid

        Example:
            >>> calculate_savings_timeline(
            ...     "user_123",
            ...     50000,
            ...     800,
            ...     current_savings=5000
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if goal_amount <= 0 or not isinstance(goal_amount, (int, float)):
            return "Error: goal_amount must be a positive number"
        if monthly_contribution <= 0 or not isinstance(monthly_contribution, (int, float)):
            return "Error: monthly_contribution must be a positive number"

        try:
            current = float(current_savings)
            monthly_rate = (float(annual_return_rate) / 100) / 12

            # Calculate timeline
            months = 0
            total_contributions = current
            investment_earnings = 0.0
            yearly_breakdown = []
            year_balance = current

            while current < goal_amount and months <= 600:  # Max 50 years
                months += 1

                # Add monthly contribution
                total_contributions += monthly_contribution

                # Calculate investment earnings this month
                monthly_earnings = current * monthly_rate
                investment_earnings += monthly_earnings

                # Update balance with contribution and earnings
                current = current + monthly_contribution + monthly_earnings

                # Track yearly breakdown
                if months % 12 == 0:
                    yearly_breakdown.append(
                        {
                            "year": months // 12,
                            "balance": round(current, 2),
                            "contributions_this_year": round(monthly_contribution * 12, 2),
                        }
                    )

            years = months / 12

            # Check if goal is achievable
            if current < goal_amount:
                return (
                    f"Warning: At ${monthly_contribution:,.2f}/month with {annual_return_rate}% returns, "
                    f"it would take more than 50 years to reach ${goal_amount:,.2f}. "
                    f"Consider increasing monthly contributions."
                )

            # Calculate final totals
            total_contributions = current_savings + (monthly_contribution * months)
            investment_earnings = current - total_contributions

            # Build timeline data
            timeline_data = {
                "user_id": user_id,
                "goal_amount": goal_amount,
                "current_savings": current_savings,
                "monthly_contribution": monthly_contribution,
                "annual_return_rate": annual_return_rate,
                "months_to_goal": months,
                "years_to_goal": round(years, 1),
                "final_balance": round(current, 2),
                "total_contributions": round(total_contributions, 2),
                "investment_earnings": round(investment_earnings, 2),
                "yearly_breakdown": yearly_breakdown,
                "timestamp": datetime.now().isoformat(),
            }

            # Save to file
            json_content = json.dumps(timeline_data, indent=2)
            path = f"financial_plans/{user_id}/savings_timeline.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            years_int = int(years)
            months_remainder = int((years - years_int) * 12)

            response_parts = [
                "Savings Timeline Calculator",
                "=" * 60,
                f"\nGoal Amount: ${goal_amount:,.2f}",
                f"Current Savings: ${current_savings:,.2f}",
                f"Monthly Contribution: ${monthly_contribution:,.2f}",
                f"Expected Annual Return: {annual_return_rate}%",
            ]

            response_parts.append(
                f"\n---\n🎯 Timeline to Goal:"
                f"\n  {years_int} years, {months_remainder} months ({months} total months)"
            )

            response_parts.append(
                f"\n---\n💰 Breakdown at Goal Achievement:"
                f"\n  Total Balance: ${current:,.2f}"
                f"\n  Your Contributions: ${total_contributions:,.2f} ({100 * total_contributions / current:.1f}%)"
                f"\n  Investment Earnings: ${investment_earnings:,.2f} ({100 * investment_earnings / current:.1f}%)"
            )

            # Show yearly breakdown for first 5 years or until goal
            response_parts.append("\n---\n📈 Year-by-Year Projection:")
            years_to_show = min(5, len(yearly_breakdown))
            for year_data in yearly_breakdown[:years_to_show]:
                response_parts.append(
                    f"\n  Year {year_data['year']}: "
                    f"${year_data['balance']:,.2f} (+${year_data['contributions_this_year']:,.2f})"
                )

            if len(yearly_breakdown) > 5:
                response_parts.append(f"\n  ... (continues to Year {len(yearly_breakdown)})")

            # Recommendations
            response_parts.append("\n---\n💡 Tips to Reach Goal Sooner:")
            response_parts.append(
                f"  • Increase monthly contribution by $100: Reduces timeline by ~{int(months * (monthly_contribution / (monthly_contribution + 100)))} months"
            )
            response_parts.append(
                f"  • Increase return rate by 1%: Can save {int(years * 0.05)} years or more"
            )
            response_parts.append(
                "  • Consider tax-advantaged accounts (IRA, 401k) for retirement goals"
            )

            response_parts.append(f"\nTimeline saved to: {path}")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error calculating savings timeline: {str(e)}"

    @tool
    def calculate_compound_interest(
        user_id: str,
        principal: float,
        annual_rate: float,
        time_years: int,
        compound_frequency: Optional[str] = "monthly",
    ) -> str:
        """Calculate compound interest growth over time.

        This tool computes the future value of an investment using compound
        interest formulas, providing year-by-year breakdowns and comparing
        simple vs. compound interest to demonstrate the power of compounding.

        Args:
            user_id: The user's unique identifier
            principal: Initial investment amount (in dollars)
            annual_rate: Annual interest rate as percentage (e.g., 5.0 for 5%)
            time_years: Number of years to calculate
            compound_frequency: How often interest compounds (daily, monthly,
                               quarterly, annually)

        Returns:
            Compound interest calculation with future value, total interest earned,
            yearly breakdown, and comparison to simple interest.
            Saved to financial_calculations/{user_id}/

        Raises:
            ValueError: If required parameters are invalid

        Example:
            >>> calculate_compound_interest(
            ...     "user_123",
            ...     10000,
            ...     7.0,
            ...     10,
            ...     compound_frequency="monthly"
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if principal <= 0 or not isinstance(principal, (int, float)):
            return "Error: principal must be a positive number"
        if annual_rate < 0 or not isinstance(annual_rate, (int, float)):
            return "Error: annual_rate must be a non-negative number"
        if time_years <= 0 or not isinstance(time_years, int):
            return "Error: time_years must be a positive integer"

        # Normalize compound frequency
        freq_map = {
            "daily": 365,
            "monthly": 12,
            "quarterly": 4,
            "annually": 1,
        }
        n = freq_map.get(compound_frequency.lower(), 12)

        try:
            # Calculate compound interest: A = P(1 + r/n)^(nt)
            rate_decimal = annual_rate / 100
            future_value = principal * (1 + rate_decimal / n) ** (n * time_years)
            compound_interest_earned = future_value - principal

            # Calculate simple interest for comparison: I = P * r * t
            simple_interest_earned = principal * rate_decimal * time_years
            simple_future_value = principal + simple_interest_earned

            # Calculate additional earnings from compounding
            compound_bonus = future_value - simple_future_value

            # Generate yearly breakdown
            yearly_breakdown = []
            balance = principal
            for year in range(1, time_years + 1):
                new_balance = principal * (1 + rate_decimal / n) ** (n * year)
                yearly_earnings = new_balance - balance
                yearly_breakdown.append(
                    {
                        "year": year,
                        "starting_balance": round(balance, 2),
                        "interest_earned": round(yearly_earnings, 2),
                        "ending_balance": round(new_balance, 2),
                    }
                )
                balance = new_balance

            # Build calculation data
            calc_data = {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "parameters": {
                    "principal": principal,
                    "annual_rate_percent": annual_rate,
                    "time_years": time_years,
                    "compound_frequency": compound_frequency,
                },
                "results": {
                    "future_value": round(future_value, 2),
                    "compound_interest_earned": round(compound_interest_earned, 2),
                    "simple_future_value": round(simple_future_value, 2),
                    "compound_bonus": round(compound_bonus, 2),
                },
                "yearly_breakdown": yearly_breakdown,
            }

            # Save to file
            json_content = json.dumps(calc_data, indent=2)
            path = f"financial_calculations/{user_id}/compound_interest.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            response_parts = [
                f"Compound Interest Calculation",
                "=" * 60,
                f"\nInitial Investment: ${principal:,.2f}",
                f"Annual Interest Rate: {annual_rate}%",
                f"Time Period: {time_years} years",
                f"Compounding Frequency: {compound_frequency}",
            ]

            response_parts.append("\n---\n📈 Results:")
            response_parts.append(f"  Future Value: ${future_value:,.2f}")
            response_parts.append(f"  Total Interest Earned: ${compound_interest_earned:,.2f}")
            response_parts.append(
                f"  Total Return: {(compound_interest_earned / principal * 100):.1f}%"
            )

            response_parts.append("\n---\n💰 Compound Interest Bonus:")
            response_parts.append(f"  Simple Interest Future Value: ${simple_future_value:,.2f}")
            response_parts.append(f"  Compound Interest Future Value: ${future_value:,.2f}")
            response_parts.append(f"  Additional Earnings from Compounding: ${compound_bonus:,.2f}")

            response_parts.append("\n---\n📊 Year-by-Year Breakdown:")
            for year_data in yearly_breakdown[:5]:  # Show first 5 years
                response_parts.append(
                    f"\n  Year {year_data['year']}:"
                    f"\n    Starting Balance: ${year_data['starting_balance']:,.2f}"
                )
                response_parts.append(f"    Interest Earned: ${year_data['interest_earned']:,.2f}")
                response_parts.append(f"    Ending Balance: ${year_data['ending_balance']:,.2f}")

            if time_years > 5:
                response_parts.append(f"\n  ... ({time_years - 5} more years)")
                response_parts.append(
                    f"\n  Year {time_years}: ${yearly_breakdown[-1]['ending_balance']:,.2f}"
                )

            response_parts.append("\n---\n💡 Key Insight:")
            if compound_bonus > principal * 0.5:
                response_parts.append(
                    f"  Compounding adds ${compound_bonus:,.2f} more than simple interest!"
                )
            response_parts.append("  The power of compounding grows exponentially over time.")

            response_parts.append(f"\nCalculation saved to: {path}")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error calculating compound interest: {str(e)}"

    @tool
    def calculate_budget_ratio(
        user_id: str,
        income: float,
        category_spending: Dict[str, float],
        framework: Optional[str] = "50/30/20",
    ) -> str:
        """Calculate spending ratios across budget categories.

        This tool analyzes spending as a percentage of income and compares
        against established budgeting frameworks to identify areas where
        spending aligns or deviates from recommended ratios.

        Args:
            user_id: The user's unique identifier
            income: Monthly or annual income (specify in notes)
            category_spending: Dictionary of spending by category
                               {"housing": 1500, "food": 500, ...}
            framework: Budgeting framework to compare against ("50/30/20" or custom)

        Returns:
            Budget ratio analysis with category percentages, framework comparisons,
            and optimization recommendations. Saved to financial_assessments/{user_id}/

        Raises:
            ValueError: If required parameters are invalid

        Example:
            >>> calculate_budget_ratio(
            ...     "user_123",
            ...     5000,
            ...     {"housing": 1500, "food": 600, "transportation": 300},
            ...     framework="50/30/20"
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if income <= 0 or not isinstance(income, (int, float)):
            return "Error: income must be a positive number"
        if not category_spending or not isinstance(category_spending, dict):
            return "Error: category_spending must be a non-empty dictionary"

        try:
            total_spending = sum(category_spending.values())
            remaining_income = income - total_spending

            # Calculate ratios for each category
            category_ratios = {}
            for category, amount in category_spending.items():
                ratio = (amount / income * 100) if income > 0 else 0
                category_ratios[category] = round(ratio, 1)

            # Framework targets (50/30/20 rule)
            framework_targets = {
                "needs": 50,  # Housing, food, utilities, transportation
                "wants": 30,  # Entertainment, dining out, hobbies
                "savings": 20,  # Emergency fund, investments, debt repayment
            }

            # Categorize spending into needs/wants/savings
            needs_keywords = [
                "housing",
                "rent",
                "mortgage",
                "utilities",
                "food",
                "groceries",
                "transportation",
                "insurance",
                "healthcare",
            ]
            wants_keywords = [
                "entertainment",
                "dining",
                "restaurant",
                "hobbies",
                "shopping",
                "subscriptions",
            ]
            savings_keywords = ["savings", "investment", "debt", "emergency"]

            actual_spending = {"needs": 0, "wants": 0, "savings": remaining_income}

            for category, amount in category_spending.items():
                cat_lower = category.lower()
                matched = False
                for kw in needs_keywords:
                    if kw in cat_lower:
                        actual_spending["needs"] += amount
                        matched = True
                        break
                if not matched:
                    for kw in wants_keywords:
                        if kw in cat_lower:
                            actual_spending["wants"] += amount
                            matched = True
                            break

            # Calculate actual percentages
            actual_percentages = {
                key: round((value / income * 100) if income > 0 else 0, 1)
                for key, value in actual_spending.items()
            }

            # Calculate gaps
            gaps = {
                key: round(actual_percentages[key] - framework_targets[key], 1)
                for key in framework_targets.keys()
            }

            # Generate recommendations
            recommendations = []
            if gaps["needs"] > 5:
                recommendations.append(
                    f"⚠ Needs spending ({actual_percentages['needs']}%) exceeds 50% target by {abs(gaps['needs'])}%"
                )
            if gaps["wants"] > 5:
                recommendations.append(
                    f"◐ Wants spending ({actual_percentages['wants']}%) exceeds 30% target by {abs(gaps['wants'])}%"
                )
            if gaps["savings"] < 0:
                recommendations.append(
                    f"📉 Savings rate ({actual_percentages['savings']}%) is below 20% target"
                )
            if remaining_income < 0:
                recommendations.append(
                    f"🚨 OVER BUDGET: You are spending ${abs(remaining_income):,.2f} more than you earn"
                )

            # Build ratio data
            ratio_data = {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "income": income,
                "total_spending": total_spending,
                "remaining_income": remaining_income,
                "category_ratios": category_ratios,
                "framework_comparison": {
                    "targets": framework_targets,
                    "actual": actual_spending,
                    "percentages": actual_percentages,
                    "gaps": gaps,
                },
                "recommendations": recommendations,
            }

            # Save to file
            json_content = json.dumps(ratio_data, indent=2)
            today = date.today()
            path = f"financial_assessments/{user_id}/{today}_budget_ratios.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            response_parts = [
                f"Budget Ratio Analysis ({framework.upper()} Framework)",
                "=" * 60,
                f"\nTotal Income: ${income:,.2f}",
                f"Total Spending: ${total_spending:,.2f} ({(total_spending / income * 100):.1f}%)",
                f"Remaining: ${remaining_income:,.2f} ({(remaining_income / income * 100):.1f}%)",
            ]

            response_parts.append("\n---\n📊 Category Breakdown:")
            for category, ratio in sorted(
                category_ratios.items(), key=lambda x: x[1], reverse=True
            ):
                bar = "█" * int(ratio / 2)
                response_parts.append(f"  {category.title():<20} {ratio:>6}% |{bar}")

            response_parts.append("\n---\n🎯 Framework Comparison (50/30/20 Rule):")
            for category in ["needs", "wants", "savings"]:
                target = framework_targets[category]
                actual = actual_percentages[category]
                gap = gaps[category]
                status = "✓" if abs(gap) <= 5 else ("⚠️" if gap > 0 else "📉")
                response_parts.append(
                    f"  {category.title():<10} Target: {target:>3}% | Actual: {actual:>6}% ({status})"
                )

            if recommendations:
                response_parts.append("\n---\n💡 Recommendations:")
                for rec in recommendations:
                    response_parts.append(f"  {rec}")

            response_parts.append(f"\nAnalysis saved to: {path}")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error calculating budget ratios: {str(e)}"

    @tool
    def estimate_debt_free_date(
        user_id: str,
        debts: List[Dict[str, Any]],
        monthly_payment: float,
    ) -> str:
        """Estimate when you'll become debt-free based on current payment plan.

        This tool calculates the timeline to becoming debt-free, projecting
        month-by-month payoff schedules and showing how extra payments could
        accelerate the journey.

        Args:
            user_id: The user's unique identifier
            debts: List of debt dictionaries with 'name', 'balance', and 'interest_rate'
                   [{"name": "Credit Card", "balance": 5000, "interest_rate": 18.5}, ...]
            monthly_payment: Total amount you can pay toward debt each month

        Returns:
            Debt-free date estimate with payoff timeline, total interest paid,
            and accelerated payoff scenarios. Saved to financial_plans/{user_id}/

        Raises:
            ValueError: If required parameters are invalid

        Example:
            >>> estimate_debt_free_date(
            ...     "user_123",
            ...     [{"name": "Credit Card", "balance": 5000, "interest_rate": 18.5}],
            ...     500
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not debts or not isinstance(debts, list):
            return "Error: debts must be a non-empty list"
        if monthly_payment <= 0 or not isinstance(monthly_payment, (int, float)):
            return "Error: monthly_payment must be a positive number"

        # Validate each debt
        for debt in debts:
            if not isinstance(debt, dict):
                return "Error: each debt must be a dictionary"
            if "name" not in debt or "balance" not in debt or "interest_rate" not in debt:
                return "Error: each debt must have 'name', 'balance', and 'interest_rate'"
            if debt["balance"] <= 0 or debt["interest_rate"] < 0:
                return "Error: balance must be positive and interest_rate must be non-negative"

        try:
            # Calculate total debt
            total_debt = sum(debt["balance"] for debt in debts)

            # Check if payment is sufficient
            total_minimum = sum(max(debt["balance"] * 0.02, 25) for debt in debts)
            if monthly_payment < total_minimum:
                return (
                    f"Error: Monthly payment (${monthly_payment:.2f}) is less than "
                    f"total minimum payments (${total_minimum:.2f}). You may never become debt-free "
                    "at this rate."
                )

            # Simulate payoff (avalanche method - highest interest first)
            working_debts = [
                {
                    "name": d["name"],
                    "balance": float(d["balance"]),
                    "interest_rate": float(d["interest_rate"]),
                }
                for d in sorted(debts, key=lambda x: -x["interest_rate"])
            ]

            current_date = datetime.now()
            month_count = 0
            total_interest_paid = 0.0

            payoff_schedule = []

            while any(d["balance"] > 0 for d in working_debts):
                month_count += 1
                payment_remaining = monthly_payment

                # Calculate and apply minimums first
                min_payments = [max(d["balance"] * 0.02, 25) for d in working_debts]
                total_min = sum(min_payments)

                # Apply interest
                for debt in working_debts:
                    if debt["balance"] > 0:
                        monthly_interest = debt["balance"] * (debt["interest_rate"] / 100 / 12)
                        total_interest_paid += monthly_interest
                        debt["balance"] += monthly_interest

                # Apply payments
                for i, debt in enumerate(working_debts):
                    if debt["balance"] > 0:
                        min_pay = min(min_payments[i], payment_remaining)
                        debt["balance"] -= min_pay
                        payment_remaining -= min_pay

                # Apply extra to highest interest debt (first non-zero)
                if payment_remaining > 0:
                    for debt in working_debts:
                        if debt["balance"] > 0:
                            extra = min(debt["balance"], payment_remaining)
                            debt["balance"] -= extra
                            payment_remaining -= extra

                # Track payoff milestones
                debts_paid_off = [d["name"] for d in working_debts if d["balance"] <= 0]
                if debts_paid_off:
                    payoff_date = current_date + pd_timedelta(days=month_count * 30)
                    for debt_name in debts_paid_off:
                        payoff_schedule.append(
                            {
                                "debt": debt_name,
                                "months": month_count,
                                "date": payoff_date.strftime("%Y-%m-%d"),
                            }
                        )

                # Safety cap
                if month_count > 600:  # 50 years max
                    break

            # Calculate debt-free date
            from datetime import timedelta as pd_timedelta

            debt_free_date = current_date + pd_timedelta(days=month_count * 30)
            years_to_freedom = month_count / 12

            # Calculate accelerated scenarios
            scenarios = []
            for accelerator in [1.2, 1.5]:  # 20% and 50% extra payments
                accelerated_months = int(month_count / accelerator)
                accelerated_date = current_date + pd_timedelta(days=accelerated_months * 30)
                scenarios.append(
                    {
                        "payment_multiplier": accelerator,
                        "monthly_payment": round(monthly_payment * accelerator, 2),
                        "months_to_freedom": accelerated_months,
                        "years_to_freedom": round(accelerated_months / 12, 1),
                        "debt_free_date": accelerated_date.strftime("%Y-%m-%d"),
                    }
                )

            # Build estimate data
            estimate_data = {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "debts": debts,
                "total_debt": total_debt,
                "monthly_payment": monthly_payment,
                "months_to_freedom": month_count,
                "years_to_freedom": round(years_to_freedom, 1),
                "debt_free_date": debt_free_date.strftime("%Y-%m-%d"),
                "total_interest_paid": round(total_interest_paid, 2),
                "total_amount_paid": round(total_debt + total_interest_paid, 2),
                "payoff_schedule": payoff_schedule,
                "accelerated_scenarios": scenarios,
            }

            # Save to file
            json_content = json.dumps(estimate_data, indent=2)
            path = f"financial_plans/{user_id}/debt_free_estimate.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            response_parts = [
                "Debt-Free Date Estimate",
                "=" * 60,
                f"\nTotal Debt: ${total_debt:,.2f}",
                f"Monthly Payment: ${monthly_payment:,.2f}",
            ]

            response_parts.append("\n---\n🎉 Your Debt-Free Date:")
            response_parts.append(f"  {debt_free_date.strftime('%B %Y')}")
            response_parts.append(
                f"  Time to Freedom: {years_to_freedom:.1f} years ({month_count} months)"
            )

            response_parts.append("\n---\n💰 Total Cost:")
            response_parts.append(f"  Principal: ${total_debt:,.2f}")
            response_parts.append(f"  Total Interest: ${total_interest_paid:,.2f}")
            response_parts.append(f"  Total Paid: ${total_debt + total_interest_paid:,.2f}")

            if payoff_schedule:
                response_parts.append("\n---\n📅 Payoff Schedule:")
                for milestone in payoff_schedule:
                    response_parts.append(
                        f"  {milestone['months']} months ({milestone['date']}) - {milestone['debt']}"
                    )

            if scenarios:
                response_parts.append("\n---\n🚀 Accelerated Payoff Scenarios:")
                for scenario in scenarios:
                    months_saved = month_count - scenario["months_to_freedom"]
                    response_parts.append(
                        f"\n  {scenario['payment_multiplier']:.0f}x Payments (${scenario['monthly_payment']:,.2f}/month):"
                    )
                    response_parts.append(f"    Debt-free: {scenario['debt_free_date']}")
                    response_parts.append(
                        f"    Time saved: {months_saved} months ({months_saved / 12:.1f} years)"
                    )

            response_parts.append("\n---\n💡 Tips:")
            response_parts.append("  • Consider increasing payments as income allows")
            response_parts.append("  • Use any windfalls (bonuses, tax refunds) as extra payments")
            response_parts.append("  • Track progress monthly to stay motivated")

            response_parts.append(f"\nEstimate saved to: {path}")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error estimating debt-free date: {str(e)}"

    print("Finance tools created successfully!")
    return (
        create_budget_analyzer,
        generate_debt_payoff_plan,
        calculate_emergency_fund_target,
        set_financial_goal,
        analyze_expense_optimization,
        calculate_savings_timeline,
        calculate_compound_interest,
        calculate_budget_ratio,
        estimate_debt_free_date,
    )


# Export tools at module level for convenience
__all__ = [
    "create_finance_tools",
]


# Helper function for date calculations (needed for set_financial_goal)
def pd_timedelta(days: int):
    """Simple timedelta implementation."""
    from datetime import timedelta

    return timedelta(days=days)
