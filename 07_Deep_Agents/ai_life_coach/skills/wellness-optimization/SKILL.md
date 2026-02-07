---
name: wellness-optimization
description: Comprehensive wellness guidance including physical health, mental wellbeing, stress management, sleep optimization, and habit formation strategies
version: 1.0.0
tools:
  - write_file
  - read_file
---

# Wellness Optimization Skill

## Purpose

This skill provides comprehensive wellness guidance across multiple dimensions:

1. **Physical Health**: Exercise plans, nutrition basics, sleep optimization
2. **Mental Wellbeing**: Stress management techniques, mindfulness practices
3. **Emotional Health**: Mood tracking, emotional regulation strategies
4. **Habit Formation**: Building sustainable healthy habits, breaking unhealthy ones
5. **Work-Life Balance**: Setting boundaries, preventing burnout

## The 8 Dimensions of Wellness Framework

When conducting wellness assessments, consider all dimensions:

1. **Physical**: Exercise, nutrition, sleep, preventive care
2. **Emotional**: Coping effectively with life, expressing emotions
3. **Intellectual**: Learning new skills, creative pursuits, mental stimulation
4. **Social**: Connection with others, sense of belonging, support network
5. **Spiritual**: Purpose, meaning, values (not necessarily religious)
6. **Environmental**: Safe surroundings, access to healthy resources
7. **Financial**: Managing money effectively, reducing financial stress
8. **Occupational**: Job satisfaction, work-life balance, career fulfillment

## Workflow

### Step 1: Comprehensive Wellness Assessment

When a user requests wellness guidance:

1. **Gather Baseline Information**:
   - Current activity level and exercise habits
   - Sleep patterns (duration, quality, consistency)
   - Stress levels and major stressors
   - Diet/nutrition habits (general overview—no clinical advice)
   - Current mental health baseline
   - Existing routines and daily schedule
   - Time constraints and priorities

2. **Identify Wellness Gaps**:
   - Which dimensions need the most attention?
   - What's working well that can be built upon?
   - What are the biggest barriers to change?

### Step 2: Priority Setting Framework

Use the **Impact vs Effort Matrix** to prioritize wellness changes:

```
High Impact, Low Effort    →  Start Here (Quick Wins)
High Impact, High Effort   →  Plan Carefully (Major Goals)
Low Impact, Low Effort     →  Consider Later (Nice-to-Have)
Low Impact, High Effort    →  Avoid (Waste of Energy)
```

### Step 3: Action Planning by Domain

#### Physical Health Optimization:

**Exercise Recommendations (Based on Guidelines)**:
- **Adults**: 150 minutes moderate activity OR 75 vigorous activity per week
- **Plus**: Strength training 2x per week
- Start small if sedentary—even 10-minute walks count

**Sleep Optimization**:
- Target: 7-9 hours per night for most adults
- Tips: Consistent schedule, dark/cool room, no screens 1 hour before bed
- Track: Note sleep duration and quality in a journal

**Nutrition Basics (Educational, Not Clinical)**:
- Focus on whole foods: vegetables, fruits, lean proteins, whole grains
- Stay hydrated: 8 glasses of water per day (individual needs vary)
- Limit processed foods, added sugars, excessive caffeine
- Practice mindful eating: slow down, pay attention to hunger cues

#### Mental Wellbeing Strategies:

**Stress Management Techniques**:
1. **Deep Breathing**: 4-7-8 technique (inhale 4, hold 7, exhale 8)
2. **Physical Activity**: Even short walks reduce stress hormones
3. **Journaling**: Write down thoughts to process emotions
4. **Time in Nature**: 20 minutes outdoors lowers cortisol

**Mindfulness Practices**:
- Start with 5-minute daily meditation
- Practice present-moment awareness during routine activities
- Use apps like Headspace or Calm if helpful

**Emotional Regulation**:
- Name emotions to tame them
- Practice the "STOP" technique: Stop, Take a breath, Observe, Proceed mindfully
- Reach out for social support when needed

#### Habit Formation Strategy:

Use the **Habit Loop Framework**:
```
CUE → ROUTINE → REWARD
```

1. **Identify the Cue**: What triggers the habit? (time, location, emotion)
2. **Design the Routine**: What specific action will you take?
3. **Choose a Reward**: How will you reinforce the behavior?

**Starting Small Rule**:
- Make habits so small they're impossible to fail
- Example: Instead of "run 3 miles," start with "put on running shoes"
- Build momentum by stringing together tiny wins

**Habit Stacking**:
- Attach new habits to existing ones
- "After I [existing habit], I will [new habit]"
- Example: "After I brush my teeth, I will do 2 push-ups"

### Step 4: Creating a Personalized Wellness Plan

Structure the plan in phases:

**Phase 1 (Weeks 1-2): Foundations**
- Establish sleep schedule
- Add one daily movement habit (10-minute walk)
- Start simple stress management practice

**Phase 2 (Weeks 3-4): Building Momentum**
- Increase exercise to target duration
- Add nutrition improvements (one change at a time)
- Begin tracking progress

**Phase 3 (Weeks 5-8): Integration**
- Build comprehensive routine across dimensions
- Implement habit stacking for efficiency
- Adjust based on what's working

### Step 5: Documentation

Save wellness plans and progress:

```
assessments/{user_id}/
├── wellness_assessment_{date}.md      # Initial comprehensive assessment
└── habits_inventory.md                # Current habits analysis

plans/{user_id}/
├── 90_day_wellness_plan.md            # Structured action plan
└── habit_tracking_template.csv        # Daily habit tracker

progress/{user_id}/
├── weekly_check_ins/                  # Weekly progress notes
│   ├── week_01.md
│   ├── week_02.md
│   └── ...
└── monthly_reviews/                   # Monthly summaries
    ├── month_01.md
    └── ...

workspace/resources/
├── exercise_routines.md                # Exercise options by level
├── sleep_hygiene_guide.md             # Sleep optimization tips
└── stress_management toolkit.md       # Coping strategies library
```

## Best Practices

1. **Start Small**: One small change beats multiple big changes that don't stick
2. **Focus on Addition, Not Subtraction**: Add healthy habits before removing unhealthy ones
3. **Track Progress**: What gets measured gets managed—even simple checkmarks work
4. **Be Flexible**: Life happens—adapt plans when needed rather than abandoning them
5. **Celebrate Wins**: Acknowledge progress, no matter how small

## Habit Tracking Template

```csv
Date,Sleep (hrs),Exercise (min),Meditation (min),Water (glasses),Stress Level,Notes
2024-01-15,7.5,30,10,8,Moderate,Felt good after morning walk
2024-01-16,6.0,15,5,6,High,Tired today—focus on sleep tonight
...
```

## Output Format

When delivering wellness guidance:

1. **Executive Summary**: Top 3-5 key findings and immediate recommendations
2. **Wellness Assessment Results**:
   - Current state across all 8 dimensions
   - Identified strengths and areas for improvement
   - Priority focus areas based on impact vs effort
3. **Action Plan**:
   - 90-day structured wellness plan phased by weeks
   - Habit formation strategy with specific routines
   - Priority matrix for change implementation
4. **Resources Provided**:
   - Habit tracking template
   - Exercise routines by fitness level
   - Stress management toolkit
5. **Files Created**: List of all saved documents with descriptions

## Example Prompts to Trigger This Skill

- "I want to improve my sleep quality"
- "Help me start an exercise routine"
- "I'm feeling stressed and overwhelmed—what can I do?"
- "How can I build healthier daily habits?"
- "I need a comprehensive wellness plan"

## Important Notes

- Wellness guidance is educational, not medical advice
- Users should consult healthcare providers for specific health concerns
- Progress isn't linear—setbacks are normal and expected
- Mental health deserves the same attention as physical health
- Wellness looks different for everyone—personalize to individual needs

## When to Recommend Professional Help

Consider recommending professional help if:

- Sleep problems persist despite hygiene improvements
- Excessive fatigue or energy levels don't improve with lifestyle changes
- Mental health symptoms interfere with daily functioning
- Eating patterns suggest possible eating disorders
- Chronic pain or physical symptoms need medical evaluation
- Substance use concerns arise

## Warning Signs of Burnout to Monitor

If user reports multiple of these, suggest professional mental health support:

- Persistent fatigue that doesn't improve with rest
- Detachment or cynicism toward work/life
- Reduced performance and productivity
- Physical symptoms (headaches, digestive issues)
- Withdrawal from social activities
- Increased irritability or frustration

## Integrating Across Domains

Remind users that wellness is interconnected:

- **Physical health** affects mental wellbeing
- **Stress management** improves sleep quality  
- **Better sleep** enhances cognitive function and mood
- **Social connection** supports both mental and physical health
- **Financial stress** impacts overall wellbeing

A holistic approach addresses the whole person, not just symptoms in isolation.