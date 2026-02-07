"""
Quick demo of planning tools functionality.

This script demonstrates the three planning tools:
1. write_todos - Create a structured todo list
2. update_todo - Update individual todos
3. list_todos - Display filtered todos

Run this to verify the planning tools work correctly.
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from tools.planning_tools import create_planning_tools


def main():
    print("=" * 60)
    print("AI Life Coach - Planning Tools Demo")
    print("=" * 60)

    # Create planning tools
    write_todos, update_todo, list_todos = create_planning_tools()

    # Example 1: Create a todo list for life coaching
    print("\n### Step 1: Creating a structured todo list ###")
    todos = [
        {"title": "Initial life assessment", "phase": "discovery"},
        {
            "title": "Identify top 3 priorities",
            "phase": "discovery",
            "depends_on": [0],
        },
        {"title": "Create 90-day action plan", "phase": "planning", "depends_on": [1]},
        {"title": "Weekly check-in system", "phase": "execution"},
    ]

    result = write_todos.invoke({"todos": todos})
    print(f"✓ {result}")

    # Example 2: List all todos
    print("\n### Step 2: Listing all todos ###")
    result = list_todos.invoke({})
    print(result)

    # Example 3: Update a todo status
    print("\n### Step 3: Updating first todo to in_progress ###")
    result = update_todo.invoke({"todo_id": 0, "status": "in_progress"})
    print(f"✓ {result}")

    # Example 4: Try to update a dependent task (should be blocked)
    print("\n### Step 4: Trying to mark dependent task as in_progress (should be blocked) ###")
    result = update_todo.invoke({"todo_id": 2, "status": "in_progress"})
    print(f"✗ {result}")

    # Example 5: Complete the blocking task
    print("\n### Step 5: Completing task 0 and 1 ###")
    result = update_todo.invoke({"todo_id": 0, "status": "completed"})
    print(f"✓ {result}")
    result = update_todo.invoke({"todo_id": 1, "status": "completed"})
    print(f"✓ {result}")

    # Example 6: Now task 2 can be updated
    print("\n### Step 6: Updating dependent task (now allowed) ###")
    result = update_todo.invoke({"todo_id": 2, "status": "in_progress"})
    print(f"✓ {result}")

    # Example 7: Filter by phase
    print("\n### Step 7: Listing only discovery phase todos ###")
    result = list_todos.invoke({"phase": "discovery"})
    print(result)

    # Example 8: Filter by status
    print("\n### Step 8: Listing only pending todos ###")
    result = list_todos.invoke({"status": "pending"})
    print(result)

    # Example 9: Add notes to a todo
    print("\n### Step 9: Adding notes to task 3 ###")
    result = update_todo.invoke(
        {"todo_id": 3, "notes": "Will implement weekly check-ins on Mondays"}
    )
    print(f"✓ {result}")

    # Example 10: Show circular dependency detection
    print("\n### Step 10: Demonstrating circular dependency protection ###")
    circular_todos = [
        {"title": "Task A", "depends_on": [1]},
        {"title": "Task B", "depends_on": [0]},
    ]
    result = write_todos.invoke({"todos": circular_todos})
    print(f"✗ {result}")

    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
