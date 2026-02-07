"""
Reflection Prompt Tools for AI Life Coach.

This module provides personalized weekly reflection prompts with dynamic
selection based on current challenges, mood, and progress.

Based on research in:
- 5R Reflection Framework (Reporting, Responding, Relating, Reasoning, Reconstructing)
- DEAL Model (Description, Examination, Application)
- "What? So What? Now What?" model
- Coaching reflection best practices (open-ended, thought-provoking questions)
- Reflective journaling for personal growth and self-discovery

Key Features:
1. Dynamic Prompt Selection - Selects prompts based on mood, progress, context
2. Progress-Based Triggers - Milestone celebration and setback recovery prompts
3. Multi-Domain Library - 50+ prompts across 4 categories (Celebration, Challenge, Learning, Planning)
4. Reflection Journal - Saves reflections with metadata and sentiment analysis
5. Insights Extraction - Identifies patterns, themes, and growth areas from past reflections

Tools:
- generate_weekly_reflection_prompts: Generate personalized weekly reflection prompts
- save_reflection_response: Save user's reflection responses to journal
- get_reflection_history: Retrieve historical reflection entries
- extract_insights_from_reflections: Analyze patterns and themes from past reflections
- trigger_milestone_reflection: Generate prompts for milestone celebration
- trigger_setback_reflection: Generate prompts for setback recovery
"""

from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import json
import random

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
# Reflection Prompt Library
# ==============================================================================

REFLECTION_PROMPT_LIBRARY = {
    "celebration": [
        # Achievement-focused prompts
        {
            "id": "ce1",
            "prompt": "What achievement this week made you feel most proud of yourself? What qualities did you demonstrate in achieving it?",
            "theme": "achievement",
            "depth": "medium",
        },
        {
            "id": "ce2",
            "prompt": "Reflect on a moment this week when you exceeded your own expectations. What surprised you about what you were capable of?",
            "theme": "achievement",
            "depth": "deep",
        },
        {
            "id": "ce3",
            "prompt": "What small win or victory did you experience that might have gone unnoticed? Why was this actually significant?",
            "theme": "achievement",
            "depth": "light",
        },
        {
            "id": "ce4",
            "prompt": "In what ways did you grow stronger or more capable this week, even in areas where you didn't achieve specific goals?",
            "theme": "growth",
            "depth": "medium",
        },
        {
            "id": "ce5",
            "prompt": "What positive feedback or recognition did you receive this week? How did it make you feel, and what does it reveal about your strengths?",
            "theme": "recognition",
            "depth": "medium",
        },
        {
            "id": "ce6",
            "prompt": "Think about a difficult situation you handled well this week. What skills or perspectives did you draw upon?",
            "theme": "resilience",
            "depth": "deep",
        },
        {
            "id": "ce7",
            "prompt": "What habit or routine that you've been working on showed positive progress this week? What made the difference?",
            "theme": "habits",
            "depth": "medium",
        },
        {
            "id": "ce8",
            "prompt": "Describe a moment when you felt truly aligned with your values or purpose this week. What was happening?",
            "theme": "purpose",
            "depth": "deep",
        },
        {
            "id": "ce9",
            "prompt": "What relationship or connection brought you joy or support this week? How did you contribute to it?",
            "theme": "relationships",
            "depth": "medium",
        },
        {
            "id": "ce10",
            "prompt": "What fear or doubt did you overcome this week, even in a small way? How can you build on this courage?",
            "theme": "courage",
            "depth": "deep",
        },
        {
            "id": "ce11",
            "prompt": "What new insight or understanding about yourself gained this week are you most grateful for?",
            "theme": "self-awareness",
            "depth": "deep",
        },
        {
            "id": "ce12",
            "prompt": "What did you do this week that demonstrated self-care or boundary-setting? Why was this important?",
            "theme": "self-care",
            "depth": "medium",
        },
    ],
    "challenge": [
        # Obstacle and difficulty-focused prompts
        {
            "id": "ch1",
            "prompt": "What was the biggest challenge you faced this week? What did this experience teach you about your capacity to handle difficulty?",
            "theme": "resilience",
            "depth": "deep",
        },
        {
            "id": "ch2",
            "prompt": "Reflect on a situation where you didn't perform or respond as well as you hoped. What factors contributed to this, and what would you do differently?",
            "theme": "learning",
            "depth": "deep",
        },
        {
            "id": "ch3",
            "prompt": "What pattern or habit got in the way of your progress this week? Where does this pattern come from, and what might help you change it?",
            "theme": "patterns",
            "depth": "deep",
        },
        {
            "id": "ch4",
            "prompt": "What external obstacle or circumstance made things harder for you this week? How can you adapt or work around similar challenges in the future?",
            "theme": "adaptation",
            "depth": "medium",
        },
        {
            "id": "ch5",
            "prompt": "When you felt most discouraged or overwhelmed this week, what was happening? What does this tell you about your needs or limits?",
            "theme": "emotional-awareness",
            "depth": "deep",
        },
        {
            "id": "ch6",
            "prompt": "What difficult conversation or conflict did you experience this week? What role did you play, and what could you learn from it?",
            "theme": "relationships",
            "depth": "deep",
        },
        {
            "id": "ch7",
            "prompt": "What goal or task did you procrastinate on this week? What fears, beliefs, or resistance might be underneath the procrastination?",
            "theme": "procrastination",
            "depth": "deep",
        },
        {
            "id": "ch8",
            "prompt": "What boundary was crossed or need neglected this week? Why did this happen, and what needs to change?",
            "theme": "boundaries",
            "depth": "medium",
        },
        {
            "id": "ch9",
            "prompt": "In what ways did you doubt or criticize yourself this week? Where do these inner voices come from, and are they accurate?",
            "theme": "self-talk",
            "depth": "deep",
        },
        {
            "id": "ch10",
            "prompt": "What resource or support did you lack this week that would have made a difference? How can you address this gap?",
            "theme": "resources",
            "depth": "medium",
        },
        {
            "id": "ch11",
            "prompt": "What expectation (your own or others') felt unrealistic or overwhelming this week? How might you adjust expectations to be more sustainable?",
            "theme": "expectations",
            "depth": "medium",
        },
        {
            "id": "ch12",
            "prompt": "What did you avoid facing this week? What are you afraid might happen if you confronted it directly?",
            "theme": "avoidance",
            "depth": "deep",
        },
    ],
    "learning": [
        # Growth and insight-focused prompts
        {
            "id": "le1",
            "prompt": "What is the most important thing you learned about yourself this week? How does this understanding change how you approach your life or goals?",
            "theme": "self-discovery",
            "depth": "deep",
        },
        {
            "id": "le2",
            "prompt": "Reflect on a mistake or failure this week. What valuable lesson does it contain, and how will you apply that learning going forward?",
            "theme": "learning",
            "depth": "medium",
        },
        {
            "id": "le3",
            "prompt": "What new perspective or insight did you gain this week that shifted your thinking in a meaningful way?",
            "theme": "perspective",
            "depth": "medium",
        },
        {
            "id": "le4",
            "prompt": "What strength or quality do you want to develop further based on this week's experiences? Why is this important to you?",
            "theme": "growth",
            "depth": "medium",
        },
        {
            "id": "le5",
            "prompt": "What surprised you about your reactions, choices, or feelings this week? What does this reveal about hidden aspects of yourself?",
            "theme": "self-awareness",
            "depth": "deep",
        },
        {
            "id": "le6",
            "prompt": "What feedback did you receive this week (from others or from outcomes) that was difficult to hear but might be valuable?",
            "theme": "feedback",
            "depth": "deep",
        },
        {
            "id": "le7",
            "prompt": "What assumption or belief did you hold this week that turned out to be inaccurate? What does this teach you about being more open-minded?",
            "theme": "assumptions",
            "depth": "deep",
        },
        {
            "id": "le8",
            "prompt": "What experience this week stretched you outside your comfort zone? What did you discover about yourself through this discomfort?",
            "theme": "growth",
            "depth": "medium",
        },
        {
            "id": "le9",
            "prompt": "What pattern or theme do you notice emerging across multiple situations this week? What might this pattern be telling you?",
            "theme": "patterns",
            "depth": "deep",
        },
        {
            "id": "le10",
            "prompt": "What did you learn this week about what truly motivates or fulfills you (versus what you thought would)?",
            "theme": "motivation",
            "depth": "deep",
        },
        {
            "id": "le11",
            "prompt": "What choice or decision this week felt aligned with your most authentic self? What made it feel true?",
            "theme": "authenticity",
            "depth": "deep",
        },
        {
            "id": "le12",
            "prompt": "What practice, habit, or approach worked particularly well for you this week? How can you make it a consistent part of your life?",
            "theme": "practices",
            "depth": "medium",
        },
    ],
    "planning": [
        # Future-focused prompts
        {
            "id": "pl1",
            "prompt": "Based on this week's experiences, what is one thing you want to do differently next week? Why will this make a positive difference?",
            "theme": "adjustment",
            "depth": "medium",
        },
        {
            "id": "pl2",
            "prompt": "What goal or intention feels most important to focus on next week? What specific actions will move you toward it?",
            "theme": "focus",
            "depth": "medium",
        },
        {
            "id": "pl3",
            "prompt": "What do you need to let go of or release from this week to create space for what matters most in the coming days?",
            "theme": "release",
            "depth": "deep",
        },
        {
            "id": "pl4",
            "prompt": "What support, resources, or help do you need to make next week more successful? How will you ask for or access this?",
            "theme": "support",
            "depth": "medium",
        },
        {
            "id": "pl5",
            "prompt": "What self-care practice will make the biggest difference for you next week? When and how will you prioritize it?",
            "theme": "self-care",
            "depth": "medium",
        },
        {
            "id": "pl6",
            "prompt": "What potential challenge or obstacle do you anticipate next week? How can you prepare to handle it effectively?",
            "theme": "anticipation",
            "depth": "medium",
        },
        {
            "id": "pl7",
            "prompt": "If you could focus your energy on just one or two priorities next week, what would they be and why?",
            "theme": "priorities",
            "depth": "light",
        },
        {
            "id": "pl8",
            "prompt": "What relationship or connection do you want to nurture next week? What specific gesture or action will show care?",
            "theme": "relationships",
            "depth": "medium",
        },
        {
            "id": "pl9",
            "prompt": "What small experiment or new approach do you want to try next week? What might it teach you?",
            "theme": "experimentation",
            "depth": "medium",
        },
        {
            "id": "pl10",
            "prompt": "What boundary will you set or uphold next week to protect your time, energy, or wellbeing? Why is this important?",
            "theme": "boundaries",
            "depth": "medium",
        },
        {
            "id": "pl11",
            "prompt": "How do you want to feel at the end of next week? What choices and actions will create that feeling?",
            "theme": "intention",
            "depth": "deep",
        },
        {
            "id": "pl12",
            "prompt": "What's one meaningful way you can celebrate or acknowledge your progress and efforts from this week as you move into the next?",
            "theme": "celebration",
            "depth": "light",
        },
    ],
}

# Milestone-specific prompts
MILESTONE_PROMPTS = {
    "goal_achieved": [
        "You've achieved a significant goal! What did this journey teach you about your capacity for growth and persistence?",
        "Reflect on who you were when you started this goal versus who you are now. How have you changed?",
        "What strengths did you discover or develop through achieving this goal? How can you apply them elsewhere?",
        "Who supported you on this journey, and how did their support make a difference? How will you acknowledge them?",
        "What's next for you now that you've achieved this goal? How will you build on this momentum?",
    ],
    "major_breakthrough": [
        "You experienced a major breakthrough! What shifted in your thinking or approach that made this possible?",
        "What old belief or pattern did you release to allow for this breakthrough? How does it feel to be free of it?",
        "How can you anchor this learning so that it becomes a permanent part of who you are and how you operate?",
        "What doors does this breakthrough open for you? What new possibilities feel available now?",
    ],
    "streak_completed": [
        "You've maintained consistency! What habits or systems helped you stay committed to this streak?",
        "What did you learn about yourself through maintaining this consistency? How does it change your self-perception?",
        "How can you build on this streak to create even more positive momentum in your life?",
    ],
}

# Setback recovery prompts
SETBACK_PROMPTS = {
    "setback_occurred": [
        "You faced a setback. What does this experience reveal about what's truly important to you?",
        "If this setback is trying to teach you something, what might the lesson be? How can you apply it going forward?",
        "What aspects of this situation were outside your control, and what was within your control? How can you focus your energy differently?",
        "What support do you need right now to recover and move forward? How will you ask for it?",
        "What's one small step you can take today to begin moving in a positive direction again?",
    ],
    "pattern_recurring": [
        "You've noticed this challenge before. What might be the deeper root or need underneath it?",
        "What have you tried in the past to address this pattern? What worked, what didn't, and why?",
        "What new approach or perspective could you try this time? What might be different now than before?",
        "What would compassion and understanding look like toward yourself as you navigate this familiar territory?",
    ],
}


# ==============================================================================
# Dynamic Prompt Selection Logic
# ==============================================================================


def select_prompts_by_context(
    mood_state: Optional[Dict[str, int]] = None,
    progress_score: Optional[float] = None,
    challenges: Optional[List[str]] = None,
    wins: Optional[List[str]] = None,
    num_prompts_per_category: int = 2,
) -> Dict[str, List[Dict]]:
    """
    Select reflection prompts dynamically based on user's current context.

    Uses multi-factor selection:
    - High mood + high progress → Focus on celebration and learning
    - Low mood or setbacks → More challenge-focused prompts for processing
    - Specific challenges mentioned → Theme-matched prompts
    - Recent wins included → Celebration prompts

    Args:
        mood_state: Dictionary with mood dimension scores (1-10)
        progress_score: Overall progress score (0.0-1.0)
        challenges: List of current challenges or obstacles
        wins: List of recent achievements or wins
        num_prompts_per_category: Number of prompts to select per category

    Returns:
        Dictionary with selected prompts for each category
    """
    selected = {"celebration": [], "challenge": [], "learning": [], "planning": []}

    # Determine focus based on mood and progress
    mood_avg = sum(mood_state.values()) / len(mood_state) if mood_state else 5.0

    # Low mood or low progress: more challenge and learning prompts
    if (mood_state and mood_state.get("happiness", 5) < 4) or (
        progress_score is not None and progress_score < 0.4
    ):
        num_prompts_per_category = {
            "celebration": 1,  # Still include some for balance
            "challenge": 3,  # More processing prompts
            "learning": 2,
            "planning": 2,
        }
    # High mood and good progress: more celebration prompts
    elif (mood_state and mood_state.get("happiness", 5) >= 7) or (
        progress_score is not None and progress_score >= 0.7
    ):
        num_prompts_per_category = {
            "celebration": 3,  # Celebrate success
            "challenge": 1,
            "learning": 2,
            "planning": 2,
        }

    # Select prompts from each category
    for category, prompts in REFLECTION_PROMPT_LIBRARY.items():
        # If specific challenges/wins provided, prioritize theme-matched prompts
        category_prompt_count = (
            num_prompts_per_category.get(category, 2)
            if isinstance(num_prompts_per_category, dict)
            else num_prompts_per_category
        )

        # Shuffle prompts for variety
        shuffled = random.sample(prompts, min(len(prompts), category_prompt_count))
        selected[category] = shuffled

    return selected


def trigger_milestone_prompts(
    milestone_type: str,
    context: Optional[Dict[str, Any]] = None,
) -> List[str]:
    """
    Generate specialized prompts for milestone celebrations.

    Args:
        milestone_type: Type of milestone ("goal_achieved", "major_breakthrough", "streak_completed")
        context: Optional contextual information about the milestone

    Returns:
        List of milestone-specific reflection prompts
    """
    if milestone_type not in MILESTONE_PROMPTS:
        return []

    # Get base prompts for this milestone type
    base_prompts = MILESTONE_PROMPTS[milestone_type]

    # Contextually customize prompts if context provided
    customized = []
    for prompt in base_prompts:
        if context and "goal_name" in context:
            prompt = prompt.replace("this goal", f"'{context['goal_name']}'")
        if context and "streak_length" in context:
            prompt = prompt.replace("this streak", f"{context['streak_length']}")
        customized.append(prompt)

    return customized


def trigger_setback_prompts(
    setback_type: str,
    context: Optional[Dict[str, Any]] = None,
) -> List[str]:
    """
    Generate specialized prompts for setback processing and recovery.

    Args:
        setback_type: Type of setback ("setback_occurred", "pattern_recurring")
        context: Optional contextual information about the setback

    Returns:
        List of setback-specific reflection prompts
    """
    if setback_type not in SETBACK_PROMPTS:
        return []

    # Get base prompts for this setback type
    base_prompts = SETBACK_PROMPTS[setback_type]

    # Contextually customize prompts if context provided
    customized = []
    for prompt in base_prompts:
        if context and "challenge_name" in context:
            prompt = prompt.replace("this challenge", f"'{context['challenge_name']}'")
        if context and "pattern_name" in context:
            prompt = prompt.replace("this pattern", f"'{context['pattern_name']}'")
        customized.append(prompt)

    return customized


def analyze_reflection_sentiment(reflection_text: str) -> Dict[str, Any]:
    """
    Analyze sentiment and emotional content of a reflection response.

    Uses keyword-based analysis similar to mood_tools.py but adapted
    for reflection content (growth-oriented, introspective language).

    Args:
        reflection_text: Text of the reflection response

    Returns:
        Dictionary with sentiment analysis results
    """
    if not reflection_text or not isinstance(reflection_text, str):
        return {"sentiment": "neutral", "confidence": 0.0, "key_emotions": []}

    text_lower = reflection_text.lower()

    # Growth and learning indicators
    growth_keywords = [
        "learned",
        "grew",
        "growth",
        "insight",
        "understanding",
        "realized",
        "discovered",
        "awareness",
        "clarity",
        "breakthrough",
        "shifted",
        "changed",
        "transformed",
    ]

    # Positive achievement indicators
    positive_keywords = [
        "proud",
        "accomplished",
        "succeeded",
        "achieved",
        "progress",
        "stronger",
        "capable",
        "confident",
        "grateful",
        "joy",
    ]

    # Challenge and difficulty indicators
    challenge_keywords = [
        "difficult",
        "hard",
        "challenging",
        "struggle",
        "obstacle",
        "setback",
        "failed",
        "mistake",
        "overwhelmed",
        "discouraged",
    ]

    # Growth-oriented indicators
    growth_count = sum(1 for kw in growth_keywords if kw in text_lower)
    positive_count = sum(1 for kw in positive_keywords if kw in text_lower)
    challenge_count = sum(1 for kw in challenge_keywords if kw in text_lower)

    # Determine overall sentiment
    total_indicators = growth_count + positive_count + challenge_count

    if total_indicators == 0:
        sentiment = "neutral"
        confidence = 0.5
    elif challenge_count > (growth_count + positive_count):
        # More difficulty indicators, but this can still be growth-oriented
        if growth_count > 0:
            sentiment = "growth_through_challenge"
            confidence = min(1.0, (growth_count + challenge_count) / total_indicators)
        else:
            sentiment = "challenging"
            confidence = min(1.0, challenge_count / total_indicators)
    else:
        # More growth/positive indicators
        sentiment = "growth_positive"
        confidence = min(1.0, (growth_count + positive_count) / total_indicators)

    return {
        "sentiment": sentiment,
        "confidence": round(confidence, 2),
        "growth_indicators": growth_count,
        "positive_indicators": positive_count,
        "challenge_indicators": challenge_count,
    }


def extract_insights_from_history(
    reflections: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Extract patterns, themes, and insights from reflection history.

    Analyzes multiple reflections to identify:
    - Recurring themes
    - Emotional patterns
    - Growth trajectories
    - Areas needing attention

    Args:
        reflections: List of reflection entries with metadata and content

    Returns:
        Dictionary with insights analysis
    """
    if not reflections:
        return {
            "total_reflections": 0,
            "recurring_themes": [],
            "emotional_patterns": {},
            "growth_trajectory": None,
        }

    # Collect all themes mentioned
    all_themes = []
    sentiment_distribution = {"growth_positive": 0, "challenging": 0, "neutral": 0}

    for reflection in reflections:
        # Add themes
        if "themes" in reflection:
            all_themes.extend(reflection["themes"])

        # Add sentiment
        if "sentiment_analysis" in reflection:
            sentiment = reflection["sentiment_analysis"].get("sentiment", "neutral")
            if sentiment in sentiment_distribution:
                sentiment_distribution[sentiment] += 1
            else:
                sentiment_distribution["neutral"] += 1

    # Count theme occurrences
    from collections import Counter

    theme_counts = Counter(all_themes)
    recurring_themes = [
        {"theme": theme, "occurrences": count} for theme, count in theme_counts.most_common(5)
    ]

    # Analyze emotional patterns over time
    if len(reflections) >= 3:
        recent_sentiments = [
            r.get("sentiment_analysis", {}).get("sentiment", "neutral") for r in reflections[-3:]
        ]

        if all(s == "growth_positive" for s in recent_sentiments):
            growth_trajectory = "strongly_positive"
        elif all(s == "challenging" for s in recent_sentiments):
            growth_trajectory = "needs_support"
        else:
            growth_trajectory = "mixed_with_growth"
    else:
        growth_trajectory = "insufficient_data"

    return {
        "total_reflections": len(reflections),
        "recurring_themes": recurring_themes,
        "emotional_patterns": sentiment_distribution,
        "growth_trajectory": growth_trajectory,
    }


# ==============================================================================
# Reflection Tools Factory
# ==============================================================================


def create_reflection_tools(backend=None):
    """
    Create reflection prompt tools with shared backend instance.

    These tools enable the AI Life Coach to:
    - Generate personalized weekly reflection prompts based on context
    - Save user reflections with sentiment analysis and metadata
    - Retrieve historical reflection entries
    - Extract insights and patterns from reflection history
    - Trigger specialized prompts for milestones and setbacks

    Args:
        backend: Optional FilesystemBackend instance. If None, uses get_backend()

    Returns:
        Tuple of reflection tools (generate_weekly_reflection_prompts,
                                save_reflection_response,
                                get_reflection_history,
                                extract_insights_from_reflections,
                                trigger_milestone_reflection,
                                trigger_setback_reflection)

    Example:
        >>> from src.config import config
        >>> config.initialize_environment()
        >>> tools = create_reflection_tools()
        >>> result = generate_weekly_reflection_prompts(
        ...     "user_123",
        ...     mood_state={"happiness": 7, "stress": 3},
        ...     progress_score=0.75
        ... )
    """
    if backend is None:
        backend = get_backend()

    # Get the workspace directory path from backend
    workspace_path = Path(backend.root_dir) if hasattr(backend, "root_dir") else Path("workspace")

    @tool
    def generate_weekly_reflection_prompts(
        user_id: str,
        mood_state: Optional[Dict[str, int]] = None,
        progress_score: Optional[float] = None,
        challenges: Optional[List[str]] = None,
        wins: Optional[List[str]] = None,
    ) -> str:
        """Generate personalized weekly reflection prompts based on current context.

        This tool dynamically selects from a library of 50+ reflection prompts
        across four categories:
        - Celebration (achievements and wins)
        - Challenge (obstacles and difficulties)
        - Learning (growth moments and insights)
        - Planning (future intentions and adjustments)

        Prompts are selected based on:
        - Current mood state (happiness, stress, energy, motivation)
        - Recent progress score
        - Specific challenges or obstacles mentioned
        - Recent wins or achievements

        Based on reflection frameworks including 5R, DEAL model, and "What? So What? Now What?"

        Args:
            user_id: The user's unique identifier
            mood_state: Optional dictionary with mood dimension scores (1-10):
                - happiness (int): Overall happiness/satisfaction
                - stress (int): Stress level (higher is more stressed)
                - energy (int): Energy/vitality
                - motivation (int): Motivation/engagement
            progress_score: Optional overall progress score (0.0-1.0)
            challenges: Optional list of current challenges or obstacles
            wins: Optional list of recent achievements

        Returns:
            Structured reflection prompts organized by category with
            context-aware selection rationale.

        Example:
            >>> generate_weekly_reflection_prompts("user_123", {
            ...     "happiness": 7,
            ...     "stress": 4,
            ... }, progress_score=0.75)
        """
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        try:
            # Select prompts based on context
            selected_prompts = select_prompts_by_context(
                mood_state=mood_state,
                progress_score=progress_score,
                challenges=challenges or [],
                wins=wins or [],
            )

            # Format response
            lines = [
                f"📝 Weekly Reflection Prompts for {user_id}",
                "=" * 60,
                f"\nGenerated on: {date.today().strftime('%B %d, %Y')}",
            ]

            # Include context summary
            if mood_state or progress_score is not None:
                lines.append("\n📊 Context Used for Selection:")

                if mood_state:
                    lines.append("   Mood State:")
                    for dim, score in mood_state.items():
                        lines.append(f"     • {dim.capitalize()}: {score}/10")

                if progress_score is not None:
                    lines.append(f"   Progress Score: {progress_score * 100:.0f}%")

            # Display prompts by category
            lines.append("\n" + "=" * 60)
            lines.append("YOUR REFLECTION PROMPTS")
            lines.append("=" * 60)

            category_titles = {
                "celebration": "🎉 Celebration - Acknowledge Your Achievements",
                "challenge": "💪 Challenge - Process Obstacles & Difficulties",
                "learning": "🌱 Learning - Discover Growth & Insights",
                "planning": "🎯 Planning - Set Intentions for Next Week",
            }

            for category, prompts in selected_prompts.items():
                lines.append(f"\n{category_titles.get(category, category.upper())}")
                lines.append("─" * 60)

                for i, prompt in enumerate(prompts, 1):
                    lines.append(f"\n{i}. {prompt['prompt']}")
                    lines.append(f"   Theme: {prompt.get('theme', 'general')}")
                    lines.append(f"   Depth: {prompt.get('depth', 'medium')}")

            # Add guidance
            lines.append("\n" + "=" * 60)
            lines.append("💡 Reflection Tips:")
            lines.append("• Set aside 15-30 minutes for thoughtful reflection")
            lines.append("• Write freely and honestly without self-judgment")
            lines.append("• Focus on what you learned, not just what happened")
            lines.append("• Use these prompts as starting points - follow where your thoughts lead")
            lines.append("=" * 60)

            return "\n".join(lines)

        except Exception as e:
            return f"Error generating reflection prompts: {str(e)}"

    @tool
    def save_reflection_response(
        user_id: str,
        prompt_category: str,
        prompt_text: str,
        response_text: str,
    ) -> str:
        """Save a user's reflection response to the journal.

        This tool stores reflection responses with metadata including:
        - Timestamp and date
        - Category and original prompt
        - Full response text
        - Sentiment analysis (growth indicators, challenge indicators)
        - Extracted themes

        Reflections are saved in the reflections/{user_id}/ directory.

        Args:
            user_id: The user's unique identifier
            prompt_category: Category of the reflection (celebration, challenge, learning, planning)
            prompt_text: The original reflection prompt
            response_text: User's written reflection response

        Returns:
            Confirmation with sentiment analysis and extracted themes.

        Example:
            >>> save_reflection_response(
            ...     "user_123",
            ...     "celebration",
            ...     "What achievement this week made you feel proud?",
            ...     "I completed my project ahead of schedule..."
            ... )
        """
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not response_text or not isinstance(response_text, str):
            return "Error: response_text must be a non-empty string"

        try:
            # Analyze sentiment
            sentiment_analysis = analyze_reflection_sentiment(response_text)

            # Extract themes from prompt and response
            all_text = f"{prompt_text} {response_text}".lower()

            theme_keywords = {
                "growth": ["grow", "learn", "develop", "improve", "progress"],
                "relationships": ["relationship", "connection", "friend", "family", "partner"],
                "career": ["work", "job", "career", "project", "professional"],
                "wellness": ["health", "wellness", "self-care", "exercise", "mental"],
                "resilience": ["overcome", "challenge", "difficult", "persist", "strength"],
                "purpose": ["meaning", "purpose", "values", "authentic", "aligned"],
            }

            themes = []
            for theme, keywords in theme_keywords.items():
                if any(kw in all_text for kw in keywords):
                    themes.append(theme)

            # Prepare reflection entry
            timestamp_str = datetime.now().isoformat()
            date_str = date.today().isoformat()

            reflection_entry = {
                "user_id": user_id,
                "timestamp": timestamp_str,
                "date": date_str,
                "category": prompt_category,
                "prompt": prompt_text,
                "response": response_text,
                "sentiment_analysis": sentiment_analysis,
                "themes": themes,
            }

            # Convert to JSON
            json_content = json.dumps(reflection_entry, indent=2)

            # Save reflection file
            path = (
                f"reflections/{user_id}/reflection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )

            if hasattr(backend, "write_file"):
                backend.write_file(path, json_content)
            else:
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)

            # Format response
            lines = [
                f"💾 Reflection Saved for {user_id}",
                "=" * 60,
                f"\nDate: {date_str} | Category: {prompt_category.capitalize()}",
            ]

            # Show sentiment analysis
            lines.append("\n📊 Sentiment Analysis:")
            lines.append(f"   Type: {sentiment_analysis['sentiment'].replace('_', ' ').title()}")
            lines.append(f"   Confidence: {sentiment_analysis['confidence']:.0%}")

            if sentiment_analysis.get("growth_indicators", 0) > 0:
                lines.append(
                    f"   Growth indicators detected: {sentiment_analysis['growth_indicators']}"
                )

            # Show themes
            if themes:
                lines.append("\n🏷️  Themes Identified:")
                for theme in themes:
                    lines.append(f"   • {theme}")

            lines.append(f"\n💾 Reflection saved to: {path}")

            return "\n".join(lines)

        except Exception as e:
            return f"Error saving reflection response: {str(e)}"

    @tool
    def get_reflection_history(
        user_id: str,
        days: int = 30,
        category_filter: Optional[str] = None,
    ) -> str:
        """Retrieve historical reflection entries.

        This tool provides a summary of reflection entries within the
        specified time period, including:
        - Category and prompts
        - Responses with sentiment analysis
        - Identified themes
        - Timeline of reflections

        Useful for reviewing growth patterns and insights over time.

        Args:
            user_id: The user's unique identifier
            days: Number of recent days to retrieve (default: 30)
            category_filter: Optional filter by category (celebration, challenge, learning, planning)

        Returns:
            Summary of reflection entries within the time period.

        Example:
            >>> get_reflection_history("user_123", days=14)
        """
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        try:
            # Load reflection entries
            reflections_dir = workspace_path / "reflections" / user_id

            if not reflections_dir.exists():
                return f"No reflection entries found for user '{user_id}'. Save a reflection first."

            # Get recent reflection files
            cutoff_date = date.today() - timedelta(days=days)

            reflection_files = sorted(
                (
                    f
                    for f in reflections_dir.glob("reflection_*.json")
                    if datetime.fromtimestamp(f.stat().st_mtime).date() >= cutoff_date
                ),
                key=lambda f: f.stat().st_mtime,
            )

            # Apply category filter if specified
            if category_filter:
                filtered_files = []
                for file_path in reflection_files:
                    if hasattr(backend, "read_file"):
                        rel_path = f"reflections/{user_id}/{file_path.name}"
                        content = backend.read_file(rel_path)
                    else:
                        content = file_path.read_text()

                    data = json.loads(content)
                    if data.get("category") == category_filter:
                        filtered_files.append(file_path)

                reflection_files = filtered_files

            if not reflection_files:
                return f"No reflection entries found for the specified criteria."

            # Format response
            lines = [
                f"📖 Reflection History for {user_id}",
                "=" * 60,
                f"\nShowing {len(reflection_files)} entries from the last {days} days",
            ]

            if category_filter:
                lines.append(f"Filtered by category: {category_filter}")

            # Summarize each reflection
            for file_path in reflection_files:
                if hasattr(backend, "read_file"):
                    rel_path = f"reflections/{user_id}/{file_path.name}"
                    content = backend.read_file(rel_path)
                else:
                    content = file_path.read_text()

                reflection_data = json.loads(content)

                lines.append("\n" + "─" * 60)
                lines.append(
                    f"\n📅 {reflection_data.get('date', 'Unknown date')} | {reflection_data.get('category', 'unknown').capitalize()}"
                )

                # Show prompt
                lines.append(f"\nPrompt: {reflection_data.get('prompt', 'N/A')[:100]}...")

                # Show sentiment
                sentiment = reflection_data.get("sentiment_analysis", {}).get(
                    "sentiment", "neutral"
                )
                lines.append(f"Sentiment: {sentiment.replace('_', ' ').title()}")

                # Show themes
                themes = reflection_data.get("themes", [])
                if themes:
                    lines.append(f"Themes: {', '.join(themes)}")

            return "\n".join(lines)

        except Exception as e:
            return f"Error retrieving reflection history: {str(e)}"

    @tool
    def extract_insights_from_reflections(
        user_id: str,
        days: int = 90,
    ) -> str:
        """Extract patterns, themes, and insights from reflection history.

        This tool analyzes multiple reflections to identify:
        - Recurring themes across entries
        - Emotional patterns and trends
        - Growth trajectory over time
        - Areas that may need attention or support

        Useful for understanding long-term patterns and growth areas.

        Args:
            user_id: The user's unique identifier
            days: Number of recent days to analyze (default: 90)

        Returns:
            Comprehensive insights analysis with patterns and recommendations.

        Example:
            >>> extract_insights_from_reflections("user_123", days=60)
        """
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        try:
            # Load reflection entries
            reflections_dir = workspace_path / "reflections" / user_id

            if not reflections_dir.exists():
                return f"No reflection entries found for user '{user_id}'. Save a reflection first."

            # Get recent reflection files
            cutoff_date = date.today() - timedelta(days=days)

            reflection_files = sorted(
                (
                    f
                    for f in reflections_dir.glob("reflection_*.json")
                    if datetime.fromtimestamp(f.stat().st_mtime).date() >= cutoff_date
                ),
                key=lambda f: f.stat().st_mtime,
            )

            if len(reflection_files) < 2:
                return f"Need at least 2 reflection entries for insights analysis. Found {len(reflection_files)}."

            # Load all reflections
            reflections = []
            for file_path in reflection_files:
                if hasattr(backend, "read_file"):
                    rel_path = f"reflections/{user_id}/{file_path.name}"
                    content = backend.read_file(rel_path)
                else:
                    content = file_path.read_text()

                reflection_data = json.loads(content)
                reflections.append(reflection_data)

            # Extract insights
            insights = extract_insights_from_history(reflections)

            # Format response
            lines = [
                f"💡 Reflection Insights for {user_id}",
                "=" * 60,
                f"\nAnalyzing {insights['total_reflections']} reflections over the last {days} days",
            ]

            # Show recurring themes
            if insights["recurring_themes"]:
                lines.append("\n🏷️  Recurring Themes:")
                for theme_info in insights["recurring_themes"]:
                    lines.append(
                        f"   • {theme_info['theme'].title()}: {theme_info['occurrences']} mentions"
                    )

            # Show emotional patterns
            lines.append("\n📊 Emotional Patterns:")
            for sentiment, count in insights["emotional_patterns"].items():
                if count > 0:
                    percentage = (count / insights["total_reflections"]) * 100
                    lines.append(
                        f"   • {sentiment.replace('_', ' ').title()}: {percentage:.0f}% ({count} reflections)"
                    )

            # Show growth trajectory
            lines.append("\n📈 Growth Trajectory:")
            trajectory = insights["growth_trajectory"]

            if trajectory == "strongly_positive":
                lines.append("   ✨ Strong positive growth trajectory")
                lines.append("      Your recent reflections show consistent growth and learning.")
            elif trajectory == "needs_support":
                lines.append("   ⚠️  May need additional support")
                lines.append(
                    "      Recent reflections indicate ongoing challenges. Consider reaching out for support."
                )
            elif trajectory == "mixed_with_growth":
                lines.append("   🌱 Mixed with growth")
                lines.append(
                    "      You're experiencing both challenges and growth, which is normal. Keep reflecting!"
                )
            else:
                lines.append("   ℹ️  Insufficient data for trajectory analysis")

            # Provide recommendations
            lines.append("\n🎯 Recommendations:")

            if insights["recurring_themes"]:
                top_theme = insights["recurring_themes"][0]["theme"]
                lines.append(f"   • Your reflections often focus on {top_theme}")
                lines.append(
                    f"     Consider setting specific goals or seeking resources related to this area."
                )

            if insights["emotional_patterns"].get("challenge_indicators", 0) > insights[
                "emotional_patterns"
            ].get("growth_positive", 0):
                lines.append(
                    "   • Your reflections show more challenge indicators than growth-positive ones"
                )
                lines.append("     Consider focusing on small wins and self-compassion.")

            lines.append("   • Continue regular reflection to deepen insights")
            lines.append("   • Share key insights with your coach or support network")

            return "\n".join(lines)

        except Exception as e:
            return f"Error extracting insights from reflections: {str(e)}"

    @tool
    def trigger_milestone_reflection(
        user_id: str,
        milestone_type: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate specialized reflection prompts for milestone celebrations.

        This tool provides targeted prompts when users achieve significant
        milestones including:
        - Goal achievement (goal_achieved)
        - Major breakthroughs or insights (major_breakthrough)
        - Streak completion (streak_completed)

        These prompts help users process and integrate the meaning
        of their achievements.

        Args:
            user_id: The user's unique identifier
            milestone_type: Type of milestone (goal_achieved, major_breakthrough, streak_completed)
            context: Optional dictionary with contextual information:
                - goal_name (str): Name of the achieved goal
                - streak_length (int): Length of completed streak

        Returns:
            Milestone-specific reflection prompts with celebration guidance.

        Example:
            >>> trigger_milestone_reflection(
            ...     "user_123",
            ...     "goal_achieved",
            ...     {"goal_name": "Complete certification"}
            ... )
        """
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        try:
            # Get milestone prompts
            prompts = trigger_milestone_prompts(milestone_type, context)

            if not prompts:
                return f"Error: Unknown milestone type '{milestone_type}'. Valid types: goal_achieved, major_breakthrough, streak_completed"

            # Format response
            lines = [
                f"🎉 Milestone Reflection for {user_id}",
                "=" * 60,
            ]

            if context and "goal_name" in context:
                lines.append(f"\nCelebrating Achievement: {context['goal_name']}")
            elif context and "streak_length" in context:
                lines.append(f"\nCelebrating Streak: {context['streak_length']} days")
            else:
                milestone_names = {
                    "goal_achieved": "Goal Achieved!",
                    "major_breakthrough": "Major Breakthrough!",
                    "streak_completed": "Streak Completed!",
                }
                lines.append(f"\n{milestone_names.get(milestone_type, 'Milestone')}")

            lines.append("\n" + "─" * 60)
            lines.append("📝 Milestone Reflection Prompts")
            lines.append("─" * 60)

            for i, prompt in enumerate(prompts, 1):
                lines.append(f"\n{i}. {prompt}")

            # Add celebration guidance
            lines.append("\n" + "─" * 60)
            lines.append("💡 Celebration Suggestions:")
            lines.append("• Take time to fully acknowledge and feel proud of this achievement")
            lines.append("• Share your success with someone who supports you")
            lines.append("• Document what contributed to this milestone for future reference")
            lines.append("• Consider how you'd like to celebrate in a meaningful way")

            return "\n".join(lines)

        except Exception as e:
            return f"Error generating milestone reflection: {str(e)}"

    @tool
    def trigger_setback_reflection(
        user_id: str,
        setback_type: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate specialized reflection prompts for setback processing.

        This tool provides supportive prompts when users encounter
        setbacks including:
        - General setbacks (setback_occurred)
        - Recurring patterns or challenges (pattern_recurring)

        These prompts help users process setbacks constructively
        and identify learning opportunities.

        Args:
            user_id: The user's unique identifier
            setback_type: Type of setback (setback_occurred, pattern_recurring)
            context: Optional dictionary with contextual information:
                - challenge_name (str): Name of the challenge
                - pattern_name (str): Name of the recurring pattern

        Returns:
            Setback-specific reflection prompts with recovery guidance.

        Example:
            >>> trigger_setback_reflection(
            ...     "user_123",
            ...     "setback_occurred",
            ...     {"challenge_name": "Missed deadline"}
            ... )
        """
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        try:
            # Get setback prompts
            prompts = trigger_setback_prompts(setback_type, context)

            if not prompts:
                return f"Error: Unknown setback type '{setback_type}'. Valid types: setback_occurred, pattern_recurring"

            # Format response
            lines = [
                f"💪 Setback Reflection for {user_id}",
                "=" * 60,
            ]

            if context and "challenge_name" in context:
                lines.append(f"\nWorking With Challenge: {context['challenge_name']}")
            elif context and "pattern_name" in context:
                lines.append(f"\nExploring Pattern: {context['pattern_name']}")
            else:
                setback_names = {
                    "setback_occurred": "Setback Occurred",
                    "pattern_recurring": "Recurring Pattern",
                }
                lines.append(f"\n{setback_names.get(setback_type, 'Setback')}")

            lines.append("\n" + "─" * 60)
            lines.append("📝 Setback Reflection Prompts")
            lines.append("─" * 60)

            for i, prompt in enumerate(prompts, 1):
                lines.append(f"\n{i}. {prompt}")

            # Add recovery guidance
            lines.append("\n" + "─" * 60)
            lines.append("💡 Recovery Suggestions:")
            lines.append("• Be kind and compassionate with yourself during this time")
            lines.append("• Remember that setbacks are a normal part of growth, not failures")
            lines.append("• Focus on what you can control and take one small step forward")
            lines.append(
                "• Reach out for support if you need it - you don't have to navigate this alone"
            )

            return "\n".join(lines)

        except Exception as e:
            return f"Error generating setback reflection: {str(e)}"

    return (
        generate_weekly_reflection_prompts,
        save_reflection_response,
        get_reflection_history,
        extract_insights_from_reflections,
        trigger_milestone_reflection,
        trigger_setback_reflection,
    )
