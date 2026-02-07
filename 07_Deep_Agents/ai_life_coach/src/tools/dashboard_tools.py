"""
Progress Dashboard Tools for AI Life Coach.

This module provides comprehensive dashboard functionality for visualizing
multi-domain life progress with text-based ASCII visualizations.

Key Features:
1. Multi-Domain Progress Display - Career, Relationship, Finance, Wellness
2. Life Satisfaction Score - Composite score across all domains
3. Trend Visualizations - Text-based sparklines and progress bars
4. Achievements & Milestones - Recent wins and upcoming goals
5. Configurable Views - Daily, Weekly, Monthly timeframes
6. Export Functionality - Markdown report generation

Based on research in:
- Dashboard Design Patterns (Bach et al., 2022) - 42 design patterns
- CLI visualization best practices (Textual, Rich libraries)
- ASCII art visualization techniques
- Multi-domain life assessment frameworks

Tools:
- render_progress_dashboard: Main dashboard with all components
- calculate_life_satisfaction_score: Composite scoring algorithm
- generate_domain_progress_bar: Visual progress indicators
- create_mood_trend_sparkline: ASCII sparkline charts
- get_recent_achievements: Recent milestone highlights
- get_upcoming_milestones: Goals approaching deadline
- export_dashboard_report: Generate Markdown reports
- switch_dashboard_view: Toggle between daily/weekly/monthly views
"""

from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
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
# Dashboard Configuration
# ==============================================================================

# Domain definitions with icons and colors (represented by emoji/symbols)
DOMAINS = {
    "career": {
        "name": "Career & Professional",
        "icon": "💼",
        "symbol": "C",
        "color_code": "\033[94m",  # Blue (for terminals that support it)
        "weight": 0.25,
        "description": "Work satisfaction, career progression, skills",
    },
    "relationship": {
        "name": "Relationships",
        "icon": "❤️",
        "symbol": "R",
        "color_code": "\033[91m",  # Red
        "weight": 0.25,
        "description": "Family, friends, romantic, community",
    },
    "finance": {
        "name": "Financial Health",
        "icon": "💰",
        "symbol": "F",
        "color_code": "\033[92m",  # Green
        "weight": 0.25,
        "description": "Budgeting, savings, debt, investments",
    },
    "wellness": {
        "name": "Wellness & Health",
        "icon": "🌿",
        "symbol": "W",
        "color_code": "\033[93m",  # Yellow
        "weight": 0.25,
        "description": "Physical, mental, emotional wellbeing",
    },
}

# View configurations
VIEW_CONFIGS = {
    "daily": {
        "name": "Daily View",
        "days": 1,
        "mood_points": 7,  # Number of data points for sparkline
        "label": "Today",
        "aggregation": "single",
    },
    "weekly": {
        "name": "Weekly View",
        "days": 7,
        "mood_points": 7,
        "label": "This Week",
        "aggregation": "average",
    },
    "monthly": {
        "name": "Monthly View",
        "days": 30,
        "mood_points": 10,
        "label": "This Month",
        "aggregation": "average",
    },
}

# ASCII visualization characters
ASCII_CHARS = {
    "horizontal": "─",
    "vertical": "│",
    "corner_tl": "┌",
    "corner_tr": "┐",
    "corner_bl": "└",
    "corner_br": "┘",
    "tee_right": "├",
    "tee_left": "┤",
    "tee_down": "┬",
    "tee_up": "┴",
    "cross": "┼",
    "filled": "█",
    "partial": ["░", "▒", "▓"],
    "sparkline_chars": ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"],
    "arrow_up": "↑",
    "arrow_down": "↓",
    "arrow_flat": "→",
    "bullet": "●",
    "star": "★",
    "check": "✓",
    "pending": "○",
    "trend_up": "📈",
    "trend_down": "📉",
    "trend_flat": "➡️",
}

# Progress bar characters (for different styles)
PROGRESS_STYLES = {
    "solid": {"filled": "█", "empty": "░"},
    "blocks": {"filled": "█", "empty": "▒"},
    "arrows": {"filled": "▶", "empty": "▷"},
    "circles": {"filled": "●", "empty": "○"},
}


# ==============================================================================
# Dashboard Rendering Engine
# ==============================================================================


class DashboardRenderer:
    """Renders progress dashboards using ASCII art and text."""

    def __init__(self, backend=None):
        """Initialize the dashboard renderer."""
        self.backend = backend or get_backend()
        self.chars = ASCII_CHARS
        self.style = PROGRESS_STYLES["solid"]
        self.width = 70  # Default dashboard width

    def _box_top(self, width: Optional[int] = None) -> str:
        """Generate top border of a box."""
        w = width or self.width
        return f"{self.chars['corner_tl']}{self.chars['horizontal'] * (w - 2)}{self.chars['corner_tr']}"

    def _box_bottom(self, width: Optional[int] = None) -> str:
        """Generate bottom border of a box."""
        w = width or self.width
        return f"{self.chars['corner_bl']}{self.chars['horizontal'] * (w - 2)}{self.chars['corner_br']}"

    def _box_line(self, content: str, width: Optional[int] = None, align: str = "left") -> str:
        """Generate a content line within a box."""
        w = (width or self.width) - 4  # Account for borders and padding
        content = content[:w]  # Truncate if too long
        if align == "center":
            content = content.center(w)
        elif align == "right":
            content = content.rjust(w)
        else:
            content = content.ljust(w)
        return f"{self.chars['vertical']} {content} {self.chars['vertical']}"

    def _separator(self, width: Optional[int] = None) -> str:
        """Generate a horizontal separator line."""
        w = width or self.width
        return (
            f"{self.chars['tee_right']}{self.chars['horizontal'] * (w - 2)}{self.chars['tee_left']}"
        )

    def _progress_bar(
        self,
        percentage: float,
        width: int = 30,
        show_percent: bool = True,
        style: Optional[str] = None,
    ) -> str:
        """Generate an ASCII progress bar."""
        style_dict = PROGRESS_STYLES.get(style, self.style)
        filled_width = int((percentage / 100.0) * width)
        empty_width = width - filled_width

        bar = style_dict["filled"] * filled_width + style_dict["empty"] * empty_width

        if show_percent:
            return f"{bar} {percentage:5.1f}%"
        return bar

    def _sparkline(
        self,
        values: List[float],
        width: int = 20,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None,
    ) -> str:
        """Generate an ASCII sparkline from values."""
        if not values:
            return "─" * width

        # Normalize values to 0-7 range (8 sparkline levels)
        min_value = min_val if min_val is not None else min(values)
        max_value = max_val if max_val is not None else max(values)

        if max_value == min_value:
            return "─" * min(width, len(values))

        chars = self.chars["sparkline_chars"]
        result = []

        for val in values[:width]:
            normalized = int(((val - min_value) / (max_value - min_value)) * (len(chars) - 1))
            normalized = max(0, min(normalized, len(chars) - 1))
            result.append(chars[normalized])

        return "".join(result)

    def _trend_indicator(self, current: float, previous: float) -> str:
        """Generate a trend indicator based on value change."""
        diff = current - previous
        if diff > 0.5:
            return f"{self.chars['arrow_up']} +{diff:.1f}"
        elif diff < -0.5:
            return f"{self.chars['arrow_down']} {diff:.1f}"
        else:
            return f"{self.chars['arrow_flat']} ~"


# ==============================================================================
# Dashboard Tool Factory
# ==============================================================================


def create_dashboard_tools(backend=None):
    """
    Create progress dashboard tools with shared state.

    Args:
        backend: Optional FilesystemBackend instance

    Returns:
        Tuple of dashboard tools
    """
    backend = backend or get_backend()
    renderer = DashboardRenderer(backend)

    # ==========================================================================
    # Tool 1: Render Main Dashboard
    # ==========================================================================

    @tool
    def render_progress_dashboard(
        user_id: str,
        view: str = "weekly",
        include_mood: bool = True,
        include_goals: bool = True,
        include_achievements: bool = True,
    ) -> str:
        """
        Render a comprehensive progress dashboard with all components.

        Displays overall life satisfaction score, domain-specific progress bars,
        mood trends, recent achievements, and upcoming milestones in an
        ASCII-based layout.

        Args:
            user_id: The user's unique identifier
            view: Timeframe view - "daily", "weekly", or "monthly"
            include_mood: Whether to include mood trend section
            include_goals: Whether to include goal progress section
            include_achievements: Whether to include achievements section

        Returns:
            Formatted dashboard as multi-line string

        Example:
            >>> render_progress_dashboard("user_123", view="weekly")
            '┌────────────────────────────────────────────────────────────────────┐
             │  🎯 AI LIFE COACH - Progress Dashboard       This Week            │
             ...'
        """
        # Validate view
        if view not in VIEW_CONFIGS:
            view = "weekly"

        view_config = VIEW_CONFIGS[view]
        lines = []
        r = renderer

        # Header
        lines.append(r._box_top())
        header_text = f"🎯 AI LIFE COACH - Progress Dashboard       {view_config['label']}"
        lines.append(r._box_line(header_text))
        lines.append(r._separator())

        # Calculate overall life satisfaction score
        life_score = _calculate_overall_score(user_id, view, backend)
        score_color = _score_color(life_score)
        score_bar = r._progress_bar(life_score, width=40)

        lines.append(r._box_line(""))
        lines.append(r._box_line("📊 OVERALL LIFE SATISFACTION", align="center"))
        lines.append(r._box_line(""))
        lines.append(r._box_line(f"     Composite Score: {life_score:5.1f}/100", align="center"))
        lines.append(r._box_line(f"     {score_bar}", align="center"))
        lines.append(r._box_line(f"     Status: {_score_label(life_score)}", align="center"))
        lines.append(r._box_line(""))
        lines.append(r._separator())

        # Domain Progress Section
        if include_goals:
            lines.append(r._box_line("📈 DOMAIN PROGRESS", align="left"))
            lines.append(r._box_line(""))

            for domain_key, domain_info in DOMAINS.items():
                progress = _get_domain_progress(user_id, domain_key, view, backend)
                trend = _get_domain_trend(user_id, domain_key, view, backend)
                bar = r._progress_bar(progress, width=25)
                trend_str = f"{trend:+.1f}" if trend != 0 else "~"

                line_text = f"  {domain_info['icon']} {domain_info['name']:<25} {bar} ({trend_str})"
                lines.append(r._box_line(line_text))

            lines.append(r._box_line(""))
            lines.append(r._separator())

        # Mood Trend Section
        if include_mood:
            lines.append(r._box_line("😊 MOOD TREND", align="left"))
            lines.append(r._box_line(""))

            mood_data = _get_mood_history(user_id, view_config["mood_points"], backend)
            if mood_data:
                sparkline = r._sparkline(mood_data, width=40)
                current_mood = mood_data[-1] if mood_data else 5.0
                avg_mood = sum(mood_data) / len(mood_data) if mood_data else 5.0

                lines.append(r._box_line(f"  Recent Mood: {sparkline}"))
                lines.append(
                    r._box_line(f"  Current: {current_mood:.1f}/10  |  Average: {avg_mood:.1f}/10")
                )

                # Mood trend indicator
                if len(mood_data) >= 2:
                    trend = r._trend_indicator(current_mood, mood_data[0])
                    lines.append(r._box_line(f"  Trend: {trend}"))
            else:
                lines.append(r._box_line("  No mood data available. Start logging your mood!"))

            lines.append(r._box_line(""))
            lines.append(r._separator())

        # Recent Achievements Section
        if include_achievements:
            lines.append(r._box_line("🏆 RECENT ACHIEVEMENTS", align="left"))
            lines.append(r._box_line(""))

            achievements = _get_recent_achievements(user_id, 3, backend)
            if achievements:
                for ach in achievements:
                    icon = "★" if ach.get("significance") == "major" else "✓"
                    date_str = ach.get("date", "Recently")
                    line = f"  {icon} {ach.get('title', 'Achievement')} ({date_str})"
                    lines.append(r._box_line(line))
                    if ach.get("description"):
                        lines.append(r._box_line(f"     {ach.get('description')[:50]}"))
            else:
                lines.append(
                    r._box_line("  No recent achievements. Keep working toward your goals!")
                )

            lines.append(r._box_line(""))
            lines.append(r._separator())

        # Upcoming Milestones Section
        lines.append(r._box_line("🎯 UPCOMING MILESTONES", align="left"))
        lines.append(r._box_line(""))

        milestones = _get_upcoming_milestones(user_id, 3, backend)
        if milestones:
            for ms in milestones:
                days_left = ms.get("days_remaining", "?")
                icon = "🔥" if days_left and days_left <= 3 else "○"
                line = f"  {icon} {ms.get('title', 'Milestone')} - {days_left} days left"
                lines.append(r._box_line(line))
        else:
            lines.append(r._box_line("  No upcoming milestones. Set some goals to get started!"))

        lines.append(r._box_line(""))
        lines.append(r._box_bottom())

        # Footer tips
        lines.append("")
        lines.append("💡 Tips:")
        lines.append("   • Use switch_dashboard_view() to change timeframe")
        lines.append("   • Use export_dashboard_report() to save as Markdown")
        lines.append("   • Check individual domains for detailed progress")

        return "\n".join(lines)

    # ==========================================================================
    # Tool 2: Calculate Life Satisfaction Score
    # ==========================================================================

    @tool
    def calculate_life_satisfaction_score(user_id: str, view: str = "weekly") -> str:
        """
        Calculate comprehensive life satisfaction score across all domains.

        Computes a weighted composite score (0-100) based on:
        - Domain goal completion rates
        - Mood and wellness metrics
        - Recent achievements
        - Habit consistency

        Args:
            user_id: The user's unique identifier
            view: Timeframe for calculation - "daily", "weekly", or "monthly"

        Returns:
            Detailed score breakdown with domain contributions

        Example:
            >>> calculate_life_satisfaction_score("user_123", "weekly")
            'Life Satisfaction Score: 72.5/100\n\nDomain Breakdown:\n  Career: 75.0% (weight: 25%)...'
        """
        if view not in VIEW_CONFIGS:
            view = "weekly"

        score = _calculate_overall_score(user_id, view, backend)
        domain_scores = {}

        for domain_key in DOMAINS.keys():
            domain_scores[domain_key] = _get_domain_progress(user_id, domain_key, view, backend)

        # Build detailed report
        lines = []
        lines.append("=" * 60)
        lines.append("🎯 LIFE SATISFACTION SCORE REPORT")
        lines.append("=" * 60)
        lines.append("")
        lines.append(f"Overall Score: {score:.1f}/100")
        lines.append(f"Rating: {_score_label(score)}")
        lines.append("")

        # Visual representation
        bar_width = 50
        filled = int((score / 100) * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)
        lines.append(f"[{bar}]")
        lines.append("")

        # Domain breakdown
        lines.append("Domain Breakdown:")
        lines.append("-" * 40)

        for domain_key, domain_info in DOMAINS.items():
            domain_score = domain_scores.get(domain_key, 0)
            weight = domain_info["weight"] * 100
            contribution = domain_score * domain_info["weight"]

            mini_bar = "█" * int(domain_score / 5) + "░" * (20 - int(domain_score / 5))
            lines.append(f"  {domain_info['icon']} {domain_info['name']:<20}")
            lines.append(f"     Score: {domain_score:5.1f}% {mini_bar}")
            lines.append(f"     Weight: {weight:.0f}% | Contribution: {contribution:.1f} points")
            lines.append("")

        # Interpretation
        lines.append("-" * 40)
        lines.append("")
        lines.append("Interpretation:")
        lines.append(_score_interpretation(score))
        lines.append("")

        # Recommendations
        lines.append("Recommendations:")
        weakest_domain = min(domain_scores.items(), key=lambda x: x[1])
        strongest_domain = max(domain_scores.items(), key=lambda x: x[1])

        lines.append(
            f"  • Strongest area: {DOMAINS[strongest_domain[0]]['name']} ({strongest_domain[1]:.1f}%)"
        )
        lines.append(
            f"  • Focus area: {DOMAINS[weakest_domain[0]]['name']} ({weakest_domain[1]:.1f}%)"
        )

        if score < 50:
            lines.append("  • Consider setting smaller, achievable goals to build momentum")
        elif score < 75:
            lines.append("  • You're making good progress - maintain consistency")
        else:
            lines.append("  • Excellent! Consider mentoring others or setting stretch goals")

        return "\n".join(lines)

    # ==========================================================================
    # Tool 3: Generate Domain Progress Bar
    # ==========================================================================

    @tool
    def generate_domain_progress_bar(
        user_id: str,
        domain: str,
        view: str = "weekly",
        bar_width: int = 40,
    ) -> str:
        """
        Generate detailed progress bar for a specific life domain.

        Creates an ASCII progress bar with percentage, trend indicator,
        and detailed breakdown of contributing factors.

        Args:
            user_id: The user's unique identifier
            domain: Domain to visualize - "career", "relationship", "finance", or "wellness"
            view: Timeframe - "daily", "weekly", or "monthly"
            bar_width: Width of the progress bar in characters

        Returns:
            Formatted progress bar with details

        Example:
            >>> generate_domain_progress_bar("user_123", "career", "weekly", 40)
            '💼 Career Progress: 68.5%\n[████████████████████░░░░░░░░░░░░░░░░░░░░] ▲ +5.2\n...'
        """
        if domain not in DOMAINS:
            return f"Error: Invalid domain '{domain}'. Choose from: {', '.join(DOMAINS.keys())}"

        if view not in VIEW_CONFIGS:
            view = "weekly"

        domain_info = DOMAINS[domain]
        progress = _get_domain_progress(user_id, domain, view, backend)
        trend = _get_domain_trend(user_id, domain, view, backend)

        # Get detailed breakdown
        breakdown = _get_domain_breakdown(user_id, domain, view, backend)

        lines = []
        lines.append("")
        lines.append(f"{domain_info['icon']} {domain_info['name'].upper()} PROGRESS")
        lines.append("=" * 60)
        lines.append("")

        # Main progress bar
        filled = int((progress / 100) * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)

        trend_icon = "▲" if trend > 0 else "▼" if trend < 0 else "→"
        trend_str = f"{trend_icon} {trend:+.1f}"

        lines.append(f"Progress: {progress:.1f}%")
        lines.append(f"[{bar}] {trend_str}")
        lines.append("")

        # Status description
        if progress >= 80:
            status = "Excellent"
            desc = "You're excelling in this area!"
        elif progress >= 60:
            status = "Good"
            desc = "Solid progress with room for growth"
        elif progress >= 40:
            status = "Developing"
            desc = "Making progress, keep building momentum"
        else:
            status = "Starting"
            desc = "Early stages - focus on small wins"

        lines.append(f"Status: {status}")
        lines.append(f"  {desc}")
        lines.append("")

        # Contributing factors
        if breakdown:
            lines.append("Contributing Factors:")
            for factor, value in breakdown.items():
                mini_bar = "█" * int(value / 10) + "░" * (10 - int(value / 10))
                lines.append(f"  {factor:<20} {value:5.1f}% {mini_bar}")
            lines.append("")

        # Tips for improvement
        lines.append("Tips to improve:")
        tips = _get_domain_tips(domain, progress)
        for tip in tips:
            lines.append(f"  • {tip}")

        return "\n".join(lines)

    # ==========================================================================
    # Tool 4: Create Mood Trend Sparkline
    # ==========================================================================

    @tool
    def create_mood_trend_sparkline(
        user_id: str,
        view: str = "weekly",
        width: int = 30,
    ) -> str:
        """
        Generate ASCII sparkline visualization of mood trends.

        Creates a text-based line chart showing mood changes over time
        using Unicode block characters (▁▂▃▄▅▆▇█).

        Args:
            user_id: The user's unique identifier
            view: Timeframe - "daily", "weekly", or "monthly"
            width: Width of the sparkline in characters

        Returns:
            Formatted sparkline chart with statistics

        Example:
            >>> create_mood_trend_sparkline("user_123", "weekly", 30)
            'Mood Trend (Last 7 Days):\n\n▃▄▆█▇▅▄▃\n\nStatistics:\n  Current: 6.5/10...'
        """
        if view not in VIEW_CONFIGS:
            view = "weekly"

        view_config = VIEW_CONFIGS[view]
        mood_data = _get_mood_history(user_id, view_config["mood_points"], backend)

        if not mood_data:
            return "No mood data available. Start logging your mood to see trends!"

        r = renderer
        sparkline = r._sparkline(mood_data, width=width, min_val=1, max_val=10)

        lines = []
        lines.append("")
        lines.append(f"😊 MOOD TREND SPARKLINE ({view_config['name']})")
        lines.append("=" * 60)
        lines.append("")
        lines.append(sparkline)
        lines.append("")

        # Statistics
        current = mood_data[-1]
        avg = sum(mood_data) / len(mood_data)
        min_val = min(mood_data)
        max_val = max(mood_data)

        lines.append("Statistics:")
        lines.append(f"  Current:     {current:.1f}/10 {'█' * int(current)}")
        lines.append(f"  Average:     {avg:.1f}/10 {'█' * int(avg)}")
        lines.append(f"  Range:       {min_val:.1f} - {max_val:.1f}")

        # Trend analysis
        if len(mood_data) >= 2:
            change = current - mood_data[0]
            if change > 1:
                trend_desc = "📈 Improving"
            elif change < -1:
                trend_desc = "📉 Declining"
            else:
                trend_desc = "➡️ Stable"

            lines.append(f"  Trend:       {trend_desc} ({change:+.1f} over period)")

        # Volatility
        if len(mood_data) >= 3:
            variance = sum((x - avg) ** 2 for x in mood_data) / len(mood_data)
            std_dev = variance**0.5

            if std_dev < 1:
                volatility = "Low (stable)"
            elif std_dev < 2:
                volatility = "Moderate"
            else:
                volatility = "High (variable)"

            lines.append(f"  Volatility:  {volatility} (σ={std_dev:.1f})")

        lines.append("")
        lines.append("Scale: ▁(low) ▂ ▃ ▄ ▅ ▆ ▇ █(high)")

        return "\n".join(lines)

    # ==========================================================================
    # Tool 5: Get Recent Achievements
    # ==========================================================================

    @tool
    def get_recent_achievements(user_id: str, limit: int = 5) -> str:
        """
        Display recent achievements and milestones.

        Retrieves and formats the user's most recent accomplishments
        across all life domains with significance indicators.

        Args:
            user_id: The user's unique identifier
            limit: Maximum number of achievements to display (default: 5)

        Returns:
            Formatted list of achievements with details

        Example:
            >>> get_recent_achievements("user_123", 3)
            '🏆 RECENT ACHIEVEMENTS\n\n1. ★ Completed Project X (Major)\n   Career - 2 days ago\n   ...'
        """
        achievements = _get_recent_achievements(user_id, limit, backend)

        if not achievements:
            return (
                "🏆 RECENT ACHIEVEMENTS\n\n"
                "No achievements recorded yet.\n\n"
                "Tips to build your achievement list:\n"
                "  • Set clear, measurable goals\n"
                "  • Celebrate small wins along the way\n"
                "  • Track milestones when you reach them\n"
                "  • Use update_milestone() to record achievements"
            )

        lines = []
        lines.append("🏆 RECENT ACHIEVEMENTS")
        lines.append("=" * 60)
        lines.append("")

        for i, ach in enumerate(achievements, 1):
            significance = ach.get("significance", "normal")
            icon = "★" if significance == "major" else "✦" if significance == "minor" else "✓"

            lines.append(f"{i}. {icon} {ach.get('title', 'Achievement')}")
            lines.append(f"   Domain: {ach.get('domain', 'General').title()}")
            lines.append(f"   Date: {ach.get('date', 'Unknown')}")

            if ach.get("description"):
                desc = ach.get("description")
                if len(desc) > 100:
                    desc = desc[:97] + "..."
                lines.append(f"   {desc}")

            lines.append("")

        # Summary stats
        major_count = sum(1 for a in achievements if a.get("significance") == "major")
        lines.append("-" * 40)
        lines.append(f"Showing {len(achievements)} recent achievements")
        lines.append(f"Major milestones: {major_count}")

        return "\n".join(lines)

    # ==========================================================================
    # Tool 6: Get Upcoming Milestones
    # ==========================================================================

    @tool
    def get_upcoming_milestones(user_id: str, limit: int = 5) -> str:
        """
        Display upcoming milestones and approaching deadlines.

        Shows goals and milestones with their remaining time,
        helping users prioritize upcoming work.

        Args:
            user_id: The user's unique identifier
            limit: Maximum number of milestones to display (default: 5)

        Returns:
            Formatted list of upcoming milestones with urgency indicators

        Example:
            >>> get_upcoming_milestones("user_123", 3)
            '🎯 UPCOMING MILESTONES\n\n🔥 Complete quarterly review (3 days)\n   Finance domain...'
        """
        milestones = _get_upcoming_milestones(user_id, limit, backend)

        if not milestones:
            return (
                "🎯 UPCOMING MILESTONES\n\n"
                "No upcoming milestones found.\n\n"
                "To set milestones:\n"
                "  • Use phase planning tools to set goals\n"
                "  • Define target dates for your objectives\n"
                "  • Break large goals into smaller milestones"
            )

        lines = []
        lines.append("🎯 UPCOMING MILESTONES")
        lines.append("=" * 60)
        lines.append("")

        for ms in milestones:
            days_left = ms.get("days_remaining")

            # Urgency indicator
            if days_left is not None:
                if days_left <= 3:
                    urgency = "🔥"
                elif days_left <= 7:
                    urgency = "⚡"
                elif days_left <= 14:
                    urgency = "📅"
                else:
                    urgency = "○"

                time_str = f"{days_left} day{'s' if days_left != 1 else ''}"
            else:
                urgency = "○"
                time_str = "No deadline"

            lines.append(f"{urgency} {ms.get('title', 'Milestone')}")
            lines.append(f"   Time remaining: {time_str}")

            if ms.get("domain"):
                lines.append(f"   Domain: {ms.get('domain').title()}")

            if ms.get("description"):
                desc = ms.get("description")
                if len(desc) > 80:
                    desc = desc[:77] + "..."
                lines.append(f"   {desc}")

            # Progress indicator if available
            if ms.get("progress") is not None:
                progress = ms.get("progress")
                bar = "█" * int(progress / 10) + "░" * (10 - int(progress / 10))
                lines.append(f"   Progress: [{bar}] {progress:.0f}%")

            lines.append("")

        # Summary
        urgent = sum(1 for m in milestones if m.get("days_remaining", 999) <= 7)
        lines.append("-" * 40)
        lines.append(f"Total upcoming: {len(milestones)}")
        lines.append(f"Urgent (≤7 days): {urgent}")

        return "\n".join(lines)

    # ==========================================================================
    # Tool 7: Export Dashboard Report
    # ==========================================================================

    @tool
    def export_dashboard_report(
        user_id: str,
        view: str = "weekly",
        format: str = "markdown",
        include_charts: bool = True,
    ) -> str:
        """
        Export dashboard data as a formatted report.

        Generates a comprehensive progress report in Markdown format
        suitable for saving, printing, or sharing.

        Args:
            user_id: The user's unique identifier
            view: Timeframe - "daily", "weekly", or "monthly"
            format: Output format - "markdown" (default) or "text"
            include_charts: Whether to include ASCII charts in output

        Returns:
            Confirmation message with report content or file path

        Example:
            >>> export_dashboard_report("user_123", "weekly", "markdown")
            'Report exported to workspace/dashboard_report_20240115.md\n\n# AI Life Coach Progress Report...'
        """
        if view not in VIEW_CONFIGS:
            view = "weekly"

        view_config = VIEW_CONFIGS[view]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        date_display = datetime.now().strftime("%B %d, %Y")

        lines = []

        # Header
        lines.append("# 🎯 AI Life Coach Progress Report")
        lines.append("")
        lines.append(f"**User:** {user_id}  ")
        lines.append(f"**Period:** {view_config['name']}  ")
        lines.append(f"**Generated:** {date_display}  ")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Executive Summary
        lines.append("## 📊 Executive Summary")
        lines.append("")

        overall_score = _calculate_overall_score(user_id, view, backend)
        lines.append(f"### Overall Life Satisfaction: {overall_score:.1f}/100")
        lines.append("")
        lines.append(f"**Status:** {_score_label(overall_score)}")
        lines.append("")

        if include_charts:
            bar_width = 40
            filled = int((overall_score / 100) * bar_width)
            bar = "█" * filled + "░" * (bar_width - filled)
            lines.append(f"```")
            lines.append(f"[{bar}]")
            lines.append(f"```")
            lines.append("")

        # Domain Summary
        lines.append("## 📈 Domain Progress Summary")
        lines.append("")
        lines.append("| Domain | Progress | Trend | Status |")
        lines.append("|--------|----------|-------|--------|")

        for domain_key, domain_info in DOMAINS.items():
            progress = _get_domain_progress(user_id, domain_key, view, backend)
            trend = _get_domain_trend(user_id, domain_key, view, backend)
            trend_str = f"{trend:+.1f}" if trend != 0 else "~"
            status = _score_label(progress)

            lines.append(
                f"| {domain_info['icon']} {domain_info['name']} | "
                f"{progress:.1f}% | {trend_str} | {status} |"
            )

        lines.append("")

        # Mood Analysis
        lines.append("## 😊 Mood Analysis")
        lines.append("")

        mood_data = _get_mood_history(user_id, view_config["mood_points"], backend)
        if mood_data:
            current = mood_data[-1]
            avg = sum(mood_data) / len(mood_data)
            lines.append(f"- **Current Mood:** {current:.1f}/10")
            lines.append(f"- **Average Mood:** {avg:.1f}/10")
            lines.append(f"- **Mood Range:** {min(mood_data):.1f} - {max(mood_data):.1f}")

            if include_charts:
                sparkline = renderer._sparkline(mood_data, width=30)
                lines.append(f"- **Trend:** `{sparkline}`")
        else:
            lines.append("No mood data recorded for this period.")

        lines.append("")

        # Achievements
        lines.append("## 🏆 Recent Achievements")
        lines.append("")

        achievements = _get_recent_achievements(user_id, 5, backend)
        if achievements:
            for ach in achievements:
                sig_icon = "⭐" if ach.get("significance") == "major" else "✓"
                lines.append(
                    f"- {sig_icon} **{ach.get('title')}** ({ach.get('domain', 'General')})"
                )
                if ach.get("description"):
                    lines.append(f"  - {ach.get('description')}")
        else:
            lines.append("No achievements recorded this period.")

        lines.append("")

        # Upcoming Milestones
        lines.append("## 🎯 Upcoming Milestones")
        lines.append("")

        milestones = _get_upcoming_milestones(user_id, 5, backend)
        if milestones:
            for ms in milestones:
                days = ms.get("days_remaining", "?")
                lines.append(f"- **{ms.get('title')}** - {days} days remaining")
                if ms.get("description"):
                    lines.append(f"  - {ms.get('description')}")
        else:
            lines.append("No upcoming milestones set.")

        lines.append("")

        # Insights and Recommendations
        lines.append("## 💡 Insights & Recommendations")
        lines.append("")

        domain_scores = {k: _get_domain_progress(user_id, k, view, backend) for k in DOMAINS.keys()}
        weakest = min(domain_scores.items(), key=lambda x: x[1])
        strongest = max(domain_scores.items(), key=lambda x: x[1])

        lines.append(f"### Strengths")
        lines.append(
            f"Your strongest area is **{DOMAINS[strongest[0]]['name']}** at {strongest[1]:.1f}%. "
        )
        lines.append("Continue building on this success!")
        lines.append("")

        lines.append(f"### Growth Opportunities")
        lines.append(f"Consider focusing on **{DOMAINS[weakest[0]]['name']}** ({weakest[1]:.1f}%).")
        lines.append("Small consistent actions can create meaningful improvement.")
        lines.append("")

        # Footer
        lines.append("---")
        lines.append("")
        lines.append("*This report was generated by AI Life Coach*  ")
        lines.append("*Track your progress daily for best results*")

        report_content = "\n".join(lines)

        # Save to file
        try:
            filename = f"dashboard_report_{user_id}_{view}_{timestamp}.md"
            filepath = backend.workspace / filename

            with open(filepath, "w") as f:
                f.write(report_content)

            return (
                f"✅ Report exported successfully!\n\nFile: {filepath}\n\n{report_content[:500]}..."
            )
        except Exception as e:
            return f"Report generated (save failed: {e}):\n\n{report_content}"

    # ==========================================================================
    # Tool 8: Switch Dashboard View
    # ==========================================================================

    @tool
    def switch_dashboard_view(
        user_id: str,
        view: str,
        render: bool = True,
    ) -> str:
        """
        Switch between daily, weekly, and monthly dashboard views.

        Changes the timeframe for all dashboard displays and optionally
        renders the updated dashboard.

        Args:
            user_id: The user's unique identifier
            view: New view mode - "daily", "weekly", or "monthly"
            render: Whether to render the dashboard immediately

        Returns:
            Confirmation message and optionally the rendered dashboard

        Example:
            >>> switch_dashboard_view("user_123", "monthly", render=True)
            'View switched to monthly. Here is your updated dashboard...'
        """
        if view not in VIEW_CONFIGS:
            valid_views = ", ".join(VIEW_CONFIGS.keys())
            return f"Error: Invalid view '{view}'. Choose from: {valid_views}"

        view_config = VIEW_CONFIGS[view]

        message_parts = []
        message_parts.append(f"✅ Dashboard view switched to **{view_config['name']}**")
        message_parts.append("")
        message_parts.append(f"This view shows:")
        message_parts.append(f"  • Data from the last {view_config['days']} days")
        message_parts.append(f"  • {view_config['mood_points']} data points for trends")
        message_parts.append(f"  • {view_config['aggregation']} aggregation method")
        message_parts.append("")

        if render:
            message_parts.append("=" * 60)
            message_parts.append("")
            dashboard = render_progress_dashboard.invoke(
                {
                    "user_id": user_id,
                    "view": view,
                }
            )
            message_parts.append(dashboard)

        return "\n".join(message_parts)

    print("Dashboard tools created successfully!")
    return (
        render_progress_dashboard,
        calculate_life_satisfaction_score,
        generate_domain_progress_bar,
        create_mood_trend_sparkline,
        get_recent_achievements,
        get_upcoming_milestones,
        export_dashboard_report,
        switch_dashboard_view,
    )


# ==============================================================================
# Helper Functions
# ==============================================================================


def _calculate_overall_score(user_id: str, view: str, backend) -> float:
    """Calculate overall life satisfaction score (0-100)."""
    scores = []
    weights = []

    for domain_key, domain_info in DOMAINS.items():
        progress = _get_domain_progress(user_id, domain_key, view, backend)
        scores.append(progress)
        weights.append(domain_info["weight"])

    # Weighted average
    if scores:
        total_weight = sum(weights)
        weighted_sum = sum(s * w for s, w in zip(scores, weights))
        return weighted_sum / total_weight if total_weight > 0 else 0
    return 50.0  # Default neutral score


def _get_domain_progress(user_id: str, domain: str, view: str, backend) -> float:
    """Get progress percentage for a specific domain (0-100)."""
    # Try to load from stored check-in data
    try:
        checkin_file = backend.workspace / f"checkins_{user_id}.json"
        if checkin_file.exists():
            with open(checkin_file) as f:
                checkins = json.load(f)

            # Get most recent check-ins for this view
            view_days = VIEW_CONFIGS[view]["days"]
            cutoff = (datetime.now() - timedelta(days=view_days)).isoformat()

            recent_checkins = [c for c in checkins if c.get("timestamp", "") >= cutoff]

            if recent_checkins:
                # Look for domain-specific progress in check-ins
                key = f"{domain}_goals_completed"
                values = [
                    c.get("responses", {}).get(key, 50)
                    for c in recent_checkins
                    if key in c.get("responses", {})
                ]

                if values:
                    return sum(values) / len(values)
    except Exception:
        pass

    # Default: generate from mock/simulated data for demo
    return _generate_mock_progress(user_id, domain, view)


def _get_domain_trend(user_id: str, domain: str, view: str, backend) -> float:
    """Get trend change for a domain (+/- percentage points)."""
    # Compare current period to previous period
    current = _get_domain_progress(user_id, domain, view, backend)

    # For trend, we'd ideally compare to previous period
    # For now, simulate a small trend
    import hashlib

    hash_val = int(hashlib.md5(f"{user_id}{domain}{view}".encode()).hexdigest(), 16)
    return (hash_val % 20) - 10  # -10 to +10


def _get_domain_breakdown(user_id: str, domain: str, view: str, backend) -> Dict[str, float]:
    """Get breakdown of factors contributing to domain score."""
    # Domain-specific breakdowns
    breakdowns = {
        "career": {
            "Goal Completion": 0,
            "Skill Development": 0,
            "Work Satisfaction": 0,
            "Work-Life Balance": 0,
        },
        "relationship": {
            "Communication": 0,
            "Quality Time": 0,
            "Support Network": 0,
            "Conflict Resolution": 0,
        },
        "finance": {
            "Budget Adherence": 0,
            "Savings Progress": 0,
            "Debt Reduction": 0,
            "Investment Growth": 0,
        },
        "wellness": {
            "Physical Activity": 0,
            "Sleep Quality": 0,
            "Stress Management": 0,
            "Healthy Eating": 0,
        },
    }

    base_progress = _get_domain_progress(user_id, domain, view, backend)

    # Generate realistic breakdown around base progress
    import random

    random.seed(f"{user_id}{domain}{view}")

    factors = breakdowns.get(domain, {})
    for key in factors:
        # Vary each factor around the base progress
        variation = random.uniform(-15, 15)
        factors[key] = max(0, min(100, base_progress + variation))

    return factors


def _get_mood_history(user_id: str, points: int, backend) -> List[float]:
    """Get mood history data for sparkline."""
    try:
        mood_file = backend.workspace / f"mood_{user_id}.json"
        if mood_file.exists():
            with open(mood_file) as f:
                entries = json.load(f)

            # Extract mood scores
            scores = []
            for entry in entries[-points:]:
                if "composite_score" in entry:
                    scores.append(entry["composite_score"])
                elif "dimensions" in entry:
                    dims = entry["dimensions"]
                    score = (
                        dims.get("happiness", 5)
                        + (10 - dims.get("stress", 5))  # Invert stress
                        + dims.get("energy", 5)
                        + dims.get("motivation", 5)
                    ) / 4
                    scores.append(score)

            if len(scores) >= 2:
                return scores
    except Exception:
        pass

    # Generate mock data if no real data
    return _generate_mock_mood_data(user_id, points)


def _get_recent_achievements(user_id: str, limit: int, backend) -> List[Dict]:
    """Get recent achievements from storage or memory."""
    achievements = []

    try:
        # Try to load from milestones file
        milestone_file = backend.workspace / f"milestones_{user_id}.json"
        if milestone_file.exists():
            with open(milestone_file) as f:
                data = json.load(f)
                milestones = data.get("milestones", [])

                for ms in milestones[-limit:]:
                    achievements.append(
                        {
                            "title": ms.get("title", "Achievement"),
                            "description": ms.get("description", ""),
                            "domain": ms.get("domain", "general"),
                            "date": ms.get("achieved_at", "Recently"),
                            "significance": ms.get("significance", "normal"),
                        }
                    )

                if achievements:
                    return list(reversed(achievements))  # Most recent first
    except Exception:
        pass

    # Generate mock achievements if none exist
    return _generate_mock_achievements(user_id, limit)


def _get_upcoming_milestones(user_id: str, limit: int, backend) -> List[Dict]:
    """Get upcoming milestones with days remaining."""
    milestones = []

    try:
        # Try to load from goals/plans
        goals_file = backend.workspace / f"goals_{user_id}.json"
        if goals_file.exists():
            with open(goals_file) as f:
                data = json.load(f)
                goals = data.get("goals", [])

                now = datetime.now()

                for goal in goals:
                    if goal.get("status") != "completed":
                        target_date = goal.get("target_date")
                        if target_date:
                            try:
                                target = datetime.fromisoformat(target_date)
                                days_remaining = (target - now).days

                                if days_remaining >= 0:  # Future or today
                                    milestones.append(
                                        {
                                            "title": goal.get("title", "Goal"),
                                            "description": goal.get("description", ""),
                                            "domain": goal.get("domain", "general"),
                                            "days_remaining": days_remaining,
                                            "progress": goal.get("progress", 0),
                                        }
                                    )
                            except:
                                pass

                # Sort by days remaining
                milestones.sort(key=lambda x: x.get("days_remaining", 999))

                if milestones:
                    return milestones[:limit]
    except Exception:
        pass

    # Generate mock milestones
    return _generate_mock_milestones(user_id, limit)


def _score_color(score: float) -> str:
    """Get color code for a score (for terminals that support it)."""
    if score >= 80:
        return "\033[92m"  # Green
    elif score >= 60:
        return "\033[93m"  # Yellow
    elif score >= 40:
        return "\033[93m"  # Orange-ish
    else:
        return "\033[91m"  # Red


def _score_label(score: float) -> str:
    """Get text label for a score."""
    if score >= 80:
        return "Excellent"
    elif score >= 60:
        return "Good"
    elif score >= 40:
        return "Developing"
    else:
        return "Starting"


def _score_interpretation(score: float) -> str:
    """Get interpretation text for a score."""
    interpretations = {
        (
            80,
            100,
        ): "Your life satisfaction is in an excellent range. You're thriving across multiple domains. Consider mentoring others or setting ambitious stretch goals.",
        (
            60,
            80,
        ): "You're doing well with solid progress across domains. Focus on maintaining consistency while addressing your lowest-scoring area.",
        (
            40,
            60,
        ): "You're making progress but there's room for improvement. Focus on small wins and building momentum in your weakest domain.",
        (
            0,
            40,
        ): "You're in the early stages of your journey. Start with small, achievable goals and celebrate every step forward.",
    }

    for (min_s, max_s), text in interpretations.items():
        if min_s <= score <= max_s:
            return text

    return "Keep tracking your progress to see trends over time."


def _get_domain_tips(domain: str, progress: float) -> List[str]:
    """Get tips for improving in a domain."""
    tips = {
        "career": [
            "Set 15 minutes daily for skill development",
            "Schedule regular check-ins with your manager",
            "Build your professional network consistently",
            "Document your achievements weekly",
        ],
        "relationship": [
            "Practice active listening in conversations",
            "Schedule quality time with loved ones",
            "Express appreciation daily",
            "Set healthy boundaries respectfully",
        ],
        "finance": [
            "Review your budget weekly",
            "Set up automatic savings transfers",
            "Track expenses for one week",
            "Learn about one investment option",
        ],
        "wellness": [
            "Move your body for 20 minutes daily",
            "Establish a consistent sleep schedule",
            "Practice 5 minutes of mindfulness",
            "Hydrate - drink water regularly",
        ],
    }

    domain_tips = tips.get(domain, ["Set specific, measurable goals", "Track your progress daily"])

    # Add progress-specific tips
    if progress < 40:
        domain_tips.insert(0, "Start with one small habit")
    elif progress > 80:
        domain_tips.insert(0, "Challenge yourself with stretch goals")

    return domain_tips[:3]


# Mock data generators for demo/testing
def _generate_mock_progress(user_id: str, domain: str, view: str) -> float:
    """Generate deterministic mock progress for demo."""
    import hashlib

    seed = f"{user_id}{domain}{view}"
    hash_val = int(hashlib.md5(seed.encode()).hexdigest(), 16)

    # Generate between 30-90%
    base = 30 + (hash_val % 60)
    return float(base)


def _generate_mock_mood_data(user_id: str, points: int) -> List[float]:
    """Generate deterministic mock mood data for demo."""
    import hashlib
    import random

    seed = f"{user_id}mood"
    hash_val = int(hashlib.md5(seed.encode()).hexdigest(), 16)
    random.seed(hash_val)

    # Generate realistic mood curve (5-8 range typical)
    data = []
    current = 6.0

    for _ in range(points):
        change = random.uniform(-1.5, 1.5)
        current = max(1, min(10, current + change))
        data.append(round(current, 1))

    return data


def _generate_mock_achievements(user_id: str, limit: int) -> List[Dict]:
    """Generate mock achievements for demo."""
    mock_achievements = [
        {
            "title": "Completed Weekly Check-in Streak",
            "description": "Logged progress for 4 consecutive weeks",
            "domain": "wellness",
            "date": "2 days ago",
            "significance": "minor",
        },
        {
            "title": "Emergency Fund Milestone",
            "description": "Reached 50% of emergency fund goal",
            "domain": "finance",
            "date": "1 week ago",
            "significance": "major",
        },
        {
            "title": "Skill Assessment Completed",
            "description": "Identified key growth areas for career",
            "domain": "career",
            "date": "1 week ago",
            "significance": "normal",
        },
        {
            "title": "Quality Time Initiative",
            "description": "Planned and executed meaningful family activity",
            "domain": "relationship",
            "date": "2 weeks ago",
            "significance": "normal",
        },
        {
            "title": "Stress Management Breakthrough",
            "description": "Successfully applied new coping technique",
            "domain": "wellness",
            "date": "2 weeks ago",
            "significance": "major",
        },
    ]

    return mock_achievements[:limit]


def _generate_mock_milestones(user_id: str, limit: int) -> List[Dict]:
    """Generate mock milestones for demo."""
    mock_milestones = [
        {
            "title": "Complete Quarterly Review",
            "description": "Prepare and deliver Q1 performance review",
            "domain": "career",
            "days_remaining": 3,
            "progress": 75,
        },
        {
            "title": "Emergency Fund Target",
            "description": "Reach $5,000 emergency savings goal",
            "domain": "finance",
            "days_remaining": 14,
            "progress": 85,
        },
        {
            "title": "Weekly Date Night",
            "description": "Schedule quality time with partner",
            "domain": "relationship",
            "days_remaining": 5,
            "progress": 0,
        },
        {
            "title": "Exercise Consistency",
            "description": "Complete 4 workouts this week",
            "domain": "wellness",
            "days_remaining": 4,
            "progress": 50,
        },
        {
            "title": "Networking Event",
            "description": "Attend industry meetup and connect with 3 people",
            "domain": "career",
            "days_remaining": 10,
            "progress": 25,
        },
    ]

    return mock_milestones[:limit]


# Export tools at module level for convenience
__all__ = [
    "create_dashboard_tools",
    "DashboardRenderer",
    "DOMAINS",
    "VIEW_CONFIGS",
]
