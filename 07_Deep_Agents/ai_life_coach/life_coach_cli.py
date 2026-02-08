#!/usr/bin/env python3
"""
AI Life Coach - Production CLI Interface

Real interactive coaching system with persistent sessions.

Usage:
    python ai_life_coach.py                    # Start interactive session
    python ai_life_coach.py --user <id>        # Resume previous session
    python ai_life_coach.py --export report    # Generate progress report
    python ai_life_coach.py --help             # Show usage
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

# Configure logging
log_dir = Path.home() / ".ai_life_coach"
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "cli.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


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


class AILifeCoachCLI:
    """Production CLI for AI Life Coach."""

    def __init__(self, user_id: str = None):
        self.user_id = user_id or "default"
        self.coach = None
        self.session_manager = SessionManager(self.user_id)
        self.current_session = None
        self.verbose = False

    def initialize(self):
        """Initialize the coach system."""
        try:
            logger.info(f"Initializing AI Life Coach for user: {self.user_id}")
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
            print(f"Error: Failed to initialize system - {e}")
            return False

    def run_interactive_session(self):
        """Main interactive loop."""
        print("\n" + "=" * 60)
        print("AI Life Coach")
        print("=" * 60)
        print(f"User: {self.user_id}")
        if self.current_session.get("created_at"):
            created = datetime.fromisoformat(self.current_session["created_at"])
            print(f"Session started: {created.strftime('%Y-%m-%d')}")
        if self.current_session.get("message_history"):
            print(f"Previous exchanges: {len(self.current_session['message_history'])}")
        print("\nCommands:")
        print("  exit/quit   - End session and save progress")
        print("  help        - Show available commands")
        print("  report      - Generate progress report")
        print("  clear       - Clear screen")
        print("=" * 60 + "\n")

        # Check if this is a new user
        if not self.current_session.get("message_history"):
            print("Welcome! This appears to be your first session.")
            print("Feel free to share anything about yourself - your goals, challenges,")
            print("or what you'd like help with. I'm here to guide you across all areas of life.\n")

        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.lower() in ["exit", "quit"]:
                    self.handle_exit()
                    break

                if user_input.lower() == "help":
                    self.show_help()
                    continue

                if user_input.lower() == "report":
                    self.generate_and_show_report()
                    continue

                if user_input.lower() == "clear":
                    print("\033[H\033[J", end="")  # ANSI clear screen
                    continue

                # Send message to coach
                response = self.send_message(user_input)
                print(f"\nCoach: {response}\n")

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
                print(f"\nSorry, something went wrong. Your session has been saved.\n")
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
        print("\n" + "=" * 60)
        total_exchanges = len(self.current_session.get("message_history", []))
        print(f"Session complete. Total exchanges: {total_exchanges}")
        print("Progress saved. Come back anytime!")
        print("=" * 60 + "\n")

        self.session_manager.save_session(self.current_session)

    def show_help(self):
        """Display help information."""
        print("\n" + "=" * 60)
        print("AI Life Coach - Help")
        print("=" * 60)
        print("\nAvailable Commands:")
        print("  exit/quit   - End session and save progress")
        print("  help        - Show this help message")
        print("  report      - Generate and display progress report")
        print("  clear       - Clear the screen")
        print("\nHow to use:")
        print("- Simply type your question or share what's on your mind")
        print("- I can help with career, relationships, finance, wellness")
        print("- All conversations are saved and can be resumed later")
        print("\nTips:")
        print("- Be specific about what you'd like help with")
        print("- Feel free to ask follow-up questions")
        print("- I remember our previous conversations")
        print("=" * 60 + "\n")

    def generate_and_show_report(self):
        """Generate and display progress report."""
        print("\n" + "=" * 60)
        print("Generating Progress Report...")
        print("=" * 60 + "\n")

        report_gen = ReportGenerator(self.current_session)
        markdown_report = report_gen.generate_markdown_report()

        print(markdown_report)

    def export_report(self, format: str = "markdown"):
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

            print(f"\nReport exported to: {filepath}")
            return True

        except Exception as e:
            logger.error(f"Failed to export report: {e}")
            print(f"\nError: Failed to export report - {e}")
            return False


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="AI Life Coach - Production CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ai_life_coach.py                    # Start interactive session
  python ai_life_coach.py --user john        # Resume user 'john' session
  python ai_life_coach.py --export markdown  # Export progress report
  python ai_life_coach.py --export json      # Export JSON report

Commands in interactive mode:
  exit/quit   - End session and save progress
  help        - Show available commands
  report      - Generate progress report
  clear       - Clear screen
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

    # Create CLI instance
    cli = AILifeCoachCLI(user_id=args.user)
    cli.verbose = args.verbose

    # Initialize system
    if not cli.initialize():
        sys.exit(1)

    # Handle export mode
    if args.export:
        cli.export_report(format=args.export)
        sys.exit(0)

    # Run interactive session
    try:
        cli.run_interactive_session()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error in CLI: {e}")
        print(f"\nFatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
