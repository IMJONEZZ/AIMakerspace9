"""
Habit Tracking System for AI Life Coach.

This module implements comprehensive habit tracking based on:
- Atomic Habits framework by James Clear
- Habit Loop: Cue → Craving → Response → Reward
- Evidence-based habit formation research (2-5 months to automaticity)
- Streak tracking and strength calculation algorithms

Key Features:
1. Habit Data Model - Trigger, Action, Reward structure
2. Streak Tracking - Current streak, longest streak, completion history
3. Strength Scoring - 0-100 habit strength calculation
4. Habit Stacking - Recommendations based on existing habits
5. Domain Grouping - Group habits by life domains (health, career, etc.)
6. Review Workflow - Periodic habit assessment and adjustment

Research Basis:
- Habit formation takes 18-254 days (avg 66 days) per Lally et al.
- 21-day rule is a myth (originated from Maxwell Maltz, 1960)
- Automaticity develops gradually over 2-5 months
- Streak psychology: consistency > perfection, "never miss twice"
"""

from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Set
from enum import Enum
import json
import math

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
# Habit Constants and Configuration
# ==============================================================================


class HabitFrequency(str, Enum):
    """Habit frequency types."""

    DAILY = "daily"
    WEEKLY = "weekly"
    WEEKDAYS = "weekdays"
    WEEKENDS = "weekends"
    CUSTOM = "custom"


class HabitDomain(str, Enum):
    """Life domains for habit categorization."""

    HEALTH = "health"
    CAREER = "career"
    RELATIONSHIPS = "relationships"
    FINANCE = "finance"
    PERSONAL_GROWTH = "personal_growth"
    MINDFULNESS = "mindfulness"
    PRODUCTIVITY = "productivity"
    SOCIAL = "social"


class HabitStatus(str, Enum):
    """Habit status states."""

    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


# Habit formation research constants (based on Lally et al. study)
HABIT_FORMATION_RESEARCH = {
    "min_days": 18,
    "max_days": 254,
    "median_days": 66,
    "avg_days": 66,
    "automaticity_threshold": 0.8,  # 80% automaticity = strong habit
}

# Strength calculation weights
STRENGTH_WEIGHTS = {
    "consistency": 0.35,  # 35% - consistent completion
    "streak": 0.25,  # 25% - current streak length
    "duration": 0.20,  # 20% - how long habit has been tracked
    "frequency_adherence": 0.15,  # 15% - adherence to target frequency
    "recovery": 0.05,  # 5% - ability to recover from missed days
}

# Domain colors for visualization
DOMAIN_COLORS = {
    HabitDomain.HEALTH: "🟢",
    HabitDomain.CAREER: "🔵",
    HabitDomain.RELATIONSHIPS: "🟣",
    HabitDomain.FINANCE: "🟡",
    HabitDomain.PERSONAL_GROWTH: "🟠",
    HabitDomain.MINDFULNESS: "⚪",
    HabitDomain.PRODUCTIVITY: "🔴",
    HabitDomain.SOCIAL: "🩷",
}

# Streak milestones for celebration
STREAK_MILESTONES = [7, 21, 30, 60, 90, 180, 365]

# Visual indicators for streak levels
STREAK_INDICATORS = {
    "fire": "🔥",
    "spark": "✨",
    "star": "⭐",
    "trophy": "🏆",
    "crown": "👑",
}

# ==============================================================================
# Habit Data Models
# ==============================================================================


class Habit:
    """Represents a single habit with trigger-action-reward structure."""

    def __init__(
        self,
        habit_id: str,
        user_id: str,
        name: str,
        domain: str = HabitDomain.HEALTH.value,
        frequency: str = HabitFrequency.DAILY.value,
        # Habit Loop Components
        cue: Optional[str] = None,
        action: Optional[str] = None,
        reward: Optional[str] = None,
        # Habit Stacking
        stack_after: Optional[str] = None,
        # Configuration
        target_days: Optional[List[int]] = None,  # 0=Monday, 6=Sunday
        reminder_time: Optional[str] = None,
        notes: Optional[str] = None,
        # Metadata
        created_at: Optional[str] = None,
        status: str = HabitStatus.ACTIVE.value,
    ):
        self.habit_id = habit_id
        self.user_id = user_id
        self.name = name
        self.domain = domain
        self.frequency = frequency
        # Habit Loop
        self.cue = cue or ""
        self.action = action or name
        self.reward = reward or ""
        # Stacking
        self.stack_after = stack_after
        # Configuration
        self.target_days = target_days or self._default_target_days(frequency)
        self.reminder_time = reminder_time
        self.notes = notes or ""
        # Metadata
        self.created_at = created_at or datetime.now().isoformat()
        self.status = status

    def _default_target_days(self, frequency: str) -> List[int]:
        """Get default target days based on frequency."""
        if frequency == HabitFrequency.DAILY.value:
            return [0, 1, 2, 3, 4, 5, 6]
        elif frequency == HabitFrequency.WEEKDAYS.value:
            return [0, 1, 2, 3, 4]
        elif frequency == HabitFrequency.WEEKENDS.value:
            return [5, 6]
        elif frequency == HabitFrequency.WEEKLY.value:
            return [0]  # Default to Monday
        else:
            return [0, 1, 2, 3, 4, 5, 6]

    def to_dict(self) -> Dict[str, Any]:
        """Convert habit to dictionary."""
        return {
            "habit_id": self.habit_id,
            "user_id": self.user_id,
            "name": self.name,
            "domain": self.domain,
            "frequency": self.frequency,
            "cue": self.cue,
            "action": self.action,
            "reward": self.reward,
            "stack_after": self.stack_after,
            "target_days": self.target_days,
            "reminder_time": self.reminder_time,
            "notes": self.notes,
            "created_at": self.created_at,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Habit":
        """Create habit from dictionary."""
        return cls(
            habit_id=data.get("habit_id", ""),
            user_id=data.get("user_id", ""),
            name=data.get("name", ""),
            domain=data.get("domain", HabitDomain.HEALTH.value),
            frequency=data.get("frequency", HabitFrequency.DAILY.value),
            cue=data.get("cue"),
            action=data.get("action"),
            reward=data.get("reward"),
            stack_after=data.get("stack_after"),
            target_days=data.get("target_days"),
            reminder_time=data.get("reminder_time"),
            notes=data.get("notes"),
            created_at=data.get("created_at"),
            status=data.get("status", HabitStatus.ACTIVE.value),
        )


class HabitEntry:
    """Represents a single habit completion entry."""

    def __init__(
        self,
        entry_id: str,
        habit_id: str,
        user_id: str,
        completed_at: Optional[str] = None,
        completion_date: Optional[str] = None,
        notes: Optional[str] = None,
        mood: Optional[int] = None,  # 1-10 mood when completing
        difficulty: Optional[int] = None,  # 1-10 difficulty rating
    ):
        self.entry_id = entry_id
        self.habit_id = habit_id
        self.user_id = user_id
        self.completed_at = completed_at or datetime.now().isoformat()
        self.completion_date = completion_date or date.today().isoformat()
        self.notes = notes or ""
        self.mood = mood
        self.difficulty = difficulty

    def to_dict(self) -> Dict[str, Any]:
        """Convert entry to dictionary."""
        return {
            "entry_id": self.entry_id,
            "habit_id": self.habit_id,
            "user_id": self.user_id,
            "completed_at": self.completed_at,
            "completion_date": self.completion_date,
            "notes": self.notes,
            "mood": self.mood,
            "difficulty": self.difficulty,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HabitEntry":
        """Create entry from dictionary."""
        return cls(
            entry_id=data.get("entry_id", ""),
            habit_id=data.get("habit_id", ""),
            user_id=data.get("user_id", ""),
            completed_at=data.get("completed_at"),
            completion_date=data.get("completion_date"),
            notes=data.get("notes"),
            mood=data.get("mood"),
            difficulty=data.get("difficulty"),
        )


class HabitStats:
    """Statistics for a habit."""

    def __init__(
        self,
        habit_id: str,
        total_completions: int = 0,
        current_streak: int = 0,
        longest_streak: int = 0,
        strength_score: float = 0.0,  # 0-100
        completion_rate: float = 0.0,  # 0-1
        last_completed: Optional[str] = None,
        days_active: int = 0,
    ):
        self.habit_id = habit_id
        self.total_completions = total_completions
        self.current_streak = current_streak
        self.longest_streak = longest_streak
        self.strength_score = strength_score
        self.completion_rate = completion_rate
        self.last_completed = last_completed
        self.days_active = days_active

    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            "habit_id": self.habit_id,
            "total_completions": self.total_completions,
            "current_streak": self.current_streak,
            "longest_streak": self.longest_streak,
            "strength_score": self.strength_score,
            "completion_rate": self.completion_rate,
            "last_completed": self.last_completed,
            "days_active": self.days_active,
        }


# ==============================================================================
# Helper Functions
# ==============================================================================


def generate_habit_id() -> str:
    """Generate unique habit ID."""
    return f"habit_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(datetime.now()) % 10000}"


def generate_entry_id() -> str:
    """Generate unique entry ID."""
    return f"entry_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(datetime.now()) % 10000}"


def parse_date(date_str: str) -> date:
    """Parse date string to date object."""
    return datetime.fromisoformat(date_str).date()


def get_target_dates(
    frequency: str, target_days: List[int], start_date: date, end_date: date
) -> List[date]:
    """Get all target dates for a habit within a date range."""
    dates = []
    current = start_date

    while current <= end_date:
        # Check if current day is a target day (0=Monday, 6=Sunday)
        if current.weekday() in target_days:
            dates.append(current)
        current += timedelta(days=1)

    return dates


def calculate_streak(
    completion_dates: List[date], target_days: Optional[List[int]] = None
) -> Tuple[int, int]:
    """
    Calculate current and longest streak.

    Args:
        completion_dates: List of dates when habit was completed
        target_days: Optional list of target weekdays (0=Monday, 6=Sunday)

    Returns:
        Tuple of (current_streak, longest_streak)
    """
    if not completion_dates:
        return 0, 0

    # Sort dates
    sorted_dates = sorted(completion_dates)

    # Calculate longest streak
    longest_streak = 1
    current_streak_count = 1

    for i in range(1, len(sorted_dates)):
        prev_date = sorted_dates[i - 1]
        curr_date = sorted_dates[i]

        # Check if consecutive (accounting for target days)
        if target_days:
            # Get expected next date based on target days
            expected_next = _get_next_target_date(prev_date, target_days)
            if curr_date == expected_next:
                current_streak_count += 1
                longest_streak = max(longest_streak, current_streak_count)
            elif curr_date > expected_next:
                # Streak broken
                current_streak_count = 1
        else:
            # Daily habit - check if consecutive calendar days
            if (curr_date - prev_date).days == 1:
                current_streak_count += 1
                longest_streak = max(longest_streak, current_streak_count)
            elif (curr_date - prev_date).days > 1:
                # Streak broken
                current_streak_count = 1

    # Calculate current streak (from most recent completion)
    current_streak = 0
    today = date.today()

    if sorted_dates:
        most_recent = sorted_dates[-1]

        # Check if most recent completion is today or acceptable range
        days_since_last = (today - most_recent).days

        if target_days:
            # For non-daily habits, allow more leeway
            # Current streak is valid if last completion was recent enough
            if days_since_last <= _get_max_gap(target_days):
                # Count streak backwards from most recent
                current_streak = 1
                for i in range(len(sorted_dates) - 2, -1, -1):
                    expected_prev = _get_prev_target_date(sorted_dates[i + 1], target_days)
                    if sorted_dates[i] == expected_prev:
                        current_streak += 1
                    else:
                        break
        else:
            # Daily habit
            if days_since_last <= 1:  # Today or yesterday
                current_streak = 1
                for i in range(len(sorted_dates) - 2, -1, -1):
                    if (sorted_dates[i + 1] - sorted_dates[i]).days == 1:
                        current_streak += 1
                    else:
                        break

    return current_streak, longest_streak


def _get_next_target_date(from_date: date, target_days: List[int]) -> date:
    """Get the next target date after from_date."""
    next_date = from_date + timedelta(days=1)
    while next_date.weekday() not in target_days:
        next_date += timedelta(days=1)
    return next_date


def _get_prev_target_date(from_date: date, target_days: List[int]) -> date:
    """Get the previous target date before from_date."""
    prev_date = from_date - timedelta(days=1)
    while prev_date.weekday() not in target_days:
        prev_date -= timedelta(days=1)
    return prev_date


def _get_max_gap(target_days: List[int]) -> int:
    """Get maximum allowed gap between completions based on frequency."""
    if len(target_days) >= 6:
        return 2  # Daily or near-daily
    elif len(target_days) >= 5:
        return 3  # Weekdays
    elif len(target_days) >= 2:
        return 4  # Few times per week
    else:
        return 7  # Weekly


def calculate_habit_strength(
    total_completions: int,
    current_streak: int,
    longest_streak: int,
    days_active: int,
    completion_rate: float,
    target_days: List[int],
) -> float:
    """
    Calculate habit strength score (0-100) based on multiple factors.

    Algorithm based on habit formation research:
    - Consistency (35%): Overall completion rate
    - Streak (25%): Current streak length relative to formation threshold
    - Duration (20%): Days active relative to automaticity threshold (~66 days)
    - Frequency Adherence (15%): Adherence to target frequency
    - Recovery (5%): Ability to maintain habits after breaks

    Args:
        total_completions: Total number of completions
        current_streak: Current streak length
        longest_streak: Longest streak achieved
        days_active: Number of days habit has been active
        completion_rate: Overall completion rate (0-1)
        target_days: List of target weekdays

    Returns:
        Habit strength score (0-100)
    """
    # Consistency score (35%)
    consistency_score = completion_rate * 100

    # Streak score (25%) - logarithmic scale to reward longer streaks
    # 7 days = 25%, 30 days = 60%, 66 days = 85%, 100+ days = 95%+
    if current_streak >= 100:
        streak_score = 95
    elif current_streak >= 66:
        streak_score = 85 + (current_streak - 66) * 0.3
    elif current_streak >= 30:
        streak_score = 60 + (current_streak - 30) * 0.8
    elif current_streak >= 7:
        streak_score = 25 + (current_streak - 7) * 1.4
    else:
        streak_score = current_streak * 3.5

    # Duration score (20%) - based on automaticity research
    # 66 days = automaticity threshold
    if days_active >= 254:  # Max from research
        duration_score = 100
    elif days_active >= 66:
        duration_score = 70 + (days_active - 66) * 0.16
    elif days_active >= 21:
        duration_score = 35 + (days_active - 21) * 0.8
    else:
        duration_score = days_active * 1.67

    # Frequency adherence (15%) - already reflected in completion rate
    # but can be adjusted for frequency complexity
    freq_factor = 7 / len(target_days) if target_days else 1
    frequency_score = min(100, completion_rate * 100 * freq_factor)

    # Recovery score (5%) - based on longest streak relative to current
    if longest_streak > 0:
        recovery_ratio = current_streak / longest_streak
        recovery_score = min(100, recovery_ratio * 100)
    else:
        recovery_score = 100

    # Calculate weighted score
    strength = (
        consistency_score * STRENGTH_WEIGHTS["consistency"]
        + streak_score * STRENGTH_WEIGHTS["streak"]
        + duration_score * STRENGTH_WEIGHTS["duration"]
        + frequency_score * STRENGTH_WEIGHTS["frequency_adherence"]
        + recovery_score * STRENGTH_WEIGHTS["recovery"]
    )

    return round(min(100, max(0, strength)), 1)


def get_streak_visual(streak: int) -> str:
    """Get visual indicator for streak level."""
    if streak >= 365:
        return f"{STREAK_INDICATORS['crown']}" * min(3, streak // 365)
    elif streak >= 100:
        return f"{STREAK_INDICATORS['trophy']}" * min(3, streak // 100)
    elif streak >= 30:
        return f"{STREAK_INDICATORS['star']}" * min(3, streak // 30)
    elif streak >= 7:
        return f"{STREAK_INDICATORS['fire']}" * min(3, streak // 7)
    elif streak >= 3:
        return STREAK_INDICATORS["spark"]
    else:
        return ""


def get_strength_level(strength: float) -> Tuple[str, str]:
    """Get strength level label and emoji."""
    if strength >= 80:
        return "Strong", "💪"
    elif strength >= 60:
        return "Developing", "🌱"
    elif strength >= 40:
        return "Building", "🔨"
    elif strength >= 20:
        return "Starting", "🌟"
    else:
        return "New", "🆕"


def generate_calendar_visual(
    completion_dates: List[date],
    year: int,
    month: int,
) -> str:
    """Generate ASCII calendar with habit completion markers."""
    # Get first day of month and number of days
    first_day = date(year, month, 1)
    if month == 12:
        last_day = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(year, month + 1, 1) - timedelta(days=1)

    # Create set of completion dates for quick lookup
    completion_set = set(completion_dates)

    # Build calendar
    lines = []
    lines.append(f"{first_day.strftime('%B %Y')}")
    lines.append("Mo Tu We Th Fr Sa Su")

    # Pad start
    current_line = ""
    start_weekday = first_day.weekday()  # 0=Monday
    current_line += "   " * start_weekday

    # Fill in days
    current_date = first_day
    while current_date <= last_day:
        day_str = f"{current_date.day:2d}"

        # Mark completion
        if current_date in completion_set:
            day_str = f"[{current_date.day:2d}]"
        elif current_date > date.today():
            day_str = "  "

        current_line += day_str + " "

        if current_date.weekday() == 6:  # Sunday
            lines.append(current_line)
            current_line = ""

        current_date += timedelta(days=1)

    if current_line:
        lines.append(current_line)

    lines.append("\n[XX] = Completed  XX = Not completed")

    return "\n".join(lines)


def suggest_habit_stack(
    existing_habits: List[Habit], new_habit_domain: str
) -> List[Dict[str, Any]]:
    """
    Suggest habit stacking opportunities based on existing habits.

    Based on Atomic Habits: "After [CURRENT HABIT], I will [NEW HABIT]."

    Args:
        existing_habits: List of user's existing habits
        new_habit_domain: Domain of the new habit being created

    Returns:
        List of stacking suggestions with scores
    """
    suggestions = []

    # Score existing habits for stacking potential
    for habit in existing_habits:
        if habit.status != HabitStatus.ACTIVE.value:
            continue

        score = 0
        reasons = []

        # Higher strength habits make better anchors
        if hasattr(habit, "strength_score"):
            score += habit.strength_score * 0.3
            if habit.strength_score >= 60:
                reasons.append("Strong, established habit")

        # Same domain habits stack well
        if habit.domain == new_habit_domain:
            score += 25
            reasons.append("Same domain - creates identity reinforcement")

        # Daily habits are better anchors
        if habit.frequency == HabitFrequency.DAILY.value:
            score += 15
            reasons.append("Daily habit - consistent anchor")

        # Morning habits often work well as anchors
        if habit.reminder_time:
            hour = int(habit.reminder_time.split(":")[0])
            if 5 <= hour <= 9:
                score += 10
                reasons.append("Morning habit - strong routine anchor")

        # Habits that are already stacked indicate user likes stacking
        if habit.stack_after:
            score += 5
            reasons.append("Already using habit stacking")

        if score > 20:  # Only include reasonable suggestions
            suggestions.append(
                {
                    "habit": habit,
                    "score": score,
                    "reasons": reasons,
                    "stacking_template": f"After I {habit.action}, I will [NEW HABIT].",
                }
            )

    # Sort by score
    suggestions.sort(key=lambda x: x["score"], reverse=True)

    return suggestions[:5]  # Return top 5


# ==============================================================================
# Habit Tools Factory
# ==============================================================================


def create_habit_tools(backend=None):
    """
    Create habit tracking tools with shared backend instance.

    These tools enable comprehensive habit tracking based on:
    - Atomic Habits framework (Cue-Craving-Response-Reward)
    - Evidence-based habit formation research
    - Streak tracking and strength calculation
    - Habit stacking recommendations

    Args:
        backend: Optional FilesystemBackend instance. If None, uses get_backend()

    Returns:
        Tuple of habit tools
    """
    if backend is None:
        backend = get_backend()

    # Get the workspace directory path from backend
    workspace_path = Path(backend.root_dir) if hasattr(backend, "root_dir") else Path("workspace")

    # --------------------------------------------------------------------------
    # Helper functions for tool implementation
    # --------------------------------------------------------------------------

    def _save_habit(habit: Habit) -> None:
        """Save habit to file."""
        json_content = json.dumps(habit.to_dict(), indent=2)
        path = f"habits/{habit.user_id}/{habit.habit_id}.json"

        if hasattr(backend, "write_file"):
            backend.write_file(path, json_content)
        else:
            file_path = workspace_path / path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(json_content)

    def _load_habit(user_id: str, habit_id: str) -> Optional[Habit]:
        """Load habit from file."""
        path = f"habits/{user_id}/{habit_id}.json"

        try:
            if hasattr(backend, "read_file"):
                content = backend.read_file(path)
            else:
                file_path = workspace_path / path
                if not file_path.exists():
                    return None
                content = file_path.read_text()

            return Habit.from_dict(json.loads(content))
        except Exception:
            return None

    def _load_all_habits(user_id: str) -> List[Habit]:
        """Load all habits for a user."""
        habits = []
        habits_dir = workspace_path / "habits" / user_id

        if not habits_dir.exists():
            return habits

        for habit_file in habits_dir.glob("habit_*.json"):
            try:
                if hasattr(backend, "read_file"):
                    content = backend.read_file(f"habits/{user_id}/{habit_file.name}")
                else:
                    content = habit_file.read_text()

                habit = Habit.from_dict(json.loads(content))
                if habit.user_id == user_id:
                    habits.append(habit)
            except Exception:
                continue

        return habits

    def _save_entry(entry: HabitEntry) -> None:
        """Save habit entry to file."""
        json_content = json.dumps(entry.to_dict(), indent=2)
        path = f"habits/{entry.user_id}/entries/{entry.habit_id}/{entry.entry_id}.json"

        if hasattr(backend, "write_file"):
            backend.write_file(path, json_content)
        else:
            file_path = workspace_path / path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(json_content)

    def _load_entries(user_id: str, habit_id: str) -> List[HabitEntry]:
        """Load all entries for a habit."""
        entries = []
        entries_dir = workspace_path / "habits" / user_id / "entries" / habit_id

        if not entries_dir.exists():
            return entries

        for entry_file in entries_dir.glob("entry_*.json"):
            try:
                if hasattr(backend, "read_file"):
                    content = backend.read_file(
                        f"habits/{user_id}/entries/{habit_id}/{entry_file.name}"
                    )
                else:
                    content = entry_file.read_text()

                entry = HabitEntry.from_dict(json.loads(content))
                entries.append(entry)
            except Exception:
                continue

        return entries

    def _calculate_habit_stats(habit: Habit) -> HabitStats:
        """Calculate statistics for a habit."""
        entries = _load_entries(habit.user_id, habit.habit_id)

        total_completions = len(entries)
        completion_dates = [parse_date(e.completion_date) for e in entries]

        # Calculate streaks
        current_streak, longest_streak = calculate_streak(completion_dates, habit.target_days)

        # Calculate days active
        created_date = parse_date(habit.created_at)
        days_active = (date.today() - created_date).days + 1

        # Calculate completion rate
        target_dates = get_target_dates(
            habit.frequency, habit.target_days, created_date, date.today()
        )
        expected_completions = len(target_dates)
        completion_rate = (
            total_completions / expected_completions if expected_completions > 0 else 0
        )

        # Calculate strength score
        strength_score = calculate_habit_strength(
            total_completions=total_completions,
            current_streak=current_streak,
            longest_streak=longest_streak,
            days_active=days_active,
            completion_rate=completion_rate,
            target_days=habit.target_days,
        )

        last_completed = entries[-1].completion_date if entries else None

        return HabitStats(
            habit_id=habit.habit_id,
            total_completions=total_completions,
            current_streak=current_streak,
            longest_streak=longest_streak,
            strength_score=strength_score,
            completion_rate=completion_rate,
            last_completed=last_completed,
            days_active=days_active,
        )

    # --------------------------------------------------------------------------
    # Tool 1: Create Habit
    # --------------------------------------------------------------------------

    @tool
    def create_habit(
        user_id: str,
        name: str,
        domain: str = "health",
        frequency: str = "daily",
        cue: Optional[str] = None,
        action: Optional[str] = None,
        reward: Optional[str] = None,
        stack_after: Optional[str] = None,
        reminder_time: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> str:
        """Create a new habit with trigger-action-reward structure.

        This tool creates a habit using the Atomic Habits framework:
        - Cue: What triggers the habit (time, location, emotional state)
        - Action: The behavior you want to perform
        - Reward: The benefit you get from completing the habit

        Args:
            user_id: The user's unique identifier
            name: Name of the habit (e.g., "Morning Meditation")
            domain: Life domain (health, career, relationships, finance,
                   personal_growth, mindfulness, productivity, social)
            frequency: How often (daily, weekly, weekdays, weekends, custom)
            cue: What triggers this habit? (time, location, preceding action)
            action: The specific behavior (defaults to habit name)
            reward: What makes this satisfying? (immediate benefit)
            stack_after: Optional habit to stack this after (habit ID or name)
            reminder_time: Optional reminder time (HH:MM format)
            notes: Additional notes about this habit

        Returns:
            Confirmation with habit details and next steps.
            Saved to habits/{user_id}/{habit_id}.json

        Example:
            >>> create_habit(
            ...     user_id="user_123",
            ...     name="10-Minute Morning Walk",
            ...     domain="health",
            ...     cue="After I put on my shoes",
            ...     action="Walk for 10 minutes outside",
            ...     reward="Feel energized and listen to music",
            ...     stack_after="Putting on shoes"
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not name or not isinstance(name, str):
            return "Error: name must be a non-empty string"

        # Validate domain
        valid_domains = [d.value for d in HabitDomain]
        if domain not in valid_domains:
            return f"Error: domain must be one of {valid_domains}"

        # Validate frequency
        valid_frequencies = [f.value for f in HabitFrequency]
        if frequency not in valid_frequencies:
            return f"Error: frequency must be one of {valid_frequencies}"

        try:
            # Create habit
            habit = Habit(
                habit_id=generate_habit_id(),
                user_id=user_id,
                name=name,
                domain=domain,
                frequency=frequency,
                cue=cue or "",
                action=action or name,
                reward=reward or "",
                stack_after=stack_after,
                reminder_time=reminder_time,
                notes=notes or "",
            )

            # Save habit
            _save_habit(habit)

            # Get habit stacking suggestions
            existing_habits = _load_all_habits(user_id)
            stack_suggestions = suggest_habit_stack(existing_habits, domain)

            # Format response
            lines = [
                f"✅ Habit Created: {name}",
                "=" * 60,
                f"\n📋 Habit ID: {habit.habit_id}",
                f"📁 Domain: {domain.replace('_', ' ').title()}",
                f"🔄 Frequency: {frequency.title()}",
            ]

            # Show habit loop
            lines.append("\n🔄 The Habit Loop")
            lines.append("-" * 40)
            lines.append(f"Cue: {habit.cue or 'Not set - define your trigger!'}")
            lines.append(f"Action: {habit.action}")
            lines.append(f"Reward: {habit.reward or 'Not set - define your benefit!'}")

            if stack_after:
                lines.append(f"\n🔗 Stack After: {stack_after}")
                lines.append(f"   Template: 'After I {stack_after}, I will {action or name}'")

            if reminder_time:
                lines.append(f"\n⏰ Reminder: {reminder_time}")

            # Show stacking suggestions
            if stack_suggestions and not stack_after:
                lines.append("\n💡 Habit Stacking Suggestions:")
                for i, suggestion in enumerate(stack_suggestions[:3], 1):
                    lines.append(f"\n{i}. Stack after: {suggestion['habit'].name}")
                    lines.append(f"   Score: {suggestion['score']:.0f}/100")
                    lines.append(f"   Template: {suggestion['stacking_template']}")
                    lines.append(f"   Why: {', '.join(suggestion['reasons'][:2])}")

            # Show next steps
            lines.append("\n🎯 Next Steps:")
            lines.append("1. Log your first completion using log_habit_completion()")
            lines.append("2. Start small - focus on consistency, not perfection")
            lines.append("3. Track your streak using get_habit_streaks()")
            lines.append(f"4. Review progress in {HABIT_FORMATION_RESEARCH['median_days']} days")

            # Research note
            lines.append(f"\n📊 Research Note:")
            lines.append(
                f"   Habits take {HABIT_FORMATION_RESEARCH['min_days']}-{HABIT_FORMATION_RESEARCH['max_days']}"
            )
            lines.append(f"   days to form (avg: {HABIT_FORMATION_RESEARCH['median_days']} days).")
            lines.append(f"   Be patient and consistent!")

            lines.append(f"\n💾 Saved to: habits/{user_id}/{habit.habit_id}.json")

            return "\n".join(lines)

        except Exception as e:
            return f"Error creating habit: {str(e)}"

    # --------------------------------------------------------------------------
    # Tool 2: Log Habit Completion
    # --------------------------------------------------------------------------

    @tool
    def log_habit_completion(
        user_id: str,
        habit_id: str,
        completion_date: Optional[str] = None,
        notes: Optional[str] = None,
        mood: Optional[int] = None,
        difficulty: Optional[int] = None,
    ) -> str:
        """Log completion of a habit.

        Records that a habit was completed on a specific date with optional
        context (mood, difficulty, notes). Updates streaks automatically.

        Args:
            user_id: The user's unique identifier
            habit_id: ID of the habit being completed
            completion_date: Optional date (YYYY-MM-DD, defaults to today)
            notes: Optional notes about this completion
            mood: Optional mood rating when completing (1-10)
            difficulty: Optional difficulty rating (1-10)

        Returns:
            Confirmation with streak info and milestone celebrations.
            Saved to habits/{user_id}/entries/{habit_id}/{entry_id}.json

        Example:
            >>> log_habit_completion(
            ...     user_id="user_123",
            ...     habit_id="habit_20240115_083000_1234",
            ...     notes="Felt great today!"
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not habit_id or not isinstance(habit_id, str):
            return "Error: habit_id must be a non-empty string"

        # Validate mood and difficulty
        if mood is not None and (not isinstance(mood, int) or mood < 1 or mood > 10):
            return "Error: mood must be an integer between 1 and 10"
        if difficulty is not None and (
            not isinstance(difficulty, int) or difficulty < 1 or difficulty > 10
        ):
            return "Error: difficulty must be an integer between 1 and 10"

        try:
            # Load habit
            habit = _load_habit(user_id, habit_id)
            if not habit:
                return f"Error: Habit '{habit_id}' not found for user '{user_id}'"

            # Parse completion date
            if completion_date:
                try:
                    comp_date = datetime.fromisoformat(completion_date).date()
                except ValueError:
                    return "Error: completion_date must be in YYYY-MM-DD format"
            else:
                comp_date = date.today()

            # Check if already completed for this date
            existing_entries = _load_entries(user_id, habit_id)
            for entry in existing_entries:
                if parse_date(entry.completion_date) == comp_date:
                    return f"Habit '{habit.name}' already logged for {comp_date}. Use a different date or update existing entry."

            # Create entry
            entry = HabitEntry(
                entry_id=generate_entry_id(),
                habit_id=habit_id,
                user_id=user_id,
                completion_date=comp_date.isoformat(),
                notes=notes or "",
                mood=mood,
                difficulty=difficulty,
            )

            # Save entry
            _save_entry(entry)

            # Calculate updated stats
            stats = _calculate_habit_stats(habit)

            # Format response
            lines = [
                f"✅ Habit Completed: {habit.name}",
                "=" * 60,
                f"\n📅 Date: {comp_date}",
            ]

            # Show streak info
            streak_visual = get_streak_visual(stats.current_streak)
            lines.append(f"\n🔥 Current Streak: {stats.current_streak} days {streak_visual}")

            if stats.longest_streak > stats.current_streak:
                lines.append(f"🏆 Longest Streak: {stats.longest_streak} days")

            # Check for milestones
            if stats.current_streak in STREAK_MILESTONES:
                lines.append(f"\n🎉 MILESTONE: {stats.current_streak} day streak! Keep it up!")

            # Show strength score
            level, emoji = get_strength_level(stats.strength_score)
            lines.append(f"\n💪 Habit Strength: {stats.strength_score:.1f}/100 ({emoji} {level})")

            # Show completion rate
            lines.append(f"📊 Completion Rate: {stats.completion_rate * 100:.1f}%")
            lines.append(f"📈 Total Completions: {stats.total_completions}")

            # Show optional context
            if mood:
                lines.append(f"😊 Mood: {mood}/10")
            if difficulty:
                lines.append(f"⚡ Difficulty: {difficulty}/10")
            if notes:
                lines.append(f"📝 Notes: {notes}")

            # Encouragement based on streak
            lines.append("\n💬 Encouragement:")
            if stats.current_streak == 1:
                lines.append("   Every journey begins with a single step. Great start!")
            elif stats.current_streak < 7:
                lines.append("   Building momentum! Consistency is key.")
            elif stats.current_streak < 21:
                lines.append("   You're building a solid habit. Keep going!")
            elif stats.current_streak < 66:
                lines.append("   Impressive dedication! You're making this automatic.")
            else:
                lines.append("   Outstanding! This habit is now part of who you are.")

            lines.append(
                f"\n💾 Entry saved to: habits/{user_id}/entries/{habit_id}/{entry.entry_id}.json"
            )

            return "\n".join(lines)

        except Exception as e:
            return f"Error logging habit completion: {str(e)}"

    # --------------------------------------------------------------------------
    # Tool 3: Get Habit Streaks
    # --------------------------------------------------------------------------

    @tool
    def get_habit_streaks(
        user_id: str,
        habit_id: Optional[str] = None,
    ) -> str:
        """Get streak information for habits.

        Shows current streaks, longest streaks, and visual indicators
        for all habits or a specific habit.

        Args:
            user_id: The user's unique identifier
            habit_id: Optional specific habit ID (shows all if not provided)

        Returns:
            Streak information with visual indicators and milestones.

        Example:
            >>> get_habit_streaks(user_id="user_123")
            >>> get_habit_streaks(user_id="user_123", habit_id="habit_20240115_083000_1234")
        """
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        try:
            if habit_id:
                # Get specific habit
                habit = _load_habit(user_id, habit_id)
                if not habit:
                    return f"Error: Habit '{habit_id}' not found for user '{user_id}'"
                habits = [habit]
            else:
                # Get all habits
                habits = _load_all_habits(user_id)

            if not habits:
                return f"No habits found for user '{user_id}'. Create a habit first using create_habit()."

            # Calculate stats for each habit
            habit_stats = []
            for habit in habits:
                if habit.status == HabitStatus.ACTIVE.value:
                    stats = _calculate_habit_stats(habit)
                    habit_stats.append((habit, stats))

            # Sort by current streak (descending)
            habit_stats.sort(key=lambda x: x[1].current_streak, reverse=True)

            # Format response
            lines = [
                f"🔥 Habit Streaks for {user_id}",
                "=" * 60,
            ]

            # Summary stats
            total_habits = len(habit_stats)
            active_streaks = sum(1 for _, s in habit_stats if s.current_streak > 0)
            total_completions = sum(s.total_completions for _, s in habit_stats)

            lines.append(f"\n📊 Summary:")
            lines.append(f"   Active Habits: {total_habits}")
            lines.append(f"   Active Streaks: {active_streaks}")
            lines.append(f"   Total Completions: {total_completions}")

            # Individual habit streaks
            lines.append("\n📈 Individual Habit Streaks:")
            lines.append("-" * 60)

            for habit, stats in habit_stats:
                domain_emoji = DOMAIN_COLORS.get(HabitDomain(habit.domain), "⚪")
                streak_visual = get_streak_visual(stats.current_streak)

                lines.append(f"\n{domain_emoji} {habit.name}")
                lines.append(f"   Current: {stats.current_streak} days {streak_visual}")
                lines.append(f"   Longest: {stats.longest_streak} days")
                lines.append(f"   Total: {stats.total_completions} completions")

                # Show next milestone
                next_milestone = None
                for m in STREAK_MILESTONES:
                    if m > stats.current_streak:
                        next_milestone = m
                        break

                if next_milestone:
                    days_to_go = next_milestone - stats.current_streak
                    lines.append(
                        f"   🎯 Next milestone: {next_milestone} days ({days_to_go} to go)"
                    )

            # Streak tips
            lines.append("\n💡 Streak Tips:")
            lines.append("• Never miss twice - if you break a streak, restart immediately")
            lines.append("• Consistency beats perfection - small daily actions add up")
            lines.append("• Visualize your progress - tracking reinforces the habit")

            return "\n".join(lines)

        except Exception as e:
            return f"Error getting habit streaks: {str(e)}"

    # --------------------------------------------------------------------------
    # Tool 4: Calculate Habit Strength
    # --------------------------------------------------------------------------

    @tool
    def calculate_habit_strength_score(
        user_id: str,
        habit_id: Optional[str] = None,
    ) -> str:
        """Calculate habit strength score (0-100) based on tracking data.

        The strength score is calculated using multiple factors:
        - Consistency (35%): Overall completion rate
        - Streak (25%): Current streak length
        - Duration (20%): How long you've been tracking
        - Frequency Adherence (15%): Meeting target frequency
        - Recovery (5%): Ability to restart after breaks

        Based on habit formation research showing automaticity develops
        over 2-5 months (avg 66 days) of consistent practice.

        Args:
            user_id: The user's unique identifier
            habit_id: Optional specific habit ID (shows all if not provided)

        Returns:
            Detailed strength analysis with breakdown and recommendations.

        Example:
            >>> calculate_habit_strength_score(user_id="user_123")
        """
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        try:
            if habit_id:
                habit = _load_habit(user_id, habit_id)
                if not habit:
                    return f"Error: Habit '{habit_id}' not found for user '{user_id}'"
                habits = [habit]
            else:
                habits = _load_all_habits(user_id)

            if not habits:
                return f"No habits found for user '{user_id}'. Create a habit first."

            # Get active habits
            active_habits = [h for h in habits if h.status == HabitStatus.ACTIVE.value]

            lines = [
                f"💪 Habit Strength Analysis for {user_id}",
                "=" * 60,
            ]

            # Calculate stats for each habit
            habit_data = []
            for habit in active_habits:
                stats = _calculate_habit_stats(habit)
                habit_data.append((habit, stats))

            # Sort by strength
            habit_data.sort(key=lambda x: x[1].strength_score, reverse=True)

            # Show each habit
            for habit, stats in habit_data:
                domain_emoji = DOMAIN_COLORS.get(HabitDomain(habit.domain), "⚪")
                level, emoji = get_strength_level(stats.strength_score)

                lines.append(f"\n{domain_emoji} {habit.name}")
                lines.append(f"   Strength: {stats.strength_score:.1f}/100 {emoji} ({level})")
                lines.append(f"   Current Streak: {stats.current_streak} days")
                lines.append(f"   Completion Rate: {stats.completion_rate * 100:.1f}%")
                lines.append(f"   Days Active: {stats.days_active}")

                # Strength interpretation
                if stats.strength_score >= 80:
                    lines.append(f"   ✓ Strong habit - this is becoming automatic!")
                elif stats.strength_score >= 60:
                    lines.append(f"   🌱 Developing well - keep the momentum!")
                elif stats.strength_score >= 40:
                    lines.append(f"   📈 Building - consistency will strengthen it")
                else:
                    lines.append(f"   🆕 New habit - focus on daily consistency")

            # Overall summary
            if habit_data:
                avg_strength = sum(s.strength_score for _, s in habit_data) / len(habit_data)
                lines.append(f"\n📊 Overall Average Strength: {avg_strength:.1f}/100")

                # Habit formation progress
                strong_habits = sum(1 for _, s in habit_data if s.strength_score >= 80)
                developing = sum(1 for _, s in habit_data if 60 <= s.strength_score < 80)

                lines.append(f"\n🏆 Strong Habits (80+): {strong_habits}")
                lines.append(f"🌱 Developing (60-79): {developing}")
                lines.append(f"📚 Building (<60): {len(habit_data) - strong_habits - developing}")

            # Research context
            lines.append(f"\n📖 Research Context:")
            lines.append(
                f"   • Automaticity threshold: ~{HABIT_FORMATION_RESEARCH['median_days']} days"
            )
            lines.append(f"   • Strength 80+ = Strong automatic habit")
            lines.append(f"   • Strength 60-79 = Developing automaticity")
            lines.append(f"   • Strength 40-59 = Habit building phase")
            lines.append(f"   • Strength <40 = Early formation stage")

            return "\n".join(lines)

        except Exception as e:
            return f"Error calculating habit strength: {str(e)}"

    # --------------------------------------------------------------------------
    # Tool 5: Get Habit Stacking Suggestions
    # --------------------------------------------------------------------------

    @tool
    def get_habit_stacking_suggestions(
        user_id: str,
        new_habit_name: str,
        new_habit_domain: str = "health",
    ) -> str:
        """Get habit stacking suggestions based on existing habits.

        Based on Atomic Habits by James Clear:
        "After [CURRENT HABIT], I will [NEW HABIT]."

        Analyzes your existing habits to suggest the best anchors
        for stacking a new habit.

        Args:
            user_id: The user's unique identifier
            new_habit_name: Name of the new habit you want to create
            new_habit_domain: Domain of the new habit

        Returns:
            Stacking suggestions with scores and templates.

        Example:
            >>> get_habit_stacking_suggestions(
            ...     user_id="user_123",
            ...     new_habit_name="Read 10 pages",
            ...     new_habit_domain="personal_growth"
            ... )
        """
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not new_habit_name or not isinstance(new_habit_name, str):
            return "Error: new_habit_name must be a non-empty string"

        try:
            # Load existing habits
            existing_habits = _load_all_habits(user_id)

            if not existing_habits:
                return f"""No existing habits found for user '{user_id}'.

To use habit stacking, you need at least one established habit.

Create your first habit using create_habit(), then come back for stacking suggestions!

Alternative: You can still use time-based cues:
• "After I pour my morning coffee, I will {new_habit_name}"
• "When I sit down at my desk, I will {new_habit_name}"
• "After I close my work laptop, I will {new_habit_name}"
"""

            # Calculate strength for each habit
            for habit in existing_habits:
                if habit.status == HabitStatus.ACTIVE.value:
                    stats = _calculate_habit_stats(habit)
                    habit.strength_score = stats.strength_score  # type: ignore

            # Get suggestions
            suggestions = suggest_habit_stack(existing_habits, new_habit_domain)

            # Format response
            lines = [
                f"🔗 Habit Stacking Suggestions for: {new_habit_name}",
                "=" * 60,
                f"\nDomain: {new_habit_domain.replace('_', ' ').title()}",
                f"Existing Habits: {len(existing_habits)}",
            ]

            if not suggestions:
                lines.append("\n💡 No strong stacking candidates found.")
                lines.append("\nGeneral Recommendations:")
                lines.append("• Look for habits that happen at the same time of day")
                lines.append("• Choose habits you already do consistently")
                lines.append("• Consider location-based cues (e.g., 'when I enter the kitchen')")
            else:
                lines.append(f"\n🎯 Top {len(suggestions)} Stacking Candidates:")
                lines.append("-" * 60)

                for i, suggestion in enumerate(suggestions, 1):
                    habit = suggestion["habit"]
                    domain_emoji = DOMAIN_COLORS.get(HabitDomain(habit.domain), "⚪")

                    lines.append(f"\n{i}. {domain_emoji} {habit.name}")
                    lines.append(f"   Score: {suggestion['score']:.0f}/100")
                    lines.append(f"   Domain: {habit.domain}")

                    if hasattr(habit, "strength_score"):
                        level, emoji = get_strength_level(habit.strength_score)
                        lines.append(f"   Habit Strength: {habit.strength_score:.0f}/100 {emoji}")

                    lines.append(f"\n   ✅ Stacking Template:")
                    lines.append(f"      'After I {habit.action}, I will {new_habit_name}'")

                    lines.append(f"\n   💡 Why this works:")
                    for reason in suggestion["reasons"]:
                        lines.append(f"      • {reason}")

            # Habit stacking principles
            lines.append("\n📚 Habit Stacking Principles (from Atomic Habits):")
            lines.append("1. The cue should be specific and consistent")
            lines.append("2. The new habit should immediately follow the anchor")
            lines.append("3. Choose anchors that match the desired frequency")
            lines.append("4. Stack habits in the same location when possible")

            lines.append("\n🎯 Formula for Success:")
            lines.append(f"   'After I [CURRENT HABIT], I will [{new_habit_name}]'")

            return "\n".join(lines)

        except Exception as e:
            return f"Error getting stacking suggestions: {str(e)}"

    # --------------------------------------------------------------------------
    # Tool 6: Get Habits by Domain
    # --------------------------------------------------------------------------

    @tool
    def get_habits_by_domain(
        user_id: str,
        domain: Optional[str] = None,
    ) -> str:
        """Get habits organized by life domain.

        Groups habits by domain (health, career, relationships, etc.)
        with statistics and strength scores.

        Args:
            user_id: The user's unique identifier
            domain: Optional specific domain to filter (shows all if not provided)

        Returns:
            Habits organized by domain with statistics.

        Example:
            >>> get_habits_by_domain(user_id="user_123")
            >>> get_habits_by_domain(user_id="user_123", domain="health")
        """
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        if domain:
            valid_domains = [d.value for d in HabitDomain]
            if domain not in valid_domains:
                return f"Error: domain must be one of {valid_domains}"

        try:
            habits = _load_all_habits(user_id)

            if not habits:
                return f"No habits found for user '{user_id}'. Create habits using create_habit()."

            # Group by domain
            domain_habits: Dict[str, List[Tuple[Habit, HabitStats]]] = {}

            for habit in habits:
                if habit.status != HabitStatus.ACTIVE.value:
                    continue

                habit_domain = habit.domain
                if domain and habit_domain != domain:
                    continue

                if habit_domain not in domain_habits:
                    domain_habits[habit_domain] = []

                stats = _calculate_habit_stats(habit)
                domain_habits[habit_domain].append((habit, stats))

            if not domain_habits:
                return f"No active habits found for user '{user_id}'" + (
                    f" in domain '{domain}'" if domain else ""
                )

            # Format response
            lines = [
                f"📊 Habits by Domain for {user_id}",
                "=" * 60,
            ]

            # Calculate domain summaries
            domain_summaries = []
            for domain_name, habits_list in domain_habits.items():
                total_strength = sum(s.strength_score for _, s in habits_list)
                avg_strength = total_strength / len(habits_list) if habits_list else 0
                total_streak = sum(s.current_streak for _, s in habits_list)

                domain_summaries.append(
                    {
                        "domain": domain_name,
                        "count": len(habits_list),
                        "avg_strength": avg_strength,
                        "total_streak": total_streak,
                        "habits": habits_list,
                    }
                )

            # Sort by average strength
            domain_summaries.sort(key=lambda x: x["avg_strength"], reverse=True)

            # Show summary
            lines.append(f"\n📈 Domain Summary:")
            for summary in domain_summaries:
                domain_emoji = DOMAIN_COLORS.get(HabitDomain(summary["domain"]), "⚪")
                level, _ = get_strength_level(summary["avg_strength"])
                lines.append(
                    f"   {domain_emoji} {summary['domain'].replace('_', ' ').title()}: "
                    f"{summary['count']} habits (Avg Strength: {summary['avg_strength']:.0f}/100, {level})"
                )

            # Show detailed habits for each domain
            for summary in domain_summaries:
                domain_name = summary["domain"]
                domain_emoji = DOMAIN_COLORS.get(HabitDomain(domain_name), "⚪")

                lines.append(f"\n{domain_emoji} {domain_name.replace('_', ' ').title()}")
                lines.append("-" * 40)

                # Sort habits by strength within domain
                sorted_habits = sorted(
                    summary["habits"], key=lambda x: x[1].strength_score, reverse=True
                )

                for habit, stats in sorted_habits:
                    streak_visual = get_streak_visual(stats.current_streak)
                    level, emoji = get_strength_level(stats.strength_score)

                    lines.append(f"\n   • {habit.name}")
                    lines.append(
                        f"     Strength: {stats.strength_score:.0f}/100 {emoji} | "
                        f"Streak: {stats.current_streak} days {streak_visual} | "
                        f"Rate: {stats.completion_rate * 100:.0f}%"
                    )

            # Balance recommendations
            lines.append("\n💡 Domain Balance Tips:")

            if len(domain_summaries) < 3:
                lines.append("• Consider adding habits in more life domains for balance")

            # Find weakest domain
            weakest = min(domain_summaries, key=lambda x: x["avg_strength"])
            if weakest["avg_strength"] < 50:
                lines.append(
                    f"• Your {weakest['domain'].replace('_', ' ')} habits could use more attention"
                )

            return "\n".join(lines)

        except Exception as e:
            return f"Error getting habits by domain: {str(e)}"

    # --------------------------------------------------------------------------
    # Tool 7: Review and Adjust Habit
    # --------------------------------------------------------------------------

    @tool
    def review_habit(
        user_id: str,
        habit_id: str,
    ) -> str:
        """Review a habit and get adjustment recommendations.

        Performs comprehensive analysis of a habit including:
        - Completion patterns and trends
        - Streak analysis
        - Strength score evaluation
        - Calendar visualization
        - Adjustment recommendations

        Args:
            user_id: The user's unique identifier
            habit_id: ID of the habit to review

        Returns:
            Comprehensive review with analysis and recommendations.

        Example:
            >>> review_habit(
            ...     user_id="user_123",
            ...     habit_id="habit_20240115_083000_1234"
            ... )
        """
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not habit_id or not isinstance(habit_id, str):
            return "Error: habit_id must be a non-empty string"

        try:
            habit = _load_habit(user_id, habit_id)
            if not habit:
                return f"Error: Habit '{habit_id}' not found for user '{user_id}'"

            stats = _calculate_habit_stats(habit)
            entries = _load_entries(user_id, habit_id)

            # Get completion dates
            completion_dates = [parse_date(e.completion_date) for e in entries]

            # Format response
            domain_emoji = DOMAIN_COLORS.get(HabitDomain(habit.domain), "⚪")
            level, strength_emoji = get_strength_level(stats.strength_score)

            lines = [
                f"{domain_emoji} Habit Review: {habit.name}",
                "=" * 60,
            ]

            # Habit details
            lines.append(f"\n📋 Details:")
            lines.append(f"   ID: {habit.habit_id}")
            lines.append(f"   Domain: {habit.domain.replace('_', ' ').title()}")
            lines.append(f"   Frequency: {habit.frequency.title()}")
            lines.append(f"   Created: {parse_date(habit.created_at).strftime('%Y-%m-%d')}")
            lines.append(f"   Days Active: {stats.days_active}")

            # Habit Loop
            lines.append(f"\n🔄 Habit Loop:")
            lines.append(f"   Cue: {habit.cue or 'Not defined'}")
            lines.append(f"   Action: {habit.action}")
            lines.append(f"   Reward: {habit.reward or 'Not defined'}")

            if habit.stack_after:
                lines.append(f"   Stack After: {habit.stack_after}")

            # Statistics
            streak_visual = get_streak_visual(stats.current_streak)
            lines.append(f"\n📊 Statistics:")
            lines.append(
                f"   Strength Score: {stats.strength_score:.1f}/100 {strength_emoji} ({level})"
            )
            lines.append(f"   Current Streak: {stats.current_streak} days {streak_visual}")
            lines.append(f"   Longest Streak: {stats.longest_streak} days")
            lines.append(f"   Total Completions: {stats.total_completions}")
            lines.append(f"   Completion Rate: {stats.completion_rate * 100:.1f}%")

            # Recent activity
            if entries:
                lines.append(f"\n📅 Recent Activity:")
                recent_entries = sorted(entries, key=lambda e: e.completion_date, reverse=True)[:7]
                for entry in recent_entries:
                    comp_date = parse_date(entry.completion_date)
                    lines.append(f"   ✓ {comp_date.strftime('%Y-%m-%d (%a)')}")

            # Calendar visualization for current month
            if completion_dates:
                lines.append(f"\n📆 This Month:")
                today = date.today()
                calendar = generate_calendar_visual(completion_dates, today.year, today.month)
                lines.append(calendar)

            # Analysis
            lines.append(f"\n🔍 Analysis:")

            # Strength assessment
            if stats.strength_score >= 80:
                lines.append(f"   ✓ Strong habit - well established!")
            elif stats.strength_score >= 60:
                lines.append(f"   🌱 Developing positively - keep consistent")
            elif stats.strength_score >= 40:
                lines.append(f"   📈 Building - needs more consistency")
            else:
                lines.append(f"   🆕 Early stage - focus on daily completion")

            # Completion rate assessment
            if stats.completion_rate >= 0.9:
                lines.append(f"   ✓ Excellent completion rate (90%+)")
            elif stats.completion_rate >= 0.7:
                lines.append(f"   🟡 Good completion rate (70%+)")
            elif stats.completion_rate >= 0.5:
                lines.append(f"   ⚠️ Fair completion rate - room for improvement")
            else:
                lines.append(f"   🔴 Low completion rate - consider adjustments")

            # Pattern analysis
            if stats.current_streak < 7 and stats.longest_streak >= 7:
                lines.append(f"   ⚠️ Streak broken - you had {stats.longest_streak} days before")

            if stats.days_active > 30 and stats.completion_rate < 0.5:
                lines.append(f"   ⚠️ Low engagement over time - habit may need revision")

            # Recommendations
            lines.append(f"\n💡 Recommendations:")

            if not habit.cue:
                lines.append(f"   1. Define a clear cue: When/where will you do this?")

            if not habit.reward:
                lines.append(f"   2. Define a reward: What makes this satisfying?")

            if stats.completion_rate < 0.7:
                lines.append(f"   3. Make it easier: Start with a 2-minute version")
                lines.append(f"   4. Reduce friction: Prepare everything in advance")

            if stats.current_streak < 3 and stats.longest_streak >= 7:
                lines.append(f"   5. Restart today: 'Never miss twice' - get back on track")

            if stats.strength_score >= 80:
                lines.append(
                    f"   ✓ This habit is automatic - maintain and consider adding new ones"
                )

            # Formation timeline
            days_to_automaticity = max(
                0, HABIT_FORMATION_RESEARCH["median_days"] - stats.days_active
            )
            if days_to_automaticity > 0 and stats.strength_score < 80:
                lines.append(f"\n⏱️ Formation Timeline:")
                lines.append(
                    f"   ~{days_to_automaticity} more days to reach automaticity threshold"
                )
                lines.append(f"   (Based on {HABIT_FORMATION_RESEARCH['median_days']} day average)")

            return "\n".join(lines)

        except Exception as e:
            return f"Error reviewing habit: {str(e)}"

    # --------------------------------------------------------------------------
    # Tool 8: Update Habit
    # --------------------------------------------------------------------------

    @tool
    def update_habit(
        user_id: str,
        habit_id: str,
        name: Optional[str] = None,
        cue: Optional[str] = None,
        action: Optional[str] = None,
        reward: Optional[str] = None,
        status: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> str:
        """Update an existing habit's properties.

        Allows modification of habit details without losing tracking history.

        Args:
            user_id: The user's unique identifier
            habit_id: ID of the habit to update
            name: Optional new name
            cue: Optional new cue
            action: Optional new action
            reward: Optional new reward
            status: Optional new status (active, paused, completed, archived)
            notes: Optional new notes

        Returns:
            Confirmation of updates made.

        Example:
            >>> update_habit(
            ...     user_id="user_123",
            ...     habit_id="habit_20240115_083000_1234",
            ...     cue="After I brush my teeth"
            ... )
        """
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not habit_id or not isinstance(habit_id, str):
            return "Error: habit_id must be a non-empty string"

        if status:
            valid_statuses = [s.value for s in HabitStatus]
            if status not in valid_statuses:
                return f"Error: status must be one of {valid_statuses}"

        try:
            habit = _load_habit(user_id, habit_id)
            if not habit:
                return f"Error: Habit '{habit_id}' not found for user '{user_id}'"

            # Track what was updated
            updates = []

            if name is not None:
                old_name = habit.name
                habit.name = name
                updates.append(f"name: '{old_name}' → '{name}'")

            if cue is not None:
                old_cue = habit.cue
                habit.cue = cue
                updates.append(f"cue: '{old_cue}' → '{cue}'")

            if action is not None:
                old_action = habit.action
                habit.action = action
                updates.append(f"action: '{old_action}' → '{action}'")

            if reward is not None:
                old_reward = habit.reward
                habit.reward = reward
                updates.append(f"reward: '{old_reward}' → '{reward}'")

            if status is not None:
                old_status = habit.status
                habit.status = status
                updates.append(f"status: '{old_status}' → '{status}'")

            if notes is not None:
                habit.notes = notes
                updates.append("notes updated")

            if not updates:
                return "No updates provided. Specify at least one field to update."

            # Save updated habit
            _save_habit(habit)

            # Format response
            lines = [
                f"✏️ Habit Updated: {habit.name}",
                "=" * 60,
                f"\nHabit ID: {habit.habit_id}",
                f"\nChanges Made:",
            ]

            for update in updates:
                lines.append(f"   • {update}")

            lines.append(f"\n💾 Changes saved to: habits/{user_id}/{habit_id}.json")

            if status == HabitStatus.PAUSED.value:
                lines.append(f"\n⏸️ Habit paused. Your streak will be preserved when you resume.")
            elif status == HabitStatus.COMPLETED.value:
                lines.append(f"\n🎉 Congratulations! Marking habit as completed.")
            elif status == HabitStatus.ARCHIVED.value:
                lines.append(f"\n📦 Habit archived. Data preserved but no longer tracked.")

            return "\n".join(lines)

        except Exception as e:
            return f"Error updating habit: {str(e)}"

    # --------------------------------------------------------------------------
    # Tool 9: Delete Habit
    # --------------------------------------------------------------------------

    @tool
    def delete_habit(
        user_id: str,
        habit_id: str,
        confirm: bool = False,
    ) -> str:
        """Delete a habit and all its tracking data.

        WARNING: This permanently removes the habit and all completion history.
        Consider archiving instead to preserve data.

        Args:
            user_id: The user's unique identifier
            habit_id: ID of the habit to delete
            confirm: Must be True to confirm deletion

        Returns:
            Confirmation of deletion or warning if not confirmed.

        Example:
            >>> delete_habit(
            ...     user_id="user_123",
            ...     habit_id="habit_20240115_083000_1234",
            ...     confirm=True
            ... )
        """
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not habit_id or not isinstance(habit_id, str):
            return "Error: habit_id must be a non-empty string"

        try:
            habit = _load_habit(user_id, habit_id)
            if not habit:
                return f"Error: Habit '{habit_id}' not found for user '{user_id}'"

            if not confirm:
                return f"""⚠️ DELETE CONFIRMATION REQUIRED

Habit: {habit.name}
ID: {habit_id}

This will permanently delete:
• The habit definition
• All completion history
• All streak data

To confirm deletion, call with confirm=True:
  delete_habit(user_id="{user_id}", habit_id="{habit_id}", confirm=True)

Alternative: Use update_habit() to archive instead:
  update_habit(user_id="{user_id}", habit_id="{habit_id}", status="archived")
"""

            # Delete habit file
            habit_path = workspace_path / "habits" / user_id / f"{habit_id}.json"
            if habit_path.exists():
                habit_path.unlink()

            # Delete all entries
            entries_dir = workspace_path / "habits" / user_id / "entries" / habit_id
            if entries_dir.exists():
                for entry_file in entries_dir.glob("*.json"):
                    entry_file.unlink()
                entries_dir.rmdir()

            return f"✅ Habit '{habit.name}' (ID: {habit_id}) has been permanently deleted."

        except Exception as e:
            return f"Error deleting habit: {str(e)}"

    # --------------------------------------------------------------------------
    # Tool 10: List All Habits
    # --------------------------------------------------------------------------

    @tool
    def list_habits(
        user_id: str,
        status: Optional[str] = "active",
    ) -> str:
        """List all habits for a user with summary information.

        Args:
            user_id: The user's unique identifier
            status: Filter by status (active, paused, completed, archived, all)

        Returns:
            List of habits with key statistics.

        Example:
            >>> list_habits(user_id="user_123")
            >>> list_habits(user_id="user_123", status="all")
        """
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        valid_statuses = [s.value for s in HabitStatus] + ["all"]
        if status not in valid_statuses:
            return f"Error: status must be one of {valid_statuses}"

        try:
            habits = _load_all_habits(user_id)

            if not habits:
                return f"No habits found for user '{user_id}'. Create habits using create_habit()."

            # Filter by status
            if status != "all":
                habits = [h for h in habits if h.status == status]

            if not habits:
                return f"No {status} habits found for user '{user_id}'."

            # Calculate stats
            habit_data = []
            for habit in habits:
                stats = _calculate_habit_stats(habit)
                habit_data.append((habit, stats))

            # Sort by domain then strength
            habit_data.sort(key=lambda x: (x[0].domain, -x[1].strength_score))

            # Format response
            lines = [
                f"📋 Habits for {user_id}" + (f" ({status})" if status != "all" else " (All)"),
                "=" * 60,
            ]

            # Summary
            lines.append(f"\nTotal: {len(habit_data)} habits")

            # Group by domain
            current_domain = None
            for habit, stats in habit_data:
                if habit.domain != current_domain:
                    current_domain = habit.domain
                    domain_emoji = DOMAIN_COLORS.get(HabitDomain(habit.domain), "⚪")
                    lines.append(f"\n{domain_emoji} {habit.domain.replace('_', ' ').title()}")
                    lines.append("-" * 40)

                level, emoji = get_strength_level(stats.strength_score)
                streak_visual = get_streak_visual(stats.current_streak)

                status_indicator = ""
                if habit.status == HabitStatus.PAUSED.value:
                    status_indicator = "⏸️ "
                elif habit.status == HabitStatus.COMPLETED.value:
                    status_indicator = "✅ "
                elif habit.status == HabitStatus.ARCHIVED.value:
                    status_indicator = "📦 "

                lines.append(f"   {status_indicator}{habit.name}")
                lines.append(f"      ID: {habit.habit_id}")
                lines.append(
                    f"      Strength: {stats.strength_score:.0f}/100 {emoji} | "
                    f"Streak: {stats.current_streak} {streak_visual} | "
                    f"Rate: {stats.completion_rate * 100:.0f}%"
                )

            # Quick actions
            lines.append(f"\n🔧 Quick Actions:")
            lines.append(
                f"   • Log completion: log_habit_completion(user_id='{user_id}', habit_id='HABIT_ID')"
            )
            lines.append(
                f"   • Review habit: review_habit(user_id='{user_id}', habit_id='HABIT_ID')"
            )
            lines.append(f"   • View streaks: get_habit_streaks(user_id='{user_id}')")

            return "\n".join(lines)

        except Exception as e:
            return f"Error listing habits: {str(e)}"

    # Return all tools
    return (
        create_habit,
        log_habit_completion,
        get_habit_streaks,
        calculate_habit_strength_score,
        get_habit_stacking_suggestions,
        get_habits_by_domain,
        review_habit,
        update_habit,
        delete_habit,
        list_habits,
    )
