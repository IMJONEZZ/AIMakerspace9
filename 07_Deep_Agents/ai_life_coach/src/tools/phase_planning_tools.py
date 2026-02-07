"""
Phase-Based Planning Tools for AI Life Coach.

This module provides advanced tools for managing 4-phase project workflows
with automated milestone generation, adaptive planning, and phase transition logic.

Based on research in:
- Hybrid project management (combining Waterfall structure with Agile flexibility)
- Multi-phase project lifecycle management
- Adaptive planning methodologies for dynamic goal adjustment

Phases:
1. Discovery: Assessment, goal identification, current state analysis
2. Planning: Action plan creation with dependencies and resource allocation
3. Execution: Task implementation, progress tracking, iterative refinement
4. Review: Progress evaluation, adaptation, lessons learned, next steps

Tools:
- initialize_phase_workflow: Create a new 4-phase workflow for goals
- transition_to_next_phase: Move to next phase with dependency validation
- generate_milestones_from_goals: Auto-generate milestones based on goals and phases
- adapt_plan_based_on_progress: Adjust plan based on progress feedback
- get_phase_status: Show current phase and completion criteria status
- apply_phase_template: Generate phase-specific formatted output
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import json

# Import LangChain components
try:
    from langchain_core.tools import tool
except ImportError:
    # Fallback for development environments without full LangChain
    def tool(func):
        """Fallback decorator when langchain_core is not available."""
        func.is_tool = True  # type: ignore
        return func


# Import backend configuration
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import get_backend


# ==============================================================================
# Phase Configuration and Data Models
# ==============================================================================


class Phase:
    """Represents a single phase in the 4-phase workflow."""

    VALID_PHASES = ["discovery", "planning", "execution", "review"]

    PHASE_CONFIG = {
        "discovery": {
            "name": "Discovery",
            "description": "Assessment, goal identification, and current state analysis",
            "objective": "Understand the starting point and define clear goals",
            "typical_duration_days": 7,
            "completion_criteria": [
                "Initial assessment completed",
                "Current state documented",
                "Goals identified and prioritized",
                "Constraints and resources listed",
            ],
            "deliverables": [
                "Current state assessment",
                "Goal list with priorities",
                "Resource inventory",
                "Constraint analysis",
            ],
            "icon": "🔍",
        },
        "planning": {
            "name": "Planning",
            "description": "Action plan creation with dependencies and resource allocation",
            "objective": "Create a detailed, executable roadmap",
            "typical_duration_days": 14,
            "completion_criteria": [
                "Action plan created",
                "Dependencies identified and validated",
                "Timeline established",
                "Resources allocated",
            ],
            "deliverables": [
                "Detailed action plan",
                "Dependency graph",
                "Timeline with milestones",
                "Resource allocation plan",
            ],
            "icon": "📋",
        },
        "execution": {
            "name": "Execution",
            "description": "Task implementation, progress tracking, and iterative refinement",
            "objective": "Execute the plan while adapting to changes",
            "typical_duration_days": 90,
            "completion_criteria": [
                "All tasks completed or documented",
                "Progress tracked against milestones",
                "Adaptations made as needed",
                "Results documented",
            ],
            "deliverables": [
                "Completed tasks and outcomes",
                "Progress tracking records",
                "Adaptation log",
                "Results documentation",
            ],
            "icon": "🚀",
        },
        "review": {
            "name": "Review",
            "description": "Progress evaluation, adaptation, lessons learned, and next steps",
            "objective": "Evaluate outcomes and identify improvements for future iterations",
            "typical_duration_days": 7,
            "completion_criteria": [
                "Outcomes evaluated",
                "Lessons learned documented",
                "Success metrics assessed",
                "Next steps planned",
            ],
            "deliverables": [
                "Outcome evaluation report",
                "Lessons learned document",
                "Success metrics analysis",
                "Next steps recommendations",
            ],
            "icon": "📊",
        },
    }

    @classmethod
    def get_phase_info(cls, phase_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific phase."""
        return cls.PHASE_CONFIG.get(phase_name)

    @classmethod
    def get_next_phase(cls, current_phase: str) -> Optional[str]:
        """Get the next phase in sequence."""
        phases = cls.VALID_PHASES
        try:
            current_index = phases.index(current_phase)
            if current_index < len(phases) - 1:
                return phases[current_index + 1]
        except ValueError:
            pass
        return None


class Milestone:
    """Represents a milestone in the project timeline."""

    def __init__(
        self,
        id: str,
        title: str,
        target_date: Optional[str] = None,
        status: str = "pending",
        dependencies: Optional[List[str]] = None,
        phase: Optional[str] = None,
        description: Optional[str] = None,
    ):
        self.id = id
        self.title = title
        self.target_date = target_date  # ISO format date string
        self.status = status  # pending, in_progress, completed, delayed
        self.dependencies = dependencies or []
        self.phase = phase  # Which phase this milestone belongs to
        self.description = description

    def to_dict(self) -> Dict[str, Any]:
        """Convert milestone to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "target_date": self.target_date,
            "status": self.status,
            "dependencies": self.dependencies,
            "phase": self.phase,
            "description": self.description,
        }


class PhaseWorkflow:
    """Manages the complete 4-phase workflow with state tracking."""

    def __init__(self, user_id: str, goals: List[Dict[str, Any]]):
        self.user_id = user_id
        self.goals = goals
        self.current_phase = "discovery"
        self.phase_history: List[Dict[str, Any]] = []
        self.milestones: Dict[str, Milestone] = {}
        self.adaptations: List[Dict[str, Any]] = []
        self.phase_dates: Dict[str, str] = {}
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at

        # Track completion of each phase's criteria
        self.phase_completion: Dict[str, Dict[str, bool]] = {
            phase: {
                criterion: False for criterion in Phase.PHASE_CONFIG[phase]["completion_criteria"]
            }
            for phase in Phase.VALID_PHASES
        }

    def add_milestone(self, milestone: Milestone) -> None:
        """Add a milestone to the workflow."""
        self.milestones[milestone.id] = milestone
        self.updated_at = datetime.now().isoformat()

    def update_milestone_status(self, milestone_id: str, status: str) -> None:
        """Update milestone status."""
        if milestone_id in self.milestones:
            self.milestones[milestone_id].status = status
            self.updated_at = datetime.now().isoformat()

    def update_phase_completion(self, phase: str, criterion: str, completed: bool) -> None:
        """Update completion status for a phase's criterion."""
        if phase in self.phase_completion and criterion in self.phase_completion[phase]:
            self.phase_completion[phase][criterion] = completed
            self.updated_at = datetime.now().isoformat()

    def get_phase_completion_percentage(self, phase: str) -> float:
        """Get completion percentage for a phase."""
        if phase not in self.phase_completion:
            return 0.0
        criteria = self.phase_completion[phase]
        completed = sum(1 for c in criteria.values() if c)
        total = len(criteria)
        return (completed / total * 100) if total > 0 else 0.0

    def can_transition_to_next_phase(self) -> tuple[bool, List[str]]:
        """
        Check if transition to next phase is allowed.

        Returns:
            Tuple of (can_transition, list_of_blocking_criteria)
        """
        if self.current_phase not in Phase.VALID_PHASES:
            return False, [f"Invalid current phase: {self.current_phase}"]

        # Check if all completion criteria for current phase are met
        blocking_criteria = []
        for criterion, completed in self.phase_completion[self.current_phase].items():
            if not completed:
                blocking_criteria.append(criterion)

        # Check if milestone dependencies are satisfied
        for milestone in self.milestones.values():
            if milestone.phase == self.current_phase and milestone.status != "completed":
                blocking_criteria.append(f"Milestone '{milestone.title}' not completed")

        can_transition = len(blocking_criteria) == 0
        return can_transition, blocking_criteria

    def transition_to_next_phase(self) -> tuple[bool, str]:
        """
        Attempt to transition to the next phase.

        Returns:
            Tuple of (success, message)
        """
        can_transition, blocking_criteria = self.can_transition_to_next_phase()

        if not can_transition:
            return False, f"Cannot transition: {', '.join(blocking_criteria)}"

        next_phase = Phase.get_next_phase(self.current_phase)
        if not next_phase:
            return False, "Already in final phase (review)"

        # Record transition in history
        self.phase_history.append(
            {
                "from_phase": self.current_phase,
                "to_phase": next_phase,
                "timestamp": datetime.now().isoformat(),
            }
        )

        self.current_phase = next_phase
        self.updated_at = datetime.now().isoformat()

        return True, f"Successfully transitioned from {self.current_phase} to {next_phase}"

    def add_adaptation(self, reason: str, changes: Dict[str, Any]) -> None:
        """Record an adaptation made to the plan."""
        self.adaptations.append(
            {
                "timestamp": datetime.now().isoformat(),
                "phase": self.current_phase,
                "reason": reason,
                "changes": changes,
            }
        )
        self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow to dictionary."""
        return {
            "user_id": self.user_id,
            "goals": self.goals,
            "current_phase": self.current_phase,
            "phase_history": self.phase_history,
            "milestones": {mid: m.to_dict() for mid, m in self.milestones.items()},
            "adaptations": self.adaptations,
            "phase_completion": self.phase_completion,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


# ==============================================================================
# Helper Functions
# ==============================================================================


def generate_milestones_from_goals(
    goals: List[Dict[str, Any]], phases: Optional[List[str]] = None
) -> List[Milestone]:
    """
    Automatically generate milestones from goals.

    Args:
        goals: List of goal dictionaries
        phases: Optional list of phases to generate milestones for. If None, uses all phases.

    Returns:
        List of Milestone objects
    """
    if phases is None:
        phases = Phase.VALID_PHASES

    milestones = []
    milestone_counter = 1

    # Generate phase-specific milestones
    for i, phase in enumerate(phases):
        phase_info = Phase.get_phase_info(phase)
        if not phase_info:
            continue

        # Create a milestone for completing the phase
        ms_id = f"ms_{milestone_counter}"
        milestone_counter += 1

        completion_milestone = Milestone(
            id=ms_id,
            title=f"Complete {phase_info['name']} Phase",
            phase=phase,
            description=f"All deliverables for {phase_info['name']} completed and validated",
        )
        milestones.append(completion_milestone)

    # Generate goal-specific milestones (aligned with execution phase)
    # Only generate if execution is in the requested phases
    if "execution" in phases:
        for i, goal in enumerate(goals):
            ms_id = f"ms_{milestone_counter}"
            milestone_counter += 1

            goal_milestone = Milestone(
                id=ms_id,
                title=f"Achieve Goal: {goal.get('title', 'Goal ' + str(i + 1))}",
                phase="execution",
                description=f"Complete goal: {goal.get('description', goal.get('title', ''))}",
            )
            milestones.append(goal_milestone)

    return milestones


def estimate_phase_start_dates(
    start_date: datetime, phases: Optional[List[str]] = None
) -> Dict[str, str]:
    """
    Estimate start dates for each phase.

    Args:
        start_date: The start date for the first phase
        phases: Optional list of phases. If None, uses all phases.

    Returns:
        Dictionary mapping phase names to ISO format start dates
    """
    if phases is None:
        phases = Phase.VALID_PHASES

    phase_dates = {}
    current_date = start_date

    for phase in phases:
        phase_info = Phase.get_phase_info(phase)
        if not phase_info:
            continue

        phase_dates[phase] = current_date.isoformat()

        # Move to next phase start date
        duration_days = phase_info.get("typical_duration_days", 7)
        current_date += timedelta(days=duration_days)

    return phase_dates


def calculate_adaptive_recommendations(
    workflow: PhaseWorkflow, progress_data: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Calculate adaptive planning recommendations based on progress.

    Args:
        workflow: The current phase workflow
        progress_data: Current progress data

    Returns:
        List of recommended adaptations
    """
    recommendations = []

    # Check milestone delays
    for mid, milestone in workflow.milestones.items():
        if milestone.status == "delayed":
            recommendations.append(
                {
                    "type": "milestone_adjustment",
                    "priority": "high",
                    "milestone_id": mid,
                    "recommendation": f"Reschedule or adjust approach for delayed milestone '{milestone.title}'",
                    "reason": "Milestone is behind schedule",
                }
            )

    # Check phase completion progress
    for phase in Phase.VALID_PHASES:
        completion_pct = workflow.get_phase_completion_percentage(phase)
        if phase == workflow.current_phase and completion_pct < 50:
            recommendations.append(
                {
                    "type": "phase_extension",
                    "priority": "medium",
                    "phase": phase,
                    "recommendation": f"Consider extending {phase} phase duration",
                    "reason": f"Only {completion_pct:.0f}% completion, may need more time",
                }
            )

    # Check goal progress if provided
    if "goal_progress" in progress_data:
        for goal_id, goal_pct in progress_data["goal_progress"].items():
            if goal_pct < 30:
                goal = next((g for g in workflow.goals if g.get("id") == goal_id), None)
                if goal:
                    recommendations.append(
                        {
                            "type": "goal_adjustment",
                            "priority": "high",
                            "goal_id": goal_id,
                            "recommendation": f"Review and adjust approach for '{goal.get('title', goal_id)}'",
                            "reason": f"Low progress ({goal_pct:.0f}%)",
                        }
                    )

    return recommendations


def apply_phase_template(phase: str, content: Dict[str, Any], completion_pct: float = 0.0) -> str:
    """
    Apply phase-specific formatting template.

    Args:
        phase: The phase name
        content: Content to format
        completion_pct: Optional completion percentage (default: 0.0)

    Returns:
        Formatted string output
    """
    phase_info = Phase.get_phase_info(phase)
    if not phase_info:
        return f"Unknown phase: {phase}"

    lines = []
    icon = phase_info["icon"]

    # Header
    lines.append(f"{icon} {phase_info['name'].upper()} PHASE")
    lines.append("=" * 60)
    lines.append(f"Objective: {phase_info['objective']}")
    lines.append("")

    # Content sections
    if "status" in content:
        lines.append("📊 Status:")
        for key, value in content["status"].items():
            lines.append(f"  • {key}: {value}")
        lines.append("")

    if "completion_criteria" in content:
        # Use provided completion_pct or calculate from criteria
        if completion_pct == 0.0 and "completion_criteria" in content:
            completed = sum(1 for c in content["completion_criteria"].values() if c)
            total = len(content["completion_criteria"])
            completion_pct = (completed / total * 100) if total > 0 else 0

        lines.append(f"✓ Completion Criteria ({completion_pct:.0f}% complete):")
        for criterion, completed in content["completion_criteria"].items():
            status_icon = "✅" if completed else "⬜"
            lines.append(f"  {status_icon} {criterion}")
        lines.append("")

    if "deliverables" in content:
        lines.append("📦 Deliverables:")
        for deliverable in content["deliverables"]:
            status = content.get("deliverable_status", {}).get(deliverable, "pending")
            status_icon = {"completed": "✅", "in_progress": "🔄"}.get(status, "⏳")
            lines.append(f"  {status_icon} {deliverable}")
        lines.append("")

    if "milestones" in content:
        lines.append("🎯 Phase Milestones:")
        for milestone in content["milestones"]:
            ms_status = milestone.get("status", "pending")
            status_icon = {"completed": "✅", "in_progress": "🔄", "delayed": "⚠️"}.get(
                ms_status, "⏳"
            )
            lines.append(f"  {status_icon} {milestone.get('title', 'Untitled')}")
            if milestone.get("target_date"):
                lines.append(f"     Target: {milestone['target_date']}")
        lines.append("")

    if "notes" in content:
        lines.append("📝 Notes:")
        lines.append(content["notes"])
        lines.append("")

    return "\n".join(lines)


# ==============================================================================
# Global Workflow Storage
# ==============================================================================

_workflows: Dict[str, PhaseWorkflow] = {}


def get_workflow(user_id: str) -> Optional[PhaseWorkflow]:
    """Get workflow for a user."""
    return _workflows.get(user_id)


def save_workflow(workflow: PhaseWorkflow) -> None:
    """Save workflow to storage."""
    _workflows[workflow.user_id] = workflow


# ==============================================================================
# Phase Planning Tools Factory
# ==============================================================================


def create_phase_planning_tools(backend=None):
    """
    Create phase-based planning tools with shared workflow state.

    These tools enable the AI Life Coach to:
    - Initialize 4-phase workflows for goal management
    - Manage phase transitions with dependency validation
    - Generate automated milestones from goals
    - Adapt plans based on progress feedback
    - Apply phase-specific output formatting

    Args:
        backend: Optional FilesystemBackend instance. If None, uses get_backend()

    Returns:
        Tuple of phase planning tools (initialize_phase_workflow,
                                      transition_to_next_phase,
                                      generate_milestones_from_goals_tool,
                                      adapt_plan_based_on_progress,
                                      get_phase_status,
                                      apply_phase_template_tool)

    Example:
        >>> from src.config import config
        >>> config.initialize_environment()
        >>> tools = create_phase_planning_tools()
        >>> result = initialize_phase_workflow(
        ...     user_id="user_123",
        ...     goals=[{"title": "Get promotion", "domain": "career"}]
        ... )
    """
    if backend is None:
        backend = get_backend()

    # Get the workspace directory path from backend
    workspace_path = Path(backend.root_dir) if hasattr(backend, "root_dir") else Path("workspace")

    @tool
    def initialize_phase_workflow(
        user_id: str,
        goals: List[Dict[str, Any]],
        start_date: Optional[str] = None,
    ) -> str:
        """Initialize a new 4-phase workflow for goal management.

        This tool creates a structured workflow with the following phases:
        1. Discovery: Assessment, goal identification
        2. Planning: Action plan creation with dependencies
        3. Execution: Task implementation and tracking
        4. Review: Progress evaluation and adaptation

        Args:
            user_id: The user's unique identifier
            goals: List of goal dictionaries, each with:
                   - title (str): Goal description [required]
                   - domain (str): Domain category (career/relationship/finance/wellness) [optional]
                   - description (str): Detailed goal description [optional]
            start_date: Optional ISO format date string for workflow start.
                       If None, uses today's date.

        Returns:
            Confirmation message with phase information and initial milestone generation.
            Workflow saved to phase_planning/{user_id}/

        Example:
            >>> initialize_phase_workflow(
            ...     "user_123",
            ...     [
            ...         {"title": "Get promotion", "domain": "career"},
            ...         {"title": "Improve sleep quality", "domain": "wellness"}
            ...     ],
            ...     start_date="2025-02-01"
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not goals or not isinstance(goals, list):
            return "Error: goals must be a non-empty list"

        try:
            # Parse start date
            if start_date:
                start_dt = datetime.fromisoformat(start_date)
            else:
                start_dt = datetime.now()

            # Create workflow
            workflow = PhaseWorkflow(user_id, goals)

            # Generate initial milestones
            milestones = generate_milestones_from_goals(goals)
            for milestone in milestones:
                workflow.add_milestone(milestone)

            # Estimate phase dates
            phase_dates = estimate_phase_start_dates(start_dt)
            workflow.phase_dates = phase_dates

            # Save to storage
            save_workflow(workflow)

            # Also persist to file
            json_content = json.dumps(workflow.to_dict(), indent=2)
            path = f"phase_planning/{user_id}/workflow.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format response
            lines = [
                f"Phase-Based Workflow Initialized for {user_id}",
                "=" * 60,
                f"\nGoals: {len(goals)}",
            ]
            for i, goal in enumerate(goals, 1):
                domain = goal.get("domain", "general")
                lines.append(f"  {i}. [{domain}] {goal.get('title', 'Untitled')}")

            lines.append(f"\nCurrent Phase: Discovery 🔍")
            lines.append("\n4-Phase Workflow:")
            for phase in Phase.VALID_PHASES:
                info = Phase.get_phase_info(phase)
                lines.append(f"  {phase.capitalize()}: {info['description']}")

            lines.append(f"\nMilestones Generated: {len(milestones)}")
            for milestone in milestones[:5]:  # Show first 5
                lines.append(f"  • {milestone.title} ({milestone.phase})")

            if len(milestones) > 5:
                lines.append(f"  ... and {len(milestones) - 5} more milestones")

            lines.append(f"\nWorkflow saved to: {path}")

            return "\n".join(lines)

        except Exception as e:
            return f"Error initializing phase workflow: {str(e)}"

    @tool
    def transition_to_next_phase(user_id: str) -> str:
        """Transition to the next phase with dependency validation.

        This tool validates that all completion criteria and milestones
        for the current phase are satisfied before allowing transition.

        Args:
            user_id: The user's unique identifier

        Returns:
            Confirmation message with transition status or blocking issues.

        Example:
            >>> transition_to_next_phase("user_123")
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        try:
            workflow = get_workflow(user_id)
            if not workflow:
                return f"Error: No workflow found for user {user_id}. Initialize one first."

            can_transition, blocking_criteria = workflow.can_transition_to_next_phase()

            if not can_transition:
                lines = [
                    f"Cannot transition from {workflow.current_phase.capitalize()} phase",
                    "=" * 60,
                ]

                if blocking_criteria:
                    lines.append("\nBlocking issues:")
                    for criterion in blocking_criteria:
                        lines.append(f"  ❌ {criterion}")

                completion_pct = workflow.get_phase_completion_percentage(workflow.current_phase)
                lines.append(f"\nCurrent phase completion: {completion_pct:.0f}%")

                return "\n".join(lines)

            # Perform transition
            success, message = workflow.transition_to_next_phase()

            if not success:
                return f"Error: {message}"

            # Persist updated workflow
            json_content = json.dumps(workflow.to_dict(), indent=2)
            path = f"phase_planning/{user_id}/workflow.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.write_text(json_content)

            # Format success response
            next_phase_info = Phase.get_phase_info(workflow.current_phase)
            lines = [
                f"✅ Successfully transitioned to {workflow.current_phase.capitalize()} Phase",
                "=" * 60,
            ]

            if next_phase_info:
                lines.append(
                    f"\n{next_phase_info['icon']} {next_phase_info['name']}: {next_phase_info['description']}"
                )
                lines.append(f"Objective: {next_phase_info['objective']}")

            lines.append("\nCompletion Criteria:")
            for criterion in next_phase_info.get("completion_criteria", []):
                lines.append(f"  ⬜ {criterion}")

            return "\n".join(lines)

        except Exception as e:
            return f"Error transitioning phase: {str(e)}"

    @tool
    def generate_milestones_from_goals_tool(
        user_id: str,
        phases: Optional[List[str]] = None,
    ) -> str:
        """Generate automated milestones from goals and phases.

        This tool creates a set of milestones based on:
        - Phase completion checkpoints
        - Goal achievement targets
        - Timeline estimation

        Args:
            user_id: The user's unique identifier
            phases: Optional list of phases to generate milestones for.
                    If None, generates for all phases.

        Returns:
            List of generated milestone details with target dates.

        Example:
            >>> generate_milestones_from_goals_tool("user_123", ["discovery", "planning"])
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        if phases is None:
            phases = Phase.VALID_PHASES
        elif not isinstance(phases, list):
            return "Error: phases must be a list"

        # Validate phase names
        for phase in phases:
            if phase not in Phase.VALID_PHASES:
                return f"Error: Invalid phase '{phase}'. Must be one of {Phase.VALID_PHASES}"

        try:
            workflow = get_workflow(user_id)
            if not workflow:
                return f"Error: No workflow found for user {user_id}. Initialize one first."

            # Generate milestones
            milestones = generate_milestones_from_goals(workflow.goals, phases)

            # Add to workflow if not already present
            for milestone in milestones:
                if milestone.id not in workflow.milestones:
                    workflow.add_milestone(milestone)

            # Persist updated workflow
            json_content = json.dumps(workflow.to_dict(), indent=2)
            path = f"phase_planning/{user_id}/workflow.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.write_text(json_content)

            # Format response
            lines = [
                f"Milestones Generated for {user_id}",
                "=" * 60,
                f"\nTotal Milestones: {len(milestones)}",
            ]

            # Group by phase
            for phase in phases:
                phase_milestones = [m for m in milestones if m.phase == phase]
                if phase_milestones:
                    phase_info = Phase.get_phase_info(phase)
                    lines.append(f"\n{phase_info['icon']} {phase_info['name']} Phase:")
                    for milestone in phase_milestones:
                        lines.append(f"  • {milestone.title}")
                        if milestone.description:
                            lines.append(f"    {milestone.description}")

            return "\n".join(lines)

        except Exception as e:
            return f"Error generating milestones: {str(e)}"

    @tool
    def adapt_plan_based_on_progress(
        user_id: str,
        progress_data: Dict[str, Any],
        apply_recommendations: bool = False,
    ) -> str:
        """Adapt the plan based on progress feedback and analysis.

        This tool analyzes current progress against milestones and completion
        criteria, then provides adaptive recommendations. Optionally applies
        the adaptations to adjust the plan.

        Args:
            user_id: The user's unique identifier
            progress_data: Dictionary containing progress information:
                          - milestone_progress (dict): Milestone ID to status/percentage
                          - goal_progress (dict): Goal ID to percentage complete
                          - notes (str, optional): Additional context about progress
            apply_recommendations: If True, automatically applies recommendations.
                                  If False, only suggests them.

        Returns:
            Analysis of current progress and adaptive recommendations.

        Example:
            >>> adapt_plan_based_on_progress(
            ...     "user_123",
            ...     {
            ...         "milestone_progress": {"ms_1": 75, "ms_2": 30},
            ...         "goal_progress": {"g1": 80, "g2": 40},
            ...         "notes": "Making good progress on career goals"
            ...     },
            ...     apply_recommendations=False
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not progress_data or not isinstance(progress_data, dict):
            return "Error: progress_data must be a dictionary"

        try:
            workflow = get_workflow(user_id)
            if not workflow:
                return f"Error: No workflow found for user {user_id}. Initialize one first."

            # Update milestone statuses based on progress
            if "milestone_progress" in progress_data:
                for mid, progress in progress_data["milestone_progress"].items():
                    if mid in workflow.milestones:
                        milestone = workflow.milestones[mid]
                        if isinstance(progress, (int, float)):
                            if progress >= 100:
                                milestone.status = "completed"
                            elif progress > 0:
                                milestone.status = "in_progress"

            # Calculate adaptive recommendations
            recommendations = calculate_adaptive_recommendations(workflow, progress_data)

            lines = [
                f"Adaptive Planning Analysis for {user_id}",
                "=" * 60,
            ]

            # Show current status
            lines.append(f"\nCurrent Phase: {workflow.current_phase.capitalize()}")
            completion_pct = workflow.get_phase_completion_percentage(workflow.current_phase)
            lines.append(f"Phase Completion: {completion_pct:.0f}%")

            # Show milestone progress
            if workflow.milestones:
                lines.append(f"\n🎯 Milestone Progress ({len(workflow.milestones)} total):")
                for mid, milestone in workflow.milestones.items():
                    progress = progress_data.get("milestone_progress", {}).get(mid, 0)
                    status_icon = {"completed": "✅", "in_progress": "🔄", "delayed": "⚠️"}.get(
                        milestone.status, "⏳"
                    )
                    lines.append(f"  {status_icon} {milestone.title}: {progress}%")

            # Show user notes if provided
            if progress_data.get("notes"):
                lines.append(f"\n📝 Notes:")
                lines.append(f"  {progress_data['notes']}")

            # Show recommendations
            if recommendations:
                lines.append(f"\n💡 Adaptive Recommendations ({len(recommendations)}):")
                for i, rec in enumerate(recommendations, 1):
                    priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                        rec["priority"], "⚪"
                    )
                    lines.append(f"\n  {i}. {priority_icon} {rec['recommendation']}")
                    lines.append(f"     Priority: {rec['priority']} | Reason: {rec['reason']}")

                if apply_recommendations:
                    # Apply recommendations and record adaptations
                    for rec in recommendations:
                        workflow.add_adaptation(rec["reason"], {"recommendation": rec})

                    # Persist updates
                    json_content = json.dumps(workflow.to_dict(), indent=2)
                    path = f"phase_planning/{user_id}/workflow.json"

                    if hasattr(backend, "write_file"):
                        backend.write_file(path, json_content)
                    else:
                        file_path = workspace_path / path
                        file_path.write_text(json_content)

                    lines.append(f"\n✅ {len(recommendations)} adaptation(s) applied to workflow")
            else:
                lines.append("\n✅ No immediate adaptations needed - on track!")

            return "\n".join(lines)

        except Exception as e:
            return f"Error adapting plan: {str(e)}"

    @tool
    def get_phase_status(user_id: str) -> str:
        """Get detailed status of the current phase and all phases.

        This tool provides an overview of:
        - Current phase and its completion progress
        - Completion criteria status for all phases
        - Milestone status across the workflow
        - Transition eligibility

        Args:
            user_id: The user's unique identifier

        Returns:
            Comprehensive status report for the phase workflow.

        Example:
            >>> get_phase_status("user_123")
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        try:
            workflow = get_workflow(user_id)
            if not workflow:
                return f"Error: No workflow found for user {user_id}. Initialize one first."

            lines = [
                f"Phase Workflow Status for {user_id}",
                "=" * 60,
            ]

            # Current phase details
            current_info = Phase.get_phase_info(workflow.current_phase)
            lines.append(f"\n{current_info['icon']} Current Phase: {current_info['name']}")
            lines.append(f"  Description: {current_info['description']}")
            lines.append(f"  Objective: {current_info['objective']}")

            # Phase completion status
            lines.append(f"\n📊 All Phases Status:")
            for phase in Phase.VALID_PHASES:
                info = Phase.get_phase_info(phase)
                completion_pct = workflow.get_phase_completion_percentage(phase)

                if phase == workflow.current_phase:
                    lines.append(
                        f"\n  {info['icon']} {info['name']} (CURRENT) - {completion_pct:.0f}%"
                    )
                else:
                    lines.append(f"\n  ⏪ {info['name']} - {completion_pct:.0f}%")

                # Show completion criteria
                for criterion, completed in workflow.phase_completion[phase].items():
                    status_icon = "✅" if completed else "⬜"
                    lines.append(f"    {status_icon} {criterion}")

            # Transition eligibility
            can_transition, blocking = workflow.can_transition_to_next_phase()
            lines.append(f"\n{'=' * 60}")
            if workflow.current_phase == "review":
                lines.append("\n🏁 Workflow in final phase - no further transitions")
            elif can_transition:
                lines.append("\n✅ Ready to transition to next phase")
                next_phase = Phase.get_next_phase(workflow.current_phase)
                if next_phase:
                    lines.append(f"   Next phase: {next_phase}")
            else:
                lines.append("\n⚠️ Not ready to transition")
                if blocking:
                    lines.append("   Blocking issues:")
                    for issue in blocking:
                        lines.append(f"     • {issue}")

            # Milestone summary
            if workflow.milestones:
                lines.append(f"\n{'=' * 60}")
                lines.append(f"\n🎯 Milestone Summary ({len(workflow.milestones)} total):")
                status_counts = {"pending": 0, "in_progress": 0, "completed": 0, "delayed": 0}
                for milestone in workflow.milestones.values():
                    status_counts[milestone.status] += 1

                lines.append(f"  ⏳ Pending: {status_counts['pending']}")
                lines.append(f"  🔄 In Progress: {status_counts['in_progress']}")
                lines.append(f"  ✅ Completed: {status_counts['completed']}")
                if status_counts["delayed"] > 0:
                    lines.append(f"  ⚠️ Delayed: {status_counts['delayed']}")

            # Phase history
            if workflow.phase_history:
                lines.append(f"\n{'=' * 60}")
                lines.append("\n📜 Phase Transition History:")
                for transition in workflow.phase_history:
                    from_phase = transition["from_phase"].capitalize()
                    to_phase = transition["to_phase"].capitalize()
                    timestamp = datetime.fromisoformat(transition["timestamp"]).strftime(
                        "%Y-%m-%d %H:%M"
                    )
                    lines.append(f"  {timestamp}: {from_phase} → {to_phase}")

            return "\n".join(lines)

        except Exception as e:
            return f"Error getting phase status: {str(e)}"

    @tool
    def apply_phase_template_tool(
        user_id: str,
        phase: Optional[str] = None,
    ) -> str:
        """Apply phase-specific output formatting template.

        This tool generates a formatted view of the phase workflow using
        templates tailored to each phase's characteristics.

        Args:
            user_id: The user's unique identifier
            phase: Optional phase name to format. If None, uses current phase.

        Returns:
            Formatted phase view with status, deliverables, and milestones.

        Example:
            >>> apply_phase_template_tool("user_123", phase="planning")
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        try:
            workflow = get_workflow(user_id)
            if not workflow:
                return f"Error: No workflow found for user {user_id}. Initialize one first."

            # Determine which phase to format
            target_phase = phase or workflow.current_phase

            if target_phase not in Phase.VALID_PHASES:
                return f"Error: Invalid phase '{target_phase}'. Must be one of {Phase.VALID_PHASES}"

            # Get phase info
            phase_info = Phase.get_phase_info(target_phase)
            if not phase_info:
                return f"Error: No configuration found for phase '{target_phase}'"

            # Build content dictionary
            completion_pct = workflow.get_phase_completion_percentage(target_phase)
            phase_milestones = [
                m.to_dict() for m in workflow.milestones.values() if m.phase == target_phase
            ]

            content = {
                "status": {
                    "Completion Percentage": f"{completion_pct:.0f}%",
                    "Total Milestones in Phase": len(phase_milestones),
                },
                "completion_criteria": workflow.phase_completion[target_phase],
                "deliverables": phase_info["deliverables"],
                "milestones": phase_milestones,
            }

            # Apply template
            return apply_phase_template(target_phase, content)

        except Exception as e:
            return f"Error applying phase template: {str(e)}"

    print("Phase planning tools created successfully!")
    return (
        initialize_phase_workflow,
        transition_to_next_phase,
        generate_milestones_from_goals_tool,
        adapt_plan_based_on_progress,
        get_phase_status,
        apply_phase_template_tool,
    )


# Export tools at module level for convenience
__all__ = [
    "create_phase_planning_tools",
    "Phase",
    "Milestone",
    "PhaseWorkflow",
]
