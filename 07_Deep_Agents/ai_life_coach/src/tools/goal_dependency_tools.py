"""
Goal Dependency Mapping Tools for AI Life Coach.

This module provides advanced tools for modeling, analyzing, and visualizing
goal dependencies using Directed Acyclic Graphs (DAGs).

Tools:
- build_goal_dependency_graph: Create dependency graph with cycle detection
- detect_implicit_dependencies: Auto-detect potential dependencies between goals
- simulate_goal_impact: Propagate impact of goal success/failure through graph
- visualize_dependency_graph: Generate text-based visualization of dependencies
- find_critical_path: Identify critical path for goal achievement
- suggest_dependency_resolutions: Resolve circular dependencies and conflicts

Based on research in:
- Goal dependency graph algorithms (DAGs, topological sorting)
- Critical path analysis for project planning
- Impact propagation in dependency networks
- Conflict resolution strategies
"""

from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
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
# Data Structures for Goal Dependency Graph
# ==============================================================================


class GoalNode:
    """Represents a single goal in the dependency graph."""

    def __init__(
        self,
        id: str,
        domain: str,
        title: str,
        priority: int = 5,  # 1-10 scale
        status: str = "pending",  # pending, in_progress, completed
        estimated_effort: Optional[float] = None,  # Hours or days to complete
        deadline: Optional[str] = None,  # ISO format date string
    ):
        self.id = id
        self.domain = domain  # career, relationship, finance, wellness
        self.title = title
        self.priority = priority
        self.status = status
        self.estimated_effort = estimated_effort
        self.deadline = deadline

    def to_dict(self) -> Dict[str, Any]:
        """Convert goal node to dictionary."""
        return {
            "id": self.id,
            "domain": self.domain,
            "title": self.title,
            "priority": self.priority,
            "status": self.status,
            "estimated_effort": self.estimated_effort,
            "deadline": self.deadline,
        }


class DependencyEdge:
    """Represents a relationship between two goals."""

    def __init__(
        self,
        from_goal_id: str,
        to_goal_id: str,
        relationship_type: str,  # enables, requires, conflicts, supports
        strength: float = 1.0,  # 0-1 scale for impact strength
        reason: Optional[str] = None,
    ):
        self.from_goal_id = from_goal_id
        self.to_goal_id = to_goal_id
        # Relationship type determines directionality:
        # - enables: from_goal helps achieve to_goal (positive)
        # - requires: from_goal must happen for to_goal (strong positive)
        # - conflicts: goals compete for resources (negative)
        # - supports: from_goal helps but isn't required (weak positive)
        self.relationship_type = relationship_type
        self.strength = strength
        self.reason = reason

    def to_dict(self) -> Dict[str, Any]:
        """Convert dependency edge to dictionary."""
        return {
            "from_goal_id": self.from_goal_id,
            "to_goal_id": self.to_goal_id,
            "relationship_type": self.relationship_type,
            "strength": self.strength,
            "reason": self.reason,
        }


class GoalDependencyGraph:
    """Directed Acyclic Graph (DAG) representing goal dependencies."""

    def __init__(self):
        self.nodes: Dict[str, GoalNode] = {}
        self.edges: List[DependencyEdge] = []

    def add_goal(self, goal: GoalNode) -> None:
        """Add a goal node to the graph."""
        self.nodes[goal.id] = goal

    def add_dependency(self, edge: DependencyEdge) -> None:
        """Add a dependency edge to the graph."""
        self.edges.append(edge)

    def remove_goal(self, goal_id: str) -> None:
        """Remove a goal and all its edges from the graph."""
        if goal_id in self.nodes:
            del self.nodes[goal_id]
            # Remove all edges involving this goal
            self.edges = [
                e for e in self.edges if e.from_goal_id != goal_id and e.to_goal_id != goal_id
            ]

    def update_goal(self, goal_id: str, **kwargs) -> None:
        """Update goal attributes."""
        if goal_id in self.nodes:
            for key, value in kwargs.items():
                setattr(self.nodes[goal_id], key, value)

    def get_dependencies(
        self, goal_id: str, relationship_type: Optional[str] = None
    ) -> List[DependencyEdge]:
        """Get all dependencies for a goal, optionally filtered by type."""
        deps = [e for e in self.edges if e.to_goal_id == goal_id]
        if relationship_type:
            deps = [e for e in deps if e.relationship_type == relationship_type]
        return deps

    def get_dependents(
        self, goal_id: str, relationship_type: Optional[str] = None
    ) -> List[DependencyEdge]:
        """Get all goals that depend on this goal."""
        deps = [e for e in self.edges if e.from_goal_id == goal_id]
        if relationship_type:
            deps = [e for e in deps if e.relationship_type == relationship_type]
        return deps

    def detect_cycles(self) -> List[List[str]]:
        """Detect cycles in the dependency graph using DFS."""
        WHITE, GRAY, BLACK = 0, 1, 2
        color: Dict[str, int] = {node_id: WHITE for node_id in self.nodes}
        cycles: List[List[str]] = []
        path: List[str] = []

        def dfs(node_id: str):
            color[node_id] = GRAY
            path.append(node_id)

            # Check all outgoing edges (goals this goal enables/requires)
            for edge in self.get_dependents(node_id):
                if edge.relationship_type not in ["enables", "requires"]:
                    continue  # Only check positive dependencies for cycles

                if color[edge.to_goal_id] == GRAY:
                    # Found a cycle
                    cycle_start = path.index(edge.to_goal_id)
                    cycles.append(path[cycle_start:] + [edge.to_goal_id])
                elif color[edge.to_goal_id] == WHITE:
                    dfs(edge.to_goal_id)

            path.pop()
            color[node_id] = BLACK

        for node_id in self.nodes:
            if color[node_id] == WHITE:
                dfs(node_id)

        return cycles

    def topological_sort(self) -> List[str]:
        """Return goals in topological order (dependencies first)."""
        # Check for cycles
        cycles = self.detect_cycles()
        if cycles:
            raise ValueError(f"Cannot perform topological sort with cycles: {cycles}")

        # Kahn's algorithm
        in_degree = {node_id: 0 for node_id in self.nodes}
        adjacency_list: Dict[str, List[str]] = {node_id: [] for node_id in self.nodes}

        # Build adjacency list and in-degree counts
        for edge in self.edges:
            if edge.relationship_type not in ["enables", "requires"]:
                continue
            adjacency_list[edge.from_goal_id].append(edge.to_goal_id)
            in_degree[edge.to_goal_id] += 1

        # Find nodes with no incoming edges
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            node_id = queue.pop(0)
            result.append(node_id)

            for neighbor in adjacency_list[node_id]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        return result

    def find_critical_path(self) -> Tuple[List[str], float]:
        """
        Find the critical path for goal achievement.

        The critical path is the longest path through the DAG when considering
        estimated effort. It represents the minimum time needed to complete all goals.

        Returns:
            Tuple of (list of goal IDs in critical path, total effort)
        """
        # Check for cycles first
        cycles = self.detect_cycles()
        if cycles:
            raise ValueError(f"Cannot find critical path with cycles: {cycles}")

        # Build adjacency list for positive dependencies
        adj_list = {node_id: [] for node_id in self.nodes}
        for edge in self.edges:
            if edge.relationship_type in ["enables", "requires"]:
                adj_list[edge.from_goal_id].append(edge.to_goal_id)

        # Use DFS to find all paths and their total effort
        def dfs(node_id: str, visited: Set[str]) -> Tuple[List[str], float]:
            visited.add(node_id)
            max_path = [node_id]
            max_effort = self.nodes[node_id].estimated_effort or 1.0

            for neighbor in adj_list[node_id]:
                if neighbor not in visited:
                    path, effort = dfs(neighbor, visited.copy())
                    total_effort = max_effort + effort
                    if total_effort > max_effort:
                        max_path = [node_id] + path
                        max_effort = total_effort

            return max_path, max_effort

        # Find the critical path from all source nodes
        critical_path = []
        max_total_effort = 0.0

        for node_id in self.nodes:
            # Check if it's a source node (no incoming positive dependencies)
            has_incoming = any(
                e.to_goal_id == node_id
                for e in self.edges
                if e.relationship_type in ["enables", "requires"]
            )
            if not has_incoming:
                path, effort = dfs(node_id, set())
                if effort > max_total_effort:
                    critical_path = path
                    max_total_effort = effort

        return critical_path, max_total_effort

    def simulate_impact(self, goal_id: str, outcome: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Simulate the impact of a goal outcome on dependent goals.

        Args:
            goal_id: The ID of the goal that succeeded/failed
            outcome: 'success' or 'failure'

        Returns:
            Dictionary with affected goals and impact details
        """
        affected_goals: Dict[str, List[Dict[str, Any]]] = {
            "positively_affected": [],
            "negatively_affected": [],
            "blocked": [],
        }

        # BFS to propagate impact
        queue = [(goal_id, 1.0)]  # (node_id, impact_strength)
        visited = {goal_id}

        while queue:
            current_id, current_impact = queue.pop(0)

            # Get all goals that depend on this one
            for edge in self.get_dependents(current_id):
                if edge.to_goal_id in visited:
                    continue

                # Calculate impact based on relationship type and strength
                if outcome == "success":
                    if edge.relationship_type in ["enables", "requires"]:
                        # Success helps dependent goals
                        impact = {
                            "goal_id": edge.to_goal_id,
                            "title": self.nodes[edge.to_goal_id].title,
                            "impact_type": "positive",
                            "strength": current_impact * edge.strength,
                            "reason": f"{self.nodes[current_id].title} succeeded, which {edge.relationship_type} this goal",
                        }
                        affected_goals["positively_affected"].append(impact)
                    elif edge.relationship_type == "conflicts":
                        # Success may conflict with dependent goals
                        impact = {
                            "goal_id": edge.to_goal_id,
                            "title": self.nodes[edge.to_goal_id].title,
                            "impact_type": "negative",
                            "strength": current_impact * edge.strength,
                            "reason": f"{self.nodes[current_id].title} succeeded, creating conflict with this goal",
                        }
                        affected_goals["negatively_affected"].append(impact)
                    elif edge.relationship_type == "supports":
                        impact = {
                            "goal_id": edge.to_goal_id,
                            "title": self.nodes[edge.to_goal_id].title,
                            "impact_type": "positive",
                            "strength": current_impact * edge.strength * 0.5,
                            "reason": f"{self.nodes[current_id].title} succeeded, supporting this goal",
                        }
                        affected_goals["positively_affected"].append(impact)
                else:  # failure
                    if edge.relationship_type == "requires":
                        # Failure blocks required goals
                        impact = {
                            "goal_id": edge.to_goal_id,
                            "title": self.nodes[edge.to_goal_id].title,
                            "impact_type": "blocked",
                            "strength": current_impact * edge.strength,
                            "reason": f"{self.nodes[current_id].title} failed, which is required for this goal",
                        }
                        affected_goals["blocked"].append(impact)
                    elif edge.relationship_type in ["enables", "supports"]:
                        # Failure makes enabled/supported goals harder
                        impact = {
                            "goal_id": edge.to_goal_id,
                            "title": self.nodes[edge.to_goal_id].title,
                            "impact_type": "negative",
                            "strength": current_impact * edge.strength * 0.5,
                            "reason": f"{self.nodes[current_id].title} failed, making this goal harder",
                        }
                        affected_goals["negatively_affected"].append(impact)

                visited.add(edge.to_goal_id)
                queue.append((edge.to_goal_id, current_impact * edge.strength))

        return affected_goals

    def to_dict(self) -> Dict[str, Any]:
        """Convert graph to dictionary representation."""
        node_dicts = [node.to_dict() for node in self.nodes.values()]
        edge_dicts = [edge.to_dict() for edge in self.edges]

        return {
            "nodes": node_dicts,
            "edges": edge_dicts,
        }


# ==============================================================================
# Helper Functions
# ==============================================================================


def suggest_conflict_resolution(
    goal1: GoalNode, goal2: GoalNode, edge: DependencyEdge
) -> List[str]:
    """Suggest resolution strategies for conflicting goals."""
    resolutions = []

    # Strategy 1: Prioritize based on priority
    if goal1.priority > goal2.priority:
        resolutions.append(
            f"Consider deprioritizing '{goal2.title}' (P{goal2.priority}) in favor of '{goal1.title}' (P{goal1.priority})"
        )
    elif goal2.priority > goal1.priority:
        resolutions.append(
            f"Consider deprioritizing '{goal1.title}' (P{goal1.priority}) in favor of '{goal2.title}' (P{goal2.priority})"
        )

    # Strategy 2: Sequential execution
    resolutions.append(
        f"Try completing '{goal1.title}' first, then focus on '{goal2.title}' to avoid resource competition"
    )

    # Strategy 3: Deadlines
    if goal1.deadline and goal2.deadline:
        resolutions.append(
            f"Both have deadlines ({goal1.deadline} and {goal2.deadline}), consider extending one or adjusting timelines"
        )
    elif goal1.deadline:
        resolutions.append(
            f"'{goal1.title}' has deadline {goal1.deadline}, prioritize it and defer '{goal2.title}'"
        )
    elif goal2.deadline:
        resolutions.append(
            f"'{goal2.title}' has deadline {goal2.deadline}, prioritize it and defer '{goal1.title}'"
        )

    # Strategy 4: Resource analysis
    if edge.reason:
        resolutions.append(
            f"Conflict reason: {edge.reason}. Consider allocating dedicated time blocks for each goal"
        )

    # Strategy 5: Integration
    resolutions.append(
        f"Look for ways to integrate these goals - can progress on one help with the other?"
    )

    return resolutions


def detect_implicit_dependencies(
    goals: List[GoalNode], existing_edges: List[DependencyEdge]
) -> List[Dict[str, Any]]:
    """
    Detect potential implicit dependencies between goals.

    Analyzes goals for patterns that suggest relationships not explicitly marked:
    - Same domain with overlapping keywords
    - Complementary domains (e.g., career-finance)
    - Temporal sequences implied by deadlines

    Args:
        goals: List of goal nodes
        existing_edges: Existing dependency edges to avoid duplicates

    Returns:
        List of suggested dependencies with confidence scores
    """
    suggestions = []

    # Build keyword sets for each goal
    goal_keywords: Dict[str, Set[str]] = {}
    for goal in goals:
        words = set(goal.title.lower().split())
        # Remove common stop words
        stop_words = {"a", "an", "the", "and", "or", "but", "to", "for", "with"}
        goal_keywords[goal.id] = words - stop_words

    # Check for keyword overlaps
    for i, goal1 in enumerate(goals):
        for j, goal2 in enumerate(goals):
            if i >= j:
                continue  # Avoid duplicates and self-comparison

            # Check for existing relationship
            has_existing = any(
                (e.from_goal_id == goal1.id and e.to_goal_id == goal2.id)
                or (e.from_goal_id == goal2.id and e.to_goal_id == goal1.id)
                for e in existing_edges
            )
            if has_existing:
                continue

            # Keyword overlap analysis
            common_keywords = goal_keywords[goal1.id] & goal_keywords[goal2.id]
            overlap_ratio = len(common_keywords) / max(
                len(goal_keywords[goal1.id]), len(goal_keywords[goal2.id])
            )

            if overlap_ratio > 0.3:
                suggestions.append(
                    {
                        "from_goal_id": goal1.id,
                        "to_goal_id": goal2.id,
                        "relationship_type": "supports",
                        "confidence": round(overlap_ratio, 2),
                        "reason": f"Shared keywords: {', '.join(common_keywords)}",
                    }
                )

            # Complementary domain analysis
            complementary_pairs = [
                ("career", "finance"),
                ("wellness", "career"),
                ("relationship", "wellness"),
            ]
            domain_pair = tuple(sorted([goal1.domain, goal2.domain]))
            if domain_pair in complementary_pairs:
                suggestions.append(
                    {
                        "from_goal_id": goal1.id,
                        "to_goal_id": goal2.id,
                        "relationship_type": "supports",
                        "confidence": 0.6,
                        "reason": f"Complementary domains: {goal1.domain} and {goal2.domain}",
                    }
                )

            # Deadline-based temporal sequence
            if goal1.deadline and goal2.deadline:
                deadline1 = datetime.fromisoformat(goal1.deadline)
                deadline2 = datetime.fromisoformat(goal2.deadline)
                if deadline1 < deadline2:
                    suggestions.append(
                        {
                            "from_goal_id": goal1.id,
                            "to_goal_id": goal2.id,
                            "relationship_type": "enables",
                            "confidence": 0.5,
                            "reason": f"Temporal sequence: Goal 1 deadline ({goal1.deadline}) before Goal 2 ({goal2.deadline})",
                        }
                    )

    return suggestions


def visualize_dependency_graph_text(
    graph: GoalDependencyGraph, focus_goal_id: Optional[str] = None
) -> str:
    """
    Generate text-based visualization of the dependency graph.

    Args:
        graph: The goal dependency graph
        focus_goal_id: Optional ID of a goal to highlight and show its immediate dependencies

    Returns:
        Text-based visualization of the graph
    """
    lines = []
    lines.append("╔" + "═" * 78 + "╗")
    lines.append("║" + " GOAL DEPENDENCY GRAPH ".center(78) + "║")
    lines.append("╚" + "═" * 78 + "╝")
    lines.append("")

    if focus_goal_id and focus_goal_id in graph.nodes:
        # Focused view: show only the goal and its immediate dependencies
        focus_goal = graph.nodes[focus_goal_id]
        lines.append(f"Focused View: {focus_goal.title}")
        lines.append("─" * 80)
        lines.append("")

        # Dependencies (what this goal needs)
        deps = graph.get_dependencies(focus_goal_id)
        if deps:
            lines.append("Dependencies (required for this goal):")
            for edge in deps:
                dep_goal = graph.nodes.get(edge.from_goal_id)
                if dep_goal:
                    icon = "⚠" if edge.relationship_type == "conflicts" else "✓"
                    lines.append(f"  {icon} [{dep_goal.domain}] {dep_goal.title}")
                    lines.append(
                        f"     Type: {edge.relationship_type} | Strength: {edge.strength:.1f}"
                    )
                    if edge.reason:
                        lines.append(f"     Reason: {edge.reason}")
        else:
            lines.append("No dependencies for this goal")
        lines.append("")

        # Dependents (what depends on this goal)
        dependents = graph.get_dependents(focus_goal_id)
        if dependents:
            lines.append("Dependents (goals that rely on this one):")
            for edge in dependents:
                dep_goal = graph.nodes.get(edge.to_goal_id)
                if dep_goal:
                    icon = "⚠" if edge.relationship_type == "conflicts" else "✓"
                    lines.append(f"  {icon} [{dep_goal.domain}] {dep_goal.title}")
                    lines.append(
                        f"     Type: {edge.relationship_type} | Strength: {edge.strength:.1f}"
                    )
                    if edge.reason:
                        lines.append(f"     Reason: {edge.reason}")
        else:
            lines.append("No goals depend on this one")
    else:
        # Full view: show all domains and their relationships
        # Group by domain
        domain_goals: Dict[str, List[GoalNode]] = {}
        for node in graph.nodes.values():
            if node.domain not in domain_goals:
                domain_goals[node.domain] = []
            domain_goals[node.domain].append(node)

        # Show goals by domain
        for domain in sorted(domain_goals.keys()):
            lines.append(f"┌─ {domain.upper()} DOMAIN " + "─" * (75 - len(domain)) + "┐")
            for goal in domain_goals[domain]:
                status_icon = {"pending": "○", "in_progress": "◐", "completed": "●"}[goal.status]
                lines.append(f"│ {status_icon} [{goal.priority}] {goal.title}".ljust(76) + "│")
            lines.append("└" + "─" * 78 + "┘")
            lines.append("")

        # Show cross-domain dependencies
        lines.append("CROSS-DOMAIN RELATIONSHIPS:")
        lines.append("─" * 80)

        # Group relationships by type
        edges_by_type: Dict[str, List[DependencyEdge]] = {}
        for edge in graph.edges:
            if edge.relationship_type not in edges_by_type:
                edges_by_type[edge.relationship_type] = []
            edges_by_type[edge.relationship_type].append(edge)

        type_icons = {
            "enables": "→",
            "requires": "⇒",
            "supports": "→̂",
            "conflicts": "⚡",
        }

        for rel_type, edges in sorted(edges_by_type.items()):
            if not edges:
                continue
            lines.append(f"\n{rel_type.upper()} ({type_icons.get(rel_type, '→')}):")
            for edge in edges:
                from_goal = graph.nodes.get(edge.from_goal_id)
                to_goal = graph.nodes.get(edge.to_goal_id)

                if from_goal and to_goal:
                    cross_domain = "🔗" if from_goal.domain != to_goal.domain else ""
                    lines.append(
                        f"  {cross_domain} [{from_goal.domain}] {from_goal.title} "
                        f"{type_icons.get(rel_type, '→')} [{to_goal.domain}] {to_goal.title}"
                    )
                    if edge.reason:
                        lines.append(f"      ({edge.reason})")

    # Show cycle warnings
    cycles = graph.detect_cycles()
    if cycles:
        lines.append("\n" + "⚠" * 40)
        lines.append("WARNING: CIRCULAR DEPENDENCIES DETECTED!")
        lines.append("⚠" * 40)
        for i, cycle in enumerate(cycles, 1):
            cycle_titles = " → ".join(
                [graph.nodes[gid].title for gid in cycle if gid in graph.nodes]
            )
            lines.append(f"\nCycle {i}:")
            lines.append(f"  {cycle_titles} → (back to start)")

    return "\n".join(lines)


# ==============================================================================
# Goal Dependency Tools Factory
# ==============================================================================


def create_goal_dependency_tools(backend=None):
    """
    Create goal dependency mapping tools with shared FilesystemBackend instance.

    These tools enable the AI Life Coach to:
    - Build and visualize goal dependency graphs
    - Detect implicit dependencies between goals
    - Simulate impact propagation through the graph
    - Find critical paths for goal achievement
    - Resolve circular dependencies and conflicts

    Args:
        backend: Optional FilesystemBackend instance. If None, uses get_backend()

    Returns:
        Tuple of dependency tools (build_goal_dependency_graph,
                                  detect_implicit_dependencies,
                                  simulate_goal_impact,
                                  visualize_dependency_graph,
                                  find_critical_path,
                                  suggest_dependency_resolutions)

    Example:
        >>> from src.config import config
        >>> config.initialize_environment()
        >>> tools = create_goal_dependency_tools()
        >>> result = build_goal_dependency_graph(
        ...     user_id="user_123",
        ...     goals=[{"id": "g1", "domain": "career", "title": "Get promotion"}]
        ... )
    """
    if backend is None:
        backend = get_backend()

    # Get the workspace directory path from backend
    workspace_path = Path(backend.root_dir) if hasattr(backend, "root_dir") else Path("workspace")

    @tool
    def build_goal_dependency_graph(
        user_id: str,
        goals: List[Dict[str, Any]],
        dependencies: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """Build a comprehensive goal dependency graph.

        This tool creates a Directed Acyclic Graph (DAG) representing goals
        and their interdependencies with advanced features:
        - Cycle detection to prevent impossible plans
        - Topological sorting for execution order
        - Critical path analysis for timing
        - Support for effort estimates and deadlines

        Args:
            user_id: The user's unique identifier
            goals: List of goal dictionaries, each containing:
                   - id (str): Unique identifier for the goal
                   - domain (str): Domain category (career/relationship/finance/wellness)
                   - title (str): Human-readable goal description
                   - priority (int, optional): 1-10 priority level (default: 5)
                   - status (str, optional): pending/in_progress/completed
                   - estimated_effort (float, optional): Effort in hours/days
                   - deadline (str, optional): ISO format date string
            dependencies: Optional list of dependency dictionaries
                         - from_goal_id (str): Source goal ID
                         - to_goal_id (str): Target goal ID
                         - relationship_type (str): enables/requires/conflicts/supports
                         - strength (float, optional): 0-1 impact strength (default: 1.0)
                         - reason (str, optional): Explanation of the dependency

        Returns:
            Structured dependency graph with analysis and visualization.
            Saved to goal_dependencies/{user_id}/

        Example:
            >>> build_goal_dependency_graph(
            ...     "user_123",
            ...     [
            ...         {"id": "g1", "domain": "career", "title": "Get promotion",
            ...          "estimated_effort": 40, "deadline": "2025-06-01"}
            ...     ],
            ...     [
            ...         {"from_goal_id": "g1", "to_goal_id": "g2",
            ...          "relationship_type": "enables", "reason": "Higher income enables savings"}
            ...     ]
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not goals or not isinstance(goals, list):
            return "Error: goals must be a non-empty list"

        dependencies = dependencies or []

        try:
            # Create the dependency graph
            graph = GoalDependencyGraph()

            # Add goal nodes
            for goal_data in goals:
                if "id" not in goal_data or "domain" not in goal_data or "title" not in goal_data:
                    return f"Error: Each goal must have id, domain, and title. Got: {goal_data}"

                goal = GoalNode(
                    id=goal_data["id"],
                    domain=goal_data["domain"],
                    title=goal_data["title"],
                    priority=goal_data.get("priority", 5),
                    status=goal_data.get("status", "pending"),
                    estimated_effort=goal_data.get("estimated_effort"),
                    deadline=goal_data.get("deadline"),
                )
                graph.add_goal(goal)

            # Add dependency edges
            for dep_data in dependencies:
                if "from_goal_id" not in dep_data or "to_goal_id" not in dep_data:
                    return f"Error: Each dependency must have from_goal_id and to_goal_id. Got: {dep_data}"
                if "relationship_type" not in dep_data:
                    return f"Error: Each dependency must have relationship_type. Got: {dep_data}"

                edge = DependencyEdge(
                    from_goal_id=dep_data["from_goal_id"],
                    to_goal_id=dep_data["to_goal_id"],
                    relationship_type=dep_data["relationship_type"],
                    strength=dep_data.get("strength", 1.0),
                    reason=dep_data.get("reason"),
                )
                graph.add_dependency(edge)

            # Detect cycles
            cycles = graph.detect_cycles()
            cycle_analysis = []
            if cycles:
                for cycle in cycles:
                    goals_in_cycle = [graph.nodes[gid].title for gid in cycle if gid in graph.nodes]
                    cycle_analysis.append(" → ".join(goals_in_cycle))

            # Get topological order (if no cycles)
            execution_order = []
            if not cycles:
                try:
                    execution_order = graph.topological_sort()
                except ValueError as e:
                    cycle_analysis.append(str(e))

            # Find critical path
            critical_path = []
            critical_effort = 0.0
            if not cycles:
                try:
                    critical_path, critical_effort = graph.find_critical_path()
                except ValueError:
                    pass

            # Analyze by domain
            domain_stats: Dict[str, Dict[str, Any]] = {}
            for node in graph.nodes.values():
                if node.domain not in domain_stats:
                    domain_stats[node.domain] = {
                        "goals": [],
                        "avg_priority": 0,
                    }
                domain_stats[node.domain]["goals"].append(node.to_dict())

            for domain, stats in domain_stats.items():
                priorities = [g["priority"] for g in stats["goals"]]
                stats["avg_priority"] = sum(priorities) / len(priorities) if priorities else 0

            # Build analysis structure
            analysis = {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "graph": graph.to_dict(),
                "analysis": {
                    "total_goals": len(graph.nodes),
                    "total_dependencies": len(graph.edges),
                    "domains": domain_stats,
                    "cycles_detected": cycle_analysis,
                    "execution_order": execution_order if not cycles else None,
                    "critical_path": critical_path,
                    "critical_effort": critical_effort,
                },
            }

            # Save to file
            json_content = json.dumps(analysis, indent=2)
            today = date.today()
            path = f"goal_dependencies/{user_id}/{today}_dependency_graph.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Generate text visualization
            viz = visualize_dependency_graph_text(graph)

            # Format user-friendly response
            response_parts = [
                f"Goal Dependency Graph for {user_id}",
                "=" * 60,
                f"\nTotal Goals: {len(graph.nodes)}",
                f"Total Dependencies: {len(graph.edges)}",
            ]

            # Domain breakdown
            response_parts.append("\nGoals by Domain:")
            for domain, stats in sorted(domain_stats.items()):
                response_parts.append(f"  {domain.title()}:")
                for goal in stats["goals"]:
                    response_parts.append(f"    - {goal['title']} (Priority: {goal['priority']})")

            # Cycle warnings
            if cycle_analysis:
                response_parts.append("\n⚠ WARNING: Circular Dependencies Detected!")
                response_parts.append("These create impossible execution sequences:")
                for cycle in cycle_analysis:
                    response_parts.append(f"  - {cycle}")
                response_parts.append("\nPlease resolve these by adjusting dependencies.")
            elif execution_order:
                response_parts.append("\n✓ No cycles detected - valid dependency structure")
                response_parts.append("\nRecommended Execution Order:")
                for i, goal_id in enumerate(execution_order, 1):
                    if goal_id in graph.nodes:
                        goal = graph.nodes[goal_id]
                        response_parts.append(f"  {i}. [{goal.domain}] {goal.title}")

            # Critical path information
            if critical_path and not cycles:
                response_parts.append("\n🎯 Critical Path (Longest path to completion):")
                critical_titles = [
                    graph.nodes[gid].title for gid in critical_path if gid in graph.nodes
                ]
                response_parts.append(" → ".join(critical_titles))
                response_parts.append(f"Estimated Total Effort: {critical_effort:.1f} hours/days")

            response_parts.append(f"\nDependency graph saved to: {path}")
            response_parts.append("\n" + "─" * 60)
            response_parts.append(viz)

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error building goal dependency graph: {str(e)}"

    @tool
    def detect_implicit_dependencies(
        user_id: str,
        goal_dependencies_path: Optional[str] = None,
    ) -> str:
        """Detect potential implicit dependencies between goals.

        This tool analyzes existing goals to find patterns that suggest
        relationships not explicitly marked by the user:
        - Keyword overlaps suggesting related goals
        - Complementary domain relationships
        - Temporal sequences based on deadlines

        Args:
            user_id: The user's unique identifier
            goal_dependencies_path: Optional path to existing dependency graph JSON.
                                    If None, uses the most recent one.

        Returns:
            List of suggested dependencies with confidence scores.
            Saved to implicit_dependencies/{user_id}/

        Example:
            >>> detect_implicit_dependencies("user_123")
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        try:
            # Load dependency graph
            if goal_dependencies_path is None:
                deps_dir = workspace_path / "goal_dependencies" / user_id
                if not deps_dir.exists():
                    return f"Error: No dependency graphs found for user {user_id}"

                graph_files = sorted(
                    deps_dir.glob("*_dependency_graph.json"),
                    key=lambda p: p.stat().st_mtime,
                    reverse=True,
                )
                if not graph_files:
                    return f"Error: No dependency graphs found for user {user_id}"

                goal_dependencies_path = str(graph_files[0].relative_to(workspace_path))

            # Read the graph file
            try:
                if hasattr(backend, "read_file"):
                    json_content = backend.read_file(goal_dependencies_path)
                else:
                    file_path = workspace_path / goal_dependencies_path
                    json_content = file_path.read_text()

                graph_data = json.loads(json_content)
            except FileNotFoundError:
                return f"Error: Dependency graph file not found at {goal_dependencies_path}"

            # Reconstruct graph
            graph = GoalDependencyGraph()
            for node_data in graph_data.get("graph", {}).get("nodes", []):
                goal = GoalNode(
                    id=node_data["id"],
                    domain=node_data["domain"],
                    title=node_data["title"],
                    priority=node_data.get("priority", 5),
                    status=node_data.get("status", "pending"),
                    estimated_effort=node_data.get("estimated_effort"),
                    deadline=node_data.get("deadline"),
                )
                graph.add_goal(goal)

            for edge_data in graph_data.get("graph", {}).get("edges", []):
                edge = DependencyEdge(
                    from_goal_id=edge_data["from_goal_id"],
                    to_goal_id=edge_data["to_goal_id"],
                    relationship_type=edge_data["relationship_type"],
                    strength=edge_data.get("strength", 1.0),
                    reason=edge_data.get("reason"),
                )
                graph.add_dependency(edge)

            # Detect implicit dependencies
            suggestions = detect_implicit_dependencies(list(graph.nodes.values()), graph.edges)

            # Build response structure
            result = {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "source_file": goal_dependencies_path,
                "suggestions_count": len(suggestions),
                "suggestions": suggestions,
            }

            # Save results
            json_content = json.dumps(result, indent=2)
            today = date.today()
            path = f"implicit_dependencies/{user_id}/{today}_suggestions.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            response_parts = [
                f"Implicit Dependency Detection for {user_id}",
                "=" * 60,
            ]

            if not suggestions:
                response_parts.append("\n✓ No implicit dependencies detected!")
                response_parts.append(
                    "Your goals appear to be well-defined with clear relationships."
                )
            else:
                response_parts.append(
                    f"\nFound {len(suggestions)} potential implicit dependency(ies):\n"
                )

                for i, suggestion in enumerate(suggestions, 1):
                    from_goal = graph.nodes.get(suggestion["from_goal_id"])
                    to_goal = graph.nodes.get(suggestion["to_goal_id"])

                    if from_goal and to_goal:
                        response_parts.append(f"{i}. {from_goal.title} → {to_goal.title}")
                        response_parts.append(
                            f"   Type: {suggestion['relationship_type']} | "
                            f"Confidence: {suggestion['confidence']:.0%}"
                        )
                        response_parts.append(f"   Reason: {suggestion['reason']}\n")

            response_parts.append(f"\nSuggestions saved to: {path}")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error detecting implicit dependencies: {str(e)}"

    @tool
    def simulate_goal_impact(
        user_id: str,
        goal_id: str,
        outcome: str,  # "success" or "failure"
        goal_dependencies_path: Optional[str] = None,
    ) -> str:
        """Simulate the impact of a goal outcome on dependent goals.

        This tool propagates the effects of a goal success or failure through
        the dependency graph to show what other goals will be affected.

        Args:
            user_id: The user's unique identifier
            goal_id: ID of the goal to simulate outcome for
            outcome: "success" or "failure"
            goal_dependencies_path: Optional path to existing dependency graph JSON.
                                    If None, uses the most recent one.

        Returns:
            Analysis of affected goals with impact details.
            Saved to impact_simulations/{user_id}/

        Example:
            >>> simulate_goal_impact("user_123", "g1", "success")
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if outcome not in ["success", "failure"]:
            return 'Error: outcome must be either "success" or "failure"'

        try:
            # Load dependency graph
            if goal_dependencies_path is None:
                deps_dir = workspace_path / "goal_dependencies" / user_id
                if not deps_dir.exists():
                    return f"Error: No dependency graphs found for user {user_id}"

                graph_files = sorted(
                    deps_dir.glob("*_dependency_graph.json"),
                    key=lambda p: p.stat().st_mtime,
                    reverse=True,
                )
                if not graph_files:
                    return f"Error: No dependency graphs found for user {user_id}"

                goal_dependencies_path = str(graph_files[0].relative_to(workspace_path))

            # Read the graph file
            try:
                if hasattr(backend, "read_file"):
                    json_content = backend.read_file(goal_dependencies_path)
                else:
                    file_path = workspace_path / goal_dependencies_path
                    json_content = file_path.read_text()

                graph_data = json.loads(json_content)
            except FileNotFoundError:
                return f"Error: Dependency graph file not found at {goal_dependencies_path}"

            # Reconstruct graph
            graph = GoalDependencyGraph()
            for node_data in graph_data.get("graph", {}).get("nodes", []):
                goal = GoalNode(
                    id=node_data["id"],
                    domain=node_data["domain"],
                    title=node_data["title"],
                    priority=node_data.get("priority", 5),
                    status=node_data.get("status", "pending"),
                    estimated_effort=node_data.get("estimated_effort"),
                    deadline=node_data.get("deadline"),
                )
                graph.add_goal(goal)

            for edge_data in graph_data.get("graph", {}).get("edges", []):
                edge = DependencyEdge(
                    from_goal_id=edge_data["from_goal_id"],
                    to_goal_id=edge_data["to_goal_id"],
                    relationship_type=edge_data["relationship_type"],
                    strength=edge_data.get("strength", 1.0),
                    reason=edge_data.get("reason"),
                )
                graph.add_dependency(edge)

            # Validate goal_id exists
            if goal_id not in graph.nodes:
                return f"Error: Goal {goal_id} not found in dependency graph"

            # Simulate impact
            affected_goals = graph.simulate_impact(goal_id, outcome)

            # Build result structure
            result = {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "source_file": goal_dependencies_path,
                "simulated_goal": {"id": goal_id, "title": graph.nodes[goal_id].title},
                "outcome": outcome,
                "affected_goals": affected_goals,
            }

            # Save results
            json_content = json.dumps(result, indent=2)
            today = date.today()
            path = f"impact_simulations/{user_id}/{today}_goal_{goal_id}_{outcome}.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            outcome_icon = "✓" if outcome == "success" else "✗"
            response_parts = [
                f"Impact Simulation for {user_id}",
                "=" * 60,
                f"\nSimulating: {outcome_icon} '{graph.nodes[goal_id].title}' - {outcome.upper()}",
            ]

            if not any(affected_goals.values()):
                response_parts.append("\n✓ No other goals are affected by this outcome.")
            else:
                if affected_goals["positively_affected"]:
                    response_parts.append("\n✓ Positively Affected Goals:")
                    for impact in affected_goals["positively_affected"]:
                        response_parts.append(f"  • {impact['title']}")
                        response_parts.append(
                            f"    Impact Strength: {impact['strength']:.1f} | {impact['reason']}"
                        )

                if affected_goals["negatively_affected"]:
                    response_parts.append("\n⚠ Negatively Affected Goals:")
                    for impact in affected_goals["negatively_affected"]:
                        response_parts.append(f"  • {impact['title']}")
                        response_parts.append(
                            f"    Impact Strength: {impact['strength']:.1f} | {impact['reason']}"
                        )

                if affected_goals["blocked"]:
                    response_parts.append("\n🚫 Blocked Goals:")
                    for impact in affected_goals["blocked"]:
                        response_parts.append(f"  • {impact['title']}")
                        response_parts.append(
                            f"    Impact Strength: {impact['strength']:.1f} | {impact['reason']}"
                        )

            response_parts.append(f"\nSimulation results saved to: {path}")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error simulating goal impact: {str(e)}"

    @tool
    def visualize_dependency_graph(
        user_id: str,
        goal_dependencies_path: Optional[str] = None,
        focus_goal_id: Optional[str] = None,
    ) -> str:
        """Generate text-based visualization of the dependency graph.

        This tool creates a visual representation of goal dependencies,
        either showing:
        - Full graph with all domains and relationships
        - Focused view on a single goal and its immediate dependencies

        Args:
            user_id: The user's unique identifier
            goal_dependencies_path: Optional path to existing dependency graph JSON.
                                    If None, uses the most recent one.
            focus_goal_id: Optional goal ID to highlight (shows focused view)

        Returns:
            Text-based visualization of the dependency graph.

        Example:
            >>> visualize_dependency_graph("user_123", focus_goal_id="g1")
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        try:
            # Load dependency graph
            if goal_dependencies_path is None:
                deps_dir = workspace_path / "goal_dependencies" / user_id
                if not deps_dir.exists():
                    return f"Error: No dependency graphs found for user {user_id}"

                graph_files = sorted(
                    deps_dir.glob("*_dependency_graph.json"),
                    key=lambda p: p.stat().st_mtime,
                    reverse=True,
                )
                if not graph_files:
                    return f"Error: No dependency graphs found for user {user_id}"

                goal_dependencies_path = str(graph_files[0].relative_to(workspace_path))

            # Read the graph file
            try:
                if hasattr(backend, "read_file"):
                    json_content = backend.read_file(goal_dependencies_path)
                else:
                    file_path = workspace_path / goal_dependencies_path
                    json_content = file_path.read_text()

                graph_data = json.loads(json_content)
            except FileNotFoundError:
                return f"Error: Dependency graph file not found at {goal_dependencies_path}"

            # Reconstruct graph
            graph = GoalDependencyGraph()
            for node_data in graph_data.get("graph", {}).get("nodes", []):
                goal = GoalNode(
                    id=node_data["id"],
                    domain=node_data["domain"],
                    title=node_data["title"],
                    priority=node_data.get("priority", 5),
                    status=node_data.get("status", "pending"),
                    estimated_effort=node_data.get("estimated_effort"),
                    deadline=node_data.get("deadline"),
                )
                graph.add_goal(goal)

            for edge_data in graph_data.get("graph", {}).get("edges", []):
                edge = DependencyEdge(
                    from_goal_id=edge_data["from_goal_id"],
                    to_goal_id=edge_data["to_goal_id"],
                    relationship_type=edge_data["relationship_type"],
                    strength=edge_data.get("strength", 1.0),
                    reason=edge_data.get("reason"),
                )
                graph.add_dependency(edge)

            # Generate visualization
            viz = visualize_dependency_graph_text(graph, focus_goal_id)

            return viz

        except Exception as e:
            return f"Error visualizing dependency graph: {str(e)}"

    @tool
    def find_critical_path(
        user_id: str,
        goal_dependencies_path: Optional[str] = None,
    ) -> str:
        """Find the critical path for goal achievement.

        The critical path is the longest sequence of dependent goals (by estimated effort).
        It represents the minimum time needed to complete all goals and highlights
        which goals are most critical for timely completion.

        Args:
            user_id: The user's unique identifier
            goal_dependencies_path: Optional path to existing dependency graph JSON.
                                    If None, uses the most recent one.

        Returns:
            Analysis of critical path with timing and dependencies.
            Saved to critical_paths/{user_id}/

        Example:
            >>> find_critical_path("user_123")
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        try:
            # Load dependency graph
            if goal_dependencies_path is None:
                deps_dir = workspace_path / "goal_dependencies" / user_id
                if not deps_dir.exists():
                    return f"Error: No dependency graphs found for user {user_id}"

                graph_files = sorted(
                    deps_dir.glob("*_dependency_graph.json"),
                    key=lambda p: p.stat().st_mtime,
                    reverse=True,
                )
                if not graph_files:
                    return f"Error: No dependency graphs found for user {user_id}"

                goal_dependencies_path = str(graph_files[0].relative_to(workspace_path))

            # Read the graph file
            try:
                if hasattr(backend, "read_file"):
                    json_content = backend.read_file(goal_dependencies_path)
                else:
                    file_path = workspace_path / goal_dependencies_path
                    json_content = file_path.read_text()

                graph_data = json.loads(json_content)
            except FileNotFoundError:
                return f"Error: Dependency graph file not found at {goal_dependencies_path}"

            # Reconstruct graph
            graph = GoalDependencyGraph()
            for node_data in graph_data.get("graph", {}).get("nodes", []):
                goal = GoalNode(
                    id=node_data["id"],
                    domain=node_data["domain"],
                    title=node_data["title"],
                    priority=node_data.get("priority", 5),
                    status=node_data.get("status", "pending"),
                    estimated_effort=node_data.get("estimated_effort"),
                    deadline=node_data.get("deadline"),
                )
                graph.add_goal(goal)

            for edge_data in graph_data.get("graph", {}).get("edges", []):
                edge = DependencyEdge(
                    from_goal_id=edge_data["from_goal_id"],
                    to_goal_id=edge_data["to_goal_id"],
                    relationship_type=edge_data["relationship_type"],
                    strength=edge_data.get("strength", 1.0),
                    reason=edge_data.get("reason"),
                )
                graph.add_dependency(edge)

            # Find critical path
            try:
                critical_path, total_effort = graph.find_critical_path()
            except ValueError as e:
                return f"Error finding critical path: {str(e)}"

            # Analyze goals on critical path
            critical_goals = [graph.nodes[gid] for gid in critical_path if gid in graph.nodes]

            # Identify non-critical goals (those with slack)
            critical_goal_ids = set(critical_path)
            non_critical_goals = [
                node for gid, node in graph.nodes.items() if gid not in critical_goal_ids
            ]

            # Build result structure
            result = {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "source_file": goal_dependencies_path,
                "critical_path": critical_path,
                "total_effort": total_effort,
                "critical_goals_count": len(critical_goals),
                "non_critical_goals_count": len(non_critical_goals),
            }

            # Save results
            json_content = json.dumps(result, indent=2)
            today = date.today()
            path = f"critical_paths/{user_id}/{today}_critical_path.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            response_parts = [
                f"Critical Path Analysis for {user_id}",
                "=" * 60,
            ]

            response_parts.append("\n🎯 CRITICAL PATH (Longest dependency chain):")
            for i, goal in enumerate(critical_goals, 1):
                effort = goal.estimated_effort or "N/A"
                response_parts.append(
                    f"  {i}. [{goal.domain}] {goal.title} "
                    f"(Priority: {goal.priority}, Effort: {effort})"
                )

            response_parts.append(f"\nTotal Estimated Effort: {total_effort:.1f} hours/days")

            response_parts.append(
                "\nGoals on critical path are the most time-sensitive. "
                "Delays here will impact overall completion time."
            )

            if non_critical_goals:
                response_parts.append(f"\nNon-Critical Goals (have scheduling flexibility):")
                for goal in non_critical_goals[:10]:  # Show up to 10
                    response_parts.append(f"  • [{goal.domain}] {goal.title}")

            # Slack analysis
            if critical_goals and non_critical_goals:
                response_parts.append(
                    f"\n📊 Summary: {len(critical_goals)} critical, "
                    f"{len(non_critical_goals)} non-critical goals"
                )
                response_parts.append(
                    "Focus your attention on critical path goals for timely completion."
                )

            response_parts.append(f"\nCritical path analysis saved to: {path}")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error finding critical path: {str(e)}"

    @tool
    def suggest_dependency_resolutions(
        user_id: str,
        goal_dependencies_path: Optional[str] = None,
    ) -> str:
        """Suggest resolutions for circular dependencies and conflicts.

        This tool analyzes the dependency graph to identify:
        - Circular dependencies that create impossible execution sequences
        - Strong conflicts between high-priority goals
        - Conflict resolution strategies

        Args:
            user_id: The user's unique identifier
            goal_dependencies_path: Optional path to existing dependency graph JSON.
                                    If None, uses the most recent one.

        Returns:
            List of resolution strategies for identified issues.
            Saved to conflict_resolutions/{user_id}/

        Example:
            >>> suggest_dependency_resolutions("user_123")
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        try:
            # Load dependency graph
            if goal_dependencies_path is None:
                deps_dir = workspace_path / "goal_dependencies" / user_id
                if not deps_dir.exists():
                    return f"Error: No dependency graphs found for user {user_id}"

                graph_files = sorted(
                    deps_dir.glob("*_dependency_graph.json"),
                    key=lambda p: p.stat().st_mtime,
                    reverse=True,
                )
                if not graph_files:
                    return f"Error: No dependency graphs found for user {user_id}"

                goal_dependencies_path = str(graph_files[0].relative_to(workspace_path))

            # Read the graph file
            try:
                if hasattr(backend, "read_file"):
                    json_content = backend.read_file(goal_dependencies_path)
                else:
                    file_path = workspace_path / goal_dependencies_path
                    json_content = file_path.read_text()

                graph_data = json.loads(json_content)
            except FileNotFoundError:
                return f"Error: Dependency graph file not found at {goal_dependencies_path}"

            # Reconstruct graph
            graph = GoalDependencyGraph()
            for node_data in graph_data.get("graph", {}).get("nodes", []):
                goal = GoalNode(
                    id=node_data["id"],
                    domain=node_data["domain"],
                    title=node_data["title"],
                    priority=node_data.get("priority", 5),
                    status=node_data.get("status", "pending"),
                    estimated_effort=node_data.get("estimated_effort"),
                    deadline=node_data.get("deadline"),
                )
                graph.add_goal(goal)

            for edge_data in graph_data.get("graph", {}).get("edges", []):
                edge = DependencyEdge(
                    from_goal_id=edge_data["from_goal_id"],
                    to_goal_id=edge_data["to_goal_id"],
                    relationship_type=edge_data["relationship_type"],
                    strength=edge_data.get("strength", 1.0),
                    reason=edge_data.get("reason"),
                )
                graph.add_dependency(edge)

            # Detect cycles
            cycles = graph.detect_cycles()

            resolutions = []

            # Resolve circular dependencies
            if cycles:
                for i, cycle in enumerate(cycles, 1):
                    resolution = {
                        "type": "circular_dependency",
                        "cycle_id": i,
                        "cycle_goals": [
                            {"id": gid, "title": graph.nodes[gid].title}
                            for gid in cycle
                            if gid in graph.nodes
                        ],
                        "resolutions": [],
                    }

                    # Suggest breaking the weakest link
                    for j in range(len(cycle) - 1):
                        from_id = cycle[j]
                        to_id = cycle[j + 1]

                        # Find the edge
                        edge = None
                        for e in graph.edges:
                            if e.from_goal_id == from_id and e.to_goal_id == to_id:
                                edge = e
                                break

                        if edge and edge.relationship_type in ["enables", "supports"]:
                            # Suggest removing or weakening this dependency
                            resolution["resolutions"].append(
                                {
                                    "action": "remove_dependency",
                                    "from_goal_id": from_id,
                                    "to_goal_id": to_id,
                                    "reason": f"Remove '{edge.relationship_type}' dependency between "
                                    f"'{graph.nodes[from_id].title}' and '{graph.nodes[to_id].title}' "
                                    f"to break the cycle",
                                }
                            )

                    # Suggest making one dependency non-blocking
                    if resolution["resolutions"]:
                        resolutions.append(resolution)

            # Resolve conflicts
            conflict_edges = [e for e in graph.edges if e.relationship_type == "conflicts"]

            high_priority_conflicts = []
            for edge in conflict_edges:
                from_node = graph.nodes.get(edge.from_goal_id)
                to_node = graph.nodes.get(edge.to_goal_id)

                if from_node and to_node:
                    # Identify high-priority conflicts
                    if from_node.priority >= 7 or to_node.priority >= 7:
                        resolution = {
                            "type": "high_priority_conflict",
                            "goal_1": from_node.to_dict(),
                            "goal_2": to_node.to_dict(),
                            "conflict_strength": edge.strength,
                            "reason": edge.reason,
                        }

                        # Get resolution suggestions
                        resolution["resolutions"] = suggest_conflict_resolution(
                            from_node, to_node, edge
                        )

                        high_priority_conflicts.append(resolution)

            # Build result structure
            result = {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "source_file": goal_dependencies_path,
                "cycles_detected": len(cycles),
                "high_priority_conflicts": len(high_priority_conflicts),
                "resolutions": {
                    "circular_dependencies": [
                        r for r in resolutions if r["type"] == "circular_dependency"
                    ],
                    "high_priority_conflicts": high_priority_conflicts,
                },
            }

            # Save results
            json_content = json.dumps(result, indent=2)
            today = date.today()
            path = f"conflict_resolutions/{user_id}/{today}_resolutions.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            response_parts = [
                f"Dependency Resolution Suggestions for {user_id}",
                "=" * 60,
            ]

            if not resolutions and high_priority_conflicts:
                response_parts.append("\n✓ No circular dependencies detected!")
            elif not resolutions and not high_priority_conflicts:
                response_parts.append("\n✓ No issues detected!")
                response_parts.append("Your goal dependencies are well-structured.")
            else:
                if resolutions:
                    response_parts.append(
                        f"\n⚠ Found {len(resolutions)} circular dependency(ies) to resolve:\n"
                    )

                    for resolution in resolutions:
                        cycle_titles = " → ".join([g["title"] for g in resolution["cycle_goals"]])
                        response_parts.append(f"Cycle: {cycle_titles}")
                        response_parts.append("Suggested Resolutions:")

                        for res in resolution["resolutions"]:
                            response_parts.append(f"  • {res['reason']}")

                        response_parts.append("")

                if high_priority_conflicts:
                    response_parts.append(
                        f"\n⚠ Found {len(high_priority_conflicts)} high-priority conflict(s):\n"
                    )

                    for i, conflict in enumerate(high_priority_conflicts, 1):
                        response_parts.append(
                            f"{i}. {conflict['goal_1']['title']} vs {conflict['goal_2']['title']}"
                        )
                        response_parts.append(
                            f"   Priorities: {conflict['goal_1']['priority']} vs "
                            f"{conflict['goal_2']['priority']} | "
                            f"Conflict Strength: {conflict['conflict_strength']:.1f}"
                        )

                        response_parts.append("\n   Resolution Strategies:")
                        for strategy in conflict["resolutions"]:
                            response_parts.append(f"     • {strategy}")

                        response_parts.append("")

            if resolutions or high_priority_conflicts:
                response_parts.append(
                    "💡 Tip: Review these suggestions and adjust your goal dependencies "
                    "accordingly to create a achievable plan."
                )

            response_parts.append(f"\nResolution suggestions saved to: {path}")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error suggesting dependency resolutions: {str(e)}"

    return (
        build_goal_dependency_graph,
        detect_implicit_dependencies,
        simulate_goal_impact,
        visualize_dependency_graph,
        find_critical_path,
        suggest_dependency_resolutions,
    )
