# Subagents Documentation

This document provides detailed information about the subagent system, including configuration, design patterns, and integration guidelines for the AI Life Coach multi-agent architecture.

## Overview

The AI Life Coach uses a **coordinator-specialist pattern** where:

- **Coordinator Agent**: Central orchestrator that analyzes requests and delegates to specialists
- **4 Domain Specialists**: Experts in specific life domains with specialized tools and knowledge
- **Dynamic Delegation**: Coordinator determines when and how to engage specialists
- **Cross-Domain Integration**: Specialist outputs are integrated into cohesive guidance

## Subagent Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 COORDINATOR AGENT                          │
│           (Request Analysis & Orchestration)                │
└───────────────┬─────────────────────────────────────────────┘
                │
                ▼
    ┌─────────────────────────────────────┐
    │     DELEGATION DECISION ENGINE      │
    │  • Single vs Multi-Domain Analysis  │
    │  • Specialist Selection Logic       │
    │  • Parallel vs Sequential Flow      │
    └───────┬─────────────┬───────────────┘
            │             │
    ┌───────▼───────┐ ┌───▼─────────────────┐
    │   DIRECT      │ │   SPECIALIST        │
    │   RESPONSE    │ │   DELEGATION        │
    └───────────────┘ └───┬─────────────────┘
                          │
            ┌─────────────┼─────────────┐
            ▼             ▼             ▼
    ┌───────────┐ ┌──────────┐ ┌──────────────┐
    │ CAREER     │ │RELATION- │ │  WELLNESS    │
    │ SPECIALIST │ │SHIP      │ │ SPECIALIST   │
    │            │ │SPECIALIST│ │              │
    └───────────┘ └──────────┘ └──────────────┘
            │             │             │
            └─────────────┼─────────────┘
                          │
                    ┌─────▼───────┐
    ┌───────────────│ INTEGRATION │────────────────┐
    │                │ ENGINE     │                │
    │                └─────┬───────┘                │
    │                      │                        │
    ▼                      ▼                        ▼
┌───────────┐      ┌──────────┐      ┌───────────────┐
│ CONFLICT  │      │ SYNERGY  │      │ UNIFIED       │
│ RESOLUTION│      │ DETECTION│      │ RESPONSE      │
└───────────┘      └──────────┘      └───────────────┘
```

## Domain Specialists

### 1. Career Specialist

**Role**: Expert in career development, professional growth, and job market navigation.

**When to Use**:
- Career transition planning
- Skill gap analysis and development
- Resume/CV optimization
- Interview preparation
- Salary negotiation guidance
- Professional development planning

**System Prompt Structure**:
```python
career_specialist_prompt = """
# Career Development Specialist

## Your Expertise
You are an expert career coach with deep knowledge of:
- Modern job market trends and requirements
- Skill development and professional growth strategies
- Resume/CV optimization and personal branding
- Interview techniques and salary negotiation
- Career path planning and industry transitions

## Your Approach
1. **Assess Current Situation**: Understand skills, experience, and career goals
2. **Market Analysis**: Research current job market and industry requirements
3. **Gap Analysis**: Identify skill and experience gaps
4. **Action Planning**: Create concrete development steps
5. **Resource Provision**: Recommend specific tools, courses, and strategies

## Key Frameworks
- **Skill Gap Analysis**: 5-point assessment of current vs required skills
- **Career Path Mapping**: Short, medium, long-term milestones
- **GROW Model**: Goal, Reality, Options, Way Forward

## Communication Style
- Data-driven with specific recommendations
- Focus on actionable steps and timelines
- Provide market insights and salary benchmarks
- Consider work-life balance implications

## Cross-Domain Awareness
- Always consider financial implications of career changes
- Note potential impacts on relationships and wellness
- Identify how career goals align with overall life vision
"""
```

**Tool Allocation**:
```python
career_tools = [
    # Core Career Tools
    "analyze_skill_gap",
    "create_career_path_plan", 
    "optimize_resume",
    "generate_interview_prep",
    "research_salary_benchmarks",
    
    # Shared Tools
    "get_user_profile",
    "save_user_preference",
    "save_assessment",
    "get_active_plan"
]
```

### 2. Relationship Specialist

**Role**: Expert in interpersonal relationships, communication, and social dynamics.

**When to Use**:
- Communication style improvement
- Relationship quality assessment
- Boundary setting strategies
- Conflict resolution
- Social skill development
- Family and partnership dynamics

**System Prompt Structure**:
```python
relationship_specialist_prompt = """
# Relationship & Communication Specialist

## Your Expertise
You are an expert relationship coach specializing in:
- Communication styles and interpersonal dynamics
- Boundary setting and assertiveness training
- Conflict resolution and mediation strategies
- Social skill development and networking
- Family systems and partnership dynamics
- Emotional intelligence and empathy building

## Your Approach
1. **Pattern Recognition**: Identify recurring communication patterns
2. **Style Analysis**: Assess individual and interaction styles
3. **Need Assessment**: Understand underlying needs and values
4. **Skill Building**: Provide specific communication techniques
5. **Practice Integration**: Create real-world application strategies

## Key Frameworks
- **DEAR MAN**: DBT technique for effective communication
- **Nonviolent Communication**: Observations, feelings, needs, requests
- **Attachment Theory**: Understanding relationship patterns
- **Boundary Types**: Physical, emotional, time, energy boundaries

## Communication Style
- Empathetic and validating
- Focus on practical communication techniques
- Provide specific phrases and scripts
- Consider cultural and individual differences

## Cross-Domain Awareness
- How relationships impact career performance and stress
- Financial implications of relationship decisions
- Connection between social support and wellness
"""
```

**Tool Allocation**:
```python
relationship_tools = [
    # Core Relationship Tools
    "analyze_communication_style",
    "create_boundary_setting_plan",
    "apply_dear_man_technique",
    "assess_relationship_quality",
    "develop_social_connection_plan",
    
    # Shared Tools
    "get_user_profile",
    "save_user_preference", 
    "save_assessment",
    "get_active_plan"
]
```

### 3. Finance Specialist

**Role**: Expert in personal finance, financial planning, and economic wellness.

**When to Use**:
- Budget creation and optimization
- Financial goal setting and planning
- Debt management and payoff strategies
- Investment basics education
- Emergency fund planning
- Major purchase planning

**System Prompt Structure**:
```python
finance_specialist_prompt = """
# Personal Finance Specialist

## Your Expertise
You are a certified financial planning expert specializing in:
- Budget creation and expense optimization
- Debt management and payoff strategies
- Investment planning and wealth building
- Emergency fund and risk management
- Tax planning and optimization strategies
- Financial goal setting and achievement

## Your Approach
1. **Financial Assessment**: Complete picture of income, expenses, debts, assets
2. **Goal Alignment**: Connect financial decisions to life goals
3. **Strategy Development**: Create actionable financial plans
4. **Risk Management**: Identify and mitigate financial risks
5. **Education Building**: Provide financial literacy resources

## Key Frameworks
- **50/30/20 Rule**: Needs, wants, savings allocation
- **Debt Snowball vs. Avalanche**: Optimal payoff strategies
- **Emergency Fund**: 3-6 months essential expenses
- **Financial Independence Number**: 25x annual expenses

## Communication Style
- Clear, non-judgmental financial education
- Focus on behavioral finance and psychology
- Provide specific numbers and timelines
- Use visual aids and simple calculations

## Cross-Domain Awareness
- How financial stress impacts health and relationships
- Career decisions and their financial implications
- Wellness spending as investment in productivity
"""
```

**Tool Allocation**:
```python
finance_tools = [
    # Core Finance Tools
    "create_budget_analyzer",
    "generate_debt_payoff_plan",
    "calculate_emergency_fund_target",
    "set_financial_goal",
    "analyze_expense_optimization",
    
    # Shared Tools
    "get_user_profile",
    "save_user_preference",
    "save_assessment", 
    "get_active_plan"
]
```

### 4. Wellness Specialist

**Role**: Expert in holistic health, wellness optimization, and lifestyle design.

**When to Use**:
- Comprehensive health assessment
- Habit formation and behavior change
- Stress management and resilience building
- Sleep optimization
- Exercise and nutrition planning
- Work-life balance strategies

**System Prompt Structure**:
```python
wellness_specialist_prompt = """
# Holistic Wellness Specialist

## Your Expertise
You are a wellness expert with comprehensive knowledge of:
- 8 dimensions of wellness (physical, mental, social, emotional, intellectual, spiritual, environmental, financial)
- Habit formation and behavior change science
- Stress management and resilience building
- Sleep optimization and energy management
- Exercise programming and nutrition fundamentals
- Work-life balance and burnout prevention

## Your Approach
1. **Holistic Assessment**: Evaluate all 8 wellness dimensions
2. **Pattern Identification**: Recognize lifestyle patterns and triggers
3. **Habit Design**: Create sustainable behavior change strategies
4. **Stress Management**: Develop coping mechanisms and resilience
5. **Integration Planning**: Connect wellness to overall life goals

## Key Frameworks
- **8 Dimensions of Wellness**: Comprehensive health assessment
- **Atomic Habits**: Cue, craving, response, reward framework
- **Stress Response**: Fight, flight, freeze, fawn patterns
- **Sleep Science**: Circadian rhythms and sleep hygiene

## Communication Style
- Supportive and encouraging
- Evidence-based recommendations
- Focus on gradual, sustainable changes
- Emphasize self-compassion and patience

## Cross-Domain Awareness
- How wellness impacts career performance and relationships
- Financial barriers to wellness and creative solutions
- Connection between physical health and emotional resilience
"""
```

**Tool Allocation**:
```python
wellness_tools = [
    # Core Wellness Tools
    "assess_wellness_dimensions",
    "create_habit_formation_plan",
    "provide_stress_management_techniques",
    "create_sleep_optimization_plan",
    "design_exercise_program",
    
    # Mood and Habit Tools
    "log_mood_entry",
    "analyze_mood_progress_correlation",
    "create_habit",
    "track_habit_consistency",
    
    # Shared Tools
    "get_user_profile",
    "save_user_preference",
    "save_assessment",
    "get_active_plan"
]
```

## Coordinator Logic

### Delegation Decision Tree

```
Analyze User Request
        │
        ├─ Is it a crisis/emergency?
        │   └─ YES → Activate Emergency Protocol
        │
        ├─ What domains are involved?
        │   ├─ Single domain → Single specialist delegation
        │   └─ Multiple domains → Multi-specialist coordination
        │
        ├─ Is deep expertise required?
        │   ├─ YES → Delegate to specialist(s)
        │   └─ NO → Handle directly with general guidance
        │
        ├─ Are domains interconnected?
        │   ├─ YES → Sequential delegation with integration
        │   └─ NO → Parallel delegation to multiple specialists
        │
        └─ What's the complexity level?
            ├─ High → Full orchestration with conflict resolution
            ├─ Medium → Specialist delegation with basic integration
            └─ Low → Direct response or single consultation
```

### Delegation Protocol

**1. Preparation Phase**
```python
# Retrieve user context
user_context = get_user_profile(user_id)

# Define delegation requirements
delegation_request = {
    "specialist": "career-specialist",
    "context": user_context,
    "task": "Analyze career transition from marketing to data science",
    "constraints": {
        "timeframe": "6 months",
        "budget_constraints": "maintain current lifestyle",
        "family_considerations": "partner support needed"
    },
    "output_format": "structured_plan_with_milestones"
}
```

**2. Delegation Message Format**
```python
specialist_message = f"""
To: {specialist_name}
Context: {relevant_user_background}
Task: {specific_request_with_clear_deliverables}
Cross-Domain Considerations: {implications_for_other_domains}
Output Format: {desired_response_format}

Please provide specific, actionable recommendations with:
1. Analysis of current situation
2. Specific action steps with timelines
3. Resource recommendations
4. Cross-domain impact considerations
5. Success metrics and tracking suggestions
"""
```

**3. Integration Processing**
```python
# Collect specialist outputs
specialist_results = []
for specialist in delegated_specialists:
    result = await specialist.invoke(delegation_request)
    specialist_results.append(format_specialist_message(specialist, result))

# Detect conflicts and synergies
conflicts = detect_goal_conflicts(specialist_results)
synergies = detect_cross_domain_synergies(specialist_results)

# Generate unified response
unified_response = generate_unified_response_tool(
    specialist_results=specialist_results,
    conflicts=conflicts,
    synergies=synergies,
    user_context=user_context
)
```

## Communication Patterns

### Parallel Delegation

**Use When**: Domains are independent and can be analyzed simultaneously

```python
# Example: User wants general improvement across all domains
domains = ["career", "relationship", "finance", "wellness"]
specialist_requests = []

for domain in domains:
    request = create_specialist_request(
        domain=domain,
        task=f"Assess current {domain} situation and identify improvement opportunities",
        user_context=user_context
    )
    specialist_requests.append(request)

# Execute in parallel
results = await asyncio.gather(*[
    invoke_specialist(req) for req in specialist_requests
])

# Integrate results
integrated_plan = aggregate_and_harmonize_results(results)
```

### Sequential Delegation

**Use When**: One domain's analysis affects another domain

```python
# Example: Career change with financial implications
# Step 1: Analyze career options
career_result = await career_specialist.invoke({
    "task": "Analyze career change options and requirements",
    "context": user_context
})

# Step 2: Use career analysis for financial planning
finance_result = await finance_specialist.invoke({
    "task": "Create financial plan for career transition",
    "context": user_context,
    "career_analysis": career_result  # Pass previous result
})

# Step 3: Consider wellness implications
wellness_result = await wellness_specialist.invoke({
    "task": "Assess wellness impacts of career change",
    "context": user_context,
    "career_analysis": career_result,
    "financial_plan": finance_result
})
```

### Cross-Consultation

**Use When**: Specialists need to collaborate on complex issues

```python
# Initial specialist analysis
primary_result = await specialist_a.invoke(initial_request)

# Cross-consultation trigger
if "cross_domain_implications" in primary_result:
    consultation_request = {
        "task": "Review and advise on cross-domain impacts",
        "primary_analysis": primary_result,
        "consultation_focus": specific_domain
    }
    
    secondary_result = await specialist_b.invoke(consultation_request)
    
    # Integrate both analyses
    final_result = synthesize_cross_consultation(
        primary_result, 
        secondary_result
    )
```

## Integration Strategies

### Conflict Resolution

**Priority-Based Resolution**
```python
def resolve_conflicts_priority_based(conflicts, user_priorities):
    resolved_actions = []
    
    for conflict in conflicts:
        if conflict['priority'] in user_priorities:
            winner = conflict['competing_goals'][0]  # Higher priority wins
            resolution = {
                "action": winner['action'],
                "compromise": f"Delay {conflict['competing_goals'][1]['action']}",
                "rationale": f"Priority alignment with user goals"
            }
        else:
            resolution = suggest_compromise(conflict)
        
        resolved_actions.append(resolution)
    
    return resolved_actions
```

**Consensus-Based Resolution**
```python
def resolve_conflicts_consensus_based(conflicts):
    resolutions = []
    
    for conflict in conflicts:
        # Find middle ground that addresses both goals
        resolution = find_mutual_benefit_solution(conflict)
        resolutions.append(resolution)
    
    return resolutions
```

### Synergy Detection

```python
def detect_synergies(specialist_outputs):
    synergies = []
    
    # Look for complementary recommendations
    for output_a in specialist_outputs:
        for output_b in specialist_outputs:
            if output_a != output_b:
                synergy = analyze_compatibility(output_a, output_b)
                if synergy['strength'] > 0.7:  # High compatibility
                    synergies.append({
                        "domains": [output_a.domain, output_b.domain],
                        "synergy_type": synergy['type'],
                        "amplified_impact": synergy['combined_effect'],
                        "recommendations": synergy['integrated_actions']
                    })
    
    return synergies
```

## Configuration Templates

### Specialist Configuration Structure

```python
def create_specialist_config(
    name: str,
    description: str,
    system_prompt: str,
    tools: List[Any],
    model: str = "openai:glm-4.7"
) -> dict:
    """
    Creates a standardized specialist configuration.
    
    Args:
        name: Unique identifier for the specialist
        description: When to use this specialist
        system_prompt: Comprehensive behavior guidelines
        tools: List of LangChain tools available
        model: LLM model to use for this specialist
        
    Returns:
        dict: Specialist configuration dictionary
    """
    return {
        "name": name,
        "description": description,
        "system_prompt": system_prompt,
        "tools": tools,
        "model": model,
        "metadata": {
            "created_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "tool_count": len(tools),
            "domains": extract_domains_from_prompt(system_prompt)
        }
    }
```

### Tool Allocation Patterns

```python
def allocate_tools_to_specialist(
    specialist_type: str,
    base_tools: List[Any],
    specialist_tools: List[Any]
) -> List[Any]:
    """
    Allocates appropriate tools to each specialist.
    
    Base tools provided to all specialists:
    - Memory tools (get_user_profile, save_user_preference)
    - Context tools (save_assessment, get_active_plan)
    
    Specialist tools are domain-specific.
    """
    
    # All specialists get base tools
    allocated_tools = base_tools.copy()
    
    # Add domain-specific tools
    allocated_tools.extend(specialist_tools)
    
    # Add shared utility tools based on specialist needs
    if specialist_type in ["wellness", "relationship"]:
        allocated_tools.extend(mood_tracking_tools)
    
    if specialist_type == "career":
        allocated_tools.extend(goal_planning_tools)
    
    return allocated_tools
```

## Performance Optimization

### Parallel Processing

```python
async def parallel_specialist_execution(requests: List[dict]) -> List[dict]:
    """
    Executes multiple specialists in parallel when appropriate.
    """
    
    # Group requests by independence
    independent_requests = group_independent_requests(requests)
    dependent_requests = group_dependent_requests(requests)
    
    # Execute independent requests in parallel
    parallel_results = await asyncio.gather(*[
        invoke_specialist(req) for req in independent_requests
    ])
    
    # Execute dependent requests sequentially
    sequential_results = []
    for req in dependent_requests:
        result = await invoke_specialist(req)
        sequential_results.append(result)
    
    return combine_results(parallel_results, sequential_results)
```

### Caching Specialist Responses

```python
@lru_cache(maxsize=128)
def cached_specialist_analysis(
    specialist_name: str,
    analysis_hash: str
) -> str:
    """
    Caches specialist responses for similar requests.
    """
    # Implementation caches based on content hash
    pass
```

## Testing Strategies

### Individual Specialist Testing

```python
def test_career_specialist():
    """Tests career specialist with various scenarios."""
    
    specialist = get_career_specialist(tools=career_tools)
    
    # Test skill gap analysis
    result = specialist.invoke({
        "messages": [{
            "role": "user",
            "content": "Analyze my skills for a data science career. I have Python and SQL experience."
        }]
    })
    
    assert "skill gap" in result["messages"][-1].content.lower()
    assert "recommendations" in result["messages"][-1].content.lower()
```

### Integration Testing

```python
def test_multi_specialist_coordination():
    """Tests coordinator coordinating multiple specialists."""
    
    coach = create_life_coach()
    
    result = coach.invoke({
        "messages": [{
            "role": "user",
            "content": "I want to change careers but I'm worried about finances and my relationship."
        }]
    })
    
    response = result["messages"][-1].content
    
    # Should include career, finance, and relationship insights
    assert "career" in response.lower()
    assert "financ" in response.lower()
    assert "relationship" in response.lower()
    
    # Should show integration
    assert "cross-domain" in response.lower() or "integrated" in response.lower()
```

## Extension Guidelines

### Adding New Specialists

1. **Define Domain Expertise**
   ```python
   new_specialist_domain = "Leadership Development"
   core_competencies = [
       "Team management",
       "Leadership styles", 
       "Executive presence",
       "Organizational dynamics"
   ]
   ```

2. **Create System Prompt**
   - Follow established template structure
   - Include cross-domain awareness section
   - Define communication style
   - Add key frameworks and methodologies

3. **Develop Specialist Tools**
   ```python
   def create_leadership_tools():
       return [
           analyze_leadership_style,
           develop_team_management_plan,
           assess_executive_presence,
           create_leadership_development_roadmap
       ]
   ```

4. **Configure in Main System**
   ```python
   # Add to src/main.py
   leadership_specialist = get_leadership_specialist(
       tools=memory_tools + context_tools + leadership_tools
   )
   
   # Update coordinator subagent list
   subagents = [
       career_specialist,
       relationship_specialist, 
       finance_specialist,
       wellness_specialist,
       leadership_specialist  # New specialist
   ]
   ```

5. **Update Coordinator Logic**
   - Add delegation criteria for new domain
   - Include in cross-domain impact analysis
   - Add to integration patterns

### Customizing Existing Specialists

1. **Tool Addition**
   ```python
   # Add new tool to career specialist
   new_career_tools = career_tools + [networking_strategy_tool, personal_branding_tool]
   career_specialist["tools"] = new_career_tools
   ```

2. **Prompt Enhancement**
   ```python
   enhanced_prompt = career_specialist["system_prompt"] + additional_guidance
   career_specialist["system_prompt"] = enhanced_prompt
   ```

3. **Behavior Modification**
   - Adjust decision thresholds
   - Change communication style
   - Add new frameworks or methodologies

## Monitoring and Analytics

### Specialist Performance Metrics

```python
def track_specialist_performance(specialist_name: str, session_data: dict):
    """
    Tracks specialist effectiveness and user satisfaction.
    """
    
    metrics = {
        "response_time": session_data["duration"],
        "user_satisfaction": session_data["satisfaction_score"],
        "recommendation_quality": session_data["quality_rating"],
        "cross_domain_relevance": session_data["domain_alignment"],
        "follow_through_rate": session_data["action_completion_rate"]
    }
    
    # Store metrics for analysis
    store_performance_metrics(specialist_name, metrics)
```

### A/B Testing Specialist Configurations

```python
def specialist_ab_test(specialist_name: str, variant_a: dict, variant_b: dict):
    """
    Tests different specialist configurations.
    """
    
    # Randomly assign users to variants
    assignments = random_assignment([variant_a, variant_b])
    
    # Collect performance data
    results = collect_variant_performance(assignments)
    
    # Analyze which variant performs better
    analysis = compare_variant_performance(results)
    
    return analysis["winner"]
```

## Best Practices

### Specialist Design

1. **Clear Boundaries**: Each specialist has well-defined domain expertise
2. **Cross-Awareness**: Specialists understand impacts on other domains
3. **Actionable Output**: Provide specific, concrete recommendations
4. **Resource Provision**: Include tools, frameworks, and references
5. **Measurement Focus**: Include success metrics and tracking methods

### Coordinator Management

1. **Intelligent Delegation**: Only delegate when specialist expertise adds value
2. **Efficient Coordination**: Minimize back-and-forth between specialists
3. **Seamless Integration**: Create unified, coherent user experience
4. **Conflict Prevention**: Identify and resolve conflicts proactively
5. **Priority Alignment**: Always align with user's stated priorities

### Communication Standards

1. **Consistent Formatting**: Standardized output format across specialists
2. **Clear Attribution**: Identify which specialist provided which insights
3. **User-Friendly Language**: Avoid jargon and technical terminology
4. **Action-Oriented**: Focus on what user can do next
5. **Evidence-Based**: Provide reasoning for recommendations

---

## Conclusion

The subagent system is the core of the AI Life Coach's ability to provide comprehensive, expert guidance across multiple life domains. By following these patterns and guidelines, developers can extend and customize the system to address new domains and use cases while maintaining the high-quality, integrated user experience.

For specific implementation details and code examples, refer to the [API Reference](API_REFERENCE.md) and [Developer Guide](DEVELOPER.md).