# Tool Allocation Strategy

## Overview

This document defines the tool allocation strategy for the AI Life Coach system, specifying which tools are available to each component (coordinator and specialists) and the rationale behind these decisions.

Based on Deep Agents subagent spawning best practices:
https://docs.langchain.com/oss/python/deepagents/subagents

---

## Tool Categories

### 1. Planning Tools
- `write_todos`: Create or replace a complete todo list with phases and dependencies
- `update_todo`: Update individual todo items (status, notes) while tracking dependencies
- `list_todos`: Display todos with phase filtering and dependency status

### 2. Memory Tools
- `get_user_profile`: Retrieve a user's profile for context
- `save_user_preference`: Save user preferences for future sessions
- `update_milestone`: Track achievements and milestones as users progress
- `get_progress_history`: Review a user's progress over time

### 3. Context Tools
- `save_assessment`: Save user assessments as JSON files with timestamps
- `get_active_plan`: Retrieve a user's current active plan from the plans directory
- `save_weekly_progress`: Save weekly progress summaries as JSON files
- `list_user_assessments`: List all assessments for a user with key metrics
- `read_assessment`: Read a specific assessment by date
- `save_curated_resource`: Save curated resources (articles, guides) for reference

---

## Tool Allocation Matrix

| Component | Planning Tools | Memory Tools | Context Tools |
|-----------|---------------|--------------|---------------|
| **Coordinator** | ✅ All three | ✅ All four | ✅ All six |
| **Career Specialist** | ❌ None | ✅ All four | ✅ All six |
| **Relationship Specialist** | ❌ None | ✅ All four | ✅ All six |
| **Finance Specialist** | ❌ None | ✅ All four | ✅ All six |
| **Wellness Specialist** | ❌ None | ✅ All four | ✅ All six |

---

## Detailed Tool Allocation by Component

### Coordinator (Full Access)

**Planning Tools: All**
- **Why**: The coordinator is responsible for:
  - Breaking down complex multi-step tasks
  - Creating phased action plans (discovery, planning, execution, review)
  - Managing dependencies between tasks
  - Tracking overall progress across all domains

**Memory Tools: All**
- **Why**: The coordinator needs to:
  - Understand full user context across all domains
  - Save communication preferences
  - Track milestones in any domain
  - Review progress history to inform decisions

**Context Tools: All**
- **Why**: The coordinator needs to:
  - Save comprehensive assessments
  - Retrieve active plans across domains
  - Store weekly progress summaries
  - Curate resources for users
  - Maintain complete picture of user's journey

### Career Specialist (No Planning, Memory + Context)

**Memory Tools: All**
- **Rationale**:
  - `get_user_profile`: Understand user's career background, current role, goals
  - `save_user_preference`: Remember communication style preferences (detailed vs. concise)
  - `update_milestone`: Track career achievements (new job, promotion, certification earned)
  - `get_progress_history`: Review past career progress to adapt advice

**Context Tools: All**
- **Rationale**:
  - `save_assessment`: Document detailed career assessments with SWOT analysis
  - `get_active_plan`: Retrieve existing career development plans for continuity
  - `save_weekly_progress`: Track weekly progress on career actions
  - `list_user_assessments`: Review past assessments to identify patterns
  - `read_assessment`: Access specific assessment details
  - `save_curated_resource`: Save job search resources, industry reports, learning materials

**No Planning Tools**
- **Rationale**: Planning is coordination work. The specialist focuses on domain-specific analysis and recommendations, while the coordinator creates and manages the overall task structure.

### Relationship Specialist (No Planning, Memory + Context)

**Memory Tools: All**
- **Rationale**:
  - `get_user_profile`: Understand relationship history, family background, social context
  - `save_user_preference`: Remember communication style (direct vs. gentle)
  - `update_milestone`: Track relationship improvements (resolved conflict, set boundary)
  - `get_progress_history`: Review relationship patterns and progress over time

**Context Tools: All**
- **Rationale**:
  - `save_assessment`: Document relationship assessments with dynamics and patterns
  - `get_active_plan`: Retrieve existing relationship improvement plans
  - `save_weekly_progress`: Track weekly progress on relationship goals
  - `list_user_assessments`: Review past assessments for pattern recognition
  - `read_assessment`: Access specific assessment details
  - `save_curated_resource`: Save communication exercises, relationship-building activities

**No Planning Tools**
- **Rationale**: The specialist provides expertise on relationships and communication. The coordinator handles the structuring of actions and workflows.

### Finance Specialist (No Planning, Memory + Context)

**Memory Tools: All**
- **Rationale**:
  - `get_user_profile`: Understand income level, family situation, financial constraints
  - `save_user_preference`: Remember budgeting style preferences (detailed vs. simple)
  - `update_milestone`: Track financial achievements (debt paid off, savings goal reached)
  - `get_progress_history`: Review financial progress over time

**Context Tools: All**
- **Rationale**:
  - `save_assessment`: Document financial health assessments with details
  - `get_active_plan`: Retrieve existing budget or financial plans
  - `save_weekly_progress`: Track weekly spending/saving progress
  - `list_user_assessments`: Review past financial assessments for trends
  - `read_assessment`: Access specific assessment details
  - `save_curated_resource`: Save budgeting templates, financial education resources

**No Planning Tools**
- **Rationale**: The specialist focuses on financial analysis and strategy. The coordinator manages the overall planning structure.

### Wellness Specialist (No Planning, Memory + Context)

**Memory Tools: All**
- **Rationale**:
  - `get_user_profile`: Understand health context, activities they enjoy, constraints
  - `save_user_preference`: Remember wellness preferences (types of exercise, etc.)
  - `update_milestone`: Track wellness achievements (consistency streaks, goals reached)
  - `get_progress_history`: Review wellness progress over time

**Context Tools: All**
- **Rationale**:
  - `save_assessment`: Document wellness assessments across multiple dimensions
  - `get_active_plan`: Retrieve existing exercise or habit plans
  - `save_weekly_progress`: Track weekly wellness metrics and habits
  - `list_user_assessments`: Review past assessments for patterns
  - `read_assessment**: Access specific assessment details
  - `save_curated_resource`: Save workout routines, meditation guides, wellness articles

**No Planning Tools**
- **Rationale**: The specialist provides expertise on health and wellbeing. The coordinator manages the planning structure.

---

## Rationale for Tool Allocation Strategy

### 1. Security Principle: Least Privilege
**Concept**: Each component has access only to tools it needs.

**Implementation**:
- Specialists do not have planning tools (coordination is coordinator's job)
- All components need memory and context tools for their domain
- No component has unnecessary tools that could lead to errors

**Benefits**:
- Reduces surface area for mistakes
- Prevents specialists from creating conflicting plans
- Maintains clear separation of concerns

### 2. Focus Principle: Minimal Tool Sets
**Concept**: Smaller tool sets lead to better focus and faster decisions.

**Implementation**:
- Specialists have 10 tools (4 memory + 6 context)
- Coordinator has 13 tools (3 planning + 4 memory + 6 context)

**Benefits**:
- Specialists can make decisions faster with fewer tool options
- Reduces context overhead for specialists
- Improves reliability by limiting complexity

### 3. Coordination Principle: Central Planning
**Concept**: The coordinator maintains the "big picture" through planning tools.

**Implementation**:
- Only the coordinator can create, update, and list todos
- Specialists provide recommendations but don't manage task structure
- Coordinator integrates specialist outputs into cohesive plans

**Benefits**:
- Single source of truth for task planning
- Prevents conflicting action plans across domains
- Enables cross-domain dependency management

### 4. Context Principle: Shared Memory and Storage
**Concept**: All components access the same memory and context systems.

**Implementation**:
- All specialists can use same memory tools for user context
- All specialists save to the same filesystem structure
- Coordinator can access all specialist-saved content

**Benefits**:
- Consistent understanding of user across components
- Persistent storage for specialist outputs
- Cross-domain visibility into progress

---

## Tool Usage Patterns

### Pattern 1: Specialist Workflow
```
1. Retrieve Context (Memory Tools)
   └─ get_user_profile() → understand user's background
   └─ get_progress_history() → see past progress

2. Perform Analysis (Internal + Domain Knowledge)
   └─ Specialist uses domain expertise to analyze situation

3. Save Results (Context Tools)
   └─ save_assessment() → document detailed assessment
   └─ save_curated_resource() → save relevant resources

4. Return Summary to Coordinator
   └─ Concise summary (<500-1000 words)
   └─ Key recommendations with priorities
   └─ References to saved files

5. Track Progress (Memory Tools)
   └─ update_milestone() → if user achieves goal
```

### Pattern 2: Coordinator Workflow
```
1. Retrieve Context (Memory Tools)
   └─ get_user_profile() → full user context

2. Plan Tasks (Planning Tools)
   └─ write_todos() → create initial plan
   └─ update_todo() → mark progress

3. Delegate to Specialist (if needed)
   └─ Provide context and specific request
   └─ Receive summary and saved file references

4. Integrate Results (Planning + Context Tools)
   └─ update_todo() → adjust plan based on results
   └─ save_weekly_progress() → track overall progress

5. Communicate with User
   └─ Present integrated guidance
   └─ Celebrate wins (update_milestone)
```

---

## Tool Interaction Examples

### Example 1: Career Specialist Working
```python
# Specialist retrieves user's career background
profile = get_user_profile(user_id="user_alex")

# Based on profile and domain knowledge, specialist analyzes:
# - Current role: Marketing Manager
# - Goals: Transition to Data Science
# - Skills: Python (beginner), SQL (none)

# Specialist saves detailed assessment
save_assessment(
    user_id="user_alex",
    assessment_data={
        "domain": "career",
        "skills_have": ["marketing", "analytics"],
        "skills_need": ["python", "sql", "ml"],
        "learning_path": [...]
    }
)

# Specialist returns concise summary to coordinator:
"""
Alex wants to transition from Marketing Manager to Data Science.
Key skill gaps: Python (beginner), SQL, Machine Learning fundamentals.

Recommended 6-month learning path:
1. Month 1-2: Python (DataCamp course)
2. Month 3: SQL (Codecademy)
3. Month 4-5: ML fundamentals (Coursera)
4. Month 6: Portfolio projects

Full assessment saved to: assessments/user_alex/career_transition_plan.json
"""
```

### Example 2: Coordinator Integrating Specialist Work
```python
# Coordinator receives specialist summary

# Updates todo list to include learning plan
update_todo(
    task_id="python_learning",
    status="in_progress",
    notes="Based on career specialist recommendation"
)

# Tracks milestone when user completes course
update_milestone(
    user_id="user_alex",
    milestone={
        "domain": "career",
        "title": "Completed Python for Data Science",
        "date": "2025-02-15"
    }
)

# Saves weekly progress
save_weekly_progress(
    user_id="user_alex",
    week_data={
        "week": 3,
        "career_progress": "Completed Python module",
        "completion_rate": 0.85
    }
)
```

---

## Security and Safety Considerations

### 1. Tool Access Control
- Only coordinator can create/modify plans (prevents conflicting specialist plans)
- Specialists cannot delete or modify files created by other specialists
- All tool calls are logged for auditability

### 2. Data Privacy
- Memory tools use user-scoped namespaces (no cross-user data access)
- Context tools save to user-specific directories
- No specialist can access another user's data

### 3. Error Prevention
- Planning tools validate dependencies (prevent circular or impossible plans)
- Context tools validate file paths and permissions
- Memory tools handle missing data gracefully

---

## Future Enhancements

### 1. Dynamic Tool Allocation
Currently, specialists have fixed tool sets. Future versions could:
- Add tools dynamically based on task complexity
- Remove unused tools to optimize context
- Allow specialists to request additional tools with justification

### 2. Tool-Level Permissions
Currently, all tools are read/write enabled. Future versions could:
- Make some tools read-only for specialists
- Implement approval workflows for sensitive operations (e.g., milestone tracking)

### 3. Tool Usage Analytics
Monitoring how tools are used can inform:
- Which tools are most/least effective
- Where specialists might need more capabilities
- Opportunities to streamline workflows

---

## Summary

The tool allocation strategy is designed to:

1. **Maintain Clear Separation of Concerns**: Coordinator plans, specialists analyze
2. **Optimize for Focus and Efficiency**: Minimal tool sets reduce decision overhead
3. **Enable Cross-Domain Coordination**: Shared memory and context provide visibility
4. **Ensure Security and Reliability**: Least privilege, clear error boundaries

By carefully allocating tools based on component responsibilities, the system achieves both specialization and integration while maintaining security and performance.