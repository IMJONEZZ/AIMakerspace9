# Architecture Quick Reference

## System Overview
The AI Life Coach is a **Deep Agent** system that orchestrates 4 domain specialists through a central coordinator, using planning, context management, and persistent memory to provide comprehensive life guidance.

---

## Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE                           │
│                  (CLI or Web Interface)                      │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              LIFE COACH COORDINATOR                         │
│          (Main Agent - Claude Model)                        │
├─────────────────────────────────────────────────────────────┤
│  Responsibilities:                                           │
│  • Multi-domain assessment & prioritization                 │
│  • Phase-based planning (discovery → execution)            │
│  • Subagent coordination & delegation                      │
│  • Cross-domain insight synthesis                           │
├─────────────────────────────────────────────────────────────┤
│  Tools Available:                                            │
│  • write_todos, update_todo, list_todos                    │
│  • get_user_profile, save_user_preference                   │
│  • save_assessment, get_active_plan                         │
│  • generate_weekly_report                                   │
└───────┬─────────┬───────────────┬─────────────┬──────────────┘
        │         │               │             │
        ▼         ▼               ▼             ▼
┌───────────┐ ┌──────────────┐ ┌──────────┐ ┌──────────────┐
│   CAREER  │ │ RELATIONSHIP │ │ FINANCE  │ │  WELLNESS    │
│  SPECIAL- │ │   SPECIALIST  │ │SPECIAL-  │ │  SPECIALIST  │
│    IST    │ └──────────────┘ │   IST    │ └──────────────┘
└───────────┘                  └──────────┘
    │                              │             │
    ◄─────── SPECIALIST TOOLS ───────────────────┘

                ▼
┌─────────────────────────────────────┐
│        INTEGRATED PLAN              │
│  • Unified recommendations          │
│  • Cross-domain connections         │
│  • Prioritized action items         │
└─────────────────────────────────────┘
```

---

## Memory Architecture

### Namespace Hierarchy
```
LangGraph Store (InMemoryStore)
│
├── (user_id, "profile") 
│   ├── demographics → {name: "Alex", age: 35}
│   ├── values → ["growth", "balance", "autonomy"]
│   └── life_situation → {work: "employed", family: "single"}
│
├── (user_id, "goals")
│   ├── short_term → [{title: "Learn Python", deadline: "2025-04"}]
│   ├── medium_term → [{title: "Get promotion", deadline: "2025-12"}]
│   └── long_term → [{title: "Buy house", deadline: "2028"}]
│
├── (user_id, "progress")
│   ├── milestones → [{title: "Completed Python course", date: "2025-03"}]
│   └── setbacks → [{description: "Missed study sessions", resolved: true}]
│
├── (user_id, "preferences")
│   ├── communication_style → "detailed"
│   └── coaching_approach → "encouraging"
│
└── ("coaching", "patterns")  # Cross-user, anonymized
    ├── effective_strategies → [...]
    └── common_challenges → [...]
```

### Memory Operations
```python
# Write to memory
store.put((user_id, "profile"), "demographics", {"name": "Alex"})

# Read from memory
items = list(store.search((user_id, "profile")))

# Semantic search (if vector store is added)
items = list(store.search(("coaching", "patterns"), query="procrastination"))
```

---

## Filesystem Context Structure

```
workspace/
│
├── user_profile/{user_id}/
│   ├── profile.json          # Complete user profile data
│   └── preferences.json      # User communication/style preferences
│
├── assessments/{user_id}/
│   ├── 2025-02-04_initial.json     # Initial comprehensive assessment
│   └── 2025-03-01_quarterly.json   # Quarterly reassessment
│
├── plans/{user_id}/
│   ├── career_growth_90day.md      # Career domain plan
│   ├── relationship_goals.md       # Relationship domain plan
│   ├── financial_plan_2025.md      # Financial planning document
│   └── wellness_routine.md         # Wellness action plan
│
├── progress/{user_id}/
│   ├── week_01_summary.json        # Weekly progress tracking
│   ├── week_02_summary.json
│   └── ...
├── resources/
│   ├── articles/                   # Curated articles by domain
│   │   ├── career/pod2025_job_market.md
│   │   └── wellness/stress_management_101.md
│   ├── exercises/                  # Practical worksheets and tools
│   │   └── budget_template.json
│   └── reflection_prompts/         # Personalized prompts library
```

---

## Planning System

### Todo List Structure
```python
todos = [
    {
        "id": "assessment",
        "title": "Initial life assessment",
        "phase": "discovery",
        "status": "completed",
        "depends_on": []
    },
    {
        "id": "priorities",
        "title": "Identify top 3 priorities",
        "phase": "discovery",
        "status": "in_progress",
        "depends_on": ["assessment"]
    },
    {
        "id": "action_plan",
        "title": "Create 90-day action plan",
        "phase": "planning",
        "status": "pending",
        "depends_on": ["priorities"]
    },
    {
        "id": "checkins",
        "title": "Weekly check-in system",
        "phase": "execution",
        "status": "pending",
        "depends_on": ["action_plan"]
    }
]
```

### Phase Transitions
```
Discovery (Assessment & Understanding)
         │
         ▼ (when assessment complete and priorities identified)
    Planning (Create Action Plans)
         │
         ▼ (when 90-day plan created and approved)
   Execution (Implement & Track)
         │
         ▼ (weekly, after check-in completes)
     Review (Evaluate & Adapt)
         │
         ▼ (adaptations made if needed)
   [Back to Execution or Planning]
```

---

## Subagent Configuration Template

```python
specialist_config = {
    "name": "domain-specialist",           # Unique identifier
    "description": "...",                  # When to use this specialist
    "system_prompt": """
# Domain Specialist

## Your Role
Expert in [domain] with deep knowledge of...

## Core Competencies
- ...

## Workflow
1. Analyze the user's [domain] situation
2. Identify key challenges and opportunities
3. Generate specific, actionable recommendations
4. Provide resources for implementation

## Important
- Always consider cross-domain impacts
- Note any synergies or conflicts with other life areas
- Provide concrete next steps, not just general advice
""",
    "tools": [
        # Domain-specific tools only
    ],
    "model": "openai:glm-4.7"               # Model to use
}
```

---

## Specialist Capabilities Matrix

| Capability | Career | Relationship | Finance | Wellness |
|------------|--------|--------------|---------|----------|
| Assessment | ✓ Skill gaps, career fit | ✓ Communication style, relationship quality | ✓ Financial health, spending patterns | ✓ 8-dimension wellness score |
| Planning | ✓ Career path mapping | ✓ Social skills development | ✓ Budget creation, goal setting | ✓ Habit formation plans |
| Tools | Market research, resume optimization | Boundary frameworks, conflict resolution | Budget calculators, debt payoff strategies | Habit trackers, stress techniques |
| Metrics | Interview success rate, skill progress | Relationship satisfaction score | Savings rate, debt reduction | Wellness score, habit streaks |
| Resources | Industry reports, courses | Communication exercises | Budget templates, investment guides | Exercise plans, meditation guides |

---

## Goal Dependency System

### Data Model
```python
class Goal:
    id: str
    title: str
    domain: str  # career, relationship, finance, wellness
    priority: int  # 1-5 (5 = highest)
    status: str  # pending, in_progress, completed
    deadline: Optional[date]
    dependencies: List[str]  # IDs of prerequisite goals
    enables: List[Dependency]  # Goals this enables
    conflicts_with: List[str]  # IDs of conflicting goals

class Dependency:
    type: str  # "enables", "requires", "conflicts", "supports"
    target_goal_id: str
    strength: float  # 0.0-1.0 importance weight
```

### Dependency Types
| Type | Description | Example |
|------|-------------|---------|
| **Enables** | Goal A makes Goal B possible/easier | "Get promotion" → "Buy house" |
| **Requires** | Goal A needs Goal B to succeed | "Run marathon" → requires "6 months training" |
| **Conflicts** | Goals compete for resources | "Work 60h/week" ↔ "Spend quality family time" |
| **Supports** | Goal A helps but doesn't require Goal B | "Exercise regularly" → supports "Better sleep" |

### Dependency Graph (Text Visualization)
```
Career: Get Promotion ─────┐
                           │
                           │ enables (strength: 0.8)
                           ▼
Finance: Save $50k for House
                           │
                           │ requires (strength: 1.0)
                           ▼
Wellness: Reduce Work Stress ┐
                            │ conflicts (strength: 0.7) with
                            ▼
Relationship: Spend Quality Time with Family

Critical Path: Career → Finance → Wellness (must resolve conflict)
```

---

## Workflow Examples

### Example 1: Single-Domain Request
```
User: "I want to transition from marketing to data science"

Coordinator Analysis:
- Domain identified: Career
- No cross-domain implications detected
- Delegating to career specialist

Career Specialist:
- Assesses current skills and gaps
- Recommends learning path (Python, SQL, ML)
- Creates 6-month transition timeline
- Provides portfolio and resume strategies

Output: Personalized career transition plan with milestones
```

### Example 2: Multi-Domain Request
```
User: "I feel stuck in my career and it's affecting my relationships"

Coordinator Analysis:
- Domains identified: Career + Relationship
- Cross-domain connection detected (work stress → relationship quality)
- Parallel delegation to both specialists

Career Specialist:
- Identifies career stagnation causes
- Recommends advancement or pivot strategies

Relationship Specialist:
- Analyzes relationship impact patterns
- Provides communication tools for discussing work stress

Integration:
- Highlights how career improvements will benefit relationships
- Creates balanced action plan addressing both domains
- Identifies potential conflicts (e.g., taking on extra work for promotion)

Output: Integrated plan with cross-domain considerations
```

### Example 3: Complex Cross-Domain Scenario
```
User: "I want to move to a new city for better job opportunities,
       but I'm worried about my partner and the financial cost"

Coordinator Analysis:
- Domains: Career + Relationship + Finance
- Complex interdependencies detected
- Requires all 3 specialists

Career Specialist:
- Researches target city job market
- Evaluates career advancement potential

Relationship Specialist:
- Assesses relationship readiness for relocation
- Provides long-distance transition strategies if needed

Finance Specialist:
- Calculates moving costs and cost-of-living differences
- Creates savings plan for relocation

Integration:
- Goal dependency graph created
- Conflict analysis: Career growth vs. Relationship strain
- Phased plan recommended (secure finances → job secured → move)

Output: Comprehensive relocation plan with risk mitigation
```

---

## Weekly Check-In Flow

```
1. User provides check-in data:
   - Completed tasks (by domain)
   - Skipped tasks and reasons
   - Mood/energy levels (1-10 scale)
   - Obstacles encountered
   - Wins to celebrate

2. System processes:
   ┌─────────────┐    ┌──────────────┐    ┌─────────────┐
   │ Update goals│ -> │ Trend analysis│ -> │ Calculate  │
   │ progress    │    │ (mood, comple-│    │ scores      │
   │             │    │  tion rates) │    │             │
   └─────────────┘    └──────────────┘    └─────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ Detect patterns  │
                    │ • Streaks        │
                    │ • Drop-offs      │
                    │ • Correlations   │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ Generate adapta- │
                    │ tations (if      │
                    │ needed)          │
                    └──────────────────┘

3. Output:
   - Weekly summary report
   - Progress scores by domain
   - Mood trend visualization
   - Adaptation recommendations (if any)
   - Celebrated wins highlighted
```

---

## Emergency Support Flow

```
User Input: "I'm feeling completely overwhelmed and hopeless"
            [or keywords: suicide, self-harm, crisis]

Coordinator Detection:
- Emergency keyword detected
- Activate crisis protocol (immediate priority override)

System Response:
1. Immediate empathetic acknowledgment
2. Provide crisis resources (hotlines, immediate support)
3. Gently assess safety level
4. Encourage professional help
5. Offer to create safety plan (if appropriate)
6. Follow-up check-in scheduled

Resources Provided:
- National Suicide Prevention Lifeline: 988
- Crisis Text Line: HOME to 741741
- Local emergency services information
- Mental health professional directory

Safety Plan Template Generated:
- Warning signs to watch for
- Coping strategies that work
- People/places for distraction
- Reason for living (documented)
- Emergency contact list

Post-Crisis:
- Check-in scheduled within 24 hours
- Gentle return to regular coaching
- Monitor for continued support needs
```

---

## Key Design Decisions

### Why Deep Agents?
- **Planning**: Complex life goals require structured planning across time horizons
- **Context Management**: Life coaching generates extensive context over weeks/months
- **Subagents**: Different life domains require specialized expertise
- **Memory**: Coaching relationships are long-term; memory must persist across sessions

### Why 4 Specialists?
- **Balanced Coverage**: Career, Relationships, Finance, Wellness represent major life domains
- **Manageable Complexity**: 4 specialists provide comprehensive coverage without overwhelming coordination complexity
- **Research-Based**: Based on holistic life satisfaction frameworks (e.g., 8 dimensions of wellness)

### Why Filesystem + Store?
- **Filesystem**: Ideal for structured documents (plans, assessments, reports)
- **Store**: Perfect for key-value data (preferences, progress metrics) and semantic search
- **Complementary**: Each serves different use cases; both needed for complete system

### Why Phase-Based Planning?
- **Mimics Human Behavior**: People naturally work in phases (understand → plan → act → review)
- **Reduces Overwhelm**: Breaking into phases makes large goals manageable
- **Enables Adaptation**: Review phase provides natural points for course correction

### Why Goal Dependencies?
- **Realistic**: Life goals are rarely independent
- **Prioritization Helper**: Understanding dependencies helps order actions effectively
- **Conflict Detection**: Identifies competing goals before they cause problems

---

## Performance Considerations

### Optimization Targets
- **Response Time**: < 30 seconds for simple queries, < 2 minutes for complex multi-domain requests
- **Parallelization**: Specialists work in parallel when possible (non-dependent tasks)
- **Caching**: Frequently accessed data cached to reduce memory calls
- **Context Management**: Offload large documents to filesystem, keep only summaries in agent context

### Bottleneck Prevention
- **Tool Calls**: Batch related operations; avoid redundant calls
- **Memory Access**: Use efficient namespace organization; minimize search scope
- **Subagent Coordination**: Limit back-and-forth between coordinator and specialists
- **File Operations**: Minimize I/O; aggregate writes where possible

---

## Extension Points

### Adding New Domains
1. Create new specialist configuration (following template)
2. Implement domain-specific tools
3. Add to coordinator's subagent list
4. Update assessment workflow if needed

### Adding New Tools
1. Implement tool function with proper type hints
2. Add descriptive docstring
3. Register with appropriate specialist(s)
4. Update documentation

### New Skill Definition
1. Create `skills/new-skill/SKILL.md` following format
2. Add skill loading tool if needed
3. Update coordinator's available skills list

### Custom Memory Backend
1. Implement `BaseStore` interface from LangGraph
2. Replace InMemoryStore in configuration
3. Test all memory operations

---

**Document Created**: Architecture Quick Reference
**Purpose**: Fast lookup for key architecture decisions and patterns