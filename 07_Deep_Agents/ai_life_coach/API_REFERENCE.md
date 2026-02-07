# API Reference

This document provides comprehensive API documentation for all tools, agents, and interfaces in the AI Life Coach system.

## Table of Contents

- [Core APIs](#core-apis)
- [Memory Tools](#memory-tools)
- [Planning Tools](#planning-tools)
- [Context Tools](#context-tools)
- [Assessment Tools](#assessment-tools)
- [Career Tools](#career-tools)
- [Relationship Tools](#relationship-tools)
- [Finance Tools](#finance-tools)
- [Wellness Tools](#wellness-tools)
- [Cross-Domain Tools](#cross-domain-tools)
- [Communication Tools](#communication-tools)
- [Emergency Tools](#emergency-tools)
- [User Management Tools](#user-management-tools)
- [Helper Functions](#helper-functions)

## Core APIs

### `create_life_coach()` → CompiledStateGraph

**Description**: Creates the complete AI Life Coach system with all specialists and tools.

**Returns**: 
- `CompiledStateGraph`: Configured Life Coach agent ready for invocation

**Example**:
```python
from src.main import create_life_coach

coach = create_life_coach()
result = coach.invoke({
    "messages": [{
        "role": "user", 
        "content": "I need help with my career"
    }]
})
```

### `create_memory_store()` → InMemoryStore

**Description**: Initializes the persistent memory store with namespace management.

**Returns**:
- `InMemoryStore`: Configured memory store instance

**Example**:
```python
from src.memory import create_memory_store

store = create_memory_store()
store.put(("user_123", "profile"), "demographics", {"name": "Alex"})
```

### `get_backend()` → FilesystemBackend

**Description**: Returns configured filesystem backend for context management.

**Returns**:
- `FilesystemBackend`: Backend instance for workspace operations

---

## Memory Tools

Located in: `src/tools/memory_tools.py`

### `get_user_profile(user_id: str) -> str`

**Description**: Retrieves comprehensive user profile including demographics, goals, and preferences.

**Parameters**:
- `user_id` (str): Unique identifier for the user

**Returns**: 
- `str`: JSON string containing user profile data

**Example**:
```python
profile = get_user_profile("user_123")
# Returns: {"name": "Alex", "age": 35, "goals": [...], "preferences": {...}}
```

### `save_user_preference(user_id: str, key: str, value: str) -> str`

**Description**: Saves a user preference to memory.

**Parameters**:
- `user_id` (str): Unique identifier for the user
- `key` (str): Preference key (e.g., "communication_style")
- `value` (str): Preference value

**Returns**:
- `str`: Confirmation message

**Example**:
```python
result = save_user_preference("user_123", "communication_style", "detailed")
# Returns: "Preference saved: communication_style = detailed"
```

### `update_milestone(user_id: str, milestone_data: str) -> str`

**Description**: Updates user milestones and achievements.

**Parameters**:
- `user_id` (str): Unique identifier for the user
- `milestone_data` (str): JSON string containing milestone information

**Returns**:
- `str`: Confirmation message

**Example**:
```python
milestone = '{"title": "Completed Python course", "date": "2025-03-15", "domain": "career"}'
result = update_milestone("user_123", milestone)
```

### `get_progress_history(user_id: str, timeframe: str = "all") -> str`

**Description**: Retrieves user's progress history.

**Parameters**:
- `user_id` (str): Unique identifier for the user
- `timeframe` (str, optional): Time period ("week", "month", "quarter", "all")

**Returns**:
- `str`: JSON string containing progress history

---

## Planning Tools

Located in: `src/tools/planning_tools.py`

### `write_todos(todos_data: str) -> str`

**Description**: Creates structured todo lists with phases and dependencies.

**Parameters**:
- `todos_data` (str): JSON string containing todo items

**Expected Format**:
```json
[
    {
        "title": "Complete assessment",
        "phase": "discovery",
        "priority": 1,
        "depends_on": [],
        "domain": "career"
    }
]
```

**Returns**:
- `str`: Confirmation with todo summary

### `update_todo(todo_id: str, updates: str) -> str`

**Description**: Updates todo status or adds notes.

**Parameters**:
- `todo_id` (str): Unique identifier for the todo item
- `updates` (str): JSON string with updates to apply

**Returns**:
- `str`: Updated todo information

### `list_todos(filter_params: str = "{}") -> str`

**Description**: Retrieves todos with optional filtering.

**Parameters**:
- `filter_params` (str): JSON string with filter criteria

**Filter Options**:
```json
{
    "phase": "discovery",
    "status": "pending", 
    "domain": "career",
    "priority": 1
}
```

**Returns**:
- `str`: JSON array of matching todos

---

## Context Tools

Located in: `src/tools/context_tools.py`

### `save_assessment(user_id: str, assessment_data: str) -> str`

**Description**: Saves assessment results to filesystem.

**Parameters**:
- `user_id` (str): Unique identifier for the user
- `assessment_data` (str): JSON string containing assessment results

**Returns**:
- `str`: File path where assessment was saved

### `get_active_plan(user_id: str) -> str`

**Description**: Retrieves user's current active plans.

**Parameters**:
- `user_id` (str): Unique identifier for the user

**Returns**:
- `str`: JSON string containing active plan data

### `save_weekly_progress(user_id: str, week_data: str) -> str`

**Description**: Saves weekly progress data.

**Parameters**:
- `user_id` (str): Unique identifier for the user
- `week_data` (str): JSON string with weekly progress

**Returns**:
- `str`: File path where progress was saved

### `list_user_assessments(user_id: str) -> str`

**Description**: Lists all assessments for a user.

**Parameters**:
- `user_id` (str): Unique identifier for the user

**Returns**:
- `str`: JSON array of assessment file paths and metadata

---

## Assessment Tools

Located in: `src/tools/assessment_tools.py`

### `conduct_initial_assessment(user_id: str, domain_focus: str = "all") -> str`

**Description**: Conducts comprehensive initial assessment across domains.

**Parameters**:
- `user_id` (str): Unique identifier for the user
- `domain_focus` (str): Focus area ("career", "relationship", "finance", "wellness", "all")

**Returns**:
- `str`: Assessment results with domain scores and recommendations

### `prioritize_domains_by_urgency(user_id: str, user_context: str) -> str`

**Description**: Analyzes and prioritizes domains based on urgency and impact.

**Parameters**:
- `user_id` (str): Unique identifier for the user
- `user_context` (str): Context about current situation and goals

**Returns**:
- `str`: Prioritized domain list with urgency scores

### `assess_cross_domain_impacts(user_id: str, action: str, domains: str) -> str`

**Description**: Assesses impact of an action across multiple domains.

**Parameters**:
- `user_id` (str): Unique identifier for the user
- `action` (str): Action being considered
- `domains` (str): JSON array of domains to analyze

**Returns**:
- `str`: Cross-domain impact analysis

---

## Career Tools

Located in: `src/tools/career_tools.py`

### `analyze_skill_gap(current_skills: str, target_role: str) -> str`

**Description**: Compares current skills to target role requirements.

**Parameters**:
- `current_skills` (str): JSON array of current skills
- `target_role` (str): Target job role or position

**Returns**:
- `str`: Skill gap analysis with missing skills and recommendations

### `create_career_path_plan(user_id: str, current_role: str, target_role: str, timeframe: str) -> str`

**Description**: Generates structured career progression plan.

**Parameters**:
- `user_id` (str): Unique identifier for the user
- `current_role` (str): Current job role
- `target_role` (str): Desired target role
- `timeframe` (str): Timeline for career transition (e.g., "6 months", "2 years")

**Returns**:
- `str`: Career path plan with milestones and action steps

### `optimize_resume(resume_text: str, job_description: str) -> str`

**Description**: Provides actionable resume improvement recommendations.

**Parameters**:
- `resume_text` (str): Current resume text
- `job_description` (str): Target job description

**Returns**:
- `str`: Specific recommendations for resume improvements

### `research_salary_benchmarks(role: str, location: str, experience_level: str) -> str`

**Description**: Provides salary range information and negotiation tips.

**Parameters**:
- `role` (str): Job role or position
- `location` (str): Geographic location
- `experience_level` (str): Years of experience or level

**Returns**:
- `str`: Salary data with ranges and negotiation guidance

---

## Relationship Tools

Located in: `src/tools/relationship_tools.py`

### `analyze_communication_style(user_id: str, interaction_examples: str) -> str`

**Description**: Analyzes communication patterns and styles.

**Parameters**:
- `user_id` (str): Unique identifier for the user
- `interaction_examples` (str): Examples of recent interactions

**Returns**:
- `str`: Communication style analysis with improvement suggestions

### `create_boundary_setting_plan(user_id: str, situation: str) -> str`

**Description**: Creates personalized boundary setting strategies.

**Parameters**:
- `user_id` (str): Unique identifier for the user
- `situation` (str): Specific situation requiring boundaries

**Returns**:
- `str`: Boundary setting plan with specific phrases and strategies

### `assess_relationship_quality(user_id: str, relationship_type: str, context: str) -> str`

**Description**: Evaluates relationship health and quality.

**Parameters**:
- `user_id` (str): Unique identifier for the user
- `relationship_type` (str): Type of relationship (e.g., "romantic", "professional", "family")
- `context` (str): Context about the relationship

**Returns**:
- `str`: Relationship quality assessment with scores and recommendations

---

## Finance Tools

Located in: `src/tools/finance_tools.py`

### `create_budget_analyzer(user_id: str, income_data: str, expense_data: str) -> str`

**Description**: Analyzes budget and provides optimization recommendations.

**Parameters**:
- `user_id` (str): Unique identifier for the user
- `income_data` (str): JSON string with income sources and amounts
- `expense_data` (str): JSON string with expense categories and amounts

**Returns**:
- `str`: Budget analysis with optimization suggestions

### `generate_debt_payoff_plan(user_id: str, debt_data: str) -> str`

**Description**: Creates optimized debt payoff strategy.

**Parameters**:
- `user_id` (str): Unique identifier for the user
- `debt_data` (str): JSON array of debts with amounts and interest rates

**Returns**:
- `str`: Debt payoff plan with timeline and strategy recommendations

### `calculate_emergency_fund_target(user_id: str, monthly_expenses: str) -> str`

**Description**: Calculates recommended emergency fund amount.

**Parameters**:
- `user_id` (str): Unique identifier for the user
- `monthly_expenses` (str): Monthly essential expenses amount

**Returns**:
- `str`: Emergency fund target with savings timeline

---

## Wellness Tools

Located in: `src/tools/wellness_tools.py`

### `assess_wellness_dimensions(user_id: str) -> str`

**Description**: Comprehensive wellness assessment across 8 dimensions.

**Parameters**:
- `user_id` (str): Unique identifier for the user

**Wellness Dimensions**:
- Physical health
- Mental health
- Social connections
- Emotional wellbeing
- Intellectual growth
- Spiritual health
- Environmental quality
- Financial wellness

**Returns**:
- `str`: Wellness assessment with scores and improvement areas

### `create_habit_formation_plan(user_id: str, habit_description: str) -> str`

**Description**: Creates habit formation plan based on behavioral science.

**Parameters**:
- `user_id` (str): Unique identifier for the user
- `habit_description` (str): Description of habit to form

**Returns**:
- `str`: Habit formation plan with triggers and rewards

### `provide_stress_management_techniques(stress_level: str, stressors: str) -> str`

**Description**: Provides personalized stress management strategies.

**Parameters**:
- `stress_level` (str): Current stress level (1-10 scale)
- `stressors` (str): Description of main stressors

**Returns**:
- `str`: Stress management techniques and coping strategies

---

## Cross-Domain Tools

Located in: `src/tools/cross_domain_tools.py`

### `build_goal_dependency_graph(goals_data: str) -> str`

**Description**: Maps goal relationships and dependencies.

**Parameters**:
- `goals_data` (str): JSON array of goals with metadata

**Returns**:
- `str`: Visual dependency graph and analysis

### `analyze_cross_domain_impacts(user_id: str, action: str, domains: str) -> str`

**Description**: Analyzes ripple effects across life domains.

**Parameters**:
- `user_id` (str): Unique identifier for the user
- `action` (str): Action being considered
- `domains` (str): JSON array of domains to analyze

**Returns**:
- `str`: Cross-domain impact analysis

### `detect_goal_conflicts(user_id: str, goals: str) -> str`

**Description**: Identifies conflicting goals and resource competition.

**Parameters**:
- `user_id` (str): Unique identifier for the user
- `goals` (str): JSON array of current goals

**Returns**:
- `str`: Conflict analysis with resolution strategies

---

## Communication Tools

Located in: `src/tools/communication_tools.py`

### `format_specialist_message(specialist_name: str, analysis_result: str) -> str`

**Description**: Formats specialist output for coordinator integration.

**Parameters**:
- `specialist_name` (str): Name of the specialist
- `analysis_result` (str): Raw specialist analysis

**Returns**:
- `str`: Formatted message for coordinator

### `aggregate_results(specialist_outputs: str) -> str`

**Description**: Combines multiple specialist outputs.

**Parameters**:
- `specialist_outputs` (str): JSON array of specialist outputs

**Returns**:
- `str`: Aggregated results with synergies identified

### `resolve_conflicts(conflicts_data: str, strategy: str) -> str`

**Description**: Resolves conflicts between specialist recommendations.

**Parameters**:
- `conflicts_data` (str): JSON array of conflicts
- `strategy` (str): Resolution strategy ("priority_based", "consensus_based", "hybrid")

**Returns**:
- `str`: Conflict resolution outcomes

---

## Emergency Tools

Located in: `src/tools/emergency_tools.py`

### `analyze_crisis_risk(user_message: str) -> str`

**Description**: Analyzes message for crisis indicators.

**Parameters**:
- `user_message` (str): User's message to analyze

**Returns**:
- `str`: Crisis level (critical, high, moderate, low/none) and type

### `get_immediate_resources(crisis_types: str) -> str`

**Description**: Provides crisis resources based on type.

**Parameters**:
- `crisis_types` (str): JSON array of crisis types detected

**Returns**:
- `str`: List of immediate resources and hotlines

### `create_safety_plan(user_id: str, plan_data: str) -> str`

**Description**: Creates personalized safety plan.

**Parameters**:
- `user_id` (str): Unique identifier for the user
- `plan_data` (str): Safety plan components

**Returns**:
- `str`: Created safety plan reference

---

## User Management Tools

Located in: `src/tools/user_tools.py`

### `create_user(username: str, password: str, name: str) -> str`

**Description**: Creates new user account with data isolation.

**Parameters**:
- `username` (str): Unique username
- `password` (str): User password
- `name` (str): Display name

**Returns**:
- `str`: User ID and confirmation

### `authenticate_user(user_id: str, password: str) -> str`

**Description**: Authenticates user and creates session.

**Parameters**:
- `user_id` (str): User identifier
- `password` (str): User password

**Returns**:
- `str`: Session token and authentication confirmation

### `get_current_user() -> str`

**Description**: Retrieves current active user information.

**Returns**:
- `str`: Current user details and session status

---

## Helper Functions

### Error Handling

All tools follow this error handling pattern:

```python
try:
    # Tool logic
    return "Success message"
except Exception as e:
    return f"Error: {str(e)}"
```

### Input Validation

Tools validate inputs and provide helpful error messages:

```python
if not user_id or not isinstance(user_id, str):
    return "Error: user_id must be a non-empty string"
```

### Response Format

Tools return user-friendly messages with:
- Success confirmations
- Clear error descriptions  
- Structured data (JSON when appropriate)
- Actionable next steps

---

## Integration Examples

### Multi-Domain Coaching Session

```python
# Initialize coach
coach = create_life_coach()

# Complex multi-domain request
result = coach.invoke({
    "messages": [{
        "role": "user",
        "content": "I want to change careers but I'm worried about finances and relationships"
    }]
})

# System will:
# 1. Analyze request (coordinator)
# 2. Delegate to career, finance, and relationship specialists
# 3. Analyze cross-domain impacts
# 4. Generate integrated plan with conflict resolution
```

### Progress Tracking Session

```python
# Weekly check-in
result = coach.invoke({
    "messages": [{
        "role": "user", 
        "content": "Weekly check-in: I completed 3 career tasks but missed my wellness goals due to work stress"
    }]
})

# System will:
# 1. Update progress tracking
# 2. Analyze patterns and correlations
# 3. Generate adaptation recommendations
# 4. Update todo priorities based on performance
```

---

## API Versioning

Current API version: **1.0.0**

Version history:
- 1.0.0: Initial release with full multi-agent functionality

Backward compatibility is maintained for minor version updates. Breaking changes will increment major version number.

---

## Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| AUTH_001 | Invalid user credentials | Check user_id and password |
| MEMORY_001 | Store access failed | Check store initialization |
| TOOL_001 | Tool not found | Verify tool import and registration |
| FILE_001 | Filesystem access error | Check workspace permissions |
| AGENT_001 | Subagent not responding | Check subagent configuration |

---

## Performance Metrics

The API is designed to meet these performance targets:

- **Simple queries**: < 30 seconds response time
- **Single specialist delegation**: < 60 seconds
- **Multi-domain coordination**: < 120 seconds
- **Parallel specialist execution**: 2-4x speedup vs sequential

---

## Rate Limiting

No built-in rate limiting for local deployments. Production deployments should implement:

- Per-user request limits
- Tool call frequency limits  
- Memory access throttling
- Filesystem I/O limits

---

## Authentication

Current implementation uses basic session-based authentication. Future versions will support:

- OAuth 2.0 integration
- API key authentication
- Multi-factor authentication
- Session timeout management

---

For complete usage examples and integration patterns, see the [Developer Guide](DEVELOPER.md).