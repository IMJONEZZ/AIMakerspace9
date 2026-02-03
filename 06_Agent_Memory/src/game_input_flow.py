"""
Game Input Flow Module

Handles the initial conversation flow where users specify which game they're asking about.
This happens BEFORE any routing or agent invocation.

The selected game name is stored and passed to:
- Game Story Research Agent (for knowledge base population)
- All specialist agents (for their queries)

This eliminates the need for game detection in the router.
"""

from typing import Optional, Dict
from datetime import datetime


class GameInputFlow:
    """
    Manages the game selection flow for users.

    Stores which game each user is currently asking about and provides
    methods to prompt for game selection when needed.
    """

    def __init__(self):
        """Initialize the game input flow manager."""
        # Store user's selected games: {user_id: {"game_name": str, "display_name": str, "selected_at": str}}
        self.user_games: Dict[str, Dict[str, str]] = {}

    def prompt_for_game(self) -> str:
        """
        Generate the initial prompt to ask user which game they're asking about.

        Returns:
            Prompt string to display to the user
        """
        return (
            "Welcome! Before I can help you, please let me know which video game "
            "you're asking about. For example: 'Elden Ring', 'Minecraft', 'God of War', etc."
        )

    def set_user_game(
        self, user_id: str, game_name: str, display_name: Optional[str] = None
    ) -> bool:
        """
        Set the game for a user.

        Args:
            user_id: User identifier
            game_name: Normalized game name (lowercase with underscores)
            display_name: Display name for the game (e.g., "Elden Ring")

        Returns:
            True if successfully set, False otherwise
        """
        self.user_games[user_id] = {
            "game_name": game_name,
            "display_name": display_name or game_name.replace("_", " ").title(),
            "selected_at": datetime.now().isoformat(),
        }
        return True

    def get_user_game(self, user_id: str) -> Optional[Dict[str, str]]:
        """
        Get the currently selected game for a user.

        Args:
            user_id: User identifier

        Returns:
            Dictionary with game_name, display_name, and selected_at, or None if no game set
        """
        return self.user_games.get(user_id)

    def clear_user_game(self, user_id: str) -> bool:
        """
        Clear the selected game for a user.

        Args:
            user_id: User identifier

        Returns:
            True if successfully cleared, False otherwise
        """
        if user_id in self.user_games:
            del self.user_games[user_id]
            return True
        return False

    def has_user_game(self, user_id: str) -> bool:
        """
        Check if a user has selected a game.

        Args:
            user_id: User identifier

        Returns:
            True if the user has a game selected, False otherwise
        """
        return user_id in self.user_games

    def normalize_game_name(self, game_name: str) -> str:
        """
        Normalize a game name for consistent storage.

        Args:
            game_name: Game name to normalize

        Returns:
            Normalized game name (lowercase with underscores)
        """
        return game_name.lower().strip().replace(" ", "_")

    def get_all_users(self) -> list[str]:
        """
        Get a list of all user IDs that have selected games.

        Returns:
            List of user IDs
        """
        return list(self.user_games.keys())

    def get_user_count(self) -> int:
        """
        Get the total number of users with selected games.

        Returns:
            Number of users
        """
        return len(self.user_games)


def create_game_input_flow() -> GameInputFlow:
    """
    Factory function to create a GameInputFlow instance.

    Returns:
        New GameInputFlow instance
    """
    return GameInputFlow()


__all__ = [
    "GameInputFlow",
    "create_game_input_flow",
]
