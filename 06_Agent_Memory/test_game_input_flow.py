"""
Test suite for GameInputFlow

Tests the game selection flow and user game management.
"""

import pytest
from src.game_input_flow import GameInputFlow, create_game_input_flow


class TestGameInputFlow:
    """Test the basic functionality of GameInputFlow."""

    def test_create_game_input_flow(self):
        """Test creating a GameInputFlow instance."""
        flow = create_game_input_flow()
        assert isinstance(flow, GameInputFlow)
        assert len(flow.get_all_users()) == 0

    def test_prompt_for_game(self):
        """Test the game prompt generation."""
        flow = GameInputFlow()
        prompt = flow.prompt_for_game()

        assert "Welcome!" in prompt
        assert "game" in prompt.lower()
        assert "Elden Ring" in prompt

    def test_set_and_get_user_game(self):
        """Test setting and getting a user's game."""
        flow = GameInputFlow()
        user_id = "user_123"

        # Set the game
        result = flow.set_user_game(user_id, "elden_ring", "Elden Ring")
        assert result is True

        # Get the game
        game_info = flow.get_user_game(user_id)
        assert game_info is not None
        assert game_info["game_name"] == "elden_ring"
        assert game_info["display_name"] == "Elden Ring"
        assert "selected_at" in game_info

    def test_set_user_game_without_display_name(self):
        """Test setting a user's game without providing display name."""
        flow = GameInputFlow()
        user_id = "user_456"

        # Set the game without display name
        result = flow.set_user_game(user_id, "minecraft")
        assert result is True

        # Get the game - display name should be auto-generated
        game_info = flow.get_user_game(user_id)
        assert game_info is not None
        assert game_info["game_name"] == "minecraft"
        assert game_info["display_name"] == "Minecraft"

    def test_normalize_game_name(self):
        """Test game name normalization."""
        flow = GameInputFlow()

        assert flow.normalize_game_name("Elden Ring") == "elden_ring"
        assert flow.normalize_game_name("God of War Ragnarök") == "god_of_war_ragnarök"
        assert flow.normalize_game_name("  Minecraft  ") == "minecraft"

    def test_has_user_game(self):
        """Test checking if a user has a game selected."""
        flow = GameInputFlow()
        user_id = "user_789"

        # Initially should not have a game
        assert flow.has_user_game(user_id) is False

        # Set the game
        flow.set_user_game(user_id, "elden_ring")

        # Now should have a game
        assert flow.has_user_game(user_id) is True

    def test_clear_user_game(self):
        """Test clearing a user's game."""
        flow = GameInputFlow()
        user_id = "user_999"

        # Set the game
        flow.set_user_game(user_id, "elden_ring")
        assert flow.has_user_game(user_id) is True

        # Clear the game
        result = flow.clear_user_game(user_id)
        assert result is True

        # Should no longer have a game
        assert flow.has_user_game(user_id) is False

    def test_clear_nonexistent_user(self):
        """Test clearing a game for a user that doesn't exist."""
        flow = GameInputFlow()
        result = flow.clear_user_game("nonexistent_user")
        assert result is False

    def test_get_nonexistent_user(self):
        """Test getting game for a user that doesn't exist."""
        flow = GameInputFlow()
        game_info = flow.get_user_game("nonexistent_user")
        assert game_info is None

    def test_multiple_users(self):
        """Test managing games for multiple users."""
        flow = GameInputFlow()

        # Set up multiple users
        flow.set_user_game("user_1", "elden_ring")
        flow.set_user_game("user_2", "minecraft")
        flow.set_user_game("user_3", "god_of_war")

        # Check all users are tracked
        assert flow.get_user_count() == 3
        assert len(flow.get_all_users()) == 3

        # Verify each game
        assert flow.get_user_game("user_1")["game_name"] == "elden_ring"
        assert flow.get_user_game("user_2")["game_name"] == "minecraft"
        assert flow.get_user_game("user_3")["game_name"] == "god_of_war"

    def test_get_all_users(self):
        """Test getting list of all users."""
        flow = GameInputFlow()

        # Initially empty
        assert len(flow.get_all_users()) == 0

        # Add users
        flow.set_user_game("user_1", "elden_ring")
        flow.set_user_game("user_2", "minecraft")

        # Get all users
        users = flow.get_all_users()
        assert len(users) == 2
        assert "user_1" in users
        assert "user_2" in users

    def test_get_user_count(self):
        """Test getting user count."""
        flow = GameInputFlow()

        # Initially 0
        assert flow.get_user_count() == 0

        # Add users one by one
        flow.set_user_game("user_1", "elden_ring")
        assert flow.get_user_count() == 1

        flow.set_user_game("user_2", "minecraft")
        assert flow.get_user_count() == 2

        # Remove a user
        flow.clear_user_game("user_1")
        assert flow.get_user_count() == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
