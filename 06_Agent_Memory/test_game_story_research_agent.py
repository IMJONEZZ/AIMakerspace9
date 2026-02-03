"""
Test suite for GameStoryResearchAgent

Tests the research agent's ability to search, fetch, and store game content.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.game_story_research_agent import (
    GameStoryResearchAgent,
    create_game_story_research_agent,
)


@pytest.fixture
def research_agent():
    """Create a GameStoryResearchAgent instance for testing."""
    return create_game_story_research_agent()


class TestInitialization:
    """Test agent initialization."""

    def test_create_agent(self, research_agent):
        """Test creating a research agent."""
        assert isinstance(research_agent, GameStoryResearchAgent)
        assert research_agent.game_tracker is not None
        assert research_agent.knowledge_base is not None


class TestProgressMarkerClassification:
    """Test progress marker classification logic."""

    def test_classify_intro_tutorial(self):
        """Test classifying intro/tutorial content."""
        agent = GameStoryResearchAgent()

        text = "Welcome to the tutorial area. Learn the basics here."
        marker = agent._classify_progress_marker(text)
        assert marker == "intro/tutorial"

    def test_classify_early_game(self):
        """Test classifying early game content."""
        agent = GameStoryResearchAgent()

        text = "This is for the early game. First boss strategies."
        marker = agent._classify_progress_marker(text)
        assert marker == "early_game"

    def test_classify_mid_game(self):
        """Test classifying mid game content."""
        agent = GameStoryResearchAgent()

        text = "Mid game progression and halfway point strategies."
        marker = agent._classify_progress_marker(text)
        assert marker == "mid_game"

    def test_classify_late_game(self):
        """Test classifying late game content."""
        agent = GameStoryResearchAgent()

        text = "Late game strategies and final challenges."
        marker = agent._classify_progress_marker(text)
        assert marker == "late_game"

    def test_classify_endgame(self):
        """Test classifying endgame content."""
        agent = GameStoryResearchAgent()

        text = "Endgame guide and final boss strategies."
        marker = agent._classify_progress_marker(text)
        assert marker == "endgame"

    def test_classify_post_game(self):
        """Test classifying post-game content."""
        agent = GameStoryResearchAgent()

        text = "Post game secrets and New Game+ content."
        marker = agent._classify_progress_marker(text)
        assert marker == "post_game"

    def test_classify_general(self):
        """Test classifying general content."""
        agent = GameStoryResearchAgent()

        text = "This is some general information about the game."
        marker = agent._classify_progress_marker(text)
        assert marker == "general"


class TestContentTypeClassification:
    """Test content type classification logic."""

    def test_classify_spoiler(self):
        """Test classifying spoiler content."""
        agent = GameStoryResearchAgent()

        query = "elden ring spoilers ending"
        content_type = agent._classify_content_type(query)
        assert content_type == "spoiler"

    def test_classify_lore(self):
        """Test classifying lore content."""
        agent = GameStoryResearchAgent()

        query = "elden ring lore story background"
        content_type = agent._classify_content_type(query)
        assert content_type == "lore"

    def test_classify_walkthrough(self):
        """Test classifying walkthrough content."""
        agent = GameStoryResearchAgent()

        query = "elden ring walkthrough guide"
        content_type = agent._classify_content_type(query)
        assert content_type == "walkthrough"

    def test_classify_tips(self):
        """Test classifying tips content."""
        agent = GameStoryResearchAgent()

        query = "elden ring strategies"
        content_type = agent._classify_content_type(query)
        assert content_type == "tips"


class TestSpoilerDetection:
    """Test spoiler detection logic."""

    def test_spoiler_type_is_spoiler(self):
        """Test that spoiler content type is marked as spoiler."""
        agent = GameStoryResearchAgent()

        text = "Some regular content"
        is_spoiler = agent._is_spoiler_content("spoiler", text)
        assert is_spoiler is True

    def test_walkthrough_with_ending_keyword(self):
        """Test detecting spoilers in walkthrough content."""
        agent = GameStoryResearchAgent()

        text = "This is about the ending of the game"
        is_spoiler = agent._is_spoiler_content("walkthrough", text)
        assert is_spoiler is True

    def test_walkthrough_without_keywords(self):
        """Test walkthrough without spoiler keywords."""
        agent = GameStoryResearchAgent()

        text = "This is about gameplay mechanics and controls"
        is_spoiler = agent._is_spoiler_content("walkthrough", text)
        assert is_spoiler is False

    def test_lore_with_plot_twist(self):
        """Test detecting plot twist in lore."""
        agent = GameStoryResearchAgent()

        text = "The story has a major plot twist involving the main character"
        is_spoiler = agent._is_spoiler_content("lore", text)
        assert is_spoiler is True

    def test_lore_without_keywords(self):
        """Test lore without spoiler keywords."""
        agent = GameStoryResearchAgent()

        text = "The world was created by ancient gods"
        is_spoiler = agent._is_spoiler_content("lore", text)
        assert is_spoiler is False


class TestTextChunking:
    """Test text chunking functionality."""

    def test_chunk_long_text(self, research_agent):
        """Test chunking long text."""
        # Create a long text (1000 chars)
        text = "A" * 1000

        chunks = research_agent._chunk_text(text)

        assert len(chunks) > 1
        # Each chunk should be around 500 chars with overlap
        assert all(len(chunk) <= 550 for chunk in chunks)

    def test_chunk_short_text(self, research_agent):
        """Test chunking short text."""
        text = "Short text"

        chunks = research_agent._chunk_text(text)

        assert len(chunks) == 1
        assert chunks[0] == text


class TestSearxngSearch:
    """Test searxng search integration."""

    @patch("httpx.get")
    def test_search_searxng_success(self, mock_get):
        """Test successful searxng search."""
        agent = GameStoryResearchAgent()

        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {"url": "https://example.com/1", "title": "Result 1"},
                {"url": "https://example.com/2", "title": "Result 2"},
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        results = agent._search_searxng("test query", num_results=5)

        assert len(results) == 2
        assert results[0]["url"] == "https://example.com/1"
        assert results[0]["title"] == "Result 1"

    @patch("httpx.get")
    def test_search_searxng_error(self, mock_get):
        """Test searxng search error handling."""
        agent = GameStoryResearchAgent()

        mock_get.side_effect = Exception("Network error")

        results = agent._search_searxng("test query")

        assert len(results) == 0


class TestContentFetching:
    """Test content fetching with webfetch."""

    @patch("src.tools.webfetch.webfetch")
    def test_fetch_content_success(self, mock_webfetch):
        """Test successful content fetch."""
        agent = GameStoryResearchAgent()

        mock_webfetch.return_value = "Fetched content"

        content = agent._fetch_content("https://example.com")

        assert content == "Fetched content"

    @patch("src.tools.webfetch.webfetch")
    def test_fetch_content_error(self, mock_webfetch):
        """Test content fetch error handling."""
        agent = GameStoryResearchAgent()

        mock_webfetch.side_effect = Exception("Fetch error")

        content = agent._fetch_content("https://example.com")

        assert content is None


class TestResearchWorkflow:
    """Test the complete research workflow."""

    @patch("src.tools.webfetch.webfetch")
    @patch("httpx.get")
    def test_research_game_already_processed(self, mock_get, mock_webfetch):
        """Test research when game is already processed."""
        agent = GameStoryResearchAgent()

        # Mock that game is already processed
        with patch.object(
            agent.game_tracker, "check_game_processed", return_value=True
        ):
            result = agent.research_game("elden_ring")

            assert result["success"] is True
            assert "already processed" in result["message"]
            # Should not call webfetch or searxng
            mock_webfetch.assert_not_called()
            mock_get.assert_not_called()

    @patch("src.tools.webfetch.webfetch")
    @patch("httpx.get")
    def test_research_game_new_game(self, mock_get, mock_webfetch):
        """Test researching a new game."""
        agent = GameStoryResearchAgent()

        # Mock searxng search
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {"url": "https://example.com/walkthrough", "title": "Walkthrough"}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Mock webfetch
        long_content = "A" * 1000
        mock_webfetch.return_value = f"# Walkthrough\n\n{long_content}"

        # Mock game not processed
        with patch.object(
            agent.game_tracker, "check_game_processed", return_value=False
        ):
            result = agent.research_game("test_game")

            assert result["success"] is True
            assert result["total_chunks"] > 0

    def test_force_refresh(self):
        """Test force refresh flag."""
        agent = GameStoryResearchAgent()

        with patch.object(
            agent.game_tracker, "check_game_processed", return_value=True
        ):
            with patch.object(agent, "_search_searxng") as mock_search:
                # Without force_refresh
                agent.research_game("test_game", force_refresh=False)
                assert mock_search.call_count == 0

                # With force_refresh
                agent.research_game("test_game", force_refresh=True)
                assert mock_search.call_count > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
