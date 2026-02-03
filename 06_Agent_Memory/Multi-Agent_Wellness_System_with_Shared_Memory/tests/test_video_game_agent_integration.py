#!/usr/bin/env python3
"""
Integration tests for the complete video game agent system.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


class TestVideoGameAgentIntegration:
    """Integration tests for the complete video game agent system."""

    @pytest.fixture
    def mock_qdrant_client(self):
        """Mock QDrant client for testing."""
        client = Mock()
        client.get_collections.return_value = Mock(collections=[])
        client.scroll.return_value = ([], None)
        client.upsert.return_value = None
        client.search.return_value = []
        return client

    @pytest.fixture
    def mock_webfetch(self):
        """Mock webfetch for testing."""
        webfetch = Mock()
        webfetch.fetch.return_value = """
        Test Game is an adventure game with:
        - Combat system with various weapons
        - Open-world exploration
        - Character progression
        - Multiple endings
        - Hidden unlockables
        - Rich lore and history
        """
        return webfetch

    @pytest.fixture
    def mock_llm(self):
        """Mock LLM for testing."""
        llm = Mock()
        llm.return_value.invoke.return_value = Mock(
            content="This is a test response from the agent."
        )
        llm.return_value.with_structured_output.return_value.invoke.return_value = Mock(
            agent="progression",
            reasoning="Query relates to game progression",
            confidence=0.9,
        )
        return llm

    @pytest.mark.asyncio
    async def test_game_story_research_flow(self, mock_qdrant_client, mock_webfetch):
        """Test the complete game story research flow."""
        with patch("src.game_story_research_agent.GameTracker") as mock_tracker:
            with patch(
                "src.game_story_research_agent.GameKnowledgeBase"
            ) as mock_knowledge_base:
                with patch("src.tools.webfetch.webfetch", return_value=mock_webfetch):
                    from src.game_story_research_agent import GameStoryResearchAgent

                    # Setup mocks
                    mock_tracker_instance = Mock()
                    mock_tracker_instance.is_game_processed.return_value = False
                    mock_tracker_instance.mark_game_processed.return_value = True
                    mock_tracker.return_value = mock_tracker_instance

                    mock_knowledge_base_instance = Mock()
                    mock_knowledge_base_instance.store_game_content.return_value = {
                        "chunks_stored": 5
                    }
                    mock_knowledge_base.return_value = mock_knowledge_base_instance

                    # Test research
                    agent = GameStoryResearchAgent(mock_qdrant_client)
                    result = agent.research_game("Test Game")

                    # Assertions
                    assert result["status"] == "success"
                    assert result["chunks_stored"] == 5
                    mock_tracker_instance.mark_game_processed.assert_called_once_with(
                        "Test Game"
                    )

    @pytest.mark.asyncio
    async def test_game_router_integration(self, mock_llm):
        """Test game router with mocked dependencies."""
        with patch("src.game_router.GameInputFlow") as mock_input_flow:
            with patch("src.game_router.ChatOpenAI", return_value=mock_llm):
                from src.game_router import GameRouterAgent

                # Setup mocks
                mock_input_flow_instance = Mock()
                mock_input_flow_instance.get_user_game.return_value = {
                    "game_name": "Test Game",
                    "prompt": "Help me progress",
                }
                mock_input_flow.return_value = mock_input_flow_instance

                # Test routing
                router = GameRouterAgent(mock_input_flow_instance)
                result = router.route_query("user123", "how do I beat the boss?")

                # Assertions
                assert result.agent == "progression"
                assert "progression" in result.reasoning.lower()
                assert result.confidence > 0.8

    @pytest.mark.asyncio
    async def test_specialist_agents_with_progress_filtering(self, mock_llm):
        """Test specialist agents with progress-based content filtering."""
        with patch("src.game_specialist_agents.GameInputFlow") as mock_input_flow:
            with patch("src.game_specialist_agents.UserGameProgress") as mock_progress:
                with patch(
                    "src.game_specialist_agents.GameKnowledgeBase"
                ) as mock_knowledge_base:
                    with patch(
                        "src.game_specialist_agents.ChatOpenAI", return_value=mock_llm
                    ):
                        from src.game_specialist_agents import (
                            UnlockablesAgent,
                            ProgressionAgent,
                            LoreAgent,
                        )

                        # Setup mocks
                        mock_input_flow_instance = Mock()
                        mock_input_flow_instance.get_user_game.return_value = {
                            "game_name": "Test Game"
                        }
                        mock_input_flow.return_value = mock_input_flow_instance

                        mock_progress_instance = Mock()
                        mock_progress_instance.get_progress.return_value = "early_game"
                        mock_progress.return_value = mock_progress_instance

                        mock_knowledge_base_instance = Mock()
                        mock_knowledge_base_instance.search_game_knowledge.return_value = [
                            {
                                "text": "Early game unlockable",
                                "metadata": {"spoiler_level": "early"},
                            }
                        ]
                        mock_knowledge_base.return_value = mock_knowledge_base_instance

                        # Test unlockables agent
                        unlockables = UnlockablesAgent(
                            mock_input_flow_instance,
                            mock_progress_instance,
                            mock_knowledge_base_instance,
                        )
                        response, success = unlockables.handle_query(
                            "user123", "secret items"
                        )

                        assert success
                        assert response is not None

    @pytest.mark.asyncio
    async def test_user_progress_tracking(self):
        """Test user game progress tracking."""
        with patch("src.user_game_progress.BaseStore"):
            from src.user_game_progress import UserGameProgress

            progress = UserGameProgress()

            # Test progress setting and getting
            progress.set_progress("user123", "mid_game")
            current_progress = progress.get_progress("user123")

            assert current_progress == "mid_game"

            # Test progress validation
            try:
                progress.set_progress("user123", "invalid_progress")
                assert False, "Should have raised ValueError"
            except ValueError:
                pass  # Expected

    @pytest.mark.asyncio
    async def test_memory_conflict_resolution(self):
        """Test memory conflict resolution functionality."""
        with patch("src.wellness_memory.memory_types.BaseStore"):
            from src.wellness_memory.memory_types import EpisodicMemory

            memory = EpisodicMemory(Mock())

            # Mock similar episodes
            mock_similar = [
                Mock(key="episode1", value={"importance": 0.5}),
                Mock(key="episode2", value={"importance": 0.8}),
            ]
            memory.find_similar = Mock(return_value=mock_similar)
            memory.remove_episode = Mock(return_value=True)
            memory.store_episode = Mock(return_value="new_episode_key")

            # Test conflict resolution
            result = memory.store_episode(
                key="test_episode",
                situation="test situation",
                input_text="test input",
                output_text="test output",
                importance=0.9,
            )

            assert result == "new_episode_key"

    @pytest.mark.asyncio
    async def test_end_to_end_game_flow(
        self, mock_qdrant_client, mock_webfetch, mock_llm
    ):
        """Test complete end-to-end flow."""
        # This test simulates a user asking for help with a game

        # Step 1: Research the game
        with patch("src.game_story_research_agent.GameTracker") as mock_tracker:
            with patch(
                "src.game_story_research_agent.GameKnowledgeBase"
            ) as mock_knowledge_base:
                with patch("src.tools.webfetch.webfetch", return_value=mock_webfetch):
                    from src.game_story_research_agent import GameStoryResearchAgent

                    mock_tracker_instance = Mock()
                    mock_tracker_instance.is_game_processed.return_value = False
                    mock_tracker_instance.mark_game_processed.return_value = True
                    mock_tracker.return_value = mock_tracker_instance

                    mock_knowledge_base_instance = Mock()
                    mock_knowledge_base_instance.store_game_content.return_value = {
                        "chunks_stored": 5
                    }
                    mock_knowledge_base.return_value = mock_knowledge_base_instance

                    researcher = GameStoryResearchAgent(mock_qdrant_client)
                    research_result = researcher.research_game("Test Game")

                    assert research_result["status"] == "success"

        # Step 2: Route the query
        with patch("src.game_router.GameInputFlow") as mock_input_flow:
            with patch("src.game_router.ChatOpenAI", return_value=mock_llm):
                from src.game_router import GameRouterAgent

                mock_input_flow_instance = Mock()
                mock_input_flow_instance.get_user_game.return_value = {
                    "game_name": "Test Game",
                    "prompt": "How do I find the secret sword?",
                }
                mock_input_flow.return_value = mock_input_flow_instance

                router = GameRouterAgent(mock_input_flow_instance)
                routing_result = router.route_query(
                    "user123", "How do I find the secret sword?"
                )

                assert routing_result.agent == "progression"  # Mock response

        # Step 3: Handle with specialist agent
        with patch("src.game_specialist_agents.GameInputFlow") as mock_input_flow:
            with patch("src.game_specialist_agents.UserGameProgress") as mock_progress:
                with patch(
                    "src.game_specialist_agents.GameKnowledgeBase"
                ) as mock_knowledge_base:
                    with patch(
                        "src.game_specialist_agents.ChatOpenAI", return_value=mock_llm
                    ):
                        from src.game_specialist_agents import ProgressionAgent

                        mock_input_flow_instance = Mock()
                        mock_input_flow_instance.get_user_game.return_value = {
                            "game_name": "Test Game"
                        }
                        mock_input_flow.return_value = mock_input_flow_instance

                        mock_progress_instance = Mock()
                        mock_progress_instance.get_progress.return_value = "early_game"
                        mock_progress.return_value = mock_progress_instance

                        mock_knowledge_base_instance = Mock()
                        mock_knowledge_base_instance.search_game_knowledge.return_value = [
                            {
                                "text": "Early game progression info",
                                "metadata": {"spoiler_level": "early"},
                            }
                        ]
                        mock_knowledge_base.return_value = mock_knowledge_base_instance

                        agent = ProgressionAgent(
                            mock_input_flow_instance,
                            mock_progress_instance,
                            mock_knowledge_base_instance,
                        )
                        response, success = agent.handle_query(
                            "user123", "How do I find the secret sword?"
                        )

                        assert success
                        assert response is not None

    def test_system_components_initialization(self):
        """Test that all system components can be initialized."""
        try:
            # Test imports
            from src.game_router import GameRouterAgent
            from src.game_specialist_agents import (
                UnlockablesAgent,
                ProgressionAgent,
                LoreAgent,
            )
            from src.game_story_research_agent import GameStoryResearchAgent
            from src.user_game_progress import UserGameProgress
            from src.game_knowledge_base import GameKnowledgeBase

            # Test basic initialization with mocks
            with patch("src.game_router.GameInputFlow"):
                router = GameRouterAgent(Mock())
                assert router is not None

            with patch("src.game_specialist_agents.GameInputFlow"):
                with patch("src.game_specialist_agents.UserGameProgress"):
                    with patch("src.game_specialist_agents.GameKnowledgeBase"):
                        unlockables = UnlockablesAgent(Mock(), Mock(), Mock())
                        progression = ProgressionAgent(Mock(), Mock(), Mock())
                        lore = LoreAgent(Mock(), Mock(), Mock())

                        assert unlockables is not None
                        assert progression is not None
                        assert lore is not None

            with patch("src.user_game_progress.BaseStore"):
                progress = UserGameProgress()
                assert progress is not None

        except ImportError as e:
            pytest.fail(f"Failed to import system components: {e}")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
