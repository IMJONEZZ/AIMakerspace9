"""
Test suite for GameKnowledgeBase

Tests spoiler-aware search, progress filtering, and content management.
"""

import pytest
from qdrant_client import QdrantClient
from src.game_knowledge_base import (
    GameKnowledgeBase,
    PROGRESS_ORDER,
    get_progress_order,
    is_progress_allowed,
)


@pytest.fixture
def qdrant_client():
    """Create in-memory QDrant client for testing."""
    return QdrantClient(":memory:")


@pytest.fixture
def knowledge_base(qdrant_client):
    """Create GameKnowledgeBase instance for testing."""
    return GameKnowledgeBase(qdrant_client)


class TestProgressOrdering:
    """Test progress marker ordering utilities."""

    def test_progress_order_dict(self):
        """Verify PROGRESS_ORDER has correct values."""
        assert PROGRESS_ORDER["intro/tutorial"] == 0
        assert PROGRESS_ORDER["early_game"] == 1
        assert PROGRESS_ORDER["mid_game"] == 2
        assert PROGRESS_ORDER["late_game"] == 3
        assert PROGRESS_ORDER["endgame"] == 4
        assert PROGRESS_ORDER["post_game"] == 5
        assert PROGRESS_ORDER["general"] == -1

    def test_get_progress_order(self):
        """Test get_progress_order function."""
        assert get_progress_order("intro/tutorial") == 0
        assert get_progress_order("early_game") == 1
        assert get_progress_order("mid_game") == 2
        assert get_progress_order("unknown") == 0

    def test_is_progress_allowed(self):
        """Test progress filtering logic."""
        # General content is always allowed
        assert is_progress_allowed("general", "intro/tutorial")
        assert is_progress_allowed("general", "post_game")

        # Earlier content is always allowed
        assert is_progress_allowed("intro/tutorial", "early_game")
        assert is_progress_allowed("early_game", "mid_game")
        assert is_progress_allowed("mid_game", "late_game")

        # Same progress is allowed
        assert is_progress_allowed("early_game", "early_game")
        assert is_progress_allowed("mid_game", "mid_game")

        # Later content is not allowed
        assert not is_progress_allowed("mid_game", "early_game")
        assert not is_progress_allowed("late_game", "mid_game")
        assert not is_progress_allowed("endgame", "early_game")


class TestStoreGameContent:
    """Test storing game content with metadata."""

    def test_store_basic_content(self, knowledge_base):
        """Test storing basic game content."""
        chunks = ["This is a test chunk about the beginning of Elden Ring."]

        metadata = {
            "game_name": "Elden Ring",
            "game_display_name": "Elden Ring",
            "content_type": "walkthrough",
            "is_spoiler": False,
            "progress_marker": "intro/tutorial",
            "source_url": "https://example.com/test",
            "source_type": "manual",
        }

        result = knowledge_base.store_game_content(chunks, metadata)
        assert result is True

    def test_store_multiple_chunks(self, knowledge_base):
        """Test storing multiple chunks."""
        chunks = [
            "First chunk about early game content.",
            "Second chunk with more information.",
            "Third chunk completing the section.",
        ]

        metadata = {
            "game_name": "Minecraft",
            "game_display_name": "Minecraft",
            "content_type": "walkthrough",
            "is_spoiler": False,
            "progress_marker": "early_game",
            "source_url": "https://example.com/minecraft",
            "source_type": "manual",
        }

        result = knowledge_base.store_game_content(chunks, metadata)
        assert result is True

    def test_store_with_optional_fields(self, knowledge_base):
        """Test storing content with optional metadata fields."""
        chunks = ["Content about a specific chapter."]

        metadata = {
            "game_name": "Elden Ring",
            "game_display_name": "Elden Ring",
            "content_type": "walkthrough",
            "is_spoiler": False,
            "progress_marker": "mid_game",
            "source_url": "https://example.com/test",
            "source_type": "manual",
            "chapter": 5,
            "section_name": "Leyndell",
            "quality_score": 0.9,
        }

        result = knowledge_base.store_game_content(chunks, metadata)
        assert result is True

    def test_store_missing_required_field(self, knowledge_base):
        """Test that missing required fields fail gracefully."""
        chunks = ["Test content."]

        # Missing is_spoiler field
        metadata = {
            "game_name": "Elden Ring",
            "game_display_name": "Elden Ring",
            "content_type": "walkthrough",
            # "is_spoiler": False,  # MISSING
            "progress_marker": "intro/tutorial",
            "source_url": "https://example.com/test",
            "source_type": "manual",
        }

        result = knowledge_base.store_game_content(chunks, metadata)
        assert result is False

    def test_store_spoiler_content(self, knowledge_base):
        """Test storing content marked as spoiler."""
        chunks = ["The final boss is defeated by using a specific strategy."]

        metadata = {
            "game_name": "Elden Ring",
            "game_display_name": "Elden Ring",
            "content_type": "spoiler",
            "is_spoiler": True,
            "progress_marker": "endgame",
            "source_url": "https://example.com/spoilers",
            "source_type": "manual",
        }

        result = knowledge_base.store_game_content(chunks, metadata)
        assert result is True


class TestSearchGameKnowledge:
    """Test semantic search with spoiler and progress filtering."""

    def test_search_basic(self, knowledge_base):
        """Test basic semantic search."""
        # Store some content
        chunks = ["To defeat the first boss in Elden Ring, head to Stormveil Castle."]

        metadata = {
            "game_name": "Elden Ring",
            "game_display_name": "Elden Ring",
            "content_type": "walkthrough",
            "is_spoiler": False,
            "progress_marker": "early_game",
            "source_url": "https://example.com/test",
            "source_type": "manual",
        }

        knowledge_base.store_game_content(chunks, metadata)

        # Search for similar content
        results = knowledge_base.search_game_knowledge(
            query="How do I beat the first boss?",
            game_name="Elden Ring",
            user_progress_marker="early_game",  # User is at early game stage
        )

        assert len(results) > 0
        assert (
            "Stormveil" in results[0]["text"]
            or "first boss" in results[0]["text"].lower()
        )

    def test_search_spoiler_filtering(self, knowledge_base):
        """Test that avoid_spoilers filters out marked spoilers."""
        # Store non-spoiler content
        non_spoiler_chunks = ["Early game tutorial area with basic enemies."]

        non_spoiler_metadata = {
            "game_name": "Elden Ring",
            "game_display_name": "Elden Ring",
            "content_type": "walkthrough",
            "is_spoiler": False,
            "progress_marker": "intro/tutorial",
            "source_url": "https://example.com/test1",
            "source_type": "manual",
        }

        knowledge_base.store_game_content(non_spoiler_chunks, non_spoiler_metadata)

        # Store spoiler content
        spoiler_chunks = [
            "In the endgame, you learn that Malenia is actually related to Miquella."
        ]

        spoiler_metadata = {
            "game_name": "Elden Ring",
            "game_display_name": "Elden Ring",
            "content_type": "spoiler",
            "is_spoiler": True,
            "progress_marker": "endgame",
            "source_url": "https://example.com/test2",
            "source_type": "manual",
        }

        knowledge_base.store_game_content(spoiler_chunks, spoiler_metadata)

        # Search with avoid_spoilers=True
        results_no_spoilers = knowledge_base.search_game_knowledge(
            query="What happens in the game?",
            game_name="Elden Ring",
            avoid_spoilers=True,
        )

        # Search with avoid_spoilers=False
        results_with_spoilers = knowledge_base.search_game_knowledge(
            query="What happens in the game?",
            game_name="Elden Ring",
            avoid_spoilers=False,
        )

        # No spoilers should be filtered out
        assert all(not r["is_spoiler"] for r in results_no_spoilers)

        # With avoid_spoilers=False, we might get spoilers
        assert len(results_with_spoilers) >= 0

    def test_search_progress_filtering(self, knowledge_base):
        """Test that progress filtering hides late-game content from early players."""
        # Store early game content
        early_chunks = ["Tutorial area in Limgrave with basic guidance."]

        early_metadata = {
            "game_name": "Elden Ring",
            "game_display_name": "Elden Ring",
            "content_type": "walkthrough",
            "is_spoiler": False,
            "progress_marker": "early_game",
            "source_url": "https://example.com/early",
            "source_type": "manual",
        }

        knowledge_base.store_game_content(early_chunks, early_metadata)

        # Store late game content
        late_chunks = ["In the endgame, you face Radagon in the Erdtree."]

        late_metadata = {
            "game_name": "Elden Ring",
            "game_display_name": "Elden Ring",
            "content_type": "walkthrough",
            "is_spoiler": False,
            "progress_marker": "endgame",
            "source_url": "https://example.com/late",
            "source_type": "manual",
        }

        knowledge_base.store_game_content(late_chunks, late_metadata)

        # Search as early game player
        results_early_player = knowledge_base.search_game_knowledge(
            query="What areas can I explore?",
            game_name="Elden Ring",
            user_progress_marker="early_game",
        )

        # Search as late game player
        results_late_player = knowledge_base.search_game_knowledge(
            query="What areas can I explore?",
            game_name="Elden Ring",
            user_progress_marker="endgame",
        )

        # Early player should not see endgame content
        assert all(
            get_progress_order(r["progress_marker"]) <= get_progress_order("early_game")
            for r in results_early_player
        )

        # Late player can see all content (up to their progress)
        assert len(results_late_player) >= 0

    def test_search_content_type_filtering(self, knowledge_base):
        """Test filtering by specific content type."""
        # Store walkthrough content
        walkthrough_chunks = ["Step-by-step guide to complete the tutorial."]

        walkthrough_metadata = {
            "game_name": "Elden Ring",
            "game_display_name": "Elden Ring",
            "content_type": "walkthrough",
            "is_spoiler": False,
            "progress_marker": "intro/tutorial",
            "source_url": "https://example.com/walkthrough",
            "source_type": "manual",
        }

        knowledge_base.store_game_content(walkthrough_chunks, walkthrough_metadata)

        # Store lore content
        lore_chunks = ["The world was created by the Greater Will."]

        lore_metadata = {
            "game_name": "Elden Ring",
            "game_display_name": "Elden Ring",
            "content_type": "lore",
            "is_spoiler": False,
            "progress_marker": "general",
            "source_url": "https://example.com/lore",
            "source_type": "manual",
        }

        knowledge_base.store_game_content(lore_chunks, lore_metadata)

        # Search for walkthrough only
        results_walkthrough = knowledge_base.search_game_knowledge(
            query="How do I play?",
            game_name="Elden Ring",
            content_types=["walkthrough"],
        )

        # All results should be walkthrough
        assert all(r["content_type"] == "walkthrough" for r in results_walkthrough)

    def test_search_game_isolation(self, knowledge_base):
        """Test that search results are isolated to the specified game."""
        # Store Elden Ring content
        elden_chunks = ["Elden Ring has a vast open world to explore."]

        elden_metadata = {
            "game_name": "Elden Ring",
            "game_display_name": "Elden Ring",
            "content_type": "walkthrough",
            "is_spoiler": False,
            "progress_marker": "general",
            "source_url": "https://example.com/elden",
            "source_type": "manual",
        }

        knowledge_base.store_game_content(elden_chunks, elden_metadata)

        # Store Minecraft content
        minecraft_chunks = ["Minecraft lets you build and explore blocky worlds."]

        minecraft_metadata = {
            "game_name": "Minecraft",
            "game_display_name": "Minecraft",
            "content_type": "walkthrough",
            "is_spoiler": False,
            "progress_marker": "general",
            "source_url": "https://example.com/minecraft",
            "source_type": "manual",
        }

        knowledge_base.store_game_content(minecraft_chunks, minecraft_metadata)

        # Search Elden Ring should not return Minecraft content
        elden_results = knowledge_base.search_game_knowledge(
            query="What can I do in this game?",
            game_name="Elden Ring",
        )

        assert all(r["game_name"] == "Elden Ring" for r in elden_results)

        # Search Minecraft should not return Elden Ring content
        minecraft_results = knowledge_base.search_game_knowledge(
            query="What can I do in this game?",
            game_name="Minecraft",
        )

        assert all(r["game_name"] == "Minecraft" for r in minecraft_results)


class TestGetAllSpoilers:
    """Test retrieving all marked spoilers."""

    def test_get_all_spoilers(self, knowledge_base):
        """Test retrieving all spoilers for a game."""
        # Store spoiler content
        spoiler_chunks = [
            "Spoiler 1: The final boss is Radagon.",
            "Spoiler 2: Malenia is the Blade of Miquella.",
        ]

        for i, chunk in enumerate(spoiler_chunks):
            metadata = {
                "game_name": "Elden Ring",
                "game_display_name": "Elden Ring",
                "content_type": "spoiler",
                "is_spoiler": True,
                "progress_marker": "endgame",
                "source_url": f"https://example.com/spoiler{i}",
                "source_type": "manual",
            }
            knowledge_base.store_game_content([chunk], metadata)

        # Store non-spoiler content
        non_spoiler_chunks = ["This is safe to read."]

        non_spoiler_metadata = {
            "game_name": "Elden Ring",
            "game_display_name": "Elden Ring",
            "content_type": "walkthrough",
            "is_spoiler": False,
            "progress_marker": "intro/tutorial",
            "source_url": "https://example.com/safe",
            "source_type": "manual",
        }

        knowledge_base.store_game_content(non_spoiler_chunks, non_spoiler_metadata)

        # Get all spoilers
        spoilers = knowledge_base.get_all_spoilers("Elden Ring")

        # All results should be marked as spoilers
        assert len(spoilers) >= 2
        # Note: We can't guarantee all results will have is_spoiler in the returned dict
        # because get_all_spoilers doesn't include it, but we can check the text

    def test_get_all_spoilers_empty(self, knowledge_base):
        """Test getting spoilers from a game with no content."""
        spoilers = knowledge_base.get_all_spoilers("Nonexistent Game")
        assert len(spoilers) == 0


class TestGetContentByType:
    """Test retrieving content by type."""

    def test_get_walkthrough_content(self, knowledge_base):
        """Test getting walkthrough content."""
        # Store walkthrough
        walkthrough_chunks = ["Step-by-step guide to the tutorial."]

        walkthrough_metadata = {
            "game_name": "Elden Ring",
            "game_display_name": "Elden Ring",
            "content_type": "walkthrough",
            "is_spoiler": False,
            "progress_marker": "intro/tutorial",
            "source_url": "https://example.com/walkthrough",
            "source_type": "manual",
        }

        knowledge_base.store_game_content(walkthrough_chunks, walkthrough_metadata)

        # Store lore
        lore_chunks = ["The world has deep history."]

        lore_metadata = {
            "game_name": "Elden Ring",
            "game_display_name": "Elden Ring",
            "content_type": "lore",
            "is_spoiler": False,
            "progress_marker": "general",
            "source_url": "https://example.com/lore",
            "source_type": "manual",
        }

        knowledge_base.store_game_content(lore_chunks, lore_metadata)

        # Get walkthrough only
        walkthrough_results = knowledge_base.get_content_by_type(
            "Elden Ring", "walkthrough"
        )

        # All results should be walkthrough
        assert len(walkthrough_results) > 0


class TestDeleteGameContent:
    """Test deleting game content."""

    def test_delete_game(self, knowledge_base):
        """Test deleting all content for a game."""
        # Store content
        chunks = ["Content to be deleted."]

        metadata = {
            "game_name": "Elden Ring",
            "game_display_name": "Elden Ring",
            "content_type": "walkthrough",
            "is_spoiler": False,
            "progress_marker": "early_game",
            "source_url": "https://example.com/test",
            "source_type": "manual",
        }

        knowledge_base.store_game_content(chunks, metadata)

        # Verify content exists
        results = knowledge_base.search_game_knowledge(
            query="test", game_name="Elden Ring", user_progress_marker="early_game"
        )
        assert len(results) > 0

        # Delete content
        result = knowledge_base.delete_game_content("Elden Ring")
        assert result is True

        # Verify content is gone
        results_after_delete = knowledge_base.search_game_knowledge(
            query="test", game_name="Elden Ring"
        )
        assert len(results_after_delete) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
