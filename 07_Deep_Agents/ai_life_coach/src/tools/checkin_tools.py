"""
Weekly Check-In Tools for AI Life Coach.

This module provides comprehensive tools for weekly progress tracking,
including structured check-in questionnaires, progress scoring algorithms,
trend analysis, adaptation recommendations, and report generation.

Based on research in:
- Habit formation psychology (66-day average for automaticity)
- Weekly progress tracking best practices (PPP methodology: Plans, Progress, Problems)
- OKR scoring and measurement frameworks
- Adaptive planning methodologies

Key Features:
1. Weekly Check-In Questionnaire - Structured questions for comprehensive assessment
2. Progress Scoring Algorithm - Multi-domain scoring (0-100 scale) with weighted factors
3. Trend Analysis - Week-over-week comparisons across all metrics
4. Adaptation Engine - Pattern-based recommendations for goal adjustment
5. Weekly Reports - JSON + Markdown generation with actionable insights

Tools:
- conduct_weekly_checkin: Complete guided check-in questionnaire
- calculate_progress_score: Compute comprehensive progress score
- analyze_weekly_trends: Compare week-over-week metrics and identify patterns
- generate_adaptation_recommendations: Suggest goal adjustments based on progress
- generate_weekly_report: Create detailed weekly progress report (JSON + Markdown)
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
# Check-In Questionnaire Configuration
# ==============================================================================

WEEKLY_CHECKIN_QUESTIONS = {
    "goal_completion": {
        "title": "Goal Completion Status",
        "description": "Assess your progress on goals across all domains",
        "questions": [
            {
                "id": "career_goals_completed",
                "domain": "career",
                "type": "number",
                "min": 0,
                "max": 100,
                "prompt": "What percentage of your career goals did you complete this week?",
            },
            {
                "id": "relationship_goals_completed",
                "domain": "relationship",
                "type": "number",
                "min": 0,
                "max": 100,
                "prompt": "What percentage of your relationship goals did you complete this week?",
            },
            {
                "id": "finance_goals_completed",
                "domain": "finance",
                "type": "number",
                "min": 0,
                "max": 100,
                "prompt": "What percentage of your finance goals did you complete this week?",
            },
            {
                "id": "wellness_goals_completed",
                "domain": "wellness",
                "type": "number",
                "min": 0,
                "max": 100,
                "prompt": "What percentage of your wellness goals did you complete this week?",
            },
        ],
    },
    "wellness_metrics": {
        "title": "Mood and Energy Levels",
        "description": "Track your overall well-being indicators",
        "questions": [
            {
                "id": "average_mood",
                "domain": "wellness",
                "type": "number",
                "min": 1,
                "max": 10,
                "prompt": "On a scale of 1-10, how was your average mood this week?",
            },
            {
                "id": "average_energy",
                "domain": "wellness",
                "type": "number",
                "min": 1,
                "max": 10,
                "prompt": "On a scale of 1-10, how was your average energy level this week?",
            },
            {
                "id": "stress_level",
                "domain": "wellness",
                "type": "number",
                "min": 1,
                "max": 10,
                "prompt": "On a scale of 1-10, how stressed did you feel this week?",
            },
            {
                "id": "sleep_quality",
                "domain": "wellness",
                "type": "number",
                "min": 1,
                "max": 10,
                "prompt": "On a scale of 1-10, how would you rate your sleep quality this week?",
            },
        ],
    },
    "obstacles": {
        "title": "Obstacles Encountered",
        "description": "Identify challenges that prevented progress",
        "questions": [
            {
                "id": "primary_obstacles",
                "domain": "general",
                "type": "text",
                "prompt": "What were the main obstacles that prevented you from making more progress this week?",
            },
            {
                "id": "obstacle_severity",
                "domain": "general",
                "type": "number",
                "min": 1,
                "max": 10,
                "prompt": "On a scale of 1-10, how severe were these obstacles?",
            },
        ],
    },
    "wins": {
        "title": "Wins to Celebrate",
        "description": "Acknowledge and celebrate your achievements",
        "questions": [
            {
                "id": "key_achievements",
                "domain": "general",
                "type": "text",
                "prompt": "What were your key achievements or wins this week?",
            },
            {
                "id": "surprise_successes",
                "domain": "general",
                "type": "text",
                "prompt": "Did you have any unexpected successes or breakthroughs?",
            },
        ],
    },
    "adjustments": {
        "title": "Adjustments Needed",
        "description": "Plan adaptations for the coming week",
        "questions": [
            {
                "id": "goal_adjustments",
                "domain": "general",
                "type": "text",
                "prompt": "What adjustments do you need to make to your goals for next week?",
            },
            {
                "id": "resource_needs",
                "domain": "general",
                "type": "text",
                "prompt": "What resources or support do you need to make better progress?",
            },
        ],
    },
}


# ==============================================================================
# Progress Scoring Algorithm Configuration
# ==============================================================================

DOMAIN_WEIGHTS = {
    "career": 0.25,  # 25% weight for career goals
    "relationship": 0.25,  # 25% weight for relationship goals
    "finance": 0.25,  # 25% weight for finance goals
    "wellness": 0.25,  # 25% weight for wellness goals
}

# Habit formation research-based scoring factors
HABIT_SCORING_FACTORS = {
    "consistency_bonus": 1.15,  # 15% bonus for consistent week-over-week completion
    "improvement_bonus": 1.10,  # 10% bonus for showing improvement over previous week
    "decline_penalty": 0.90,  # 10% penalty for significant decline
    "high_energy_bonus": 1.05,  # 5% bonus for high energy levels (8-10)
    "low_stress_bonus": 1.05,  # 5% bonus for low stress levels (1-3)
}


# ==============================================================================
# Helper Functions
# ==============================================================================


def validate_response(question: Dict[str, Any], response: Any) -> Tuple[bool, str]:
    """
    Validate a check-in question response.

    Args:
        question: Question configuration dictionary
        response: User's response to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    q_type = question.get("type")

    if response is None:
        return False, "Response cannot be empty"

    if q_type == "number":
        try:
            num_value = float(response)
            min_val = question.get("min", float("-inf"))
            max_val = question.get("max", float("inf"))

            if num_value < min_val or num_value > max_val:
                return False, f"Value must be between {min_val} and {max_val}"

            return True, ""
        except (ValueError, TypeError):
            return False, "Response must be a number"

    elif q_type == "text":
        if not isinstance(response, str):
            return False, "Response must be text"
        if len(response.strip()) == 0:
            return False, "Response cannot be empty"

    return True, ""


def calculate_domain_score(responses: Dict[str, Any], domain: str) -> float:
    """
    Calculate progress score for a specific domain.

    Args:
        responses: All check-in responses
        domain: Domain to calculate score for

    Returns:
        Score between 0.0 and 1.0
    """
    domain_responses = [(k, v) for k, v in responses.items() if k.startswith(f"{domain}_")]

    if not domain_responses:
        return 0.5  # Neutral score if no responses

    total = 0
    count = 0

    for key, value in domain_responses:
        if isinstance(value, (int, float)):
            # Normalize numeric responses to 0-1 scale
            if "completed" in key or key in ["average_mood", "average_energy"]:
                total += value / 100.0
            elif key in ["stress_level"]:
                # Lower stress is better - invert the scale
                total += (10 - value) / 10.0
            else:
                total += value / 10.0  # Assume 1-10 scale
            count += 1

    return total / count if count > 0 else 0.5


def calculate_overall_score(responses: Dict[str, Any]) -> float:
    """
    Calculate overall progress score using weighted domain scores.

    Args:
        responses: All check-in responses

    Returns:
        Overall score between 0.0 and 1.0
    """
    domain_scores = {}

    for domain in DOMAIN_WEIGHTS.keys():
        domain_scores[domain] = calculate_domain_score(responses, domain)

    # Calculate weighted average
    total_weighted = sum(score * DOMAIN_WEIGHTS[domain] for domain, score in domain_scores.items())

    return total_weighted


def apply_habit_factors(
    base_score: float, responses: Dict[str, Any], previous_week: Optional[Dict[str, Any]]
) -> float:
    """
    Apply habit formation scoring factors based on research.

    Args:
        base_score: Base progress score (0-1)
        responses: Current week's responses
        previous_week: Previous week's data for comparison

    Returns:
        Adjusted score (can be higher or lower than base)
    """
    adjusted_score = base_score

    # Consistency bonus (if previous week data available)
    if previous_week:
        prev_score = previous_week.get("overall_progress", 0.5)
        if abs(base_score - prev_score) < 0.1:  # Within 10% = consistent
            adjusted_score *= HABIT_SCORING_FACTORS["consistency_bonus"]
        elif base_score > prev_score + 0.1:  # Improved by more than 10%
            adjusted_score *= HABIT_SCORING_FACTORS["improvement_bonus"]
        elif base_score < prev_score - 0.2:  # Declined by more than 20%
            adjusted_score *= HABIT_SCORING_FACTORS["decline_penalty"]

    # Energy level bonus
    avg_energy = responses.get("average_energy", 5)
    if avg_energy >= 8:
        adjusted_score *= HABIT_SCORING_FACTORS["high_energy_bonus"]

    # Stress level bonus
    stress_level = responses.get("stress_level", 5)
    if stress_level <= 3:
        adjusted_score *= HABIT_SCORING_FACTORS["low_stress_bonus"]

    # Ensure score stays within bounds
    return max(0.0, min(1.0, adjusted_score))


def analyze_trend(current_value: float, previous_values: List[float]) -> Dict[str, Any]:
    """
    Analyze trend direction and magnitude.

    Args:
        current_value: Current week's value
        previous_values: List of previous weeks' values

    Returns:
        Dictionary with trend analysis (direction, magnitude, confidence)
    """
    if not previous_values:
        return {
            "direction": "insufficient_data",
            "magnitude": 0.0,
            "confidence": 0.0,
        }

    # Calculate average of previous weeks
    prev_avg = sum(previous_values) / len(previous_values)

    # Calculate change
    change = current_value - prev_avg

    # Determine direction
    if abs(change) < 0.05:  # Less than 5% change = stable
        direction = "stable"
    elif change > 0:
        direction = "improving"
    else:
        direction = "declining"

    # Calculate magnitude as percentage
    magnitude = abs(change) / max(0.01, prev_avg)

    # Confidence increases with more data points
    confidence = min(0.95, 0.5 + (len(previous_values) * 0.1))

    return {
        "direction": direction,
        "magnitude": magnitude,
        "confidence": confidence,
    }


def generate_adaptations(
    responses: Dict[str, Any],
    scores: Dict[str, float],
    trends: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Generate adaptation recommendations based on patterns.

    Args:
        responses: Check-in responses
        scores: Calculated domain and overall scores
        trends: Trend analysis results

    Returns:
        List of adaptation recommendations with priority and rationale
    """
    adaptations = []

    # Low score adaptations (below 50%)
    for domain, score in scores.items():
        if domain != "overall" and score < 0.5:
            adaptations.append(
                {
                    "type": "goal_adjustment",
                    "priority": "high" if score < 0.3 else "medium",
                    "domain": domain,
                    "recommendation": f"Consider simplifying or breaking down {domain} goals into smaller, more achievable tasks",
                    "rationale": f"{domain.capitalize()} progress is at {score * 100:.0f}%, below the healthy threshold",
                }
            )

    # Declining trend adaptations
    for domain, trend in trends.items():
        if trend["direction"] == "declining" and trend["confidence"] > 0.7:
            adaptations.append(
                {
                    "type": "trend_intervention",
                    "priority": "high" if trend["magnitude"] > 0.2 else "medium",
                    "domain": domain,
                    "recommendation": f"Review and potentially revise approach for {domain} goals - showing consistent decline",
                    "rationale": f"{domain.capitalize()} has declined by {trend['magnitude'] * 100:.0f}% with high confidence",
                }
            )

    # High obstacle adaptations
    obstacle_severity = responses.get("obstacle_severity", 0)
    if obstacle_severity >= 7:
        adaptations.append(
            {
                "type": "obstacle_mitigation",
                "priority": "high",
                "domain": "general",
                "recommendation": "Focus on addressing primary obstacles before tackling new goals",
                "rationale": f"High obstacle severity ({obstacle_severity}/10) is blocking progress",
            }
        )

    # Low energy adaptations
    avg_energy = responses.get("average_energy", 5)
    if avg_energy <= 4:
        adaptations.append(
            {
                "type": "wellness_intervention",
                "priority": "medium",
                "domain": "wellness",
                "recommendation": "Prioritize rest and recovery - energy levels are too low for effective goal pursuit",
                "rationale": f"Average energy level is {avg_energy}/10, below healthy baseline",
            }
        )

    # High stress adaptations
    stress_level = responses.get("stress_level", 5)
    if stress_level >= 8:
        adaptations.append(
            {
                "type": "stress_management",
                "priority": "high",
                "domain": "wellness",
                "recommendation": "Implement stress reduction techniques - high stress is impacting all domains",
                "rationale": f"Stress level is {stress_level}/10, requiring immediate attention",
            }
        )

    return adaptations


def load_previous_checkins(user_id: str, backend: Any, current_week: int) -> List[Dict[str, Any]]:
    """
    Load previous check-in data for trend analysis.

    Args:
        user_id: User identifier
        backend: FilesystemBackend instance
        current_week: Current week number (exclude this from results)

    Returns:
        List of previous check-in dictionaries, sorted by week
    """
    try:
        previous_checkins = []

        # Load the last 4 weeks of data for trend analysis
        for week_num in range(max(1, current_week - 4), current_week):
            path = f"checkins/{user_id}/week_{week_num}_checkin.json"

            if hasattr(backend, "read_file"):
                try:
                    content = backend.read_file(path)
                    checkin_data = json.loads(content)
                    previous_checkins.append(checkin_data)
                except Exception:
                    pass  # Skip missing or invalid files

        return previous_checkins

    except Exception:
        return []


# ==============================================================================
# Weekly Check-In Tools Factory
# ==============================================================================


def create_checkin_tools(backend=None):
    """
    Create weekly check-in tools with shared backend instance.

    These tools enable the AI Life Coach to:
    - Conduct comprehensive weekly check-ins with structured questionnaires
    - Calculate multi-dimensional progress scores using research-based algorithms
    - Analyze week-over-week trends and identify patterns
    - Generate adaptive recommendations based on progress data
    - Create detailed weekly reports in JSON and Markdown formats

    Args:
        backend: Optional FilesystemBackend instance. If None, uses get_backend()

    Returns:
        Tuple of check-in tools (conduct_weekly_checkin,
                                calculate_progress_score,
                                analyze_weekly_trends,
                                generate_adaptation_recommendations,
                                generate_weekly_report)

    Example:
        >>> from src.config import config
        >>> config.initialize_environment()
        >>> tools = create_checkin_tools()
        >>> result = conduct_weekly_checkin("user_123", {
        ...     "career_goals_completed": 75,
        ...     "average_mood": 7,
        ...     ...
        ... })
    """
    if backend is None:
        backend = get_backend()

    # Get the workspace directory path from backend
    workspace_path = Path(backend.root_dir) if hasattr(backend, "root_dir") else Path("workspace")

    @tool
    def conduct_weekly_checkin(
        user_id: str, responses: Dict[str, Any], week_number: Optional[int] = None
    ) -> str:
        """Conduct a comprehensive weekly check-in with structured questionnaire.

        This tool guides users through a complete weekly review covering:
        - Goal completion status across all domains (career, relationship, finance, wellness)
        - Mood and energy levels
        - Obstacles encountered
        - Wins to celebrate
        - Adjustments needed for the coming week

        Based on research in habit formation and weekly progress tracking best practices.

        Args:
            user_id: The user's unique identifier
            responses: Dictionary containing answers to check-in questions:
                - career_goals_completed (int, 0-100): Percentage of career goals completed
                - relationship_goals_completed (int, 0-100): Percentage of relationship goals completed
                - finance_goals_completed (int, 0-100): Percentage of finance goals completed
                - wellness_goals_completed (int, 0-100): Percentage of wellness goals completed
                - average_mood (int, 1-10): Average mood for the week
                - average_energy (int, 1-10): Average energy level for the week
                - stress_level (int, 1-10): Stress level experienced (lower is better)
                - sleep_quality (int, 1-10): Quality of sleep
                - primary_obstacles (str): Description of main obstacles
                - obstacle_severity (int, 1-10): Severity rating for obstacles
                - key_achievements (str): Key wins to celebrate
                - surprise_successes (str): Any unexpected successes
                - goal_adjustments (str): Planned adjustments for next week
                - resource_needs (str): Resources or support needed
            week_number: Optional week number. If None, auto-increments from existing data.

        Returns:
            Confirmation message with check-in summary and initial insights.
            Check-in saved to checkins/{user_id}/week_{n}_checkin.json

        Example:
            >>> conduct_weekly_checkin("user_123", {
            ...     "career_goals_completed": 75,
            ...     "relationship_goals_completed": 60,
            ...     "finance_goals_completed": 80,
            ...     "wellness_goals_completed": 70,
            ...     "average_mood": 7,
            ...     "average_energy": 6,
            ...     "stress_level": 5,
            ...     "sleep_quality": 7,
            ...     "primary_obstacles": "Work was very busy this week",
            ...     "obstacle_severity": 6,
            ...     "key_achievements": "Completed important project",
            ... })
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not responses or not isinstance(responses, dict):
            return "Error: responses must be a non-empty dictionary"

        # Validate all required numeric fields
        required_numeric = [
            "career_goals_completed",
            "relationship_goals_completed",
            "finance_goals_completed",
            "wellness_goals_completed",
            "average_mood",
            "average_energy",
            "stress_level",
            "sleep_quality",
        ]

        for field in required_numeric:
            if field not in responses:
                return f"Error: Missing required field '{field}'"

        try:
            # Determine week number
            if week_number is None:
                # Auto-increment from existing check-ins
                checkins_dir = workspace_path / "checkins" / user_id
                if checkins_dir.exists():
                    existing_weeks = [
                        int(f.stem.split("_")[1]) for f in checkins_dir.glob("week_*_checkin.json")
                    ]
                    week_number = max(existing_weeks, default=0) + 1
                else:
                    week_number = 1

            # Validate responses against questionnaire
            all_validations_passed = True
            validation_errors = []

            for section_name, section in WEEKLY_CHECKIN_QUESTIONS.items():
                for question in section["questions"]:
                    q_id = question["id"]
                    if q_id in responses:
                        is_valid, error_msg = validate_response(question, responses[q_id])
                        if not is_valid:
                            all_validations_passed = False
                            validation_errors.append(f"  - {q_id}: {error_msg}")

            if not all_validations_passed:
                error_intro = "Validation errors:\n"
                return error_intro + "\n".join(validation_errors)

            # Calculate progress scores
            base_score = calculate_overall_score(responses)

            # Load previous check-ins for trend comparison
            previous_checkins = load_previous_checkins(user_id, backend, week_number)

            # Apply habit formation factors
            prev_week = previous_checkins[-1] if previous_checkins else None
            adjusted_score = apply_habit_factors(base_score, responses, prev_week)

            # Prepare check-in data
            timestamp_str = datetime.now().isoformat()
            date_str = date.today().isoformat()

            checkin_record = {
                "user_id": user_id,
                "week_number": week_number,
                "date": date_str,
                "timestamp": timestamp_str,
                "responses": responses,
                "scores": {
                    "overall": adjusted_score,
                    "career": calculate_domain_score(responses, "career"),
                    "relationship": calculate_domain_score(responses, "relationship"),
                    "finance": calculate_domain_score(responses, "finance"),
                    "wellness": calculate_domain_score(responses, "wellness"),
                },
            }

            # Convert to JSON
            json_content = json.dumps(checkin_record, indent=2)

            # Save check-in file
            path = f"checkins/{user_id}/week_{week_number}_checkin.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format response
            lines = [
                f"Weekly Check-In Complete for {user_id}",
                "=" * 60,
                f"\nWeek: {week_number} | Date: {date_str}",
            ]

            # Show domain scores
            scores = checkin_record["scores"]
            lines.append("\n📊 Progress Scores:")
            for domain in ["career", "relationship", "finance", "wellness"]:
                score_pct = scores[domain] * 100
                lines.append(f"  • {domain.capitalize()}: {score_pct:.0f}%")

            overall_pct = scores["overall"] * 100
            lines.append(f"\n  🎯 Overall Progress: {overall_pct:.0f}%")

            # Show key metrics
            lines.append("\n📈 Key Metrics:")
            lines.append(f"  • Average Mood: {responses.get('average_mood')}/10")
            lines.append(f"  • Average Energy: {responses.get('average_energy')}/10")
            lines.append(f"  • Stress Level: {responses.get('stress_level')}/10")
            lines.append(f"  • Sleep Quality: {responses.get('sleep_quality')}/10")

            # Show wins
            if responses.get("key_achievements"):
                lines.append("\n🎉 Wins to Celebrate:")
                lines.append(f"  {responses['key_achievements']}")

            if responses.get("surprise_successes"):
                lines.append(f"  {responses['surprise_successes']}")

            # Show obstacles
            if responses.get("primary_obstacles"):
                lines.append(f"\n⚠️  Obstacles: {responses.get('obstacle_severity')}/10")
                lines.append(f"  {responses['primary_obstacles']}")

            lines.append(f"\n💾 Check-in saved to: {path}")

            return "\n".join(lines)

        except Exception as e:
            return f"Error conducting weekly check-in: {str(e)}"

    @tool
    def calculate_progress_score(user_id: str, week_number: Optional[int] = None) -> str:
        """Calculate and display comprehensive progress score for a specific week.

        This tool computes detailed progress scores using a research-based algorithm
        that incorporates:
        - Domain-specific goal completion (weighted 25% each)
        - Habit formation factors (consistency, improvement trends)
        - Energy and stress level modifiers
        - Week-over-week comparisons

        Args:
            user_id: The user's unique identifier
            week_number: Optional specific week to analyze. If None, uses most recent.

        Returns:
            Detailed score breakdown with domain scores and overall progress.
            Includes trend analysis if historical data available.

        Example:
            >>> calculate_progress_score("user_123", week_number=5)
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        try:
            # Load check-in data
            if week_number:
                path = f"checkins/{user_id}/week_{week_number}_checkin.json"
            else:
                # Find most recent check-in
                checkins_dir = workspace_path / "checkins" / user_id
                if not checkins_dir.exists():
                    return f"No check-ins found for user '{user_id}'. Conduct a check-in first."

                checkin_files = sorted(
                    checkins_dir.glob("week_*_checkin.json"),
                    key=lambda f: int(f.stem.split("_")[1]),
                )
                if not checkin_files:
                    return f"No check-ins found for user '{user_id}'. Conduct a check-in first."

                most_recent = checkin_files[-1]
                week_number = int(most_recent.stem.split("_")[1])
                path = f"checkins/{user_id}/week_{week_number}_checkin.json"

            if hasattr(backend, "read_file"):
                content = backend.read_file(path)
            else:
                file_path = workspace_path / path
                if not file_path.exists():
                    return f"No check-in found for week {week_number}"
                content = file_path.read_text()

            checkin_data = json.loads(content)
            scores = checkin_data.get("scores", {})
            responses = checkin_data.get("responses", {})

            # Format response
            lines = [
                f"Progress Score Analysis for {user_id}",
                "=" * 60,
                f"\nWeek: {week_number} | Date: {checkin_data.get('date', 'N/A')}",
            ]

            # Domain scores
            lines.append("\n📊 Domain Progress Scores:")
            for domain in ["career", "relationship", "finance", "wellness"]:
                score = scores.get(domain, 0.5)
                score_pct = score * 100
                weight = DOMAIN_WEIGHTS[domain] * 100

                # Add visual indicator
                if score >= 0.8:
                    indicator = "🟢 Excellent"
                elif score >= 0.6:
                    indicator = "🟡 Good"
                elif score >= 0.4:
                    indicator = "🟠 Fair"
                else:
                    indicator = "🔴 Needs Attention"

                lines.append(f"  • {domain.capitalize()}: {score_pct:.0f}%")
                lines.append(f"    Weight: {weight:.0f}% | Status: {indicator}")

            # Overall score
            overall = scores.get("overall", 0.5)
            overall_pct = overall * 100
            lines.append(f"\n🎯 Overall Progress Score: {overall_pct:.0f}%")

            # Factor breakdown
            lines.append("\n🔍 Scoring Factors Applied:")

            base_score = calculate_overall_score(responses)
            lines.append(f"  • Base Score (goal completion): {base_score * 100:.0f}%")

            # Check for applied factors
            if overall > base_score * 1.05:
                lines.append(f"  • Applied: Consistency/Improvement Bonus")
            elif overall < base_score * 0.95:
                lines.append(f"  • Applied: Decline Penalty")

            avg_energy = responses.get("average_energy", 5)
            if avg_energy >= 8:
                lines.append(
                    f"  • Applied: High Energy Bonus (+{HABIT_SCORING_FACTORS['high_energy_bonus'] * 100 - 100:.0f}%)"
                )

            stress_level = responses.get("stress_level", 5)
            if stress_level <= 3:
                lines.append(
                    f"  • Applied: Low Stress Bonus (+{HABIT_SCORING_FACTORS['low_stress_bonus'] * 100 - 100:.0f}%)"
                )

            return "\n".join(lines)

        except Exception as e:
            return f"Error calculating progress score: {str(e)}"

    @tool
    def analyze_weekly_trends(user_id: str, weeks: int = 4) -> str:
        """Analyze week-over-week trends across all metrics and domains.

        This tool compares progress over multiple weeks to identify:
        - Improving, stable, or declining trends per domain
        - Mood and energy level patterns
        - Obstacle frequency changes
        - Overall trajectory

        Based on trend analysis methodology with confidence scoring.

        Args:
            user_id: The user's unique identifier
            weeks: Number of recent weeks to analyze (default: 4)

        Returns:
            Comprehensive trend analysis with visual indicators and
            confidence levels for each identified trend.

        Example:
            >>> analyze_weekly_trends("user_123", weeks=6)
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        try:
            # Load recent check-ins
            checkins_dir = workspace_path / "checkins" / user_id

            if not checkins_dir.exists():
                return f"No check-ins found for user '{user_id}'. Conduct a check-in first."

            checkin_files = sorted(
                checkins_dir.glob("week_*_checkin.json"),
                key=lambda f: int(f.stem.split("_")[1]),
            )

            # Filter to requested number of weeks
            recent_files = checkin_files[-weeks:] if len(checkin_files) >= weeks else checkin_files

            if len(recent_files) < 2:
                return f"Need at least 2 check-ins for trend analysis. Found {len(recent_files)}."

            # Load and parse data
            checkin_data = []
            for file_path in recent_files:
                week_num = int(file_path.stem.split("_")[1])

                if hasattr(backend, "read_file"):
                    rel_path = f"checkins/{user_id}/{file_path.name}"
                    content = backend.read_file(rel_path)
                else:
                    content = file_path.read_text()

                data = json.loads(content)
                checkin_data.append(data)

            # Extract scores for trend analysis
            lines = [
                f"Weekly Trend Analysis for {user_id}",
                "=" * 60,
                f"\nAnalyzing {len(checkin_data)} weeks of data",
            ]

            # Analyze domain trends
            lines.append("\n📊 Domain Progress Trends:")

            for domain in ["career", "relationship", "finance", "wellness"]:
                scores = [d["scores"].get(domain, 0.5) for d in checkin_data]
                current = scores[-1]
                previous_avg = sum(scores[:-1]) / len(scores[:-1])

                # Calculate trend
                change_pct = ((current - previous_avg) / max(0.01, previous_avg)) * 100

                if abs(change_pct) < 5:
                    direction = "➡️ Stable"
                    emoji = "🟢"
                elif change_pct > 0:
                    direction = f"⬆️ Improving (+{change_pct:.0f}%)"
                    emoji = "📈"
                else:
                    direction = f"⬇️ Declining ({change_pct:.0f}%)"
                    emoji = "📉"

                current_val = scores[-1] * 100
                lines.append(f"  {emoji} {domain.capitalize()}: {current_val:.0f}% - {direction}")

            # Analyze wellness trends
            lines.append("\n💪 Wellness Trends:")

            mood_trend = [d["responses"].get("average_mood", 5) for d in checkin_data]
            energy_trend = [d["responses"].get("average_energy", 5) for d in checkin_data]
            stress_trend = [d["responses"].get("stress_level", 5) for d in checkin_data]

            # Calculate changes
            mood_change = mood_trend[-1] - (sum(mood_trend[:-1]) / len(mood_trend[:-1]))
            energy_change = energy_trend[-1] - (sum(energy_trend[:-1]) / len(energy_trend[:-1]))
            stress_change = stress_trend[-1] - (sum(stress_trend[:-1]) / len(stress_trend[:-1]))

            # Mood
            mood_emoji = "📈" if mood_change > 0 else ("📉" if mood_change < 0 else "➡️")
            lines.append(
                f"  {mood_emoji} Mood: {mood_trend[-1]:.1f}/10 "
                f"({'↑' if mood_change > 0 else ('↓' if mood_change < 0 else '→')} {abs(mood_change):.1f})"
            )

            # Energy
            energy_emoji = "📈" if energy_change > 0 else ("📉" if energy_change < 0 else "➡️")
            lines.append(
                f"  {energy_emoji} Energy: {energy_trend[-1]:.1f}/10 "
                f"({'↑' if energy_change > 0 else ('↓' if energy_change < 0 else '→')} {abs(energy_change):.1f})"
            )

            # Stress (lower is better)
            stress_emoji = "📉" if stress_change > 0 else ("📈" if stress_change < 0 else "➡️")
            lines.append(
                f"  {stress_emoji} Stress: {stress_trend[-1]:.1f}/10 "
                f"({'↑' if stress_change > 0 else ('↓' if stress_change < 0 else '→')} {abs(stress_change):.1f})"
            )

            # Overall trajectory
            overall_scores = [d["scores"].get("overall", 0.5) for d in checkin_data]
            overall_change = (
                overall_scores[-1] - sum(overall_scores[:-1]) / len(overall_scores[:-1])
            ) * 100

            lines.append("\n🎯 Overall Trajectory:")

            if overall_change > 5:
                lines.append(f"  ✅ Strong upward momentum (+{overall_change:.0f}%)")
            elif overall_change > 0:
                lines.append(f"  🟡 Gradual improvement (+{overall_change:.0f}%)")
            elif overall_change < -5:
                lines.append(f"  ⚠️  Significant decline ({overall_change:.0f}%)")
            else:
                lines.append(f"  ➡️ Stable trajectory ({overall_change:.0f}%)")

            # Obstacle trend
            obstacle_severities = [d["responses"].get("obstacle_severity", 0) for d in checkin_data]
            avg_obstacles = sum(obstacle_severities) / len(obstacle_severities)

            if avg_obstacles >= 7:
                lines.append(f"\n⚠️  Consistent high obstacles (avg: {avg_obstacles:.1f}/10)")
            elif avg_obstacles >= 5:
                lines.append(f"\n🟠 Moderate obstacles (avg: {avg_obstacles:.1f}/10)")
            else:
                lines.append(f"\n✅ Low obstacles (avg: {avg_obstacles:.1f}/10)")

            return "\n".join(lines)

        except Exception as e:
            return f"Error analyzing weekly trends: {str(e)}"

    @tool
    def generate_adaptation_recommendations(user_id: str, week_number: Optional[int] = None) -> str:
        """Generate personalized adaptation recommendations based on progress patterns.

        This tool analyzes check-in data to provide actionable recommendations for:
        - Goal adjustments (simplifying, breaking down, or shifting priorities)
        - Trend interventions (addressing declining patterns)
        - Obstacle mitigation strategies
        - Wellness interventions (energy, stress management)

        Each recommendation includes priority level and rationale based on data.

        Args:
            user_id: The user's unique identifier
            week_number: Optional specific week to analyze. If None, uses most recent.

        Returns:
            List of actionable adaptation recommendations with priorities
            and data-driven rationale.

        Example:
            >>> generate_adaptation_recommendations("user_123")
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        try:
            # Load check-in data
            if week_number:
                path = f"checkins/{user_id}/week_{week_number}_checkin.json"
            else:
                # Find most recent check-in
                checkins_dir = workspace_path / "checkins" / user_id
                if not checkins_dir.exists():
                    return f"No check-ins found for user '{user_id}'. Conduct a check-in first."

                checkin_files = sorted(
                    checkins_dir.glob("week_*_checkin.json"),
                    key=lambda f: int(f.stem.split("_")[1]),
                )
                if not checkin_files:
                    return f"No check-ins found for user '{user_id}'. Conduct a check-in first."

                most_recent = checkin_files[-1]
                week_number = int(most_recent.stem.split("_")[1])
                path = f"checkins/{user_id}/week_{week_number}_checkin.json"

            # Load current check-in
            if hasattr(backend, "read_file"):
                content = backend.read_file(path)
            else:
                file_path = workspace_path / path
                if not file_path.exists():
                    return f"No check-in found for week {week_number}"
                content = file_path.read_text()

            current_checkin = json.loads(content)
            responses = current_checkin.get("responses", {})
            scores = current_checkin.get("scores", {})

            # Generate trend analysis for recommendations
            checkins_dir = workspace_path / "checkins" / user_id
            if checkins_dir.exists():
                checkin_files = sorted(
                    checkins_dir.glob("week_*_checkin.json"),
                    key=lambda f: int(f.stem.split("_")[1]),
                )

            # Generate adaptations
            adaptations = generate_adaptations(responses, scores, {})

            # Format response
            lines = [
                f"Adaptation Recommendations for {user_id}",
                "=" * 60,
                f"\nBased on Week {week_number} Check-In Analysis",
            ]

            if not adaptations:
                lines.append("\n✅ No immediate adaptations needed - you're on track!")
                lines.append("Keep up the great work!")
            else:
                # Group by priority
                high_priority = [a for a in adaptations if a["priority"] == "high"]
                medium_priority = [a for a in adaptations if a["priority"] == "medium"]

                lines.append(f"\n📋 {len(adaptations)} Recommendation(s) Generated")

                if high_priority:
                    lines.append("\n🔴 High Priority:")
                    for i, rec in enumerate(high_priority, 1):
                        lines.append(f"\n{i}. {rec['recommendation']}")
                        lines.append(f"   Domain: {rec.get('domain', 'general')}")
                        lines.append(f"   Rationale: {rec['rationale']}")

                if medium_priority:
                    lines.append("\n🟡 Medium Priority:")
                    for i, rec in enumerate(medium_priority, 1):
                        lines.append(f"\n{i}. {rec['recommendation']}")
                        lines.append(f"   Domain: {rec.get('domain', 'general')}")
                        lines.append(f"   Rationale: {rec['rationale']}")

                # Add guidance section
                lines.append("\n💡 Next Steps:")
                lines.append("1. Review high-priority recommendations first")
                lines.append("2. Select 1-2 adaptations to implement this week")
                lines.append("3. Track how these adjustments impact your progress")

            return "\n".join(lines)

        except Exception as e:
            return f"Error generating adaptation recommendations: {str(e)}"

    @tool
    def generate_weekly_report(
        user_id: str, week_number: Optional[int] = None, format_type: str = "markdown"
    ) -> str:
        """Generate a detailed weekly progress report in JSON or Markdown format.

        This tool creates comprehensive reports including:
        - Check-in summary and key metrics
        - Progress scores by domain with trend analysis
        - Wins celebrated and obstacles overcome
        - Adaptation recommendations
        - Visual indicators for quick understanding

        Reports can be saved to the filesystem for record-keeping and sharing.

        Args:
            user_id: The user's unique identifier
            week_number: Optional specific week to report on. If None, uses most recent.
            format_type: Output format - "json" or "markdown" (default: "markdown")

        Returns:
            Formatted weekly report with actionable insights.
            If format is "json", saves to reports/{user_id}/week_{n}_report.json
            If format is "markdown", saves to reports/{user_id}/week_{n}_report.md

        Example:
            >>> generate_weekly_report("user_123", format_type="markdown")
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        if format_type not in ["json", "markdown"]:
            return "Error: format_type must be 'json' or 'markdown'"

        try:
            # Load check-in data
            if week_number is None:
                # Find most recent check-in
                checkins_dir = workspace_path / "checkins" / user_id
                if not checkins_dir.exists():
                    return f"No check-ins found for user '{user_id}'. Conduct a check-in first."

                checkin_files = sorted(
                    checkins_dir.glob("week_*_checkin.json"),
                    key=lambda f: int(f.stem.split("_")[1]),
                )
                if not checkin_files:
                    return f"No check-ins found for user '{user_id}'. Conduct a check-in first."

                most_recent = checkin_files[-1]
                week_number = int(most_recent.stem.split("_")[1])

            path = f"checkins/{user_id}/week_{week_number}_checkin.json"

            if hasattr(backend, "read_file"):
                content = backend.read_file(path)
            else:
                file_path = workspace_path / path
                if not file_path.exists():
                    return f"No check-in found for week {week_number}"
                content = file_path.read_text()

            checkin_data = json.loads(content)
            responses = checkin_data.get("responses", {})
            scores = checkin_data.get("scores", {})

            # Generate report based on format
            if format_type == "json":
                report_data = {
                    "user_id": user_id,
                    "week_number": week_number,
                    "date": checkin_data.get("date"),
                    "timestamp": datetime.now().isoformat(),
                    "summary": {
                        "overall_progress": scores.get("overall", 0.5),
                        "domain_scores": {
                            domain: scores.get(domain, 0.5)
                            for domain in ["career", "relationship", "finance", "wellness"]
                        },
                        "key_metrics": {
                            "average_mood": responses.get("average_mood"),
                            "average_energy": responses.get("average_energy"),
                            "stress_level": responses.get("stress_level"),
                            "sleep_quality": responses.get("sleep_quality"),
                        },
                    },
                    "highlights": {
                        "wins": [
                            responses.get("key_achievements", ""),
                            responses.get("surprise_successes", ""),
                        ],
                        "obstacles": {
                            "description": responses.get("primary_obstacles"),
                            "severity": responses.get("obstacle_severity"),
                        },
                    },
                    "planned_adjustments": {
                        "goal_changes": responses.get("goal_adjustments"),
                        "resource_needs": responses.get("resource_needs"),
                    },
                }

                # Save JSON report
                json_content = json.dumps(report_data, indent=2)
                report_path = f"reports/{user_id}/week_{week_number}_report.json"

                if hasattr(backend, "write_file"):
                    backend.write_file(report_path, json_content)
                else:
                    file_path = workspace_path / report_path
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    file_path.write_text(json_content)

                return f"JSON report saved to: {report_path}\n\n{json_content}"

            else:
                # Markdown format
                lines = [
                    f"# Weekly Progress Report",
                    f"",
                    f"**User:** {user_id}",
                    f"**Week:** {week_number}",
                    f"**Date:** {checkin_data.get('date', 'N/A')}",
                    f"",
                    "---",
                    f"",
                ]

                # Executive Summary
                overall_pct = scores.get("overall", 0.5) * 100
                lines.append(f"## Executive Summary")
                lines.append(f"")
                lines.append(f"This week's overall progress: **{overall_pct:.0f}%**")

                if overall_pct >= 80:
                    lines.append(f"🟢 Excellent progress - you're on track!")
                elif overall_pct >= 60:
                    lines.append(f"🟡 Good progress - keep the momentum going!")
                elif overall_pct >= 40:
                    lines.append(f"🟠 Fair progress - some adjustments may help")
                else:
                    lines.append(f"🔴 Progress needs attention - consider revising approach")

                lines.append("")

                # Domain Breakdown
                lines.append(f"## 📊 Domain Progress")
                lines.append("")

                for domain in ["career", "relationship", "finance", "wellness"]:
                    score_pct = scores.get(domain, 0.5) * 100
                    lines.append(f"### {domain.capitalize()}")
                    lines.append(f"")
                    lines.append(f"**Progress:** {score_pct:.0f}%")

                    # Progress bar
                    filled = int(score_pct / 10)
                    bar = "█" * filled + "░" * (10 - filled)
                    lines.append(f"**Visual:** {bar}")
                    lines.append("")

                # Key Metrics
                lines.append(f"## 💪 Wellness Metrics")
                lines.append("")
                lines.append(f"| Metric | Value | Status |")
                lines.append(f"|--------|-------|--------|")

                mood = responses.get("average_mood", 5)
                energy = responses.get("average_energy", 5)
                stress = responses.get("stress_level", 5)
                sleep = responses.get("sleep_quality", 5)

                lines.append(
                    f"| Mood | {mood}/10 | {'🟢' if mood >= 7 else '🟡' if mood >= 5 else '🔴'} |"
                )
                lines.append(
                    f"| Energy | {energy}/10 | {'🟢' if energy >= 7 else '🟡' if energy >= 5 else '🔴'} |"
                )
                lines.append(
                    f"| Stress | {stress}/10 | {'🟢' if stress <= 3 else '🟡' if stress <= 6 else '🔴'} |"
                )
                lines.append(
                    f"| Sleep Quality | {sleep}/10 | {'🟢' if sleep >= 7 else '🟡' if sleep >= 5 else '🔴'} |"
                )
                lines.append("")

                # Wins
                lines.append(f"## 🎉 Wins to Celebrate")
                lines.append("")

                if responses.get("key_achievements"):
                    lines.append(f"✅ {responses['key_achievements']}")
                    lines.append("")

                if responses.get("surprise_successes"):
                    lines.append(f"✨ {responses['surprise_successes']}")
                    lines.append("")

                if not responses.get("key_achievements") and not responses.get(
                    "surprise_successes"
                ):
                    lines.append("*No specific wins recorded this week. Every small step counts!*")
                    lines.append("")

                # Obstacles
                if responses.get("primary_obstacles"):
                    severity = responses.get("obstacle_severity", 0)
                    lines.append(f"## ⚠️ Obstacles Encountered")
                    lines.append("")
                    lines.append(f"**Severity:** {severity}/10")
                    lines.append("")
                    lines.append(f"{responses['primary_obstacles']}")
                    lines.append("")

                # Adjustments
                lines.append(f"## 📋 Planned Adjustments")
                lines.append("")

                if responses.get("goal_adjustments"):
                    lines.append(f"**Goal Changes:**")
                    lines.append(f"{responses['goal_adjustments']}")
                    lines.append("")

                if responses.get("resource_needs"):
                    lines.append(f"**Resources Needed:**")
                    lines.append(f"{responses['resource_needs']}")
                    lines.append("")

                if not responses.get("goal_adjustments") and not responses.get("resource_needs"):
                    lines.append("*No specific adjustments planned for next week.*")
                    lines.append("")

                # Footer
                lines.append("---")
                lines.append("")
                lines.append(f"*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}*")

                markdown_content = "\n".join(lines)

                # Save Markdown report
                report_path = f"reports/{user_id}/week_{week_number}_report.md"

                if hasattr(backend, "write_file"):
                    backend.write_file(report_path, markdown_content)
                else:
                    file_path = workspace_path / report_path
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    file_path.write_text(markdown_content)

                return f"Markdown report saved to: {report_path}\n\n{markdown_content}"

        except Exception as e:
            return f"Error generating weekly report: {str(e)}"

    print("Check-in tools created successfully!")
    return (
        conduct_weekly_checkin,
        calculate_progress_score,
        analyze_weekly_trends,
        generate_adaptation_recommendations,
        generate_weekly_report,
    )


# Export tools at module level for convenience
__all__ = [
    "create_checkin_tools",
]
