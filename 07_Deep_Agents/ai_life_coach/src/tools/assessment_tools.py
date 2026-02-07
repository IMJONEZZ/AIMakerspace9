"""
Multi-Domain Assessment Tools for AI Life Coach.

This module provides tools for conducting comprehensive assessments across
all life domains, integrating specialist insights, and generating prioritized
action plans.

Tools:
- conduct_initial_assessment: Orchestrate baseline multi-domain assessment
- prioritize_domains_by_urgency: Algorithm to rank domains by urgency and impact
- assess_cross_domain_impacts: Analyze how changes in one domain affect others
- generate_integrated_report: Create comprehensive assessment report
- design_follow_up_questions: Generate targeted follow-up questions based on gaps

Based on research in:
- Multi-domain assessment frameworks (MAQIP, CLEAR Metrics)
- Cross-domain impact analysis methods
- Holistic life assessment tools (Wellness Wheel, Wheel of Life)
- Priority-weighted multi-criteria decision analysis
"""

from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
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
# Domain Definitions and Frameworks
# ==============================================================================

LIFE_DOMAINS = {
    "career": {
        "name": "Career & Professional Development",
        "description": "Work satisfaction, career progression, skill development, and professional goals",
        "specialist": "Career Specialist",
        "assessment_tools": ["analyze_skill_gap", "create_career_path_plan"],
        "key_indicators": [
            "Job satisfaction",
            "Career growth trajectory",
            "Skill development progress",
            "Work-life balance",
            "Professional network quality",
        ],
    },
    "relationship": {
        "name": "Relationships & Social Connection",
        "description": "Quality of relationships with family, friends, romantic partners, and community",
        "specialist": "Relationship Specialist",
        "assessment_tools": ["assess_relationship_quality", "develop_social_connection_plan"],
        "key_indicators": [
            "Relationship satisfaction",
            "Communication quality",
            "Support network strength",
            "Social connection frequency",
            "Boundary health",
        ],
    },
    "finance": {
        "name": "Financial Health & Stability",
        "description": "Budgeting, savings, debt management, and financial planning for goals",
        "specialist": "Finance Specialist",
        "assessment_tools": [
            "create_budget_analyzer",
            "calculate_emergency_fund_target",
        ],
        "key_indicators": [
            "Budget adherence",
            "Emergency fund status",
            "Debt-to-income ratio",
            "Savings rate",
            "Financial goal progress",
        ],
    },
    "wellness": {
        "name": "Wellness & Personal Growth",
        "description": "Physical, emotional, and mental wellbeing including habits, stress management, and self-care",
        "specialist": "Wellness Specialist",
        "assessment_tools": [
            "assess_wellness_dimensions",
            "create_habit_formation_plan",
        ],
        "key_indicators": [
            "Physical activity level",
            "Sleep quality",
            "Stress management",
            "Emotional regulation",
            "Self-care practices",
        ],
    },
}

# Cross-domain impact matrix (how changes in one domain affect others)
CROSS_DOMAIN_IMPACTS = {
    ("career", "wellness"): {
        "impact_type": "bidirectional",
        "strength": 0.8,
        "description": "Career stress affects wellness; good health improves work performance",
    },
    ("career", "finance"): {
        "impact_type": "career_to_finance",
        "strength": 0.9,
        "description": "Career determines income; financial decisions may constrain career choices",
    },
    ("wellness", "relationship"): {
        "impact_type": "bidirectional",
        "strength": 0.7,
        "description": "Health affects relationship quality; relationships impact emotional wellbeing",
    },
    ("finance", "wellness"): {
        "impact_type": "finance_to_wellness",
        "strength": 0.6,
        "description": "Financial stress affects mental health; good health reduces healthcare costs",
    },
    ("finance", "relationship"): {
        "impact_type": "bidirectional",
        "strength": 0.5,
        "description": "Financial disagreements strain relationships; shared goals strengthen bonds",
    },
    ("career", "relationship"): {
        "impact_type": "bidirectional",
        "strength": 0.7,
        "description": "Work demands affect personal time; relationships provide emotional support",
    },
}


# ==============================================================================
# Assessment Tool Factory
# ==============================================================================


def create_assessment_tools(backend=None) -> tuple:
    """
    Create multi-domain assessment tools with shared FilesystemBackend instance.

    These tools enable the Life Coach to:
    - Conduct comprehensive baseline assessments across all domains
    - Prioritize focus areas based on urgency, impact, and user goals
    - Analyze cross-domain connections and interdependencies
    - Generate integrated assessment reports with actionable recommendations
    - Design targeted follow-up questions to fill information gaps

    Args:
        backend: Optional FilesystemBackend instance. If None, uses get_backend()

    Returns:
        Tuple of assessment tools (conduct_initial_assessment,
                                prioritize_domains_by_urgency,
                                assess_cross_domain_impacts,
                                generate_integrated_report,
                                design_follow_up_questions)

    Example:
        >>> from src.config import config
        >>> config.initialize_environment()
        >>> tools = create_assessment_tools()
        >>> result = conduct_initial_assessment(
        ...     user_id="user_123",
        ...     goals=["Advance career", "Improve fitness"],
        ...     current_situation="Mid-level professional, looking to grow"
        ... )
    """
    if backend is None:
        backend = get_backend()

    # Get the workspace directory path from backend
    workspace_path = Path(backend.root_dir) if hasattr(backend, "root_dir") else Path("workspace")

    @tool
    def conduct_initial_assessment(
        user_id: str,
        goals: List[str],
        current_situation: Optional[str] = None,
        demographics: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Conduct comprehensive baseline assessment across all life domains.

        This tool orchestrates a holistic initial assessment that:
        1. Gathers baseline information (demographics, current situation)
        2. Structurally assesses each domain independently
        3. Identifies cross-domain connections and patterns
        4. Creates foundation for prioritized action planning

        Args:
            user_id: The user's unique identifier
            goals: List of primary life goals (e.g., ["Advance career", "Improve fitness"])
            current_situation: Optional brief description of current life situation
            demographics: Optional dictionary with demographic information

        Returns:
            Structured initial assessment with domain scores, patterns, and
            prioritization recommendations. Saved to assessments/{user_id}/

        Raises:
            ValueError: If required parameters are invalid

        Example:
            >>> conduct_initial_assessment(
            ...     "user_123",
            ...     ["Get promoted to manager", "Build better relationships"],
            ...     "Software engineer at mid-sized company"
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not goals or not isinstance(goals, list):
            return "Error: goals must be a non-empty list"

        try:
            # Initialize assessment structure
            assessment = {
                "assessment_type": "initial_baseline",
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "goals": goals,
                "current_situation": current_situation or "Not provided",
                "demographics": demographics or {},
                "domains": {},
                "cross_domain_analysis": {},
                "recommendations": [],
            }

            # Initialize each domain assessment
            for domain_key, domain_info in LIFE_DOMAINS.items():
                assessment["domains"][domain_key] = {
                    "name": domain_info["name"],
                    "specialist": domain_info["specialist"],
                    "status": "pending_assessment",  # pending, in_progress, completed
                    "score": None,
                    "key_indicators": domain_info["key_indicators"],
                    "strengths": [],
                    "challenges": [],
                    "assessment_tools_needed": domain_info["assessment_tools"],
                }

            # Map goals to domains
            goal_domain_mapping = {}
            for goal in goals:
                goal_lower = goal.lower()
                mapped_domains = []
                if any(
                    keyword in goal_lower
                    for keyword in ["career", "job", "work", "promote", "professional"]
                ):
                    mapped_domains.append("career")
                if any(
                    keyword in goal_lower
                    for keyword in [
                        "relationship",
                        "friend",
                        "family",
                        "social",
                        "connect",
                    ]
                ):
                    mapped_domains.append("relationship")
                if any(
                    keyword in goal_lower
                    for keyword in ["money", "save", "finance", "debt", "budget"]
                ):
                    mapped_domains.append("finance")
                if any(
                    keyword in goal_lower
                    for keyword in [
                        "health",
                        "fitness",
                        "wellness",
                        "weight",
                        "exercise",
                    ]
                ):
                    mapped_domains.append("wellness")

                goal_domain_mapping[goal] = mapped_domains

            assessment["goal_domain_mapping"] = goal_domain_mapping

            # Identify priority domains based on goals
            domain_priority_scores = {}
            for domain_key in LIFE_DOMAINS.keys():
                # Count how many goals map to this domain
                goal_count = sum(
                    1 for domains in goal_domain_mapping.values() if domain_key in domains
                )
                domain_priority_scores[domain_key] = goal_count

            assessment["domain_priority_initial"] = domain_priority_scores

            # Generate initial recommendations
            recommendations = []
            if goal_domain_mapping:
                recommendations.append(
                    f"Primary focus areas: {', '.join(set([d for domains in goal_domain_mapping.values() for d in domains]))}"
                )
            recommendations.append(
                "Complete specialist assessments for each domain to gather detailed information"
            )
            recommendations.append(
                "Review cross-domain connections after individual assessments are complete"
            )

            assessment["recommendations"] = recommendations

            # Save assessment
            json_content = json.dumps(assessment, indent=2)
            today = date.today()
            path = f"assessments/{user_id}/{today}_initial_baseline.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            response_parts = [
                "Initial Multi-Domain Assessment",
                "=" * 60,
                f"\nUser ID: {user_id}",
                f"Date: {today.strftime('%Y-%m-%d')}",
                f"\nGoals:",
            ]

            for i, goal in enumerate(goals, 1):
                mapped = ", ".join(
                    [LIFE_DOMAINS[d]["name"] for d in goal_domain_mapping.get(goal, [])]
                )
                response_parts.append(f"  {i}. {goal} → {mapped}")

            response_parts.append("\nCurrent Situation:")
            response_parts.append(f"  {current_situation or 'Not provided'}")

            response_parts.append("\nDomains to Assess:")
            for domain_key, info in LIFE_DOMAINS.items():
                priority = domain_priority_scores.get(domain_key, 0)
                response_parts.append(
                    f"  • {info['name']} (Priority: {'High' if priority > 0 else 'General'})"
                )

            response_parts.append("\nNext Steps:")
            for i, rec in enumerate(recommendations, 1):
                response_parts.append(f"  {i}. {rec}")

            response_parts.append(f"\nAssessment framework saved to: {path}")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error conducting initial assessment: {str(e)}"

    @tool
    def prioritize_domains_by_urgency(
        user_id: str,
        domain_scores: Dict[str, float],
        urgency_factors: Optional[Dict[str, List[str]]] = None,
        user_goals: Optional[List[str]] = None,
    ) -> str:
        """Prioritize domains using urgency, impact, and goal-alignment algorithm.

        This tool implements a multi-criteria decision analysis (MCDA) approach to
        prioritize domains based on:
        1. Baseline domain scores (lower scores = higher urgency)
        2. User-provided urgency factors and constraints
        3. Alignment with stated user goals
        4. Cross-domain impact potential (leverage points)

        Args:
            user_id: The user's unique identifier
            domain_scores: Dictionary mapping domains to current scores (1-10 scale)
                           e.g., {"career": 6, "wellness": 4}
            urgency_factors: Optional dict mapping domains to urgent issues
                            e.g., {"finance": ["pending bills", "debt deadline"]}
            user_goals: Optional list of current goals for alignment scoring

        Returns:
            Prioritized domain list with scores, reasoning, and action recommendations.
            Saved to assessments/{user_id}/

        Raises:
            ValueError: If required parameters are invalid

        Example:
            >>> prioritize_domains_by_urgency(
            ...     "user_123",
            ...     {"career": 6, "wellness": 3, "finance": 5},
            ...     {"finance": ["rent due soon"]}
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not domain_scores or not isinstance(domain_scores, dict):
            return "Error: domain_scores must be a non-empty dictionary"

        try:
            # Initialize prioritization analysis
            priority_analysis = {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "input_domain_scores": domain_scores,
                "urgency_factors": urgency_factors or {},
                "user_goals": user_goals or [],
                "domain_priorities": {},
            }

            # Calculate priority score for each domain
            # Formula: Priority = (10 - baseline_score) * 0.4 + urgency_bonus + goal_alignment_bonus
            for domain_key, baseline_score in domain_scores.items():
                if domain_key not in LIFE_DOMAINS:
                    continue

                # Base priority: inverse of current score
                base_priority = (10 - baseline_score) * 0.4

                # Urgency bonus: if domain has urgent factors, boost priority
                urgency_bonus = 0.0
                urgent_issues = []
                if domain_key in (urgency_factors or {}):
                    issue_count = len(urgency_factors[domain_key])
                    urgency_bonus = min(issue_count * 1.5, 3.0)  # Cap at 3.0
                    urgent_issues = urgency_factors[domain_key]

                # Goal alignment bonus: higher priority for domains aligned with goals
                goal_alignment_bonus = 0.0
                if user_goals:
                    for goal in user_goals:
                        goal_lower = goal.lower()
                        # Check if domain is relevant to this goal
                        if domain_key == "career" and any(
                            kw in goal_lower for kw in ["career", "job", "work"]
                        ):
                            goal_alignment_bonus += 0.5
                        elif domain_key == "wellness" and any(
                            kw in goal_lower for kw in ["health", "fitness", "wellness"]
                        ):
                            goal_alignment_bonus += 0.5
                        elif domain_key == "finance" and any(
                            kw in goal_lower for kw in ["money", "save", "debt"]
                        ):
                            goal_alignment_bonus += 0.5
                        elif domain_key == "relationship" and any(
                            kw in goal_lower for kw in ["relationship", "friend"]
                        ):
                            goal_alignment_bonus += 0.5

                    goal_alignment_bonus = min(goal_alignment_bonus, 2.0)  # Cap at 2.0

                # Calculate total priority score
                total_priority = base_priority + urgency_bonus + goal_alignment_bonus

                # Normalize to 0-10 scale
                normalized_priority = min(total_priority, 10)

                priority_analysis["domain_priorities"][domain_key] = {
                    "baseline_score": baseline_score,
                    "base_priority_contribution": round(base_priority, 2),
                    "urgency_bonus": round(urgency_bonus, 2),
                    "urgent_issues": urgent_issues,
                    "goal_alignment_bonus": round(goal_alignment_bonus, 2),
                    "total_priority_score": round(normalized_priority, 1),
                }

            # Sort domains by priority
            sorted_domains = sorted(
                priority_analysis["domain_priorities"].items(),
                key=lambda x: x[1]["total_priority_score"],
                reverse=True,
            )

            # Generate recommendations based on prioritization
            recommendations = []
            for i, (domain_key, priority_data) in enumerate(sorted_domains):
                if i == 0:
                    recommendations.append(
                        f"Highest Priority: {LIFE_DOMAINS[domain_key]['name']} "
                        f"(Score: {priority_data['total_priority_score']}/10)"
                    )
                elif i < 2:
                    recommendations.append(
                        f"High Priority: {LIFE_DOMAINS[domain_key]['name']} "
                        f"(Score: {priority_data['total_priority_score']}/10)"
                    )

                if priority_data["urgent_issues"]:
                    recommendations.append(
                        f"  - Urgent issues in {LIFE_DOMAINS[domain_key]['name']}: "
                        f"{', '.join(priority_data['urgent_issues'])}"
                    )

            if len(sorted_domains) > 2:
                recommendations.append(
                    f"Other domains: {', '.join([LIFE_DOMAINS[d]['name'] for d, _ in sorted_domains[2:]])}"
                )

            priority_analysis["recommendations"] = recommendations

            # Save prioritization analysis
            json_content = json.dumps(priority_analysis, indent=2)
            today = date.today()
            path = f"assessments/{user_id}/{today}_domain_prioritization.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            response_parts = [
                "Domain Prioritization Analysis",
                "=" * 60,
                f"\nPrioritized Domains (Highest to Lowest):",
            ]

            for i, (domain_key, priority_data) in enumerate(sorted_domains, 1):
                response_parts.append(
                    f"\n{i}. {LIFE_DOMAINS[domain_key]['name']} "
                    f"(Priority: {priority_data['total_priority_score']}/10)"
                )
                response_parts.append(f"   Current Score: {priority_data['baseline_score']}/10")

                if priority_data["urgent_issues"]:
                    response_parts.append(
                        f"   Urgent Issues: {', '.join(priority_data['urgent_issues'])}"
                    )

                explanation = (
                    f"   Priority Breakdown: Base ({priority_data['base_priority_contribution']}) "
                )
                if priority_data["urgency_bonus"] > 0:
                    explanation += f"+ Urgency ({priority_data['urgency_bonus']}) "
                if priority_data["goal_alignment_bonus"] > 0:
                    explanation += f"+ Goal Alignment ({priority_data['goal_alignment_bonus']}) "
                response_parts.append(explanation)

            response_parts.append("\nRecommendations:")
            for i, rec in enumerate(recommendations, 1):
                response_parts.append(f"  {i}. {rec}")

            response_parts.append(f"\nPrioritization analysis saved to: {path}")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error prioritizing domains: {str(e)}"

    @tool
    def assess_cross_domain_impacts(
        user_id: str,
        domain_changes: Dict[str, str],
        current_domain_scores: Optional[Dict[str, float]] = None,
    ) -> str:
        """Analyze how changes in one domain affect other life domains.

        This tool uses the cross-domain impact matrix to identify:
        1. Which domains will be positively impacted by planned changes
        2. Which domains might experience negative side effects or trade-offs
        3. Synergies where improvements in one domain amplify others
        4. Conflicts where progress in one area may hinder another

        Args:
            user_id: The user's unique identifier
            domain_changes: Dictionary mapping domains to planned changes/actions
                           e.g., {"career": "Take on new role with more responsibility"}
            current_domain_scores: Optional dict of current domain scores (1-10 scale)

        Returns:
            Cross-domain impact analysis with positive/negative impacts,
            synergies, conflicts, and mitigation strategies. Saved to assessments/{user_id}/

        Raises:
            ValueError: If required parameters are invalid

        Example:
            >>> assess_cross_domain_impacts(
            ...     "user_123",
            ...     {"career": "Accept promotion requiring more hours"},
            ...     {"wellness": 6, "relationship": 5}
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not domain_changes or not isinstance(domain_changes, dict):
            return "Error: domain_changes must be a non-empty dictionary"

        try:
            # Initialize impact analysis
            impact_analysis = {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "planned_changes": domain_changes,
                "current_domain_scores": current_domain_scores or {},
                "positive_impacts": [],
                "negative_risks": [],
                "synergies": [],
                "conflicts": [],
                "mitigation_strategies": [],
            }

            # Analyze impacts for each planned change
            for source_domain, change_description in domain_changes.items():
                if source_domain not in LIFE_DOMAINS:
                    continue

                # Check all cross-domain connections
                for (domain_a, domain_b), impact_data in CROSS_DOMAIN_IMPACTS.items():
                    # Check if this change involves either domain in the pair
                    target_domain = None
                    impact_direction = None

                    if source_domain == domain_a:
                        target_domain = domain_b
                        impact_direction = impact_data["impact_type"]
                    elif source_domain == domain_b:
                        target_domain = domain_a
                        # Reverse the direction for impact type interpretation
                        if impact_data["impact_type"] == "career_to_finance":
                            # This becomes finance_to_career
                            impact_direction = "finance_to_career"
                        elif impact_data["impact_type"] == "finance_to_wellness":
                            impact_direction = "wellness_to_finance"
                        else:
                            impact_direction = impact_data["impact_type"]

                    if target_domain is None:
                        continue

                    strength = impact_data["strength"]
                    description = impact_data["description"]

                    # Analyze based on change content
                    positive_indicators = ["improve", "better", "increase", "enhance", "grow"]
                    negative_indicators = ["reduce", "cut", "decrease", "less", "burden"]

                    change_lower = change_description.lower()
                    has_positive = any(ind in change_lower for ind in positive_indicators)
                    has_negative = any(ind in change_lower for ind in negative_indicators)

                    # Determine impact type
                    if has_positive or not any([has_positive, has_negative]):
                        # Default to positive for neutral changes
                        impact_analysis["positive_impacts"].append(
                            {
                                "source_domain": source_domain,
                                "target_domain": target_domain,
                                "impact_strength": strength,
                                "description": description,
                                "planned_change": change_description,
                            }
                        )

                    # Check for potential negative side effects
                    if any(
                        keyword in change_lower
                        for keyword in ["more hours", "stressful", "demanding"]
                    ):
                        risk_assessment = {
                            "source_domain": source_domain,
                            "target_domain": target_domain,
                            "risk_description": f"Planned change '{change_description}' may negatively impact {LIFE_DOMAINS[target_domain]['name']}",
                            "risk_level": strength,  # Higher strength = higher risk
                        }

                        if target_domain == "wellness":
                            risk_assessment["specific_risks"] = [
                                "Increased stress levels",
                                "Reduced time for self-care",
                                "Potential sleep disruption",
                            ]
                        elif target_domain == "relationship":
                            risk_assessment["specific_risks"] = [
                                "Less quality time with loved ones",
                                "Potential relationship strain",
                            ]
                        elif target_domain == "finance":
                            risk_assessment["specific_risks"] = [
                                "Potential burnout affecting income",
                                "Healthcare costs from stress",
                            ]

                        impact_analysis["negative_risks"].append(risk_assessment)

            # Identify synergies (positive impacts on multiple domains)
            if len(impact_analysis["positive_impacts"]) >= 2:
                # Check if same source affects multiple targets positively
                source_counts = {}
                for impact in impact_analysis["positive_impacts"]:
                    src = impact["source_domain"]
                    source_counts[src] = source_counts.get(src, 0) + 1

                for src, count in source_counts.items():
                    if count >= 2:
                        impact_analysis["synergies"].append(
                            {
                                "source_domain": src,
                                "description": f"Improvements in {LIFE_DOMAINS[src]['name']} will positively impact multiple areas of life",
                                "affected_domains": [
                                    imp["target_domain"]
                                    for imp in impact_analysis["positive_impacts"]
                                    if imp["source_domain"] == src
                                ],
                            }
                        )

            # Identify conflicts (negative risks to vulnerable domains)
            if current_domain_scores and impact_analysis["negative_risks"]:
                for risk in impact_analysis["negative_risks"]:
                    target = risk["target_domain"]
                    if target in current_domain_scores:
                        score = current_domain_scores[target]
                        if score < 5:  # Low scores indicate vulnerability
                            impact_analysis["conflicts"].append(
                                {
                                    "risk": risk,
                                    "vulnerability_reason": f"{LIFE_DOMAINS[target]['name']} currently has low score ({score}/10)",
                                    "recommendation": f"Consider protective measures for {LIFE_DOMAINS[target]['name']}",
                                }
                            )

            # Generate mitigation strategies
            if impact_analysis["negative_risks"]:
                for risk in impact_analysis["negative_risks"]:
                    target = risk["target_domain"]
                    mitigation = {
                        "risk": risk["risk_description"],
                        "strategies": [],
                    }

                    if target == "wellness":
                        mitigation["strategies"] = [
                            "Schedule dedicated self-care time",
                            "Set boundaries for work hours",
                            "Practice stress management techniques",
                        ]
                    elif target == "relationship":
                        mitigation["strategies"] = [
                            "Schedule regular quality time with loved ones",
                            "Communicate changes and expectations clearly",
                            "Maintain existing routines as much as possible",
                        ]
                    elif target == "finance":
                        mitigation["strategies"] = [
                            "Build emergency buffer before changes",
                            "Monitor healthcare costs",
                            "Review budget for new expenses",
                        ]

                    impact_analysis["mitigation_strategies"].append(mitigation)

            # Save impact analysis
            json_content = json.dumps(impact_analysis, indent=2)
            today = date.today()
            path = f"assessments/{user_id}/{today}_cross_domain_impacts.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            response_parts = [
                "Cross-Domain Impact Analysis",
                "=" * 60,
                f"\nPlanned Changes:",
            ]

            for domain, change in domain_changes.items():
                response_parts.append(
                    f"  • {LIFE_DOMAINS.get(domain, {}).get('name', domain)}: {change}"
                )

            if impact_analysis["positive_impacts"]:
                response_parts.append("\n✓ Positive Impacts (Leverage Points):")
                for impact in impact_analysis["positive_impacts"]:
                    response_parts.append(
                        f"  • {LIFE_DOMAINS[impact['source_domain']]['name']} → "
                        f"{LIFE_DOMAINS[impact['target_domain']]['name']}"
                    )
                    response_parts.append(f"    {impact['description']}")

            if impact_analysis["negative_risks"]:
                response_parts.append("\n⚠ Potential Negative Risks:")
                for risk in impact_analysis["negative_risks"]:
                    response_parts.append(f"  • {risk['risk_description']}")
                    if "specific_risks" in risk:
                        for specific in risk["specific_risks"]:
                            response_parts.append(f"    - {specific}")

            if impact_analysis["synergies"]:
                response_parts.append("\n🔄 Synergies Identified:")
                for synergy in impact_analysis["synergies"]:
                    response_parts.append(f"  • {synergy['description']}")
                    affected = ", ".join(
                        [LIFE_DOMAINS[d]["name"] for d in synergy["affected_domains"]]
                    )
                    response_parts.append(f"    Affects: {affected}")

            if impact_analysis["conflicts"]:
                response_parts.append("\n⚡ Conflicts with Vulnerable Areas:")
                for conflict in impact_analysis["conflicts"]:
                    response_parts.append(f"  • {conflict['vulnerability_reason']}")
                    response_parts.append(f"    Suggestion: {conflict['recommendation']}")

            if impact_analysis["mitigation_strategies"]:
                response_parts.append("\n🛡️ Mitigation Strategies:")
                for i, mitigation in enumerate(impact_analysis["mitigation_strategies"], 1):
                    response_parts.append(f"  {i}. For: {mitigation['risk']}")
                    for strategy in mitigation["strategies"]:
                        response_parts.append(f"     • {strategy}")

            response_parts.append(f"\nImpact analysis saved to: {path}")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error analyzing cross-domain impacts: {str(e)}"

    @tool
    def generate_integrated_report(
        user_id: str,
        domain_assessments: Dict[str, Dict[str, Any]],
        priotization_data: Optional[Dict[str, Any]] = None,
        cross_domain_analysis: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate comprehensive integrated assessment report.

        This tool synthesizes all assessment data into a cohesive, human-readable
        report that includes:
        1. Executive summary of overall life balance and priorities
        2. Domain-by-domain analysis with scores, strengths, and challenges
        3. Cross-domain connections and interdependencies
        4. Prioritized action plan with short/medium/long-term steps
        5. Follow-up questions to guide ongoing coaching

        Args:
            user_id: The user's unique identifier
            domain_assessments: Dictionary of completed assessments per domain
                                e.g., {"career": {...}, "wellness": {...}}
            priotization_data: Optional data from domain prioritization analysis
            cross_domain_analysis: Optional results from cross-domain impact analysis

        Returns:
            Comprehensive integrated report in both JSON and Markdown formats.
            Saved to assessments/{user_id}/reports/

        Raises:
            ValueError: If required parameters are invalid

        Example:
            >>> generate_integrated_report(
            ...     "user_123",
            ...     {"career": {"score": 6, "strengths": [...], "challenges": [...]}}
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not domain_assessments or not isinstance(domain_assessments, dict):
            return "Error: domain_assessments must be a non-empty dictionary"

        try:
            # Initialize report structure
            report = {
                "report_type": "integrated_assessment",
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "executive_summary": {},
                "domain_analyses": {},
                "cross_domain_insights": cross_domain_analysis or {},
                "prioritized_action_plan": [],
            }

            # Calculate overall life balance score
            total_score = 0
            score_count = 0
            for domain_key, assessment in domain_assessments.items():
                if "score" in assessment and isinstance(assessment["score"], (int, float)):
                    total_score += assessment["score"]
                    score_count += 1

            overall_balance = (total_score / score_count) if score_count > 0 else None

            report["executive_summary"] = {
                "overall_balance_score": round(overall_balance, 1) if overall_balance else None,
                "domains_assessed": list(domain_assessments.keys()),
                "number_of_domains": len(domain_assessments),
            }

            # Add balance assessment
            if overall_balance:
                if overall_balance >= 8:
                    balance_assessment = "Strong - Good balance across domains"
                elif overall_balance >= 6:
                    balance_assessment = "Moderate - Some areas need attention"
                elif overall_balance >= 4:
                    balance_assessment = "Needs Attention - Several areas require focus"
                else:
                    balance_assessment = "Critical - Comprehensive support needed"

                report["executive_summary"]["balance_assessment"] = balance_assessment

            # Compile domain analyses
            for domain_key, assessment in domain_assessments.items():
                if domain_key not in LIFE_DOMAINS:
                    continue

                report["domain_analyses"][domain_key] = {
                    "name": LIFE_DOMAINS[domain_key]["name"],
                    "score": assessment.get("score"),
                    "strengths": assessment.get("strengths", []),
                    "challenges": assessment.get("challenges", []),
                    "key_insights": assessment.get("insights", []),
                }

            # Generate prioritized action plan
            if priotization_data and "domain_priorities" in priotization_data:
                sorted_domains = sorted(
                    priotization_data["domain_priorities"].items(),
                    key=lambda x: x[1].get("total_priority_score", 0),
                    reverse=True,
                )

                for domain_key, priority_data in sorted_domains:
                    if domain_key not in domain_assessments:
                        continue

                    assessment = domain_assessments[domain_key]
                    prioritized_item = {
                        "domain": LIFE_DOMAINS[domain_key]["name"],
                        "priority_score": priority_data.get("total_priority_score", 0),
                        "current_score": assessment.get("score"),
                        "focus_areas": assessment.get("challenges", [])[:2],  # Top 2 challenges
                        "recommended_actions": [],
                    }

                    # Generate domain-specific actions
                    if domain_key == "career":
                        prioritized_item["recommended_actions"] = [
                            "Schedule career planning session",
                            "Identify skill development priorities",
                            "Update professional goals document",
                        ]
                    elif domain_key == "wellness":
                        prioritized_item["recommended_actions"] = [
                            "Establish daily self-care routine",
                            "Schedule health checkup if needed",
                            "Create habit formation plan",
                        ]
                    elif domain_key == "finance":
                        prioritized_item["recommended_actions"] = [
                            "Review current budget and expenses",
                            "Set up emergency fund contributions",
                            "Prioritize debt payments if applicable",
                        ]
                    elif domain_key == "relationship":
                        prioritized_item["recommended_actions"] = [
                            "Schedule quality time with key relationships",
                            "Practice active listening skills",
                            "Review and adjust relationship boundaries",
                        ]

                    report["prioritized_action_plan"].append(prioritized_item)

            # Save JSON report
            json_content = json.dumps(report, indent=2)
            today = date.today()
            path = f"assessments/{user_id}/reports/{today}_integrated_assessment.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Generate Markdown report
            md_report = f"""# Integrated Life Assessment Report

**User ID:** {user_id}
**Assessment Date:** {today.strftime("%B %d, %Y")}
**Report Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}

---

## Executive Summary

**Overall Life Balance Score:** {report["executive_summary"]["overall_balance_score"]}/10
**Balance Assessment:** {report["executive_summary"].get("balance_assessment", "N/A")}
**Domains Assessed:** {len(report["domain_analyses"])}

"""

            if overall_balance:
                md_report += f"""Your current life balance is {round(overall_balance, 1)} out of 10. {"This indicates good overall balance across domains." if overall_balance >= 7 else "Some areas may need focused attention to achieve better balance."}

---

"""

            # Domain-by-domain analysis
            md_report += "## Domain Analysis\n\n"

            for domain_key, analysis in report["domain_analyses"].items():
                score = analysis.get("score", "N/A")
                md_report += f"### {analysis['name']} (Score: {score}/10)\n\n"

                if analysis.get("strengths"):
                    md_report += "**Strengths:**\n"
                    for strength in analysis["strengths"]:
                        md_report += f"- {strength}\n"
                    md_report += "\n"

                if analysis.get("challenges"):
                    md_report += "**Areas for Improvement:**\n"
                    for challenge in analysis["challenges"]:
                        md_report += f"- {challenge}\n"
                    md_report += "\n"

                if analysis.get("key_insights"):
                    md_report += "**Key Insights:**\n"
                    for insight in analysis["key_insights"]:
                        md_report += f"- {insight}\n"
                    md_report += "\n"

                md_report += "---\n\n"

            # Prioritized action plan
            if report["prioritized_action_plan"]:
                md_report += "## Prioritized Action Plan\n\n"
                md_report += (
                    f"Based on your assessment data, here are the recommended focus areas:\n\n"
                )

                for i, item in enumerate(report["prioritized_action_plan"], 1):
                    md_report += f"### Priority {i}: {item['domain']}\n\n"
                    md_report += f"**Current Score:** {item.get('current_score', 'N/A')}/10\n"
                    md_report += f"**Priority Score:** {item.get('priority_score', 'N/A')}/10\n\n"

                    if item.get("focus_areas"):
                        md_report += "**Focus Areas:**\n"
                        for area in item["focus_areas"]:
                            md_report += f"- {area}\n"
                        md_report += "\n"

                    if item.get("recommended_actions"):
                        md_report += "**Recommended Actions:**\n"
                        for action in item["recommended_actions"]:
                            md_report += f"1. {action}\n"
                        md_report += "\n"

                    md_report += "---\n\n"

            # Cross-domain insights
            if cross_domain_analysis:
                md_report += "## Cross-Domain Insights\n\n"
                if isinstance(cross_domain_analysis, dict):
                    for key, value in cross_domain_analysis.items():
                        md_report += f"**{key.replace('_', ' ').title()}:**\n"
                        if isinstance(value, list):
                            for item in value:
                                md_report += f"- {item}\n"
                        else:
                            md_report += f"{value}\n"
                        md_report += "\n"

            # Conclusion
            md_report += """---

## Next Steps

1. Review this report and identify which priorities resonate most
2. Choose 1-2 high-priority items to focus on first
3. Schedule regular check-ins (recommended: weekly initially)
4. Reassess domains periodically (recommended: monthly)

Remember that improvement is a journey, not a race. Focus on progress over perfection.

---

*Report saved to: assessments/{user_id}/reports/{today}_integrated_assessment.json*
"""

            # Save Markdown report
            md_path = path.replace(".json", ".md")
            if hasattr(backend, "write_file"):
                backend.write_file(md_path, md_report)
            else:
                file_path = workspace_path / md_path
                file_path.write_text(md_report)

            # Format user-friendly summary response
            return f"""Integrated Assessment Report Generated

User ID: {user_id}
Date: {today.strftime("%Y-%m-%d")}

Report Summary:
- Overall Balance Score: {report["executive_summary"]["overall_balance_score"]}/10
- Domains Assessed: {len(report["domain_analyses"])}
- Priority Actions Identified: {len(report["prioritized_action_plan"])}

Report Components:
1. Executive Summary with overall balance assessment
2. Detailed analysis for each assessed domain
3. Prioritized action plan with recommended steps
4. Cross-domain insights and connections

Files Created:
- JSON Report: {path}
- Markdown Report: {md_path}

Next Steps:
1. Review the complete report in the markdown file
2. Identify 1-2 top priorities to focus on first
3. Use the recommended actions as starting points
4. Schedule follow-up assessments to track progress
"""

        except Exception as e:
            return f"Error generating integrated report: {str(e)}"

    @tool
    def design_follow_up_questions(
        user_id: str,
        assessment_gaps: Dict[str, List[str]],
        domain_scores: Optional[Dict[str, float]] = None,
    ) -> str:
        """Generate targeted follow-up questions to fill assessment gaps.

        This tool analyzes incomplete or unclear areas from assessments and creates
        specific follow-up questions to gather more detailed information. Questions
        are organized by domain and priority level.

        Args:
            user_id: The user's unique identifier
            assessment_gaps: Dictionary mapping domains to areas needing more info
                            e.g., {"wellness": ["sleep habits", "stress triggers"]}
            domain_scores: Optional current domain scores to guide question complexity

        Returns:
            Structured follow-up questions organized by domain and priority.
            Saved to assessments/{user_id}/

        Raises:
            ValueError: If required parameters are invalid

        Example:
            >>> design_follow_up_questions(
            ...     "user_123",
            ...     {"wellness": ["sleep quality", "stress sources"]}
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not assessment_gaps or not isinstance(assessment_gaps, dict):
            return "Error: assessment_gaps must be a non-empty dictionary"

        try:
            # Initialize follow-up questions structure
            follow_up_plan = {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "identified_gaps": assessment_gaps,
                "domain_scores": domain_scores or {},
                "follow_up_questions": {},
            }

            # Domain-specific question templates
            domain_question_templates = {
                "career": {
                    "general": [
                        "What aspects of your current role do you find most fulfilling?",
                        "What are the main challenges you're facing in your career right now?",
                    ],
                    "skill_gap": [
                        "What specific skills do you feel are missing for your next career step?",
                        "Have you identified any resources or opportunities to develop these skills?",
                    ],
                    "satisfaction": [
                        "On a scale of 1-10, how satisfied are you with your current work-life balance?",
                        "What would need to change for you to rate your job satisfaction higher?",
                    ],
                },
                "wellness": {
                    "general": [
                        "How would you describe your current energy levels throughout the day?",
                        "What does a typical day of self-care look like for you?",
                    ],
                    "sleep": [
                        "What time do you typically go to bed and wake up?",
                        "Do you feel rested when you wake up, or do you often need more sleep?",
                    ],
                    "stress": [
                        "What are your main sources of stress right now?",
                        "What coping mechanisms or strategies have you tried for managing stress?",
                    ],
                },
                "finance": {
                    "general": [
                        "How comfortable are you with your current financial situation?",
                        "What financial goals are most important to you right now?",
                    ],
                    "budgeting": [
                        "Do you currently track your expenses or follow a budget?",
                        "What are your largest monthly expense categories?",
                    ],
                    "savings": [
                        "Do you have an emergency fund? If so, how many months of expenses does it cover?",
                        "What's currently preventing you from saving more (if applicable)?",
                    ],
                },
                "relationship": {
                    "general": [
                        "How satisfied are you with the quality of your relationships overall?",
                        "What do you value most in your close relationships?",
                    ],
                    "communication": [
                        "How would you describe your communication style in conflicts or disagreements?",
                        "Are there any recurring patterns in your relationships you'd like to change?",
                    ],
                    "support": [
                        "Who do you turn to when you need emotional support?",
                        "Do you feel you have enough people in your life who understand and support you?",
                    ],
                },
            }

            # Generate follow-up questions for each domain with gaps
            for domain_key, gaps in assessment_gaps.items():
                if domain_key not in LIFE_DOMAINS:
                    continue

                questions = {}

                # Map gap keywords to question templates
                for gap in gaps:
                    gap_lower = gap.lower()

                    if domain_key == "career":
                        if any(kw in gap_lower for kw in ["skill", "ability"]):
                            questions["skills"] = domain_question_templates["career"]["skill_gap"]
                        elif any(kw in gap_lower for kw in ["satisfy", "happy"]):
                            questions["satisfaction"] = domain_question_templates["career"][
                                "satisfaction"
                            ]
                        else:
                            questions["general"] = domain_question_templates["career"]["general"]

                    elif domain_key == "wellness":
                        if any(kw in gap_lower for kw in ["sleep", "rest"]):
                            questions["sleep_habits"] = domain_question_templates["wellness"][
                                "sleep"
                            ]
                        elif any(kw in gap_lower for kw in ["stress", "pressure"]):
                            questions["stress_management"] = domain_question_templates["wellness"][
                                "stress"
                            ]
                        else:
                            questions["general_wellness"] = domain_question_templates["wellness"][
                                "general"
                            ]

                    elif domain_key == "finance":
                        if any(kw in gap_lower for kw in ["budget", "spend", "expense"]):
                            questions["budgeting"] = domain_question_templates["finance"][
                                "budgeting"
                            ]
                        elif any(kw in gap_lower for kw in ["save", "emergency"]):
                            questions["savings"] = domain_question_templates["finance"]["savings"]
                        else:
                            questions["general_finance"] = domain_question_templates["finance"][
                                "general"
                            ]

                    elif domain_key == "relationship":
                        if any(kw in gap_lower for kw in ["communicate", "talk"]):
                            questions["communication"] = domain_question_templates["relationship"][
                                "communication"
                            ]
                        elif any(kw in gap_lower for kw in ["support", "help"]):
                            questions["support_network"] = domain_question_templates[
                                "relationship"
                            ]["support"]
                        else:
                            questions["general_relationships"] = domain_question_templates[
                                "relationship"
                            ]["general"]

                follow_up_plan["follow_up_questions"][domain_key] = {
                    "domain_name": LIFE_DOMAINS[domain_key]["name"],
                    "identified_gaps": gaps,
                    "questions_by_category": questions,
                }

            # Save follow-up plan
            json_content = json.dumps(follow_up_plan, indent=2)
            today = date.today()
            path = f"assessments/{user_id}/{today}_follow_up_questions.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            response_parts = [
                "Follow-Up Questions Plan",
                "=" * 60,
                f"\nUser ID: {user_id}",
                f"Date: {today.strftime('%Y-%m-%d')}",
            ]

            for domain_key, question_data in follow_up_plan["follow_up_questions"].items():
                response_parts.append(f"\n{question_data['domain_name']}")
                response_parts.append("-" * 60)
                response_parts.append(
                    f"Gaps Identified: {', '.join(question_data['identified_gaps'])}"
                )

                for category, questions in question_data["questions_by_category"].items():
                    response_parts.append(f"\n{category.replace('_', ' ').title()}:")
                    for i, question in enumerate(questions, 1):
                        response_parts.append(f"  {i}. {question}")

            response_parts.append("\n\nUsage Guide:")
            response_parts.append(
                "1. Use these questions to gather more detail in identified gap areas"
            )
            response_parts.append(
                "2. Ask 2-3 high-priority questions per session to avoid overwhelming"
            )
            response_parts.append("3. Document user responses and update assessments accordingly")
            response_parts.append("4. Re-prioritize based on new information gathered")

            response_parts.append(f"\nFollow-up plan saved to: {path}")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error designing follow-up questions: {str(e)}"

    print("Assessment tools created successfully!")
    return (
        conduct_initial_assessment,
        prioritize_domains_by_urgency,
        assess_cross_domain_impacts,
        generate_integrated_report,
        design_follow_up_questions,
    )


# Export tools at module level for convenience
__all__ = [
    "create_assessment_tools",
]
