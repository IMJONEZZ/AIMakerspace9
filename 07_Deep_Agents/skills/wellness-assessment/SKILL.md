---
name: wellness-assessment
description: Assess user wellness goals and create personalized recommendations
version: 1.0.0
tools:
  - read_file
  - write_file
---

# Wellness Assessment Skill

You are conducting a comprehensive wellness assessment. Follow these steps:

## Step 1: Gather Information
Ask the user about:
- Current health goals (weight, fitness, stress, sleep)
- Any medical conditions or limitations
- Current exercise routine (or lack thereof)
- Dietary preferences and restrictions
- Sleep patterns and quality
- Stress levels and sources

## Step 2: Analyze Responses
Review the user's answers and identify:
- Primary wellness priority
- Secondary goals
- Potential barriers to success
- Existing healthy habits to build on

## Step 3: Create Assessment Report
Write a wellness assessment report to `workspace/wellness_assessment.md` containing:
- Summary of current wellness state
- Identified strengths
- Areas for improvement
- Recommended focus areas (prioritized)
- Suggested next steps

## Step 4: Provide Recommendations
Based on the assessment, provide:
- 3 immediate action items (can start today)
- 3 short-term goals (1-2 weeks)
- 3 long-term goals (1-3 months)

## Output Format
Always save results to the workspace directory and provide a clear summary to the user.
