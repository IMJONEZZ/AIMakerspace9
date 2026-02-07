"""
Cross-Domain Integration Tools for AI Life Coach.

This module provides tools for analyzing and integrating goals across
different life domains (career, relationships, finance, wellness).

Tools:
- build_goal_dependency_graph: Create dependency graph structure for goals
- analyze_cross_domain_impacts: Analyze how goals affect each other across domains
- detect_goal_conflicts: Identify conflicts between competing goals
- recommend_priority_adjustments: Suggest priority changes based on dependencies
- generate_integration_plan: Create cohesive plan addressing all domains

Based on research in:
- Goal dependency graph algorithms (DAGs, topological sorting)
- Cross-domain conflict resolution strategies
- Multi-agent goal integration patterns
- Life domain interdependence theory (8 dimensions of wellness)
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
    ):
        self.id = id
        self.domain = domain  # career, relationship, finance, wellness
        self.title = title
        self.priority = priority
        self.status = status

    def to_dict(self) -> Dict[str, Any]:
        """Convert goal node to dictionary."""
        return {
            "id": self.id,
            "domain": self.domain,
            "title": self.title,
            "priority": self.priority,
            "status": self.status,
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

    def to_dict(self) -> Dict[str, Any]:
        """Convert graph to dictionary representation."""
        # Convert nodes using their to_dict() method
        node_dicts = [node.to_dict() for node in self.nodes.values()]
        # Convert edges using their to_dict() method
        edge_dicts = [edge.to_dict() for edge in self.edges]

        return {
            "nodes": node_dicts,
            "edges": edge_dicts,
        }


# ==============================================================================
# Cross-Domain Integration Tool Factory
# ==============================================================================


def create_cross_domain_tools(backend=None):
    """
    Create cross-domain integration tools with shared FilesystemBackend instance.

    These tools enable the AI Life Coach coordinator to:
    - Build goal dependency graphs across domains
    - Analyze cross-domain impacts between goals
    - Detect conflicts and provide resolution strategies
    - Recommend priority adjustments based on dependencies
    - Generate integrated plans that address all domains

    Args:
        backend: Optional FilesystemBackend instance. If None, uses get_backend()

    Returns:
        Tuple of cross-domain tools (build_goal_dependency_graph,
                                   analyze_cross_domain_impacts,
                                   detect_goal_conflicts,
                                   recommend_priority_adjustments,
                                   generate_integration_plan)

    Example:
        >>> from src.config import config
        >>> config.initialize_environment()
        >>> tools = create_cross_domain_tools()
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
        """Build a goal dependency graph across all life domains.

        This tool creates a Directed Acyclic Graph (DAG) representing goals
        and their interdependencies. It supports:
        - Goals from any domain (career, relationship, finance, wellness)
        - Four dependency types: enables, requires, conflicts, supports
        - Cycle detection to prevent impossible plans
        - Topological sorting for execution order

        Args:
            user_id: The user's unique identifier
            goals: List of goal dictionaries, each containing:
                   - id (str): Unique identifier for the goal
                   - domain (str): Domain category (career/relationship/finance/wellness)
                   - title (str): Human-readable goal description
                   - priority (int, optional): 1-10 priority level (default: 5)
            dependencies: Optional list of dependency dictionaries, each containing:
                         - from_goal_id (str): Source goal ID
                         - to_goal_id (str): Target goal ID
                         - relationship_type (str): enables/requires/conflicts/supports
                         - strength (float, optional): 0-1 impact strength (default: 1.0)
                         - reason (str, optional): Explanation of the dependency

        Returns:
            Structured dependency graph with nodes, edges, and analysis.
            Saved to goal_dependencies/{user_id}/

        Raises:
            ValueError: If goals have circular dependencies or invalid parameters

        Example:
            >>> build_goal_dependency_graph(
            ...     "user_123",
            ...     [
            ...         {"id": "g1", "domain": "career", "title": "Get promotion"},
            ...         {"id": "g2", "domain": "finance", "title": "Save $50k for down payment"}
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
                    cycle_analysis.append(" -> ".join(goals_in_cycle))

            # Get topological order (if no cycles)
            execution_order = []
            if not cycles:
                try:
                    execution_order = graph.topological_sort()
                except ValueError as e:
                    cycle_analysis.append(str(e))

            # Analyze by domain
            domain_stats: Dict[str, Dict[str, Any]] = {}
            for node in graph.nodes.values():
                if node.domain not in domain_stats:
                    domain_stats[node.domain] = {
                        "goals": [],
                        "avg_priority": 0,
                    }
                # Store as dict, not GoalNode object
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

            # Dependency types
            response_parts.append("\nDependencies by Type:")
            dep_types: Dict[str, List[DependencyEdge]] = {}
            for edge in graph.edges:
                if edge.relationship_type not in dep_types:
                    dep_types[edge.relationship_type] = []
                dep_types[edge.relationship_type].append(edge)

            for dep_type, edges in sorted(dep_types.items()):
                response_parts.append(f"  {dep_type.title()}:")
                for edge in edges:
                    from_title = (
                        graph.nodes.get(edge.from_goal_id, {}).title
                        if edge.from_goal_id in graph.nodes
                        else "Unknown"
                    )
                    to_title = (
                        graph.nodes.get(edge.to_goal_id, {}).title
                        if edge.to_goal_id in graph.nodes
                        else "Unknown"
                    )
                    reason = f" - {edge.reason}" if edge.reason else ""
                    response_parts.append(f"    {from_title} → {to_title}{reason}")

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

            response_parts.append(f"\nDependency graph saved to: {path}")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error building goal dependency graph: {str(e)}"

    @tool
    def analyze_cross_domain_impacts(
        user_id: str,
        goal_dependencies_path: Optional[str] = None,
    ) -> str:
        """Analyze how goals in different domains affect each other.

        This tool examines cross-domain impacts, identifying:
        - Positive synergies (goals that support each other across domains)
        - Negative conflicts (goals that compete for resources)
        - Cascading effects (how achieving one goal affects others)
        - Domain interdependencies

        Args:
            user_id: The user's unique identifier
            goal_dependencies_path: Optional path to existing dependency graph JSON.
                                    If None, uses the most recent one.

        Returns:
            Structured cross-domain impact analysis with recommendations.
            Saved to cross_domain_analysis/{user_id}/

        Raises:
            ValueError: If required parameters are invalid or graph file not found

        Example:
            >>> analyze_cross_domain_impacts("user_123")
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        try:
            # Load dependency graph
            if goal_dependencies_path is None:
                # Find the most recent dependency graph file
                deps_dir = workspace_path / "goal_dependencies" / user_id
                if not deps_dir.exists():
                    return f"Error: No dependency graphs found for user {user_id}"

                # Find the most recent JSON file
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

            # Analyze cross-domain impacts
            domain_pairs: Set[Tuple[str, str]] = set()
            for edge in graph.edges:
                from_domain = graph.nodes.get(edge.from_goal_id)
                to_domain = graph.nodes.get(edge.to_goal_id)
                if from_domain and to_domain:
                    if from_domain.domain != to_domain.domain:
                        pair = tuple(sorted([from_domain.domain, to_domain.domain]))
                        domain_pairs.add(pair)

            # Analyze each domain pair
            cross_domain_impacts: Dict[str, List[Dict[str, Any]]] = {}
            for from_domain, to_domain in domain_pairs:
                pair_key = f"{from_domain}_{to_domain}"
                cross_domain_impacts[pair_key] = []

                # Find all edges between these domains
                for edge in graph.edges:
                    from_node = graph.nodes.get(edge.from_goal_id)
                    to_node = graph.nodes.get(edge.to_goal_id)

                    if from_node and to_node:
                        edges_between = []
                        if from_node.domain == from_domain and to_node.domain == to_domain:
                            edges_between.append((edge, from_node.title, to_node.title))
                        elif from_node.domain == to_domain and to_node.domain == from_domain:
                            edges_between.append((edge, to_node.title, from_node.title))

                        for edge_data in edges_between:
                            impact = {
                                "from_goal": edge_data[1],
                                "to_goal": edge_data[2],
                                "relationship_type": edge_data[0].relationship_type,
                                "strength": edge_data[0].strength,
                                "reason": edge_data[0].reason,
                            }
                            cross_domain_impacts[pair_key].append(impact)

            # Generate insights
            positive_synergies: List[Dict[str, Any]] = []
            negative_conflicts: List[Dict[str, Any]] = []

            for pair_key, impacts in cross_domain_impacts.items():
                for impact in impacts:
                    if impact["relationship_type"] in ["enables", "requires", "supports"]:
                        positive_synergies.append({**impact, "domains": pair_key})
                    elif impact["relationship_type"] == "conflicts":
                        negative_conflicts.append({**impact, "domains": pair_key})

            # Sort by strength
            positive_synergies.sort(key=lambda x: x["strength"], reverse=True)
            negative_conflicts.sort(key=lambda x: x["strength"], reverse=True)

            # Build analysis structure
            impact_analysis = {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "source_file": goal_dependencies_path,
                "domains_analyzed": list(domain_pairs),
                "cross_domain_impacts": cross_domain_impacts,
                "insights": {
                    "positive_synergies": positive_synergies[:5],  # Top 5
                    "negative_conflicts": negative_conflicts,
                },
            }

            # Save analysis
            json_content = json.dumps(impact_analysis, indent=2)
            today = date.today()
            path = f"cross_domain_analysis/{user_id}/{today}_cross_domain_impacts.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            response_parts = [
                f"Cross-Domain Impact Analysis for {user_id}",
                "=" * 60,
            ]

            if positive_synergies:
                response_parts.append("\n✓ Positive Synergies (Goals that support each other):")
                for i, synergy in enumerate(positive_synergies[:5], 1):
                    response_parts.append(f"  {i}. {synergy['from_goal']} → {synergy['to_goal']}")
                    response_parts.append(
                        f"     Type: {synergy['relationship_type']} | Strength: {synergy['strength']:.1f}"
                    )
                    if synergy.get("reason"):
                        response_parts.append(f"     Reason: {synergy['reason']}")

            if negative_conflicts:
                response_parts.append("\n⚠ Conflicts (Competing goals):")
                for i, conflict in enumerate(negative_conflicts, 1):
                    response_parts.append(
                        f"  {i}. {conflict['from_goal']} vs {conflict['to_goal']}"
                    )
                    response_parts.append(
                        f"     Strength: {conflict['strength']:.1f} | Reason: {conflict.get('reason', 'N/A')}"
                    )

            response_parts.append("\nDomain Interdependencies:")
            for pair_key, impacts in sorted(cross_domain_impacts.items()):
                domains = " ↔ ".join(pair_key.split("_"))
                response_parts.append(f"\n  {domains}:")
                for impact in impacts:
                    icon = "✓" if impact["relationship_type"] != "conflicts" else "⚠"
                    response_parts.append(
                        f"    {icon} {impact['from_goal']} → {impact['to_goal']}"
                        f" ({impact['relationship_type']})"
                    )

            response_parts.append(f"\nAnalysis saved to: {path}")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error analyzing cross-domain impacts: {str(e)}"

    @tool
    def detect_goal_conflicts(
        user_id: str,
        goal_dependencies_path: Optional[str] = None,
    ) -> str:
        """Detect and analyze conflicts between competing goals.

        This tool identifies:
        - Resource conflicts (time, money, energy competition)
        - Logical conflicts (mutually exclusive outcomes)
        - Priority mismatches
        - Conflict resolution strategies

        Args:
            user_id: The user's unique identifier
            goal_dependencies_path: Optional path to existing dependency graph JSON.
                                    If None, uses the most recent one.

        Returns:
            Structured conflict detection report with resolution strategies.
            Saved to conflict_analysis/{user_id}/

        Raises:
            ValueError: If required parameters are invalid or graph file not found

        Example:
            >>> detect_goal_conflicts("user_123")
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        try:
            # Load dependency graph (reusing logic from analyze_cross_domain_impacts)
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

            # Detect explicit conflicts (marked as "conflicts" relationship)
            explicit_conflicts: List[Dict[str, Any]] = []
            for edge in graph.edges:
                if edge.relationship_type == "conflicts":
                    from_node = graph.nodes.get(edge.from_goal_id)
                    to_node = graph.nodes.get(edge.to_goal_id)

                    if from_node and to_node:
                        conflict = {
                            "goal_1": {
                                "id": from_node.id,
                                "title": from_node.title,
                                "domain": from_node.domain,
                                "priority": from_node.priority,
                            },
                            "goal_2": {
                                "id": to_node.id,
                                "title": to_node.title,
                                "domain": to_node.domain,
                                "priority": to_node.priority,
                            },
                            "strength": edge.strength,
                            "reason": edge.reason,
                            "resolution_strategy": suggest_conflict_resolution(
                                from_node, to_node, edge
                            ),
                        }
                        explicit_conflicts.append(conflict)

            # Detect implicit conflicts (same domain, high priority, time/money competition)
            implicit_conflicts: List[Dict[str, Any]] = []
            domain_goals: Dict[str, List[GoalNode]] = {}

            for node in graph.nodes.values():
                if node.domain not in domain_goals:
                    domain_goals[node.domain] = []
                domain_goals[node.domain].append(node)

            for domain, goals in domain_goals.items():
                # Find high-priority goals in same domain
                high_priority = [g for g in goals if g.priority >= 7]
                if len(high_priority) > 1:
                    for i in range(len(high_priority)):
                        for j in range(i + 1, len(high_priority)):
                            # Check if they're not already marked as conflicting
                            has_explicit_conflict = any(
                                (
                                    edge.from_goal_id == high_priority[i].id
                                    and edge.to_goal_id == high_priority[j].id
                                )
                                or (
                                    edge.from_goal_id == high_priority[j].id
                                    and edge.to_goal_id == high_priority[i].id
                                )
                                for edge in graph.edges
                                if edge.relationship_type == "conflicts"
                            )

                            if not has_explicit_conflict:
                                # Create the reason string first
                                conflict_reason = (
                                    f"Both high-priority goals in {domain} domain "
                                    f"- likely competing for time/attention"
                                )

                                implicit_conflict = {
                                    "goal_1": {
                                        "id": high_priority[i].id,
                                        "title": high_priority[i].title,
                                        "domain": high_priority[i].domain,
                                        "priority": high_priority[i].priority,
                                    },
                                    "goal_2": {
                                        "id": high_priority[j].id,
                                        "title": high_priority[j].title,
                                        "domain": high_priority[j].domain,
                                        "priority": high_priority[j].priority,
                                    },
                                    "strength": 0.7,  # Default for implicit conflicts
                                    "reason": conflict_reason,
                                    "resolution_strategy": suggest_conflict_resolution(
                                        high_priority[i],
                                        high_priority[j],
                                        DependencyEdge(
                                            high_priority[i].id,
                                            high_priority[j].id,
                                            "conflicts",
                                            0.7,
                                            conflict_reason,
                                        ),
                                    ),
                                    "type": "implicit",
                                }
                                implicit_conflicts.append(implicit_conflict)

            # Combine all conflicts
            all_conflicts = explicit_conflicts + implicit_conflicts

            # Build conflict report structure
            conflict_report = {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "source_file": goal_dependencies_path,
                "conflicts_detected": len(all_conflicts),
                "explicit_conflicts": explicit_conflicts,
                "implicit_conflicts": implicit_conflicts,
            }

            # Save report
            json_content = json.dumps(conflict_report, indent=2)
            today = date.today()
            path = f"conflict_analysis/{user_id}/{today}_conflicts.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            response_parts = [
                f"Conflict Detection Report for {user_id}",
                "=" * 60,
            ]

            if not all_conflicts:
                response_parts.append("\n✓ No conflicts detected!")
                response_parts.append("Your goals appear to be well-integrated.")
            else:
                response_parts.append(f"\n⚠ {len(all_conflicts)} conflict(s) detected")

                if explicit_conflicts:
                    response_parts.append("\n**Explicit Conflicts (Marked by user):**")
                    for i, conflict in enumerate(explicit_conflicts, 1):
                        response_parts.append(
                            f"\n{i}. {conflict['goal_1']['title']} vs {conflict['goal_2']['title']}"
                        )
                        response_parts.append(
                            f"   Domains: {conflict['goal_1']['domain']} ↔ "
                            f"{conflict['goal_2']['domain']}"
                        )
                        response_parts.append(
                            f"   Priorities: {conflict['goal_1']['priority']} vs "
                            f"{conflict['goal_2']['priority']}"
                        )
                        response_parts.append(f"   Strength: {conflict['strength']:.1f}/1.0")
                        if conflict.get("reason"):
                            response_parts.append(f"   Reason: {conflict['reason']}")
                        response_parts.append("\n   Suggested Resolution:")
                        for line in conflict["resolution_strategy"]:
                            response_parts.append(f"     • {line}")

                if implicit_conflicts:
                    response_parts.append("\n**Potential Conflicts (Detected automatically):**")
                    for i, conflict in enumerate(implicit_conflicts, 1):
                        response_parts.append(
                            f"\n{i}. {conflict['goal_1']['title']} vs {conflict['goal_2']['title']}"
                        )
                        response_parts.append(f"   Domain: {conflict['goal_1']['domain']}")
                        response_parts.append(
                            f"   Priorities: {conflict['goal_1']['priority']} vs "
                            f"{conflict['goal_2']['priority']}"
                        )
                        response_parts.append(f"   Reason: {conflict['reason']}")
                        response_parts.append("\n   Suggested Resolution:")
                        for line in conflict["resolution_strategy"]:
                            response_parts.append(f"     • {line}")

            response_parts.append(f"\nConflict report saved to: {path}")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error detecting goal conflicts: {str(e)}"

    @tool
    def recommend_priority_adjustments(
        user_id: str,
        goal_dependencies_path: Optional[str] = None,
    ) -> str:
        """Recommend priority adjustments based on dependencies and conflicts.

        This tool analyzes the dependency graph to suggest:
        - Priority boosts for goals that enable many others
        - Priority reductions for conflicting goals
        - Dependency-aware priority ordering
        - Risk assessment of current priorities

        Args:
            user_id: The user's unique identifier
            goal_dependencies_path: Optional path to existing dependency graph JSON.
                                    If None, uses the most recent one.

        Returns:
            Structured priority adjustment recommendations with rationale.
            Saved to priority_recommendations/{user_id}/

        Raises:
            ValueError: If required parameters are invalid or graph file not found

        Example:
            >>> recommend_priority_adjustments("user_123")
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

            # Calculate influence scores
            influence_scores: Dict[str, float] = {}
            for node_id in graph.nodes:
                score = 0.0

                # Goals this enables/requires (outgoing positive dependencies)
                for edge in graph.get_dependents(node_id):
                    if edge.relationship_type in ["enables", "requires"]:
                        score += 2.0 * edge.strength
                    elif edge.relationship_type == "supports":
                        score += 1.0 * edge.strength

                # Goals this conflicts with (negative influence)
                for edge in graph.get_dependents(node_id):
                    if edge.relationship_type == "conflicts":
                        score -= 1.5 * edge.strength

                # Goals this depends on (incoming positive dependencies)
                for edge in graph.get_dependencies(node_id):
                    if edge.relationship_type in ["enables", "requires"]:
                        score += 1.0 * edge.strength
                    elif edge.relationship_type == "supports":
                        score += 0.5 * edge.strength

                influence_scores[node_id] = score

            # Generate priority recommendations
            recommendations: List[Dict[str, Any]] = []

            for node_id, node in graph.nodes.items():
                current_priority = node.priority
                influence_score = influence_scores[node_id]
                recommended_priority = current_priority

                # Adjust priority based on influence
                if influence_score > 2.0:
                    # Goal enables many others - boost priority
                    recommended_priority = min(10, current_priority + 2)
                elif influence_score > 1.0:
                    # Goal supports others - slight boost
                    recommended_priority = min(10, current_priority + 1)
                elif influence_score < -1.0:
                    # Goal has significant conflicts - reduce priority
                    recommended_priority = max(1, current_priority - 2)
                elif influence_score < 0.0:
                    # Goal has some conflicts - slight reduction
                    recommended_priority = max(1, current_priority - 1)

                # Only include if recommendation differs from current
                if recommended_priority != current_priority:
                    change = recommended_priority - current_priority
                    direction = "↑" if change > 0 else "↓"
                    reason_parts = []

                    if influence_score > 1.0:
                        reason_parts.append(
                            f"Enables/supports {abs(int(influence_score))} other goal(s)"
                        )
                    elif influence_score < -0.5:
                        reason_parts.append(f"Conflicts with {abs(int(influence_score))} goal(s)")

                    recommendations.append(
                        {
                            "goal_id": node_id,
                            "title": node.title,
                            "domain": node.domain,
                            "current_priority": current_priority,
                            "recommended_priority": recommended_priority,
                            "change_direction": direction,
                            "influence_score": round(influence_score, 2),
                            "reason": "; ".join(reason_parts)
                            if reason_parts
                            else "Based on dependency analysis",
                        }
                    )

            # Sort recommendations by magnitude of change
            recommendations.sort(
                key=lambda x: abs(x["recommended_priority"] - x["current_priority"]), reverse=True
            )

            # Build recommendations structure
            priority_analysis = {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "source_file": goal_dependencies_path,
                "influence_scores": influence_scores,
                "recommendations": recommendations[:10],  # Top 10
            }

            # Save recommendations
            json_content = json.dumps(priority_analysis, indent=2)
            today = date.today()
            path = f"priority_recommendations/{user_id}/{today}_priorities.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            response_parts = [
                f"Priority Adjustment Recommendations for {user_id}",
                "=" * 60,
            ]

            if not recommendations:
                response_parts.append("\n✓ Priorities look good!")
                response_parts.append("No adjustments needed based on dependency analysis.")
            else:
                response_parts.append(f"\n{len(recommendations)} recommendation(s) found:\n")

                for i, rec in enumerate(recommendations[:10], 1):
                    response_parts.append(f"{i}. {rec['title']}")
                    response_parts.append(f"   Domain: {rec['domain']}")
                    response_parts.append(
                        f"   Priority: {rec['current_priority']} → "
                        f"{rec['recommended_priority']} ({rec['change_direction']})"
                    )
                    response_parts.append(f"   Influence Score: {rec['influence_score']}")
                    response_parts.append(f"   Reason: {rec['reason']}\n")

            response_parts.append(f"\nRecommendations saved to: {path}")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error recommending priority adjustments: {str(e)}"

    @tool
    def generate_integration_plan(
        user_id: str,
        goal_dependencies_path: Optional[str] = None,
    ) -> str:
        """Generate a cohesive integration plan addressing all domains.

        This tool creates a comprehensive plan that:
        - Orders goals based on dependencies and priorities
        - Addresses conflicts with specific strategies
        - Provides timeline estimates for goal achievement
        - Suggests milestones and check-ins

        Args:
            user_id: The user's unique identifier
            goal_dependencies_path: Optional path to existing dependency graph JSON.
                                    If None, uses the most recent one.

        Returns:
            Structured integration plan with phases, milestones, and action steps.
            Saved to integration_plans/{user_id}/

        Raises:
            ValueError: If required parameters are invalid or graph file not found

        Example:
            >>> generate_integration_plan("user_123")
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

            # Get topological order (if no cycles)
            execution_order = []
            try:
                execution_order = graph.topological_sort()
            except ValueError:
                # Has cycles - order by priority instead
                execution_order = sorted(
                    graph.nodes.keys(), key=lambda x: (graph.nodes[x].priority, x), reverse=True
                )

            # Group goals by domain for phase planning
            domains_present = sorted(set(node.domain for node in graph.nodes.values()))

            # Create phases
            phases: List[Dict[str, Any]] = []

            # Phase 1: Foundation (high-priority goals with no dependencies)
            phase_1_goals = []
            for goal_id in execution_order:
                node = graph.nodes[goal_id]
                deps = [
                    e
                    for e in graph.get_dependencies(goal_id)
                    if e.relationship_type in ["enables", "requires"]
                ]
                if not deps and node.priority >= 7:
                    phase_1_goals.append(node)

            # Phase 2: Build-out (medium priority, or goals enabled by phase 1)
            phase_2_goals = []
            for goal_id in execution_order:
                node = graph.nodes[goal_id]
                if node not in phase_1_goals and node.priority >= 5:
                    phase_2_goals.append(node)

            # Phase 3: Expansion (remaining goals)
            phase_3_goals = []
            for goal_id in execution_order:
                node = graph.nodes[goal_id]
                if node not in phase_1_goals and node not in phase_2_goals:
                    phase_3_goals.append(node)

            if phase_1_goals:
                phases.append(
                    {
                        "phase": 1,
                        "name": "Foundation - High Priority",
                        "duration_months": len(phase_1_goals) * 2,  # Estimate: 2 months per goal
                        "goals": [g.title for g in phase_1_goals],
                    }
                )

            if phase_2_goals:
                phases.append(
                    {
                        "phase": 2,
                        "name": "Build-out - Medium Priority",
                        "duration_months": len(phase_2_goals) * 3,  # Estimate: 3 months per goal
                        "goals": [g.title for g in phase_2_goals],
                    }
                )

            if phase_3_goals:
                phases.append(
                    {
                        "phase": 3,
                        "name": "Expansion - All Remaining Goals",
                        "duration_months": len(phase_3_goals) * 4,  # Estimate: 4 months per goal
                        "goals": [g.title for g in phase_3_goals],
                    }
                )

            # Identify conflicts and suggest resolutions
            conflict_resolutions: List[Dict[str, Any]] = []
            for edge in graph.edges:
                if edge.relationship_type == "conflicts":
                    from_node = graph.nodes.get(edge.from_goal_id)
                    to_node = graph.nodes.get(edge.to_goal_id)

                    if from_node and to_node:
                        resolution = suggest_conflict_resolution(from_node, to_node, edge)
                        conflict_resolutions.append(
                            {
                                "conflict": f"{from_node.title} vs {to_node.title}",
                                "resolution": resolution,
                            }
                        )

            # Build integration plan structure
            total_months = sum(p["duration_months"] for p in phases)
            integration_plan = {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "source_file": goal_dependencies_path,
                "total_goals": len(graph.nodes),
                "domains_covered": domains_present,
                "estimated_duration_months": total_months,
                "phases": phases,
                "conflict_resolutions": conflict_resolutions,
            }

            # Save plan
            json_content = json.dumps(integration_plan, indent=2)
            today = date.today()
            path = f"integration_plans/{user_id}/{today}_integration_plan.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Create markdown version for readability
            markdown_content = f"""# Integrated Life Plan

**User:** {user_id}
**Created:** {datetime.now().strftime("%Y-%m-%d")}
**Estimated Duration:** {total_months} months
**Domains Covered:** {", ".join(domains_present)}

## Overview

This plan integrates your goals across all life domains into a cohesive,
achievable roadmap. Goals are ordered based on dependencies and priorities
to maximize progress while minimizing conflicts.

---

## Phases

"""

            for phase in phases:
                markdown_content += f"""### Phase {phase["phase"]}: {phase["name"]}
**Duration:** {phase["duration_months"]} months

Goals in this phase:
"""
                for i, goal_title in enumerate(phase["goals"], 1):
                    markdown_content += f"{i}. {goal_title}\n"

                markdown_content += "\n"

            if conflict_resolutions:
                markdown_content += "---\n\n## Conflict Management\n\n"
                for i, conflict in enumerate(conflict_resolutions, 1):
                    markdown_content += f"{i}. **{conflict['conflict']}**\n"
                    for resolution in conflict["resolution"]:
                        markdown_content += f"   - {resolution}\n"
                    markdown_content += "\n"

            markdown_content += """---

## Next Steps

1. Review this plan and adjust goals if needed
2. Start with Phase 1 goals - focus on one or two at a time
3. Schedule regular check-ins to track progress
4. Be flexible - adjust timelines as life circumstances change
5. Celebrate milestones and achievements along the way

## Review Schedule

- **Weekly**: Check progress on current phase goals
- **Monthly**: Assess overall plan and make adjustments
- **Phase completion**: Review achievements before moving to next phase

---

*Plan saved to: {path}*
"""

            # Save markdown version
            md_path = path.replace(".json", ".md")
            if hasattr(backend, "write_file"):
                backend.write_file(md_path, markdown_content)
            else:
                file_path = workspace_path / md_path
                file_path.write_text(markdown_content)

            # Format user-friendly response
            response_parts = [
                f"Integrated Life Plan for {user_id}",
                "=" * 60,
                f"\nEstimated Duration: {total_months} months",
                f"Domains Covered: {', '.join(domains_present)}",
                f"Total Goals: {len(graph.nodes)}",
            ]

            response_parts.append("\nPlan Phases:")
            for phase in phases:
                response_parts.append(
                    f"\nPhase {phase['phase']}: {phase['name']} ({phase['duration_months']} months)"
                )
                for goal_title in phase["goals"][:3]:  # Show first 3
                    response_parts.append(f"  • {goal_title}")
                if len(phase["goals"]) > 3:
                    response_parts.append(f"  • ... and {len(phase['goals']) - 3} more")

            if conflict_resolutions:
                response_parts.append(f"\n⚠ {len(conflict_resolutions)} conflict(s) to manage")
                response_parts.append("See the full plan for resolution strategies.")

            response_parts.append(f"\nIntegration plan saved to: {md_path}")
            response_parts.append("\nNext steps:")
            response_parts.append("  1. Review the detailed plan")
            response_parts.append("  2. Start with Phase 1 goals")
            response_parts.append("  3. Schedule regular progress check-ins")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error generating integration plan: {str(e)}"

    print("Cross-domain tools created successfully!")
    return (
        build_goal_dependency_graph,
        analyze_cross_domain_impacts,
        detect_goal_conflicts,
        recommend_priority_adjustments,
        generate_integration_plan,
    )


# ==============================================================================
# Helper Functions
# ==============================================================================


def suggest_conflict_resolution(
    goal_1: GoalNode, goal_2: GoalNode, edge: DependencyEdge
) -> List[str]:
    """Suggest resolution strategies for conflicting goals."""
    resolutions = []

    # Strategy 1: Prioritize by domain importance
    if goal_1.domain != goal_2.domain:
        # Different domains - suggest focus on one at a time
        if goal_1.priority > goal_2.priority:
            resolutions.append(f"Focus on '{goal_1.title}' first ({goal_1.domain} domain)")
            resolutions.append(f"Defer '{goal_2.title}' until first goal is achieved")
        elif goal_2.priority > goal_1.priority:
            resolutions.append(f"Focus on '{goal_2.title}' first ({goal_2.domain} domain)")
            resolutions.append(f"Defer '{goal_1.title}' until first goal is achieved")
        else:
            resolutions.append(f"Choose one domain to prioritize this quarter")
    else:
        # Same domain competing goals
        if goal_1.priority > goal_2.priority:
            resolutions.append(f"Prioritize '{goal_1.title}' (higher priority)")
        elif goal_2.priority > goal_1.priority:
            resolutions.append(f"Prioritize '{goal_2.title}' (higher priority)")
        else:
            resolutions.append("Consider combining or redefining these goals")

    # Strategy 2: Time-boxing
    if "time" in (edge.reason or "").lower():
        resolutions.append("Allocate specific time blocks for each goal")
        resolutions.append("For example: Mornings for Goal A, Evenings for Goal B")

    # Strategy 3: Resource allocation
    if "money" in (edge.reason or "").lower():
        resolutions.append("Create a budget that allocates resources to both goals")
        resolutions.append("Consider phased funding: focus on one, then redirect resources")

    # Strategy 4: Compromise
    resolutions.append("Find a middle ground: reduce scope of one or both goals")
    resolutions.append("Break large goals into smaller, more manageable pieces")

    # Strategy 5: Seek alternatives
    resolutions.append("Look for ways to achieve similar outcomes with less conflict")
    resolutions.append("Consider if there's a third path that satisfies both goals")

    return resolutions


# Export tools at module level for convenience
__all__ = [
    "create_cross_domain_tools",
]
