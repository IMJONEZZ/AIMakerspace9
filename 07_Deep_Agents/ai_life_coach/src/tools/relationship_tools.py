"""
Relationship Coach tools for AI Life Coach.

This module provides LangChain tools specialized for relationship coaching.
All tools use the @tool decorator and follow best practices for validation,
error handling, and user-friendly output.

Tools:
- analyze_communication_style: Assess communication patterns (passive/aggressive/assertive)
- create_boundary_setting_plan: Generate personalized boundary-setting strategies
- apply_dear_man_technique: Guide users through DEAR MAN conflict resolution
- assess_relationship_quality: Evaluate relationship health across key dimensions
- develop_social_connection_plan: Build strategies for strengthening relationships

Based on evidence-based relationship coaching frameworks:
- DEAR MAN (Dialectical Behavior Therapy - DBT)
- Nonviolent Communication (NVC) frameworks
- Boundary setting best practices from positive psychology
- Attachment theory-informed approaches
"""

from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, List, Optional
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
# Relationship Tool Factory
# ==============================================================================


def create_relationship_tools(backend=None) -> tuple:
    """
    Create relationship tools with shared FilesystemBackend instance.

    These tools enable the Relationship Specialist to:
    - Analyze communication styles and patterns
    - Create personalized boundary-setting strategies
    - Apply DEAR MAN technique for conflict resolution
    - Assess relationship quality across dimensions
    - Develop social connection building strategies

    Args:
        backend: Optional FilesystemBackend instance. If None, uses get_backend()

    Returns:
        Tuple of relationship tools (analyze_communication_style,
                                     create_boundary_setting_plan,
                                     apply_dear_man_technique,
                                     assess_relationship_quality,
                                     develop_social_connection_plan)

    Example:
        >>> from src.config import config
        >>> config.initialize_environment()
        >>> tools = create_relationship_tools()
        >>> result = analyze_communication_style(
        ...     user_id="user_123",
        ...     scenario_description="I often avoid expressing my needs to others..."
        ... )
    """
    if backend is None:
        backend = get_backend()

    # Get the workspace directory path from backend
    workspace_path = Path(backend.root_dir) if hasattr(backend, "root_dir") else Path("workspace")

    @tool
    def analyze_communication_style(
        user_id: str, scenario_descriptions: List[str], relationship_context: Optional[str] = None
    ) -> str:
        """Analyze communication style patterns based on provided scenarios.

        This tool assesses communication tendencies across four main styles:
        - Passive: Avoids conflict, suppresses needs, trouble saying "no"
        - Aggressive: Overly direct, insensitive to others' feelings
        - Passive-Aggressive: Indirect expression of negative feelings, sarcasm
        - Assertive: Direct, honest communication while respecting others

        Args:
            user_id: The user's unique identifier
            scenario_descriptions: List of 3-5 real-life communication scenarios
                                  or situations the user has experienced
            relationship_context: Optional context (e.g., "workplace", "romantic",
                                  "family", "friendship")

        Returns:
            Structured communication style analysis with dominant patterns,
            strengths, areas for improvement, and actionable recommendations.
            Saved to relationship_assessments/{user_id}/

        Raises:
            ValueError: If user_id or scenario_descriptions are invalid

        Example:
            >>> analyze_communication_style(
            ...     "user_123",
            ...     ["I often say 'yes' when I want to say 'no'",
            ...      "When people criticize me, I shut down",
            ...      "I rarely express my true feelings to others"]
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not scenario_descriptions or not isinstance(scenario_descriptions, list):
            return "Error: scenario_descriptions must be a non-empty list"
        if len(scenario_descriptions) < 2:
            return "Error: Please provide at least 2-3 scenarios for accurate analysis"

        try:
            # Communication style indicators (knowledge base)
            passive_indicators = [
                "avoid",
                "shut down",
                "don't say",
                "hesitate",
                "fear",
                "keep quiet",
                "withhold",
                "suppress",
                "agree when disagree",
                "hard to say no",
                "stay silent",
            ]

            aggressive_indicators = [
                "demand",
                "attack",
                "interrupt",
                "force",
                "blame",
                "yell",
                "dominate",
                "(too) direct",
                "insensitive",
                "always right",
                "win arguments",
            ]

            passive_aggressive_indicators = [
                "sarcasm",
                "silent treatment",
                "indirectly",
                "behind back",
                "subtle",
                "hint instead of say",
                "resent",
                "sabotage",
            ]

            assertive_indicators = [
                "express clearly",
                "respect others",
                "honest but kind",
                "say no nicely",
                "compromise",
                "listen actively",
                "assert my needs",
                "find win-win",
            ]

            # Analyze each scenario
            scores = {"passive": 0, "aggressive": 0, "passive_aggressive": 0, "assertive": 0}

            scenario_analysis = []

            for i, scenario in enumerate(scenario_descriptions):
                scenario_lower = scenario.lower()
                scenario_score = {
                    "passive": 0,
                    "aggressive": 0,
                    "passive_aggressive": 0,
                    "assertive": 0,
                }

                # Count indicators in each scenario
                for indicator in passive_indicators:
                    if indicator in scenario_lower:
                        scores["passive"] += 1
                        scenario_score["passive"] += 1

                for indicator in aggressive_indicators:
                    if indicator in scenario_lower:
                        scores["aggressive"] += 1
                        scenario_score["aggressive"] += 1

                for indicator in passive_aggressive_indicators:
                    if indicator in scenario_lower:
                        scores["passive_aggressive"] += 1
                        scenario_score["passive_aggressive"] += 1

                for indicator in assertive_indicators:
                    if indicator in scenario_lower:
                        scores["assertive"] += 1
                        scenario_score["assertive"] += 1

                # Determine dominant style for this scenario
                max_style = max(scenario_score, key=scenario_score.get)
                if scenario_score[max_style] > 0:
                    scenario_analysis.append(
                        {
                            "scenario": scenario[:100] + "..." if len(scenario) > 100 else scenario,
                            "dominant_style": max_style,
                        }
                    )
                else:
                    scenario_analysis.append(
                        {
                            "scenario": scenario[:100] + "..." if len(scenario) > 100 else scenario,
                            "dominant_style": "unclear",
                        }
                    )

            # Determine overall dominant style
            total_score = sum(scores.values())
            if total_score == 0:
                # No clear indicators - provide general assessment
                dominant_style = "unclear_from_scenarios"
            else:
                dominant_style = max(scores, key=scores.get)

            # Generate recommendations based on dominant style
            if dominant_style == "passive":
                strengths = ["Cares about others' feelings", "Avoids unnecessary conflict"]
                improvements = [
                    "Practice saying 'no' when needed",
                    "Express your needs more directly",
                    "Recognize that conflict can be healthy",
                ]
            elif dominant_style == "aggressive":
                strengths = ["Clear about what you want", "Takes initiative"]
                improvements = [
                    "Practice active listening",
                    "Consider others' perspectives before speaking",
                    "Use 'I' statements instead of blaming",
                ]
            elif dominant_style == "passive_aggressive":
                strengths = ["Aware of feelings", "Wants to express needs"]
                improvements = [
                    "Be direct instead of using hints",
                    "Address issues when they occur",
                    "Use clear, respectful language",
                ]
            elif dominant_style == "assertive":
                strengths = ["Balances own needs with others'", "Communicates clearly"]
                improvements = [
                    "Continue practicing active listening",
                    "Stay aware of power dynamics in different contexts",
                ]
            else:
                strengths = ["Reflecting on communication patterns"]
                improvements = [
                    "Continue observing your patterns",
                    "Practice expressing needs directly",
                ]

            # Create analysis object
            analysis = {
                "user_id": user_id,
                "relationship_context": relationship_context or "general",
                "timestamp": datetime.now().isoformat(),
                "scenarios_analyzed": len(scenario_descriptions),
                "style_scores": scores,
                "dominant_style": dominant_style,
                "scenario_analysis": scenario_analysis,
                "strengths": strengths,
                "areas_for_improvement": improvements,
            }

            # Save to file
            json_content = json.dumps(analysis, indent=2)
            today = date.today()
            path = f"relationship_assessments/{user_id}/{today}_communication_style.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            response_parts = [
                f"Communication Style Analysis",
                "=" * 60,
                f"\nContext: {relationship_context or 'General relationships'}",
                f"Scenarios analyzed: {len(scenario_descriptions)}",
            ]

            response_parts.append(f"\nStyle Breakdown:")
            for style, score in scores.items():
                percentage = (score / total_score * 100) if total_score > 0 else 0
                response_parts.append(
                    f"  - {style.replace('_', '-').title()}: {score} ({percentage:.0f}%)"
                )

            if total_score > 0:
                dominant_pct = scores[dominant_style] / total_score * 100
                response_parts.append(
                    f"\nDominant Style: {dominant_style.replace('_', '-').title()} ({dominant_pct:.0f}%)"
                )

            response_parts.append("\nStrengths:")
            for strength in strengths:
                response_parts.append(f"  ✓ {strength}")

            response_parts.append("\nAreas for Improvement:")
            for improvement in improvements:
                response_parts.append(f"  → {improvement}")

            response_parts.append(f"\nAnalysis saved to: {path}")
            response_parts.append("\nNext Steps:")
            response_parts.append("  1. Choose one area for improvement this week")
            response_parts.append("  2. Practice the suggested technique in low-stakes situations")
            response_parts.append("  3. Reflect on how it felt and what you learned")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error analyzing communication style: {str(e)}"

    @tool
    def create_boundary_setting_plan(
        user_id: str, boundary_areas: List[str], relationship_type: Optional[str] = None
    ) -> str:
        """Create a personalized boundary-setting action plan.

        This tool generates specific, actionable boundary-setting strategies
        customized to the user's identified areas of concern. The plan includes:
        - Clear boundary statements for each area
        - Specific language/scripts to use
        - Consequences for when boundaries are violated
        - Practice exercises and implementation steps

        Args:
            user_id: The user's unique identifier
            boundary_areas: List of areas where boundaries need to be set
                           (e.g., ["work hours", "personal space", "emotional energy",
                                   "time with friends", "social media"])
            relationship_type: Optional type of relationship context
                              (e.g., "workplace", "romantic", "family", "friendship")

        Returns:
            Structured boundary-setting plan with specific scripts and strategies.
            Saved to relationship_guidance/{user_id}/

        Raises:
            ValueError: If user_id or boundary_areas are invalid

        Example:
            >>> create_boundary_setting_plan(
            ...     "user_123",
            ...     ["work hours", "emotional energy"],
            ...     "workplace"
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not boundary_areas or not isinstance(boundary_areas, list):
            return "Error: boundary_areas must be a non-empty list"

        try:
            # Boundary templates (knowledge base)
            boundary_templates = {
                "work hours": {
                    "boundary_statement": "I need to maintain specific work hours for my wellbeing.",
                    "specific_script": "I'm available for work-related matters between [start time] and [end time]. I'll respond to non-urgent messages outside those hours the next business day.",
                    "consequences": "If you repeatedly contact me outside work hours, I may not respond immediately. For emergencies, please call rather than text.",
                    "practice": "Practice saying this to one colleague this week. Set your phone's 'Do Not Disturb' during personal time.",
                },
                "personal space": {
                    "boundary_statement": "My home/room is my private space where I need quiet and privacy.",
                    "specific_script": "I need some alone time in my space right now. Let's connect later at [specific time].",
                    "consequences": "If you enter my space without permission, I'll ask you to leave. This isn't about you - it's what I need to recharge.",
                    "practice": "Put a small sign on your door when you need privacy. Practice the script with someone you trust.",
                },
                "emotional energy": {
                    "boundary_statement": "I can only take in so much emotional content at once.",
                    "specific_script": "I care about you, but I don't have the capacity to support this conversation right now. Can we talk about something lighter or revisit this tomorrow?",
                    "consequences": "If the conversation continues when I've expressed a limit, I'll step away. This helps me show up fully for you another time.",
                    "practice": "Notice your emotional battery level (1-10). Set a rule to step away when it drops below 3.",
                },
                "time with friends": {
                    "boundary_statement": "I value our friendship AND I need balance in my life.",
                    "specific_script": "I'd love to connect! This week I'm free on [day], but I need to keep other evenings for self-care. Would that work?",
                    "consequences": "If plans get cancelled repeatedly last minute, I may need to prioritize other commitments going forward.",
                    "practice": "Schedule specific friend time in your calendar. Protect that time like you would a work appointment.",
                },
                "social media": {
                    "boundary_statement": "I need to limit social media for my mental health.",
                    "specific_script": "I'm taking a break from social media right now. If you need to reach me, please text or call instead.",
                    "consequences": "I won't be responding to messages on social platforms during this time. Important matters: contact me directly.",
                    "practice": "Set app limits on your phone. Remove apps from your home screen for one week.",
                },
                "family expectations": {
                    "boundary_statement": "I love my family AND I need to make decisions that work for me.",
                    "specific_script": "I appreciate your input, but I need to make this decision based on what feels right for me.",
                    "consequences": "If boundaries continue to be pushed, I may need to create more space between us temporarily.",
                    "practice": "Practice saying this in the mirror first. Start with smaller, lower-stakes boundaries.",
                },
            }

            # Generate boundary plans for each area
            boundary_plans = []

            for area in boundary_areas:
                area_lower = area.lower()
                # Find matching template or use generic
                matched_template = None
                for key, template in boundary_templates.items():
                    if key in area_lower or area_lower in key:
                        matched_template = template
                        break

                if matched_template is None:
                    # Generic template for custom areas
                    matched_template = {
                        "boundary_statement": f"I need to protect my {area} for my wellbeing.",
                        "specific_script": f"Regarding {area}, I need to set a limit. Specifically: [fill in your specific boundary].",
                        "consequences": f"If this boundary isn't respected, I'll [fill in consequence].",
                        "practice": f"Practice saying this script out loud at least 3 times before using it in real situations.",
                    }

                boundary_plans.append({"area": area, **matched_template})

            # Create comprehensive plan
            plan = {
                "user_id": user_id,
                "relationship_type": relationship_type or "general",
                "timestamp": datetime.now().isoformat(),
                "boundary_areas": boundary_areas,
                "plans": boundary_plans,
            }

            # Save to file
            json_content = json.dumps(plan, indent=2)
            today = date.today()
            path = f"relationship_guidance/{user_id}/{today}_boundary_setting_plan.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            response_parts = [
                f"Boundary Setting Plan",
                "=" * 60,
                f"\nRelationship Context: {relationship_type or 'General'}",
                f"Areas to address: {', '.join(boundary_areas)}",
            ]

            for i, plan_item in enumerate(boundary_plans, 1):
                response_parts.append(f"\n{'─' * 60}")
                response_parts.append(f"{i}. {plan_item['area'].title()}")
                response_parts.append(f"{'─' * 60}")
                response_parts.append(f"\nBoundary Statement:")
                response_parts.append(f"  {plan_item['boundary_statement']}")
                response_parts.append(f"\nWhat to Say (Script):")
                response_parts.append(f'  "{plan_item["specific_script"]}"')
                response_parts.append(f"\nConsequences if Violated:")
                response_parts.append(f"  {plan_item['consequences']}")
                response_parts.append(f"\nPractice Exercise:")
                response_parts.append(f"  {plan_item['practice']}")

            # Add general tips
            response_parts.append(f"\n{'─' * 60}")
            response_parts.append("\nGeneral Boundary-Setting Tips:")
            response_parts.append("  1. Start with smaller boundaries before tackling bigger ones")
            response_parts.append("  2. Practice your scripts out loud - it builds confidence")
            response_parts.append("  3. Expect some resistance initially; stay consistent")
            response_parts.append("  4. Boundaries protect both you AND the relationship")
            response_parts.append("  5. Revisit and adjust boundaries as circumstances change")

            response_parts.append(f"\nPlan saved to: {path}")
            response_parts.append("\nNext Steps:")
            response_parts.append("  1. Choose ONE boundary to practice this week")
            response_parts.append("  2. Write your script and practice it aloud daily")
            response_parts.append("  3. Schedule a time to communicate this boundary")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error creating boundary setting plan: {str(e)}"

    @tool
    def apply_dear_man_technique(
        user_id: str, situation_description: str, goal: Optional[str] = None
    ) -> str:
        """Apply the DEAR MAN technique for effective communication and conflict resolution.

        The DEAR MAN technique (from Dialectical Behavior Therapy) is a powerful
        framework for assertive communication that helps you:
        - Express your needs clearly and respectfully
        - Handle conflicts without escalating
        - Maintain relationships while standing up for yourself

        DEAR MAN stands for:
        D - Describe the situation objectively
        E - Express your feelings using "I" statements
        A - Assert your request clearly and specifically
        R - Reinforce the positive outcome for both parties
        M - Stay Mindful (don't get distracted or defensive)
        A - Appear confident (body language matters)
        N - Negotiate if needed, find win-win solutions

        Args:
            user_id: The user's unique identifier
            situation_description: Detailed description of the situation or conflict
                                  (e.g., "My coworker keeps interrupting me in meetings")
            goal: Optional specific goal (e.g., "To speak without being interrupted")

        Returns:
            Structured DEAR MAN script tailored to the situation with specific
            wording and practice steps. Saved to relationship_guidance/{user_id}/

        Raises:
            ValueError: If user_id or situation_description are invalid

        Example:
            >>> apply_dear_man_technique(
            ...     "user_123",
            ...     "My partner always checks my phone without asking"
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not situation_description or not isinstance(situation_description, str):
            return "Error: situation_description must be a non-empty string"

        try:
            # Generate DEAR MAN script based on the situation
            dear_man_script = {
                "user_id": user_id,
                "situation_description": situation_description,
                "goal": goal or "To address this issue respectfully and effectively",
                "timestamp": datetime.now().isoformat(),
                "dear_man_breakdown": {
                    "describe": {
                        "purpose": "State the facts objectively, without judgment",
                        "script_template": f"When I notice that [situation], it affects me.",
                        "example_script": f"When you {self._extract_action(situation_description)}, I notice [specific impact].",
                    },
                    "express": {
                        "purpose": "Share your feelings using 'I' statements",
                        "script_template": "I feel [emotion] when this happens.",
                        "example_script": "I feel frustrated/hurt/concerned because...",
                    },
                    "assert": {
                        "purpose": "Clearly state what you want or need",
                        "script_template": "I would like [specific request].",
                        "example_script": "I'd like to ask that you [clear, specific action].",
                    },
                    "reinforce": {
                        "purpose": "Explain the positive outcome of your request",
                        "script_template": "This would help us both by [benefit].",
                        "example_script": "This will improve our relationship because...",
                    },
                },
                "mindful_appear_confident_negotiate": {
                    "mindful": {
                        "purpose": "Stay focused on your goal, don't get distracted",
                        "tips": [
                            "Use the 'broken record' technique if needed (repeat your request calmly)",
                            "Ignore distractions or attempts to change the subject",
                            "Stay calm and breathe",
                        ],
                    },
                    "appear_confident": {
                        "purpose": "Your body language communicates as much as your words",
                        "tips": [
                            "Make eye contact",
                            "Use a steady voice (not too loud or soft)",
                            "Stand/sit confidently with open posture",
                            "Avoid apologizing for having needs",
                        ],
                    },
                    "negotiate": {
                        "purpose": "Be willing to find a compromise that works for both",
                        "tips": [
                            "Ask 'What would work for you?'",
                            "Offer alternatives if needed",
                            "Focus on win-win solutions",
                        ],
                    },
                },
                "full_script": f"""When you [specific behavior from situation], I feel [emotion] because [impact].

I would like [clear request].

This will help us both by [positive outcome].""",
            }

            # Save to file
            json_content = json.dumps(dear_man_script, indent=2)
            today = date.today()
            path = f"relationship_guidance/{user_id}/{today}_dear_man_script.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            response_parts = [
                f"DEAR MAN Technique Applied",
                "=" * 60,
                f"\nSituation: {situation_description}",
                f"Goal: {dear_man_script['goal']}",
            ]

            response_parts.append("\n【 D - DESCRIBE 】")
            response_parts.append(
                f"  Purpose: {dear_man_script['dear_man_breakdown']['describe']['purpose']}"
            )
            response_parts.append(
                f"  What to say: {dear_man_script['dear_man_breakdown']['describe']['example_script']}"
            )

            response_parts.append("\n【 E - EXPRESS 】")
            response_parts.append(
                f"  Purpose: {dear_man_script['dear_man_breakdown']['express']['purpose']}"
            )
            response_parts.append(
                f"  What to say: {dear_man_script['dear_man_breakdown']['express']['example_script']}"
            )

            response_parts.append("\n【 A - ASSERT 】")
            response_parts.append(
                f"  Purpose: {dear_man_script['dear_man_breakdown']['assert']['purpose']}"
            )
            response_parts.append(
                f"  What to say: {dear_man_script['dear_man_breakdown']['assert']['example_script']}"
            )

            response_parts.append("\n【 R - REINFORCE 】")
            response_parts.append(
                f"  Purpose: {dear_man_script['dear_man_breakdown']['reinforce']['purpose']}"
            )
            response_parts.append(
                f"  What to say: {dear_man_script['dear_man_breakdown']['reinforce']['example_script']}"
            )

            response_parts.append("\n【 M - MINDFUL 】")
            response_parts.append(
                f"  Purpose: {dear_man_script['mindful_appear_confident_negotiate']['mindful']['purpose']}"
            )
            for tip in dear_man_script["mindful_appear_confident_negotiate"]["mindful"]["tips"]:
                response_parts.append(f"  • {tip}")

            response_parts.append("\n【 A - APPEAR CONFIDENT 】")
            response_parts.append(
                f"  Purpose: {dear_man_script['mindful_appear_confident_negotiate']['appear_confident']['purpose']}"
            )
            for tip in dear_man_script["mindful_appear_confident_negotiate"]["appear_confident"][
                "tips"
            ]:
                response_parts.append(f"  • {tip}")

            response_parts.append("\n【 N - NEGOTIATE 】")
            response_parts.append(
                f"  Purpose: {dear_man_script['mindful_appear_confident_negotiate']['negotiate']['purpose']}"
            )
            for tip in dear_man_script["mindful_appear_confident_negotiate"]["negotiate"]["tips"]:
                response_parts.append(f"  • {tip}")

            response_parts.append("\n" + "─" * 60)
            response_parts.append("\nPractice This Script:")
            response_parts.append("  1. Fill in the bracketed sections with your specific details")
            response_parts.append("  2. Practice saying it aloud at least 5 times")
            response_parts.append("  3. Choose a calm moment to have the conversation")
            response_parts.append("  4. Stay mindful - don't get sidetracked")

            response_parts.append(f"\nScript saved to: {path}")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error applying DEAR MAN technique: {str(e)}"

    def _extract_action(self, description):
        """Helper to extract action from situation description."""
        # This is a simple placeholder - in a full implementation,
        # could use NLP to better extract actions
        words = description.split()[:5]  # Take first 5 words as approximation
        return " ".join(words)

    @tool
    def assess_relationship_quality(
        user_id: str, relationship_type: str, ratings: Dict[str, int]
    ) -> str:
        """Assess relationship quality across key dimensions.

        This tool evaluates relationship health using evidence-based metrics:
        - Trust: Feeling safe, reliable, and honest in the relationship
        - Communication: Quality of dialogue, listening, and expression
        - Support: Emotional support during difficult times
        - Growth: Ability to grow together, learn from each other
        - Intimacy/Connection: Feeling emotionally close and understood
        - Conflict Resolution: How well conflicts are handled

        Args:
            user_id: The user's unique identifier
            relationship_type: Type of relationship (e.g., "romantic", "friendship",
                              "family", "workplace")
            ratings: Dictionary of dimension ratings (1-10 scale):
                     {"trust": 7, "communication": 5, "support": 8, "growth": 6,
                      "intimacy": 4, "conflict_resolution": 3}

        Returns:
            Structured relationship quality assessment with scores,
            strengths, areas for improvement, and recommendations.
            Saved to relationship_assessments/{user_id}/

        Raises:
            ValueError: If user_id, relationship_type, or ratings are invalid

        Example:
            >>> assess_relationship_quality(
            ...     "user_123",
            ...     "romantic",
            ...     {"trust": 7, "communication": 5, "support": 8}
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not relationship_type or not isinstance(relationship_type, str):
            return "Error: relationship_type must be a non-empty string"
        if not ratings or not isinstance(ratings, dict):
            return "Error: ratings must be a non-empty dictionary"

        # Validate rating values
        for key, value in ratings.items():
            if not isinstance(value, int) or value < 1 or value > 10:
                return f"Error: Rating for '{key}' must be an integer between 1 and 10"

        try:
            # Define dimensions with descriptions
            dimension_descriptions = {
                "trust": "Feeling safe, reliable, and honest",
                "communication": "Quality of dialogue, listening, expression",
                "support": "Emotional support during difficult times",
                "growth": "Ability to grow together, learn from each other",
                "intimacy": "Feeling emotionally close and understood",
                "conflict_resolution": "How well conflicts are handled",
            }

            # Calculate scores
            total_score = sum(ratings.values())
            num_dimensions = len(ratings)
            average_score = total_score / num_dimensions if num_dimensions > 0 else 0

            # Categorize overall quality
            if average_score >= 8:
                overall_category = "Thriving"
            elif average_score >= 6:
                overall_category = "Healthy with room for growth"
            elif average_score >= 4:
                overall_category = "Needs attention and improvement"
            else:
                overall_category = "Significant challenges - consider professional support"

            # Identify strengths (rated 7+) and areas for improvement (rated 5 or below)
            strengths = [dim for dim, score in ratings.items() if score >= 7]
            improvements = [dim for dim, score in ratings.items() if score <= 5]

            # Generate recommendations
            recommendations = []

            if "communication" in improvements:
                recommendations.append(
                    "Practice active listening techniques (reflect back what you hear)"
                )

            if "trust" in improvements:
                recommendations.append(
                    "Have honest conversations about expectations and boundaries"
                )

            if "conflict_resolution" in improvements:
                recommendations.append(
                    "Learn and practice the DEAR MAN technique for difficult conversations"
                )

            if "intimacy" in improvements:
                recommendations.append("Schedule quality time together without distractions")

            if not recommendations:
                recommendations.append("Continue nurturing what's working well!")

            # Create assessment object
            assessment = {
                "user_id": user_id,
                "relationship_type": relationship_type,
                "timestamp": datetime.now().isoformat(),
                "ratings": ratings,
                "total_score": total_score,
                "average_score": round(average_score, 1),
                "overall_category": overall_category,
                "strengths": strengths,
                "areas_for_improvement": improvements,
                "recommendations": recommendations,
            }

            # Save to file
            json_content = json.dumps(assessment, indent=2)
            today = date.today()
            path = f"relationship_assessments/{user_id}/{today}_relation_quality_{relationship_type.lower()}.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            response_parts = [
                f"Relationship Quality Assessment",
                "=" * 60,
                f"\nRelationship Type: {relationship_type.title()}",
                f"Overall Rating: {assessment['average_score']}/10 - {overall_category}",
            ]

            response_parts.append("\nDimension Scores:")
            for dim, score in ratings.items():
                desc = dimension_descriptions.get(dim, "")
                response_parts.append(f"  • {dim.title()}: {score}/10 ({desc})")

            if strengths:
                response_parts.append("\nStrengths:")
                for strength in strengths:
                    response_parts.append(f"  ✓ {strength.title()}")

            if improvements:
                response_parts.append("\nAreas for Improvement:")
                for improvement in improvements:
                    response_parts.append(f"  → {improvement.title()}")

            response_parts.append("\nRecommendations:")
            for i, rec in enumerate(recommendations, 1):
                response_parts.append(f"  {i}. {rec}")

            # Add context-specific guidance
            if assessment["average_score"] <= 4:
                response_parts.append("\n" + "⚠ " * 10)
                response_parts.append(
                    "\nNote: Low overall scores may indicate significant relationship challenges. "
                    "Consider seeking professional support from a couples therapist or counselor."
                )
                response_parts.append("⚠ " * 10)

            response_parts.append(f"\nAssessment saved to: {path}")
            response_parts.append("\nNext Steps:")
            response_parts.append("  1. Choose ONE dimension to focus on improving")
            response_parts.append("  2. Have an open conversation with the other person about it")
            response_parts.append("  3. Track progress by reassessing in 2-4 weeks")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error assessing relationship quality: {str(e)}"

    @tool
    def develop_social_connection_plan(
        user_id: str, current_situation: str, goals: List[str]
    ) -> str:
        """Develop a social connection building strategy.

        This tool creates personalized strategies for strengthening relationships
        and building meaningful connections. The plan includes:
        - Social skills development exercises
        - Conversation starters and practice scenarios
        - Actionable steps for building new connections
        - Strategies for deepening existing relationships

        Args:
            user_id: The user's unique identifier
            current_situation: Description of current social situation
                              (e.g., "I moved to a new city and don't know anyone",
                               "I spend most of my time at work and feel isolated")
            goals: List of social connection goals
                  (e.g., ["make new friends", "deepen existing friendships",
                          "improve conversation skills"])

        Returns:
            Structured social connection plan with exercises, strategies,
            and action steps. Saved to relationship_guidance/{user_id}/

        Raises:
            ValueError: If user_id, current_situation, or goals are invalid

        Example:
            >>> develop_social_connection_plan(
            ...     "user_123",
            ...     "I work from home and rarely see people",
            ...     ["make new friends", "improve conversation skills"]
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not current_situation or not isinstance(current_situation, str):
            return "Error: current_situation must be a non-empty string"
        if not goals or not isinstance(goals, list):
            return "Error: goals must be a non-empty list"

        try:
            # Social skills and strategies database
            social_strategies = {
                "make new friends": [
                    {
                        "strategy": "Start with shared interests",
                        "action_steps": [
                            "Join a club, class, or group related to an interest you have",
                            "Attend community events regularly (same event at least 3 times)",
                            "Volunteer for causes you care about",
                        ],
                        "conversation_starters": [
                            "How did you get interested in [topic]?",
                            "What's been your favorite part of this event/class so far?",
                            "Do you have any recommendations for [related topic]?",
                        ],
                    },
                    {
                        "strategy": "Practice reaching out",
                        "action_steps": [
                            "Start with low-stakes interactions (cashier, barista, neighbor)",
                            "Set a goal to have one genuine conversation per week",
                            "Follow up - exchange contact info and actually use it",
                        ],
                        "conversation_starters": [
                            "How's your day going?",
                            "I like [something they're wearing/doing], where did you get it?",
                            "Have you been here before? What do you recommend?",
                        ],
                    },
                ],
                "deepen existing friendships": [
                    {
                        "strategy": "Increase quality time",
                        "action_steps": [
                            "Schedule regular one-on-one time with friends",
                            "Try new activities together (creates shared memories)",
                            "Be vulnerable - share something real about yourself",
                        ],
                        "deepening_questions": [
                            "What's been on your mind lately?",
                            "Is there anything you're looking forward to or worried about?",
                            "What do you wish people understood about you?",
                        ],
                    },
                    {
                        "strategy": "Show up consistently",
                        "action_steps": [
                            "Remember important dates and follow up",
                            "Check in regularly, not just when you need something",
                            "Be a good listener - ask follow-up questions",
                        ],
                        "check_in_template": "Hey [name], I was thinking of you and wanted to see how you're doing. How's [specific thing they mentioned] going?",
                    },
                ],
                "improve conversation skills": [
                    {
                        "strategy": "Practice active listening",
                        "action_steps": [
                            "Focus fully on the other person (put phone away)",
                            "Reflect back what you hear: 'So it sounds like you're feeling...'",
                            "Ask open-ended questions starting with 'how' or 'what'",
                        ],
                        "practice_exercise": "In your next 3 conversations, aim to listen twice as much as you speak",
                    },
                    {
                        "strategy": "Learn to share about yourself appropriately",
                        "action_steps": [
                            "Share small personal details gradually",
                            "Match the other person's level of disclosure",
                            "Be honest but appropriate to context",
                        ],
                        "practice_exercise": "Prepare 2-3 'go-to' stories about yourself you feel comfortable sharing",
                    },
                ],
                "overcome social anxiety": [
                    {
                        "strategy": "Start small and build gradually",
                        "action_steps": [
                            "Begin with brief, low-stakes interactions",
                            "Gradually increase social exposure as comfort grows",
                            "Accept discomfort as part of growth, not a sign to stop",
                        ],
                        "mindset_reminders": [
                            "Most people are focused on themselves, not judging you",
                            "Awkward moments happen to everyone and don't define you",
                            "You don't have to be perfect - you just have to show up",
                        ],
                    }
                ],
            }

            # Gather relevant strategies based on goals
            plan_components = []

            for goal in goals:
                goal_lower = goal.lower()
                # Find matching strategies
                matched_strategies = []
                for key, strategies in social_strategies.items():
                    if any(word in goal_lower for word in key.split()):
                        matched_strategies.extend(strategies)

                if not matched_strategies:
                    # Add generic strategy
                    matched_strategies.append(
                        {
                            "strategy": f"Work on {goal}",
                            "action_steps": [
                                f"Identify small, achievable steps related to {goal}",
                                "Set concrete goals with timelines",
                                "Track your progress and celebrate small wins",
                            ],
                        }
                    )

                plan_components.append({"goal": goal, "strategies": matched_strategies})

            # Create comprehensive plan
            plan = {
                "user_id": user_id,
                "current_situation": current_situation,
                "goals": goals,
                "timestamp": datetime.now().isoformat(),
                "plan_components": plan_components,
            }

            # Save to file
            json_content = json.dumps(plan, indent=2)
            today = date.today()
            path = f"relationship_guidance/{user_id}/{today}_social_connection_plan.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            response_parts = [
                f"Social Connection Plan",
                "=" * 60,
                f"\nCurrent Situation: {current_situation}",
                f"Goals: {', '.join(goals)}",
            ]

            for component in plan_components:
                response_parts.append(f"\n{'─' * 60}")
                response_parts.append(f"Goal: {component['goal'].title()}")
                response_parts.append(f"{'─' * 60}")

                for i, strategy in enumerate(component["strategies"], 1):
                    response_parts.append(f"\n{i}. {strategy['strategy']}")
                    if "action_steps" in strategy:
                        response_parts.append("   Action Steps:")
                        for step in strategy["action_steps"]:
                            response_parts.append(f"     • {step}")
                    if "conversation_starters" in strategy:
                        response_parts.append("   Conversation Starters:")
                        for starter in strategy["conversation_starters"]:
                            response_parts.append(f"     - {starter}")
                    if "deepening_questions" in strategy:
                        response_parts.append("   Questions to Deepen Connection:")
                        for question in strategy["deepening_questions"]:
                            response_parts.append(f"     - {question}")
                    if "practice_exercise" in strategy:
                        response_parts.append(
                            f"   Practice Exercise: {strategy['practice_exercise']}"
                        )
                    if "mindset_reminders" in strategy:
                        response_parts.append("   Mindset Reminders:")
                        for reminder in strategy["mindset_reminders"]:
                            response_parts.append(f"     ✓ {reminder}")

            # Add overall guidance
            response_parts.append(f"\n{'─' * 60}")
            response_parts.append("\nBuilding Social Connections: General Tips")
            response_parts.append("  • Start small - consistency beats intensity")
            response_parts.append("  • Focus on quality over quantity of connections")
            response_parts.append("  • Be patient - meaningful relationships take time to build")
            response_parts.append(
                "  • Stay authentic - people connect with realness, not perfection"
            )

            response_parts.append(f"\nPlan saved to: {path}")
            response_parts.append("\nWeekly Action Plan:")
            response_parts.append("  Week 1: Choose ONE strategy and try it once")
            response_parts.append("  Week 2-3: Practice that same strategy regularly")
            response_parts.append("  Week 4: Add a second strategy while maintaining the first")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error developing social connection plan: {str(e)}"

    @tool
    def calculate_relationship_score(
        user_id: str,
        quality_metrics: Dict[str, int],
        relationship_type: Optional[str] = "general",
    ) -> str:
        """Calculate an overall relationship score based on quality metrics.

        This tool computes a weighted relationship health score using multiple
        dimensions and provides insights into relationship dynamics. The score
        helps track progress over time and identify areas for focus.

        Args:
            user_id: The user's unique identifier
            quality_metrics: Dictionary of relationship quality metrics (1-10 scale):
                           {"trust": 7, "communication": 6, "intimacy": 5, ...}
            relationship_type: Optional type of relationship
                               (romantic, friendship, family, workplace)

        Returns:
            Relationship score with breakdown by dimensions, overall health rating,
            and trend analysis suggestions. Saved to relationship_assessments/{user_id}/

        Raises:
            ValueError: If user_id or quality_metrics are invalid

        Example:
            >>> calculate_relationship_score(
            ...     "user_123",
            ...     {"trust": 7, "communication": 6, "support": 8},
            ...     relationship_type="romantic"
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not quality_metrics or not isinstance(quality_metrics, dict):
            return "Error: quality_metrics must be a non-empty dictionary"

        # Validate rating values
        for key, value in quality_metrics.items():
            if not isinstance(value, int) or value < 1 or value > 10:
                return f"Error: Rating for '{key}' must be an integer between 1 and 10"

        try:
            # Define weightings for different dimensions (sum = 100)
            dimension_weights = {
                "trust": 20,
                "communication": 18,
                "support": 15,
                "intimacy": 12,  # emotional closeness
                "growth": 10,
                "conflict_resolution": 15,
                "respect": 10,
            }

            # Calculate weighted score
            total_weight = 0.0
            weighted_sum = 0.0

            for dim, score in quality_metrics.items():
                weight = dimension_weights.get(
                    dim.lower(), 10
                )  # Default weight for custom dimensions
                weighted_sum += score * weight
                total_weight += weight

            # Calculate overall score (0-100)
            overall_score = round(weighted_sum / total_weight, 1) if total_weight > 0 else 0

            # Determine health category
            if overall_score >= 80:
                health_category = "Excellent"
                color_emoji = "🌟"
            elif overall_score >= 65:
                health_category = "Healthy"
                color_emoji = "💚"
            elif overall_score >= 50:
                health_category = "Fair - Room for Improvement"
                color_emoji = "🟡"
            elif overall_score >= 35:
                health_category = "Needs Attention"
                color_emoji = "🟠"
            else:
                health_category = "Critical - Consider Professional Help"
                color_emoji = "🔴"

            # Identify top strengths and areas for improvement
            sorted_dims = sorted(quality_metrics.items(), key=lambda x: x[1], reverse=True)
            top_strengths = [(dim, score) for dim, score in sorted_dims if score >= 7][:3]
            areas_to_improve = [(dim, score) for dim, score in sorted_dims if score <= 5][:3]

            # Generate insights
            insights = []
            if top_strengths:
                best_dim, best_score = top_strengths[0]
                insights.append(
                    f"Your strongest area is {best_dim.title()} ({best_score}/10) - leverage this strength!"
                )
            if areas_to_improve:
                worst_dim, worst_score = areas_to_improve[0]
                insights.append(
                    f"Priority focus area: {worst_dim.title()} ({worst_score}/10) - small improvements here will have big impact"
                )

            # Build score data
            score_data = {
                "user_id": user_id,
                "relationship_type": relationship_type or "general",
                "timestamp": datetime.now().isoformat(),
                "quality_metrics": quality_metrics,
                "dimension_weights": {
                    dim: dimension_weights.get(dim.lower(), 10) for dim in quality_metrics.keys()
                },
                "overall_score": overall_score,
                "health_category": health_category,
                "top_strengths": [
                    {"dimension": dim, "score": score} for dim, score in top_strengths
                ],
                "areas_to_improve": [
                    {"dimension": dim, "score": score} for dim, score in areas_to_improve
                ],
                "insights": insights,
            }

            # Save to file
            json_content = json.dumps(score_data, indent=2)
            today = date.today()
            path = f"relationship_assessments/{user_id}/{today}_relationship_score.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            response_parts = [
                f"Relationship Score Analysis",
                "=" * 60,
                f"\n{color_emoji} Overall Score: {overall_score}/100",
                f"Health Category: {health_category}",
            ]

            if relationship_type:
                response_parts.append(f"Relationship Type: {relationship_type.title()}")

            response_parts.append("\n---\nDimension Breakdown:")
            for dim, score in sorted_dims:
                bar_length = "█" * (score // 2) + "░" * ((10 - score) // 2)
                response_parts.append(f"  {dim.title():<20} [{bar_length}] {score}/10")

            if top_strengths:
                response_parts.append("\n✓ Top Strengths:")
                for dim, score in top_strengths:
                    response_parts.append(f"  • {dim.title()}: {score}/10")

            if areas_to_improve:
                response_parts.append("\n→ Areas to Improve:")
                for dim, score in areas_to_improve:
                    response_parts.append(f"  • {dim.title()}: {score}/10")

            if insights:
                response_parts.append("\n💡 Key Insights:")
                for insight in insights:
                    response_parts.append(f"  • {insight}")

            if overall_score <= 35:
                response_parts.append(
                    "\n⚠️ Note: Low scores indicate significant relationship challenges. "
                    "Consider seeking professional support from a therapist or counselor."
                )

            response_parts.append(f"\nScore saved to: {path}")
            response_parts.append("\nTip: Reassess monthly to track progress and identify trends.")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error calculating relationship score: {str(e)}"

    @tool
    def assess_communication_compatibility(
        user_id: str,
        style_a_description: str,
        style_b_description: str,
        relationship_context: Optional[str] = "general",
    ) -> str:
        """Assess communication compatibility between two individuals.

        This tool analyzes communication patterns and styles to identify
        potential synergies, friction points, and strategies for improving
        mutual understanding between two people.

        Args:
            user_id: The user's unique identifier
            style_a_description: Description of person A's communication style
                               (e.g., "Direct, prefers clear instructions")
            style_b_description: Description of person B's communication style
                               (e.g., "Diplomatic, values consensus")
            relationship_context: Optional context (workplace, romantic, family)

        Returns:
            Compatibility assessment with synergy areas, potential conflicts,
            and practical strategies for better communication.
            Saved to relationship_assessments/{user_id}/

        Raises:
            ValueError: If required parameters are invalid

        Example:
            >>> assess_communication_compatibility(
            ...     "user_123",
            ...     "I prefer direct communication and getting straight to the point",
            ...     "My colleague likes to discuss things at length and build consensus"
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not style_a_description or not isinstance(style_a_description, str):
            return "Error: style_a_description must be a non-empty string"
        if not style_b_description or not isinstance(style_b_description, str):
            return "Error: style_b_description must be a non-empty string"

        try:
            # Communication style indicators
            direct_indicators = [
                "direct",
                "straightforward",
                "clear",
                "concise",
                "brief",
                "to the point",
                "honest",
                "blunt",
            ]
            diplomatic_indicators = [
                "diplomatic",
                "polite",
                "considerate",
                "gentle",
                "tactful",
                "respectful",
                "soft-spoken",
            ]
            analytical_indicators = [
                "analytical",
                "logical",
                "data-driven",
                "facts",
                "evidence",
                "detailed",
                "thorough",
            ]
            emotional_indicators = [
                "emotional",
                "feelings",
                "expressive",
                "passionate",
                "heartfelt",
                "sensitive",
                "caring",
            ]

            # Analyze style A
            style_a_lower = style_a_description.lower()
            scores_a = {
                "direct": sum(1 for ind in direct_indicators if ind in style_a_lower),
                "diplomatic": sum(1 for ind in diplomatic_indicators if ind in style_a_lower),
                "analytical": sum(1 for ind in analytical_indicators if ind in style_a_lower),
                "emotional": sum(1 for ind in emotional_indicators if ind in style_a_lower),
            }
            dominant_a = (
                max(scores_a, key=scores_a.get) if any(scores_a.values()) else "unspecified"
            )

            # Analyze style B
            style_b_lower = style_b_description.lower()
            scores_b = {
                "direct": sum(1 for ind in direct_indicators if ind in style_b_lower),
                "diplomatic": sum(1 for ind in diplomatic_indicators if ind in style_b_lower),
                "analytical": sum(1 for ind in analytical_indicators if ind in style_b_lower),
                "emotional": sum(1 for ind in emotional_indicators if ind in style_b_lower),
            }
            dominant_b = (
                max(scores_b, key=scores_b.get) if any(scores_b.values()) else "unspecified"
            )

            # Compatibility matrix
            compatibility_matrix = {
                ("direct", "diplomatic"): {
                    "synergy": "Efficiency + relationship-building",
                    "friction": "May seem too blunt vs. too indirect",
                    "strategies": [
                        "Direct person: Add 1-2 sentences of context before main point",
                        "Diplomatic person: State key request first, then elaborate",
                    ],
                },
                ("direct", "analytical"): {
                    "synergy": "Clear, fact-based communication",
                    "friction": "May miss emotional context vs. want more detail",
                    "strategies": [
                        "Both: Use bullet points for clarity",
                        "Direct person: Provide 1-2 key examples to support claims",
                    ],
                },
                ("diplomatic", "emotional"): {
                    "synergy": "High emotional intelligence and empathy",
                    "friction": "May avoid hard conversations vs. over-personalize",
                    "strategies": [
                        "Schedule regular check-ins to address issues proactively",
                        "Use 'I' statements to express feelings constructively",
                    ],
                },
                ("analytical", "emotional"): {
                    "synergy": "Balance of logic and empathy",
                    "friction": "Logic disconnect vs. emotional overwhelm",
                    "strategies": [
                        "Acknowledge feelings first, then discuss facts",
                        "Use data to support emotional points when appropriate",
                    ],
                },
            }

            # Get compatibility info
            compat_key = tuple(
                sorted([dominant_a, dominant_b])
                if {dominant_a, dominant_b} != {"unspecified"}
                else None
            )

            if compat_key and compat_key in compatibility_matrix:
                compat_info = compatibility_matrix[compat_key]
            else:
                # Default strategies
                compat_info = {
                    "synergy": "Opportunity for mutual learning and growth",
                    "friction": "Different communication preferences may cause misunderstandings",
                    "strategies": [
                        "Practice active listening - reflect back what you hear",
                        "Ask for clarification when unsure about tone or meaning",
                        "Establish shared communication norms (preferred methods, response times)",
                    ],
                }

            # Calculate compatibility score
            if compat_key and compat_key in compatibility_matrix:
                base_score = 70  # Good baseline for recognized patterns
            else:
                base_score = 60  # Moderate starting point

            compatibility_score = min(
                95, base_score + (sum(scores_a.values()) + sum(scores_b.values()))
            )

            # Build assessment data
            assessment = {
                "user_id": user_id,
                "relationship_context": relationship_context or "general",
                "timestamp": datetime.now().isoformat(),
                "style_a": {"description": style_a_description, "dominant_style": dominant_a},
                "style_b": {"description": style_b_description, "dominant_style": dominant_b},
                "compatibility_score": compatibility_score,
                "synergy_areas": [compat_info["synergy"]],
                "potential_friction": [compat_info["friction"]],
                "strategies": compat_info["strategies"],
            }

            # Save to file
            json_content = json.dumps(assessment, indent=2)
            today = date.today()
            path = f"relationship_assessments/{user_id}/{today}_communication_compatibility.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            emoji = (
                "💚" if compatibility_score >= 70 else ("🟡" if compatibility_score >= 60 else "🔴")
            )

            response_parts = [
                f"Communication Compatibility Assessment",
                "=" * 60,
                f"\n{emoji} Compatibility Score: {compatibility_score}/100",
            ]

            if relationship_context:
                response_parts.append(f"Context: {relationship_context.title()}")

            response_parts.append("\n---\nCommunication Styles:")
            response_parts.append(f"  Person A: {dominant_a.title()} dominant")
            response_parts.append(f"  Person B: {dominant_b.title()} dominant")

            response_parts.append("\n✓ Synergy Areas:")
            for synergy in compat_info["synergy_areas"]:
                response_parts.append(f"  • {synergy}")

            response_parts.append("\n⚠️ Potential Friction Points:")
            for friction in compat_info["potential_friction"]:
                response_parts.append(f"  • {friction}")

            response_parts.append("\n💡 Strategies for Better Communication:")
            for i, strategy in enumerate(compat_info["strategies"], 1):
                response_parts.append(f"  {i}. {strategy}")

            response_parts.append("\n---\nGeneral Tips:")
            response_parts.append(
                "  • Have an explicit conversation about communication preferences"
            )
            response_parts.append("  • Establish shared norms for feedback and disagreements")
            response_parts.append("  • Check in regularly about how communication is working")

            response_parts.append(f"\nAssessment saved to: {path}")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error assessing communication compatibility: {str(e)}"

    print("Relationship tools created successfully!")
    return (
        analyze_communication_style,
        create_boundary_setting_plan,
        apply_dear_man_technique,
        assess_relationship_quality,
        develop_social_connection_plan,
        calculate_relationship_score,
        assess_communication_compatibility,
    )


# Export tools at module level for convenience
__all__ = [
    "create_relationship_tools",
]
