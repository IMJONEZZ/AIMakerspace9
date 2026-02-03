"""
Tests for User Game Progress tracking module.
"""

import pytest
from datetime import datetime

from src.user_game_progress import UserGameProgress, PROGRESS_MARKERS


class TestCollectionCreation:
    """Test collection initialization."""

    def test_create_collection(self):
        """Verify that the user_game_progress collection is created."""
        from qdrant_client import QdrantClient

        client = QdrantClient(":memory:")
        tracker = UserGameProgress(client)

        collections = client.get_collections().collections
        collection_names = {c.name for c in collections}

        assert UserGameProgress.COLLECTION_NAME in collection_names


class TestProgressMarkerValidation:
    """Test progress marker validation."""

    def test_valid_progress_markers(self):
        """Verify all defined markers are valid."""
        tracker = UserGameProgress.__new__(UserGameProgress)

        for marker in PROGRESS_MARKERS:
            assert tracker._validate_progress_marker(marker) is True

    def test_invalid_progress_marker(self):
        """Verify invalid markers are rejected."""
        tracker = UserGameProgress.__new__(UserGameProgress)

        assert tracker._validate_progress_marker("invalid") is False
        assert tracker._validate_progress_marker("early") is False
        assert tracker._validate_progress_marker("") is False


class TestUpdateProgress:
    """Test updating user progress."""

    def test_update_progress_with_default(self):
        """Test creating progress with default marker."""
        from qdrant_client import QdrantClient

        client = QdrantClient(":memory:")
        tracker = UserGameProgress(client)

        result = tracker.update_progress("user1", "Elden Ring")
        assert result is True

        progress = tracker.get_progress("user1", "Elden Ring")
        assert progress == "intro/tutorial"

    def test_update_progress_with_marker(self):
        """Test creating progress with specified marker."""
        from qdrant_client import QdrantClient

        client = QdrantClient(":memory:")
        tracker = UserGameProgress(client)

        result = tracker.update_progress(
            "user2", "Zelda: Breath of the Wild", progress_marker="mid_game"
        )
        assert result is True

        progress = tracker.get_progress("user2", "Zelda: Breath of the Wild")
        assert progress == "mid_game"

    def test_update_progress_invalid_marker(self):
        """Test that invalid markers are rejected."""
        from qdrant_client import QdrantClient

        client = QdrantClient(":memory:")
        tracker = UserGameProgress(client)

        result = tracker.update_progress(
            "user3", "Skyrim", progress_marker="invalid_marker"
        )
        assert result is False

    def test_update_existing_progress(self):
        """Test updating an existing progress record."""
        from qdrant_client import QdrantClient

        client = QdrantClient(":memory:")
        tracker = UserGameProgress(client)

        tracker.update_progress("user4", "Hollow Knight", progress_marker="early_game")
        result = tracker.update_progress(
            "user4", "Hollow Knight", progress_marker="late_game"
        )

        assert result is True
        progress = tracker.get_progress("user4", "Hollow Knight")
        assert progress == "late_game"

    def test_update_progress_different_users(self):
        """Test that different users can have progress in the same game."""
        from qdrant_client import QdrantClient

        client = QdrantClient(":memory:")
        tracker = UserGameProgress(client)

        tracker.update_progress("user5", "Dark Souls", progress_marker="early_game")
        tracker.update_progress("user6", "Dark Souls", progress_marker="endgame")

        assert tracker.get_progress("user5", "Dark Souls") == "early_game"
        assert tracker.get_progress("user6", "Dark Souls") == "endgame"

    def test_update_progress_normalization(self):
        """Test that game names are normalized consistently."""
        from qdrant_client import QdrantClient

        client = QdrantClient(":memory:")
        tracker = UserGameProgress(client)

        tracker.update_progress(
            "user7", "  The Witcher 3  ", progress_marker="mid_game"
        )
        result = tracker.update_progress(
            "user7", "THE WITCHER 3", progress_marker="late_game"
        )

        assert result is True
        progress = tracker.get_progress("user7", "the witcher 3")
        assert progress == "late_game"


class TestGetProgress:
    """Test retrieving user progress."""

    def test_get_progress_nonexistent(self):
        """Test getting progress for non-existent record returns None."""
        from qdrant_client import QdrantClient

        client = QdrantClient(":memory:")
        tracker = UserGameProgress(client)

        progress = tracker.get_progress("nonexistent_user", "Nonexistent Game")
        assert progress is None

    def test_get_progress_existing(self):
        """Test getting existing progress record."""
        from qdrant_client import QdrantClient

        client = QdrantClient(":memory:")
        tracker = UserGameProgress(client)

        tracker.update_progress("user8", "God of War", progress_marker="endgame")
        progress = tracker.get_progress("user8", "God of War")

        assert progress == "endgame"

    def test_get_progress_case_insensitive(self):
        """Test that game name lookup is case-insensitive."""
        from qdrant_client import QdrantClient

        client = QdrantClient(":memory:")
        tracker = UserGameProgress(client)

        tracker.update_progress("user9", "Cyberpunk 2077", progress_marker="mid_game")

        progress1 = tracker.get_progress("user9", "cyberpunk 2077")
        progress2 = tracker.get_progress("user9", "CYBERPUNK 2077")

        assert progress1 == "mid_game"
        assert progress2 == "mid_game"


class TestGetAllUserProgress:
    """Test retrieving all progress for a user."""

    def test_get_all_empty(self):
        """Test getting all progress when no games exist."""
        from qdrant_client import QdrantClient

        client = QdrantClient(":memory:")
        tracker = UserGameProgress(client)

        progress_list = tracker.get_all_user_progress("user10")
        assert progress_list == []

    def test_get_all_multiple_games(self):
        """Test getting all progress for a user with multiple games."""
        from qdrant_client import QdrantClient

        client = QdrantClient(":memory:")
        tracker = UserGameProgress(client)

        tracker.update_progress("user11", "Elden Ring", progress_marker="early_game")
        tracker.update_progress("user11", "Zelda: BotW", progress_marker="mid_game")
        tracker.update_progress("user11", "Hollow Knight", progress_marker="endgame")

        progress_list = tracker.get_all_user_progress("user11")
        game_names = {g["game_name"] for g in progress_list}

        assert len(progress_list) == 3
        assert "Elden Ring" in game_names
        assert "Zelda: BotW" in game_names
        assert "Hollow Knight" in game_names

    def test_get_all_isolated_by_user(self):
        """Test that get_all is isolated to the specified user."""
        from qdrant_client import QdrantClient

        client = QdrantClient(":memory:")
        tracker = UserGameProgress(client)

        tracker.update_progress("user12", "Elden Ring")
        tracker.update_progress("user13", "Zelda: BotW")

        user12_progress = tracker.get_all_user_progress("user12")
        user13_progress = tracker.get_all_user_progress("user13")

        assert len(user12_progress) == 1
        assert user12_progress[0]["game_name"] == "Elden Ring"
        assert len(user13_progress) == 1
        assert user13_progress[0]["game_name"] == "Zelda: BotW"


class TestRemoveProgress:
    """Test removing user progress."""

    def test_remove_existing(self):
        """Test removing an existing progress record."""
        from qdrant_client import QdrantClient

        client = QdrantClient(":memory:")
        tracker = UserGameProgress(client)

        tracker.update_progress("user14", "Sekiro")
        result = tracker.remove_progress("user14", "Sekiro")

        assert result is True
        progress = tracker.get_progress("user14", "Sekiro")
        assert progress is None

    def test_remove_nonexistent(self):
        """Test removing a non-existent record."""
        from qdrant_client import QdrantClient

        client = QdrantClient(":memory:")
        tracker = UserGameProgress(client)

        result = tracker.remove_progress("nonexistent_user", "Nonexistent Game")
        assert result is False

    def test_remove_one_of_many(self):
        """Test removing one game doesn't affect others."""
        from qdrant_client import QdrantClient

        client = QdrantClient(":memory:")
        tracker = UserGameProgress(client)

        tracker.update_progress("user15", "Elden Ring")
        tracker.update_progress("user15", "Sekiro")

        result = tracker.remove_progress("user15", "Elden Ring")
        assert result is True

        elden_ring_progress = tracker.get_progress("user15", "Elden Ring")
        sekiro_progress = tracker.get_progress("user15", "Sekiro")

        assert elden_ring_progress is None
        assert sekiro_progress == "intro/tutorial"


class TestProgressMarkers:
    """Test progress marker constants."""

    def test_progress_markers_list(self):
        """Verify the list of defined progress markers."""
        expected = [
            "intro/tutorial",
            "early_game",
            "mid_game",
            "late_game",
            "endgame",
            "post_game",
        ]
        assert PROGRESS_MARKERS == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
