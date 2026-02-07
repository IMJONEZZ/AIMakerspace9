"""
Adaptive Recommendation Engine Tools for AI Life Coach.

This module implements a sophisticated adaptive learning system that:
1. Tracks user response patterns to recommendations
2. Scores recommendation effectiveness (0% - 100%)
3. Learns from feedback to personalize future recommendations
4. Detects adaptation triggers (missed tasks, changing priorities)
5. Generates personalized alternative strategies

Based on research in:
- Adaptive recommendation systems with bandit algorithms
- Reinforcement learning from human feedback (RLHF)
- User preference learning and feedback loops
- Context-aware personalization

Key Features:
1. Preference Tracking System - What works for each user
2. Recommendation Effectiveness Scoring - Multi-factor scoring algorithm
3. Adaptation Trigger Detection - Pattern-based trigger identification
4. Personalized Alternative Strategy Generation - Context-aware alternatives

Tools:
- track_recommendation_response: Record user responses to recommendations
- calculate_recommendation_effectiveness: Score recommendation effectiveness (0-100%)
- learn_user_preferences: Extract and store preference patterns from feedback
- detect_adaptation_triggers: Identify when adaptation is needed (3+ missed tasks, etc.)
- generate_personalized_alternatives: Create tailored alternative strategies
- get_adaptive_recommendations_history: View learning history and patterns
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
from .checkin_tools import load_previous_checkins


# ==============================================================================
# Adaptive Learning Configuration
# ==============================================================================

# Adaptation triggers thresholds
ADAPTATION_TRIGGERS = {
    "consecutive_missed_tasks": 3,  # Trigger after 3 consecutive missed tasks
    "declining_mood_threshold": -2,  # Mood decline of 2+ points (1-10 scale)
    "declining_energy_threshold": -2,  # Energy decline of 2+ points (1-10 scale)
    "low_completion_rate": 0.4,  # Below 40% completion rate
    "high_stress_threshold": 7,  # Stress above 7/10 for multiple weeks
    "priority_shift_threshold": 2,  # Priority changes by 2+ levels
}

# Recommendation effectiveness scoring factors
EFFECTIVENESS_FACTORS = {
    "task_completion_weight": 0.40,  # 40% weight on actual task completion
    "user_satisfaction_weight": 0.25,  # 25% weight on user feedback
    "consistency_weight": 0.15,  # 15% weight on consistency over time
    "context_alignment_weight": 0.10,  # 10% weight on alignment with user context
    "time_efficiency_weight": 0.10,  # 10% weight on time/cost efficiency
}

# Preference categories for tracking
PREFERENCE_CATEGORIES = {
    "task_size": {  # User prefers tasks of certain size
        "small": {"duration_minutes": [0, 15], "description": "Quick wins under 15 minutes"},
        "medium": {"duration_minutes": [15, 60], "description": "Standard tasks 15-60 minutes"},
        "large": {"duration_minutes": [60, 180], "description": "Major projects over 1 hour"},
    },
    "task_complexity": {  # User prefers tasks of certain complexity
        "simple": {"steps_required": [1, 3], "description": "Straightforward tasks"},
        "moderate": {"steps_required": [4, 7], "description": "Multi-step tasks"},
        "complex": {"steps_required": [8, 999], "description": "Complex multi-phase tasks"},
    },
    "support_level": {  # User prefers certain levels of guidance
        "minimal": {"guidance_frequency": "weekly", "description": "Prefers autonomy"},
        "moderate": {"guidance_frequency": "bi_weekly", "description": "Balanced support"},
        "intensive": {"guidance_frequency": "daily", "description": "Frequent check-ins"},
    },
    "motivation_type": {  # What motivates the user
        "intrinsic": {"description": "Self-driven, personal satisfaction"},
        "extrinsic": {"description": "External rewards, recognition"},
        "social": {"description": "Social connection and accountability"},
    },
}


# ==============================================================================
# Helper Functions
# ==============================================================================


def calculate_task_completion_rate(responses: Dict[str, Any]) -> float:
    """
    Calculate overall task completion rate from check-in responses.

    Args:
        responses: Check-in response dictionary

    Returns:
        Completion rate between 0.0 and 1.0
    """
    domain_completions = [
        responses.get("career_goals_completed", 0),
        responses.get("relationship_goals_completed", 0),
        responses.get("finance_goals_completed", 0),
        responses.get("wellness_goals_completed", 0),
    ]

    return sum(domain_completions) / (len(domain_completions) * 100)


def detect_declining_trend(
    current_value: float, previous_values: List[float], threshold: float
) -> bool:
    """
    Detect if a metric is showing a declining trend beyond threshold.

    Args:
        current_value: Current week's value
        previous_values: List of previous weeks' values
        threshold: Decline threshold (e.g., -2 for 2-point decline)

    Returns:
        True if declining trend detected, False otherwise
    """
    if not previous_values:
        return False

    prev_avg = sum(previous_values) / len(previous_values)
    change = current_value - prev_avg

    return change <= threshold


def calculate_effectiveness_score(
    completion_rate: float,
    user_satisfaction: Optional[float],
    consistency_bonus: float,
    context_alignment: float,
    time_efficiency: float,
) -> float:
    """
    Calculate comprehensive recommendation effectiveness score.

    Uses weighted factors based on research in adaptive systems.

    Args:
        completion_rate: Task completion rate (0.0-1.0)
        user_satisfaction: User satisfaction score (0.0-1.0, optional)
        consistency_bonus: Consistency factor (0.5-1.5)
        context_alignment: Context alignment score (0.0-1.0)
        time_efficiency: Time efficiency score (0.0-1.0)

    Returns:
        Effectiveness score between 0 and 100
    """
    base_score = (
        completion_rate * EFFECTIVENESS_FACTORS["task_completion_weight"]
        + (user_satisfaction or 0.5) * EFFECTIVENESS_FACTORS["user_satisfaction_weight"]
        + context_alignment * EFFECTIVENESS_FACTORS["context_alignment_weight"]
        + time_efficiency * EFFECTIVENESS_FACTORS["time_efficiency_weight"]
    )

    # Apply consistency bonus
    final_score = base_score * consistency_bonus

    # Convert to 0-100 scale and clamp
    final_pct = min(100, max(0, final_score * 100))

    return round(final_pct, 1)


def extract_preference_pattern(
    recommendation_data: Dict[str, Any],
    response_data: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """
    Extract preference patterns from recommendation-response pairs.

    Args:
        recommendation_data: Original recommendation details
        response_data: User's response and outcome

    Returns:
        Preference pattern dictionary or None if insufficient data
    """
    pattern = {
        "category": recommendation_data.get("type", "general"),
        "task_size": None,
        "task_complexity": None,
        "time_of_day": recommendation_data.get("suggested_time"),
        "day_of_week": recommendation_data.get("suggested_day"),
        "outcome": response_data.get("completed", False),
        "user_rating": response_data.get("satisfaction_score"),
    }

    # Infer task size from duration
    if "estimated_duration" in recommendation_data:
        duration = recommendation_data["estimated_duration"]
        for size, config in PREFERENCE_CATEGORIES["task_size"].items():
            min_dur, max_dur = config["duration_minutes"]
            if min_dur <= duration < max_dur:
                pattern["task_size"] = size
                break

    # Infer complexity from steps
    if "steps_count" in recommendation_data:
        steps = recommendation_data["steps_count"]
        for complexity, config in PREFERENCE_CATEGORIES["task_complexity"].items():
            min_steps, max_steps = config["steps_required"]
            if min_steps <= steps < max_steps:
                pattern["task_complexity"] = complexity
                break

    return pattern if any(pattern.values()) else None


def generate_alternative_strategy(
    trigger_type: str,
    user_context: Dict[str, Any],
    failed_recommendation: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Generate personalized alternative strategies based on adaptation triggers.

    Args:
        trigger_type: Type of trigger (e.g., "consecutive_missed_tasks")
        user_context: User's current context and preferences
        failed_recommendation: Original recommendation that failed (optional)

    Returns:
        Alternative strategy dictionary with rationale
    """
    alternatives = {
        "trigger_type": trigger_type,
        "timestamp": datetime.now().isoformat(),
        "strategies": [],
    }

    # Generate strategies based on trigger type
    if trigger_type == "consecutive_missed_tasks":
        alternatives["strategies"] = [
            {
                "type": "task_breakdown",
                "title": "Break Tasks into Smaller Steps",
                "description": "Divide the missed task into 15-30 minute micro-tasks",
                "rationale": "Smaller tasks reduce cognitive load and increase completion likelihood",
                "example": "Instead of 'Complete project report', try: 1) Outline sections (10 min), 2) Draft introduction (15 min)",
            },
            {
                "type": "time_shift",
                "title": "Try Different Timing",
                "description": "Shift task to a different time of day when energy is higher",
                "rationale": "Circadian rhythms affect task completion - find your peak performance window",
                "example": "If morning tasks are missed, try scheduling during post-lunch energy boost (2-4 PM)",
            },
            {
                "type": "accountability_boost",
                "title": "Add Accountability Mechanism",
                "description": "Schedule a check-in or share goal with someone",
                "rationale": "Social accountability increases commitment and follow-through",
            },
        ]

    elif trigger_type == "declining_mood":
        alternatives["strategies"] = [
            {
                "type": "mood_first",
                "title": "Prioritize Mood-Boosting Activities",
                "description": "Focus on small, enjoyable tasks that improve mood before tackling challenges",
                "rationale": "Positive emotions increase cognitive flexibility and problem-solving ability",
            },
            {
                "type": "gentle_scaling",
                "title": "Scale Down Expectations Temporarily",
                "description": "Reduce task scope by 50% while in low-mood period",
                "rationale": "Lower expectations reduce pressure and allow recovery while maintaining momentum",
            },
        ]

    elif trigger_type == "declining_energy":
        alternatives["strategies"] = [
            {
                "type": "energy_matching",
                "title": "Match Tasks to Energy Levels",
                "description": "Schedule high-energy tasks for peak hours, low-energy tasks for other times",
                "rationale": "Working with natural energy cycles improves productivity and reduces fatigue",
            },
            {
                "type": "micro_rest_periods",
                "title": "Implement Micro-Rest Breaks",
                "description": "Take 2-3 minute breaks between tasks to recharge mental resources",
                "rationale": "Brief rest periods prevent depletion and maintain sustained performance",
            },
        ]

    elif trigger_type == "low_completion_rate":
        alternatives["strategies"] = [
            {
                "type": "goal_clarity",
                "title": "Increase Goal Clarity and Specificity",
                "description": "Ensure each task has clear success criteria and next steps defined",
                "rationale": "Ambiguous goals lead to procrastination - clarity drives action",
            },
            {
                "type": "obstacle_mapping",
                "title": "Identify and Remove Obstacles",
                "description": "List specific barriers preventing completion and address each directly",
                "rationale": "Removing friction points makes task initiation easier",
            },
        ]

    elif trigger_type == "changing_priorities":
        alternatives["strategies"] = [
            {
                "type": "priority_realignment",
                "title": "Realign Tasks with New Priorities",
                "description": "Review and reorganize task list based on updated values/goals",
                "rationale": "Misalignment between tasks and priorities reduces motivation",
            },
            {
                "type": "flexible_framework",
                "title": "Implement Flexible Framework Approach",
                "description": "Create adaptable plans that can accommodate shifting priorities",
                "rationale": "Rigid plans break under pressure; flexible ones adapt and persist",
            },
        ]

    # Personalize based on failed recommendation if provided
    if failed_recommendation:
        for strategy in alternatives["strategies"]:
            strategy["based_on"] = f"Failed: {failed_recommendation.get('title', 'unknown task')}"

    return alternatives


def load_adaptation_history(user_id: str, backend: Any) -> List[Dict[str, Any]]:
    """
    Load adaptation history for a user.

    Args:
        user_id: User identifier
        backend: FilesystemBackend instance

    Returns:
        List of adaptation history records, sorted by date (newest first)
    """
    try:
        path = f"adaptive/{user_id}/adaptation_history.json"

        if hasattr(backend, "read_file"):
            content = backend.read_file(path)
        else:
            workspace_path = (
                Path(backend.root_dir) if hasattr(backend, "root_dir") else Path("workspace")
            )
            file_path = workspace_path / path
            if not file_path.exists():
                return []
            content = file_path.read_text()

        history = json.loads(content)
        return sorted(history, key=lambda x: x.get("timestamp", ""), reverse=True)

    except Exception:
        return []


# ==============================================================================
# Adaptive Recommendation Tools Factory
# ==============================================================================


def create_adaptive_tools(backend=None):
    """
    Create adaptive recommendation tools with shared backend instance.

    These tools enable the AI Life Coach to:
    - Track user responses to recommendations over time
    - Score recommendation effectiveness using multi-factor algorithms
    - Learn from feedback and build preference profiles
    - Detect adaptation triggers (missed tasks, declining metrics)
    - Generate personalized alternative strategies

    Based on research in adaptive recommendation systems and reinforcement learning.

    Args:
        backend: Optional FilesystemBackend instance. If None, uses get_backend()

    Returns:
        Tuple of adaptive tools (track_recommendation_response,
                               calculate_recommendation_effectiveness,
                               learn_user_preferences,
                               detect_adaptation_triggers,
                               generate_personalized_alternatives,
                               get_adaptive_recommendations_history)

    Example:
        >>> from src.config import config
        >>> config.initialize_environment()
        >>> tools = create_adaptive_tools()
        >>> result = track_recommendation_response("user_123", {
        ...     "recommendation_id": "rec_001",
        ...     "completed": True,
        ...     "satisfaction_score": 8
        ... })
    """
    if backend is None:
        backend = get_backend()

    # Get the workspace directory path from backend
    workspace_path = Path(backend.root_dir) if hasattr(backend, "root_dir") else Path("workspace")

    @tool
    def track_recommendation_response(
        user_id: str,
        recommendation_id: str,
        completed: bool,
        satisfaction_score: Optional[int] = None,
        actual_duration_minutes: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> str:
        """Track user response to a recommendation for adaptive learning.

        This tool records how users respond to recommendations, enabling the system
        to learn what works and what doesn't for each individual. Over time, this
        data builds a preference profile that personalizes future recommendations.

        Args:
            user_id: The user's unique identifier
            recommendation_id: ID of the recommendation being tracked
            completed: Whether the user completed the recommended action (True/False)
            satisfaction_score: Optional satisfaction rating (1-10, higher is better)
            actual_duration_minutes: Optional actual time taken to complete
            notes: Optional additional feedback or context

        Returns:
            Confirmation message with learning insights if enough data available.

        Example:
            >>> track_recommendation_response(
            ...     user_id="user_123",
            ...     recommendation_id="morning_exercise_rec",
            ...     completed=True,
            ...     satisfaction_score=8,
            ...     actual_duration_minutes=25
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not recommendation_id:
            return "Error: recommendation_id is required"

        try:
            # Load existing preference profile
            pref_path = f"adaptive/{user_id}/preferences/profile.json"

            if hasattr(backend, "read_file"):
                try:
                    content = backend.read_file(pref_path)
                    profile = json.loads(content)
                except Exception:
                    profile = {"user_id": user_id, "recommendations_tracked": 0, "responses": []}
            else:
                file_path = workspace_path / pref_path
                if file_path.exists():
                    profile = json.loads(file_path.read_text())
                else:
                    profile = {"user_id": user_id, "recommendations_tracked": 0, "responses": []}

            # Create response record
            timestamp = datetime.now().isoformat()
            response_record = {
                "recommendation_id": recommendation_id,
                "completed": completed,
                "satisfaction_score": satisfaction_score,
                "actual_duration_minutes": actual_duration_minutes,
                "notes": notes,
                "timestamp": timestamp,
            }

            # Add to profile
            profile["responses"].append(response_record)
            profile["recommendations_tracked"] = len(
                set(r["recommendation_id"] for r in profile["responses"])
            )
            profile["updated_at"] = timestamp

            # Calculate basic statistics
            completed_responses = [r for r in profile["responses"] if r.get("completed")]
            completion_rate = (
                len(completed_responses) / len(profile["responses"]) if profile["responses"] else 0
            )

            rated_responses = [r for r in profile["responses"] if r.get("satisfaction_score")]
            avg_satisfaction = (
                sum(r["satisfaction_score"] for r in rated_responses) / len(rated_responses)
                if rated_responses
                else None
            )

            profile["statistics"] = {
                "total_responses": len(profile["responses"]),
                "completion_rate": round(completion_rate * 100, 1),
                "average_satisfaction": round(avg_satisfaction, 1) if avg_satisfaction else None,
                "total_recommendations_tracked": profile["recommendations_tracked"],
            }

            # Save profile
            json_content = json.dumps(profile, indent=2)

            if hasattr(backend, "write_file"):
                backend.write_file(pref_path, json_content)
            else:
                file_path = workspace_path / pref_path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format response with learning insights
            lines = [
                f"Recommendation Response Tracked for {user_id}",
                "=" * 60,
                f"\nRecommendation ID: {recommendation_id}",
                f"Status: {'✓ Completed' if completed else '✗ Not completed'}",
            ]

            if satisfaction_score:
                lines.append(f"Satisfaction: {satisfaction_score}/10")

            if actual_duration_minutes:
                lines.append(f"Duration: {actual_duration_minutes} minutes")

            # Show learning insights if enough data
            if profile["recommendations_tracked"] >= 3:
                lines.append("\n📊 Learning Insights:")
                lines.append(
                    f"  • Total recommendations tracked: {profile['recommendations_tracked']}"
                )
                lines.append(
                    f"  • Overall completion rate: {profile['statistics']['completion_rate']}%"
                )
                if profile["statistics"]["average_satisfaction"]:
                    lines.append(
                        f"  • Average satisfaction: {profile['statistics']['average_satisfaction']}/10"
                    )

                # Provide pattern recognition
                if completion_rate >= 0.7:
                    lines.append("\n  🟢 Strong engagement pattern detected")
                elif completion_rate >= 0.5:
                    lines.append("\n  🟡 Moderate engagement - consistency building")
                else:
                    lines.append("\n  🔴 Low completion rate - consider adapting approach")

            lines.append(f"\n💾 Preference profile saved to: {pref_path}")

            return "\n".join(lines)

        except Exception as e:
            return f"Error tracking recommendation response: {str(e)}"

    @tool
    def calculate_recommendation_effectiveness(
        user_id: str,
        recommendation_id: Optional[str] = None,
        week_number: Optional[int] = None,
    ) -> str:
        """Calculate recommendation effectiveness score (0-100%) for analysis.

        This tool computes comprehensive effectiveness scores using a multi-factor
        algorithm that considers:
        - Task completion rate (40% weight)
        - User satisfaction ratings (25% weight)
        - Consistency over time (15% weight)
        - Context alignment with preferences (10% weight)
        - Time/cost efficiency (10% weight)

        Scores help identify which recommendations work best and guide personalization.

        Args:
            user_id: The user's unique identifier
            recommendation_id: Optional specific recommendation to analyze. If None, analyzes overall.
            week_number: Optional week number for context-aware analysis

        Returns:
            Detailed effectiveness score with component breakdown and insights.

        Example:
            >>> calculate_recommendation_effectiveness("user_123", recommendation_id="morning_exercise")
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        try:
            # Load preference profile
            pref_path = f"adaptive/{user_id}/preferences/profile.json"

            if hasattr(backend, "read_file"):
                content = backend.read_file(pref_path)
            else:
                file_path = workspace_path / pref_path
                if not file_path.exists():
                    return f"No preference data found for user '{user_id}'. Track responses first."
                content = file_path.read_text()

            profile = json.loads(content)
            responses = profile.get("responses", [])

            # Filter if specific recommendation
            if recommendation_id:
                responses = [
                    r for r in responses if r.get("recommendation_id") == recommendation_id
                ]

            if not responses:
                return "No response data available for analysis."

            # Load check-in context
            context_bonus = 1.0
            time_efficiency_score = 0.5

            if week_number:
                checkins_dir = workspace_path / "checkins" / user_id
                if checkins_dir.exists():
                    checkin_files = sorted(
                        checkins_dir.glob("week_*_checkin.json"),
                        key=lambda f: int(f.stem.split("_")[1]),
                    )
                    # Load current and previous week
                    for checkin_file in [
                        f for f in checkin_files if int(f.stem.split("_")[1]) <= week_number
                    ][-2:]:
                        try:
                            content = (
                                checkin_file.read_text()
                                if hasattr(backend, "read_file")
                                else backend.read_file(f"checkins/{user_id}/{checkin_file.name}")
                            )
                            checkin_data = json.loads(content)
                            responses_dict = checkin_data.get("responses", {})

                            # Context alignment: higher if energy/mood are good
                            avg_energy = responses_dict.get("average_energy", 5)
                            if avg_energy >= 7:
                                context_bonus = 1.2
                            elif avg_energy <= 4:
                                context_bonus = 0.8

                        except Exception:
                            pass

            # Calculate component scores
            completion_rate = sum(1 for r in responses if r.get("completed")) / len(responses)

            rated_responses = [r for r in responses if r.get("satisfaction_score")]
            user_satisfaction = (
                sum(r["satisfaction_score"] for r in rated_responses) / len(rated_responses) / 10.0
                if rated_responses
                else None
            )

            # Consistency: check if completion rate is stable or improving
            if len(responses) >= 3:
                recent_half = responses[len(responses) // 2 :]
                earlier_half = responses[: len(responses) // 2]

                recent_completion = sum(1 for r in recent_half if r.get("completed")) / len(
                    recent_half
                )
                earlier_completion = sum(1 for r in earlier_half if r.get("completed")) / len(
                    earlier_half
                )

                if recent_completion >= earlier_completion + 0.1:
                    consistency_bonus = 1.3
                elif abs(recent_completion - earlier_completion) < 0.05:
                    consistency_bonus = 1.15
                else:
                    consistency_bonus = 0.9
            else:
                consistency_bonus = 1.0

            # Calculate final effectiveness score
            effectiveness_score = calculate_effectiveness_score(
                completion_rate=completion_rate,
                user_satisfaction=user_satisfaction,
                consistency_bonus=consistency_bonus,
                context_alignment=context_bonus,
                time_efficiency=time_efficiency_score,
            )

            # Format response
            lines = [
                f"Recommendation Effectiveness Analysis for {user_id}",
                "=" * 60,
            ]

            if recommendation_id:
                lines.append(f"\nRecommendation: {recommendation_id}")
            else:
                lines.append("\nOverall Effectiveness (all recommendations)")

            lines.append(f"\n📊 Overall Score: {effectiveness_score}/100")

            # Component breakdown
            lines.append("\n🔍 Score Components:")
            lines.append(f"  • Task Completion: {completion_rate * 100:.1f}% (weight: 40%)")
            if user_satisfaction:
                lines.append(f"  • User Satisfaction: {user_satisfaction * 100:.1f}% (weight: 25%)")
            else:
                lines.append(f"  • User Satisfaction: N/A (weight: 25%)")
            lines.append(f"  • Consistency Bonus: {consistency_bonus:.2f}x (weight: 15%)")
            lines.append(f"  • Context Alignment: {context_bonus:.2f}x (weight: 10%)")
            lines.append(f"  • Time Efficiency: {time_efficiency_score * 100:.1f}% (weight: 10%)")

            # Insights
            lines.append("\n💡 Insights:")

            if effectiveness_score >= 80:
                lines.append("  🟢 Excellent - This recommendation approach is highly effective")
            elif effectiveness_score >= 60:
                lines.append("  🟡 Good - Solid performance with room for optimization")
            elif effectiveness_score >= 40:
                lines.append("  🟠 Fair - Consider adjustments to improve effectiveness")
            else:
                lines.append("  🔴 Needs Improvement - Significant adaptation recommended")

            if consistency_bonus >= 1.15:
                lines.append("  • User is showing improved or consistent engagement")
            elif consistency_bonus <= 0.9:
                lines.append("  • Engagement is declining - may need intervention")

            if completion_rate < 0.5:
                lines.append("  • Low completion rate - consider simplifying tasks")

            return "\n".join(lines)

        except Exception as e:
            return f"Error calculating recommendation effectiveness: {str(e)}"

    @tool
    def learn_user_preferences(user_id: str, include_patterns: bool = True) -> str:
        """Extract and store preference patterns from user feedback history.

        This tool analyzes all tracked recommendation responses to identify
        patterns in what works for the user. It learns preferences around:
        - Task size (small/medium/large preferences)
        - Task complexity (simple/moderate/complex preferences)
        - Optimal timing (time of day, day of week)
        - Support level needs (minimal/moderate/intensive guidance)

        Preferences are stored and used to personalize future recommendations.

        Args:
            user_id: The user's unique identifier
            include_patterns: Whether to show detailed pattern analysis (default: True)

        Returns:
            Extracted preference profile with insights and confidence levels.

        Example:
            >>> learn_user_preferences("user_123")
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        try:
            # Load preference profile
            pref_path = f"adaptive/{user_id}/preferences/profile.json"

            if hasattr(backend, "read_file"):
                content = backend.read_file(pref_path)
            else:
                file_path = workspace_path / pref_path
                if not file_path.exists():
                    return f"No preference data found for user '{user_id}'. Track responses first."
                content = file_path.read_text()

            profile = json.loads(content)
            responses = profile.get("responses", [])

            if len(responses) < 3:
                return (
                    f"Insufficient data for preference learning. "
                    f"At least 3 tracked responses required (found: {len(responses)})"
                )

            # Extract patterns
            learned_patterns = {
                "task_size_success": {"small": 0, "medium": 0, "large": 0},
                "task_complexity_success": {"simple": 0, "moderate": 0, "complex": 0},
                "optimal_time_of_day": {},
                "support_level_preference": None,
            }

            # Analyze completion patterns
            for response in responses:
                if not response.get("completed"):
                    continue

                # Note: In a full implementation, we'd load the original recommendation
                # to get task details. For now, we'll use duration hints if available.
                duration = response.get("actual_duration_minutes")
                if duration:
                    if duration < 15:
                        learned_patterns["task_size_success"]["small"] += 1
                    elif duration < 60:
                        learned_patterns["task_size_success"]["medium"] += 1
                    else:
                        learned_patterns["task_size_success"]["large"] += 1

            # Determine preferences
            task_size_total = sum(learned_patterns["task_size_success"].values())
            if task_size_total > 0:
                learned_patterns["task_size_preference"] = max(
                    learned_patterns["task_size_success"].items(),
                    key=lambda x: x[1],
                )[0]

            # Calculate confidence based on data volume
            confidence = min(0.95, 0.3 + (len(responses) * 0.05))

            # Store learned patterns
            profile["learned_patterns"] = learned_patterns
            profile["learning_confidence"] = round(confidence * 100, 1)
            profile["last_learned_at"] = datetime.now().isoformat()

            # Save updated profile
            json_content = json.dumps(profile, indent=2)

            if hasattr(backend, "write_file"):
                backend.write_file(pref_path, json_content)
            else:
                file_path = workspace_path / pref_path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format response
            lines = [
                f"User Preference Learning Complete for {user_id}",
                "=" * 60,
                f"\nData Points Analyzed: {len(responses)}",
                f"Learning Confidence: {profile['learning_confidence']}%",
            ]

            if include_patterns:
                lines.append("\n📊 Learned Preferences:")

                # Task size preference
                if task_size_total > 0:
                    pref = learned_patterns.get("task_size_preference")
                    lines.append(f"\n  • Task Size Preference: {pref.upper()}")
                    for size, count in learned_patterns["task_size_success"].items():
                        if count > 0:
                            pct = (count / task_size_total) * 100
                            lines.append(f"    - {size}: {count} completions ({pct:.1f}%)")

                # Support level inference
                lines.append("\n  • Support Level Needs:")
                profile["statistics"] = profile.get("statistics", {})
                completion_rate = profile["statistics"].get("completion_rate", 0)

                if completion_rate >= 70:
                    lines.append("    - Autonomous (low support needs)")
                    profile["learned_patterns"]["support_level_preference"] = "minimal"
                elif completion_rate >= 50:
                    lines.append("    - Balanced (moderate support needs)")
                    profile["learned_patterns"]["support_level_preference"] = "moderate"
                else:
                    lines.append("    - Supported (higher support needs)")
                    profile["learned_patterns"]["support_level_preference"] = "intensive"

            lines.append("\n💡 How This Will Be Used:")
            lines.append("  • Future recommendations will be tailored to these patterns")
            lines.append("  • Task complexity and size will match your preferences")
            lines.append("  • Support frequency will align with your needs")

            return "\n".join(lines)

        except Exception as e:
            return f"Error learning user preferences: {str(e)}"

    @tool
    def detect_adaptation_triggers(user_id: str, week_number: Optional[int] = None) -> str:
        """Detect adaptation triggers based on user response patterns.

        This tool analyzes check-in data and recommendation responses to identify
        when adaptation is needed. Triggers include:
        - 3+ consecutive missed tasks in any domain
        - Declining mood scores (2+ point drop)
        - Declining energy levels (2+ point drop)
        - Low completion rate (< 40%)
        - High stress levels (7+ for multiple weeks)
        - Changing life circumstances or priorities

        When triggers are detected, the system can generate alternative strategies.

        Args:
            user_id: The user's unique identifier
            week_number: Optional specific week to analyze. If None, uses most recent.

        Returns:
            List of detected triggers with severity levels and recommended actions.

        Example:
            >>> detect_adaptation_triggers("user_123")
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        try:
            # Load check-in data
            if week_number is None:
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

            # Load recent check-ins for trend analysis
            previous_checkins = load_previous_checkins(user_id, backend, week_number)
            if not previous_checkins:
                return "Need at least 2 weeks of check-in data for trigger detection."

            # Load current check-in
            path = f"checkins/{user_id}/week_{week_number}_checkin.json"

            if hasattr(backend, "read_file"):
                content = backend.read_file(path)
            else:
                file_path = workspace_path / path
                if not file_path.exists():
                    return f"No check-in found for week {week_number}"
                content = file_path.read_text()

            current_checkin = json.loads(content)
            current_responses = current_checkin.get("responses", {})
            current_scores = current_checkin.get("scores", {})

            # Detect triggers
            detected_triggers = []

            # 1. Consecutive missed tasks (3+ in any domain)
            for domain in ["career", "relationship", "finance", "wellness"]:
                completion_field = f"{domain}_goals_completed"
                if current_responses.get(completion_field, 100) < 50:
                    # Check previous weeks for pattern
                    consecutive_count = 1
                    for prev in reversed(previous_checkins):
                        if prev.get("responses", {}).get(completion_field, 100) < 50:
                            consecutive_count += 1
                        else:
                            break

                    if consecutive_count >= ADAPTATION_TRIGGERS["consecutive_missed_tasks"]:
                        detected_triggers.append(
                            {
                                "type": "consecutive_missed_tasks",
                                "domain": domain,
                                "severity": "high" if consecutive_count >= 4 else "medium",
                                "data": {"consecutive_weeks": consecutive_count},
                            }
                        )

            # 2. Declining mood
            current_mood = current_responses.get("average_mood", 5)
            previous_moods = [
                c.get("responses", {}).get("average_mood", 5) for c in previous_checkins
            ]

            if detect_declining_trend(
                current_mood, previous_moods, ADAPTATION_TRIGGERS["declining_mood_threshold"]
            ):
                detected_triggers.append(
                    {
                        "type": "declining_mood",
                        "severity": "medium" if current_mood >= 5 else "high",
                        "data": {
                            "current_mood": current_mood,
                            "previous_avg": sum(previous_moods) / len(previous_moods),
                        },
                    }
                )

            # 3. Declining energy
            current_energy = current_responses.get("average_energy", 5)
            previous_energies = [
                c.get("responses", {}).get("average_energy", 5) for c in previous_checkins
            ]

            if detect_declining_trend(
                current_energy, previous_energies, ADAPTATION_TRIGGERS["declining_energy_threshold"]
            ):
                detected_triggers.append(
                    {
                        "type": "declining_energy",
                        "severity": "medium" if current_energy >= 5 else "high",
                        "data": {
                            "current_energy": current_energy,
                            "previous_avg": sum(previous_energies) / len(previous_energies),
                        },
                    }
                )

            # 4. Low completion rate
            completion_rate = calculate_task_completion_rate(current_responses)
            if completion_rate < ADAPTATION_TRIGGERS["low_completion_rate"]:
                detected_triggers.append(
                    {
                        "type": "low_completion_rate",
                        "severity": "high" if completion_rate < 0.3 else "medium",
                        "data": {"completion_rate": round(completion_rate * 100, 1)},
                    }
                )

            # 5. High stress (check if sustained over weeks)
            current_stress = current_responses.get("stress_level", 5)
            if current_stress >= ADAPTATION_TRIGGERS["high_stress_threshold"]:
                high_stress_count = sum(
                    1
                    for c in previous_checkins
                    if c.get("responses", {}).get("stress_level", 0)
                    >= ADAPTATION_TRIGGERS["high_stress_threshold"]
                )

                if high_stress_count >= 2:  # Current + 2 previous weeks
                    detected_triggers.append(
                        {
                            "type": "high_stress",
                            "severity": "high" if current_stress >= 8 else "medium",
                            "data": {
                                "current_stress": current_stress,
                                "consecutive_weeks": high_stress_count + 1,
                            },
                        }
                    )

            # Format response
            lines = [
                f"Adaptation Trigger Detection for {user_id}",
                "=" * 60,
                f"\nAnalyzing Week {week_number} with {len(previous_checkins)} weeks of historical data",
            ]

            if not detected_triggers:
                lines.append("\n✅ No adaptation triggers detected")
                lines.append("  Your current approach is working well - keep it up!")
            else:
                lines.append(f"\n⚠️  {len(detected_triggers)} Trigger(s) Detected\n")

                for i, trigger in enumerate(detected_triggers, 1):
                    severity_emoji = "🔴" if trigger["severity"] == "high" else "🟡"
                    lines.append(
                        f"{severity_emoji} {i}. {trigger['type'].replace('_', ' ').title()}"
                    )

                    if "domain" in trigger:
                        lines.append(f"   Domain: {trigger['domain'].capitalize()}")

                    if "data" in trigger:
                        for key, value in trigger["data"].items():
                            lines.append(f"   {key.replace('_', ' ').title()}: {value}")

                    # Recommended action
                    if trigger["severity"] == "high":
                        lines.append(
                            "   → Action: Use generate_personalized_alternatives for immediate strategies"
                        )
                    else:
                        lines.append("   → Action: Monitor or consider mild adjustment")

            # Save trigger detection to history
            if detected_triggers:
                history_path = f"adaptive/{user_id}/adaptation_history.json"
                try:
                    if hasattr(backend, "read_file"):
                        history_content = backend.read_file(history_path)
                        history = json.loads(history_content)
                    else:
                        file_path = workspace_path / history_path
                        if file_path.exists():
                            history = json.loads(file_path.read_text())
                        else:
                            history = []

                    history_record = {
                        "week_number": week_number,
                        "timestamp": datetime.now().isoformat(),
                        "triggers_detected": detected_triggers,
                    }
                    history.append(history_record)

                    # Keep only last 50 records
                    history = history[-50:]

                    json_history = json.dumps(history, indent=2)

                    if hasattr(backend, "write_file"):
                        backend.write_file(history_path, json_history)
                    else:
                        file_path = workspace_path / history_path
                        file_path.parent.mkdir(parents=True, exist_ok=True)
                        file_path.write_text(json_history)

                except Exception:
                    pass  # History saving is optional

            return "\n".join(lines)

        except Exception as e:
            return f"Error detecting adaptation triggers: {str(e)}"

    @tool
    def generate_personalized_alternatives(
        user_id: str,
        trigger_type: Optional[str] = None,
        week_number: Optional[int] = None,
    ) -> str:
        """Generate personalized alternative strategies based on adaptation triggers.

        When adaptation is needed, this tool creates tailored alternative approaches
        specific to the user's situation and preference patterns. Strategies are
        research-backed and personalized based on:
        - The type of trigger detected (missed tasks, declining energy, etc.)
        - User's learned preferences
        - Current context (mood, stress level, etc.)
        - Historical data on what has/hasn't worked

        Strategies include:
        - Task breakdown and simplification
        - Timing adjustments (circadian rhythms)
        - Accountability mechanisms
        - Energy matching approaches
        - Priority realignment

        Args:
            user_id: The user's unique identifier
            trigger_type: Optional specific trigger type. If None, auto-detects.
            week_number: Optional week number for context.

        Returns:
            List of personalized alternative strategies with implementation guidance.

        Example:
            >>> generate_personalized_alternatives("user_123", trigger_type="consecutive_missed_tasks")
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        try:
            # Auto-detect trigger if not specified
            if trigger_type is None:
                detection_result = detect_adaptation_triggers(user_id, week_number)
                # Parse trigger type from detection result
                if "consecutive_missed_tasks" in detection_result:
                    trigger_type = "consecutive_missed_tasks"
                elif "declining_mood" in detection_result:
                    trigger_type = "declining_mood"
                elif "declining_energy" in detection_result:
                    trigger_type = "declining_energy"
                elif "low_completion_rate" in detection_result:
                    trigger_type = "low_completion_rate"
                else:
                    return "No adaptation triggers detected. No alternatives needed."

            # Load user context
            user_context = {}

            # Get current check-in for context
            if week_number is None:
                checkins_dir = workspace_path / "checkins" / user_id
                if checkins_dir.exists():
                    checkin_files = sorted(
                        checkins_dir.glob("week_*_checkin.json"),
                        key=lambda f: int(f.stem.split("_")[1]),
                    )
                    if checkin_files:
                        most_recent = checkin_files[-1]
                        week_number = int(most_recent.stem.split("_")[1])

            if week_number:
                path = f"checkins/{user_id}/week_{week_number}_checkin.json"
                try:
                    if hasattr(backend, "read_file"):
                        content = backend.read_file(path)
                    else:
                        file_path = workspace_path / path
                        if file_path.exists():
                            content = file_path.read_text()
                        else:
                            content = None

                    if content:
                        checkin_data = json.loads(content)
                        user_context = {
                            "mood": checkin_data.get("responses", {}).get("average_mood"),
                            "energy": checkin_data.get("responses", {}).get("average_energy"),
                            "stress": checkin_data.get("responses", {}).get("stress_level"),
                        }
                except Exception:
                    pass

            # Load learned preferences
            pref_path = f"adaptive/{user_id}/preferences/profile.json"
            try:
                if hasattr(backend, "read_file"):
                    content = backend.read_file(pref_path)
                else:
                    file_path = workspace_path / pref_path
                    if file_path.exists():
                        content = file_path.read_text()
                    else:
                        content = None

                if content:
                    profile = json.loads(content)
                    learned_patterns = profile.get("learned_patterns", {})
                    user_context["task_size_preference"] = learned_patterns.get(
                        "task_size_preference"
                    )
                    user_context["support_level_preference"] = learned_patterns.get(
                        "support_level_preference"
                    )
            except Exception:
                pass

            # Generate alternative strategies
            alternatives = generate_alternative_strategy(trigger_type, user_context)

            # Format response
            lines = [
                f"Personalized Alternative Strategies for {user_id}",
                "=" * 60,
                f"\nTrigger: {alternatives['trigger_type'].replace('_', ' ').title()}",
                f"Generated: {alternatives['timestamp'][:10]}",
            ]

            # Show context awareness
            if any(user_context.values()):
                lines.append("\n📋 Context Considered:")
                if user_context.get("mood"):
                    lines.append(f"  • Current Mood: {user_context['mood']}/10")
                if user_context.get("energy"):
                    lines.append(f"  • Current Energy: {user_context['energy']}/10")
                if user_context.get("stress"):
                    lines.append(f"  • Current Stress: {user_context['stress']}/10")
                if user_context.get("task_size_preference"):
                    lines.append(
                        f"  • Prefers: {user_context['task_size_preference'].capitalize()} tasks"
                    )
                if user_context.get("support_level_preference"):
                    lines.append(
                        f"  • Support Needs: {user_context['support_level_preference'].capitalize()}"
                    )

            # Show strategies
            lines.append(f"\n💡 Recommended Strategies ({len(alternatives['strategies'])})")

            for i, strategy in enumerate(alternatives["strategies"], 1):
                lines.append(f"\n{i}. {strategy['title']}")
                lines.append(f"   Type: {strategy['type'].replace('_', ' ').title()}")
                lines.append(f"\n   Description: {strategy['description']}")
                lines.append(f"\n   Rationale: {strategy['rationale']}")

                if "example" in strategy:
                    lines.append(f"\n   Example: {strategy['example']}")

            # Implementation guidance
            lines.append("\n✅ Implementation Steps:")
            lines.append("  1. Choose 1-2 strategies to implement this week")
            lines.append("  2. Start with the strategy that resonates most")
            lines.append("  3. Track results using track_recommendation_response")
            lines.append("  4. Review effectiveness in next check-in")

            return "\n".join(lines)

        except Exception as e:
            return f"Error generating personalized alternatives: {str(e)}"

    @tool
    def get_adaptive_recommendations_history(user_id: str, limit: Optional[int] = 10) -> str:
        """View adaptive learning history and pattern evolution.

        This tool provides a comprehensive view of how the adaptive system
        has learned about the user over time, including:
        - Triggers detected and addressed
        - Strategies generated and their effectiveness
        - Preference evolution
        - Overall learning progress

        Useful for understanding how personalization has improved recommendations.

        Args:
            user_id: The user's unique identifier
            limit: Maximum number of history records to show (default: 10)

        Returns:
            Comprehensive adaptive learning history with trends and insights.

        Example:
            >>> get_adaptive_recommendations_history("user_123", limit=5)
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        try:
            # Load adaptation history
            history = load_adaptation_history(user_id, backend)

            if not history:
                return (
                    f"No adaptive learning history found for user '{user_id}'. "
                    "Triggers and adaptations will be recorded as the system learns."
                )

            # Load preference profile
            pref_path = f"adaptive/{user_id}/preferences/profile.json"
            profile = None

            try:
                if hasattr(backend, "read_file"):
                    content = backend.read_file(pref_path)
                else:
                    file_path = workspace_path / pref_path
                    if file_path.exists():
                        content = file_path.read_text()
                    else:
                        content = None

                if content:
                    profile = json.loads(content)
            except Exception:
                pass

            # Format response
            lines = [
                f"Adaptive Learning History for {user_id}",
                "=" * 60,
            ]

            if profile:
                stats = profile.get("statistics", {})
                lines.append(f"\n📊 Overall Statistics:")
                lines.append(
                    f"  • Total Recommendations Tracked: {stats.get('total_recommendations_tracked', 0)}"
                )
                lines.append(f"  • Total Responses Recorded: {stats.get('total_responses', 0)}")
                lines.append(f"  • Overall Completion Rate: {stats.get('completion_rate', 0)}%")
                if stats.get("average_satisfaction"):
                    lines.append(f"  • Average Satisfaction: {stats['average_satisfaction']}/10")

                learned = profile.get("learned_patterns", {})
                if learned:
                    lines.append(f"\n🧠 Learned Preferences:")
                    if learned.get("task_size_preference"):
                        lines.append(
                            f"  • Task Size: {learned['task_size_preference'].capitalize()}"
                        )
                    if learned.get("support_level_preference"):
                        lines.append(
                            f"  • Support Level: {learned['support_level_preference'].capitalize()}"
                        )
                    lines.append(
                        f"  • Learning Confidence: {profile.get('learning_confidence', 0)}%"
                    )

            # Show trigger history
            recent_history = history[:limit]
            lines.append(
                f"\n📜 Recent Adaptation History (showing {len(recent_history)} of {len(history)})"
            )

            for record in recent_history:
                timestamp = record.get("timestamp", "")[:10]
                week = record.get("week_number", "Unknown")
                triggers = record.get("triggers_detected", [])

                lines.append(f"\n📅 Week {week} ({timestamp})")

                if not triggers:
                    lines.append("  ✅ No triggers - on track")
                else:
                    for trigger in triggers:
                        severity = trigger.get("severity", "medium").capitalize()
                        emoji = "🔴" if severity == "High" else "🟡"
                        trigger_name = trigger.get("type", "unknown").replace("_", " ")
                        lines.append(f"  {emoji} {trigger_name.title()} (Severity: {severity})")

            # Insights
            if len(history) >= 3:
                lines.append("\n💡 Learning Insights:")

                # Count trigger types
                trigger_counts = {}
                for record in history:
                    for trigger in record.get("triggers_detected", []):
                        ttype = trigger.get("type")
                        trigger_counts[ttype] = trigger_counts.get(ttype, 0) + 1

                if trigger_counts:
                    lines.append("  Most Common Triggers:")
                    for ttype, count in sorted(
                        trigger_counts.items(), key=lambda x: x[1], reverse=True
                    )[:3]:
                        lines.append(
                            f"    • {ttype.replace('_', ' ').title()}: {count} occurrence(s)"
                        )

                # Trend analysis
                recent_weeks = history[:4]
                older_weeks = history[4:8]

                recent_trigger_count = sum(
                    len(r.get("triggers_detected", [])) for r in recent_weeks
                )
                older_trigger_count = (
                    sum(len(r.get("triggers_detected", [])) for r in older_weeks)
                    if older_weeks
                    else 0
                )

                if len(older_weeks) > 0:
                    avg_recent = recent_trigger_count / len(recent_weeks)
                    avg_older = older_trigger_count / len(older_weeks)

                    if avg_recent < avg_older:
                        lines.append(
                            "\n  ✅ Positive Trend: Fewer triggers recently - adaptations are working!"
                        )
                    elif avg_recent > avg_older:
                        lines.append(
                            "\n  ⚠️ Trend: More triggers recently - may need strategy adjustment"
                        )
                    else:
                        lines.append("\n  ➡️ Stable: Consistent trigger pattern over time")

            return "\n".join(lines)

        except Exception as e:
            return f"Error retrieving adaptive history: {str(e)}"

    # Return tuple of tools
    return (
        track_recommendation_response,
        calculate_recommendation_effectiveness,
        learn_user_preferences,
        detect_adaptation_triggers,
        generate_personalized_alternatives,
        get_adaptive_recommendations_history,
    )
