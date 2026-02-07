"""
Tests for Finance Coach tools.

This module tests all finance-specific tools including budget analysis,
debt payoff planning, emergency fund calculation, financial goal setting,
expense optimization, and savings timeline calculation.
"""

import pytest
import json
from pathlib import Path
from datetime import date, datetime

# Add parent directory to path for imports
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.finance_tools import create_finance_tools
from deepagents.backends import FilesystemBackend


class TestFinanceTools:
    """Test suite for finance coach tools."""

    def setup_method(self):
        """Setup test fixtures before each test."""
        # Create a mock FilesystemBackend
        self.backend = FilesystemBackend(root_dir="/tmp/test_finance_workspace")
        # Create finance tools with mock backend
        self.finance_tools = create_finance_tools(backend=self.backend)

    # ========================================================================
    # Test create_budget_analyzer
    # ========================================================================

    def test_create_budget_analyzer_basic(self):
        """Test basic budget analysis with 50/30/20 framework."""
        create_budget_analyzer = self.finance_tools[0]
        result = create_budget_analyzer.invoke(
            {
                "user_id": "test_user",
                "monthly_income": 5000,
                "expenses": {"rent": 1500, "groceries": 400, "dining_out": 300},
            }
        )

        assert isinstance(result, str)
        assert "Budget Analysis" in result
        assert "$5,000.00" in result

    def test_create_budget_analyzer_503020_framework(self):
        """Test budget analysis with 50/30/20 framework."""
        create_budget_analyzer = self.finance_tools[0]
        result = create_budget_analyzer.invoke(
            {
                "user_id": "test_user",
                "monthly_income": 5000,
                "expenses": {
                    "rent": 1500,  # needs
                    "groceries": 400,  # needs
                    "utilities": 200,  # needs
                    "entertainment": 300,  # wants
                },
                "budget_framework": "50/30/20",
            }
        )

        assert isinstance(result, str)
        assert "Budget Analysis" in result
        assert "Needs (Essentials)" in result
        assert "Wants (Discretionary)" in result

    def test_create_budget_analyzer_deficit(self):
        """Test budget analysis with spending exceeding income."""
        create_budget_analyzer = self.finance_tools[0]
        result = create_budget_analyzer.invoke(
            {
                "user_id": "test_user",
                "monthly_income": 3000,
                "expenses": {
                    "rent": 2000,
                    "groceries": 500,
                    "entertainment": 700,  # Total exceeds income
                },
            }
        )

        assert isinstance(result, str)
        assert "DEFICIT" in result

    def test_create_budget_analyzer_invalid_user_id(self):
        """Test budget analysis with invalid user ID."""
        create_budget_analyzer = self.finance_tools[0]
        result = create_budget_analyzer.invoke(
            {"user_id": "", "monthly_income": 5000, "expenses": {}}
        )

        assert "Error" in result
        assert "user_id must be a non-empty string" in result

    def test_create_budget_analyzer_invalid_income(self):
        """Test budget analysis with invalid income."""
        create_budget_analyzer = self.finance_tools[0]
        result = create_budget_analyzer.invoke(
            {"user_id": "test_user", "monthly_income": -100, "expenses": {}}
        )

        assert "Error" in result
        assert "monthly_income must be a positive number" in result

    # ========================================================================
    # Test generate_debt_payoff_plan
    # ========================================================================

    def test_generate_debt_payoff_plan_avalanche(self):
        """Test debt payoff with avalanche method."""
        generate_debt_payoff_plan = self.finance_tools[1]
        result = generate_debt_payoff_plan.invoke(
            {
                "user_id": "test_user",
                "debts": [
                    {"name": "Credit Card", "balance": 5000, "interest_rate": 18.5},
                    {"name": "Car Loan", "balance": 15000, "interest_rate": 5.0},
                ],
                "strategy": "avalanche",
            }
        )

        assert isinstance(result, str)
        assert "Debt Payoff Plan" in result
        assert "Avalanche" in result

    def test_generate_debt_payoff_plan_snowball(self):
        """Test debt payoff with snowball method."""
        generate_debt_payoff_plan = self.finance_tools[1]
        result = generate_debt_payoff_plan.invoke(
            {
                "user_id": "test_user",
                "debts": [
                    {"name": "Credit Card", "balance": 5000, "interest_rate": 18.5},
                    {"name": "Personal Loan", "balance": 2000, "interest_rate": 10.0},
                ],
                "strategy": "snowball",
            }
        )

        assert isinstance(result, str)
        assert "Debt Payoff Plan" in result
        assert "Snowball" in result

    def test_generate_debt_payoff_plan_compare(self):
        """Test debt payoff with method comparison."""
        generate_debt_payoff_plan = self.finance_tools[1]
        result = generate_debt_payoff_plan.invoke(
            {
                "user_id": "test_user",
                "debts": [
                    {"name": "Credit Card", "balance": 5000, "interest_rate": 18.5},
                    {"name": "Car Loan", "balance": 15000, "interest_rate": 5.0},
                ],
                "strategy": "compare",
            }
        )

        assert isinstance(result, str)
        assert "Comparison" in result
        assert "Avalanche" in result
        assert "Snowball" in result

    def test_generate_debt_payoff_plan_invalid_user_id(self):
        """Test debt payoff with invalid user ID."""
        generate_debt_payoff_plan = self.finance_tools[1]
        result = generate_debt_payoff_plan.invoke(
            {"user_id": "", "debts": [], "strategy": "avalanche"}
        )

        assert "Error" in result
        assert "user_id must be a non-empty string" in result

    def test_generate_debt_payoff_plan_invalid_debts(self):
        """Test debt payoff with invalid debts."""
        generate_debt_payoff_plan = self.finance_tools[1]
        result = generate_debt_payoff_plan.invoke(
            {"user_id": "test_user", "debts": [], "strategy": "avalanche"}
        )

        assert "Error" in result
        assert "debts must be a non-empty list" in result

    # ========================================================================
    # Test calculate_emergency_fund_target
    # ========================================================================

    def test_calculate_emergency_fund_basic(self):
        """Test emergency fund calculation with basic parameters."""
        calculate_emergency_fund_target = self.finance_tools[2]
        result = calculate_emergency_fund_target.invoke(
            {
                "user_id": "test_user",
                "monthly_essential_expenses": 3000,
            }
        )

        assert isinstance(result, str)
        assert "Emergency Fund Calculation" in result
        assert "$3,000.00" in result

    def test_calculate_emergency_fund_with_dependents(self):
        """Test emergency fund calculation with dependents."""
        calculate_emergency_fund_target = self.finance_tools[2]
        result = calculate_emergency_fund_target.invoke(
            {
                "user_id": "test_user",
                "monthly_essential_expenses": 4000,
                "dependents": 2,
            }
        )

        assert isinstance(result, str)
        assert "Emergency Fund Calculation" in result
        assert "Dependents: 2" in result

    def test_calculate_emergency_fund_homeowner(self):
        """Test emergency fund calculation for homeowner."""
        calculate_emergency_fund_target = self.finance_tools[2]
        result = calculate_emergency_fund_target.invoke(
            {
                "user_id": "test_user",
                "monthly_essential_expenses": 3500,
                "home_owner": True,
            }
        )

        assert isinstance(result, str)
        assert "Emergency Fund Calculation" in result
        assert "Home Owner: Yes" in result

    def test_calculate_emergency_fund_invalid_user_id(self):
        """Test emergency fund with invalid user ID."""
        calculate_emergency_fund_target = self.finance_tools[2]
        result = calculate_emergency_fund_target.invoke(
            {"user_id": "", "monthly_essential_expenses": 3000}
        )

        assert "Error" in result
        assert "user_id must be a non-empty string" in result

    def test_calculate_emergency_fund_invalid_expenses(self):
        """Test emergency fund with invalid expenses."""
        calculate_emergency_fund_target = self.finance_tools[2]
        result = calculate_emergency_fund_target.invoke(
            {"user_id": "test_user", "monthly_essential_expenses": -100}
        )

        assert "Error" in result
        assert "monthly_essential_expenses must be a positive number" in result

    # ========================================================================
    # Test set_financial_goal
    # ========================================================================

    def test_set_financial_goal_basic(self):
        """Test setting a basic financial goal."""
        set_financial_goal = self.finance_tools[3]
        result = set_financial_goal.invoke(
            {
                "user_id": "test_user",
                "goal_name": "House Down Payment",
                "target_amount": 60000,
                "target_date": "2027-12-31",
            }
        )

        assert isinstance(result, str)
        assert "SMART Financial Goal" in result
        assert "House Down Payment" in result

    def test_set_financial_goal_with_savings(self):
        """Test setting financial goal with existing savings."""
        set_financial_goal = self.finance_tools[3]
        result = set_financial_goal.invoke(
            {
                "user_id": "test_user",
                "goal_name": "Emergency Fund",
                "target_amount": 15000,
                "target_date": "2026-06-30",
                "current_savings": 5000,
            }
        )

        assert isinstance(result, str)
        assert "SMART Financial Goal" in result
        assert "$5,000.00" in result

    def test_set_financial_goal_long_term(self):
        """Test setting a long-term financial goal."""
        set_financial_goal = self.finance_tools[3]
        result = set_financial_goal.invoke(
            {
                "user_id": "test_user",
                "goal_name": "Retirement Fund",
                "target_amount": 500000,
                "target_date": "2045-12-31",
                "category": "retirement",
            }
        )

        assert isinstance(result, str)
        assert "SMART Financial Goal" in result
        assert "long-term" in result.lower()

    def test_set_financial_goal_invalid_user_id(self):
        """Test setting goal with invalid user ID."""
        set_financial_goal = self.finance_tools[3]
        result = set_financial_goal.invoke(
            {"user_id": "", "goal_name": "Test", "target_amount": 1000, "target_date": "2025-12-31"}
        )

        assert "Error" in result
        assert "user_id must be a non-empty string" in result

    def test_set_financial_goal_invalid_amount(self):
        """Test setting goal with invalid amount."""
        set_financial_goal = self.finance_tools[3]
        result = set_financial_goal.invoke(
            {
                "user_id": "test_user",
                "goal_name": "Test",
                "target_amount": -100,
                "target_date": "2025-12-31",
            }
        )

        assert "Error" in result
        assert "target_amount must be a positive number" in result

    def test_set_financial_goal_invalid_date(self):
        """Test setting goal with invalid date format."""
        set_financial_goal = self.finance_tools[3]
        result = set_financial_goal.invoke(
            {
                "user_id": "test_user",
                "goal_name": "Test",
                "target_amount": 1000,
                "target_date": "invalid",
            }
        )

        assert "Error" in result
        assert "target_date must be in YYYY-MM-DD format" in result

    # ========================================================================
    # Test analyze_expense_optimization
    # ========================================================================

    def test_analyze_expense_optimization_basic(self):
        """Test basic expense optimization analysis."""
        analyze_expense_optimization = self.finance_tools[4]
        result = analyze_expense_optimization.invoke(
            {
                "user_id": "test_user",
                "expenses": {"rent": 1500, "groceries": 400, "entertainment": 200},
            }
        )

        assert isinstance(result, str)
        assert "Expense Optimization Analysis" in result

    def test_analyze_expense_optimization_subscriptions(self):
        """Test expense optimization with subscription services."""
        analyze_expense_optimization = self.finance_tools[4]
        result = analyze_expense_optimization.invoke(
            {
                "user_id": "test_user",
                "expenses": {
                    "rent": 1500,
                    "netflix": 15,
                    "spotify": 10,
                    "dining_out": 300,
                },
            }
        )

        assert isinstance(result, str)
        assert "Expense Optimization Analysis" in result
        assert "Subscriptions" in result or "Optimization Opportunities" in result

    def test_analyze_expense_optimization_with_income(self):
        """Test expense optimization with income context."""
        analyze_expense_optimization = self.finance_tools[4]
        result = analyze_expense_optimization.invoke(
            {
                "user_id": "test_user",
                "expenses": {"rent": 1500, "groceries": 400},
                "monthly_income": 5000,
            }
        )

        assert isinstance(result, str)
        assert "Expense Optimization Analysis" in result

    def test_analyze_expense_optimization_invalid_user_id(self):
        """Test expense optimization with invalid user ID."""
        analyze_expense_optimization = self.finance_tools[4]
        result = analyze_expense_optimization.invoke({"user_id": "", "expenses": {}})

        assert "Error" in result
        assert "user_id must be a non-empty string" in result

    def test_analyze_expense_optimization_empty_expenses(self):
        """Test expense optimization with empty expenses (should return error)."""
        analyze_expense_optimization = self.finance_tools[4]
        # Empty dict is not valid - should return error
        result = analyze_expense_optimization.invoke({"user_id": "test_user", "expenses": {}})

        assert isinstance(result, str)
        assert "Error" in result
        # Should handle empty expenses with validation error

    # ========================================================================
    # Test calculate_savings_timeline
    # ========================================================================

    def test_calculate_savings_timeline_basic(self):
        """Test basic savings timeline calculation."""
        calculate_savings_timeline = self.finance_tools[5]
        result = calculate_savings_timeline.invoke(
            {
                "user_id": "test_user",
                "goal_amount": 50000,
                "monthly_contribution": 800,
            }
        )

        assert isinstance(result, str)
        assert "Savings Timeline Calculator" in result

    def test_calculate_savings_timeline_with_current_savings(self):
        """Test savings timeline with existing savings."""
        calculate_savings_timeline = self.finance_tools[5]
        result = calculate_savings_timeline.invoke(
            {
                "user_id": "test_user",
                "goal_amount": 50000,
                "monthly_contribution": 800,
                "current_savings": 10000,
            }
        )

        assert isinstance(result, str)
        assert "Savings Timeline Calculator" in result
        assert "$10,000.00" in result

    def test_calculate_savings_timeline_with_higher_return(self):
        """Test savings timeline with higher return rate."""
        calculate_savings_timeline = self.finance_tools[5]
        result = calculate_savings_timeline.invoke(
            {
                "user_id": "test_user",
                "goal_amount": 100000,
                "monthly_contribution": 1500,
                "annual_return_rate": 7.0,
            }
        )

        assert isinstance(result, str)
        assert "Savings Timeline Calculator" in result
        assert "7.0%" in result or "7%" in result  # Accept either format

    def test_calculate_savings_timeline_invalid_user_id(self):
        """Test savings timeline with invalid user ID."""
        calculate_savings_timeline = self.finance_tools[5]
        result = calculate_savings_timeline.invoke(
            {"user_id": "", "goal_amount": 10000, "monthly_contribution": 500}
        )

        assert "Error" in result
        assert "user_id must be a non-empty string" in result

    def test_calculate_savings_timeline_invalid_goal(self):
        """Test savings timeline with invalid goal amount."""
        calculate_savings_timeline = self.finance_tools[5]
        result = calculate_savings_timeline.invoke(
            {"user_id": "test_user", "goal_amount": -100, "monthly_contribution": 500}
        )

        assert "Error" in result
        assert "goal_amount must be a positive number" in result

    def test_calculate_savings_timeline_invalid_contribution(self):
        """Test savings timeline with invalid contribution."""
        calculate_savings_timeline = self.finance_tools[5]
        result = calculate_savings_timeline.invoke(
            {"user_id": "test_user", "goal_amount": 10000, "monthly_contribution": -500}
        )

        assert "Error" in result
        assert "monthly_contribution must be a positive number" in result

    # ========================================================================
    # Integration Tests
    # ========================================================================

    def test_complete_financial_planning_workflow(self):
        """Test a complete financial planning workflow using multiple tools."""
        # 1. Create budget
        create_budget_analyzer = self.finance_tools[0]
        budget_result = create_budget_analyzer.invoke(
            {
                "user_id": "test_user",
                "monthly_income": 5000,
                "expenses": {"rent": 1500, "groceries": 400, "utilities": 200, "dining_out": 300},
            }
        )
        assert "Budget Analysis" in budget_result

        # 2. Calculate emergency fund
        calculate_emergency_fund_target = self.finance_tools[2]
        emergency_result = calculate_emergency_fund_target.invoke(
            {
                "user_id": "test_user",
                "monthly_essential_expenses": 2100,  # rent + groceries + utilities
            }
        )
        assert "Emergency Fund Calculation" in emergency_result

        # 3. Set financial goal
        set_financial_goal = self.finance_tools[3]
        goal_result = set_financial_goal.invoke(
            {
                "user_id": "test_user",
                "goal_name": "Emergency Fund",
                "target_amount": 12600,  # 6 months from emergency calculation
                "target_date": "2027-12-31",
            }
        )
        assert "SMART Financial Goal" in goal_result

        # 4. Calculate savings timeline
        calculate_savings_timeline = self.finance_tools[5]
        timeline_result = calculate_savings_timeline.invoke(
            {
                "user_id": "test_user",
                "goal_amount": 12600,
                "monthly_contribution": 500,
            }
        )
        assert "Savings Timeline Calculator" in timeline_result

    def test_debt_management_workflow(self):
        """Test a debt management workflow."""
        # 1. Analyze budget to understand capacity
        create_budget_analyzer = self.finance_tools[0]
        budget_result = create_budget_analyzer.invoke(
            {
                "user_id": "test_user",
                "monthly_income": 4000,
                "expenses": {"rent": 1200, "groceries": 300, "utilities": 150},
            }
        )
        assert "Budget Analysis" in budget_result

        # 2. Generate debt payoff plan
        generate_debt_payoff_plan = self.finance_tools[1]
        debt_result = generate_debt_payoff_plan.invoke(
            {
                "user_id": "test_user",
                "debts": [
                    {"name": "Credit Card", "balance": 5000, "interest_rate": 18.5},
                ],
                "strategy": "avalanche",
                "monthly_payment": 500,
            }
        )
        assert "Debt Payoff Plan" in debt_result

    def test_all_tools_created(self):
        """Test that all finance tools are created successfully."""
        assert len(self.finance_tools) == 9
        tool_names = [
            "create_budget_analyzer",
            "generate_debt_payoff_plan",
            "calculate_emergency_fund_target",
            "set_financial_goal",
            "analyze_expense_optimization",
            "calculate_savings_timeline",
            "calculate_compound_interest",
            "calculate_budget_ratio",
            "estimate_debt_free_date",
        ]
        for i, tool in enumerate(self.finance_tools):
            assert hasattr(tool, "func") or callable(tool)
