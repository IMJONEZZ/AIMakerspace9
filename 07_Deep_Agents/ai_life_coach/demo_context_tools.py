"""
Simple demo to verify context tools work correctly.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import config

# Initialize environment
print("Initializing AI Life Coach environment...")
config.initialize_environment()
print(f"✓ Workspace: {config.memory.workspace_dir}")

# Create context tools
from src.tools.context_tools import create_context_tools

print("\nCreating context tools...")
(
    save_assessment,
    get_active_plan,
    save_weekly_progress,
    list_user_assessments,
    read_assessment,
    save_curated_resource,
) = create_context_tools(backend=config.backend)
print("✓ Context tools created successfully")

# Test 1: Save an assessment
print("\n" + "=" * 60)
print("Test 1: Saving a user assessment")
print("=" * 60)

result = save_assessment.invoke(
    {
        "user_id": "test_user_001",
        "assessment_data": {
            "energy_level": 7,
            "stress_level": 4,
            "sleep_quality": "good",
            "mood": "positive",
            "notes": "Feeling good today!",
        },
    }
)
print(f"Result: {result}")

# Test 2: List assessments
print("\n" + "=" * 60)
print("Test 2: Listing user assessments")
print("=" * 60)

result = list_user_assessments.invoke({"user_id": "test_user_001"})
print(f"Result:\n{result}")

# Test 3: Read specific assessment
print("\n" + "=" * 60)
print("Test 3: Reading a specific assessment")
print("=" * 60)

from datetime import date

today = str(date.today())
result = read_assessment.invoke({"user_id": "test_user_001", "assessment_date": today})
print(f"Result:\n{result}")

# Test 4: Save weekly progress
print("\n" + "=" * 60)
print("Test 4: Saving weekly progress")
print("=" * 60)

result = save_weekly_progress.invoke(
    {
        "user_id": "test_user_001",
        "week_data": {
            "week_number": 1,
            "completion_rate": 0.85,
            "achievements": ["Started morning routine", "Exercised 3 times"],
            "challenges": ["Difficulty waking up early"],
        },
    }
)
print(f"Result: {result}")

# Test 5: Save a curated resource
print("\n" + "=" * 60)
print("Test 5: Saving a curated resource")
print("=" * 60)

result = save_curated_resource.invoke(
    {
        "title": "Morning Routine Guide",
        "category": "wellness_tips",
        "content": """
Start your day with these habits:
1. Drink a glass of water
2. 10 minutes of meditation
3. Light stretching or exercise
4. Healthy breakfast
""",
    }
)
print(f"Result: {result}")

# Test 6: Get active plan (should return no plan error)
print("\n" + "=" * 60)
print("Test 6: Getting active plan (no plan exists yet)")
print("=" * 60)

result = get_active_plan.invoke({"user_id": "test_user_001"})
print(f"Result: {result}")

# Test 7: Create a plan file manually and then read it
print("\n" + "=" * 60)
print("Test 7: Creating and reading a plan")
print("=" * 60)

# Create a test plan file
plans_dir = config.memory.workspace_dir / "plans" / "test_user_001"
plans_dir.mkdir(parents=True, exist_ok=True)

plan_file = plans_dir / "90_day_wellness_plan.md"
plan_content = """# 90-Day Wellness Challenge

## Phase 1: Foundation (Weeks 1-4)
### Week 1
- Establish morning routine
- Start tracking sleep

## Phase 2: Building Habits (Weeks 5-8)
### Week 5
- Maintain morning routine consistently
- Add strength training

## Phase 3: Optimization (Weeks 9-12)
### Week 9
- Fine-tune routine based on feedback

Let's do this! 💪
"""
plan_file.write_text(plan_content)

# Now read it using the tool
result = get_active_plan.invoke({"user_id": "test_user_001"})
print(f"Result:\n{result}")

# Final check - verify directory structure
print("\n" + "=" * 60)
print("Verification: Directory Structure")
print("=" * 60)

import os

for root, dirs, files in os.walk(config.memory.workspace_dir):
    level = root.replace(str(config.memory.workspace_dir), "").count(os.sep)
    indent = " " * 2 * level
    print(f"{indent}{os.path.basename(root)}/")
    subindent = " " * 2 * (level + 1)
    for file in files:
        print(f"{subindent}{file}")

print("\n" + "=" * 60)
print("✅ All tests completed successfully!")
print("=" * 60)
