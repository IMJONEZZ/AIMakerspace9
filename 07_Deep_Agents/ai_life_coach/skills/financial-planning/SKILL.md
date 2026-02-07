---
name: financial-planning
description: Personal finance guidance including budget creation, debt management strategies, savings planning, and basic financial goal setting
version: 1.0.0
tools:
  - write_file
  - read_file
---

# Financial Planning Skill

## Purpose

This skill provides comprehensive personal finance guidance including:

1. **Budget Creation**: Income allocation, expense tracking, spending optimization
2. **Debt Management**: Prioritization strategies, payoff plans, debt reduction techniques
3. **Savings Planning**: Emergency funds, short-term goals, long-term planning
4. **Financial Goal Setting**: SMART financial objectives and roadmaps
5. **Basic Financial Literacy**: Understanding credit, interest rates, investment fundamentals

## Workflow

### Step 1: Financial Assessment Framework

When a user requests financial guidance:

1. **Gather Information**:
   - Current income sources and amounts
   - Fixed expenses (rent/mortgage, utilities, insurance)
   - Variable expenses (food, entertainment, transportation)
   - Current debt balances and interest rates
   - Existing savings and emergency fund status
   - Financial goals (short-term: <1 year, medium-term: 1-5 years, long-term: 5+ years)
   - Current age and risk tolerance (for investment discussions)

2. **Financial Health Check**:
   - Calculate debt-to-income ratio
   - Assess emergency fund adequacy (3-6 months of expenses recommended)
   - Review spending patterns and identify waste
   - Check credit score impact factors

### Step 2: Budget Creation Process

#### The 50/30/20 Rule Framework:
- **50% Needs**: Essential expenses (housing, food, utilities, minimum debt payments)
- **30% Wants**: Discretionary spending (entertainment, dining out, hobbies)
- **20% Savings/Debt Repayment**: Emergency fund, retirement, extra debt payments

#### Detailed Budget Categories:

**Fixed Expenses (Needs)**:
- Housing (rent/mortgage, HOA, property taxes)
- Utilities (electricity, water, gas, internet, phone)
- Insurance (health, auto, renters/homeowners)
- Transportation costs (car payment, insurance, gas/public transit)
- Minimum debt payments

**Variable Expenses (Needs)**:
- Groceries
- Household supplies
- Personal care
- Medical costs (copays, prescriptions)

**Discretionary Expenses (Wants)**:
- Dining out
- Entertainment/streaming services
- Hobbies and recreation
- Shopping (non-essentials)
- Vacations

**Savings/Debt Categories**:
- Emergency fund contributions
- Retirement savings (401k, IRA)
- Short-term goal savings
- Extra debt payments (above minimums)

### Step 3: Debt Management Strategy

#### Debt Prioritization:

**Avalanche Method** (Mathematically optimal):
1. List debts by interest rate (highest to lowest)
2. Pay minimums on all debts
3. Put extra money toward highest-interest debt
4. When paid off, move to next-highest rate

**Snowball Method** (Psychologically motivating):
1. List debts by balance (smallest to largest)
2. Pay minimums on all debts
3. Put extra money toward smallest-balance debt
4. When paid off, move to next-smallest balance

Choose based on user's personality and motivation style.

### Step 4: Savings Hierarchy

**Priority Order for Extra Money**:

1. **Emergency Fund (High Priority)**:
   - Target: 3-6 months of essential expenses
   - Keep in high-yield savings account
   - Only use for true emergencies

2. **High-Interest Debt (Next Priority)**:
   - Credit cards with >15% APR
   - Pay off before investing

3. **Employer Match (Free Money)**:
   - Contribute enough to get full employer 401k match

4. **Short-Term Goals**:
   - Vacation, car down payment, etc.
   - Timeline: 1-2 years
   - Use high-yield savings or CDs

5. **Long-Term Retirement**:
   - Max out tax-advantaged accounts (401k, IRA)
   - Consider index funds for diversification
   - Timeline: 5+ years

### Step 5: Documentation

Save financial plans and budgets:

```
assessments/{user_id}/
├── financial_assessment_{date}.md     # Overall assessment
└── debt_inventory.xlsx                # Detailed debt breakdown

plans/{user_id}/
├── monthly_budget.xlsx                 # Budget template with categories
├── debt_payoff_plan.md                 # Debt elimination strategy
└── savings_goals_roadmap.md            # Timeline for financial goals

workspace/resources/
├── budget_tracker_template.csv         # Monthly tracking template
└── financial_checklist.md              # Regular tasks (bill payments, etc.)
```

## Best Practices

1. **Automate Where Possible**: Set up automatic transfers for savings and bill payments
2. **Track Regularly**: Review spending at least monthly, adjust as needed
3. **Be Realistic**: Budgets should reflect actual spending habits, not idealized ones
4. **Build Flexibility**: Always include a "buffer" category for unexpected expenses
5. **Celebrate Milestones**: Acknowledge progress toward financial goals

## Budget Template Structure

```csv
Category,Subcategory,Budgeted,Actual,Difference,Notes
Housing,Rent,$1500,$1500,$0,
Utilities,Electricity,$100,$85,+$15,Saved by turning off lights
Food,Groceries,$400,$450,-$50,Need to meal plan better
Transportation,Gas,$150,$120,+$30,
Debt,Credit Card Minimum,$200,$200,$0,
Savings,Emergency Fund,$300,$300,$0,
...
TOTAL,,$2650,$2700,-$50,
```

## Output Format

When delivering financial guidance:

1. **Executive Summary**: Top 3-5 key findings and immediate recommendations
2. **Financial Health Assessment**:
   - Current financial standing overview
   - Key metrics (debt-to-income ratio, emergency fund status)
   - Identified areas for improvement
3. **Action Plan**:
   - Prioritized budget adjustments
   - Debt payoff strategy and timeline
   - Savings goals roadmap with milestones
4. **Tools & Templates**:
   - Budget tracker template
   - Debt payoff calculator/plan
   - Savings goal worksheet
5. **Files Created**: List of all saved documents with descriptions

## Example Prompts to Trigger This Skill

- "Help me create a budget"
- "I need a plan to pay off my credit card debt"
- "How much should I save for emergencies?"
- "I want to buy a house in 5 years—how do I prepare?"
- "What's the best order to tackle my student loans and car payment?"

## Important Notes

- Financial guidance is educational, not professional financial advice
- Users should consult qualified advisors for complex situations
- Life circumstances change—plans need regular review and adjustment
- Small, consistent actions compound over time (both positively and negatively)
- Financial health impacts mental health—acknowledge the emotional component

## When to Recommend Professional Help

Consider recommending professional financial advice if:

- Complex tax situations (self-employed, multiple income streams)
- Large debt loads (>50% of annual income)
- Nearing retirement with inadequate savings
- Considering major investments (real estate, starting business)
- Estate planning needs (wills, trusts)
- Special circumstances (divorce, inheritance, disability)

## Common Financial Pitfalls to Warn Against

1. **Lifestyle Creep**: Increasing spending as income rises
2. **Neglecting Emergency Fund**: No cushion for unexpected expenses
3. **High-Interest Debt Carrying**: Paying interest instead of building wealth
4. **Inadequate Retirement Savings**: Starting too late or contributing too little
5. **Impulse Purchases**: Small, frequent expenses that add up
6. **Not Tracking Spending**: Flying blind with money management
7. **Keeping Up Appearances**: Spending to impress others rather than for personal values