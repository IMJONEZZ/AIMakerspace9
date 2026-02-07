# Subagent Coordination Workflow

## Overview

This document describes how the AI Life Coach coordinator orchestrates work across four domain specialist subagents: Career, Relationship, Finance, and Wellness specialists.

Based on Deep Agents subagent spawning best practices:
https://docs.langchain.com/oss/python/deepagents/subagents

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  LIFE COACH COORDINATOR                     │
│         (Main Agent - Orchestrator & Integrator)            │
├─────────────────────────────────────────────────────────────┤
│  Responsibilities:                                           │
│  • Multi-domain assessment & prioritization                 │
│  • Task decomposition and planning                          │
│  • Subagent delegation decisions                            │
│  • Cross-domain insight synthesis                           │
│  • User communication and guidance                          │
└───────┬─────────┬───────────────┬─────────────┬──────────────┘
        │         │               │             │
        ▼         ▼               ▼             ▼
┌─────────────┐ ┌──────────────┐ ┌──────────┐ ┌──────────────┐
│   CAREER    │ │ RELATIONSHIP  │ │ FINANCE  │ │  WELLNESS    │
│ SPECIALIST  │ │   SPECIALIST  │ │SPECIAL-  │ │  SPECIALIST  │
│             │ └──────────────┘ │   IST    │ └──────────────┘
│ Tools:      │                 │          │
│ • Memory    │   Tools:        │ Tools:   │   Tools:
│ • Context   │   • Memory      │ • Memory │   • Memory
│             │   • Context     │ • Context│   • Context
└─────────────┘                 └──────────┘

Shared Tools (Coordinator Only):
• Planning tools: write_todos, update_todo, list_todos
• All memory + context tools
```

---

## Tool Allocation Strategy

### Coordinator Tools (Full Access)
The coordinator has access to ALL tools:
- **Planning Tools** (`write_todos`, `update_todo`, `list_todos`): For managing multi-step workflows
- **Memory Tools** (`get_user_profile`, `save_user_preference`, `update_milestone`, `get_progress_history`): For user context and tracking
- **Context Tools** (`save_assessment`, `get_active_plan`, `save_weekly_progress`, etc.): For persistent file storage

### Specialist Tools (Focused Access)
Each specialist has access to a focused subset:
- **Memory Tools**: For understanding user context and tracking progress in their domain
- **Context Tools**: For saving assessments, plans, and resources specific to their domain

**What specialists do NOT have:**
- Planning tools (coordinator handles all task planning and coordination)
- Tools from other domains (enforced by specialization)

### Rationale for Tool Allocation

1. **Security**: Limiting tool access reduces surface area for errors and misuse
2. **Focus**: Specialists work with tools directly relevant to their domain expertise
3. **Coordination**: The coordinator maintains the "big picture" via planning tools
4. **Efficiency**: Smaller tool sets mean faster decisions and better focus

---

## Delegation Decision Process

### When the Coordinator Should Delegate

The coordinator uses specialists for:

1. **Domain-Specific Deep Work**
   - Creating comprehensive career development plans
   - Analyzing relationship dynamics and patterns
   - Building detailed budgets and financial strategies
   - Designing personalized exercise or wellness routines

2. **Specialized Knowledge Requirements**
   - Resume/CV/LinkedIn optimization
   - Salary negotiation strategies
   - Investment concepts (educational)
   - Mental health self-care techniques

3. **In-Depth Analysis**
   - Skill gap analysis
   - Conflict resolution strategies
   - Debt payoff planning
   - Habit formation support

4. **When the User Explicitly Requests**
   - "I need help with my career"
   - "Please review my resume"
   - "Help me create a budget"

### When the Coordinator Should Handle Directly

The coordinator handles:

1. **Cross-Domain Issues**
   - Work-life balance (career + wellness)
   - Financial stress affecting relationships
   - Time management across multiple domains

2. **High-Level Planning**
   - Creating initial assessment frameworks
   - Setting overall priorities (not detailed plans)
   - Integrating specialist outputs into cohesive strategies

3. **Simple, Quick Guidance**
   - General life coaching advice
   - Motivational support and accountability
   - Quick questions that don't require deep expertise

4. **Coordination Tasks**
   - Managing todo lists and dependencies
   - Tracking overall progress across domains
   - Synthesizing insights from multiple specialists

---

## Coordination Workflows

### Workflow 1: Initial Assessment (Single Domain)

```
User Request: "I need help with my career"
       │
       ▼
1. Coordinator retrieves user profile (get_user_profile)
       │
       ▼
2. Quick assessment: Is this career-specific?
   Yes → Delegate to career-specialist
       │
       ▼
3. Career Specialist:
   • Conducts in-depth career assessment
   • Analyzes skills, goals, market context
   • Creates detailed development plan
   • Saves assessment to file (save_assessment)
       │
       ▼
4. Coordinator receives specialist output:
   • Summary of key findings
   • Actionable recommendations
   • Path to saved assessment file
       │
       ▼
5. Coordinator integrates and presents:
   • Executive summary to user
   • Next steps with priorities
   • File reference for full details
```

### Workflow 2: Multi-Domain Request

```
User Request: "I feel stuck in my career and it's affecting my relationships"
       │
       ▼
1. Coordinator retrieves user profile (get_user_profile)
       │
       ▼
2. Analysis: Multiple domains detected (career + relationship)
   AND cross-domain connection identified
       │
       ▼
3. Parallel delegation (if independent):
   ┌──────────────┐    ┌───────────────┐
   │Career Spec.  │    │Relationship   │
   │              │    │Spec.          │
   └──────────────┘    └───────────────┘
       │                     │
       ▼                     ▼
   • Career assessment     • Relationship dynamics
   • Stagnation analysis    • Impact patterns
       │                     │
       └──────────┬──────────┘
                  ▼
4. Coordinator integrates results:
   • Identifies connections (work stress → relationship quality)
   • Highlights synergies (career progress benefits relationships)
   • Notes potential conflicts
       │
       ▼
5. Creates integrated plan:
   • Use write_todos to create phased action plan
   • Balance actions across both domains
   • Set clear priorities and dependencies
       │
       ▼
6. Present cohesive plan to user with:
   • Cross-domain insights highlighted
   • Balanced approach that addresses both areas
   • Clear action steps with timeline
```

### Workflow 3: Complex Cross-Domain Scenario

```
User Request: "I want to move to a new city for better job opportunities,
              but I'm worried about my partner and the financial cost"
       │
       ▼
1. Coordinator retrieves user profile (get_user_profile)
       │
       ▼
2. Analysis: Three domains involved (career + relationship + finance)
   Complex interdependencies detected
       │
       ▼
3. Sequential delegation (due to dependencies):
   Phase 1: Research (parallel if possible)
   ┌──────────────┐    ┌───────────────┐
   │Career Spec.  │    │Finance Spec.  │
   │              │    │               │
   └──────────────┘    └───────────────┘
       │                     │
       ▼                     ▼
   • Job market research    • Cost analysis
   • Career advancement     • Budget impact
   • Salary potential       • Savings needs
       │                     │
       └──────────┬──────────┘
                  ▼
   Phase 2: Relationship assessment (needs research results)
              │
              ▼
       ┌───────────────┐
       │Relationship   │
       │Spec.          │
       └───────────────┘
              │
              ▼
       • Readiness assessment
       • Partnership strength
       • Transition strategies
              │
              ▼
4. Coordinator creates goal dependency graph:
   Career Goal → Relocation (enables)
                 │
                 ├── Financial Readiness (requires)
                 │
                 └── Relationship Agreement (supports/conflicts)

       Identify conflicts: Career growth vs. relationship strain
              │
              ▼
5. Create phased plan with write_todos:
   Phase 1: Financial Preparation (base dependency)
   Phase 2: Secure Job Offer
   Phase 3: Relationship Alignment & Decision
   Phase 4: Relocation Execution

       Each phase has clear success criteria and dependencies
              │
              ▼
6. Present comprehensive plan with:
   • Goal dependency visualization
   • Risk mitigation strategies
   • Decision checkpoints (go/no-go points)
```

### Workflow 4: Weekly Progress Check-In

```
User Check-In Data:
• Completed tasks (by domain)
• Skipped tasks and reasons
• Mood/energy levels
• Obstacles encountered
• Wins to celebrate
       │
       ▼
1. Coordinator updates todos (update_todo)
   • Mark completed tasks
   • Update status of in-progress items
   • Note skipped tasks with reasons
       │
       ▼
2. Save weekly progress (save_weekly_progress)
   • Store completion rates by domain
   • Capture mood/energy trends
   • Document obstacles and wins
       │
       ▼
3. Analyze patterns:
   • Are there consistent skips in a domain?
   • Is energy correlating with task completion?
   • Which domains need more support?
       │
       ▼
4. If pattern detected → delegate to relevant specialist:
   Career issues → career-specialist (adaptation)
   Relationship issues → relationship-specialist
   Finance issues → finance-specialist
   Wellness issues → wellness-specialist
       │
       ▼
5. Specialist provides:
   • Analysis of the pattern
   • Adaptation recommendations
   • Modified approach if needed
       │
       ▼
6. Coordinator integrates adjustments:
   • Update todo list with adaptations (update_todo)
   • Communicate changes to user
   • Celebrate wins and progress
```

---

## Cross-Domain Consultation Patterns

### Pattern 1: Domain Synergy Identification

When specialists work on related areas, the coordinator identifies synergies:

**Example**: Career Specialist recommends network events + Wellness Specialist suggests exercise
→ Coordinator can combine: "Join an industry sports league" (career networking + fitness)

### Pattern 2: Conflict Resolution

When specialists identify competing goals:

**Example**: Career Specialist suggests "work extra hours for promotion"
         Relationship Specialist notes "this conflicts with family time"

**Coordinator action**:
1. Identify the conflict clearly
2. Present options to user with trade-offs
3. Help prioritize based on values
4. Create balanced plan that respects both domains

### Pattern 3: Dependency Management

When one domain's progress enables another:

**Example**: Finance Specialist builds emergency fund
         → Enables Career Specialist to recommend career risk (job change)

**Coordinator action**:
1. Track dependencies in todo list
2. Communicate progress across domains
3. Celebrate when enabling goal achieved

---

## Communication Patterns Between Coordinator and Specialists

### From Coordinator to Specialist (Delegation)

When delegating, the coordinator provides:
1. **Context**: What is the user trying to achieve?
2. **User Profile Info**: Relevant background from memory
3. **Specific Request**: What exactly needs to be done?
4. **Constraints**: Time, energy, resource limitations
5. **Output Format**: What should the specialist return?

### From Specialist to Coordinator (Results)

Specialists return:
1. **Executive Summary**: Key findings (2-3 sentences)
2. **Analysis**: Detailed assessment of the situation
3. **Recommendations**: Actionable steps with priorities
4. **Resources**: Specific tools, articles, or frameworks
5. **Saved References**: Paths to files with detailed content

**Important**: Specialists keep responses concise (<500-1000 words) to maintain clean context.

---

## Context Handoff Best Practices

### 1. Minimal Required Information
When delegating, coordinator provides:
- User ID for profile retrieval
- Specific question or task
- Any relevant constraints

Specialists retrieve additional context themselves using memory tools.

### 2. Isolation and Clean Context
Each specialist:
- Works in isolated context (no pollution from other specialists)
- Saves detailed work to files using context tools
- Returns only summary to coordinator

### 3. Reference Preservation
When specialists save assessments or plans:
- Coordinator receives file path references
- Future conversations can reference saved work
- Maintains continuity across sessions

---

## Error Handling and Fallback Patterns

### Specialist Not Responding Appropriately

If specialist output is off-topic or unhelpful:
1. Coordinator attempts to reinterpret and provide context
2. If still not working, coordinator handles the task directly
3. Notes the issue for future improvement

### Specialist Not Available (Future Enhancement)

If specialist system is down:
1. Coordinator attempts to handle with general knowledge
2. Provides disclaimer about temporary limitation
3. Logs incident for system monitoring

### Cross-Domain Deadlock

If specialists have conflicting recommendations that can't be resolved:
1. Coordinator presents options to user with full context
2. Helps user make values-based decision
3. Proceeds based on user's choice

---

## Performance Optimization Strategies

### 1. Parallel Execution
When tasks are independent:
- Coordinator can delegate to multiple specialists simultaneously
- Wait for all results before integrating

### 2. Caching Specialist Results
If similar domain question asked repeatedly:
- Coordinator can reference previous specialist work
- Avoid redundant delegation when appropriate

### 3. Progressive Disclosure
Start with quick assessment:
1. Initial question → coordinator handles directly
2. If deeper dive needed → delegate to specialist

---

## Monitoring and Observability

### Key Metrics (Future Enhancement)

1. **Delegation Rate**: How often coordinator delegates vs. handles directly
2. **Specialist Usage Distribution**: Which specialists are used most/least
3. **Context Bloat Monitoring**: Are specialists keeping responses concise?
4. **User Satisfaction**: Which specialist outputs users find most helpful

### Logging Patterns

Each subagent call logs:
- Timestamp
- Which specialist was called
- Task/question delegated
- Response length (to monitor context bloat)
- User feedback (if available)

---

## Future Enhancements

### 1. Dynamic Tool Allocation
Currently, specialists have fixed tool sets. Future versions could:
- Add tools dynamically based on task requirements
- Remove unused tools to optimize context

### 2. Specialist-to-Specialist Communication
Currently, all communication goes through coordinator. Future versions could:
- Allow specialists to consult each other directly for cross-domain questions
- Implement specialist peer-review process

### 3. Adaptive Specialist Selection
Currently, coordinator delegates based on domain expertise. Future versions could:
- Track user preferences for certain specialists
- Learn which specialist handles specific topics best per user

### 4. Specialist Specialization Levels
Currently, each domain has one specialist. Future versions could:
- Create sub-specialists (e.g., career → interview-coach, resume-writer)
- Hierarchical specialist structure for deeper expertise

---

## Summary

The subagent coordination workflow is designed to:

1. **Balance Specialization and Integration**: Specialists provide deep domain expertise while coordinator maintains holistic view
2. **Maintain Clean Context**: Each specialist works in isolation, returning only summaries to prevent context bloat
3. **Enable Cross-Domain Insight**: Coordinator identifies connections, synergies, and conflicts across domains
4. **Scale to Complexity**: Can handle single-domain queries, multi-domain requests, and complex cross-domain scenarios
5. **Support Continuous Improvement**: Progress tracking, pattern detection, and adaptive recommendations

The key to success is clear delegation criteria, well-defined communication patterns, and thoughtful integration of specialist outputs into cohesive guidance for the user.