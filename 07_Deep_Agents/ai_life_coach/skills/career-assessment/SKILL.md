---
name: career-assessment
description: Comprehensive career assessment including skill gap analysis, career path planning, resume optimization guidance, and professional development recommendations
version: 1.0.0
tools:
  - write_file
  - read_file
---

# Career Assessment Skill

## Purpose

This skill provides comprehensive career guidance including:

1. **Skill Gap Analysis**: Identify current skills vs required skills for target roles
2. **Career Path Planning**: Map out potential career progression paths
3. **Resume Optimization**: Guidance on improving resumes for target roles
4. **Professional Development**: Recommendations for skill development and growth

## Workflow

### Step 1: Assessment Framework

When a user requests career assessment:

1. **Gather Information**:
   - Current role and experience level
   - Target roles or career aspirations
   - Industry/sector of interest
   - Geographic preferences (if relevant)
   - Current skills and certifications
   - Work experience history

2. **Analyze Skills**:
   - Compare current skills to requirements for target roles
   - Identify critical skill gaps (must-have vs nice-to-have)
   - Assess transferable skills
   - Evaluate industry-specific knowledge

### Step 2: Career Path Mapping

Create a structured career path plan:

```
Current Role → Intermediate Roles → Target Role → Future Growth
```

For each step, identify:
- Typical time to transition
- Required skills and experience
- Recommended actions/milestones
- Potential barriers and how to overcome them

### Step 3: Action Plan Development

Break down into actionable steps:

**Short-term (0-3 months)**:
- Immediate skill priorities
- Quick wins for resume/portfolio
- Networking opportunities

**Medium-term (3-6 months)**:
- Skill development courses/certifications
- Project opportunities
- Job application strategy

**Long-term (6+ months)**:
- Major career transitions
- Advanced skill development
- Leadership opportunities

### Step 4: Documentation

Save all assessments and plans to files:

```
assessments/{user_id}/
├── career_assessment_{date}.md  # Overall assessment summary
├── skill_gap_analysis.xlsx      # Detailed skill matrix
└── career_path_plan.md          # Structured progression plan
```

## Best Practices

1. **Be Specific**: Provide concrete, actionable recommendations rather than vague advice
2. **Prioritize**: Focus on high-impact changes first (address critical skill gaps)
3. **Be Realistic**: Consider time constraints, financial resources, and current obligations
4. **Include Metrics**: Define measurable goals where possible (e.g., "Complete certification X by date Y")
5. **Regular Updates**: Recommend periodic review and adjustment of the plan

## Output Format

When delivering career assessment:

1. **Executive Summary**: Top 3-5 key findings and recommendations
2. **Detailed Analysis**:
   - Current state assessment
   - Identified gaps and opportunities
   - Market trends in target field
3. **Action Plan**:
   - Prioritized task list with timelines
   - Resources and recommendations for each action
4. **Files Created**: List of all saved documents with descriptions

## Example Prompts to Trigger This Skill

- "I want to transition from marketing manager to product manager"
- "Assess my readiness for a senior engineering role"
- "What skills do I need to become a data scientist?"
- "Help me plan my career path for the next 3 years"

## Notes

- Always ask clarifying questions if the user's goals or situation are unclear
- Consider both technical skills and soft skills in your assessment
- Account for industry trends and market conditions when making recommendations
- Encourage users to seek mentorship and networking opportunities