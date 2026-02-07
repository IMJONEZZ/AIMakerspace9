"""
Result Integration Tools for AI Life Coach.

This module implements advanced result integration functionality that builds upon
the communication protocol to provide sophisticated multi-specialist output integration.

Based on research in:
- Multi-agent result aggregation and synthesis
- Conflict resolution strategies in multi-agent systems
- Cross-domain knowledge integration
- Prioritized action list generation

Key Features:
1. Unified Response Format: Standardized structure for integrating specialist outputs
2. Specialist Output Harmonization: Normalizing and combining diverse specialist insights
3. Advanced Conflict Resolution: Multiple strategies for resolving competing recommendations
4. Cross-Domain Insight Synthesis: Engine to identify and combine insights across domains
5. Prioritized Action List Generation: Creating actionable, prioritized lists from integrated results

Integration Pattern:
    Specialist Outputs → Harmonization → Conflict Detection & Resolution
        → Cross-Domain Synthesis → Prioritization → Unified Response
"""

from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import json
from dataclasses import dataclass, field

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
# Unified Response Data Structures
# ==============================================================================


@dataclass
class IntegratedInsight:
    """
    Represents a single integrated insight from multiple specialists.

    Attributes:
        insight_id: Unique identifier for the insight
        title: Brief, descriptive title
        description: Detailed explanation of the insight
        source_specialists: List of specialists who contributed to this insight
        domains_affected: Set of life domains this insight impacts
        confidence_score: Overall confidence (0-1)
        strength_score: Importance/impact strength (0-1)
        cross_domain_connections: Links to other insights
        actionable_items: Specific actions derived from this insight
    """

    insight_id: str
    title: str
    description: str
    source_specialists: List[str] = field(default_factory=list)
    domains_affected: Set[str] = field(default_factory=set)
    confidence_score: float = 0.8
    strength_score: float = 0.5
    cross_domain_connections: List[str] = field(default_factory=list)
    actionable_items: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "insight_id": self.insight_id,
            "title": self.title,
            "description": self.description,
            "source_specialists": self.source_specialists,
            "domains_affected": list(self.domains_affected),
            "confidence_score": self.confidence_score,
            "strength_score": self.strength_score,
            "cross_domain_connections": self.cross_domain_connections,
            "actionable_items": self.actionable_items,
        }


@dataclass
class PrioritizedAction:
    """
    Represents a single prioritized action item.

    Attributes:
        action_id: Unique identifier
        description: What needs to be done
        priority_score: 0-10, higher is more urgent/important
        urgency_level: immediate, short_term, medium_term, long_term
        effort_estimate: low, medium, high
        source_insight_id: Which insight this action derives from
        preconditions: Actions that must be completed first
        expected_outcomes: What results to expect
    """

    action_id: str
    description: str
    priority_score: float  # 0-10
    urgency_level: str  # immediate, short_term, medium_term, long_term
    effort_estimate: str  # low, medium, high
    source_insight_id: str
    preconditions: List[str] = field(default_factory=list)
    expected_outcomes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "action_id": self.action_id,
            "description": self.description,
            "priority_score": self.priority_score,
            "urgency_level": self.urgency_level,
            "effort_estimate": self.effort_estimate,
            "source_insight_id": self.source_insight_id,
            "preconditions": self.preconditions,
            "expected_outcomes": self.expected_outcomes,
        }


@dataclass
class UnifiedResponse:
    """
    Complete unified response from integrating all specialist outputs.

    Attributes:
        user_id: User identifier
        query_timestamp: When the original query was made
        integration_timestamp: When this response was generated
        specialists_consulted: List of specialist names involved
        integrated_insights: List of IntegratedInsight objects
        conflicts_resolved: Summary of conflict resolution
        synergies_identified: Cross-domain synergies found
        prioritized_actions: List of PrioritizedAction objects
        overall_confidence: Aggregate confidence across all insights
    """

    user_id: str
    query_timestamp: str
    integration_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    specialists_consulted: List[str] = field(default_factory=list)
    integrated_insights: List[IntegratedInsight] = field(default_factory=list)
    conflicts_resolved: List[Dict[str, Any]] = field(default_factory=list)
    synergies_identified: List[Dict[str, Any]] = field(default_factory=list)
    prioritized_actions: List[PrioritizedAction] = field(default_factory=list)
    overall_confidence: float = 0.8

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "user_id": self.user_id,
            "query_timestamp": self.query_timestamp,
            "integration_timestamp": self.integration_timestamp,
            "specialists_consulted": self.specialists_consulted,
            "integrated_insights": [insight.to_dict() for insight in self.integrated_insights],
            "conflicts_resolved": self.conflicts_resolved,
            "synergies_identified": self.synergies_identified,
            "prioritized_actions": [action.to_dict() for action in self.prioritized_actions],
            "overall_confidence": self.overall_confidence,
        }


# ==============================================================================
# Specialist Output Harmonization
# ==============================================================================


class SpecialistOutputHarmonizer:
    """
    Harmonizes outputs from multiple specialist subagents.

    This class normalizes and combines diverse specialist insights,
    identifying patterns, redundancies, and complementary information.
    """

    def __init__(self):
        self.domain_weights = {
            "career-specialist": 0.25,
            "relationship-specialist": 0.25,
            "finance-specialist": 0.25,
            "wellness-specialist": 0.25,
        }

    def harmonize_recommendations(self, messages: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Harmonize recommendations from multiple specialists.

        This function:
        1. Collects all recommendations
        2. Identifies duplicates or near-duplicates
        3. Merges related recommendations
        4. Assigns confidence-weighted scores

        Args:
            messages: Dictionary of specialist_name -> message data

        Returns:
            List of harmonized recommendation dictionaries
        """
        all_recommendations = []

        for specialist_name, msg_data in messages.items():
            recommendations = msg_data.get("recommendations", [])

            for rec in recommendations:
                # Add specialist source and domain weight
                harmonized_rec = {
                    **rec,
                    "source_specialist": specialist_name,
                    "domain_weight": self.domain_weights.get(specialist_name, 0.25),
                }
                all_recommendations.append(harmonized_rec)

        # Identify and merge duplicates
        return self._merge_duplicate_recommendations(all_recommendations)

    def _merge_duplicate_recommendations(
        self, recommendations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Merge duplicate or similar recommendations.

        Uses simple title similarity to identify duplicates.
        """
        if not recommendations:
            return []

        merged = []
        seen_titles = set()

        for rec in recommendations:
            title = rec.get("title", "").lower().strip()

            # Simple duplicate detection
            is_duplicate = False
            for seen in seen_titles:
                if title == seen or (len(title) > 10 and (title in seen or seen in title)):
                    is_duplicate = True
                    break

            if not is_duplicate:
                merged.append(rec)
                seen_titles.add(title)

        return merged

    def calculate_confidence_weighted_score(self, recommendations: List[Dict[str, Any]]) -> float:
        """
        Calculate a confidence-weighted score for recommendations.

        Combines specialist confidence, domain weight, and recommendation priority.
        """
        if not recommendations:
            return 0.0

        total_score = 0.0
        for rec in recommendations:
            priority = rec.get("priority", 5)
            domain_weight = rec.get("domain_weight", 0.25)

            # Normalize priority to 0-1
            normalized_priority = min(priority / 10.0, 1.0)

            # Calculate weighted score
            weighted_score = normalized_priority * domain_weight
            total_score += weighted_score

        # Average across all recommendations
        return min(total_score / len(recommendations), 1.0)


# ==============================================================================
# Cross-Domain Insight Synthesis
# ==============================================================================


class CrossDomainSynthesizer:
    """
    Engine for synthesizing insights across multiple domains.

    This class identifies connections, patterns, and synergies
    between different life domains to generate integrated insights.
    """

    def __init__(self):
        # Domain relationship graph (domains that commonly interact)
        self.domain_relationships = {
            "career": {"wellness", "finance"},
            "relationship": {"wellness", "finance"},
            "finance": {"career", "relationship", "wellness"},
            "wellness": {"career", "relationship", "finance"},
        }

    def synthesize_insights(
        self,
        messages: Dict[str, Any],
        harmonized_recommendations: List[Dict[str, Any]],
    ) -> List[IntegratedInsight]:
        """
        Synthesize integrated insights from multiple domains.

        This function:
        1. Identifies cross-domain themes
        2. Connects related insights across specialists
        3. Generates higher-level integrated insights
        4. Assigns confidence and strength scores

        Args:
            messages: Dictionary of specialist_name -> message data
            harmonized_recommendations: List of harmonized recommendations

        Returns:
            List of IntegratedInsight objects
        """
        insights = []

        # Extract domain-specific analyses
        domain_analyses = self._extract_domain_analyses(messages)

        # Generate cross-domain insights
        for domain_1 in domain_analyses.keys():
            for domain_2 in self.domain_relationships.get(domain_1, set()):
                if domain_2 not in domain_analyses:
                    continue

                # Create insight from domain pair
                insight = self._create_cross_domain_insight(
                    domain_1, domain_2, messages, harmonized_recommendations
                )
                if insight:
                    insights.append(insight)

        # Generate single-domain enhancements
        for domain, analysis in domain_analyses.items():
            insight = self._create_domain_enhancement_insight(
                domain, analysis, messages.get(f"{domain}-specialist", {})
            )
            if insight:
                insights.append(insight)

        return insights

    def _extract_domain_analyses(self, messages: Dict[str, Any]) -> Dict[str, str]:
        """Extract analyses by domain."""
        domain_analyses = {}
        for specialist_name, msg_data in messages.items():
            domain = specialist_name.replace("-specialist", "")
            analysis = msg_data.get("analysis", "")
            if analysis:
                domain_analyses[domain] = analysis
        return domain_analyses

    def _create_cross_domain_insight(
        self,
        domain_1: str,
        domain_2: str,
        messages: Dict[str, Any],
        recommendations: List[Dict[str, Any]],
    ) -> Optional[IntegratedInsight]:
        """Create an integrated insight from two domains."""
        specialist_1 = f"{domain_1}-specialist"
        specialist_2 = f"{domain_2}-specialist"

        if specialist_1 not in messages or specialist_2 not in messages:
            return None

        # Find recommendations that involve both domains
        cross_domain_recs = [
            rec
            for rec in recommendations
            if rec.get("source_specialist") in [specialist_1, specialist_2]
        ]

        if not cross_domain_recs:
            return None

        # Create insight
        insight_id = f"cross_{domain_1}_{domain_2}"
        title = f"{domain_1.title()}-Wellness Integration"

        description = (
            f"Integrated insights from {domain_1.title()} and {domain_2.title()} domains. "
            f"Key themes include: {', '.join([rec.get('title', 'N/A') for rec in cross_domain_recs[:3]])}"
        )

        # Calculate confidence based on specialist confidences
        msg1 = messages[specialist_1]
        msg2 = messages[specialist_2]
        confidence_score = (
            msg1.get("confidence_level", 0.8) + msg2.get("confidence_level", 0.8)
        ) / 2

        # Strength based on number of cross-domain recommendations
        strength_score = min(len(cross_domain_recs) / 3.0, 1.0)

        insight = IntegratedInsight(
            insight_id=insight_id,
            title=title,
            description=description,
            source_specialists=[specialist_1, specialist_2],
            domains_affected={domain_1, domain_2},
            confidence_score=confidence_score,
            strength_score=strength_score,
        )

        # Add actionable items
        for rec in cross_domain_recs[:3]:
            insight.actionable_items.append(
                {
                    "description": rec.get("title", ""),
                    "priority": rec.get("priority", 5),
                }
            )

        return insight

    def _create_domain_enhancement_insight(
        self, domain: str, analysis: str, message_data: Dict[str, Any]
    ) -> Optional[IntegratedInsight]:
        """Create an insight focused on a single domain."""
        if not analysis:
            return None

        specialist_name = f"{domain}-specialist"

        insight_id = f"enhance_{domain}"
        title = f"{domain.title()} Enhancement Focus"

        description = f"Deep dive into {domain.title()} domain. {analysis[:200]}..."

        confidence_score = message_data.get("confidence_level", 0.8)
        strength_score = 0.6

        insight = IntegratedInsight(
            insight_id=insight_id,
            title=title,
            description=description,
            source_specialists=[specialist_name],
            domains_affected={domain},
            confidence_score=confidence_score,
            strength_score=strength_score,
        )

        return insight


# ==============================================================================
# Prioritized Action List Generation
# ==============================================================================


class ActionPrioritizer:
    """
    Generates prioritized action lists from integrated insights.

    This class converts insights into actionable items with clear
    priorities, urgency levels, and expected outcomes.
    """

    def __init__(self):
        # Priority weights for different factors
        self.urgency_weights = {
            "immediate": 1.0,
            "short_term": 0.8,
            "medium_term": 0.6,
            "long_term": 0.4,
        }

    def generate_prioritized_actions(
        self, insights: List[IntegratedInsight], user_goals: Optional[List[str]] = None
    ) -> List[PrioritizedAction]:
        """
        Generate a prioritized list of actions from insights.

        Args:
            insights: List of IntegratedInsight objects
            user_goals: Optional list of user's stated goals for alignment

        Returns:
            List of PrioritizedAction objects sorted by priority
        """
        actions = []

        for insight in insights:
            # Generate actions from actionable items in the insight
            for item in insight.actionable_items:
                action = self._create_action_from_item(insight, item, user_goals)
                if action:
                    actions.append(action)

        # Sort by priority score (descending)
        actions.sort(key=lambda a: a.priority_score, reverse=True)

        return actions

    def _create_action_from_item(
        self,
        insight: IntegratedInsight,
        item: Dict[str, Any],
        user_goals: Optional[List[str]] = None,
    ) -> PrioritizedAction:
        """Create a PrioritizedAction from an actionable item."""
        action_id = f"action_{insight.insight_id}_{len(insight.actionable_items)}"
        description = item.get("description", "")

        # Calculate priority score
        base_priority = item.get("priority", 5) / 10.0  # Normalize to 0-1
        confidence_boost = insight.confidence_score * 0.2
        strength_boost = insight.strength_score * 0.3

        # Boost if aligned with user goals
        goal_alignment_boost = 0.0
        if user_goals:
            for goal in user_goals:
                if goal.lower() in description.lower():
                    goal_alignment_boost = 0.2
                    break

        priority_score = (
            base_priority + confidence_boost + strength_boost + goal_alignment_boost
        ) * 10.0
        priority_score = min(priority_score, 10.0)

        # Determine urgency level based on priority
        if priority_score >= 8:
            urgency_level = "immediate"
        elif priority_score >= 6:
            urgency_level = "short_term"
        elif priority_score >= 4:
            urgency_level = "medium_term"
        else:
            urgency_level = "long_term"

        # Estimate effort (simplified)
        if priority_score >= 8:
            effort_estimate = "low"  # High priority items should be doable
        elif priority_score >= 5:
            effort_estimate = "medium"
        else:
            effort_estimate = "high"

        action = PrioritizedAction(
            action_id=action_id,
            description=description,
            priority_score=priority_score,
            urgency_level=urgency_level,
            effort_estimate=effort_estimate,
            source_insight_id=insight.insight_id,
        )

        return action


# ==============================================================================
# Advanced Conflict Resolution
# ==============================================================================


class AdvancedConflictResolver:
    """
    Enhanced conflict resolution with multiple strategies.

    This class provides sophisticated mechanisms for resolving
    competing recommendations across different domains.
    """

    def __init__(self):
        # Domain priority hierarchy (higher = more important)
        self.domain_priorities = {
            "career-specialist": 4,
            "finance-specialist": 3,
            "wellness-specialist": 2,
            "relationship-specialist": 1,
        }

    def resolve_all_conflicts(
        self, conflicts: List[Dict[str, Any]], messages: Dict[str, Any]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Resolve all detected conflicts using adaptive strategies.

        Args:
            conflicts: List of conflict dictionaries
            messages: Specialist message data

        Returns:
            Tuple of (resolved_conflicts, unresolved_conflicts)
        """
        resolved = []
        unresolved = []

        for conflict in conflicts:
            resolution = self._resolve_single_conflict(conflict, messages)

            if resolution["status"] == "resolved":
                resolved.append(resolution)
            else:
                unresolved.append(resolution)

        return resolved, unresolved

    def _resolve_single_conflict(
        self, conflict: Dict[str, Any], messages: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve a single conflict using adaptive strategy."""
        specialist_1 = conflict.get("specialist_1")
        specialist_2 = conflict.get("specialist_2")
        severity = conflict.get("severity", "medium")

        # Choose resolution strategy based on severity
        if severity == "high":
            return self._priority_based_resolution(conflict, messages)
        else:
            return self._consensus_based_resolution(conflict, messages)

    def _priority_based_resolution(
        self, conflict: Dict[str, Any], messages: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve using domain priority."""
        specialist_1 = conflict.get("specialist_1")
        specialist_2 = conflict.get("specialist_2")

        priority_1 = self.domain_priorities.get(specialist_1, 0)
        priority_2 = self.domain_priorities.get(specialist_2, 0)

        if priority_1 > priority_2:
            preferred = specialist_1
        else:
            preferred = specialist_2

        return {
            "conflict": conflict,
            "status": "resolved",
            "strategy": "priority_based",
            "preferred_specialist": preferred,
            "rationale": f"{preferred} has higher domain priority",
        }

    def _consensus_based_resolution(
        self, conflict: Dict[str, Any], messages: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve using consensus/compromise."""
        specialist_1 = conflict.get("specialist_1")
        specialist_2 = conflict.get("specialist_2")

        return {
            "conflict": conflict,
            "status": "resolved",
            "strategy": "consensus_based",
            "approach": "compromise",
            "rationale": f"Seeking balanced approach between {specialist_1} and {specialist_2}",
        }


# ==============================================================================
# Main Integration Engine
# ==============================================================================


class ResultIntegrationEngine:
    """
    Main engine for integrating results from multiple specialists.

    Orchestrates harmonization, conflict resolution, synthesis,
    and action prioritization to generate unified responses.
    """

    def __init__(self):
        self.harmonizer = SpecialistOutputHarmonizer()
        self.synthesizer = CrossDomainSynthesizer()
        self.prioritizer = ActionPrioritizer()
        self.conflict_resolver = AdvancedConflictResolver()

    def integrate_results(
        self,
        user_id: str,
        query_timestamp: str,
        messages: Dict[str, Any],
        conflicts_detected: List[Dict[str, Any]],
        synergies_identified: List[Dict[str, Any]],
        user_goals: Optional[List[str]] = None,
    ) -> UnifiedResponse:
        """
        Perform complete result integration.

        Args:
            user_id: User identifier
            query_timestamp: When the original query was made
            messages: Specialist message data
            conflicts_detected: List of detected conflicts
            synergies_identified: List of identified synergies
            user_goals: Optional user goals for alignment

        Returns:
            UnifiedResponse with complete integration results
        """
        # Step 1: Harmonize recommendations
        harmonized_recommendations = self.harmonizer.harmonize_recommendations(messages)

        # Step 2: Resolve conflicts
        resolved_conflicts, unresolved_conflicts = self.conflict_resolver.resolve_all_conflicts(
            conflicts_detected, messages
        )

        # Step 3: Synthesize cross-domain insights
        integrated_insights = self.synthesizer.synthesize_insights(
            messages, harmonized_recommendations
        )

        # Step 4: Generate prioritized actions
        prioritized_actions = self.prioritizer.generate_prioritized_actions(
            integrated_insights, user_goals
        )

        # Step 5: Build unified response
        specialists_consulted = list(messages.keys())

        # Calculate overall confidence
        if integrated_insights:
            overall_confidence = sum(
                insight.confidence_score for insight in integrated_insights
            ) / len(integrated_insights)
        else:
            overall_confidence = 0.8

        unified_response = UnifiedResponse(
            user_id=user_id,
            query_timestamp=query_timestamp,
            specialists_consulted=specialists_consulted,
            integrated_insights=integrated_insights,
            conflicts_resolved=resolved_conflicts,
            synergies_identified=synergies_identified,
            prioritized_actions=prioritized_actions,
            overall_confidence=overall_confidence,
        )

        return unified_response


# ==============================================================================
# Integration Tools Factory
# ==============================================================================


def create_integration_tools(backend=None):
    """
    Create integration tools for result aggregation and synthesis.

    These tools enable the AI Life Coach coordinator to:
    - Harmonize outputs from multiple specialists
    - Resolve conflicts between competing recommendations
    - Synthesize cross-domain insights
    - Generate prioritized action lists
    - Create unified, coherent responses

    Args:
        backend: Optional FilesystemBackend instance. If None, uses get_backend()

    Returns:
        Tuple of integration tools (harmonize_specialist_outputs,
                                   synthesize_cross_domain_insights,
                                   generate_prioritized_action_list,
                                   create_unified_response)

    Example:
        >>> from src.config import config
        >>> config.initialize_environment()
        >>> tools = create_integration_tools()
        >>> result = harmonize_specialist_outputs(
        ...     user_id="user_123",
        ...     specialist_messages=[...]
        ... )
    """
    if backend is None:
        backend = get_backend()

    # Get the workspace directory path from backend
    workspace_path = Path(backend.root_dir) if hasattr(backend, "root_dir") else Path("workspace")

    # Initialize integration engine
    integration_engine = ResultIntegrationEngine()

    @tool
    def harmonize_specialist_outputs(
        user_id: str,
        specialist_messages: List[Dict[str, Any]],
    ) -> str:
        """Harmonize and normalize outputs from multiple specialist subagents.

        This tool collects, deduplicates, and merges recommendations from
        different specialists to create a coherent set of outputs.

        Args:
            user_id: The user's unique identifier
            specialist_messages: List of formatted specialist message dictionaries

        Returns:
            Harmonized results with merged recommendations and confidence scores
            Saved to harmonized_outputs/{user_id}/

        Example:
            >>> harmonize_specialist_outputs(
            ...     "user_123",
            ...     [
            ...         {"specialist_name": "career-specialist", "recommendations": [...]},
            ...         {"specialist_name": "wellness-specialist", "recommendations": [...]}
            ...     ]
            ... )
        """
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        if not specialist_messages or not isinstance(specialist_messages, list):
            return "Error: specialist_messages must be a non-empty list"

        try:
            # Convert to dictionary format
            messages_dict = {msg.get("specialist_name"): msg for msg in specialist_messages}

            # Harmonize recommendations
            harmonizer = SpecialistOutputHarmonizer()
            harmonized_recs = harmonizer.harmonize_recommendations(messages_dict)

            # Calculate overall confidence
            if harmonized_recs:
                avg_confidence = sum(
                    msg.get("confidence_level", 0.8) for msg in messages_dict.values()
                ) / len(messages_dict)
            else:
                avg_confidence = 0.8

            # Build result
            harmonization_result = {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "specialists_count": len(specialist_messages),
                "total_recommendations": len(harmonized_recs),
                "recommendations": harmonized_recs,
                "average_confidence": avg_confidence,
            }

            # Save to file
            json_content = json.dumps(harmonization_result, indent=2)
            today = date.today()
            timestamp = datetime.now().strftime("%H%M%S")
            path = f"harmonized_outputs/{user_id}/{today}_harmonization_{timestamp}.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            specialist_names = ", ".join(
                [name.replace("-specialist", "").title() for name in messages_dict.keys()]
            )

            response_parts = [
                f"Harmonized Outputs from {specialist_names}",
                "=" * 60,
                f"\nSpecialists Consulted: {len(specialist_messages)}",
                f"Total Recommendations (after harmonization): {len(harmonized_recs)}",
                f"Average Confidence: {avg_confidence:.1%}",
            ]

            response_parts.append("\nHarmonized Recommendations:")
            for i, rec in enumerate(harmonized_recs[:5], 1):
                title = rec.get("title", "Untitled")
                source = rec.get("source_specialist", "").replace("-specialist", "").title()
                priority = rec.get("priority", 5)
                response_parts.append(f"  {i}. {title} (from {source}, Priority: {priority})")

            if len(harmonized_recs) > 5:
                response_parts.append(f"  ... and {len(harmonized_recs) - 5} more")

            response_parts.append(f"\nHarmonization saved to: {path}")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error harmonizing specialist outputs: {str(e)}"

    @tool
    def synthesize_cross_domain_insights(
        user_id: str,
        specialist_messages: List[Dict[str, Any]],
        harmonized_recommendations_path: Optional[str] = None,
    ) -> str:
        """Synthesize integrated insights across multiple life domains.

        This tool identifies connections and patterns between different
        specialist outputs to create higher-level, cross-domain insights.

        Args:
            user_id: The user's unique identifier
            specialist_messages: List of formatted specialist message dictionaries
            harmonized_recommendations_path: Optional path to harmonization results

        Returns:
            Cross-domain insights with identified synergies and connections
            Saved to cross_domain_insights/{user_id}/

        Example:
            >>> synthesize_cross_domain_insights(
            ...     "user_123",
            ...     [{"specialist_name": "career-specialist", ...}, ...]
            ... )
        """
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        if not specialist_messages or not isinstance(specialist_messages, list):
            return "Error: specialist_messages must be a non-empty list"

        try:
            # Convert to dictionary format
            messages_dict = {msg.get("specialist_name"): msg for msg in specialist_messages}

            # Load harmonized recommendations if path provided, otherwise use messages
            if harmonized_recommendations_path:
                try:
                    if hasattr(backend, "read_file"):
                        json_content = backend.read_file(harmonized_recommendations_path)
                    else:
                        file_path = workspace_path / harmonized_recommendations_path
                        json_content = file_path.read_text()

                    harmony_data = json.loads(json_content)
                    harmonized_recs = harmony_data.get("recommendations", [])
                except FileNotFoundError:
                    return (
                        f"Error: Harmonization file not found at {harmonized_recommendations_path}"
                    )
            else:
                # Generate fresh harmonization
                harmonizer = SpecialistOutputHarmonizer()
                harmonized_recs = harmonizer.harmonize_recommendations(messages_dict)

            # Synthesize insights
            synthesizer = CrossDomainSynthesizer()
            integrated_insights = synthesizer.synthesize_insights(messages_dict, harmonized_recs)

            # Build result
            synthesis_result = {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "specialists_count": len(specialist_messages),
                "total_insights": len(integrated_insights),
                "insights": [insight.to_dict() for insight in integrated_insights],
            }

            # Save to file
            json_content = json.dumps(synthesis_result, indent=2)
            today = date.today()
            timestamp = datetime.now().strftime("%H%M%S")
            path = f"cross_domain_insights/{user_id}/{today}_synthesis_{timestamp}.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            response_parts = [
                "Cross-Domain Insight Synthesis",
                "=" * 60,
                f"\nSpecialists Analyzed: {len(specialist_messages)}",
                f"Integrated Insights Generated: {len(integrated_insights)}",
            ]

            if integrated_insights:
                response_parts.append("\nKey Insights:")
                for i, insight in enumerate(integrated_insights[:5], 1):
                    domains = ", ".join(list(insight.domains_affected))
                    response_parts.append(f"\n{i}. {insight.title}")
                    response_parts.append(f"   Domains: {domains}")
                    response_parts.append(f"   Confidence: {insight.confidence_score:.1%}")
                    response_parts.append(f"   Strength: {insight.strength_score:.1%}")
                    if insight.cross_domain_connections:
                        response_parts.append(
                            f"   Connections: {len(insight.cross_domain_connections)}"
                        )

            response_parts.append(f"\nSynthesis saved to: {path}")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error synthesizing cross-domain insights: {str(e)}"

    @tool
    def generate_prioritized_action_list(
        user_id: str,
        cross_domain_insights_path: Optional[str] = None,
        user_goals: Optional[List[str]] = None,
    ) -> str:
        """Generate a prioritized action list from integrated insights.

        This tool converts cross-domain insights into actionable items with
        clear priorities, urgency levels, and expected outcomes.

        Args:
            user_id: The user's unique identifier
            cross_domain_insights_path: Path to synthesis results JSON file
            user_goals: Optional list of user's stated goals for alignment

        Returns:
            Prioritized action items sorted by importance and urgency
            Saved to prioritized_actions/{user_id}/

        Example:
            >>> generate_prioritized_action_list(
            ...     "user_123",
            ...     user_goals=["advance career", "improve health"]
            ... )
        """
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        try:
            # Load insights
            if cross_domain_insights_path is None:
                insight_dir = workspace_path / "cross_domain_insights" / user_id
                if not insight_dir.exists():
                    return f"Error: No cross-domain insights found for user {user_id}"

                insight_files = sorted(
                    insight_dir.glob("*_synthesis_*.json"),
                    key=lambda p: p.stat().st_mtime,
                    reverse=True,
                )
                if not insight_files:
                    return f"Error: No cross-domain insights found for user {user_id}"

                cross_domain_insights_path = str(insight_files[0].relative_to(workspace_path))

            # Read the insights file
            try:
                if hasattr(backend, "read_file"):
                    json_content = backend.read_file(cross_domain_insights_path)
                else:
                    file_path = workspace_path / cross_domain_insights_path
                    json_content = file_path.read_text()

                synthesis_data = json.loads(json_content)
            except FileNotFoundError:
                return (
                    f"Error: Cross-domain insights file not found at {cross_domain_insights_path}"
                )

            # Reconstruct insight objects
            integrated_insights = []
            for insight_dict in synthesis_data.get("insights", []):
                insight = IntegratedInsight(
                    insight_id=insight_dict["insight_id"],
                    title=insight_dict["title"],
                    description=insight_dict["description"],
                    source_specialists=insight_dict.get("source_specialists", []),
                    domains_affected=set(insight_dict.get("domains_affected", [])),
                    confidence_score=insight_dict.get("confidence_score", 0.8),
                    strength_score=insight_dict.get("strength_score", 0.5),
                    cross_domain_connections=insight_dict.get("cross_domain_connections", []),
                    actionable_items=insight_dict.get("actionable_items", []),
                )
                integrated_insights.append(insight)

            # Generate prioritized actions
            prioritizer = ActionPrioritizer()
            prioritized_actions = prioritizer.generate_prioritized_actions(
                integrated_insights, user_goals
            )

            # Build result
            prioritization_result = {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "source_insights_count": len(integrated_insights),
                "total_actions": len(prioritized_actions),
                "user_goals": user_goals or [],
                "actions": [action.to_dict() for action in prioritized_actions],
            }

            # Save to file
            json_output = json.dumps(prioritization_result, indent=2)
            today = date.today()
            path = f"prioritized_actions/{user_id}/{today}_actions_{datetime.now().strftime('%H%M%S')}.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_output)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_output)

            # Format user-friendly response
            response_parts = [
                "Prioritized Action List",
                "=" * 60,
            ]

            if user_goals:
                response_parts.append(f"\nUser Goals: {', '.join(user_goals)}")

            response_parts.append(f"\nTotal Actions Generated: {len(prioritized_actions)}")

            # Group by urgency
            actions_by_urgency = {}
            for action in prioritized_actions:
                urgency = action.urgency_level
                if urgency not in actions_by_urgency:
                    actions_by_urgency[urgency] = []
                actions_by_urgency[urgency].append(action)

            urgency_order = ["immediate", "short_term", "medium_term", "long_term"]
            for urgency in urgency_order:
                if urgency not in actions_by_urgency:
                    continue

                urgency_title = urgency.replace("_", " ").title()
                response_parts.append(f"\n{urgency_title} Actions:")

                for i, action in enumerate(actions_by_urgency[urgency], 1):
                    response_parts.append(f"\n{i}. {action.description}")
                    response_parts.append(
                        f"   Priority Score: {action.priority_score:.1f}/10, "
                        f"Effort: {action.effort_estimate}"
                    )

            response_parts.append(f"\nPrioritized actions saved to: {path}")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error generating prioritized action list: {str(e)}"

    @tool
    def create_unified_response(
        user_id: str,
        specialist_messages: List[Dict[str, Any]],
        conflicts_detected: Optional[List[Dict[str, Any]]] = None,
        synergies_identified: Optional[List[Dict[str, Any]]] = None,
        user_goals: Optional[List[str]] = None,
    ) -> str:
        """Create a unified response integrating all specialist outputs.

        This is the main integration tool that orchestrates harmonization,
        conflict resolution, cross-domain synthesis, and action prioritization
        to produce a coherent, user-friendly unified response.

        Args:
            user_id: The user's unique identifier
            specialist_messages: List of formatted specialist message dictionaries
            conflicts_detected: Optional list of detected conflicts
            synergies_identified: Optional list of identified synergies
            user_goals: Optional list of user's stated goals

        Returns:
            Complete unified response with integrated insights and prioritized actions
            Saved to unified_responses/{user_id}/

        Example:
            >>> create_unified_response(
            ...     "user_123",
            ...     [{"specialist_name": "career-specialist", ...}, ...],
            ...     user_goals=["advance career"]
            ... )
        """
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        if not specialist_messages or not isinstance(specialist_messages, list):
            return "Error: specialist_messages must be a non-empty list"

        conflicts_detected = conflicts_detected or []
        synergies_identified = synergies_identified or []

        try:
            # Convert to dictionary format
            messages_dict = {msg.get("specialist_name"): msg for msg in specialist_messages}

            query_timestamp = (
                messages_dict.get(next(iter(messages_dict)), {}).get("timestamp")
                or datetime.now().isoformat()
            )

            # Use integration engine to generate unified response
            unified_response = integration_engine.integrate_results(
                user_id=user_id,
                query_timestamp=query_timestamp,
                messages=messages_dict,
                conflicts_detected=conflicts_detected,
                synergies_identified=synergies_identified,
                user_goals=user_goals,
            )

            # Save to file
            json_content = json.dumps(unified_response.to_dict(), indent=2)
            today = date.today()
            path = f"unified_responses/{user_id}/{today}_unified_{datetime.now().strftime('%H%M%S')}.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            specialist_names = ", ".join(
                [
                    name.replace("-specialist", "").title()
                    for name in unified_response.specialists_consulted
                ]
            )

            response_parts = [
                f"## Unified Response from {specialist_names} Specialists",
                "=" * 70,
            ]

            # Executive summary
            response_parts.append("\n### Executive Summary")
            response_parts.append(
                f"Based on analysis from {len(unified_response.specialists_consulted)} specialists, "
                f"we generated {len(unified_response.integrated_insights)} integrated insights "
                f"and {len(unified_response.prioritized_actions)} prioritized actions."
            )
            response_parts.append(f"Overall confidence: {unified_response.overall_confidence:.1%}")

            # Conflicts resolved
            if unified_response.conflicts_resolved:
                response_parts.append(
                    f"\n### Conflicts Resolved: {len(unified_response.conflicts_resolved)}"
                )
                for i, resolution in enumerate(unified_response.conflicts_resolved[:3], 1):
                    strategy = resolution.get("strategy", "N/A")
                    rationale = resolution.get("rationale", "")
                    response_parts.append(f"{i}. {strategy.replace('_', ' ').title()}: {rationale}")

            # Synergies identified
            if unified_response.synergies_identified:
                response_parts.append(
                    f"\n### Cross-Domain Synergies: {len(unified_response.synergies_identified)}"
                )
                for i, synergy in enumerate(unified_response.synergies_identified[:3], 1):
                    desc = synergy.get("description", "")
                    response_parts.append(f"{i}. {desc}")

            # Integrated insights
            if unified_response.integrated_insights:
                response_parts.append(
                    f"\n### Integrated Insights: {len(unified_response.integrated_insights)}"
                )
                for i, insight in enumerate(unified_response.integrated_insights[:5], 1):
                    domains = ", ".join(list(insight.domains_affected))
                    response_parts.append(f"\n{i}. {insight.title}")
                    response_parts.append(
                        f"   Domains: {domains} | Confidence: {insight.confidence_score:.1%}"
                    )
                    response_parts.append(f"   {insight.description[:150]}...")

            # Prioritized actions
            if unified_response.prioritized_actions:
                response_parts.append(
                    f"\n### Prioritized Actions: {len(unified_response.prioritized_actions)}"
                )

                # Group by urgency
                top_immediate = [
                    a
                    for a in unified_response.prioritized_actions
                    if a.urgency_level == "immediate"
                ][:3]
                top_short = [
                    a
                    for a in unified_response.prioritized_actions
                    if a.urgency_level == "short_term"
                ][:2]
                top_medium = [
                    a
                    for a in unified_response.prioritized_actions
                    if a.urgency_level == "medium_term"
                ][:2]

                if top_immediate:
                    response_parts.append("\n**Immediate Actions:**")
                    for i, action in enumerate(top_immediate, 1):
                        response_parts.append(f"{i}. {action.description}")

                if top_short:
                    response_parts.append("\n**Short-Term Actions:**")
                    for i, action in enumerate(top_short, 1):
                        response_parts.append(f"{i}. {action.description}")

                if top_medium:
                    response_parts.append("\n**Medium-Term Actions:**")
                    for i, action in enumerate(top_medium, 1):
                        response_parts.append(f"{i}. {action.description}")

            # Footer
            response_parts.append("\n---")
            response_parts.append(
                f"*Unified response generated at {unified_response.integration_timestamp}*"
            )
            response_parts.append(f"*Full details saved to: {path}*")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error creating unified response: {str(e)}"

    return (
        harmonize_specialist_outputs,
        synthesize_cross_domain_insights,
        generate_prioritized_action_list,
        create_unified_response,
    )
