"""
Wellness Coach tools for AI Life Coach.

This module provides LangChain tools specialized for holistic wellness coaching.
All tools use the @tool decorator and follow best practices for validation,
error handling, and user-friendly output.

Tools:
- assess_wellness_dimensions: Comprehensive assessment across 8 dimensions of wellness
- create_habit_formation_plan: Build sustainable habits using Atomic Habits framework
- provide_stress_management_techniques: Evidence-based stress reduction strategies
- create_sleep_optimization_plan: Personalized sleep improvement recommendations
- design_exercise_program: Exercise planning based on fitness level and goals

Based on evidence-based frameworks including:
- WHO/SAMHSA 8 Dimensions of Wellness
- Atomic Habits framework (James Clear)
- Sleep hygiene and circadian rhythm research
- Evidence-based stress management techniques
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
# Wellness Tool Factory
# ==============================================================================


def create_wellness_tools(backend=None) -> tuple:
    """
    Create wellness tools with shared FilesystemBackend instance.

    These tools enable the Wellness Specialist to:
    - Assess wellness across 8 dimensions (WHO/SAMHSA framework)
    - Build sustainable habits using Atomic Habits principles
    - Provide stress management and coping strategies
    - Create sleep optimization plans based on circadian science
    - Design exercise programs appropriate for different fitness levels

    Args:
        backend: Optional FilesystemBackend instance. If None, uses get_backend()

    Returns:
        Tuple of wellness tools (assess_wellness_dimensions,
                               create_habit_formation_plan,
                               provide_stress_management_techniques,
                               create_sleep_optimization_plan,
                               design_exercise_program)

    Example:
        >>> from src.config import config
        >>> config.initialize_environment()
        >>> tools = create_wellness_tools()
        >>> result = assess_wellness_dimensions(
        ...     user_id="user_123",
        ...     physical_score=5,
        ...     emotional_score=6,
        ...     social_score=4
        ... )
    """
    if backend is None:
        backend = get_backend()

    # Get the workspace directory path from backend
    workspace_path = Path(backend.root_dir) if hasattr(backend, "root_dir") else Path("workspace")

    # WHO/SAMHSA 8 Dimensions of Wellness framework
    WELLNESS_DIMENSIONS = {
        "physical": {
            "name": "Physical Wellness",
            "description": "Caring for your body through exercise, nutrition, sleep, and preventive care",
            "indicators": [
                "Regular physical activity",
                "Adequate sleep (7-9 hours)",
                "Nutritious diet",
                "Preventive healthcare checkups",
            ],
        },
        "emotional": {
            "name": "Emotional Wellness",
            "description": "Understanding and managing your emotions, coping with stress effectively",
            "indicators": [
                "Emotional awareness and expression",
                "Stress management skills",
                "Self-compassion and resilience",
                "Healthy emotional boundaries",
            ],
        },
        "social": {
            "name": "Social Wellness",
            "description": "Building and maintaining healthy relationships and social connections",
            "indicators": [
                "Quality relationships",
                "Social support network",
                "Healthy boundaries in relationships",
                "Sense of belonging and community",
            ],
        },
        "intellectual": {
            "name": "Intellectual Wellness",
            "description": "Engaging in creative and mentally stimulating activities",
            "indicators": [
                "Continuous learning",
                "Creative expression",
                "Critical thinking skills",
                "Openness to new ideas",
            ],
        },
        "spiritual": {
            "name": "Spiritual Wellness",
            "description": "Finding meaning, purpose, and values that guide your life",
            "indicators": [
                "Sense of purpose and meaning",
                "Values alignment in daily life",
                "Practices that nurture spirit (meditation, prayer, nature)",
                "Inner peace and contentment",
            ],
        },
        "environmental": {
            "name": "Environmental Wellness",
            "description": "Creating environments that support your wellbeing at home and work",
            "indicators": [
                "Safe and comfortable living space",
                "Healthy work environment",
                "Connection with nature",
                "Minimizing environmental toxins",
            ],
        },
        "occupational": {
            "name": "Occupational Wellness",
            "description": "Finding personal satisfaction and enrichment in your work",
            "indicators": [
                "Job satisfaction",
                "Work-life balance",
                "Professional growth opportunities",
                "Meaningful contribution through work",
            ],
        },
        "financial": {
            "name": "Financial Wellness",
            "description": "Managing finances effectively and planning for the future",
            "indicators": [
                "Budget management",
                "Emergency savings",
                "Debt under control",
                "Financial planning for goals",
            ],
        },
    }

    @tool
    def assess_wellness_dimensions(
        user_id: str,
        physical_score: Optional[int] = None,
        emotional_score: Optional[int] = None,
        social_score: Optional[int] = None,
        intellectual_score: Optional[int] = None,
        spiritual_score: Optional[int] = None,
        environmental_score: Optional[int] = None,
        occupational_score: Optional[int] = None,
        financial_score: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> str:
        """Assess wellness across 8 dimensions using the WHO/SAMHSA framework.

        This tool performs a comprehensive wellness assessment based on 8 dimensions:
        Physical, Emotional, Social, Intellectual, Spiritual, Environmental,
        Occupational, and Financial wellness. Each dimension is rated 1-10.

        Args:
            user_id: The user's unique identifier
            physical_score: Physical wellness rating (1-10, optional)
            emotional_score: Emotional wellness rating (1-10, optional)
            social_score: Social wellness rating (1-10, optional)
            intellectual_score: Intellectual wellness rating (1-10, optional)
            spiritual_score: Spiritual wellness rating (1-10, optional)
            environmental_score: Environmental wellness rating (1-10, optional)
            occupational_score: Occupational wellness rating (1-10, optional)
            financial_score: Financial wellness rating (1-10, optional)
            notes: Optional additional context or observations

        Returns:
            Structured wellness assessment with dimension scores, overall health,
            and prioritized recommendations. Saved to wellness_assessments/{user_id}/

        Raises:
            ValueError: If user_id is invalid or scores are out of range (must be 1-10)

        Example:
            >>> assess_wellness_dimensions(
            ...     "user_123",
            ...     physical_score=5,
            ...     emotional_score=6,
            ...     social_score=4,
            ...     occupational_score=3
            ... )
        """
        # Validate user_id
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        # Collect all scores
        scores = {
            "physical": physical_score,
            "emotional": emotional_score,
            "social": social_score,
            "intellectual": intellectual_score,
            "spiritual": spiritual_score,
            "environmental": environmental_score,
            "occupational": occupational_score,
            "financial": financial_score,
        }

        # Validate scores
        for dimension, score in scores.items():
            if score is not None and (not isinstance(score, int) or score < 1 or score > 10):
                return f"Error: {dimension}_score must be an integer between 1 and 10"

        try:
            # Create assessment structure
            assessment = {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "dimensions": {},
                "overall_score": None,
                "notes": notes or "",
            }

            # Calculate scores for each dimension
            valid_scores = []
            for dim_key, score in scores.items():
                if score is not None:
                    valid_scores.append(score)
                    dim_info = WELLNESS_DIMENSIONS[dim_key]
                    assessment["dimensions"][dim_key] = {
                        "score": score,
                        "name": dim_info["name"],
                        "description": dim_info["description"],
                    }

            # Calculate overall average if we have at least one score
            if valid_scores:
                assessment["overall_score"] = round(sum(valid_scores) / len(valid_scores), 1)

            # Identify strengths (7+) and areas for improvement (5 or below)
            strengths = []
            improvements = []

            for dim_key, score in scores.items():
                if score is not None:
                    dim_name = WELLNESS_DIMENSIONS[dim_key]["name"]
                    if score >= 7:
                        strengths.append(f"{dim_name} ({score}/10)")
                    elif score <= 5:
                        improvements.append(f"{dim_name} ({score}/10)")

            # Generate prioritized recommendations
            recommendations = []

            if improvements:
                top_priorities = sorted(
                    [d for d in scores.keys() if scores[d] is not None and scores[d] <= 5],
                    key=lambda x: scores[x],  # type: ignore
                )

                for priority in top_priorities[:3]:  # Focus on top 3 areas
                    dim_name = WELLNESS_DIMENSIONS[priority]["name"]
                    recommendations.append(
                        f"Priority: Improve {dim_name} wellness - score is currently {scores[priority]}/10"
                    )

            if strengths:
                recommendations.append(f"Build on your strengths in: {', '.join(strengths)}")

            # Save to file
            json_content = json.dumps(assessment, indent=2)
            today = date.today()
            path = f"wellness_assessments/{user_id}/{today}_8_dimensions_assessment.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            response_parts = [
                "8 Dimensions of Wellness Assessment",
                "=" * 60,
                f"\nOverall Wellness Score: {assessment['overall_score']}/10"
                if assessment["overall_score"]
                else "\nOverall Wellness Score: Not enough data",
            ]

            if scores:
                response_parts.append("\nDimension Scores:")
                for dim_key, score in sorted(scores.items()):
                    if score is not None:
                        dim_name = WELLNESS_DIMENSIONS[dim_key]["name"]
                        response_parts.append(f"  • {dim_name}: {score}/10")

            if strengths:
                response_parts.append(f"\n✓ Strengths: {', '.join(strengths)}")

            if improvements:
                response_parts.append(f"\n◐ Areas for Improvement: {', '.join(improvements)}")

            if recommendations:
                response_parts.append("\nRecommendations:")
                for i, rec in enumerate(recommendations, 1):
                    response_parts.append(f"  {i}. {rec}")

            if notes:
                response_parts.append(f"\nNotes: {notes}")

            response_parts.append(f"\nAssessment saved to: {path}")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error assessing wellness dimensions: {str(e)}"

    @tool
    def create_habit_formation_plan(
        user_id: str,
        habit_name: str,
        cue_description: Optional[str] = None,
        routine_steps: Optional[List[str]] = None,
        reward_description: Optional[str] = None,
        existing_habit_to_stack: Optional[str] = None,
    ) -> str:
        """Create a habit formation plan using the Atomic Habits framework.

        This tool uses James Clear's 4 Laws of Behavior Change to create
        sustainable habits: Make it obvious, attractive, easy, and satisfying.
        The Cue-Routine-Reward loop forms the foundation of habit building.

        Args:
            user_id: The user's unique identifier
            habit_name: Name of the habit to build (e.g., "Morning meditation")
            cue_description: What triggers the habit? (time, location, emotion)
            routine_steps: List of steps in the habit routine (keep it small initially!)
            reward_description: What makes this habit satisfying?
            existing_habit_to_stack: Optional existing habit to stack this new one onto

        Returns:
            Structured habit formation plan with cue-routine-reward loop,
            implementation strategies, and tracking tips. Saved to habit_plans/{user_id}/

        Raises:
            ValueError: If user_id or habit_name is invalid

        Example:
            >>> create_habit_formation_plan(
            ...     "user_123",
            ...     habit_name="10-minute morning walk",
            ...     cue_description="Right after I brush my teeth",
            ...     routine_steps=["Put on walking shoes", "Walk outside for 10 minutes"],
            ...     reward_description="Feel energized and listen to music",
            ...     existing_habit_to_stack="Brushing teeth"
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not habit_name or not isinstance(habit_name, str):
            return "Error: habit_name must be a non-empty string"

        try:
            # Create habit plan structure
            habit_plan = {
                "user_id": user_id,
                "habit_name": habit_name,
                "timestamp": datetime.now().isoformat(),
                "framework": "Atomic Habits - 4 Laws of Behavior Change",
                "cue_loop": {
                    "cue": cue_description or "To be determined - identify your trigger",
                    "routine": routine_steps or ["Start with a 2-minute version"],
                    "reward": reward_description or "Identify what makes this enjoyable",
                },
                "habit_stacking": existing_habit_to_stack,
            }

            # Generate implementation strategies based on 4 Laws
            strategies = []

            # Law 1: Make it Obvious
            if existing_habit_to_stack:
                strategies.append(
                    f"Make It Obvious: Stack this habit after '{existing_habit_to_stack}' - "
                    "use implementation intention: 'After I INSERT EXISTING HABIT, I will NEW HABIT.'"
                )
            else:
                strategies.append(
                    "Make It Obvious: Choose a clear time and location. "
                    "Use implementation intention: 'I will [BEHAVIOR] at [TIME] in [LOCATION].'"
                )

            # Law 2: Make it Attractive
            strategies.append(
                "Make It Attractive: Pair this habit with something you enjoy. "
                "Focus on the benefits, not the effort."
            )

            # Law 3: Make it Easy
            strategies.append(
                "Make It Easy: Start ridiculously small - 2 minutes max. "
                "Reduce friction (prepare in advance, remove obstacles)."
            )

            # Law 4: Make it Satisfying
            strategies.append(
                "Make It Satisfying: Track your habit visually. "
                "Celebrate small wins immediately after completing the routine."
            )

            habit_plan["strategies"] = strategies

            # Create tracking and tips
            habit_plan["tracking_tips"] = [
                "Use a simple tracker (checkmark calendar, app)",
                "Focus on consistency, not perfection - never miss twice",
                "Start small and scale up after 2 weeks of consistency",
            ]

            # Save to file
            json_content = json.dumps(habit_plan, indent=2)
            today = date.today()
            path = f"habit_plans/{user_id}/{today}_{habit_name.replace(' ', '_').lower()}.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            response = f"""Habit Formation Plan: {habit_name}

{"=" * 60}

## The Habit Loop

**Cue (Trigger):**
{habit_plan["cue_loop"]["cue"]}

**Routine:**
{chr(10).join([f"  {i + 1}. {step}" for i, step in enumerate(habit_plan["cue_loop"]["routine"])]) if routine_steps else "  To be determined - start simple!"}

**Reward:**
{habit_plan["cue_loop"]["reward"]}

"""
            if existing_habit_to_stack:
                response += (
                    f"\n**Habit Stacking:** This habit will follow '{existing_habit_to_stack}'\n"
                )

            response += "\n## Implementation Strategies\n"
            for i, strategy in enumerate(strategies, 1):
                response += f"{i}. {strategy}\n"

            response += "\n## Tracking Tips\n"
            for i, tip in enumerate(habit_plan["tracking_tips"], 1):
                response += f"• {tip}\n"

            response += f"\nPlan saved to: {path}"

            return response

        except Exception as e:
            return f"Error creating habit formation plan: {str(e)}"

    @tool
    def provide_stress_management_techniques(
        user_id: str,
        stress_level: Optional[str] = None,
        preferred_technique_type: Optional[str] = None,
    ) -> str:
        """Provide evidence-based stress management techniques.

        This tool offers a variety of proven stress reduction strategies including
        breathing exercises, mindfulness practices, cognitive reframing techniques,
        and lifestyle adjustments based on the user's stress level and preferences.

        Args:
            user_id: The user's unique identifier
            stress_level: Optional current stress level (low, medium, high)
            preferred_technique_type: Optional preference for technique type
                                     (breathing, mindfulness, cognitive, lifestyle)

        Returns:
            Curated stress management techniques with step-by-step instructions,
            tailored to the user's situation. Saved to wellness_resources/{user_id}/

        Raises:
            ValueError: If user_id is invalid

        Example:
            >>> provide_stress_management_techniques(
            ...     "user_123",
            ...     stress_level="high",
            ...     preferred_technique_type="breathing"
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        try:
            # Define stress management techniques by category
            techniques = {
                "breathing": [
                    {
                        "name": "Box Breathing (4-4-4-4)",
                        "description": "Navy SEAL technique for instant calm",
                        "steps": [
                            "Inhale through nose for 4 counts",
                            "Hold breath for 4 counts",
                            "Exhale through mouth for 4 counts",
                            "Hold empty lungs for 4 counts",
                            "Repeat for 2-3 minutes",
                        ],
                        "best_for": "High stress, anxiety attacks",
                    },
                    {
                        "name": "4-7-8 Breathing",
                        "description": "Dr. Andrew Weil's relaxing breath technique",
                        "steps": [
                            "Inhale through nose for 4 counts",
                            "Hold breath for 7 counts",
                            "Exhale through mouth (making whoosh sound) for 8 counts",
                            "Repeat for 4 cycles",
                        ],
                        "best_for": "Sleep, deep relaxation",
                    },
                    {
                        "name": "Diaphragmatic Breathing",
                        "description": "Deep belly breathing to activate parasympathetic nervous system",
                        "steps": [
                            "Place one hand on chest, one on belly",
                            "Breathe in slowly through nose, feeling belly rise",
                            "Chest should remain relatively still",
                            "Exhale slowly through pursed lips",
                            "Practice for 5-10 minutes daily",
                        ],
                        "best_for": "Chronic stress, anxiety",
                    },
                ],
                "mindfulness": [
                    {
                        "name": "5-4-3-2-1 Grounding",
                        "description": "Sensory anchoring technique for present-moment awareness",
                        "steps": [
                            "Acknowledge 5 things you can see",
                            "Acknowledge 4 things you can touch",
                            "Acknowledge 3 things you can hear",
                            "Acknowledge 2 things you can smell",
                            "Acknowledge 1 thing you can taste",
                        ],
                        "best_for": "Overwhelm, racing thoughts",
                    },
                    {
                        "name": "Body Scan Meditation",
                        "description": "Systematic relaxation of the entire body",
                        "steps": [
                            "Lie down or sit comfortably",
                            "Focus attention on your feet, notice any sensations",
                            "Slowly move attention up through legs, torso, arms, head",
                            "Release tension in each area as you scan",
                            "Practice for 10-20 minutes",
                        ],
                        "best_for": "Sleep preparation, relaxation",
                    },
                ],
                "cognitive": [
                    {
                        "name": "Cognitive Reframing",
                        "description": "Changing perspective on stressful thoughts",
                        "steps": [
                            "Identify the stressful thought",
                            "Ask: 'Is this absolutely true?'",
                            "Look for alternative perspectives",
                            "Challenge catastrophic thinking with evidence",
                            "Replace with a balanced thought",
                        ],
                        "best_for": "Anxious thoughts, worry loops",
                    },
                ],
            }

            # Select techniques based on preferences
            selected_techniques = []

            if preferred_technique_type and preferred_technique_type.lower() in techniques:
                selected_techniques = techniques[preferred_technique_type.lower()]
            else:
                # Return a mix of the most effective techniques
                selected_techniques = [
                    techniques["breathing"][0],  # Box breathing
                    techniques["mindfulness"][0],  # Grounding
                    techniques["cognitive"][0],  # Cognitive reframing
                ]

            # Create resource structure
            resource = {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "stress_level": stress_level or "not specified",
                "preferred_type": preferred_technique_type or "general",
                "techniques_provided": [t["name"] for t in selected_techniques],
            }

            # Save to file
            json_content = json.dumps(resource, indent=2)
            today = date.today()
            path = f"wellness_resources/{user_id}/{today}_stress_management_techniques.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            stress_context = f" for {stress_level} stress levels" if stress_level else ""

            response = f"""Stress Management Techniques{stress_context}

{"=" * 60}
"""

            for i, technique in enumerate(selected_techniques, 1):
                response += f"""
## {i}. {technique["name"]}

**What it is:** {technique["description"]}
**Best for:** {technique["best_for"]}

**How to practice:**
{chr(10).join([f"{j}. {step}" for j, step in enumerate(technique["steps"], 1)])}

"""

            response += f"\n## Tips for Success\n"
            response += "• Try different techniques to find what works best for you\n"
            response += "• Practice regularly, not just when stressed - prevention is key\n"
            response += "• Start with shorter sessions (2-5 minutes) and build up\n"
            response += "• Be patient with yourself - these skills take time to develop\n"

            if stress_level == "high":
                response += "\n⚠️ If you're experiencing severe or persistent stress, please consider reaching out to a mental health professional.\n"

            response += f"\nSaved to: {path}"

            return response

        except Exception as e:
            return f"Error providing stress management techniques: {str(e)}"

    @tool
    def create_sleep_optimization_plan(
        user_id: str,
        current_bedtime: Optional[str] = None,
        current_wake_time: Optional[str] = None,
        sleep_issues: Optional[List[str]] = None,
    ) -> str:
        """Create a personalized sleep optimization plan based on circadian science.

        This tool generates evidence-based sleep improvement recommendations including
        sleep hygiene practices, circadian rhythm alignment strategies, and specific
        solutions for common sleep issues.

        Args:
            user_id: The user's unique identifier
            current_bedtime: Optional current bedtime (e.g., "11:30 PM")
            current_wake_time: Optional current wake time (e.g., "7:00 AM")
            sleep_issues: Optional list of specific sleep issues
                          (e.g., ["trouble falling asleep", "waking up often"])

        Returns:
            Structured sleep optimization plan with actionable recommendations,
        circadian alignment strategies, and issue-specific solutions.
        Saved to sleep_plans/{user_id}/

        Raises:
            ValueError: If user_id is invalid

        Example:
            >>> create_sleep_optimization_plan(
            ...     "user_123",
            ...     current_bedtime="11:30 PM",
            ...     current_wake_time="6:30 AM",
            ...     sleep_issues=["trouble falling asleep", "racing thoughts"]
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        try:
            # Define sleep hygiene practices based on evidence
            sleep_hygiene = {
                "environment": [
                    "Keep bedroom cool (65-68°F / 18-20°C)",
                    "Make room as dark as possible (blackout curtains, eye mask)",
                    "Minimize noise (earplugs, white noise machine)",
                    "Use bed only for sleep and intimacy",
                ],
                "routine": [
                    "Establish consistent bedtime and wake time (even weekends)",
                    "Create 30-60 minute wind-down routine before bed",
                    "Avoid screens 1-2 hours before sleep (blue light disrupts melatonin)",
                    "Limit caffeine after 2 PM",
                    "Avoid large meals and alcohol close to bedtime",
                ],
                "daytime": [
                    "Get morning sunlight exposure (15-30 minutes within an hour of waking)",
                    "Exercise regularly, but not within 2-3 hours of bedtime",
                    "Limit naps to 20-30 minutes and before 3 PM",
                ],
            }

            # Define solutions for common sleep issues
            issue_solutions = {
                "trouble falling asleep": [
                    "Try 4-7-8 breathing or progressive muscle relaxation in bed",
                    "Write tomorrow's to-do list before bed to offload racing thoughts",
                    "Keep a worry journal: write down concerns and set aside time tomorrow to address them",
                ],
                "waking up often": [
                    "Avoid liquids close to bedtime to reduce bathroom trips",
                    "Keep room temperature cool and consistent",
                    "Address any noise or light disturbances",
                ],
                "not feeling rested": [
                    "Ensure you're getting 7-9 hours of sleep opportunity",
                    "Evaluate sleep apnea risk (snoring, gasping) if symptoms persist",
                    "Limit alcohol - it disrupts sleep quality even if you fall asleep easily",
                ],
                "racing thoughts": [
                    "Practice the 4-7-8 breathing technique",
                    "Try cognitive defusion: observe thoughts without engaging with them",
                    "Use a 'brain dump' - write down everything on your mind before bed",
                ],
            }

            # Create sleep plan structure
            sleep_plan = {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "current_schedule": {
                    "bedtime": current_bedtime or "not specified",
                    "wake_time": current_wake_time or "not specified",
                },
                "reported_issues": sleep_issues or [],
                "framework": "Circadian rhythm alignment and sleep hygiene best practices",
            }

            # Calculate current sleep duration if times provided
            if current_bedtime and current_wake_time:
                # Simple calculation - in production would do proper time parsing
                sleep_plan["estimated_sleep_duration"] = "Calculated based on provided times"

            # Generate personalized recommendations
            all_recommendations = []

            # Add core sleep hygiene practices
            for category, practices in sleep_hygiene.items():
                all_recommendations.extend(practices)

            # Add issue-specific solutions
            if sleep_issues:
                for issue in sleep_issues:
                    issue_key = issue.lower()
                    for known_issue, solutions in issue_solutions.items():
                        if known_issue in issue_key or any(
                            word in issue_key for word in known_issue.split()
                        ):
                            all_recommendations.extend(solutions)

            sleep_plan["recommendations"] = all_recommendations

            # Save to file
            json_content = json.dumps(sleep_plan, indent=2)
            today = date.today()
            path = f"sleep_plans/{user_id}/{today}_sleep_optimization.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            response = f"""Sleep Optimization Plan

{"=" * 60}
"""

            if current_bedtime and current_wake_time:
                response += f"\nCurrent Schedule:\n"
                response += f"  • Bedtime: {current_bedtime}\n"
                response += f"  • Wake Time: {current_wake_time}\n"

            if sleep_issues:
                response += f"\nIdentified Issues:\n"
                for issue in sleep_issues:
                    response += f"  • {issue}\n"

            response += "\n## Sleep Environment\n"
            for i, practice in enumerate(sleep_hygiene["environment"], 1):
                response += f"{i}. {practice}\n"

            response += "\n## Bedtime Routine\n"
            for i, practice in enumerate(sleep_hygiene["routine"], 1):
                response += f"{i}. {practice}\n"

            response += "\n## Daytime Habits (Circadian Alignment)\n"
            for i, practice in enumerate(sleep_hygiene["daytime"], 1):
                response += f"{i}. {practice}\n"

            if sleep_issues:
                response += "\n## Solutions for Your Specific Issues\n"
                for issue in sleep_issues:
                    issue_key = issue.lower()
                    solutions_found = False
                    for known_issue, solutions in issue_solutions.items():
                        if known_issue in issue_key or any(
                            word in issue_key for word in known_issue.split()
                        ):
                            response += f"\n**{issue}:**\n"
                            for sol in solutions:
                                response += f"  • {sol}\n"
                            solutions_found = True
                            break

            response += f"\nPlan saved to: {path}"

            response += """

## Expected Timeline

• Week 1-2: Implement sleep environment and routine changes
• Week 3-4: Establish consistent schedule, notice initial improvements
• Month 2+: Consolidated improvements in sleep quality and energy

## Important Notes

If sleep issues persist despite implementing these strategies for 2-3 weeks,
consider consulting with a healthcare provider or sleep specialist.
"""

            return response

        except Exception as e:
            return f"Error creating sleep optimization plan: {str(e)}"

    @tool
    def design_exercise_program(
        user_id: str,
        fitness_level: Optional[str] = None,
        primary_goals: Optional[List[str]] = None,
        preferred_activities: Optional[List[str]] = None,
        time_available_per_week: Optional[int] = None,
    ) -> str:
        """Design a personalized exercise program based on fitness level and goals.

        This tool creates an evidence-based exercise plan appropriate for the
        user's current fitness level, with clear progression guidelines and a
        balanced approach to cardiovascular health, strength, and flexibility.

        Args:
            user_id: The user's unique identifier
            fitness_level: Optional current fitness level (sedentary, beginner,
                          intermediate, advanced)
            primary_goals: Optional list of fitness goals
                          (e.g., ["weight loss", "improve energy"])
            preferred_activities: Optional list of activities they enjoy
                                 (e.g., ["walking", "swimming", "yoga"])
            time_available_per_week: Optional minutes available per week (integer)

        Returns:
            Structured exercise program with weekly schedule, activity recommendations,
            progression guidelines, and safety considerations.
            Saved to exercise_plans/{user_id}/

        Raises:
            ValueError: If user_id is invalid

        Example:
            >>> design_exercise_program(
            ...     "user_123",
            ...     fitness_level="beginner",
            ...     primary_goals=["improve energy", "build strength"],
            ...     preferred_activities=["walking", "bodyweight exercises"],
            ...     time_available_per_week=150
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        if time_available_per_week is not None:
            if not isinstance(time_available_per_week, int) or time_available_per_week < 0:
                return "Error: time_available_per_week must be a non-negative integer"

        try:
            # Define fitness level characteristics
            fitness_levels = {
                "sedentary": {
                    "description": "Little to no regular physical activity",
                    "recommended_start": "10-15 minute walks, 2-3x per week",
                    "key_principle": "Start very small - consistency over intensity",
                },
                "beginner": {
                    "description": "Some activity, but not exercising regularly",
                    "recommended_start": "20-30 minute sessions, 3x per week",
                    "key_principle": "Build the exercise habit first",
                },
                "intermediate": {
                    "description": "Regularly exercising 1-2x per week",
                    "recommended_start": "30-45 minute sessions, 3-4x per week",
                    "key_principle": "Increase volume and introduce variety",
                },
                "advanced": {
                    "description": "Regularly exercising 3+ times per week",
                    "recommended_start": "45-60 minute sessions, 4-5x per week",
                    "key_principle": "Optimize performance and prevent plateauing",
                },
            }

            # Define exercise components
            exercise_components = {
                "cardiovascular": {
                    "benefits": "Heart health, endurance, calorie burn",
                    "examples": ["Walking", "Swimming", "Cycling", "Jogging", "Dancing"],
                    "guideline": "150 minutes moderate or 75 minutes vigorous per week",
                },
                "strength": {
                    "benefits": "Muscle mass, bone density, metabolism",
                    "examples": [
                        "Bodyweight exercises (squats, push-ups)",
                        "Resistance bands",
                        "Weight training",
                    ],
                    "guideline": "2-3 sessions per week, targeting major muscle groups",
                },
                "flexibility": {
                    "benefits": "Range of motion, injury prevention, relaxation",
                    "examples": ["Stretching", "Yoga", "Pilates"],
                    "guideline": "2-3 sessions per week, can be combined with other workouts",
                },
            }

            # Create exercise program structure
            exercise_program = {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "fitness_level": fitness_level or "not specified",
                "primary_goals": primary_goals or [],
                "preferred_activities": preferred_activities or [],
                "time_available_per_week": time_available_per_week,
            }

            # Generate recommendations based on inputs
            level_info = fitness_levels.get(fitness_level, fitness_levels["beginner"])

            # Determine weekly structure
            if time_available_per_week:
                sessions_per_week = min(5, max(3, time_available_per_week // 30))
                session_length = time_available_per_week // sessions_per_week
            else:
                sessions_per_week = 3
                session_length = 30

            weekly_schedule = []
            for i in range(sessions_per_week):
                day_num = i + 1
                if i % 3 == 0:
                    session_type = "Cardiovascular"
                elif i % 3 == 1:
                    session_type = "Strength"
                else:
                    session_type = "Flexibility/Recovery"

                weekly_schedule.append(
                    {
                        "day": f"Day {day_num}",
                        "type": session_type,
                        "duration_minutes": session_length,
                    }
                )

            exercise_program["weekly_schedule"] = weekly_schedule

            # Generate progression guidelines
            progression_guidelines = [
                "Week 1-2: Focus on building the habit - prioritize consistency over intensity",
                "Week 3-4: Slightly increase duration or intensity if feeling good",
                "Month 2+: Evaluate goals and adjust program accordingly",
            ]

            exercise_program["progression_guidelines"] = progression_guidelines

            # Safety considerations
            safety_considerations = [
                "Listen to your body - rest if experiencing pain (not normal discomfort)",
                "Stay hydrated before, during, and after exercise",
                "Include warm-up (5-10 minutes) and cool-down (5-10 minutes)",
                "Consult a healthcare provider before starting any new exercise program",
            ]

            if fitness_level == "sedentary" or fitness_level is None:
                safety_considerations.insert(0, "Start VERY slowly - your body needs time to adapt")

            exercise_program["safety_considerations"] = safety_considerations

            # Save to file
            json_content = json.dumps(exercise_program, indent=2)
            today = date.today()
            goals_str = "_".join(primary_goals[:2]) if primary_goals else "general"
            path = f"exercise_plans/{user_id}/{today}_{goals_str}_program.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            response = f"""Personalized Exercise Program

{"=" * 60}
"""

            if fitness_level:
                response += f"\nFitness Level: {fitness_level}\n"
                response += f"Description: {level_info['description']}\n"

            if primary_goals:
                response += f"\nPrimary Goals:\n"
                for goal in primary_goals:
                    response += f"  • {goal}\n"

            if time_available_per_week:
                response += f"\nTime Available: {time_available_per_week} minutes/week\n"

            if preferred_activities:
                response += f"\nPreferred Activities:\n"
                for activity in preferred_activities:
                    response += f"  • {activity}\n"

            response += f"\n## Key Principle\n{level_info['key_principle']}\n"

            response += "\n## Weekly Schedule\n"
            for session in weekly_schedule:
                response += f"\n**{session['day']}** - {session['type']} ({session['duration_minutes']} min)\n"

            response += "\n## Exercise Components\n"
            for comp_type, info in exercise_components.items():
                response += f"\n**{comp_type.capitalize()} Training**\n"
                response += f"Benefits: {info['benefits']}\n"
                if preferred_activities:
                    matching = [
                        a
                        for a in info["examples"]
                        if any(p.lower() in a.lower() for p in preferred_activities)
                    ]
                    examples = matching if matching else info["examples"][:3]
                else:
                    examples = info["examples"][:3]
                response += f"Examples: {', '.join(examples)}\n"
                response += f"Guideline: {info['guideline']}\n"

            response += "\n## Progression Guidelines\n"
            for i, guideline in enumerate(progression_guidelines, 1):
                response += f"{i}. {guideline}\n"

            response += "\n## Safety Considerations\n"
            for i, consideration in enumerate(safety_considerations, 1):
                response += f"{i}. {consideration}\n"

            response += f"\nProgram saved to: {path}"

            return response

        except Exception as e:
            return f"Error designing exercise program: {str(e)}"

    @tool
    def calculate_wellness_score(
        user_id: str,
        dimensions_scores: Dict[str, int],
    ) -> str:
        """Calculate an overall wellness score from dimension scores.

        This tool computes a comprehensive wellness score based on multiple
        dimensions (physical, emotional, social, intellectual, spiritual,
        environmental, occupational, financial) and provides insights into
        overall wellbeing.

        Args:
            user_id: The user's unique identifier
            dimensions_scores: Dictionary of wellness dimension scores (1-10 scale):
                              {"physical": 7, "emotional": 6, "social": 5, ...}

        Returns:
            Overall wellness score with dimension breakdowns, health category,
            and prioritized recommendations. Saved to wellness_assessments/{user_id}/

        Raises:
            ValueError: If user_id or dimensions_scores are invalid

        Example:
            >>> calculate_wellness_score(
            ...     "user_123",
            ...     {"physical": 7, "emotional": 6, "social": 5}
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not dimensions_scores or not isinstance(dimensions_scores, dict):
            return "Error: dimensions_scores must be a non-empty dictionary"

        # Validate scores
        for dim, score in dimensions_scores.items():
            if not isinstance(score, int) or score < 1 or score > 10:
                return f"Error: Score for '{dim}' must be an integer between 1 and 10"

        try:
            # Calculate overall score (average of all dimensions)
            valid_scores = [s for s in dimensions_scores.values()]
            overall_score = round(sum(valid_scores) / len(valid_scores), 1)

            # Determine wellness category
            if overall_score >= 8:
                wellness_category = "Thriving"
                emoji_level = "🌟"
            elif overall_score >= 6:
                wellness_category = "Healthy & Balanced"
                emoji_level = "💚"
            elif overall_score >= 4:
                wellness_category = "Moderate - Room for Growth"
                emoji_level = "🟡"
            else:
                wellness_category = "Needs Attention"
                emoji_level = "🔴"

            # Identify strengths and areas for improvement
            strengths = {dim: score for dim, score in dimensions_scores.items() if score >= 7}
            improvements = {dim: score for dim, score in dimensions_scores.items() if score <= 5}

            # Sort by score for prioritization
            sorted_strengths = sorted(strengths.items(), key=lambda x: -x[1])
            sorted_improvements = sorted(improvements.items(), key=lambda x: x[1])

            # Generate prioritized recommendations
            recommendations = []

            if sorted_improvements:
                # Focus on lowest-scoring dimensions first
                priority_dim, priority_score = sorted_improvements[0]
                dim_name = WELLNESS_DIMENSIONS.get(priority_dim, {}).get("name", priority_dim)
                recommendations.append(
                    f"Priority 1: Improve {dim_name} (current score: {priority_score}/10)"
                )

            if sorted_improvements and len(sorted_improvements) > 1:
                secondary_dim, secondary_score = sorted_improvements[1]
                dim_name2 = WELLNESS_DIMENSIONS.get(secondary_dim, {}).get("name", secondary_dim)
                recommendations.append(
                    f"Priority 2: Work on {dim_name2} (current score: {secondary_score}/10)"
                )

            if sorted_strengths:
                strength_names = [
                    WELLNESS_DIMENSIONS.get(dim, {}).get("name", dim)
                    for dim, _ in sorted_strengths[:2]
                ]
                recommendations.append(f"Leverage your strengths in: {', '.join(strength_names)}")

            # Build wellness score data
            wellness_data = {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "dimensions_scores": dimensions_scores,
                "overall_score": overall_score,
                "wellness_category": wellness_category,
                "strengths": strengths,
                "areas_for_improvement": improvements,
                "recommendations": recommendations,
            }

            # Save to file
            json_content = json.dumps(wellness_data, indent=2)
            today = date.today()
            path = f"wellness_assessments/{user_id}/{today}_overall_wellness_score.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            response_parts = [
                f"Overall Wellness Score",
                "=" * 60,
                f"\n{emoji_level} Overall Wellness: {overall_score}/10",
                f"Category: {wellness_category}",
            ]

            response_parts.append("\n---\nDimension Scores:")
            for dim, score in sorted(dimensions_scores.items(), key=lambda x: -x[1]):
                bar = "█" * score + "░" * (10 - score)
                dim_name = WELLNESS_DIMENSIONS.get(dim, {}).get("name", dim)
                response_parts.append(f"  {dim_name:<25} [{bar}] {score}/10")

            if sorted_strengths:
                response_parts.append("\n✓ Strengths:")
                for dim, score in sorted_strengths:
                    dim_name = WELLNESS_DIMENSIONS.get(dim, {}).get("name", dim)
                    response_parts.append(f"  • {dim_name}: {score}/10")

            if sorted_improvements:
                response_parts.append("\n→ Areas for Improvement:")
                for dim, score in sorted_improvements:
                    dim_name = WELLNESS_DIMENSIONS.get(dim, {}).get("name", dim)
                    response_parts.append(f"  • {dim_name}: {score}/10")

            if recommendations:
                response_parts.append("\n💡 Recommendations:")
                for i, rec in enumerate(recommendations, 1):
                    response_parts.append(f"  {i}. {rec}")

            if overall_score <= 4:
                response_parts.append(
                    "\n⚠️ Note: Low wellness scores may indicate need for professional support. "
                    "Consider consulting with a healthcare provider or mental health professional."
                )

            response_parts.append(f"\nScore saved to: {path}")
            response_parts.append("\nTip: Reassess monthly to track wellness journey progress.")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error calculating wellness score: {str(e)}"

    @tool
    def track_habit_consistency(
        user_id: str,
        habit_name: str,
        completion_history: List[Dict[str, Any]],
    ) -> str:
        """Track habit consistency and calculate adherence metrics.

        This tool analyzes habit completion history to provide insights into
        consistency patterns, streaks, and adherence rates. It helps identify
        what's working well and where improvements are needed.

        Args:
            user_id: The user's unique identifier
            habit_name: Name of the habit to track (e.g., "Morning meditation")
            completion_history: List of daily completions with 'date' and
                               'completed' boolean/status:
                               [{"date": "2024-01-15", "completed": True}, ...]

        Returns:
            Habit consistency analysis with completion rate, current/longest
            streaks, adherence patterns, and improvement suggestions.
            Saved to habit_tracking/{user_id}/

        Raises:
            ValueError: If required parameters are invalid

        Example:
            >>> track_habit_consistency(
            ...     "user_123",
            ...     "10-minute morning walk",
            ...     [
            ...         {"date": "2024-01-15", "completed": True},
            ...         {"date": "2024-01-16", "completed": False},
            ...     ]
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not habit_name or not isinstance(habit_name, str):
            return "Error: habit_name must be a non-empty string"
        if not completion_history or not isinstance(completion_history, list):
            return "Error: completion_history must be a non-empty list"

        try:
            # Parse and sort completion history
            parsed_history = []
            for entry in completion_history:
                if not isinstance(entry, dict) or "date" not in entry:
                    continue

                try:
                    date_obj = datetime.strptime(entry["date"], "%Y-%m-%d")
                    completed = entry.get("completed", False)
                    parsed_history.append({"date": date_obj, "completed": bool(completed)})
                except (ValueError, TypeError):
                    # Skip invalid date entries
                    continue

            if not parsed_history:
                return "Error: No valid date entries found in completion_history"

            # Sort by date
            parsed_history.sort(key=lambda x: x["date"])

            total_days = len(parsed_history)
            completed_days = sum(1 for entry in parsed_history if entry["completed"])
            completion_rate = (completed_days / total_days * 100) if total_days > 0 else 0

            # Calculate streaks
            current_streak = 0
            longest_streak = 0
            temp_streak = 0

            for entry in parsed_history:
                if entry["completed"]:
                    temp_streak += 1
                    longest_streak = max(longest_streak, temp_streak)
                else:
                    if entry == parsed_history[-1]:  # If this is the last entry
                        current_streak = temp_streak
                    else:
                        current_streak = 0
                    temp_streak = 0

            # Update current_streak if the last entry was completed
            if parsed_history and parsed_history[-1]["completed"]:
                current_streak = temp_streak

            # Calculate adherence category
            if completion_rate >= 90:
                adherence_category = "Excellent"
                emoji_adherence = "🌟"
            elif completion_rate >= 75:
                adherence_category = "Good"
                emoji_adherence = "💚"
            elif completion_rate >= 50:
                adherence_category = "Moderate"
                emoji_adherence = "🟡"
            else:
                adherence_category = "Needs Improvement"
                emoji_adherence = "🔴"

            # Analyze patterns
            missed_days = [entry for entry in parsed_history if not entry["completed"]]
            recent_performance = (
                sum(1 for e in parsed_history[-7:] if e["completed"])
                / min(len(parsed_history), 7)
                * 100
                if parsed_history
                else 0
            )

            # Generate insights and recommendations
            insights = []
            if longest_streak >= 21:
                insights.append(
                    f"Great! You've maintained a {longest_streak}-day streak - habit is forming!"
                )
            elif longest_streak >= 7:
                insights.append(f"You've built a {longest_streak}-day streak - keep going!")

            if current_streak >= 7:
                insights.append(f"Currently on a {current_streak}-day streak - momentum is strong!")
            elif current_streak == 0 and parsed_history[-1]["completed"] is False:
                insights.append("Missed yesterday - get back on track today!")

            if recent_performance < completion_rate:
                insights.append("Recent performance has dropped - consider what might have changed")
            elif recent_performance > completion_rate and recent_completion >= 80:
                insights.append("Recent improvement! You're trending in the right direction")

            # Build tracking data
            tracking_data = {
                "user_id": user_id,
                "habit_name": habit_name,
                "timestamp": datetime.now().isoformat(),
                "tracking_period_days": total_days,
                "completed_days": completed_days,
                "missed_days": len(missed_days),
                "completion_rate": round(completion_rate, 1),
                "adherence_category": adherence_category,
                "current_streak": current_streak,
                "longest_streak": longest_streak,
                "recent_performance_7_days": round(recent_performance, 1),
                "insights": insights,
            }

            # Save to file
            json_content = json.dumps(tracking_data, indent=2)
            today = date.today()
            path = (
                f"habit_tracking/{user_id}/{habit_name.replace(' ', '_').lower()}_consistency.json"
            )

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format user-friendly response
            response_parts = [
                f"Habit Consistency Tracker: {habit_name}",
                "=" * 60,
                f"\n{emoji_adherence} Completion Rate: {completion_rate:.1f}% ({completed_days}/{total_days} days)",
                f"Adherence Category: {adherence_category}",
            ]

            response_parts.append("\n---\n📊 Streak Metrics:")
            response_parts.append(f"  Current Streak: {current_streak} day(s)")
            response_parts.append(f"  Longest Streak: {longest_streak} day(s)")
            response_parts.append(f"  Recent (7 days): {recent_performance:.1f}% completion rate")

            if insights:
                response_parts.append("\n---\n💡 Insights:")
                for insight in insights:
                    response_parts.append(f"  • {insight}")

            # Pattern analysis (day of week)
            if len(parsed_history) >= 14:
                day_completion = {}
                for entry in parsed_history:
                    day_name = entry["date"].strftime("%A")
                    if day_name not in day_completion:
                        day_completion[day_name] = {"completed": 0, "total": 0}
                    day_completion[day_name]["total"] += 1
                    if entry["completed"]:
                        day_completion[day_name]["completed"] += 1

                response_parts.append("\n---\n📅 Day-by-Day Patterns:")
                for day in [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday",
                ]:
                    if day in day_completion:
                        stats = day_completion[day]
                        rate = (
                            (stats["completed"] / stats["total"] * 100) if stats["total"] > 0 else 0
                        )
                        bar = "█" * int(rate / 10)
                        response_parts.append(f"  {day:<10} [{bar}] {rate:.0f}%")

            # Recommendations
            response_parts.append("\n---\n✅ Recommendations:")
            if completion_rate < 75:
                response_parts.append(
                    "  • Consider reducing habit size - make it easier to succeed"
                )
            if longest_streak < 7:
                response_parts.append("  • Focus on consistency - never miss twice in a row")
            if current_streak == 0 and parsed_history[-1]["completed"] is False:
                response_parts.append("  • Complete the habit today to restart your streak")
            if completion_rate >= 75:
                response_parts.append(
                    "  • Great work! Consider gradually increasing habit duration"
                )

            response_parts.append(f"\nTracking data saved to: {path}")

            return "\n".join(response_parts)

        except Exception as e:
            return f"Error tracking habit consistency: {str(e)}"

    print("Wellness tools created successfully!")
    return (
        assess_wellness_dimensions,
        create_habit_formation_plan,
        provide_stress_management_techniques,
        create_sleep_optimization_plan,
        design_exercise_program,
        calculate_wellness_score,
        track_habit_consistency,
    )


# Export tools at module level for convenience
__all__ = [
    "create_wellness_tools",
]
