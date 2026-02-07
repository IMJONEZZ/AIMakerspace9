"""
Goal Dependency Visualization Tools for AI Life Coach.

This module provides advanced visualization and exploration tools for
goal dependency graphs using pure text/ASCII art (no external plotting libraries).

Tools:
- render_ascii_graph: Render dependency graph as ASCII art with tree structure
- explore_dependencies_interactive: Interactive command-based exploration of graphs
- highlight_critical_path: Visualize critical path with emphasis markers
- what_if_add_goal: Simulate adding a goal and show impact
- what_if_remove_goal: Simulate removing a goal and show cascading effects
- generate_dependency_report: Generate comprehensive dependency analysis report

Based on research in:
- ASCII graph visualization (phart, asciigraf)
- Interactive CLI patterns (cmd2, prompt-toolkit)
- Critical path method (CPM) for project management
- What-if analysis and scenario planning

Example visualization format:
    Career Promotion ──┐
                      ├──→ Save $10k for Move
    House Savings ◄───┘    ↓
                      Buy House → Wellness: Create Home Routine
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
from src.tools.goal_dependency_tools import (
    GoalNode,
    DependencyEdge,
    GoalDependencyGraph,
)


# ==============================================================================
# ASCII Graph Rendering Engine
# ==============================================================================


class ASCIIGraphRenderer:
    """Renders goal dependency graphs as ASCII art."""

    # Box-drawing characters for cleaner visualizations
    BOX_H = "─"
    BOX_V = "│"
    BOX_DL = "┌"
    BOX_DR = "┐"
    BOX_UL = "└"
    BOX_UR = "┘"
    BOX_VR = "├"
    BOX_VL = "┤"
    BOX_HD = "┬"
    BOX_HU = "┴"
    BOX_X = "┼"

    # Relationship arrows
    ARROWS = {
        "enables": "──→",
        "requires": "──⇒",
        "supports": "──➔",
        "conflicts": "──✕",
    }

    # Status indicators
    STATUS_ICONS = {
        "pending": "○",
        "in_progress": "◐",
        "completed": "●",
    }

    # Domain colors (represented by emoji for terminal compatibility)
    DOMAIN_EMOJIS = {
        "career": "💼",
        "relationship": "❤️",
        "finance": "💰",
        "wellness": "🌿",
    }

    def __init__(self, graph: GoalDependencyGraph):
        """Initialize the renderer with a dependency graph."""
        self.graph = graph

    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to fit within max_length."""
        if len(text) <= max_length:
            return text
        return text[: max_length - 3] + "..."

    def _get_goal_display_name(self, goal: GoalNode, max_length: int = 30) -> str:
        """Get formatted display name for a goal."""
        emoji = self.DOMAIN_EMOJIS.get(goal.domain, "📌")
        status_icon = self.STATUS_ICONS.get(goal.status, "?")
        title = self._truncate_text(goal.title, max_length - 4)
        return f"{emoji} {status_icon} {title}"

    def _build_tree_structure(self, root_goal_id: str, visited: Set[str] = None) -> Dict[str, Any]:
        """
        Build a hierarchical tree structure from the graph starting at root_goal_id.

        Returns:
            Dictionary with 'node' and 'children' keys
        """
        if visited is None:
            visited = set()

        if root_goal_id in visited or root_goal_id not in self.graph.nodes:
            return None

        visited.add(root_goal_id)

        node = {
            "goal": self.graph.nodes[root_goal_id],
            "children": [],
        }

        # Get all goals that this goal enables/requires (outgoing edges)
        for edge in self.graph.get_dependents(root_goal_id):
            if edge.relationship_type in ["enables", "requires"]:
                child = self._build_tree_structure(edge.to_goal_id, visited.copy())
                if child:
                    edge_info = {
                        "type": edge.relationship_type,
                        "strength": edge.strength,
                        "reason": edge.reason,
                    }
                    child["edge"] = edge_info
                    node["children"].append(child)

        return node

    def render_tree(
        self, root_goal_id: Optional[str] = None, show_critical_path: bool = False
    ) -> str:
        """
        Render the dependency graph as a hierarchical ASCII tree.

        Args:
            root_goal_id: Optional root goal ID. If None, finds a suitable root.
            show_critical_path: Whether to highlight the critical path

        Returns:
            ASCII art tree representation
        """
        if not self.graph.nodes:
            return "No goals in graph"

        # Find root goal if not specified
        if root_goal_id is None:
            # Look for goals with no incoming positive dependencies
            for node_id, goal in self.graph.nodes.items():
                has_incoming = any(
                    e.to_goal_id == node_id
                    for e in self.graph.edges
                    if e.relationship_type in ["enables", "requires"]
                )
                if not has_incoming:
                    root_goal_id = node_id
                    break

        # Default to first goal if still no root found
        if root_goal_id is None:
            root_goal_id = list(self.graph.nodes.keys())[0]

        # Get critical path if requested
        critical_path_ids = set()
        if show_critical_path:
            try:
                path, _ = self.graph.find_critical_path()
                critical_path_ids = set(path)
            except ValueError:
                pass

        # Build tree structure
        tree = self._build_tree_structure(root_goal_id)
        if not tree:
            return f"Could not build tree from goal {root_goal_id}"

        # Render the tree
        lines = []
        self._render_tree_node(tree, lines, "", is_last=True, critical_path_ids=critical_path_ids)

        # Add legend
        lines.append("")
        lines.append("Legend:")
        for rel_type, arrow in self.ARROWS.items():
            lines.append(f"  {arrow} : {rel_type}")
        lines.append("")
        for status, icon in self.STATUS_ICONS.items():
            lines.append(f"  {icon} : {status}")
        if show_critical_path:
            lines.append("  ★ : Critical path (highlighted)")

        return "\n".join(lines)

    def _render_tree_node(
        self,
        node: Dict[str, Any],
        lines: List[str],
        prefix: str,
        is_last: bool,
        critical_path_ids: Set[str],
    ) -> None:
        """
        Recursively render a tree node and its children.

        Args:
            node: Tree node dictionary
            lines: List to append rendered lines to
            prefix: Current line prefix for indentation
            is_last: Whether this node is the last child of its parent
            critical_path_ids: Set of goal IDs on the critical path
        """
        goal = node["goal"]
        is_critical = goal.id in critical_path_ids

        # Render this node
        conn = self.BOX_UL if is_last else self.BOX_VR
        connector = f"{prefix}{conn} "
        highlight = "★ " if is_critical else ""
        display_name = self._get_goal_display_name(goal)

        lines.append(f"{connector}{highlight}[{goal.domain}] {display_name}")

        # Render children
        children = node.get("children", [])
        new_prefix = prefix + (self.BOX_V if not is_last else "  ")

        for i, child in enumerate(children):
            edge = child.get("edge", {})
            edge_type = edge.get("type", "")
            arrow = self.ARROWS.get(edge_type, "→")
            strength_str = f" (strength: {edge.get('strength', 1.0):.1f})" if edge else ""

            # Render edge label
            child_prefix = new_prefix + (self.BOX_V if i < len(children) - 1 else self.BOX_UL)
            lines.append(f"{child_prefix}{arrow}{strength_str}")

            # Render child node
            self._render_tree_node(
                child, lines, new_prefix + "  ", i == len(children) - 1, critical_path_ids
            )

    def render_matrix(self, show_critical_path: bool = False) -> str:
        """
        Render the dependency graph as a matrix-style view.

        This shows goals in columns and their dependencies in rows,
        good for seeing cross-domain relationships.

        Args:
            show_critical_path: Whether to highlight critical path

        Returns:
            ASCII matrix representation
        """
        if not self.graph.nodes:
            return "No goals in graph"

        lines = []
        lines.append("╔" + "═" * 78 + "╗")
        lines.append("║" + " GOAL DEPENDENCY MATRIX ".center(78) + "║")
        lines.append("╚" + "═" * 78 + "╝")
        lines.append("")

        # Get critical path if requested
        critical_path_ids = set()
        if show_critical_path:
            try:
                path, _ = self.graph.find_critical_path()
                critical_path_ids = set(path)
            except ValueError:
                pass

        # Group by domain
        domains: Dict[str, List[GoalNode]] = {}
        for goal in self.graph.nodes.values():
            if goal.domain not in domains:
                domains[goal.domain] = []
            domains[goal.domain].append(goal)

        # Render by domain
        for domain in sorted(domains.keys()):
            emoji = self.DOMAIN_EMOJIS.get(domain, "📌")
            lines.append(f"{emoji} {domain.upper()} DOMAIN")
            lines.append(self.BOX_H * 80)

            for goal in domains[domain]:
                is_critical = goal.id in critical_path_ids
                critical_mark = "★ CRITICAL PATH" if is_critical else ""

                display_name = self._get_goal_display_name(goal, 50)
                lines.append(f"  {display_name} [{goal.priority}] {critical_mark}")

                # Show dependencies
                deps = self.graph.get_dependencies(goal.id)
                if deps:
                    for edge in deps:
                        dep_goal = self.graph.nodes.get(edge.from_goal_id)
                        if dep_goal:
                            arrow = self.ARROWS.get(edge.relationship_type, "→")
                            reason = f" - {edge.reason}" if edge.reason else ""
                            lines.append(
                                f"    {arrow} {self._get_goal_display_name(dep_goal, 40)}{reason}"
                            )

                # Show dependents
                dependents = self.graph.get_dependents(goal.id)
                if dependents:
                    lines.append(f"    Enables:")
                    for edge in dependents:
                        dep_goal = self.graph.nodes.get(edge.to_goal_id)
                        if dep_goal:
                            arrow = self.ARROWS.get(edge.relationship_type, "→")
                            reason = f" - {edge.reason}" if edge.reason else ""
                            lines.append(
                                f"      {arrow} {self._get_goal_display_name(dep_goal, 40)}{reason}"
                            )

                lines.append("")

        # Add legend
        lines.append("Legend:")
        for rel_type, arrow in self.ARROWS.items():
            lines.append(f"  {arrow} : {rel_type}")
        if show_critical_path:
            lines.append("  ★ CRITICAL PATH : Highlighted goals on longest completion path")

        return "\n".join(lines)

    def render_linear_flow(self, max_width: int = 80, show_critical_path: bool = False) -> str:
        """
        Render the dependency graph as a linear flow diagram.

        This creates horizontal ASCII art showing goal flows side by side,
        great for multi-track visualization.

        Example:
            Career Promotion ──┐
                              ├──→ Save $10k for Move
            House Savings ◄───┘    ↓
                              Buy House → Wellness: Create Home Routine

        Args:
            max_width: Maximum line width for the diagram
            show_critical_path: Whether to highlight critical path

        Returns:
            ASCII linear flow representation
        """
        if not self.graph.nodes:
            return "No goals in graph"

        lines = []
        lines.append("╔" + "=" * 78 + "╗")
        lines.append("║" + " GOAL FLOW DIAGRAM ".center(78) + "║")
        lines.append("╚" + "=" * 78 + "╝")
        lines.append("")

        # Get critical path if requested
        critical_path_ids = set()
        if show_critical_path:
            try:
                path, _ = self.graph.find_critical_path()
                critical_path_ids = set(path)
            except ValueError:
                pass

        # Find execution order
        try:
            execution_order = self.graph.topological_sort()
        except ValueError:
            # If there are cycles, use priority sorting
            execution_order = sorted(
                self.graph.nodes.keys(),
                key=lambda gid: (-self.graph.nodes[gid].priority, gid),
            )

        # Render goals in execution order with their connections
        current_lines = [""]  # Start with one line

        for i, goal_id in enumerate(execution_order):
            if goal_id not in self.graph.nodes:
                continue

            goal = self.graph.nodes[goal_id]
            is_critical = goal.id in critical_path_ids

            # Get display name
            emoji = self.DOMAIN_EMOJIS.get(goal.domain, "📌")
            status_icon = self.STATUS_ICONS.get(goal.status, "?")
            critical_mark = "★" if is_critical else ""
            title = self._truncate_text(goal.title, 25)

            # Create goal node text
            node_text = f"{emoji} {status_icon} {title}{critical_mark}"

            # Check if we need to branch (multiple dependents)
            dependents = [
                e
                for e in self.graph.get_dependents(goal.id)
                if e.relationship_type in ["enables", "requires"]
            ]

            # Find or create a line for this goal
            placed = False
            for line_idx, line in enumerate(current_lines):
                if not placed and len(line) < max_width // 2:
                    # Place goal here
                    current_lines[line_idx] = line + node_text

                    # Add arrows to dependents
                    if dependents:
                        arrow = self.ARROWS.get("enables", "→")
                        current_lines[line_idx] += f" {arrow}"

                        if len(dependents) > 1:
                            # Branching: create merge point
                            current_lines[line_idx] += "─┐"
                            for j, dep in enumerate(dependents):
                                if j == 0:
                                    current_lines[line_idx] += "\n"
                                    # Start new lines for each branch
                                    if j < len(current_lines):
                                        current_lines[j] = (
                                            f"{' ' * (len(line) + len(node_text))}  ├"
                                        )
                                    else:
                                        current_lines.append(
                                            f"{' ' * (len(line) + len(node_text))}  ├"
                                        )
                                else:
                                    # Add branches
                                    branch_prefix = "│   " * j
                                    current_lines[-1] += f"\n{branch_prefix}├"
                        else:
                            # Single continuation
                            current_lines[line_idx] += " "

                    placed = True
                    break

            if not placed:
                # Add new line for this goal
                current_lines.append(node_text + " ")

        lines.extend(current_lines)
        lines.append("")

        # Add legend
        lines.append("Legend:")
        for rel_type, arrow in self.ARROWS.items():
            lines.append(f"  {arrow} : {rel_type}")
        if show_critical_path:
            lines.append("  ★ CRITICAL PATH : Goals on the longest completion path")

        return "\n".join(lines)


# ==============================================================================
# Interactive Exploration System
# ==============================================================================


class InteractiveExplorer:
    """Interactive command-based exploration of dependency graphs."""

    COMMANDS = {
        "show": "Show all goals or a specific goal",
        "expand": "Expand a goal to show its dependencies and dependents",
        "collapse": "Collapse expanded view back to summary",
        "path": "Show the critical path for goal completion",
        "stats": "Display graph statistics",
        "help": "Show this help message",
        "quit": "Exit interactive mode",
    }

    def __init__(self, graph: GoalDependencyGraph):
        """Initialize the explorer with a dependency graph."""
        self.graph = graph
        self.current_view = "summary"  # summary, expanded
        self.selected_goal_id: Optional[str] = None

    def show_help(self) -> str:
        """Show help message with available commands."""
        lines = []
        lines.append("╔" + "═" * 78 + "╗")
        lines.append("║" + " INTERACTIVE EXPLORATION HELP ".center(78) + "║")
        lines.append("╚" + "═" * 78 + "╝")
        lines.append("")
        lines.append("Available commands:")
        for cmd, desc in self.COMMANDS.items():
            lines.append(f"  {cmd:10s} - {desc}")
        lines.append("")
        lines.append("Usage examples:")
        lines.append("  show                    # Show all goals")
        lines.append('  show g1                 # Show goal with ID "g1"')
        lines.append('  expand g1               # Expand goal "g1" to see connections')
        lines.append("  collapse                # Collapse back to summary view")
        return "\n".join(lines)

    def show_goals(self, goal_id: Optional[str] = None) -> str:
        """Show all goals or a specific goal."""
        if goal_id:
            # Show specific goal
            if goal_id not in self.graph.nodes:
                return f"Error: Goal '{goal_id}' not found"

            goal = self.graph.nodes[goal_id]
            lines = []
            lines.append(f"╔{'═' * 78}╗")
            lines.append(f"║{f' GOAL: {goal.title} '.center(78)}║")
            lines.append(f"╚{'═' * 78}╝")
            lines.append("")

            # Goal details
            emoji = ASCIIGraphRenderer.DOMAIN_EMOJIS.get(goal.domain, "📌")
            status_icon = ASCIIGraphRenderer.STATUS_ICONS.get(goal.status, "?")

            lines.append(f"ID:           {goal.id}")
            lines.append(f"Domain:       {emoji} {goal.domain}")
            lines.append(f"Status:       {status_icon} {goal.status}")
            lines.append(f"Priority:     {goal.priority}/10")
            if goal.estimated_effort:
                lines.append(f"Effort:       {goal.estimated_effort} hours/days")
            if goal.deadline:
                lines.append(f"Deadline:     {goal.deadline}")

            # Dependencies
            deps = self.graph.get_dependencies(goal_id)
            if deps:
                lines.append("")
                lines.append(f"Dependencies ({len(deps)}):")
                for edge in deps:
                    dep_goal = self.graph.nodes.get(edge.from_goal_id)
                    if dep_goal:
                        arrow = ASCIIGraphRenderer.ARROWS.get(edge.relationship_type, "→")
                        lines.append(
                            f"  {arrow} [{dep_goal.domain}] {dep_goal.title} "
                            f"(strength: {edge.strength:.1f})"
                        )
                        if edge.reason:
                            lines.append(f"      Reason: {edge.reason}")

            # Dependents
            dependents = self.graph.get_dependents(goal_id)
            if dependents:
                lines.append("")
                lines.append(f"Dependents ({len(dependents)}):")
                for edge in dependents:
                    dep_goal = self.graph.nodes.get(edge.to_goal_id)
                    if dep_goal:
                        arrow = ASCIIGraphRenderer.ARROWS.get(edge.relationship_type, "→")
                        lines.append(
                            f"  {arrow} [{dep_goal.domain}] {dep_goal.title} "
                            f"(strength: {edge.strength:.1f})"
                        )
                        if edge.reason:
                            lines.append(f"      Reason: {edge.reason}")

            return "\n".join(lines)
        else:
            # Show all goals summary
            lines = []
            lines.append("╔" + "═" * 78 + "╗")
            lines.append("║" + " ALL GOALS ".center(78) + "║")
            lines.append("╚" + "═" * 78 + "╝")
            lines.append("")

            # Group by domain
            domains: Dict[str, List[GoalNode]] = {}
            for goal in self.graph.nodes.values():
                if goal.domain not in domains:
                    domains[goal.domain] = []
                domains[goal.domain].append(goal)

            for domain in sorted(domains.keys()):
                emoji = ASCIIGraphRenderer.DOMAIN_EMOJIS.get(domain, "📌")
                lines.append(f"{emoji} {domain.upper()} ({len(domains[domain])} goals)")
                for goal in domains[domain]:
                    status_icon = ASCIIGraphRenderer.STATUS_ICONS.get(goal.status, "?")
                    lines.append(f"  {status_icon} [{goal.id}] P{goal.priority}: {goal.title}")
                lines.append("")

            return "\n".join(lines)

    def expand_goal(self, goal_id: str) -> str:
        """Expand a goal to show its dependencies and dependents."""
        if goal_id not in self.graph.nodes:
            return f"Error: Goal '{goal_id}' not found"

        self.selected_goal_id = goal_id
        self.current_view = "expanded"

        # Use renderer to create tree view centered on this goal
        renderer = ASCIIGraphRenderer(self.graph)
        lines = []

        # Show the tree
        lines.append(f"Expanded view of: {self.graph.nodes[goal_id].title} (ID: {goal_id})")
        lines.append("")

        # Show dependencies as tree going UP
        deps = self.graph.get_dependencies(goal_id)
        if deps:
            lines.append("DEPENDING ON (what this goal needs):")
            for edge in deps:
                dep_goal = self.graph.nodes.get(edge.from_goal_id)
                if dep_goal:
                    arrow = ASCIIGraphRenderer.ARROWS.get(edge.relationship_type, "→")
                    lines.append(f"  {arrow} {dep_goal.title}")
                    if edge.reason:
                        lines.append(f"      ({edge.reason})")
            lines.append("")

        # Show this goal
        emoji = ASCIIGraphRenderer.DOMAIN_EMOJIS.get(self.graph.nodes[goal_id].domain, "📌")
        lines.append(f"{emoji} ★ THIS GOAL: {self.graph.nodes[goal_id].title} ★")
        lines.append("")

        # Show dependents as tree going DOWN
        dependents = self.graph.get_dependents(goal_id)
        if dependents:
            lines.append("ENABLES (goals that depend on this one):")
            for edge in dependents:
                dep_goal = self.graph.nodes.get(edge.to_goal_id)
                if dep_goal:
                    arrow = ASCIIGraphRenderer.ARROWS.get(edge.relationship_type, "→")
                    lines.append(f"  {arrow} {dep_goal.title}")
                    if edge.reason:
                        lines.append(f"      ({edge.reason})")

        return "\n".join(lines)

    def collapse_view(self) -> str:
        """Collapse the expanded view back to summary."""
        self.current_view = "summary"
        self.selected_goal_id = None
        return "View collapsed. Showing summary."

    def show_critical_path(self) -> str:
        """Show the critical path for goal completion."""
        try:
            path, effort = self.graph.find_critical_path()

            lines = []
            lines.append("╔" + "=" * 78 + "╗")
            lines.append("║" + f" CRITICAL PATH (Total Effort: {effort:.1f}) ".center(78) + "║")
            lines.append("╚" + "=" * 78 + "╝")
            lines.append("")
            lines.append(
                "The critical path is the longest sequence of dependent goals that determines"
            )
            lines.append("the minimum time required to complete all goals. Goals on this path are")
            lines.append("critical for timely completion.")
            lines.append("")
            lines.append("Critical Path:")
            for i, goal_id in enumerate(path):
                if goal_id not in self.graph.nodes:
                    continue
                goal = self.graph.nodes[goal_id]
                emoji = ASCIIGraphRenderer.DOMAIN_EMOJIS.get(goal.domain, "📌")
                lines.append(f"  {i + 1}. {emoji} [{goal.domain}] {goal.title}")
                if goal.estimated_effort:
                    lines.append(f"      Effort: {goal.estimated_effort} hours/days")

            return "\n".join(lines)
        except ValueError as e:
            return f"Error finding critical path: {str(e)}"

    def show_stats(self) -> str:
        """Display graph statistics."""
        lines = []
        lines.append("╔" + "═" * 78 + "╗")
        lines.append("║" + " GRAPH STATISTICS ".center(78) + "║")
        lines.append("╚" + "═" * 78 + "╝")
        lines.append("")

        # Basic stats
        lines.append(f"Total Goals:         {len(self.graph.nodes)}")
        lines.append(f"Total Dependencies:  {len(self.graph.edges)}")

        # Domain breakdown
        domain_counts: Dict[str, int] = {}
        for goal in self.graph.nodes.values():
            domain_counts[goal.domain] = domain_counts.get(goal.domain, 0) + 1

        lines.append("")
        lines.append("Goals by Domain:")
        for domain, count in sorted(domain_counts.items()):
            emoji = ASCIIGraphRenderer.DOMAIN_EMOJIS.get(domain, "📌")
            lines.append(f"  {emoji} {domain.title()}: {count}")

        # Status breakdown
        status_counts: Dict[str, int] = {}
        for goal in self.graph.nodes.values():
            status_counts[goal.status] = status_counts.get(goal.status, 0) + 1

        lines.append("")
        lines.append("Goals by Status:")
        for status, count in sorted(status_counts.items()):
            icon = ASCIIGraphRenderer.STATUS_ICONS.get(status, "?")
            lines.append(f"  {icon} {status}: {count}")

        # Relationship type breakdown
        rel_counts: Dict[str, int] = {}
        for edge in self.graph.edges:
            rel_counts[edge.relationship_type] = rel_counts.get(edge.relationship_type, 0) + 1

        lines.append("")
        lines.append("Dependencies by Type:")
        for rel_type, count in sorted(rel_counts.items()):
            arrow = ASCIIGraphRenderer.ARROWS.get(rel_type, "→")
            lines.append(f"  {arrow} {rel_type}: {count}")

        # Cycle detection
        cycles = self.graph.detect_cycles()
        if cycles:
            lines.append("")
            lines.append(f"⚠ WARNING: {len(cycles)} circular dependency(ies) detected!")
        else:
            lines.append("")
            lines.append("✓ No circular dependencies detected")

        return "\n".join(lines)

    def execute_command(self, command: str) -> str:
        """
        Execute an interactive exploration command.

        Args:
            command: Command string (e.g., "show", "expand g1")

        Returns:
            Result of the command execution
        """
        parts = command.strip().split()
        if not parts:
            return "Please enter a command. Type 'help' for available commands."

        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else None

        if cmd == "help":
            return self.show_help()
        elif cmd == "show":
            return self.show_goals(arg)
        elif cmd == "expand":
            if not arg:
                return "Usage: expand <goal_id>"
            return self.expand_goal(arg)
        elif cmd == "collapse":
            return self.collapse_view()
        elif cmd == "path":
            return self.show_critical_path()
        elif cmd == "stats":
            return self.show_stats()
        elif cmd in ["quit", "exit"]:
            return "Exiting interactive mode..."
        else:
            return f"Unknown command: {cmd}. Type 'help' for available commands."


# ==============================================================================
# What-If Analysis Engine
# ==============================================================================


class WhatIfAnalyzer:
    """Performs what-if scenario analysis on goal graphs."""

    def __init__(self, graph: GoalDependencyGraph):
        """Initialize the analyzer with a dependency graph."""
        self.graph = graph

    def simulate_add_goal(
        self,
        goal_data: Dict[str, Any],
        dependencies: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """
        Simulate adding a new goal and analyze the impact.

        Args:
            goal_data: Dictionary with goal attributes (id, domain, title, etc.)
            dependencies: Optional list of dependency dictionaries

        Returns:
            Analysis report showing the impact of adding this goal
        """
        lines = []
        lines.append("╔" + "=" * 78 + "╗")
        lines.append(
            f"║ WHAT-IF ANALYSIS: ADD GOAL '{goal_data.get('title', 'Unknown')}' ".center(78) + "║"
        )
        lines.append("╚" + "=" * 78 + "╝")
        lines.append("")

        # Validate goal data
        required_fields = ["id", "domain", "title"]
        for field in required_fields:
            if field not in goal_data:
                return f"Error: Missing required field '{field}' in goal data"

        # Check for ID conflicts
        if goal_data["id"] in self.graph.nodes:
            return f"Error: Goal ID '{goal_data['id']}' already exists"

        # Create a copy of the graph for simulation
        sim_graph = GoalDependencyGraph()

        # Copy all existing nodes and edges
        for node in self.graph.nodes.values():
            sim_graph.add_goal(node)
        for edge in self.graph.edges:
            sim_graph.add_dependency(edge)

        # Add the new goal
        new_goal = GoalNode(
            id=goal_data["id"],
            domain=goal_data["domain"],
            title=goal_data["title"],
            priority=goal_data.get("priority", 5),
            status=goal_data.get("status", "pending"),
            estimated_effort=goal_data.get("estimated_effort"),
            deadline=goal_data.get("deadline"),
        )
        sim_graph.add_goal(new_goal)

        # Add dependencies if provided
        added_deps = []
        if dependencies:
            for dep_data in dependencies:
                # Validate that referenced goals exist
                if "from_goal_id" not in dep_data or "to_goal_id" not in dep_data:
                    continue
                if dep_data["from_goal_id"] not in sim_graph.nodes:
                    lines.append(
                        f"⚠ Warning: Referenced goal '{dep_data['from_goal_id']}' does not exist, skipping"
                    )
                if dep_data["to_goal_id"] not in sim_graph.nodes:
                    lines.append(
                        f"⚠ Warning: Referenced goal '{dep_data['to_goal_id']}' does not exist, skipping"
                    )

                edge = DependencyEdge(
                    from_goal_id=dep_data["from_goal_id"],
                    to_goal_id=dep_data["to_goal_id"],
                    relationship_type=dep_data.get("relationship_type", "enables"),
                    strength=dep_data.get("strength", 1.0),
                    reason=dep_data.get("reason"),
                )
                sim_graph.add_dependency(edge)
                added_deps.append(edge)

        lines.append("✓ Goal successfully added to simulation")
        lines.append("")
        lines.append(f"New Goal:")
        emoji = ASCIIGraphRenderer.DOMAIN_EMOJIS.get(new_goal.domain, "📌")
        lines.append(f"  {emoji} [{new_goal.domain}] {new_goal.title}")
        lines.append(f"      ID: {new_goal.id}")
        lines.append(f"      Priority: {new_goal.priority}/10")
        if new_goal.estimated_effort:
            lines.append(f"      Estimated Effort: {new_goal.estimated_effort} hours/days")
        if new_goal.deadline:
            lines.append(f"      Deadline: {new_goal.deadline}")

        if added_deps:
            lines.append("")
            lines.append(f"Added Dependencies ({len(added_deps)}):")
            for edge in added_deps:
                arrow = ASCIIGraphRenderer.ARROWS.get(edge.relationship_type, "→")
                from_goal = sim_graph.nodes.get(edge.from_goal_id)
                to_goal = sim_graph.nodes.get(edge.to_goal_id)
                if from_goal and to_goal:
                    lines.append(
                        f"  {arrow} [{from_goal.domain}] {from_goal.title} → "
                        f"[{to_goal.domain}] {to_goal.title}"
                    )

        # Check for cycles
        lines.append("")
        cycles = sim_graph.detect_cycles()
        if cycles:
            lines.append("⚠ WARNING: This change introduces circular dependencies!")
            for i, cycle in enumerate(cycles, 1):
                if new_goal.id in cycle:
                    titles = " → ".join(
                        [sim_graph.nodes[gid].title for gid in cycle if gid in sim_graph.nodes]
                    )
                    lines.append(f"  Cycle {i}: {titles} → (back to start)")
        else:
            lines.append("✓ No circular dependencies introduced")

        # Calculate new critical path
        try:
            old_path, old_effort = self.graph.find_critical_path()
            new_path, new_effort = sim_graph.find_critical_path()

            lines.append("")
            lines.append("Critical Path Impact:")
            if new_effort > old_effort:
                diff = new_effort - old_effort
                lines.append(
                    f"  ⚠ Critical path increased by {diff:.1f} hours/days "
                    f"(was {old_effort:.1f}, now {new_effort:.1f})"
                )
            elif new_effort < old_effort:
                diff = old_effort - new_effort
                lines.append(
                    f"  ✓ Critical path decreased by {diff:.1f} hours/days "
                    f"(was {old_effort:.1f}, now {new_effort:.1f})"
                )
            else:
                lines.append(f"  → Critical path unchanged at {new_effort:.1f} hours/days")

            lines.append("")
            if new_path != old_path:
                lines.append("  New critical path:")
                for i, goal_id in enumerate(new_path):
                    if goal_id not in sim_graph.nodes:
                        continue
                    goal = sim_graph.nodes[goal_id]
                    marker = "★ NEW" if goal.id == new_goal.id else ""
                    lines.append(f"    {i + 1}. [{goal.domain}] {goal.title} {marker}")
        except ValueError:
            lines.append("")
            lines.append("⚠ Critical path analysis skipped due to cycles")

        # Show impacted dependents
        if added_deps:
            lines.append("")
            lines.append("Goals Directly Affected:")
            for edge in added_deps:
                if edge.from_goal_id == new_goal.id:
                    # New goal enables others
                    affected = sim_graph.nodes.get(edge.to_goal_id)
                    if affected:
                        lines.append(f"  • {affected.title}")
                        lines.append(f"    Now has an additional enabler: {new_goal.title}")
                elif edge.to_goal_id == new_goal.id:
                    # New goal depends on others
                    affected = sim_graph.nodes.get(edge.from_goal_id)
                    if affected:
                        lines.append(f"  • {affected.title}")
                        lines.append(f"    Now enables: {new_goal.title}")

        return "\n".join(lines)

    def simulate_remove_goal(self, goal_id: str) -> str:
        """
        Simulate removing a goal and analyze cascading effects.

        Args:
            goal_id: ID of the goal to remove

        Returns:
            Analysis report showing the impact of removing this goal
        """
        if goal_id not in self.graph.nodes:
            return f"Error: Goal '{goal_id}' not found"

        lines = []
        goal = self.graph.nodes[goal_id]

        lines.append("╔" + "=" * 78 + "╗")
        lines.append(f"║ WHAT-IF ANALYSIS: REMOVE GOAL '{goal.title}' ".center(78) + "║")
        lines.append("╚" + "=" * 78 + "╝")
        lines.append("")

        # Get dependents before removal
        dependents = self.graph.get_dependents(goal_id)
        dependencies = self.graph.get_dependencies(goal_id)

        lines.append(f"Goal to remove:")
        emoji = ASCIIGraphRenderer.DOMAIN_EMOJIS.get(goal.domain, "📌")
        lines.append(f"  {emoji} [{goal.domain}] {goal.title}")
        lines.append(f"      ID: {goal.id}")
        lines.append("")

        # Create a copy of the graph for simulation
        sim_graph = GoalDependencyGraph()

        # Copy all existing nodes and edges
        for node in self.graph.nodes.values():
            sim_graph.add_goal(node)
        for edge in self.graph.edges:
            sim_graph.add_dependency(edge)

        # Remove the goal
        sim_graph.remove_goal(goal_id)

        lines.append("✓ Goal removed from simulation")
        lines.append("")

        # Analyze impact on dependents (goals that depended on this one)
        if dependents:
            lines.append(f"⚠ IMPACT: {len(dependents)} goal(s) that depended on this one:")
            for edge in dependents:
                if edge.relationship_type == "requires":
                    # Critical impact
                    dep_goal = self.graph.nodes.get(edge.to_goal_id)
                    if dep_goal:
                        lines.append("")
                        lines.append(f"  🚫 BLOCKED: {dep_goal.title}")
                        lines.append(
                            f"      This goal REQUIRED '{goal.title}' and cannot proceed without it"
                        )
                elif edge.relationship_type == "enables":
                    # Moderate impact
                    dep_goal = self.graph.nodes.get(edge.to_goal_id)
                    if dep_goal:
                        lines.append("")
                        lines.append(f"  ⚠ AFFECTED: {dep_goal.title}")
                        lines.append(
                            f"      This goal was ENABLED by '{goal.title}' and will be harder to complete"
                        )
                elif edge.relationship_type == "supports":
                    # Minor impact
                    dep_goal = self.graph.nodes.get(edge.to_goal_id)
                    if dep_goal:
                        lines.append("")
                        lines.append(f"  → SUPPORTED: {dep_goal.title}")
                        lines.append(
                            f"      This goal was SUPPORTED by '{goal.title}' and is less impacted"
                        )
                elif edge.relationship_type == "conflicts":
                    # Positive impact
                    dep_goal = self.graph.nodes.get(edge.to_goal_id)
                    if dep_goal:
                        lines.append("")
                        lines.append(f"  ✓ RELIEVED: {dep_goal.title}")
                        lines.append(
                            f"      This goal CONFLICTED with '{goal.title}' and may now have fewer obstacles"
                        )
        else:
            lines.append("✓ No other goals depended on this one")
            lines.append("")

        # Analyze impact on dependencies (goals that this goal depended on)
        if dependencies:
            lines.append("")
            lines.append(f"Goals that '{goal.title}' depended on:")
            for edge in dependencies:
                dep_goal = self.graph.nodes.get(edge.from_goal_id)
                if dep_goal:
                    lines.append(f"  • {dep_goal.title}")
                    lines.append(f"      This goal is no longer blocking '{goal.title}'")

        # Check if cycles were resolved
        old_cycles = self.graph.detect_cycles()
        new_cycles = sim_graph.detect_cycles()

        if len(new_cycles) < len(old_cycles):
            resolved = len(old_cycles) - len(new_cycles)
            lines.append("")
            lines.append(f"✓ Resolved {resolved} circular dependency(ies)")

        # Calculate new critical path
        try:
            old_path, old_effort = self.graph.find_critical_path()
            new_path, new_effort = sim_graph.find_critical_path()

            lines.append("")
            lines.append("Critical Path Impact:")
            if new_effort < old_effort:
                diff = old_effort - new_effort
                lines.append(
                    f"  ✓ Critical path decreased by {diff:.1f} hours/days "
                    f"(was {old_effort:.1f}, now {new_effort:.1f})"
                )
            elif new_effort > old_effort:
                diff = new_effort - old_effort
                lines.append(
                    f"  ⚠ Critical path increased by {diff:.1f} hours/days "
                    f"(was {old_effort:.1f}, now {new_effort:.1f})"
                )
            else:
                lines.append(f"  → Critical path unchanged at {new_effort:.1f} hours/days")

            lines.append("")
            if new_path != old_path:
                lines.append("  New critical path:")
                for i, gid in enumerate(new_path):
                    if gid not in sim_graph.nodes:
                        continue
                    g = sim_graph.nodes[gid]
                    lines.append(f"    {i + 1}. [{g.domain}] {g.title}")
        except ValueError:
            lines.append("")
            lines.append("⚠ Critical path analysis skipped due to cycles")

        return "\n".join(lines)


# ==============================================================================
# Dependency Report Generator
# ==============================================================================


def generate_dependency_report(
    graph: GoalDependencyGraph,
    user_id: str,
    include_visualizations: bool = True,
    backend=None,
) -> str:
    """
    Generate a comprehensive dependency analysis report.

    This report includes:
    - Summary statistics
    - Domain breakdown
    - Critical path analysis
    - Dependency matrix
    - Risk assessment (blocked goals, conflicts)
    - Recommendations

    Args:
        graph: The goal dependency graph
        user_id: User ID for the report
        include_visualizations: Whether to include ASCII visualizations
        backend: Optional backend for saving the report

    Returns:
        Comprehensive dependency analysis report
    """
    lines = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines.append("╔" + "=" * 78 + "╗")
    lines.append(f"║{f' COMPREHENSIVE DEPENDENCY REPORT - {user_id} '.center(78)}║")
    lines.append(f"║{f' Generated: {timestamp} '.center(78)}║")
    lines.append("╚" + "=" * 78 + "╝")
    lines.append("")

    # Executive Summary
    lines.append("EXECUTIVE SUMMARY")
    lines.append("=" * 80)
    lines.append("")
    total_goals = len(graph.nodes)
    total_deps = len(graph.edges)

    # Calculate metrics
    avg_priority = sum(g.priority for g in graph.nodes.values()) / total_goals if total_goals else 0
    completed_count = sum(1 for g in graph.nodes.values() if g.status == "completed")
    completion_rate = (completed_count / total_goals * 100) if total_goals else 0

    lines.append(f"Total Goals:           {total_goals}")
    lines.append(f"Total Dependencies:    {total_deps}")
    lines.append(f"Average Priority:      {avg_priority:.1f}/10")
    lines.append(f"Completed Goals:       {completed_count}/{total_goals} ({completion_rate:.1f}%)")
    lines.append("")

    # Identify risks
    cycles = graph.detect_cycles()
    if cycles:
        lines.append("⚠ RISKS IDENTIFIED:")
        lines.append(
            f"  • {len(cycles)} circular dependency(ies) found - these create impossible execution sequences"
        )
        for i, cycle in enumerate(cycles[:3], 1):  # Show max 3 cycles
            titles = " → ".join([graph.nodes[gid].title for gid in cycle if gid in graph.nodes])
            lines.append(f"    {i}. {titles}")
        if len(cycles) > 3:
            lines.append(f"    ... and {len(cycles) - 3} more cycles")
        lines.append("")

    # Check for conflicts
    conflicts = [e for e in graph.edges if e.relationship_type == "conflicts"]
    if conflicts:
        lines.append(
            f"  • {len(conflicts)} conflicting goal pair(s) found - these compete for resources"
        )
        lines.append("")

    # Check for blocked goals
    blocked_goals = []
    for goal_id, goal in graph.nodes.items():
        deps = [e for e in graph.get_dependencies(goal_id) if e.relationship_type == "requires"]
        incomplete_deps = [
            d
            for d in deps
            if graph.nodes.get(d.from_goal_id) and graph.nodes[d.from_goal_id].status != "completed"
        ]
        if incomplete_deps and goal.status == "pending":
            blocked_goals.append(goal)
    if blocked_goals:
        lines.append(
            f"  • {len(blocked_goals)} goal(s) currently blocked by incomplete dependencies"
        )
        for i, goal in enumerate(blocked_goals[:3], 1):
            lines.append(f"    {i}. {goal.title}")
        if len(blocked_goals) > 3:
            lines.append(f"    ... and {len(blocked_goals) - 3} more blocked goals")
        lines.append("")
    else:
        lines.append("✓ No critical risks identified")
        lines.append("")

    # Domain Analysis
    lines.append("")
    lines.append("DOMAIN ANALYSIS")
    lines.append("=" * 80)
    lines.append("")

    domain_stats: Dict[str, Dict[str, Any]] = {}
    for goal in graph.nodes.values():
        if goal.domain not in domain_stats:
            domain_stats[goal.domain] = {
                "goals": [],
                "avg_priority": 0,
                "completed": 0,
            }
        domain_stats[goal.domain]["goals"].append(goal)
        if goal.status == "completed":
            domain_stats[goal.domain]["completed"] += 1

    for domain, stats in sorted(domain_stats.items()):
        goals = stats["goals"]
        avg_priority = sum(g.priority for g in goals) / len(goals)
        completion_rate = (stats["completed"] / len(goals)) * 100

        emoji = ASCIIGraphRenderer.DOMAIN_EMOJIS.get(domain, "📌")
        lines.append(f"{emoji} {domain.upper()}")
        lines.append(f"  Total Goals:     {len(goals)}")
        lines.append(
            f"  Completed:       {stats['completed']}/{len(goals)} ({completion_rate:.1f}%)"
        )
        lines.append(f"  Avg Priority:    {avg_priority:.1f}/10")

        # Count dependencies
        domain_goal_ids = set(g.id for g in goals)
        internal_deps = sum(
            1
            for e in graph.edges
            if e.from_goal_id in domain_goal_ids and e.to_goal_id in domain_goal_ids
        )
        outgoing_deps = sum(
            1
            for e in graph.edges
            if e.from_goal_id in domain_goal_ids and e.to_goal_id not in domain_goal_ids
        )
        incoming_deps = sum(
            1
            for e in graph.edges
            if e.from_goal_id not in domain_goal_ids and e.to_goal_id in domain_goal_ids
        )

        lines.append(f"  Internal Deps:   {internal_deps}")
        lines.append(f"  Outgoing Deps:  {outgoing_deps} (to other domains)")
        lines.append(f"  Incoming Deps:  {incoming_deps} (from other domains)")
        lines.append("")

    # Critical Path Analysis
    try:
        critical_path, total_effort = graph.find_critical_path()

        lines.append("CRITICAL PATH ANALYSIS")
        lines.append("=" * 80)
        lines.append("")
        lines.append(f"The critical path represents the longest sequence of dependent goals.")
        lines.append(f"Completing all goals requires at least {total_effort:.1f} hours/days.")
        lines.append("")
        lines.append("Critical Path Goals:")
        for i, goal_id in enumerate(critical_path):
            if goal_id not in graph.nodes:
                continue
            goal = graph.nodes[goal_id]
            emoji = ASCIIGraphRenderer.DOMAIN_EMOJIS.get(goal.domain, "📌")
            status_icon = ASCIIGraphRenderer.STATUS_ICONS.get(goal.status, "?")

            lines.append(f"{i + 1}. {emoji} [{goal.domain}] {goal.title} {status_icon}")
            if goal.estimated_effort:
                lines.append(f"   Effort: {goal.estimated_effort} hours/days")

        # Identify bottlenecks (high effort goals on critical path)
        if len(critical_path) > 1:
            max_effort = max(
                (graph.nodes[gid].estimated_effort or 0)
                for gid in critical_path
                if gid in graph.nodes
            )
            if max_effort > 0:
                bottlenecks = [
                    graph.nodes[gid]
                    for gid in critical_path
                    if gid in graph.nodes and (graph.nodes[gid].estimated_effort or 0) == max_effort
                ]
                if bottlenecks:
                    lines.append("")
                    lines.append("⚠ BOTTLENECKS (high effort goals on critical path):")
                    for goal in bottlenecks:
                        lines.append(f"  • {goal.title} ({max_effort} hours/days)")

        lines.append("")
    except ValueError as e:
        lines.append("")
        lines.append("CRITICAL PATH ANALYSIS")
        lines.append("=" * 80)
        lines.append("")
        lines.append(f"⚠ Cannot calculate critical path: {str(e)}")
        lines.append("")

    # Dependency Matrix
    if include_visualizations:
        renderer = ASCIIGraphRenderer(graph)
        lines.append("VISUALIZATION: DEPENDENCY MATRIX")
        lines.append("=" * 80)
        lines.append("")
        matrix = renderer.render_matrix(show_critical_path=True)
        lines.append(matrix)
        lines.append("")

    # Recommendations
    lines.append("")
    lines.append("RECOMMENDATIONS")
    lines.append("=" * 80)
    lines.append("")
    recommendations = []

    # Check for cycles
    if cycles:
        recommendations.append(
            "🔴 HIGH PRIORITY: Resolve circular dependencies to create a valid execution plan"
        )

    # Check for conflicts
    if conflicts:
        recommendations.append("🟡 MEDIUM PRIORITY: Review and resolve conflicting goal pairs")

    # Check for blocked goals
    if blocked_goals:
        recommendations.append(
            "🟡 MEDIUM PRIORITY: Focus on completing dependencies for blocked goals"
        )

    # Check critical path
    try:
        if len(graph.find_critical_path()[0]) > 5:
            recommendations.append(
                "🟢 SUGGESTION: Consider breaking down critical path goals into smaller milestones"
            )
    except ValueError:
        pass

    # Check for under-prioritized domains
    if domain_stats:
        completion_rates = {
            domain: (stats["completed"] / len(stats["goals"])) * 100
            for domain, stats in domain_stats.items()
        }
        if completion_rates:
            min_domain = min(completion_rates, key=completion_rates.get)
            if completion_rates[min_domain] < 50 and len(domain_stats) > 1:
                recommendations.append(
                    f"🟢 SUGGESTION: Consider prioritizing {min_domain} domain "
                    f"(currently at {completion_rates[min_domain]:.1f}% completion)"
                )

    if recommendations:
        for rec in recommendations:
            lines.append(rec)
    else:
        lines.append("✓ No specific recommendations - your goal structure looks healthy!")

    # Save report if backend provided
    if backend:
        try:
            today = date.today()
            path = f"dependency_reports/{user_id}/{today}_report.txt"
            content = "\n".join(lines)

            if hasattr(backend, "write_file"):
                backend.write_file(path, content)
            else:
                workspace_path = (
                    Path(backend.root_dir) if hasattr(backend, "root_dir") else Path("workspace")
                )
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content)

            lines.append("")
            lines.append(f"Report saved to: {path}")
        except Exception as e:
            lines.append("")
            lines.append(f"Note: Could not save report - {str(e)}")

    return "\n".join(lines)


# ==============================================================================
# Visualization Tools Factory
# ==============================================================================


def create_viz_tools(backend=None):
    """
    Create goal dependency visualization tools with shared FilesystemBackend instance.

    These tools enable the AI Life Coach to:
    - Render dependency graphs as ASCII art
    - Explore graphs interactively with commands
    - Highlight critical paths in visualizations
    - Perform what-if analysis on goal changes
    - Generate comprehensive dependency reports

    Args:
        backend: Optional FilesystemBackend instance. If None, uses get_backend()

    Returns:
        Tuple of visualization tools (render_ascii_graph,
                                     explore_dependencies_interactive,
                                     highlight_critical_path,
                                     what_if_add_goal,
                                     what_if_remove_goal,
                                     generate_dependency_report_tool)
    """
    if backend is None:
        backend = get_backend()

    workspace_path = Path(backend.root_dir) if hasattr(backend, "root_dir") else Path("workspace")

    @tool
    def render_ascii_graph(
        user_id: str,
        goal_dependencies_path: Optional[str] = None,
        format_type: str = "tree",
        show_critical_path: bool = False,
    ) -> str:
        """Render dependency graph as ASCII art.

        Creates beautiful text-based visualizations of goal dependencies
        without requiring external plotting libraries.

        Args:
            user_id: The user's unique identifier
            goal_dependencies_path: Optional path to existing dependency graph JSON.
                                    If None, uses the most recent one.
            format_type: Visualization format - 'tree', 'matrix', or 'linear'
            show_critical_path: Whether to highlight the critical path

        Returns:
            ASCII art visualization of the dependency graph

        Example:
            >>> render_ascii_graph("user_123", format_type="tree", show_critical_path=True)
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if format_type not in ["tree", "matrix", "linear"]:
            return "Error: format_type must be 'tree', 'matrix', or 'linear'"

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

            # Render using appropriate format
            renderer = ASCIIGraphRenderer(graph)

            if format_type == "tree":
                viz = renderer.render_tree(show_critical_path=show_critical_path)
            elif format_type == "matrix":
                viz = renderer.render_matrix(show_critical_path=show_critical_path)
            else:  # linear
                viz = renderer.render_linear_flow(
                    max_width=80, show_critical_path=show_critical_path
                )

            return viz

        except Exception as e:
            return f"Error rendering ASCII graph: {str(e)}"

    @tool
    def explore_dependencies_interactive(
        user_id: str,
        command: str,
        goal_dependencies_path: Optional[str] = None,
    ) -> str:
        """Interactively explore dependency graphs with commands.

        Provides an interactive command-based interface for exploring
        goal dependencies. Commands include: show, expand, collapse,
        path, stats, help.

        Args:
            user_id: The user's unique identifier
            command: Command string (e.g., "show", "expand g1")
            goal_dependencies_path: Optional path to existing dependency graph JSON.
                                    If None, uses the most recent one.

        Returns:
            Result of command execution

        Example:
            >>> explore_dependencies_interactive("user_123", "show")
            >>> explore_dependencies_interactive("user_123", "expand g1")
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not command or not isinstance(command, str):
            return "Error: command must be a non-empty string"

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

            # Execute command using explorer
            explorer = InteractiveExplorer(graph)
            return explorer.execute_command(command)

        except Exception as e:
            return f"Error exploring dependencies: {str(e)}"

    @tool
    def highlight_critical_path(
        user_id: str,
        goal_dependencies_path: Optional[str] = None,
    ) -> str:
        """Visualize the critical path with emphasis markers.

        Shows the longest sequence of dependent goals that determines
        the minimum time required to complete all goals, with visual
        emphasis on critical path items.

        Args:
            user_id: The user's unique identifier
            goal_dependencies_path: Optional path to existing dependency graph JSON.
                                    If None, uses the most recent one.

        Returns:
            Visualization with critical path highlighted

        Example:
            >>> highlight_critical_path("user_123")
        """
        return render_ascii_graph(
            user_id=user_id,
            goal_dependencies_path=goal_dependencies_path,
            format_type="tree",
            show_critical_path=True,
        )

    @tool
    def what_if_add_goal(
        user_id: str,
        goal_data: Dict[str, Any],
        dependencies: Optional[List[Dict[str, Any]]] = None,
        goal_dependencies_path: Optional[str] = None,
    ) -> str:
        """Simulate adding a goal and show impact.

        Performs what-if analysis to understand how adding a new goal
        would affect the dependency structure, critical path, and other goals.

        Args:
            user_id: The user's unique identifier
            goal_data: Dictionary with goal attributes (id, domain, title, etc.)
            dependencies: Optional list of dependency dictionaries
            goal_dependencies_path: Optional path to existing dependency graph JSON.
                                    If None, uses the most recent one.

        Returns:
            Analysis report showing impact of adding the goal

        Example:
            >>> what_if_add_goal(
            ...     "user_123",
            ...     {"id": "g_new", "domain": "wellness", "title": "Run marathon"},
            ...     [{"from_goal_id": "g_new", "to_goal_id": "g1",
            ...      "relationship_type": "supports"}]
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not goal_data or not isinstance(goal_data, dict):
            return "Error: goal_data must be a non-empty dictionary"

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

            # Perform what-if analysis
            analyzer = WhatIfAnalyzer(graph)
            return analyzer.simulate_add_goal(goal_data, dependencies)

        except Exception as e:
            return f"Error in what-if analysis (add goal): {str(e)}"

    @tool
    def what_if_remove_goal(
        user_id: str,
        goal_id: str,
        goal_dependencies_path: Optional[str] = None,
    ) -> str:
        """Simulate removing a goal and show cascading effects.

        Performs what-if analysis to understand how removing an existing
        goal would affect dependent goals and the overall structure.

        Args:
            user_id: The user's unique identifier
            goal_id: ID of the goal to remove
            goal_dependencies_path: Optional path to existing dependency graph JSON.
                                    If None, uses the most recent one.

        Returns:
            Analysis report showing impact of removing the goal

        Example:
            >>> what_if_remove_goal("user_123", "g1")
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not goal_id or not isinstance(goal_id, str):
            return "Error: goal_id must be a non-empty string"

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

            # Perform what-if analysis
            analyzer = WhatIfAnalyzer(graph)
            return analyzer.simulate_remove_goal(goal_id)

        except Exception as e:
            return f"Error in what-if analysis (remove goal): {str(e)}"

    @tool
    def generate_dependency_report_tool(
        user_id: str,
        goal_dependencies_path: Optional[str] = None,
        include_visualizations: bool = True,
    ) -> str:
        """Generate comprehensive dependency analysis report.

        Creates a detailed report covering all aspects of the goal
        dependency structure including statistics, critical path,
        domain analysis, risks, and recommendations.

        Args:
            user_id: The user's unique identifier
            goal_dependencies_path: Optional path to existing dependency graph JSON.
                                    If None, uses the most recent one.
            include_visualizations: Whether to include ASCII visualizations

        Returns:
            Comprehensive dependency analysis report
            Saved to dependency_reports/{user_id}/

        Example:
            >>> generate_dependency_report_tool("user_123", include_visualizations=True)
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

            # Generate report
            return generate_dependency_report(graph, user_id, include_visualizations, backend)

        except Exception as e:
            return f"Error generating dependency report: {str(e)}"

    return (
        render_ascii_graph,
        explore_dependencies_interactive,
        highlight_critical_path,
        what_if_add_goal,
        what_if_remove_goal,
        generate_dependency_report_tool,
    )
