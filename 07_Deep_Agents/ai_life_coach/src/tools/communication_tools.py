"""
Subagent Communication Protocol Tools for AI Life Coach.

This module implements the communication protocol between specialist subagents
and the coordinator agent. It provides structured message formats, result aggregation,
conflict resolution, cross-consultation triggers, and unified response generation.

Based on research in:
- Multi-Agent Communication Protocols (MCP, A2A, ACP)
- Agent result aggregation patterns
- Conflict resolution strategies in multi-agent systems
- Deep Agents subagent communication best practices

Key Features:
1. Structured Message Format: Standardized JSON-like format for subagent responses
2. Result Aggregation: Combining outputs from multiple specialists intelligently
3. Conflict Resolution: Handling competing recommendations across domains
4. Cross-Consultation Triggers: Detecting when specialists should consult each other
5. Unified Response Generation: Creating cohesive responses from multiple subagent outputs

Communication Pattern:
    Coordinator → Specialist: "Analyze user's career goals"
    Specialist → Coordinator: {
        "analysis": "...",
        "recommendations": [...],
        "synergies_with_other_domains": [...],
        "conflicts_with_other_domains": [...]
    }
"""

from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
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
# Data Structures for Subagent Communication
# ==============================================================================


class SpecialistMessage:
    """
    Standardized message format from specialist subagents to coordinator.

    This structure ensures consistent communication across all specialists:
    - Career Specialist
    - Relationship Specialist
    - Finance Specialist
    - Wellness Specialist

    Attributes:
        specialist_name: Name of the specialist (e.g., "career-specialist")
        timestamp: When the message was created
        user_query: The original query from the coordinator
        analysis: Specialist's detailed analysis of the situation
        recommendations: List of actionable recommendations
        synergies_with_other_domains: How this specialist's work supports other domains
        conflicts_with_other_domains: Potential conflicts with recommendations from other domains
        confidence_level: Specialist's confidence in their analysis (0-1 scale)
        requires_cross_consultation: Whether this specialist needs input from others
        metadata: Additional context or data
    """

    def __init__(
        self,
        specialist_name: str,
        user_query: str,
        analysis: str,
        recommendations: List[Dict[str, Any]],
        synergies_with_other_domains: Optional[List[Dict[str, Any]]] = None,
        conflicts_with_other_domains: Optional[List[Dict[str, Any]]] = None,
        confidence_level: float = 0.8,
        requires_cross_consultation: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.specialist_name = specialist_name
        self.timestamp = datetime.now().isoformat()
        self.user_query = user_query
        self.analysis = analysis
        self.recommendations = recommendations or []
        self.synergies_with_other_domains = synergies_with_other_domains or []
        self.conflicts_with_other_domains = conflicts_with_other_domains or []
        self.confidence_level = max(0.0, min(1.0, confidence_level))  # Clamp to [0, 1]
        self.requires_cross_consultation = requires_cross_consultation
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for JSON serialization."""
        return {
            "specialist_name": self.specialist_name,
            "timestamp": self.timestamp,
            "user_query": self.user_query,
            "analysis": self.analysis,
            "recommendations": self.recommendations,
            "synergies_with_other_domains": self.synergies_with_other_domains,
            "conflicts_with_other_domains": self.conflicts_with_other_domains,
            "confidence_level": self.confidence_level,
            "requires_cross_consultation": self.requires_cross_consultation,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SpecialistMessage":
        """Create SpecialistMessage from dictionary."""
        return cls(
            specialist_name=data["specialist_name"],
            user_query=data.get("user_query", ""),
            analysis=data["analysis"],
            recommendations=data.get("recommendations", []),
            synergies_with_other_domains=data.get("synergies_with_other_domains", []),
            conflicts_with_other_domains=data.get("conflicts_with_other_domains", []),
            confidence_level=data.get("confidence_level", 0.8),
            requires_cross_consultation=data.get("requires_cross_consultation", False),
            metadata=data.get("metadata", {}),
        )


class AggregatedResults:
    """
    Container for aggregated results from multiple specialists.

    This structure holds collected specialist messages and provides
    methods for analysis, conflict resolution, and unified response generation.
    """

    def __init__(self, user_id: str, original_query: str):
        self.user_id = user_id
        self.original_query = original_query
        self.timestamp = datetime.now().isoformat()
        self.messages: Dict[str, SpecialistMessage] = {}  # specialist_name -> message
        self.conflicts_detected: List[Dict[str, Any]] = []
        self.synergies_identified: List[Dict[str, Any]] = []

    def add_message(self, message: SpecialistMessage) -> None:
        """Add a specialist message to the results."""
        self.messages[message.specialist_name] = message

    def get_domain_messages(self, domains: List[str]) -> List[SpecialistMessage]:
        """Get messages from specific domains."""
        domain_map = {
            "career": "career-specialist",
            "relationship": "relationship-specialist",
            "finance": "finance-specialist",
            "wellness": "wellness-specialist",
        }
        specialist_names = [domain_map.get(d, d) for d in domains]
        return [msg for name, msg in self.messages.items() if name in specialist_names]

    def to_dict(self) -> Dict[str, Any]:
        """Convert aggregated results to dictionary."""
        return {
            "user_id": self.user_id,
            "original_query": self.original_query,
            "timestamp": self.timestamp,
            "specialist_count": len(self.messages),
            "messages": {name: msg.to_dict() for name, msg in self.messages.items()},
            "conflicts_detected": self.conflicts_detected,
            "synergies_identified": self.synergies_identified,
        }


# ==============================================================================
# Conflict Resolution Strategies
# ==============================================================================


class ConflictResolutionStrategy:
    """Base class for conflict resolution strategies."""

    def resolve(
        self,
        conflicts: List[Dict[str, Any]],
        messages: Dict[str, SpecialistMessage],
    ) -> List[Dict[str, Any]]:
        """Resolve conflicts and return resolution recommendations."""
        raise NotImplementedError


class PriorityBasedResolution(ConflictResolutionStrategy):
    """
    Resolve conflicts based on specialist priority and confidence.

    Higher priority domains (career, finance) may take precedence over
    lower priority ones when conflicts exist.
    """

    def resolve(
        self,
        conflicts: List[Dict[str, Any]],
        messages: Dict[str, SpecialistMessage],
    ) -> List[Dict[str, Any]]:
        """Resolve conflicts using priority-based approach."""
        resolutions = []

        # Domain priorities (higher number = higher priority)
        domain_priorities = {
            "career-specialist": 4,
            "finance-specialist": 3,
            "wellness-specialist": 2,
            "relationship-specialist": 1,
        }

        for conflict in conflicts:
            specialist_1 = conflict.get("specialist_1")
            specialist_2 = conflict.get("specialist_2")

            priority_1 = domain_priorities.get(specialist_1, 0)
            priority_2 = domain_priorities.get(specialist_2, 0)

            msg1 = messages.get(specialist_1)
            msg2 = messages.get(specialist_2)

            if not msg1 or not msg2:
                continue

            # Resolution logic
            if priority_1 > priority_2:
                preferred_specialist = specialist_1
                rationale = f"{specialist_1} has higher domain priority"
            elif priority_2 > priority_1:
                preferred_specialist = specialist_2
                rationale = f"{specialist_2} has higher domain priority"
            else:
                # Equal priorities, use confidence level
                if msg1.confidence_level > msg2.confidence_level:
                    preferred_specialist = specialist_1
                    rationale = f"{specialist_1} has higher confidence"
                else:
                    preferred_specialist = specialist_2
                    rationale = f"{specialist_2} has higher confidence"

            resolutions.append(
                {
                    "conflict": conflict,
                    "resolution_type": "priority_based",
                    "preferred_specialist": preferred_specialist,
                    "rationale": rationale,
                    "suggested_action": f"Prioritize {preferred_specialist}'s recommendation",
                }
            )

        return resolutions


class ConsensusBasedResolution(ConflictResolutionStrategy):
    """
    Resolve conflicts by seeking consensus or compromise.

    When specialists disagree, this strategy looks for middle ground
    or suggests a sequential approach.
    """

    def resolve(
        self,
        conflicts: List[Dict[str, Any]],
        messages: Dict[str, SpecialistMessage],
    ) -> List[Dict[str, Any]]:
        """Resolve conflicts using consensus-based approach."""
        resolutions = []

        for conflict in conflicts:
            specialist_1 = conflict.get("specialist_1")
            specialist_2 = conflict.get("specialist_2")

            msg1 = messages.get(specialist_1)
            msg2 = messages.get(specialist_2)

            if not msg1 or not msg2:
                continue

            # Look for synergies that might inform compromise
            shared_synergies = []
            for syn in msg1.synergies_with_other_domains:
                if specialist_2 in syn.get("domain", ""):
                    shared_synergies.append(syn)

            # Suggest compromise or sequential approach
            if shared_synergies:
                resolution_type = "compromise"
                suggested_action = (
                    f"Find compromise leveraging shared interests: "
                    f"{', '.join([s.get('description', '') for s in shared_synergies[:2]])}"
                )
            else:
                resolution_type = "sequential"
                suggested_action = (
                    f"Address {specialist_1}'s concern first, then revisit "
                    f"{specialist_2}'s recommendation"
                )

            resolutions.append(
                {
                    "conflict": conflict,
                    "resolution_type": resolution_type,
                    "rationale": "Seeking consensus or balanced approach",
                    "suggested_action": suggested_action,
                }
            )

        return resolutions


class HybridResolution(ConflictResolutionStrategy):
    """
    Hybrid resolution combining multiple strategies.

    Uses priority-based for critical conflicts and consensus-based
    for moderate conflicts.
    """

    def __init__(self):
        self.priority_resolver = PriorityBasedResolution()
        self.consensus_resolver = ConsensusBasedResolution()

    def resolve(
        self,
        conflicts: List[Dict[str, Any]],
        messages: Dict[str, SpecialistMessage],
    ) -> List[Dict[str, Any]]:
        """Resolve conflicts using hybrid approach."""
        resolutions = []

        for conflict in conflicts:
            severity = conflict.get("severity", "medium")

            if severity == "high":
                # Use priority-based for high-severity conflicts
                result = self.priority_resolver.resolve([conflict], messages)
            else:
                # Use consensus-based for moderate conflicts
                result = self.consensus_resolver.resolve([conflict], messages)

            resolutions.extend(result)

        return resolutions


# ==============================================================================
# Cross-Consultation Triggers
# ==============================================================================


def detect_cross_consultation_needs(
    messages: Dict[str, SpecialistMessage],
) -> List[Dict[str, Any]]:
    """
    Detect when specialists should consult each other.

    Triggers cross-consultation when:
    1. Multiple specialists mark requires_cross_consultation = True
    2. Conflicts are detected between domains
    3. Strong synergies exist that warrant collaboration

    Args:
        messages: Dictionary of specialist_name -> SpecialistMessage

    Returns:
        List of cross-consultation recommendations
    """
    consultations = []

    # Check for explicit cross-consultation requests
    for name, msg in messages.items():
        if msg.requires_cross_consultation:
            consultations.append(
                {
                    "trigger_specialist": name,
                    "reason": f"{name} explicitly requested cross-consultation",
                    "recommended_consultants": [
                        other_name for other_name in messages.keys() if other_name != name
                    ],
                }
            )

    # Check for conflicts that need resolution
    all_conflicts = []
    for name, msg in messages.items():
        for conflict in msg.conflicts_with_other_domains:
            all_conflicts.append(
                {
                    "specialist": name,
                    "conflict_with": conflict.get("domain"),
                    "description": conflict.get("description", ""),
                }
            )

    # Group conflicts by pairs
    conflict_pairs: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
    for conflict in all_conflicts:
        pair = tuple(sorted([conflict["specialist"], conflict["conflict_with"]]))
        if pair not in conflict_pairs:
            conflict_pairs[pair] = []
        conflict_pairs[pair].append(conflict)

    # Recommend consultation for conflicted pairs
    for (spec1, spec2), conflicts_list in conflict_pairs.items():
        if len(conflicts_list) >= 1:
            consultations.append(
                {
                    "trigger_specialist": spec1,
                    "reason": f"Conflict detected with {spec2}: {conflicts_list[0]['description']}",
                    "recommended_consultants": [spec2],
                }
            )

    # Check for strong synergies
    synergy_pairs: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
    for name, msg in messages.items():
        for synergy in msg.synergies_with_other_domains:
            pair = tuple(sorted([name, synergy.get("domain", "")]))
            if pair not in synergy_pairs:
                synergy_pairs[pair] = []
            synergy_pairs[pair].append(synergy)

    for (spec1, spec2), synergies_list in synergy_pairs.items():
        # Only recommend if strong synergy (strength > 0.7)
        strong_synergies = [s for s in synergies_list if s.get("strength", 0) > 0.7]
        if strong_synergies:
            consultations.append(
                {
                    "trigger_specialist": spec1,
                    "reason": f"Strong synergy detected with {spec2}: opportunities for collaboration",
                    "recommended_consultants": [spec2],
                }
            )

    return consultations


# ==============================================================================
# Result Aggregation Functions
# ==============================================================================


def aggregate_specialist_results(
    messages: List[SpecialistMessage],
) -> AggregatedResults:
    """
    Aggregate results from multiple specialists into a unified structure.

    This function:
    1. Collects all specialist messages
    2. Identifies conflicts and synergies
    3. Organizes results by domain
    4. Prepares for unified response generation

    Args:
        messages: List of SpecialistMessage objects

    Returns:
        AggregatedResults object with all collected information
    """
    if not messages:
        raise ValueError("At least one specialist message is required")

    # Create aggregated results
    # Use the first message's user_query as original query (all should be same)
    aggregated = AggregatedResults(
        user_id="",  # Will be set by caller
        original_query=messages[0].user_query if messages else "",
    )

    # Add all messages
    for msg in messages:
        aggregated.add_message(msg)

    # Collect conflicts from all specialists
    all_conflicts = []
    for msg in messages:
        for conflict in msg.conflicts_with_other_domains:
            conflict_data = {
                "specialist_1": msg.specialist_name,
                "specialist_2": conflict.get("domain"),
                "description": conflict.get("description", ""),
                "severity": conflict.get("severity", "medium"),
            }
            all_conflicts.append(conflict_data)
    aggregated.conflicts_detected = all_conflicts

    # Collect synergies from all specialists
    all_synergies = []
    for msg in messages:
        for synergy in msg.synergies_with_other_domains:
            synergy_data = {
                "specialist": msg.specialist_name,
                "domain": synergy.get("domain"),
                "description": synergy.get("description", ""),
                "strength": synergy.get("strength", 0.5),
            }
            all_synergies.append(synergy_data)
    aggregated.synergies_identified = all_synergies

    return aggregated


# ==============================================================================
# Unified Response Generation
# ==============================================================================


def generate_unified_response(
    aggregated: AggregatedResults,
    resolution_strategy: Optional[ConflictResolutionStrategy] = None,
) -> str:
    """
    Generate a unified response from aggregated specialist results.

    This function creates a cohesive, human-readable response that:
    1. Summarizes insights from all specialists
    2. Highlights key recommendations
    3. Addresses conflicts with resolution strategies
    4. Emphasizes synergies and integrated approaches

    Args:
        aggregated: AggregatedResults with all specialist messages
        resolution_strategy: Optional conflict resolution strategy

    Returns:
        Formatted unified response as text
    """
    if not aggregated.messages:
        return "No specialist responses available."

    # Resolve conflicts if strategy provided
    resolutions = []
    if resolution_strategy and aggregated.conflicts_detected:
        resolutions = resolution_strategy.resolve(
            aggregated.conflicts_detected, aggregated.messages
        )

    # Build response sections
    response_parts = []

    # Header
    specialist_names = ", ".join(
        [name.replace("-specialist", "").title() for name in aggregated.messages.keys()]
    )
    response_parts.append(f"## Integrated Analysis from {specialist_names} Specialists")
    response_parts.append("=" * 70)

    # Summary section
    if len(aggregated.messages) > 1:
        response_parts.append("\n### Executive Summary")
        response_parts.append(
            f"Analyzed your query from {len(aggregated.messages)} specialist perspectives. "
        )

        if aggregated.conflicts_detected:
            response_parts.append(
                f"Identified {len(aggregated.conflicts_detected)} potential conflict(s) "
                f"and {len(resolutions if resolutions else [])} resolution strategy(ies)."
            )
        else:
            response_parts.append("All specialists are aligned - no conflicts detected.")

    # Specialist analyses
    response_parts.append("\n### Specialist Insights")

    for name, msg in aggregated.messages.items():
        domain_title = name.replace("-specialist", "").title()
        response_parts.append(f"\n#### {domain_title} Specialist")

        if msg.analysis:
            # Truncate long analyses
            analysis = msg.analysis[:500] + "..." if len(msg.analysis) > 500 else msg.analysis
            response_parts.append(f"**Analysis:** {analysis}")

        if msg.recommendations:
            response_parts.append("\n**Recommendations:**")
            for i, rec in enumerate(msg.recommendations[:3], 1):  # Top 3
                title = rec.get("title", "Recommendation")
                response_parts.append(f"  {i}. {title}")

    # Conflicts section
    if aggregated.conflicts_detected:
        response_parts.append("\n### Conflict Analysis & Resolution")
        for i, conflict in enumerate(aggregated.conflicts_detected[:3], 1):  # Top 3
            spec1_title = conflict["specialist_1"].replace("-specialist", "").title()
            spec2_title = conflict["specialist_2"].replace("-specialist", "").title()
            response_parts.append(f"\n{i}. {spec1_title} vs {spec2_title}")
            response_parts.append(f"   Issue: {conflict['description']}")

            # Show resolution if available
            matching_resolution = next(
                (r for r in resolutions if r.get("conflict") == conflict), None
            )
            if matching_resolution:
                response_parts.append(
                    f"   Resolution: {matching_resolution.get('suggested_action', '')}"
                )

    # Synergies section
    if aggregated.synergies_identified:
        response_parts.append("\n### Cross-Domain Synergies")
        for i, synergy in enumerate(aggregated.synergies_identified[:3], 1):  # Top 3
            spec_title = synergy["specialist"].replace("-specialist", "").title()
            domain_title = synergy["domain"].replace("-specialist", "").title()
            response_parts.append(f"\n{i}. {spec_title} ↔ {domain_title}")
            response_parts.append(f"   Opportunity: {synergy['description']}")

    # Cross-consultation recommendations
    consultations = detect_cross_consultation_needs(aggregated.messages)
    if consultations:
        response_parts.append("\n### Recommended Cross-Consultations")
        for i, rec in enumerate(consultations[:3], 1):  # Top 3
            spec_title = rec["trigger_specialist"].replace("-specialist", "").title()
            consultants = [
                c.replace("-specialist", "").title() for c in rec["recommended_consultants"]
            ]
            response_parts.append(f"\n{i}. {spec_title}: {rec['reason']}")
            response_parts.append(f"   Consult with: {', '.join(consultants)}")

    # Integrated recommendations
    response_parts.append("\n### Integrated Recommendations")
    response_parts.append(
        "Based on the collective analysis from all specialists, here are the key recommendations:"
    )

    # Collect top recommendations from all
    all_recs = []
    for msg in aggregated.messages.values():
        for rec in msg.recommendations:
            all_recs.append(
                {
                    "specialist": msg.specialist_name,
                    "title": rec.get("title", ""),
                    "priority": rec.get("priority", 5),
                }
            )

    # Sort by priority
    all_recs.sort(key=lambda x: x["priority"], reverse=True)

    for i, rec in enumerate(all_recs[:5], 1):  # Top 5
        spec_title = rec["specialist"].replace("-specialist", "").title()
        response_parts.append(f"{i}. **{rec['title']}** (from {spec_title})")

    # Footer
    response_parts.append("\n---")
    response_parts.append(
        f"*Analysis based on inputs from {len(aggregated.messages)} specialist(s) "
        f"generated at {aggregated.timestamp}*"
    )

    return "\n".join(response_parts)


# ==============================================================================
# Communication Tools Factory
# ==============================================================================


def create_communication_tools(backend=None):
    """
    Create communication protocol tools with shared FilesystemBackend instance.

    These tools enable the AI Life Coach coordinator to:
    - Format specialist messages in standardized format
    - Aggregate results from multiple specialists
    - Detect and resolve conflicts between specialist recommendations
    - Trigger cross-consultation when domains overlap
    - Generate unified responses from multiple specialist outputs

    Args:
        backend: Optional FilesystemBackend instance. If None, uses get_backend()

    Returns:
        Tuple of communication tools (format_specialist_message,
                                     aggregate_results,
                                     resolve_conflicts,
                                     detect_cross_consultation,
                                     generate_unified_response)

    Example:
        >>> from src.config import config
        >>> config.initialize_environment()
        >>> tools = create_communication_tools()
        >>> result = format_specialist_message(
        ...     specialist_name="career-specialist",
        ...     user_query="Help me advance my career",
        ...     analysis="Detailed career analysis...",
        ...     recommendations=[{"title": "Get certified", "priority": 8}]
        ... )
    """
    if backend is None:
        backend = get_backend()

    # Get the workspace directory path from backend
    workspace_path = Path(backend.root_dir) if hasattr(backend, "root_dir") else Path("workspace")

    @tool
    def format_specialist_message(
        specialist_name: str,
        user_query: str,
        analysis: str,
        recommendations: List[Dict[str, Any]],
        synergies_with_other_domains: Optional[List[Dict[str, Any]]] = None,
        conflicts_with_other_domains: Optional[List[Dict[str, Any]]] = None,
        confidence_level: float = 0.8,
        requires_cross_consultation: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Format a specialist's response into the standardized message format.

        This tool creates a structured message from a specialist subagent to
        the coordinator, ensuring consistent communication across all domains.

        Args:
            specialist_name: Name of the specialist (e.g., "career-specialist")
            user_query: The original query from the coordinator
            analysis: Specialist's detailed analysis of the situation
            recommendations: List of actionable recommendation dictionaries,
                            each containing at least "title" and optional "priority", "description"
            synergies_with_other_domains: List of synergy dictionaries, each containing
                                         "domain", "description", and optional "strength"
            conflicts_with_other_domains: List of conflict dictionaries, each containing
                                         "domain", "description", and optional "severity"
            confidence_level: Specialist's confidence in analysis (0-1 scale, default 0.8)
            requires_cross_consultation: Whether this specialist needs input from others
            metadata: Additional context or data

        Returns:
            Formatted JSON string representing the specialist message
            Saved to communication_logs/{user_id}/

        Example:
            >>> format_specialist_message(
            ...     "career-specialist",
            ...     "Help me advance my career",
            ...     "Your skills are strong but...",
            ...     [{"title": "Get certified", "priority": 8}],
            ...     synergies_with_other_domains=[{
            ...         "domain": "wellness-specialist",
            ...         "description": "Career success enables wellness investments"
            ...     }]
            ... )
        """
        # Validate inputs
        valid_specialists = [
            "career-specialist",
            "relationship-specialist",
            "finance-specialist",
            "wellness-specialist",
        ]
        if specialist_name not in valid_specialists:
            return (
                f"Error: Invalid specialist '{specialist_name}'. "
                f"Must be one of: {', '.join(valid_specialists)}"
            )

        if not user_query or not isinstance(user_query, str):
            return "Error: user_query must be a non-empty string"

        if not analysis or not isinstance(analysis, str):
            return "Error: analysis must be a non-empty string"

        if not recommendations or not isinstance(recommendations, list):
            return "Error: recommendations must be a non-empty list"

        try:
            # Create specialist message
            message = SpecialistMessage(
                specialist_name=specialist_name,
                user_query=user_query,
                analysis=analysis,
                recommendations=recommendations,
                synergies_with_other_domains=synergies_with_other_domains,
                conflicts_with_other_domains=conflicts_with_other_domains,
                confidence_level=confidence_level,
                requires_cross_consultation=requires_cross_consultation,
                metadata=metadata or {},
            )

            # Convert to JSON
            json_content = json.dumps(message.to_dict(), indent=2)

            # Save to communication logs
            today = date.today()
            timestamp = datetime.now().strftime("%H%M%S")
            user_id = metadata.get("user_id", "unknown") if metadata else "unknown"
            path = f"communication_logs/{user_id}/{today}_{specialist_name}_{timestamp}.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            specialist_title = specialist_name.replace("-specialist", "").title()
            response_parts = [
                f"{specialist_title} Specialist Message Formatted",
                "=" * 60,
                f"\nSpecialist: {specialist_name}",
                f"Timestamp: {message.timestamp}",
                f"Confidence Level: {message.confidence_level:.1%}",
            ]

            if message.requires_cross_consultation:
                response_parts.append("\n⚠ Requires cross-consultation with other specialists")

            response_parts.append(f"\nRecommendations ({len(message.recommendations)}):")
            for i, rec in enumerate(message.recommendations[:5], 1):
                title = rec.get("title", "Untitled")
                priority = rec.get("priority", 5)
                response_parts.append(f"  {i}. {title} (Priority: {priority})")

            if message.synergies_with_other_domains:
                response_parts.append("\nSynergies with Other Domains:")
                for syn in message.synergies_with_other_domains[:3]:
                    domain = syn.get("domain", "").replace("-specialist", "").title()
                    desc = syn.get("description", "")
                    response_parts.append(f"  • {domain}: {desc}")

            if message.conflicts_with_other_domains:
                response_parts.append("\nPotential Conflicts:")
                for conf in message.conflicts_with_other_domains[:3]:
                    domain = conf.get("domain", "").replace("-specialist", "").title()
                    desc = conf.get("description", "")
                    response_parts.append(f"  ⚠ {domain}: {desc}")

            response_parts.append(f"\nMessage saved to: {path}")
            response_parts.append("\nJSON format:")
            response_parts.append("```json")
            response_parts.append(
                json_content[:500] + "..." if len(json_content) > 500 else json_content
            )
            response_parts.append("```")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error formatting specialist message: {str(e)}"

    @tool
    def aggregate_results(
        user_id: str,
        specialist_messages: List[Dict[str, Any]],
    ) -> str:
        """Aggregate results from multiple specialist subagents.

        This tool collects outputs from multiple specialists, identifies
        conflicts and synergies, and prepares for unified response generation.

        Args:
            user_id: The user's unique identifier
            specialist_messages: List of formatted specialist message dictionaries

        Returns:
            Structured aggregation results with conflicts and synergies identified
            Saved to aggregated_results/{user_id}/

        Example:
            >>> aggregate_results(
            ...     "user_123",
            ...     [
            ...         {"specialist_name": "career-specialist", "analysis": "..."},
            ...         {"specialist_name": "finance-specialist", "analysis": "..."}
            ...     ]
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        if not specialist_messages or not isinstance(specialist_messages, list):
            return "Error: specialist_messages must be a non-empty list"

        try:
            # Convert dictionaries to SpecialistMessage objects
            messages = []
            for msg_dict in specialist_messages:
                if isinstance(msg_dict, dict):
                    messages.append(SpecialistMessage.from_dict(msg_dict))
                else:
                    return (
                        f"Error: Each specialist message must be a dictionary, got {type(msg_dict)}"
                    )

            # Aggregate results
            aggregated = aggregate_specialist_results(messages)
            aggregated.user_id = user_id

            # Convert to JSON
            json_content = json.dumps(aggregated.to_dict(), indent=2)

            # Save aggregation results
            today = date.today()
            timestamp = datetime.now().strftime("%H%M%S")
            path = f"aggregated_results/{user_id}/{today}_aggregation_{timestamp}.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            specialist_names = ", ".join(
                [name.replace("-specialist", "").title() for name in aggregated.messages.keys()]
            )
            response_parts = [
                f"Results Aggregation from {specialist_names}",
                "=" * 60,
                f"\nSpecialists Consulted: {len(aggregated.messages)}",
                f"Original Query: {aggregated.original_query}",
            ]

            # Conflicts section
            if aggregated.conflicts_detected:
                response_parts.append(
                    f"\n⚠ Conflicts Detected: {len(aggregated.conflicts_detected)}"
                )
                for i, conflict in enumerate(aggregated.conflicts_detected[:3], 1):
                    spec1 = conflict["specialist_1"].replace("-specialist", "").title()
                    spec2 = conflict["specialist_2"].replace("-specialist", "").title()
                    response_parts.append(f"  {i}. {spec1} vs {spec2}")
                    response_parts.append(f"     {conflict['description']}")
            else:
                response_parts.append("\n✓ No conflicts detected - all specialists aligned")

            # Synergies section
            if aggregated.synergies_identified:
                response_parts.append(
                    f"\n✓ Synergies Identified: {len(aggregated.synergies_identified)}"
                )
                for i, synergy in enumerate(aggregated.synergies_identified[:3], 1):
                    spec = synergy["specialist"].replace("-specialist", "").title()
                    domain = synergy["domain"].replace("-specialist", "").title()
                    response_parts.append(f"  {i}. {spec} ↔ {domain}")
                    response_parts.append(f"     {synergy['description']}")

            # Recommendations summary
            total_recs = sum(len(msg.recommendations) for msg in aggregated.messages.values())
            response_parts.append(f"\nTotal Recommendations: {total_recs}")

            response_parts.append(f"\nAggregation results saved to: {path}")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error aggregating results: {str(e)}"

    @tool
    def resolve_conflicts(
        user_id: str,
        aggregated_results_path: Optional[str] = None,
        resolution_strategy: str = "hybrid",
    ) -> str:
        """Resolve conflicts between competing specialist recommendations.

        This tool analyzes detected conflicts and provides resolution strategies
        using one of three approaches:
        - priority_based: Higher priority domains take precedence
        - consensus_based: Seek compromise or sequential approach
        - hybrid: Priority-based for high-severity, consensus for moderate

        Args:
            user_id: The user's unique identifier
            aggregated_results_path: Optional path to existing aggregation JSON file.
                                     If None, uses the most recent one.
            resolution_strategy: Strategy to use ("priority_based", "consensus_based", or "hybrid")

        Returns:
            Structured conflict resolution report with recommendations
            Saved to conflict_resolutions/{user_id}/

        Example:
            >>> resolve_conflicts("user_123", resolution_strategy="hybrid")
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        valid_strategies = ["priority_based", "consensus_based", "hybrid"]
        if resolution_strategy not in valid_strategies:
            return (
                f"Error: Invalid resolution strategy '{resolution_strategy}'. "
                f"Must be one of: {', '.join(valid_strategies)}"
            )

        try:
            # Load aggregated results
            if aggregated_results_path is None:
                agg_dir = workspace_path / "aggregated_results" / user_id
                if not agg_dir.exists():
                    return f"Error: No aggregated results found for user {user_id}"

                agg_files = sorted(
                    agg_dir.glob("*_aggregation_*.json"),
                    key=lambda p: p.stat().st_mtime,
                    reverse=True,
                )
                if not agg_files:
                    return f"Error: No aggregated results found for user {user_id}"

                aggregated_results_path = str(agg_files[0].relative_to(workspace_path))

            # Read the aggregation file
            try:
                if hasattr(backend, "read_file"):
                    json_content = backend.read_file(aggregated_results_path)
                else:
                    file_path = workspace_path / aggregated_results_path
                    json_content = file_path.read_text()

                agg_data = json.loads(json_content)
            except FileNotFoundError:
                return f"Error: Aggregated results file not found at {aggregated_results_path}"

            # Reconstruct messages
            messages = {}
            for name, msg_dict in agg_data.get("messages", {}).items():
                messages[name] = SpecialistMessage.from_dict(msg_dict)

            # Select resolution strategy
            if resolution_strategy == "priority_based":
                resolver = PriorityBasedResolution()
            elif resolution_strategy == "consensus_based":
                resolver = ConsensusBasedResolution()
            else:  # hybrid
                resolver = HybridResolution()

            # Resolve conflicts
            conflicts = agg_data.get("conflicts_detected", [])
            resolutions = resolver.resolve(conflicts, messages)

            # Build resolution report
            resolution_report = {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "source_file": aggregated_results_path,
                "resolution_strategy": resolution_strategy,
                "conflicts_detected": len(conflicts),
                "resolutions_provided": resolutions,
            }

            # Save report
            json_output = json.dumps(resolution_report, indent=2)
            today = date.today()
            path = f"conflict_resolutions/{user_id}/{today}_resolution.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_output)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_output)

            # Format user-friendly response
            strategy_title = resolution_strategy.replace("_", " ").title()
            response_parts = [
                f"Conflict Resolution Report ({strategy_title})",
                "=" * 60,
            ]

            if not conflicts:
                response_parts.append("\n✓ No conflicts to resolve!")
            else:
                response_parts.append(f"\nConflicts Analyzed: {len(conflicts)}")
                response_parts.append(f"Resolutions Provided: {len(resolutions)}\n")

                for i, resolution in enumerate(resolutions, 1):
                    response_parts.append(
                        f"{i}. {resolution.get('suggested_action', 'No action specified')}"
                    )
                    response_parts.append(
                        f"   Strategy: {resolution.get('resolution_type', 'N/A')}"
                    )
                    response_parts.append(f"   Rationale: {resolution.get('rationale', 'N/A')}\n")

            response_parts.append(f"Resolution report saved to: {path}")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error resolving conflicts: {str(e)}"

    @tool
    def detect_cross_consultation(
        user_id: str,
        specialist_messages: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """Detect when specialists should consult each other.

        This tool identifies situations where cross-specialist consultation
        would be beneficial, including:
        - Explicit requests for consultation
        - Conflicts that need resolution through dialogue
        - Strong synergies that warrant collaboration

        Args:
            user_id: The user's unique identifier
            specialist_messages: Optional list of specialist message dictionaries.
                                 If None, loads from recent aggregation.

        Returns:
            Structured cross-consultation recommendations
            Saved to consultation_recommendations/{user_id}/

        Example:
            >>> detect_cross_consultation("user_123")
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        try:
            # Load messages if not provided
            messages = {}
            if specialist_messages is None:
                # Load from most recent aggregation
                agg_dir = workspace_path / "aggregated_results" / user_id
                if not agg_dir.exists():
                    return f"Error: No aggregated results found for user {user_id}"

                agg_files = sorted(
                    agg_dir.glob("*_aggregation_*.json"),
                    key=lambda p: p.stat().st_mtime,
                    reverse=True,
                )
                if not agg_files:
                    return f"Error: No aggregated results found for user {user_id}"

                file_path = agg_files[0]
                if hasattr(backend, "read_file"):
                    json_content = backend.read_file(str(file_path.relative_to(workspace_path)))
                else:
                    json_content = file_path.read_text()

                agg_data = json.loads(json_content)
                for name, msg_dict in agg_data.get("messages", {}).items():
                    messages[name] = SpecialistMessage.from_dict(msg_dict)
            else:
                # Convert provided dictionaries
                for msg_dict in specialist_messages:
                    if isinstance(msg_dict, dict):
                        msg = SpecialistMessage.from_dict(msg_dict)
                        messages[msg.specialist_name] = msg

            if not messages:
                return "Error: No specialist messages available for analysis"

            # Detect cross-consultation needs
            consultations = detect_cross_consultation_needs(messages)

            # Build consultation report
            consultation_report = {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "specialists_analyzed": len(messages),
                "consultations_recommended": len(consultations),
                "recommendations": consultations,
            }

            # Save report
            json_output = json.dumps(consultation_report, indent=2)
            today = date.today()
            path = f"consultation_recommendations/{user_id}/{today}_consultations.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_output)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_output)

            # Format user-friendly response
            specialist_names = ", ".join(
                [name.replace("-specialist", "").title() for name in messages.keys()]
            )
            response_parts = [
                f"Cross-Consultation Analysis for {specialist_names}",
                "=" * 60,
            ]

            if not consultations:
                response_parts.append("\n✓ No cross-consultation needed at this time")
            else:
                response_parts.append(f"\n{len(consultations)} consultation(s) recommended:\n")

                for i, rec in enumerate(consultations, 1):
                    spec_title = rec["trigger_specialist"].replace("-specialist", "").title()
                    consultants = [
                        c.replace("-specialist", "").title() for c in rec["recommended_consultants"]
                    ]
                    response_parts.append(f"{i}. {spec_title}")
                    response_parts.append(f"   Reason: {rec['reason']}")
                    response_parts.append(f"   Consult with: {', '.join(consultants)}\n")

            response_parts.append(f"Consultation recommendations saved to: {path}")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error detecting cross-consultation needs: {str(e)}"

    @tool
    def generate_unified_response_tool(
        user_id: str,
        aggregated_results_path: Optional[str] = None,
        resolution_strategy: str = "hybrid",
    ) -> str:
        """Generate a unified response from aggregated specialist results.

        This tool creates a cohesive, human-readable response that integrates
        insights from all specialists, addresses conflicts with resolutions,
        and emphasizes synergies.

        Args:
            user_id: The user's unique identifier
            aggregated_results_path: Optional path to existing aggregation JSON file.
                                     If None, uses the most recent one.
            resolution_strategy: Strategy to use for conflict resolution

        Returns:
            Formatted unified response integrating all specialist inputs
            Saved to unified_responses/{user_id}/

        Example:
            >>> generate_unified_response_tool("user_123")
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        try:
            # Load aggregated results
            if aggregated_results_path is None:
                agg_dir = workspace_path / "aggregated_results" / user_id
                if not agg_dir.exists():
                    return f"Error: No aggregated results found for user {user_id}"

                agg_files = sorted(
                    agg_dir.glob("*_aggregation_*.json"),
                    key=lambda p: p.stat().st_mtime,
                    reverse=True,
                )
                if not agg_files:
                    return f"Error: No aggregated results found for user {user_id}"

                # Use the relative path
                aggregated_results_path = str(agg_files[0].relative_to(workspace_path))

            # Read the aggregation file
            try:
                if hasattr(backend, "read_file"):
                    json_content = backend.read_file(aggregated_results_path)
                else:
                    file_path = workspace_path / aggregated_results_path
                    json_content = file_path.read_text()

                agg_data = json.loads(json_content)
            except FileNotFoundError:
                return f"Error: Aggregated results file not found at {aggregated_results_path}"

            # Reconstruct aggregated results
            messages = {}
            for name, msg_dict in agg_data.get("messages", {}).items():
                messages[name] = SpecialistMessage.from_dict(msg_dict)

            aggregated = AggregatedResults(
                user_id=user_id,
                original_query=agg_data.get("original_query", ""),
            )
            aggregated.messages = messages
            aggregated.conflicts_detected = agg_data.get("conflicts_detected", [])
            aggregated.synergies_identified = agg_data.get("synergies_identified", [])

            # Select resolution strategy
            if resolution_strategy == "priority_based":
                resolver = PriorityBasedResolution()
            elif resolution_strategy == "consensus_based":
                resolver = ConsensusBasedResolution()
            else:  # hybrid
                resolver = HybridResolution()

            # Generate unified response
            unified_response = generate_unified_response(aggregated, resolver)

            # Save unified response
            today = date.today()
            timestamp = datetime.now().strftime("%H%M%S")
            path = f"unified_responses/{user_id}/{today}_response_{timestamp}.md"

            if hasattr(backend, "write_file"):
                backend.write_file(path, unified_response)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(unified_response)

            # Add reference to saved file
            response_with_reference = unified_response + f"\n\n*Unified response saved to: {path}*"

            return response_with_reference

        except Exception as e:
            return f"Error generating unified response: {str(e)}"

    return (
        format_specialist_message,
        aggregate_results,
        resolve_conflicts,
        detect_cross_consultation,
        generate_unified_response_tool,
    )
