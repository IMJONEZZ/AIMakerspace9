#!/usr/bin/env python
"""
Demonstration script for Phase-Based Planning System.

This script demonstrates the key features of the 4-phase planning system:
1. Initializing a phase workflow
2. Generating milestones from goals
3. Checking phase status and transition eligibility
4. Adapting plans based on progress
5. Applying phase-specific templates

Usage:
    python demo_phase_planning.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import config
from src.tools.phase_planning_tools import (
    create_phase_planning_tools,
)


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)


def main():
    """Run the phase planning demonstration."""
    # Initialize environment
    config.initialize_environment()

    print_section("PHASE-BASED PLANNING SYSTEM DEMONSTRATION")

    # Create phase planning tools
    from src.config import get_backend

    (
        initialize_workflow,
        transition_phase,
        generate_milestones,
        adapt_plan,
        get_status,
        apply_template,
    ) = create_phase_planning_tools(backend=get_backend())

    # Demo user
    USER_ID = "demo_user_123"

    # Sample goals
    GOALS = [
        {"title": "Learn Python programming", "domain": "career"},
        {"title": "Improve physical fitness", "domain": "wellness"},
        {"title": "Build emergency fund", "domain": "finance"},
    ]

    # 1. Initialize Phase Workflow
    print_section("Step 1: Initialize Phase Workflow")
    result = initialize_workflow.invoke({"user_id": USER_ID, "goals": GOALS})
    print(result)

    # 2. Check Initial Status
    print_section("Step 2: Check Phase Status")
    result = get_status.invoke({"user_id": USER_ID})
    print(result)

    # 3. Generate Milestones
    print_section("Step 3: Generate Milestones from Goals")
    result = generate_milestones.invoke({"user_id": USER_ID})
    print(result)

    # 4. Apply Phase Template
    print_section("Step 4: Apply Discovery Phase Template")
    result = apply_template.invoke({"user_id": USER_ID, "phase": "discovery"})
    print(result)

    # 5. Try to Transition (Should be blocked)
    print_section("Step 5: Attempt Phase Transition (Will Be Blocked)")
    result = transition_phase.invoke({"user_id": USER_ID})
    print(result)

    # 6. Simulate Progress
    print_section("Step 6: Adapt Plan Based on Progress")
    result = adapt_plan.invoke(
        {
            "user_id": USER_ID,
            "progress_data": {
                "milestone_progress": {},
                "goal_progress": {"g1": 30, "g2": 50},
                "notes": "Making good progress on fitness and Python learning",
            },
        }
    )
    print(result)

    # 7. Summary
    print_section("DEMONSTRATION COMPLETE")
    print("""
The Phase-Based Planning System provides:

✅ 4-Phase Workflow Management
   - Discovery: Assessment and goal identification
   - Planning: Action plan creation with dependencies
   - Execution: Task implementation and tracking
   - Review: Progress evaluation and adaptation

✅ Automated Milestone Generation
   - Phase completion checkpoints
   - Goal achievement targets
   - Timeline estimation

✅ Adaptive Planning
   - Progress tracking against milestones
   - Automatic adaptation recommendations
   - Plan adjustment based on feedback

✅ Phase Transition Logic
   - Dependency validation before transitions
   - Completion criteria tracking
   - Block detection and reporting

✅ Phase-Specific Templates
   - Tailored output formatting for each phase
   - Status visualization with icons
   - Deliverables and criteria tracking

All tools are integrated into the AI Life Coach system via main.py!
    """)


if __name__ == "__main__":
    main()
