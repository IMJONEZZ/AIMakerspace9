"""
Mood Tracking and Sentiment Analysis Tools for AI Life Coach.

This module implements comprehensive mood tracking with sentiment analysis:
1. Multi-dimensional mood scoring system (happiness, stress, energy, motivation)
2. Keyword-based sentiment analysis on text entries
3. Mood trend visualization with ASCII charts
4. Correlation analysis between mood and goal progress
5. Mood-informed adaptation triggers

Based on research in:
- Sentiment analysis for coaching and mental health contexts
- Mood tracking best practices (1-10 scales across dimensions)
- Keyword-based emotion detection approaches
- Emotional pattern recognition and trend analysis

Key Features:
1. Mood Dimensions - Track 4 key dimensions: happiness, stress, energy, motivation
2. Sentiment Analysis - Analyze check-in text for emotional content (positive/negative/neutral)
3. Trend Visualization - Generate ASCII charts showing mood over time
4. Correlation Analysis - Identify relationships between mood and progress
5. Adaptation Triggers - Detect when mood-based adaptation is needed

Tools:
- log_mood_entry: Record mood with optional text notes
- analyze_text_sentiment: Analyze sentiment of any text input
- calculate_mood_score: Compute composite mood score from dimensions
- generate_mood_trend_chart: Create ASCII visualization of mood trends
- analyze_mood_progress_correlation: Correlate mood with goal progress
- detect_mood_triggers: Identify when mood-based adaptation needed
- get_mood_history: Retrieve historical mood entries
"""

from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import json
import re

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
# Mood Dimensions and Sentiment Analysis Configuration
# ==============================================================================

# Mood dimensions (1-10 scale)
MOOD_DIMENSIONS = {
    "happiness": {
        "name": "Overall Happiness/Satisfaction",
        "description": "How happy and satisfied do you feel overall?",
        "low_label": "Very unhappy",
        "high_label": "Very happy",
    },
    "stress": {
        "name": "Stress Level",
        "description": "How stressed are you feeling?",
        "low_label": "No stress",
        "high_label": "Extremely stressed",
    },
    "energy": {
        "name": "Energy/Vitality Level",
        "description": "How energetic and vital do you feel?",
        "low_label": "No energy",
        "high_label": "Very energetic",
    },
    "motivation": {
        "name": "Motivation/Engagement Level",
        "description": "How motivated and engaged do you feel?",
        "low_label": "No motivation",
        "high_label": "Highly motivated",
    },
}

# Sentiment analysis keywords (keyword-based approach)
SENTIMENT_KEYWORDS = {
    "positive": [
        # High energy/enthusiasm
        "excited",
        "energetic",
        "motivated",
        "inspired",
        "enthusiastic",
        "confident",
        "optimistic",
        "hopeful",
        "grateful",
        "happy",
        # Achievement/success
        "accomplished",
        "successful",
        "completed",
        "finished",
        "productive",
        "great",
        "excellent",
        "wonderful",
        "amazing",
        # Positive emotions
        "love",
        "enjoy",
        "pleased",
        "satisfied",
        "content",
        "peaceful",
        "calm",
        "relaxed",
        "joy",
        "delight",
        # Progress/growth
        "progress",
        "growth",
        "improvement",
        "better",
        "forward",
        # Social/connection
        "connected",
        "supported",
        "understood",
        "appreciated",
    ],
    "negative": [
        # Low energy/depression
        "tired",
        "exhausted",
        "drained",
        "fatigued",
        "lethargic",
        "unmotivated",
        "discouraged",
        "hopeless",
        "depressed",
        "sad",
        # Stress/anxiety
        "stressed",
        "anxious",
        "worried",
        "overwhelmed",
        "burned out",
        "frustrated",
        "angry",
        "irritated",
        "upset",
        "nervous",
        # Failure/setback
        "failed",
        "failure",
        "struggle",
        "difficult",
        "hard",
        "disappointed",
        "regret",
        "bad",
        "terrible",
        "awful",
        # Isolation/loneliness
        "alone",
        "isolated",
        "lonely",
        "unsupported",
        # Pain/discomfort
        "pain",
        "hurt",
        "suffering",
        "miserable",
    ],
}

# Mood trigger thresholds
MOOD_TRIGGERS = {
    "low_mood_threshold": 3,  # Below 3/10 on happiness indicates low mood
    "high_stress_threshold": 7,  # Above 7/10 on stress indicates high stress
    "low_energy_threshold": 3,  # Below 3/10 on energy indicates low energy
    "low_motivation_threshold": 4,  # Below 4/10 on motivation indicates low motivation
    "consecutive_low_mood": 3,  # Trigger after 3 consecutive low mood entries
    "mood_decline_threshold": -2,  # Mood decline of 2+ points over period
}

# ASCII chart symbols
CHART_SYMBOLS = {
    "point": "●",
    "high_up": "▲",
    "up": "↗",
    "flat": "→",
    "down": "↘",
    "low_down": "▼",
}


# ==============================================================================
# Helper Functions
# ==============================================================================


def analyze_sentiment_keywords(text: str) -> Dict[str, Any]:
    """
    Analyze text sentiment using keyword-based approach.

    Args:
        text: Text to analyze

    Returns:
        Dictionary with sentiment analysis results including:
        - sentiment: "positive", "negative", or "neutral"
        - confidence: Confidence score (0.0-1.0)
        - positive_words: List of positive words found
        - negative_words: List of negative words found
    """
    if not text or not isinstance(text, str):
        return {
            "sentiment": "neutral",
            "confidence": 0.0,
            "positive_words": [],
            "negative_words": [],
        }

    # Convert to lowercase for matching
    text_lower = text.lower()

    # Find positive matches
    positive_words = []
    for word in SENTIMENT_KEYWORDS["positive"]:
        if word.lower() in text_lower:
            # Count occurrences
            count = len(re.findall(r"\b" + re.escape(word.lower()) + r"\b", text_lower))
            positive_words.extend([word] * count)

    # Find negative matches
    negative_words = []
    for word in SENTIMENT_KEYWORDS["negative"]:
        if word.lower() in text_lower:
            # Count occurrences
            count = len(re.findall(r"\b" + re.escape(word.lower()) + r"\b", text_lower))
            negative_words.extend([word] * count)

    # Calculate sentiment
    positive_score = len(positive_words)
    negative_score = len(negative_words)

    if positive_score > negative_score:
        sentiment = "positive"
        confidence = min(1.0, positive_score / (positive_score + negative_score + 1))
    elif negative_score > positive_score:
        sentiment = "negative"
        confidence = min(1.0, negative_score / (positive_score + negative_score + 1))
    else:
        sentiment = "neutral"
        confidence = 0.5

    return {
        "sentiment": sentiment,
        "confidence": round(confidence, 2),
        "positive_words": positive_words[:10],  # Limit to top 10
        "negative_words": negative_words[:10],
    }


def calculate_composite_mood_score(mood_dimensions: Dict[str, int]) -> float:
    """
    Calculate composite mood score from individual dimensions.

    Args:
        mood_dimensions: Dictionary with dimension scores (1-10)

    Returns:
        Composite score between 0.0 and 1.0
    """
    # Extract scores, defaulting to 5 if missing
    happiness = mood_dimensions.get("happiness", 5)
    stress = mood_dimensions.get("stress", 5)  # Lower is better
    energy = mood_dimensions.get("energy", 5)
    motivation = mood_dimensions.get("motivation", 5)

    # Normalize stress (invert so higher is better)
    normalized_stress = 11 - stress

    # Calculate average (1-10 scale)
    avg_score = (happiness + normalized_stress + energy + motivation) / 4

    # Normalize to 0-1 scale
    return (avg_score - 1) / 9


def generate_ascii_chart(
    values: List[float],
    labels: Optional[List[str]] = None,
    width: int = 60,
    height: int = 10,
) -> str:
    """
    Generate ASCII chart for mood trend visualization.

    Args:
        values: List of numeric values to plot
        labels: Optional list of x-axis labels
        width: Chart width in characters
        height: Chart height in lines

    Returns:
        ASCII chart as string
    """
    if not values:
        return "No data available for chart"

    # Normalize values to 0-1 scale
    min_val = min(values)
    max_val = max(values)

    if max_val == min_val:
        normalized = [0.5] * len(values)
    else:
        normalized = [(v - min_val) / (max_val - min_val) for v in values]

    # Generate chart lines
    lines = []

    # Y-axis labels
    y_labels = ["High", "Med", "Low"]
    y_positions = [0.8, 0.5, 0.2]

    # Build chart
    for y_idx in range(height):
        line_parts = []
        y_pos = 1.0 - (y_idx / height)

        # Y-axis label
        if any(abs(y_pos - yp) < 0.1 for yp in y_positions):
            label_idx = min(range(len(y_labels)), key=lambda i: abs(y_pos - y_positions[i]))
            line_parts.append(f"{y_labels[label_idx]:4}")
        else:
            line_parts.append("    ")

        # Chart content
        for val in normalized:
            if abs(val - y_pos) < 0.05:
                line_parts.append(CHART_SYMBOLS["point"])
            elif val > y_pos + 0.05:
                line_parts.append(" ")
            else:
                # Check if this is a data point
                line_parts.append(" ")

        lines.append("".join(line_parts))

    # Add trend indicators
    if len(values) >= 2:
        trend_line = "     "
        for i in range(len(normalized)):
            if i == 0:
                trend_line += CHART_SYMBOLS["point"]
            else:
                change = normalized[i] - normalized[i - 1]
                if change > 0.1:
                    trend_line += CHART_SYMBOLS["high_up"] if change > 0.2 else CHART_SYMBOLS["up"]
                elif change < -0.1:
                    trend_line += (
                        CHART_SYMBOLS["low_down"] if change < -0.2 else CHART_SYMBOLS["down"]
                    )
                else:
                    trend_line += CHART_SYMBOLS["flat"]

        lines.append(trend_line)

    # Add x-axis labels if provided
    if labels and len(labels) == len(values):
        label_line = "     "
        for i, label in enumerate(labels):
            short_label = str(label)[-2:]  # Last 2 characters
            label_line += f"{short_label:^2}"

        lines.append(label_line)

    return "\n".join(lines)


def calculate_correlation(
    mood_scores: List[float],
    progress_scores: List[float],
) -> Dict[str, Any]:
    """
    Calculate correlation between mood and progress scores.

    Uses Pearson correlation coefficient.

    Args:
        mood_scores: List of mood scores
        progress_scores: List of progress scores

    Returns:
        Dictionary with correlation analysis results
    """
    if len(mood_scores) != len(progress_scores):
        return {
            "correlation": None,
            "strength": "insufficient_data",
            "interpretation": "Mood and progress data must have the same number of points",
        }

    if len(mood_scores) < 2:
        return {
            "correlation": None,
            "strength": "insufficient_data",
            "interpretation": "Need at least 2 data points for correlation analysis",
        }

    n = len(mood_scores)

    # Calculate means
    mood_mean = sum(mood_scores) / n
    progress_mean = sum(progress_scores) / n

    # Calculate Pearson correlation coefficient
    numerator = 0.0
    for m, p in zip(mood_scores, progress_scores):
        numerator += (m - mood_mean) * (p - progress_mean)

    mood_variance = 0.0
    for m in mood_scores:
        mood_variance += (m - mood_mean) ** 2

    progress_variance = 0.0
    for p in progress_scores:
        progress_variance += (p - progress_mean) ** 2

    denominator = (mood_variance * progress_variance) ** 0.5

    if denominator == 0:
        correlation = 0.0
    else:
        correlation = numerator / denominator

    # Interpret correlation strength
    abs_corr = abs(correlation)
    if abs_corr >= 0.7:
        strength = "strong"
    elif abs_corr >= 0.4:
        strength = "moderate"
    else:
        strength = "weak"

    # Interpret direction
    if correlation > 0.3:
        interpretation = (
            f"Positive {strength} correlation: Better mood tends to accompany better progress"
        )
    elif correlation < -0.3:
        interpretation = f"Negative {strength} correlation: Higher mood tends to accompany lower progress (may indicate burnout/rushing)"
    else:
        interpretation = f"Weak/no correlation: Mood and progress appear independent"

    return {
        "correlation": round(correlation, 3),
        "strength": strength,
        "interpretation": interpretation,
    }

    n = len(mood_scores)

    # Calculate means
    mood_mean = sum(mood_scores) / n
    progress_mean = sum(progress_scores) / n

    # Calculate Pearson correlation coefficient
    numerator = sum(
        (m - mood_mean) * (p - progress_mean) for m, p in zip(mood_scores, progress_scores)
    )

    mood_variance = sum((m - mood_mean) ** 2 for m in mood_scores)
    progress_variance = sum((p - progress_mean) ** 2 for p in progress_scores)

    denominator = (mood_variance * progress_variance) ** 0.5

    if denominator == 0:
        correlation = 0.0
    else:
        correlation = numerator / denominator

    # Interpret correlation strength
    abs_corr = abs(correlation)
    if abs_corr >= 0.7:
        strength = "strong"
    elif abs_corr >= 0.4:
        strength = "moderate"
    else:
        strength = "weak"

    # Interpret direction
    if correlation > 0.3:
        interpretation = (
            f"Positive {strength} correlation: Better mood tends to accompany better progress"
        )
    elif correlation < -0.3:
        interpretation = f"Negative {strength} correlation: Higher mood tends to accompany lower progress (may indicate burnout/rushing)"
    else:
        interpretation = f"Weak/no correlation: Mood and progress appear independent"

    return {
        "correlation": round(correlation, 3),
        "strength": strength,
        "interpretation": interpretation,
    }


def detect_mood_triggers(
    current_mood: Dict[str, int],
    mood_history: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Detect mood-based adaptation triggers.

    Args:
        current_mood: Current mood dimension scores
        mood_history: List of previous mood entries

    Returns:
        List of detected triggers with recommendations
    """
    triggers = []

    # Check individual dimension thresholds
    if current_mood.get("happiness", 5) < MOOD_TRIGGERS["low_mood_threshold"]:
        triggers.append(
            {
                "type": "low_happiness",
                "priority": "high",
                "dimension": "happiness",
                "value": current_mood["happiness"],
                "threshold": MOOD_TRIGGERS["low_mood_threshold"],
                "recommendation": "Consider taking time for activities that bring joy and satisfaction. Prioritize self-care.",
            }
        )

    if current_mood.get("stress", 5) > MOOD_TRIGGERS["high_stress_threshold"]:
        triggers.append(
            {
                "type": "high_stress",
                "priority": "high",
                "dimension": "stress",
                "value": current_mood["stress"],
                "threshold": MOOD_TRIGGERS["high_stress_threshold"],
                "recommendation": "Implement stress reduction techniques. Consider simplifying goals or taking breaks.",
            }
        )

    if current_mood.get("energy", 5) < MOOD_TRIGGERS["low_energy_threshold"]:
        triggers.append(
            {
                "type": "low_energy",
                "priority": "medium",
                "dimension": "energy",
                "value": current_mood["energy"],
                "threshold": MOOD_TRIGGERS["low_energy_threshold"],
                "recommendation": "Prioritize rest and recovery. Focus on lighter tasks until energy improves.",
            }
        )

    if current_mood.get("motivation", 5) < MOOD_TRIGGERS["low_motivation_threshold"]:
        triggers.append(
            {
                "type": "low_motivation",
                "priority": "medium",
                "dimension": "motivation",
                "value": current_mood["motivation"],
                "threshold": MOOD_TRIGGERS["low_motivation_threshold"],
                "recommendation": "Reconnect with your 'why' and goals. Start with small wins to build momentum.",
            }
        )

    # Check for consecutive low mood
    if len(mood_history) >= MOOD_TRIGGERS["consecutive_low_mood"]:
        recent_happiness = [
            m.get("happiness", 5) for m in mood_history[-MOOD_TRIGGERS["consecutive_low_mood"] :]
        ]

        if all(h < MOOD_TRIGGERS["low_mood_threshold"] for h in recent_happiness):
            triggers.append(
                {
                    "type": "consecutive_low_mood",
                    "priority": "high",
                    "dimension": "happiness",
                    "value": recent_happiness[-1],
                    "threshold": MOOD_TRIGGERS["low_mood_threshold"],
                    "consecutive_count": len(recent_happiness),
                    "recommendation": f"Low mood for {len(recent_happiness)} consecutive entries. Consider seeking support and reviewing goal feasibility.",
                }
            )

    # Check for mood decline
    if len(mood_history) >= 2:
        prev_happiness = mood_history[-1].get("happiness", 5)
        current_happiness = current_mood.get("happiness", 5)

        decline = current_happiness - prev_happiness
        if decline <= MOOD_TRIGGERS["mood_decline_threshold"]:
            triggers.append(
                {
                    "type": "mood_decline",
                    "priority": "medium",
                    "dimension": "happiness",
                    "value": current_happiness,
                    "previous_value": prev_happiness,
                    "change": decline,
                    "threshold": MOOD_TRIGGERS["mood_decline_threshold"],
                    "recommendation": f"Mood declined by {abs(decline)} points. Review recent challenges and consider adjusting approach.",
                }
            )

    return triggers


# ==============================================================================
# Mood Tracking Tools Factory
# ==============================================================================


def create_mood_tools(backend=None):
    """
    Create mood tracking tools with shared backend instance.

    These tools enable the AI Life Coach to:
    - Log multi-dimensional mood entries with optional text notes
    - Analyze sentiment of any text input using keyword-based approach
    - Calculate composite mood scores across dimensions
    - Generate ASCII visualizations of mood trends
    - Correlate mood changes with goal progress
    - Detect when mood-based adaptation is needed

    Args:
        backend: Optional FilesystemBackend instance. If None, uses get_backend()

    Returns:
        Tuple of mood tools (log_mood_entry,
                            analyze_text_sentiment,
                            calculate_mood_score,
                            generate_mood_trend_chart,
                            analyze_mood_progress_correlation,
                            detect_mood_triggers,
                            get_mood_history)

    Example:
        >>> from src.config import config
        >>> config.initialize_environment()
        >>> tools = create_mood_tools()
        >>> result = log_mood_entry("user_123", {
        ...     "happiness": 7,
        ...     "stress": 4,
        ...     "energy": 6,
        ...     "motivation": 8,
        ...     "notes": "Feeling good about progress this week"
        ... })
    """
    if backend is None:
        backend = get_backend()

    # Get the workspace directory path from backend
    workspace_path = Path(backend.root_dir) if hasattr(backend, "root_dir") else Path("workspace")

    @tool
    def log_mood_entry(
        user_id: str,
        mood_dimensions: Dict[str, int],
        notes: Optional[str] = None,
    ) -> str:
        """Log a multi-dimensional mood entry with optional text notes.

        This tool records mood across four dimensions (1-10 scale):
        - Happiness/Satisfaction
        - Stress Level (lower is better)
        - Energy/Vitality
        - Motivation/Engagement

        Text notes are analyzed for sentiment to provide additional context.

        Args:
            user_id: The user's unique identifier
            mood_dimensions: Dictionary with scores for each dimension (1-10):
                - happiness (int): Overall happiness/satisfaction (1-10)
                - stress (int): Stress level (1-10, higher is more stressed)
                - energy (int): Energy/vitality level (1-10)
                - motivation (int): Motivation/engagement level (1-10)
            notes: Optional text notes about current state

        Returns:
            Confirmation message with mood summary and sentiment analysis.
            Mood saved to moods/{user_id}/mood_{timestamp}.json

        Example:
            >>> log_mood_entry("user_123", {
            ...     "happiness": 7,
            ...     "stress": 4,
            ...     "energy": 6,
            ...     "motivation": 8,
            ... })
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not mood_dimensions or not isinstance(mood_dimensions, dict):
            return "Error: mood_dimensions must be a non-empty dictionary"

        # Validate dimension scores
        valid_dimensions = {"happiness", "stress", "energy", "motivation"}
        for dim in mood_dimensions:
            if dim not in valid_dimensions:
                return f"Error: Invalid dimension '{dim}'. Valid dimensions are: {valid_dimensions}"

            score = mood_dimensions[dim]
            if not isinstance(score, (int, float)) or score < 1 or score > 10:
                return f"Error: {dim} must be a number between 1 and 10"

        try:
            # Analyze sentiment of notes if provided
            sentiment_analysis = {"sentiment": "neutral", "confidence": 0.0}
            if notes and isinstance(notes, str):
                sentiment_analysis = analyze_sentiment_keywords(notes)

            # Calculate composite mood score
            composite_score = calculate_composite_mood_score(mood_dimensions)

            # Prepare mood entry data
            timestamp_str = datetime.now().isoformat()
            date_str = date.today().isoformat()

            mood_entry = {
                "user_id": user_id,
                "timestamp": timestamp_str,
                "date": date_str,
                "dimensions": mood_dimensions,
                "composite_score": composite_score,
                "notes": notes or "",
                "sentiment_analysis": sentiment_analysis,
            }

            # Convert to JSON
            json_content = json.dumps(mood_entry, indent=2)

            # Save mood entry file
            path = f"moods/{user_id}/mood_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format response
            lines = [
                f"Mood Entry Logged for {user_id}",
                "=" * 60,
                f"\nDate: {date_str} | Time: {datetime.now().strftime('%H:%M')}",
            ]

            # Show dimension scores
            lines.append("\n📊 Mood Dimensions:")
            for dim in ["happiness", "stress", "energy", "motivation"]:
                score = mood_dimensions.get(dim, 5)
                config = MOOD_DIMENSIONS[dim]
                lines.append(f"  • {config['name']}: {score}/10")

            # Show composite score
            composite_pct = composite_score * 100
            lines.append(f"\n🎯 Composite Mood Score: {composite_pct:.0f}%")

            # Show sentiment analysis if notes provided
            if notes:
                lines.append("\n💭 Sentiment Analysis:")
                sentiment = sentiment_analysis["sentiment"].upper()
                emoji = (
                    "😊"
                    if sentiment_analysis["sentiment"] == "positive"
                    else ("😔" if sentiment_analysis["sentiment"] == "negative" else "😐")
                )
                lines.append(
                    f"  {emoji} Sentiment: {sentiment} (confidence: {sentiment_analysis['confidence']:.0%})"
                )

                if sentiment_analysis["positive_words"]:
                    lines.append(
                        f"  • Positive words: {', '.join(sentiment_analysis['positive_words'][:5])}"
                    )
                if sentiment_analysis["negative_words"]:
                    lines.append(
                        f"  • Negative words: {', '.join(sentiment_analysis['negative_words'][:5])}"
                    )

            lines.append(f"\n💾 Mood entry saved to: {path}")

            return "\n".join(lines)

        except Exception as e:
            return f"Error logging mood entry: {str(e)}"

    @tool
    def analyze_text_sentiment(text: str) -> str:
        """Analyze the emotional sentiment of any text input.

        This tool uses keyword-based sentiment analysis to detect:
        - Positive emotional indicators (excitement, achievement, joy, etc.)
        - Negative emotional indicators (stress, fatigue, frustration, etc.)
        - Neutral content
        - Confidence score for the analysis

        Based on research in sentiment analysis for coaching and mental health contexts.

        Args:
            text: Text to analyze (can be check-in notes, journal entries, etc.)

        Returns:
            Detailed sentiment analysis including:
            - Detected sentiment (positive/negative/neutral)
            - Confidence score
            - List of positive and negative words found

        Example:
            >>> analyze_text_sentiment("I feel excited about my progress today!")
        """
        if not text or not isinstance(text, str):
            return "Error: Text must be a non-empty string"

        try:
            # Perform sentiment analysis
            result = analyze_sentiment_keywords(text)

            # Format response
            lines = [
                "Sentiment Analysis Results",
                "=" * 60,
                f'\nText: "{text[:100]}{"..." if len(text) > 100 else ""}"',
            ]

            # Show sentiment
            sentiment = result["sentiment"].upper()
            emoji = (
                "😊"
                if result["sentiment"] == "positive"
                else ("😔" if result["sentiment"] == "negative" else "😐")
            )

            lines.append(f"\n🎭 Detected Sentiment: {sentiment}")
            lines.append(f"   Emoji: {emoji}")
            lines.append(f"   Confidence: {result['confidence']:.0%}")

            # Show word counts
            lines.append(f"\n📝 Emotional Words Found:")
            lines.append(f"   Positive: {len(result['positive_words'])} words")
            if result["positive_words"]:
                lines.append(f"   {', '.join(result['positive_words'][:10])}")

            lines.append(f"   Negative: {len(result['negative_words'])} words")
            if result["negative_words"]:
                lines.append(f"   {', '.join(result['negative_words'][:10])}")

            # Provide interpretation
            lines.append(f"\n💡 Interpretation:")
            if result["sentiment"] == "positive":
                lines.append(
                    "   The text contains predominantly positive emotional indicators, suggesting optimism or satisfaction."
                )
            elif result["sentiment"] == "negative":
                lines.append(
                    "   The text contains predominantly negative emotional indicators, suggesting stress, frustration, or low mood."
                )
            else:
                lines.append(
                    "   The text contains balanced emotional indicators, suggesting a neutral or mixed state."
                )

            return "\n".join(lines)

        except Exception as e:
            return f"Error analyzing sentiment: {str(e)}"

    @tool
    def calculate_mood_score(
        user_id: str,
        mood_dimensions: Optional[Dict[str, int]] = None,
    ) -> str:
        """Calculate and display composite mood score from dimensions.

        This tool computes a comprehensive mood score (0-100%) based on:
        - Happiness/Satisfaction (primary factor)
        - Stress Level (inverted - lower stress = better score)
        - Energy/Vitality
        - Motivation/Engagement

        If mood_dimensions are provided, calculates score for those values.
        Otherwise, uses the most recent mood entry.

        Args:
            user_id: The user's unique identifier
            mood_dimensions: Optional dictionary with dimension scores.
                           If None, loads most recent entry.

        Returns:
            Detailed mood score breakdown with individual dimension
            contributions and composite score.

        Example:
            >>> calculate_mood_score("user_123", {
            ...     "happiness": 7,
            ...     "stress": 4,
            ...     "energy": 6,
            ...     "motivation": 8
            ... })
        """
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        try:
            # Load mood dimensions if not provided
            if mood_dimensions is None:
                # Find most recent mood entry
                moods_dir = workspace_path / "moods" / user_id
                if not moods_dir.exists():
                    return f"No mood entries found for user '{user_id}'. Log a mood entry first."

                mood_files = sorted(
                    moods_dir.glob("mood_*.json"), key=lambda f: f.stat().st_mtime, reverse=True
                )

                if not mood_files:
                    return f"No mood entries found for user '{user_id}'. Log a mood entry first."

                if hasattr(backend, "read_file"):
                    rel_path = f"moods/{user_id}/{mood_files[0].name}"
                    content = backend.read_file(rel_path)
                else:
                    content = mood_files[0].read_text()

                mood_data = json.loads(content)
                mood_dimensions = mood_data.get("dimensions", {})

            # Validate dimensions
            if not mood_dimensions:
                return "Error: No mood dimensions available to calculate score"

            # Calculate composite score
            composite_score = calculate_composite_mood_score(mood_dimensions)

            # Format response
            lines = [
                f"Mood Score Calculation for {user_id}",
                "=" * 60,
            ]

            # Show individual dimension scores
            lines.append("\n📊 Individual Dimension Scores:")

            for dim in ["happiness", "stress", "energy", "motivation"]:
                score = mood_dimensions.get(dim, 5)
                config = MOOD_DIMENSIONS[dim]
                lines.append(f"\n  {config['name']}:")
                lines.append(f"    Score: {score}/10")
                lines.append(
                    f"    Label: {config['low_label'] if score <= 3 else (config['high_label'] if score >= 7 else 'Moderate')}"
                )

                # Show contribution (stress is inverted)
                if dim == "stress":
                    normalized = 11 - score
                    contribution = (normalized - 1) / 9
                else:
                    contribution = (score - 1) / 9

                lines.append(f"    Contribution: {contribution * 100:.0f}%")

            # Show composite score
            composite_pct = composite_score * 100
            lines.append(f"\n🎯 Composite Mood Score: {composite_pct:.0f}%")

            # Provide interpretation
            lines.append(f"\n💡 Interpretation:")
            if composite_pct >= 75:
                lines.append("   Excellent overall mood state - high satisfaction and good energy")
            elif composite_pct >= 50:
                lines.append("   Good mood state - generally positive with room for improvement")
            elif composite_pct >= 25:
                lines.append("   Fair mood state - some challenges present but manageable")
            else:
                lines.append("   Low mood state - consider focusing on self-care and support")

            return "\n".join(lines)

        except Exception as e:
            return f"Error calculating mood score: {str(e)}"

    @tool
    def generate_mood_trend_chart(
        user_id: str,
        days: int = 14,
    ) -> str:
        """Generate ASCII visualization of mood trends over time.

        This tool creates text-based charts showing:
        - Composite mood score trend
        - Individual dimension trends (happiness, stress, energy, motivation)
        - Visual indicators for improving/stable/declining patterns

        Useful for identifying emotional patterns and tracking progress.

        Args:
            user_id: The user's unique identifier
            days: Number of recent days to include (default: 14)

        Returns:
            ASCII charts showing mood trends with trend indicators.

        Example:
            >>> generate_mood_trend_chart("user_123", days=7)
        """
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        try:
            # Load mood entries
            moods_dir = workspace_path / "moods" / user_id

            if not moods_dir.exists():
                return f"No mood entries found for user '{user_id}'. Log a mood entry first."

            # Get recent mood files
            mood_files = sorted(
                moods_dir.glob("mood_*.json"),
                key=lambda f: f.stat().st_mtime,
            )

            # Filter to requested days
            from datetime import timedelta

            cutoff_date = date.today() - timedelta(days=days)
            recent_files = [
                f
                for f in mood_files
                if datetime.fromtimestamp(f.stat().st_mtime).date() >= cutoff_date
            ]

            if not recent_files:
                return f"No mood entries found in the last {days} days."

            # Load and parse data
            moods = []
            dates = []

            for file_path in recent_files[:days]:  # Limit to requested number
                if hasattr(backend, "read_file"):
                    rel_path = f"moods/{user_id}/{file_path.name}"
                    content = backend.read_file(rel_path)
                else:
                    content = file_path.read_text()

                mood_data = json.loads(content)
                moods.append(mood_data)

                # Extract date for label
                file_date = datetime.fromtimestamp(file_path.stat().st_mtime).date()
                dates.append(file_day if (file_day := file_date.strftime("%m/%d")) else "")

            # Format response
            lines = [
                f"Mood Trend Chart for {user_id}",
                "=" * 60,
                f"\nShowing {len(moods)} entries over the last {days} days",
            ]

            # Composite mood chart
            lines.append("\n📈 Composite Mood Score Trend:")
            composite_scores = [m.get("composite_score", 0.5) for m in moods]
            labels = [d[-2:] for d in dates]  # Last 2 chars of date

            lines.append(generate_ascii_chart(composite_scores, labels))

            # Individual dimension trends
            dimensions = ["happiness", "stress", "energy", "motivation"]

            for dim in dimensions:
                dimension_scores = [m.get("dimensions", {}).get(dim, 5) / 10 for m in moods]
                lines.append(f"\n{MOOD_DIMENSIONS[dim]['name']}:")
                lines.append(generate_ascii_chart(dimension_scores, labels))

            return "\n".join(lines)

        except Exception as e:
            return f"Error generating mood trend chart: {str(e)}"

    @tool
    def analyze_mood_progress_correlation(
        user_id: str,
        days: int = 30,
    ) -> str:
        """Analyze correlation between mood and goal progress.

        This tool examines the relationship between mood states
        and goal achievement to identify patterns:
        - Positive correlation: Better mood accompanies better progress
        - Negative correlation: Higher stress might be driving rushed work
        - No correlation: Mood and progress appear independent

        Useful for understanding how emotional state impacts productivity.

        Args:
            user_id: The user's unique identifier
            days: Number of recent days to analyze (default: 30)

        Returns:
            Correlation analysis with interpretation and recommendations.

        Example:
            >>> analyze_mood_progress_correlation("user_123", days=30)
        """
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        try:
            # Load mood entries
            moods_dir = workspace_path / "moods" / user_id

            if not moods_dir.exists():
                return f"No mood entries found for user '{user_id}'. Log a mood entry first."

            # Load check-in data
            checkins_dir = workspace_path / "checkins" / user_id

            if not checkins_dir.exists():
                return f"No check-in entries found for user '{user_id}'. Need both mood and check-in data."

            # Get recent entries
            from datetime import timedelta

            cutoff_date = date.today() - timedelta(days=days)

            # Load moods
            mood_files = sorted(
                (
                    f
                    for f in moods_dir.glob("mood_*.json")
                    if datetime.fromtimestamp(f.stat().st_mtime).date() >= cutoff_date
                ),
                key=lambda f: f.stat().st_mtime,
            )

            # Load check-ins (they're weekly, so fewer)
            checkin_files = sorted(
                (
                    f
                    for f in checkins_dir.glob("week_*_checkin.json")
                    if datetime.fromisoformat(f.stem.split("_")[0]).date() >= cutoff_date
                    if f.stem != "week"
                ),  # Skip invalid names
                key=lambda f: int(f.stem.split("_")[1]),
            )

            # Parse data
            mood_data = {}
            for file_path in mood_files:
                if hasattr(backend, "read_file"):
                    rel_path = f"moods/{user_id}/{file_path.name}"
                    content = backend.read_file(rel_path)
                else:
                    content = file_path.read_text()

                m = json.loads(content)
                entry_date = datetime.fromisoformat(m["timestamp"]).date()
                mood_data[entry_date] = m.get("composite_score", 0.5)

            checkin_data = {}
            for file_path in checkin_files:
                if hasattr(backend, "read_file"):
                    content = backend.read_file(f"checkins/{user_id}/{file_path.name}")
                else:
                    content = file_path.read_text()

                c = json.loads(content)
                entry_date = (
                    datetime.fromisoformat(c["date"]).date() if "date" in c else date.today()
                )
                checkin_data[entry_date] = c.get("scores", {}).get("overall", 0.5)

            # Align data by date
            aligned_moods = []
            aligned_progress = []

            for entry_date in sorted(set(list(mood_data.keys()) + list(checkin_data.keys()))):
                if entry_date in mood_data and entry_date in checkin_data:
                    aligned_moods.append(mood_data[entry_date])
                    aligned_progress.append(checkin_data[entry_date])

            if len(aligned_moods) < 2:
                return f"Need at least 2 days with both mood and check-in data. Found {len(aligned_moods)}."

            # Calculate correlation
            correlation_result = calculate_correlation(aligned_moods, aligned_progress)

            # Format response
            lines = [
                f"Mood-Progress Correlation Analysis for {user_id}",
                "=" * 60,
                f"\nAnalyzing {len(aligned_moods)} data points over the last {days} days",
            ]

            # Show correlation result
            lines.append(f"\n📊 Correlation Results:")
            lines.append(f"   Correlation Coefficient: {correlation_result['correlation']}")
            lines.append(f"   Strength: {correlation_result['strength'].capitalize()}")
            lines.append(f"\n💡 Interpretation:")
            lines.append(f"   {correlation_result['interpretation']}")

            # Show sample data
            lines.append(f"\n📈 Sample Data Points:")
            for i in range(min(5, len(aligned_moods))):
                mood_pct = aligned_moods[i] * 100
                progress_pct = aligned_progress[i] * 100
                lines.append(f"   Day {i + 1}: Mood {mood_pct:.0f}%, Progress {progress_pct:.0f}%")

            # Provide recommendations based on correlation
            lines.append(f"\n🎯 Recommendations:")

            if correlation_result["correlation"]:
                corr = correlation_result["correlation"]
                if corr > 0.3:
                    lines.append("   • Your mood and progress are positively correlated")
                    lines.append(
                        "   • Maintaining good emotional health supports your goal achievement"
                    )
                    lines.append("   • Continue practices that improve both mood and progress")
                elif corr < -0.3:
                    lines.append("   • There's a negative correlation between mood and progress")
                    lines.append("   • This might indicate rushing or stress-driven work")
                    lines.append("   • Consider finding balance - sustainable progress matters")
                else:
                    lines.append("   • Mood and progress appear relatively independent")
                    lines.append("   • This suggests good emotional resilience")
                    lines.append("   • Continue monitoring for any emerging patterns")

            return "\n".join(lines)

        except Exception as e:
            import traceback

            return f"Error analyzing mood-progress correlation: {str(e)}\n{traceback.format_exc()}"

    @tool
    def detect_mood_triggers(
        user_id: str,
    ) -> str:
        """Detect when mood-based adaptation is needed.

        This tool analyzes recent mood entries to identify triggers:
        - Low happiness/satisfaction (below 3/10)
        - High stress (above 7/10)
        - Low energy (below 3/10)
        - Low motivation (below 4/10)
        - Consecutive low mood entries
        - Mood decline over time

        Each trigger includes priority and actionable recommendations.

        Args:
            user_id: The user's unique identifier

        Returns:
            List of detected triggers with priorities and recommendations.

        Example:
            >>> detect_mood_triggers("user_123")
        """
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        try:
            # Load mood entries
            moods_dir = workspace_path / "moods" / user_id

            if not moods_dir.exists():
                return f"No mood entries found for user '{user_id}'. Log a mood entry first."

            # Get recent mood files
            mood_files = sorted(
                moods_dir.glob("mood_*.json"),
                key=lambda f: f.stat().st_mtime,
            )

            if not mood_files:
                return f"No mood entries found for user '{user_id}'. Log a mood entry first."

            # Load recent moods (last 10 entries)
            recent_files = mood_files[-min(10, len(mood_files)) :]

            # Parse data
            moods = []
            for file_path in recent_files:
                if hasattr(backend, "read_file"):
                    rel_path = f"moods/{user_id}/{file_path.name}"
                    content = backend.read_file(rel_path)
                else:
                    content = file_path.read_text()

                mood_data = json.loads(content)
                moods.append(mood_data)

            # Get current and historical mood
            if not moods:
                return "No mood data available"

            current_mood = moods[-1].get("dimensions", {})
            historical_moods = moods[:-1]

            # Detect triggers
            triggers = detect_mood_triggers(current_mood, historical_moods)

            # Format response
            lines = [
                f"Mood Trigger Detection for {user_id}",
                "=" * 60,
                f"\nAnalyzing {len(moods)} recent mood entries",
            ]

            # Show current state
            lines.append("\n📊 Current Mood State:")
            for dim in ["happiness", "stress", "energy", "motivation"]:
                score = current_mood.get(dim, 5)
                config = MOOD_DIMENSIONS[dim]
                lines.append(f"  • {config['name']}: {score}/10")

            # Show triggers
            if not triggers:
                lines.append("\n✅ No mood-based adaptation triggers detected")
                lines.append("   Your mood state appears healthy - keep up the good work!")
            else:
                lines.append(f"\n⚠️  {len(triggers)} Trigger(s) Detected:")

                # Group by priority
                high_priority = [t for t in triggers if t["priority"] == "high"]
                medium_priority = [t for t in triggers if t["priority"] == "medium"]

                if high_priority:
                    lines.append("\n🔴 High Priority:")
                    for i, trigger in enumerate(high_priority, 1):
                        lines.append(f"\n{i}. {trigger['type'].upper()}")
                        lines.append(
                            f"   Dimension: {MOOD_DIMENSIONS.get(trigger['dimension'], {}).get('name', trigger['dimension'])}"
                        )
                        lines.append(f"   Value: {trigger.get('value', 'N/A')}/10")
                        lines.append(f"   Recommendation: {trigger['recommendation']}")

                if medium_priority:
                    lines.append("\n🟡 Medium Priority:")
                    for i, trigger in enumerate(medium_priority, 1):
                        lines.append(f"\n{i}. {trigger['type'].upper()}")
                        lines.append(
                            f"   Dimension: {MOOD_DIMENSIONS.get(trigger['dimension'], {}).get('name', trigger['dimension'])}"
                        )
                        lines.append(f"   Value: {trigger.get('value', 'N/A')}/10")
                        lines.append(f"   Recommendation: {trigger['recommendation']}")

                # Add guidance
                lines.append("\n💡 Next Steps:")
                lines.append("1. Address high-priority triggers first")
                lines.append("2. Consider adjusting goals or workload if needed")
                lines.append("3. Prioritize self-care and stress reduction")
                lines.append("4. Seek support if triggers persist")

            return "\n".join(lines)

        except Exception as e:
            import traceback

            return f"Error detecting mood triggers: {str(e)}\n{traceback.format_exc()}"

    @tool
    def get_mood_history(
        user_id: str,
        days: int = 30,
    ) -> str:
        """Retrieve historical mood entries.

        This tool provides a summary of all mood entries within
        the specified time period, including:
        - Dimension scores
        - Composite scores
        - Sentiment analysis of notes

        Useful for reviewing emotional patterns and progress.

        Args:
            user_id: The user's unique identifier
            days: Number of recent days to retrieve (default: 30)

        Returns:
            Summary of mood entries within the time period.

        Example:
            >>> get_mood_history("user_123", days=14)
        """
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        try:
            # Load mood entries
            moods_dir = workspace_path / "moods" / user_id

            if not moods_dir.exists():
                return f"No mood entries found for user '{user_id}'. Log a mood entry first."

            # Get recent mood files
            from datetime import timedelta

            cutoff_date = date.today() - timedelta(days=days)

            mood_files = sorted(
                (
                    f
                    for f in moods_dir.glob("mood_*.json")
                    if datetime.fromtimestamp(f.stat().st_mtime).date() >= cutoff_date
                ),
                key=lambda f: f.stat().st_mtime,
            )

            if not mood_files:
                return f"No mood entries found in the last {days} days."

            # Format response
            lines = [
                f"Mood History for {user_id}",
                "=" * 60,
                f"\nShowing {len(mood_files)} entries over the last {days} days",
            ]

            # Load and display each entry
            for file_path in mood_files:
                if hasattr(backend, "read_file"):
                    rel_path = f"moods/{user_id}/{file_path.name}"
                    content = backend.read_file(rel_path)
                else:
                    content = file_path.read_text()

                mood_data = json.loads(content)

                lines.append(
                    f"\n📅 {mood_data.get('date', 'N/A')} ({datetime.fromisoformat(mood_data['timestamp']).strftime('%H:%M')})"
                )

                # Show dimensions
                dims = mood_data.get("dimensions", {})
                lines.append(f"   Mood: Happiness {dims.get('happiness', 'N/A')}/10, ")
                lines.append(f"Stress {dims.get('stress', 'N/A')}/10, ")
                lines.append(f"Energy {dims.get('energy', 'N/A')}/10, ")
                lines.append(f"Motivation {dims.get('motivation', 'N/A')}/10")

                # Show composite score
                composite = mood_data.get("composite_score", 0.5) * 100
                lines.append(f"   Composite: {composite:.0f}%")

                # Show sentiment if notes analyzed
                sentiment = mood_data.get("sentiment_analysis", {})
                if sentiment.get("sentiment") and sentiment["sentiment"] != "neutral":
                    emoji = (
                        "😊"
                        if sentiment["sentiment"] == "positive"
                        else ("😔" if sentiment["sentiment"] == "negative" else "😐")
                    )
                    lines.append(f"   Sentiment: {sentiment['sentiment'].upper()} {emoji}")

                # Show notes snippet
                notes = mood_data.get("notes", "")
                if notes:
                    snippet = notes[:100] + "..." if len(notes) > 100 else notes
                    lines.append(f'   Notes: "{snippet}"')

            # Calculate averages
            all_composites = []
            for file_path in mood_files:
                if hasattr(backend, "read_file"):
                    content = backend.read_file(f"moods/{user_id}/{file_path.name}")
                else:
                    content = file_path.read_text()

                mood_data = json.loads(content)
                all_composites.append(mood_data.get("composite_score", 0.5))

            if all_composites:
                avg_composite = sum(all_composites) / len(all_composites)
                lines.append(f"\n📊 Average Composite Score: {avg_composite * 100:.0f}%")

            return "\n".join(lines)

        except Exception as e:
            import traceback

            return f"Error retrieving mood history: {str(e)}\n{traceback.format_exc()}"

    return (
        log_mood_entry,
        analyze_text_sentiment,
        calculate_mood_score,
        generate_mood_trend_chart,
        analyze_mood_progress_correlation,
        detect_mood_triggers,
        get_mood_history,
    )
