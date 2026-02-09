#!/usr/bin/env python3
"""
AI Life Coach - TUI-Enhanced CLI Interface

Feature-rich terminal interface with Gruvbox Dark Hard theme.

Usage:
    python life_coach_tui.py                    # Start interactive session
    python life_coach_tui.py --user <id>        # Resume previous session
    python life_coach_tui.py --export report    # Generate progress report
    python life_coach_tui.py --help             # Show usage

Theme: Gruvbox Dark Hard
    - Background: #1d2021 (hardest background)
    - Foreground: #ebdbb2 (main text)
    - Accents: Muted pastels from official Gruvbox palette
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import argparse

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Initialize environment before importing other modules
try:
    from src.config import config, get_backend

    config.initialize_environment()
    backend = get_backend()
except Exception as e:
    print(f"Error: Environment initialization failed: {e}")
    sys.exit(1)

# Import the main AI Life Coach system
try:
    from src.main import create_life_coach
except Exception as e:
    print(f"Error: Main module import failed: {e}")
    sys.exit(1)

# Import Rich for TUI rendering
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.columns import Columns
from rich.layout import Layout
from rich.align import Align
from rich.live import Live
from rich.spinner import Spinner
import time

# Configure logging
log_dir = Path.home() / ".ai_life_coach"
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "tui.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


# ============================================================================
# GRUVBOX DARK HARD THEME PALETTE
# ============================================================================


class GruvboxColors:
    """
    Official Gruvbox Dark Hard color palette.

    Source: https://github.com/gruvbox-community/gruvbox
    """

    # Backgrounds (hard contrast for Dark Hard variant)
    BG_HARD = "#1d2021"  # Main background (darkest)
    BG0 = "#282828"  # Standard dark background
    BG1 = "#3c3836"  # Background for panels, borders
    BG2 = "#504945"  # Background for secondary elements
    BG3 = "#665c54"  # Background for tertiary elements
    BG4 = "#7c6f64"  # Darkest gray

    # Foregrounds
    FG0 = "#fbf1c7"  # Brightest text (titles, headers)
    FG1 = "#ebdbb2"  # Main foreground (body text)
    FG2 = "#d5c4a1"  # Secondary foreground
    FG3 = "#bdae93"  # Tertiary foreground (dimmed text)
    FG4 = "#a89984"  # Dimmest foreground (timestamps, metadata)

    # Bright accent colors (for emphasis)
    BRIGHT_RED = "#fb4934"
    BRIGHT_GREEN = "#b8bb26"
    BRIGHT_YELLOW = "#fabd2f"
    BRIGHT_BLUE = "#83a598"
    BRIGHT_PURPLE = "#d3869b"
    BRIGHT_AQUA = "#8ec07c"
    BRIGHT_ORANGE = "#fe8019"

    # Neutral accent colors (for standard use)
    NEUTRAL_RED = "#cc241d"
    NEUTRAL_GREEN = "#98971a"
    NEUTRAL_YELLOW = "#d79921"
    NEUTRAL_BLUE = "#458588"
    NEUTRAL_PURPLE = "#b16286"
    NEUTRAL_AQUA = "#689d6a"
    NEUTRAL_ORANGE = "#d65d0e"

    # Faded accent colors (for subtle use)
    FADED_RED = "#9d0006"
    FADED_GREEN = "#79740e"
    FADED_YELLOW = "#b57614"
    FADED_BLUE = "#076678"
    FADED_PURPLE = "#8f3f71"
    FADED_AQUA = "#427b58"
    FADED_ORANGE = "#af3a03"

    # Gray scale
    GRAY_245 = "#928374"  # Comment color, metadata


# ============================================================================
# SHARED CLASSES (REUSED FROM ORIGINAL CLI)
# ============================================================================


class SessionManager:
    """Manages session persistence and state."""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.session_dir = Path.home() / ".ai_life_coach" / "sessions"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.session_file = self.session_dir / f"{user_id}.json"

    def load_session(self) -> Dict[str, Any]:
        """Load previous session if it exists."""
        if not self.session_file.exists():
            return {
                "user_id": self.user_id,
                "created_at": datetime.now().isoformat(),
                "last_accessed": None,
                "message_history": [],
                "profile_data": {},
            }

        try:
            with open(self.session_file, "r") as f:
                session = json.load(f)
                session["last_accessed"] = datetime.now().isoformat()
                return session
        except Exception as e:
            logger.error(f"Failed to load session: {e}")
            return self._create_new_session()

    def save_session(self, session: Dict[str, Any]):
        """Save current session state."""
        try:
            session["last_accessed"] = datetime.now().isoformat()
            with open(self.session_file, "w") as f:
                json.dump(session, f, indent=2)
            logger.info(f"Session saved for user {self.user_id}")
        except Exception as e:
            logger.error(f"Failed to save session: {e}")

    def _create_new_session(self) -> Dict[str, Any]:
        """Create a new session."""
        return {
            "user_id": self.user_id,
            "created_at": datetime.now().isoformat(),
            "last_accessed": None,
            "message_history": [],
            "profile_data": {},
        }


class ReportGenerator:
    """Generates various types of progress reports."""

    def __init__(self, session_data: Dict[str, Any]):
        self.session = session_data

    def generate_markdown_report(self) -> str:
        """Generate a Markdown progress report."""
        lines = [
            "# AI Life Coach Progress Report",
            "",
            f"**User ID:** {self.session['user_id']}",
            f"**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
        ]

        if self.session.get("created_at"):
            created = datetime.fromisoformat(self.session["created_at"])
            lines.append(f"**Session Started:** {created.strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append("")

        if self.session.get("last_accessed"):
            accessed = datetime.fromisoformat(self.session["last_accessed"])
            duration = accessed - created
            lines.append(f"**Last Access:** {accessed.strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append(
                f"**Session Duration:** {str(timedelta(seconds=int(duration.total_seconds())))}"
            )
            lines.append("")

        # Message history summary
        history = self.session.get("message_history", [])
        lines.append("## Session Summary")
        lines.append("")
        lines.append(f"- **Total Exchanges:** {len(history)}")
        lines.append("")

        if history:
            # Show last few exchanges
            lines.append("## Recent Conversations")
            lines.append("")
            for i, exchange in enumerate(history[-5:], 1):
                user_msg = exchange.get("user", "")[:100]
                coach_response = exchange.get("coach", "")[:100]
                lines.append(f"### Exchange {i}")
                lines.append("")
                lines.append(f"**You:** {user_msg}...")
                lines.append(f"**Coach:** {coach_response}...")
                lines.append("")

        return "\n".join(lines)

    def generate_json_report(self) -> str:
        """Generate a JSON progress report."""
        report = {
            "user_id": self.session["user_id"],
            "report_generated": datetime.now().isoformat(),
            "session_data": self.session,
            "statistics": {
                "total_exchanges": len(self.session.get("message_history", [])),
                "session_created": self.session.get("created_at"),
                "last_accessed": self.session.get("last_accessed"),
            },
        }
        return json.dumps(report, indent=2)


# ============================================================================
# TUI RENDERER CLASS
# ============================================================================


class TUIRenderer:
    """
    Handles all visual presentation using Rich library with Gruvbox Dark Hard theme.
    """

    def __init__(self):
        """Initialize the TUI renderer with Gruvbox theme."""
        self.console = Console()
        self.colors = GruvboxColors()

    def clear_screen(self):
        """Clear the terminal screen."""
        self.console.clear()

    def print_welcome(self, user_id: str, is_new_user: bool = False):
        """
        Display animated welcome screen with branding.

        Args:
            user_id: The current user ID
            is_new_user: Whether this is a new user (no previous session)
        """
        self.clear_screen()

        # Create logo banner
        logo = Text()
        logo.append(Text("🧠 ", style=f"bold {self.colors.BRIGHT_GREEN}"))
        logo.append(Text("AI Life Coach", style=f"bold {self.colors.FG0}"))

        # Welcome message
        if is_new_user:
            subtitle = "Welcome to your personal growth journey!"
            subtitle_style = self.colors.FG2
        else:
            subtitle = f"Welcome back, {user_id}!"
            subtitle_style = self.colors.FG2

        # Session info
        now = datetime.now()
        date_str = now.strftime("%A, %B %d, %Y")
        time_str = now.strftime("%I:%M %p")

        # Build welcome panel
        content = Text()
        content.append(logo, style=f"bold {self.colors.FG0}")
        content.append("\n\n")
        content.append(subtitle, style=subtitle_style)
        content.append("\n\n")

        # Session details
        session_info = Text()
        session_info.append(Text("📅 ", style=self.colors.BRIGHT_YELLOW))
        session_info.append(date_str, style=self.colors.FG1)
        session_info.append(Text("  •  ", style=self.colors.BG4))
        session_info.append(Text("🕐 ", style=self.colors.BRIGHT_YELLOW))
        session_info.append(time_str, style=self.colors.FG1)

        content.append(session_info)

        # Tips panel
        tips = Text()
        tips.append(Text("\n\nQuick Tips:\n", style=f"bold {self.colors.BRIGHT_BLUE}"))
        tips.append(Text("• Type your message to chat with the coach\n", style=self.colors.FG2))
        tips.append(Text("• Use ", style=self.colors.FG3))
        tips.append(Text("/help", style=f"bold {self.colors.BRIGHT_ORANGE}"))
        tips.append(Text(" for commands\n", style=self.colors.FG3))
        tips.append(Text("• All conversations are saved automatically\n", style=self.colors.FG2))

        content.append(tips)

        # Create the main panel
        panel = Panel(
            Align.center(content),
            title=f"[{self.colors.FG0}]AI Life Coach[/]",
            title_align="center",
            border_style=self.colors.BRIGHT_GREEN,
            padding=(1, 2),
        )

        self.console.print(panel)
        self.console.print()

    def print_message(self, role: str, content: str, timestamp: Optional[str] = None):
        """
        Print a styled chat message.

        Args:
            role: Either 'user' or 'coach'
            content: The message content
            timestamp: Optional timestamp string (ISO format)
        """
        # Format timestamp if provided
        time_str = ""
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%H:%M")
            except:
                pass

        if role == "user":
            # User message - right-aligned, green accent
            prefix = Text()
            prefix.append(Text("You", style=f"bold {self.colors.BRIGHT_GREEN}"))
            if time_str:
                prefix.append(f" · {time_str}", style=self.colors.FG4)

            # Create right-aligned panel
            message = Text(content, style=self.colors.FG1)

            panel = Panel(
                Align.right(message),
                title=str(prefix),
                border_style=self.colors.BRIGHT_GREEN,
                padding=(0, 1),
            )
        else:
            # Coach message - left-aligned, blue/cyan accent
            prefix = Text()
            prefix.append(Text("Coach", style=f"bold {self.colors.BRIGHT_BLUE}"))
            if time_str:
                prefix.append(f" · {time_str}", style=self.colors.FG4)

            # Create left-aligned panel
            message = Text(content, style=self.colors.FG1)

            panel = Panel(
                Align.left(message),
                title=str(prefix),
                border_style=self.colors.BRIGHT_BLUE,
                padding=(0, 1),
            )

        self.console.print(panel)
        self.console.print()

    def show_typing_indicator(self):
        """Display a typing indicator while coach is processing."""
        spinner = Spinner("dots", text=" Coach is thinking...", style=self.colors.BRIGHT_BLUE)
        self.console.print(spinner)
        return spinner

    def print_dashboard(self, session_data: Dict[str, Any]):
        """
        Display session dashboard with statistics.

        Args:
            session_data: Current session data dictionary
        """
        # Calculate statistics
        history = session_data.get("message_history", [])
        total_exchanges = len(history)

        # Calculate session duration
        created_str = session_data.get("created_at")
        last_accessed_str = session_data.get("last_accessed")

        if created_str and last_accessed_str:
            try:
                created = datetime.fromisoformat(created_str)
                accessed = datetime.fromisoformat(last_accessed_str)
                duration = accessed - created
                duration_str = str(timedelta(seconds=int(duration.total_seconds())))
            except:
                duration_str = "Unknown"
        else:
            duration_str = "N/A"

        # Create statistics table
        stats_table = Table(
            title=f"[{self.colors.FG0}]Session Statistics[/]",
            show_header=True,
            header_style=f"bold {self.colors.FG0}",
            border_style=self.colors.BG3,
            box=None,
        )
        stats_table.add_column("Metric", style=self.colors.FG2)
        stats_table.add_column("Value", justify="right", style=self.colors.BRIGHT_GREEN)

        stats_table.add_row("Total Exchanges", str(total_exchanges))
        stats_table.add_row("Session Duration", duration_str)
        if created_str:
            try:
                created = datetime.fromisoformat(created_str)
                stats_table.add_row("Session Started", created.strftime("%Y-%m-%d %H:%M"))
            except:
                pass

        # Mood tracker visualization (emoji-based with Gruvbox colors)
        mood_table = Table(
            title=f"[{self.colors.FG0}]Current Focus Areas[/]",
            show_header=False,
            border_style=self.colors.BG3,
        )

        mood_table.add_column("Area", style=self.colors.FG2)
        mood_table.add_row(
            f"[{self.colors.BRIGHT_PURPLE}]🎯[/] Personal Growth",
        )
        mood_table.add_row(
            f"[{self.colors.BRIGHT_AQUA}]💼[/] Career Development",
        )
        mood_table.add_row(
            f"[{self.colors.BRIGHT_ORANGE}]💪[/] Wellness & Health",
        )
        mood_table.add_row(
            f"[{self.colors.BRIGHT_YELLOW}]🤝[/] Relationships",
        )

        # Last save indicator
        last_save = Text()
        last_save.append(Text("💾 ", style=self.colors.BRIGHT_AQUA))
        if last_accessed_str:
            try:
                accessed = datetime.fromisoformat(last_accessed_str)
                last_save.append(
                    f"Last saved: {accessed.strftime('%H:%M:%S')}",
                    style=self.colors.FG3,
                )
            except:
                last_save.append(Text("Last saved: Unknown", style=self.colors.FG3))
        else:
            last_save.append(Text("Session not saved yet", style=self.colors.FG4))

        # Combine into columns
        dashboard = Columns(
            [
                Panel(stats_table, border_style=self.colors.BG3),
                Panel(mood_table, border_style=self.colors.BG3),
            ]
        )

        self.console.print(Panel(dashboard))
        self.console.print()
        self.console.print(last_save)
        self.console.print()

    def print_help(self):
        """Display help information with styled command palette."""
        self.console.print()

        # Help panel
        help_panel = Panel(
            Text("Available Commands", style=f"bold {self.colors.FG0}"),
            title="[?]",
            title_align="center",
            border_style=self.colors.BRIGHT_BLUE,
        )
        self.console.print(help_panel)

        # Commands table
        commands_table = Table(
            show_header=True,
            header_style=f"bold {self.colors.FG0}",
            border_style=self.colors.BG3,
        )
        commands_table.add_column("Command", style=f"bold {self.colors.BRIGHT_ORANGE}")
        commands_table.add_column("Description", style=self.colors.FG1)
        commands_table.add_column("Shortcut", justify="center", style=self.colors.BRIGHT_YELLOW)

        commands_table.add_row("/help or /?", "Show this help message", "?")
        commands_table.add_row("/report or /r", "Generate and display progress report", "r")
        commands_table.add_row("/export [format]", "Export report (markdown/json)", "e")
        commands_table.add_row("/clear or /c", "Clear the screen", "c")
        commands_table.add_row("/dashboard or /d", "Show session statistics dashboard", "d")
        commands_table.add_row("/exit or /quit", "End session and save progress", "q")

        self.console.print(commands_table)
        self.console.print()

    def print_report(self, session_data: Dict[str, Any]):
        """
        Display progress report with Markdown rendering.

        Args:
            session_data: Current session data dictionary
        """
        self.console.print()

        # Generate report
        report_gen = ReportGenerator(session_data)
        markdown_content = report_gen.generate_markdown_report()

        # Render with Markdown
        md = Markdown(markdown_content)

        report_panel = Panel(
            md,
            title=f"[{self.colors.FG0}]Progress Report[/]",
            border_style=self.colors.BRIGHT_AQUA,
            padding=(1, 2),
        )

        self.console.print(report_panel)
        self.console.print()

    def print_error(self, message: str):
        """Print an error message with Gruvbox red styling."""
        error_text = Text()
        error_text.append(Text("❌ ", style=self.colors.BRIGHT_RED))
        error_text.append(message, style=self.colors.FG1)

        panel = Panel(
            error_text,
            border_style=self.colors.NEUTRAL_RED,
            padding=(0, 1),
        )
        self.console.print(panel)
        self.console.print()

    def print_success(self, message: str):
        """Print a success message with Gruvbox green styling."""
        success_text = Text()
        success_text.append(Text("✅ ", style=self.colors.BRIGHT_GREEN))
        success_text.append(message, style=self.colors.FG1)

        panel = Panel(
            success_text,
            border_style=self.colors.NEUTRAL_GREEN,
            padding=(0, 1),
        )
        self.console.print(panel)
        self.console.print()

    def print_export_progress(self, export_func):
        """
        Export report with progress bar.

        Args:
            export_func: Function to call for exporting (must return success status)
        """
        self.console.print()
        with Progress(
            SpinnerColumn(style=self.colors.BRIGHT_BLUE),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40, style=self.colors.BRIGHT_AQUA),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task("Exporting report...", total=100)

            # Simulate progress
            for i in range(0, 101, 10):
                time.sleep(0.1)
                progress.update(task, advance=10)

            # Actually perform export
            success = export_func()

        if success:
            self.print_success("Report exported successfully!")
        else:
            self.print_error("Failed to export report")

    def print_status_bar(self, is_connected: bool = True):
        """
        Print a status bar at the bottom of the screen.

        Args:
            is_connected: Whether the coach system is connected
        """
        status_text = Text()

        # Connection indicator
        if is_connected:
            status_text.append(Text("●", style=self.colors.BRIGHT_GREEN))
            status_text.append(Text(" Connected", style=f"bold {self.colors.FG1}"))
        else:
            status_text.append(Text("●", style=self.colors.NEUTRAL_RED))
            status_text.append(Text(" Disconnected", style=f"bold {self.colors.FG4}"))

        # Add separator
        status_text.append(Text("  │  ", style=self.colors.BG4))

        # Auto-save indicator
        status_text.append(Text("💾 ", style=self.colors.BRIGHT_AQUA))
        status_text.append(Text("Auto-save enabled", style=f"bold {self.colors.FG1}"))

        # Create status bar panel
        status_panel = Panel(
            Align.center(status_text),
            border_style=self.colors.BG3,
            padding=(0, 1),
        )

        self.console.print(status_panel)

    def print_exit_message(self, total_exchanges: int):
        """
        Print exit message with session summary.

        Args:
            total_exchanges: Total number of message exchanges
        """
        self.console.print()

        # Create summary text
        summary = Text()
        summary.append(Text("Session Complete", style=f"bold {self.colors.FG0}"))
        summary.append(f"\n\nTotal exchanges: ", style=self.colors.FG2)
        summary.append(str(total_exchanges), style=f"bold {self.colors.BRIGHT_GREEN}")
        summary.append(f"\n\nProgress saved. Come back anytime!", style=self.colors.FG2)

        # Create panel
        panel = Panel(
            Align.center(summary),
            title=f"[{self.colors.FG0}]Goodbye![/]",
            title_align="center",
            border_style=self.colors.BRIGHT_GREEN,
            padding=(1, 2),
        )

        self.console.print(panel)
        self.console.print()

    def print_input_prompt(self):
        """Print the input prompt for user messages."""
        self.console.print(
            f"[{self.colors.BRIGHT_GREEN}]You:[/] ",
            end="",
        )


# ============================================================================
# MAIN TUI CLASS
# ============================================================================


class AILifeCoachTUI:
    """Production TUI-enhanced CLI for AI Life Coach."""

    def __init__(self, user_id: str = None):
        self.user_id = user_id or "default"
        self.coach = None
        self.session_manager = SessionManager(self.user_id)
        self.current_session = None
        self.renderer = TUIRenderer()
        self.verbose = False

    def initialize(self):
        """Initialize the coach system."""
        try:
            logger.info(f"Initializing AI Life Coach TUI for user: {self.user_id}")
            self.coach = create_life_coach()
            logger.info("AI Life Coach initialized successfully")

            # Load previous session
            self.current_session = self.session_manager.load_session()
            logger.info(
                f"Session loaded: {len(self.current_session.get('message_history', []))} previous exchanges"
            )

            return True
        except Exception as e:
            logger.error(f"Failed to initialize AI Life Coach: {e}")
            self.renderer.print_error(f"Failed to initialize system - {e}")
            return False

    def run_interactive_session(self):
        """Main interactive loop with TUI enhancements."""
        # Check if new user
        is_new_user = not bool(self.current_session.get("message_history"))

        # Show welcome screen
        self.renderer.print_welcome(self.user_id, is_new_user)

        # If returning user, show dashboard
        if not is_new_user:
            self.renderer.print_dashboard(self.current_session)

        # Show status bar
        self.renderer.print_status_bar(is_connected=True)

        while True:
            try:
                # Print input prompt
                self.renderer.print_input_prompt()

                user_input = input().strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.lower() in ["/exit", "/quit", "exit", "quit"]:
                    self.handle_exit()
                    break

                if user_input.lower() in ["/help", "/?", "help"]:
                    self.renderer.print_help()
                    continue

                if user_input.lower() in ["/report", "/r", "report"]:
                    self.generate_and_show_report()
                    continue

                if user_input.lower() in ["/clear", "/c", "clear"]:
                    self.renderer.clear_screen()
                    continue

                if user_input.lower() in ["/dashboard", "/d"]:
                    self.renderer.print_dashboard(self.current_session)
                    continue

                if user_input.lower().startswith("/export"):
                    parts = user_input.split()
                    format_type = "markdown"
                    if len(parts) > 1:
                        format_type = parts[1]
                    self.export_report_with_progress(format=format_type)
                    continue

                # Send message to coach
                response = self.send_message(user_input)

                # Display user message (already logged, but show it)
                history = self.current_session.get("message_history", [])
                if history:
                    last_exchange = history[-1]
                    self.renderer.print_message(
                        "user", last_exchange["user"], last_exchange.get("timestamp")
                    )

                # Show typing indicator
                self.renderer.show_typing_indicator()

                # Display coach response
                self.renderer.print_message("coach", response)

            except KeyboardInterrupt:
                print("\n\nInterrupt detected. Saving session...")
                self.handle_exit()
                break

            except EOFError:
                print("\n\nSession ended. Saving progress...")
                self.handle_exit()
                break

            except Exception as e:
                logger.error(f"Error in interactive loop: {e}")
                self.renderer.print_error("Something went wrong. Your session has been saved.")
                self.session_manager.save_session(self.current_session)
                break

    def send_message(self, message: str) -> str:
        """Send message to coach and get response."""
        try:
            # Build conversation history for context
            messages = []
            if self.current_session.get("message_history"):
                # Include recent exchanges for context (last 10)
                recent_history = self.current_session["message_history"][-10:]
                for exchange in recent_history:
                    messages.append({"role": "user", "content": exchange["user"]})
                    messages.append({"role": "assistant", "content": exchange["coach"]})

            # Add current message
            messages.append({"role": "user", "content": message})

            logger.info(f"Sending message to coach: {message[:50]}...")

            # Invoke the coach
            result = self.coach.invoke({"messages": messages})
            response = result["messages"][-1].content

            logger.info(f"Received response from coach: {response[:50]}...")

            # Save to session history
            self.current_session["message_history"].append(
                {
                    "user": message,
                    "coach": response,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            # Periodically save session (every 5 exchanges)
            if len(self.current_session["message_history"]) % 5 == 0:
                self.session_manager.save_session(self.current_session)

            return response

        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return (
                "I apologize, but I encountered an error processing your request. Please try again."
            )

    def handle_exit(self):
        """Handle session exit with proper cleanup."""
        total_exchanges = len(self.current_session.get("message_history", []))
        self.renderer.print_exit_message(total_exchanges)
        self.session_manager.save_session(self.current_session)

    def generate_and_show_report(self):
        """Generate and display progress report."""
        self.renderer.print_report(self.current_session)

    def export_report_with_progress(self, format: str = "markdown"):
        """Export report with progress bar."""

        def do_export():
            return self.export_report(format=format)

        self.renderer.print_export_progress(do_export)

    def export_report(self, format: str = "markdown") -> bool:
        """Export report to file."""
        try:
            reports_dir = Path.home() / ".ai_life_coach" / "reports"
            reports_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.user_id}_report_{timestamp}.{format}"
            filepath = reports_dir / filename

            report_gen = ReportGenerator(self.current_session)

            if format == "markdown":
                content = report_gen.generate_markdown_report()
            elif format == "json":
                content = report_gen.generate_json_report()
            else:
                raise ValueError(f"Unsupported format: {format}")

            with open(filepath, "w") as f:
                f.write(content)

            logger.info(f"Report exported to: {filepath}")
            return True

        except Exception as e:
            logger.error(f"Failed to export report: {e}")
            return False


# ============================================================================
# ENTRY POINT
# ============================================================================


def main():
    """Main entry point for the TUI."""
    parser = argparse.ArgumentParser(
        description="AI Life Coach - TUI-Enhanced CLI (Gruvbox Dark Hard Theme)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python life_coach_tui.py                    # Start interactive session
  python life_coach_tui.py --user john        # Resume user 'john' session
  python life_coach_tui.py --export markdown  # Export progress report
  python life_coach_tui.py --export json      # Export JSON report

Commands in interactive mode:
  /exit or /quit    - End session and save progress
  /help or /?       - Show available commands
  /report or /r     - Generate progress report
  /clear or /c      - Clear screen
  /dashboard or /d  - Show session statistics
  /export [format]  - Export report (markdown/json)

Theme: Gruvbox Dark Hard
        """,
    )

    parser.add_argument("--user", help="User ID for session (default: 'default')", default=None)

    parser.add_argument(
        "--export",
        choices=["markdown", "json"],
        help="Export progress report in specified format and exit",
    )

    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Create TUI instance
    tui = AILifeCoachTUI(user_id=args.user)
    tui.verbose = args.verbose

    # Initialize system
    if not tui.initialize():
        sys.exit(1)

    # Handle export mode
    if args.export:
        success = tui.export_report(format=args.export)
        if success:
            print(
                f"\nReport exported successfully to: {Path.home() / '.ai_life_coach' / 'reports'}"
            )
        else:
            print("\nError: Failed to export report")
        sys.exit(0 if success else 1)

    # Run interactive session
    try:
        tui.run_interactive_session()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error in TUI: {e}")
        print(f"\nFatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
