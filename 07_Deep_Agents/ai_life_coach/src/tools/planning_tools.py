"""
Planning tools for AI Life Coach.

This module provides LangChain tools that enable agents to create and manage
structured todo lists with phase-based organization, dependency tracking,
and progress monitoring. The system supports four phases (discovery, planning,
execution, review) and prevents circular dependencies.

Tools:
- write_todos: Create or replace a complete todo list with phases and dependencies
- update_todo: Update individual todo items (status, notes) while tracking dependencies
- list_todos: Display todos with phase filtering and dependency status

The todo system uses a centralized manager to maintain state and validate
dependencies across operations.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime

# Import LangChain components
try:
    from langchain_core.tools import tool
except ImportError:
    # Fallback for development environments without full LangChain
    def tool(func):
        """Fallback decorator when langchain_core is not available."""
        func.is_tool = True  # type: ignore
        return func


# ==============================================================================
# Data Models for Todo System
# ==============================================================================


class TodoItem:
    """
    Represents a single todo item in the planning system.

    Attributes:
        title: Brief description of the task
        phase: One of "discovery", "planning", "execution", or "review"
        status: Current state - "pending", "in_progress", or "completed"
        depends_on: List of todo IDs this task depends on (must be completed first)
        notes: Additional context or comments about the task
        created_at: ISO timestamp when todo was created
        completed_at: ISO timestamp when todo was marked completed
    """

    VALID_PHASES = {"discovery", "planning", "execution", "review"}
    VALID_STATUSES = {"pending", "in_progress", "completed"}

    def __init__(
        self,
        title: str,
        phase: str = "discovery",
        status: str = "pending",
        depends_on: Optional[List[str]] = None,
        notes: Optional[str] = None,
        created_at: Optional[str] = None,
        completed_at: Optional[str] = None,
    ):
        """Initialize a TodoItem with validation."""
        if not title or not isinstance(title, str):
            raise ValueError("title must be a non-empty string")

        if phase not in self.VALID_PHASES:
            raise ValueError(f"phase must be one of {self.VALID_PHASES}, got '{phase}'")

        if status not in self.VALID_STATUSES:
            raise ValueError(f"status must be one of {self.VALID_STATUSES}, got '{status}'")

        self.title = title
        self.phase = phase
        self.status = status
        self.depends_on = depends_on or []
        self.notes = notes or ""
        self.created_at = created_at or datetime.now().isoformat()
        self.completed_at = completed_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert todo item to dictionary representation."""
        return {
            "title": self.title,
            "phase": self.phase,
            "status": self.status,
            "depends_on": self.depends_on,
            "notes": self.notes,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TodoItem":
        """Create TodoItem from dictionary."""
        return cls(
            title=data.get("title", ""),
            phase=data.get("phase", "discovery"),
            status=data.get("status", "pending"),
            depends_on=data.get("depends_on", []),
            notes=data.get("notes", ""),
            created_at=data.get("created_at"),
            completed_at=data.get("completed_at"),
        )


class TodoManager:
    """
    Manages todo list state with dependency tracking and validation.

    This class maintains the complete todo list, validates dependencies,
    prevents circular references, and provides query capabilities.
    """

    def __init__(self):
        """Initialize an empty todo manager."""
        self.todos: List[TodoItem] = []

    def set_todos(self, todo_data_list: List[Dict[str, Any]]) -> str:
        """
        Replace all todos with a new list after validation.

        Args:
            todo_data_list: List of dictionaries representing todo items

        Returns:
            Confirmation message with count and any validation errors

        Raises:
            ValueError: If circular dependencies are detected
        """
        # Convert dictionaries to TodoItem objects
        new_todos = []
        for i, data in enumerate(todo_data_list):
            try:
                todo = TodoItem.from_dict(data)
                new_todos.append(todo)
            except ValueError as e:
                return f"Error in todo item {i}: {str(e)}"

        # Validate for circular dependencies
        cycle_error = self._detect_circular_dependencies(new_todos)
        if cycle_error:
            raise ValueError(cycle_error)

        # All validations passed - replace todos
        self.todos = new_todos

        return f"Successfully created {len(self.todos)} todos across {self._count_phases()} phases"

    def update_todo(
        self, todo_id: int, status: Optional[str] = None, notes: Optional[str] = None
    ) -> str:
        """
        Update a specific todo item by ID.

        Args:
            todo_id: Index of the todo to update (0-based)
            status: New status if updating
            notes: Additional notes to append

        Returns:
            Confirmation message or error description
        """
        # Validate todo_id exists
        if todo_id < 0 or todo_id >= len(self.todos):
            return f"Error: Invalid todo_id {todo_id}. Valid range: 0-{len(self.todos) - 1}"

        todo = self.todos[todo_id]

        # Update status if provided
        if status:
            if status not in TodoItem.VALID_STATUSES:
                return f"Error: Invalid status '{status}'. Must be one of {TodoItem.VALID_STATUSES}"

            # Check if dependencies are satisfied before allowing in_progress or completed
            if status in ("in_progress", "completed"):
                blocking_deps = self._get_blocking_dependencies(todo_id)
                if blocking_deps:
                    dep_titles = [self.todos[dep_id].title for dep_id in blocking_deps]
                    return (
                        f"Cannot set '{todo.title}' to {status} because "
                        f"it depends on incomplete tasks: {', '.join(dep_titles)}"
                    )

            todo.status = status
            if status == "completed" and not todo.completed_at:
                todo.completed_at = datetime.now().isoformat()

        # Append notes if provided
        if notes:
            if todo.notes:
                todo.notes += f"\n{notes}"
            else:
                todo.notes = notes

        return f"Updated todo '{todo.title}' (status: {todo.status})" + (
            f", notes added" if notes else ""
        )

    def list_todos(self, phase: Optional[str] = None, status: Optional[str] = None) -> str:
        """
        Get formatted list of todos with optional filtering.

        Args:
            phase: Filter by phase (discovery, planning, execution, review)
            status: Filter by status (pending, in_progress, completed)

        Returns:
            Formatted string representation of filtered todos
        """
        # Apply filters
        filtered_todos = self._filter_todos(phase, status)

        if not filtered_todos:
            filter_desc = []
            if phase:
                filter_desc.append(f"phase={phase}")
            if status:
                filter_desc.append(f"status={status}")

            filter_str = f" ({', '.join(filter_desc)})" if filter_desc else ""
            return f"No todos found{filter_str}"

        # Build formatted output
        lines = []

        # Group by phase for better organization
        phases_in_order = ["discovery", "planning", "execution", "review"]
        for current_phase in phases_in_order:
            phase_todos = [
                (i, todo) for i, todo in enumerate(filtered_todos) if todo.phase == current_phase
            ]

            if phase_todos:
                # Calculate original index for each todo
                lines.append(f"\n## {current_phase.capitalize()} Phase ({len(phase_todos)} items)")

                for original_idx, todo in phase_todos:
                    # Find the actual index in self.todos
                    actual_idx = self.todos.index(todo)

                    status_icon = {
                        "pending": "⏳",
                        "in_progress": "🔄",
                        "completed": "✅",
                    }.get(todo.status, "❓")

                    lines.append(f"\n  [{actual_idx}] {status_icon} {todo.title}")

                    if todo.notes:
                        lines.append(f"      Notes: {todo.notes}")

                    # Show dependency status
                    if todo.depends_on:
                        completed_deps = sum(
                            1
                            for dep_id in todo.depends_on
                            if 0 <= dep_id < len(self.todos)
                            and self.todos[dep_id].status == "completed"
                        )
                        total_deps = len(todo.depends_on)
                        dep_status = f"Dependencies: {completed_deps}/{total_deps} completed"
                        lines.append(f"      {dep_status}")

        return "\n".join(lines)

    def _filter_todos(self, phase: Optional[str], status: Optional[str]) -> List[TodoItem]:
        """Apply phase and status filters to todo list."""
        filtered = self.todos

        if phase:
            if phase not in TodoItem.VALID_PHASES:
                raise ValueError(f"Invalid phase '{phase}'")
            filtered = [t for t in filtered if t.phase == phase]

        if status:
            if status not in TodoItem.VALID_STATUSES:
                raise ValueError(f"Invalid status '{status}'")
            filtered = [t for t in filtered if t.status == status]

        return filtered

    def _count_phases(self) -> Dict[str, int]:
        """Count todos per phase."""
        counts = {phase: 0 for phase in TodoItem.VALID_PHASES}
        for todo in self.todos:
            counts[todo.phase] += 1
        return {k: v for k, v in counts.items() if v > 0}

    def _detect_circular_dependencies(self, todos: List[TodoItem]) -> Optional[str]:
        """
        Detect circular dependencies using DFS.

        Args:
            todos: List of TodoItem objects to validate

        Returns:
            Error message if cycle detected, None otherwise
        """
        n = len(todos)
        visited = [False] * n
        rec_stack = [False] * n

        def dfs(node: int, path: List[int]) -> Optional[str]:
            """DFS traversal to detect cycles."""
            visited[node] = True
            rec_stack[node] = True
            path.append(node)

            # Check all dependencies
            for dep_idx in todos[node].depends_on:
                if not (0 <= dep_idx < n):
                    continue  # Invalid dependency reference, skip

                if not visited[dep_idx]:
                    cycle = dfs(dep_idx, path)
                    if cycle:
                        return cycle
                elif rec_stack[dep_idx]:
                    # Cycle detected - build helpful error message
                    cycle_start = path.index(dep_idx)
                    cycle_nodes = path[cycle_start:] + [dep_idx]
                    titles = [f"[{idx}] {todos[idx].title}" for idx in cycle_nodes]
                    return (
                        "Circular dependency detected: "
                        + " -> ".join(titles)
                        + f"\nTask '{todos[node].title}' depends on task [{dep_idx}] "
                        f"'{todos[dep_idx].title}', which ultimately depends back on task [{node}]."
                    )

            path.pop()
            rec_stack[node] = False
            return None

        # Check all nodes (graph may be disconnected)
        for i in range(n):
            if not visited[i]:
                cycle = dfs(i, [])
                if cycle:
                    return cycle

        return None

    def _get_blocking_dependencies(self, todo_idx: int) -> List[int]:
        """
        Get list of dependency indices that are not yet completed.

        Args:
            todo_idx: Index of todo to check

        Returns:
            List of indices of incomplete dependencies
        """
        blocking = []
        todo = self.todos[todo_idx]

        for dep_id in todo.depends_on:
            if 0 <= dep_id < len(self.todos):
                dep_todo = self.todos[dep_id]
                if dep_todo.status != "completed":
                    blocking.append(dep_id)

        return blocking


# ==============================================================================
# Global Todo Manager Instance
# ==============================================================================

_global_todo_manager = TodoManager()


def get_todo_manager() -> TodoManager:
    """Get the global todo manager instance."""
    return _global_todo_manager


# ==============================================================================
# Planning Tool Factory
# ==============================================================================


def create_planning_tools() -> tuple:
    """
    Create planning tools with shared TodoManager state.

    Returns:
        Tuple of planning tools (write_todos, update_todo, list_todos)

    Example:
        >>> write_todos, update_todo, list_todos = create_planning_tools()
        >>> result = write_todos.invoke([{"title": "Assess current situation", "phase": "discovery"}])
    """
    todo_manager = get_todo_manager()

    @tool
    def write_todos(todos: List[Dict[str, Any]]) -> str:
        """Create or replace the complete todo list with phases and dependencies.

        This tool replaces all existing todos with a new structured list.
        Each todo can be assigned to one of four phases and can depend on
        other todos by their index. Circular dependencies are automatically
        detected and rejected.

        Args:
            todos: List of todo dictionaries, each with:
                - title (str): Brief description of the task [required]
                - phase (str): One of "discovery", "planning", "execution", or "review" [default: "discovery"]
                - status (str): One of "pending", "in_progress", or "completed" [default: "pending"]
                - depends_on (list[int]): List of todo indices this task depends on [default: []]
                - notes (str): Additional context about the task [optional]

        Returns:
            Confirmation message with count of todos created. If validation fails,
            returns a descriptive error message.

        Raises:
            ValueError: If circular dependencies are detected

        Example:
            >>> write_todos([
            ...     {"title": "Initial life assessment", "phase": "discovery"},
            ...     {"title": "Identify top 3 priorities", "phase": "discovery", "depends_on": [0]},
            ...     {"title": "Create 90-day action plan", "phase": "planning", "depends_on": [1]},
            ...     {"title": "Weekly check-in system", "phase": "execution"}
            ... ])
        """
        try:
            return todo_manager.set_todos(todos)
        except ValueError as e:
            return f"Validation error: {str(e)}"
        except Exception as e:
            return f"Error creating todos: {str(e)}"

    @tool
    def update_todo(todo_id: int, status: Optional[str] = None, notes: Optional[str] = None) -> str:
        """Update a specific todo item's status or add notes.

        This tool updates individual todos while respecting dependency constraints.
        A todo cannot be marked in_progress or completed until all its dependencies
        are completed. Notes can be added at any time.

        Args:
            todo_id: Index of the todo to update (0-based, matches list_todos output)
            status: New status if updating - one of "pending", "in_progress", or "completed" [optional]
            notes: Additional notes to append to the todo (can add without changing status) [optional]

        Returns:
            Confirmation message indicating what was updated. If dependencies block
            the status change, returns a descriptive error message listing incomplete tasks.

        Example:
            >>> update_todo(0, status="in_progress")
            'Updated todo "Initial life assessment" (status: in_progress)'
            >>> update_todo(1, notes="Added research about career paths")
            'Updated todo "Identify top 3 priorities" (status: pending, notes added)'
        """
        try:
            return todo_manager.update_todo(todo_id, status, notes)
        except Exception as e:
            return f"Error updating todo {todo_id}: {str(e)}"

    @tool
    def list_todos(phase: Optional[str] = None, status: Optional[str] = None) -> str:
        """Display todos with optional phase and status filtering.

        This tool lists all todos or a filtered subset. Todos are grouped by
        phase for better organization. Each todo shows its status icon, notes,
        and dependency completion progress.

        Args:
            phase: Optional filter by phase - one of "discovery", "planning",
                   "execution", or "review" [default: show all phases]
            status: Optional filter by status - one of "pending", "in_progress",
                    or "completed" [default: show all statuses]

        Returns:
            Formatted todo list with phase headings and status indicators.
            Status icons: ⏳ pending, 🔄 in_progress, ✅ completed

        Example:
            >>> list_todos()
            '## Discovery Phase (2 items):
              [0] ⏳ Initial life assessment
                  Dependencies: 0/1 completed

            ## Planning Phase (1 items):
              [1] ⏳ Create 90-day action plan'

            >>> list_todos(phase="execution", status="pending")
        """
        try:
            return todo_manager.list_todos(phase, status)
        except ValueError as e:
            return f"Filter error: {str(e)}"
        except Exception as e:
            return f"Error listing todos: {str(e)}"

    print("Planning tools created successfully!")
    return write_todos, update_todo, list_todos


# Export tools at module level for convenience
__all__ = [
    "create_planning_tools",
    "TodoItem",
    "TodoManager",
]
