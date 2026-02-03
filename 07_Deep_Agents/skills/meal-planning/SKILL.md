---
name: meal-planning
description: Create personalized meal plans based on dietary needs and preferences
version: 1.0.0
tools:
  - read_file
  - write_file
  - web_search
---

# Meal Planning Skill

You are creating a personalized meal plan. Follow these steps:

## Step 1: Understand Requirements
Gather information about:
- Dietary restrictions (allergies, intolerances, preferences)
- Caloric needs and goals
- Cooking skill level and time available
- Budget considerations
- Number of meals per day
- Meal prep preferences (batch cooking, daily prep)

## Step 2: Check Existing Profile
Read the user's wellness profile if available:
```
workspace/wellness_assessment.md
```

## Step 3: Create Meal Plan
Design a meal plan including:
- Breakfast options (3-5 choices)
- Lunch options (3-5 choices)
- Dinner options (5-7 choices)
- Snack options (3-5 choices)
- Portion guidance

## Step 4: Generate Shopping List
Create a consolidated shopping list organized by:
- Produce
- Proteins
- Dairy/Alternatives
- Grains/Pantry
- Seasonings/Condiments

## Step 5: Save Outputs
Write the meal plan to `workspace/meal_plan.md` and shopping list to `workspace/shopping_list.md`.

## Nutritional Guidelines
- Balance macronutrients (protein, carbs, healthy fats)
- Include variety of vegetables and fruits
- Prioritize whole foods over processed
- Consider hydration needs
- Suggest prep tips for efficiency
