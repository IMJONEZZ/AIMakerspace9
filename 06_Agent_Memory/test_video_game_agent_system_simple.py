"""System tests for the complete video game agent functionality.

These tests verify the integration of all components with realistic scenarios.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.game_specialist_agents import (
    UnlockablesAgent,
    ProgressionAgent,
    LoreAgent,
)


class TestSpecialistAgentIntegration:
    """Integration tests for specialist agents working together."""

    def test_unlockables_agent_basic_functionality(self):
        """Test UnlockablesAgent with minimal mocking."""
        # Create minimal mocks
        mock_input_flow = Mock()
        mock_progress = Mock()
        mock_knowledge_base = Mock()

        # Setup mock responses
        mock_input_flow.get_user_game.return_value = {
            "game_name": "The Legend of Zelda",
            "prompt": "Find all heart pieces",
        }
        mock_progress.get_progress.return_value = "early_game"
        mock_knowledge_base.search_game_knowledge.return_value = [
            {
                "text": "Heart pieces are hidden throughout Hyrule",
                "metadata": {"spoiler_level": "early"},
            }
        ]

        # Create agent
        agent = UnlockablesAgent(
            game_input_flow=mock_input_flow,
            user_progress=mock_progress,
            knowledge_base=mock_knowledge_base,
        )

        # Mock the LLM
        with patch("src.game_specialist_agents.ChatOpenAI") as mock_llm_class:
            mock_llm_instance = Mock()
            mock_llm_class.return_value = mock_llm_instance
            mock_llm_instance.invoke.return_value = Mock(
                content="I found information about heart pieces for you..."
            )

            # Test query handling
            result, success = agent.handle_query(
                "user123", "where can I find heart pieces?"
            )

            # Verify calls were made
            mock_input_flow.get_user_game.assert_called_with("user123")
            mock_progress.get_progress.assert_called_with("user123")
            mock_knowledge_base.search_game_knowledge.assert_called()
            mock_llm.invoke.assert_called()

            # Check result
            assert success is True
            assert "heart pieces" in result

    def test_progression_agent_basic_functionality(self):
        """Test ProgressionAgent with minimal mocking."""
        # Create minimal mocks
        mock_input_flow = Mock()
        mock_progress = Mock()
        mock_knowledge_base = Mock()

        # Setup mock responses
        mock_input_flow.get_user_game.return_value = {
            "game_name": "Dark Souls",
            "prompt": "Help me progress",
        }
        mock_progress.get_progress.return_value = "mid_game"
        mock_knowledge_base.search_game_knowledge.return_value = [
            {
                "text": "Anor Londo is the next major area",
                "metadata": {"spoiler_level": "mid_game"},
            }
        ]

        # Create agent
        agent = ProgressionAgent(
            game_input_flow=mock_input_flow,
            user_progress=mock_progress,
            knowledge_base=mock_knowledge_base,
        )

        # Mock the LLM
        with patch.object(agent, "llm") as mock_llm:
            mock_llm.invoke.return_value = Mock(
                content="Based on your progress, you should head to Anor Londo..."
            )

            # Test query handling
            result, success = agent.handle_query("user456", "where should I go next?")

            # Verify calls were made
            mock_input_flow.get_user_game.assert_called_with("user456")
            mock_progress.get_progress.assert_called_with("user456")
            mock_knowledge_base.search_game_knowledge.assert_called()
            mock_llm.invoke.assert_called()

            # Check result
            assert success is True
            assert "Anor Londo" in result

    def test_lore_agent_basic_functionality(self):
        """Test LoreAgent with minimal mocking."""
        # Create minimal mocks
        mock_input_flow = Mock()
        mock_progress = Mock()
        mock_knowledge_base = Mock()

        # Setup mock responses
        mock_input_flow.get_user_game.return_value = {
            "game_name": "The Witcher 3",
            "prompt": "Learn about the world",
        }
        mock_progress.get_progress.return_value = "early_game"
        mock_knowledge_base.search_game_knowledge.return_value = [
            {
                "text": "The Wild Hunt is a group of spectral riders",
                "metadata": {"spoiler_level": "early"},
            }
        ]

        # Create agent
        agent = LoreAgent(
            game_input_flow=mock_input_flow,
            user_progress=mock_progress,
            knowledge_base=mock_knowledge_base,
        )

        # Mock the LLM
        with patch.object(agent, "llm") as mock_llm:
            mock_llm.invoke.return_value = Mock(
                content="The Wild Hunt plays a central role in the story..."
            )

            # Test query handling
            result, success = agent.handle_query(
                "user789", "tell me about the wild hunt"
            )

            # Verify calls were made
            mock_input_flow.get_user_game.assert_called_with("user789")
            mock_progress.get_progress.assert_called_with("user789")
            mock_knowledge_base.search_game_knowledge.assert_called()
            mock_llm.invoke.assert_called()

            # Check result
            assert success is True
            assert "Wild Hunt" in result

    def test_spoiler_filtering_integration(self):
        """Test that spoiler filtering works correctly across agents."""
        # Create minimal mocks
        mock_input_flow = Mock()
        mock_progress = Mock()
        mock_knowledge_base = Mock()

        # Setup user at early game progress
        mock_progress.get_progress.return_value = "intro/tutorial"

        # Mock knowledge base with mixed spoiler levels
        mock_knowledge_base.search_game_knowledge.return_value = [
            {"text": "Basic controls tutorial", "metadata": {"spoiler_level": "early"}},
            {"text": "Final boss strategy", "metadata": {"spoiler_level": "late_game"}},
            {
                "text": "Hidden treasure location",
                "metadata": {"spoiler_level": "mid_game"},
            },
        ]

        # Create progression agent
        agent = ProgressionAgent(
            game_input_flow=mock_input_flow,
            user_progress=mock_progress,
            knowledge_base=mock_knowledge_base,
        )

        # Mock the LLM
        with patch.object(agent, "llm") as mock_llm:
            mock_llm.invoke.return_value = Mock(
                content="Here's some early game advice..."
            )

            # Test query handling
            result, success = agent.handle_query("user123", "how do I get started?")

            # Verify knowledge was searched with spoiler filtering
            mock_knowledge_base.search_game_knowledge.assert_called()
            call_args = mock_knowledge_base.search_game_knowledge.call_args
            max_spoiler_level = call_args[1]["max_spoiler_level"]

            # Should filter to early game only
            assert max_spoiler_level == "intro/tutorial"

            # Check result
            assert success is True

    def test_game_context_handling(self):
        """Test that agents handle missing game context gracefully."""
        # Create minimal mocks
        mock_input_flow = Mock()
        mock_progress = Mock()
        mock_knowledge_base = Mock()

        # Setup no game selected
        mock_input_flow.get_user_game.return_value = None

        # Create agent
        agent = UnlockablesAgent(
            game_input_flow=mock_input_flow,
            user_progress=mock_progress,
            knowledge_base=mock_knowledge_base,
        )

        # Mock the LLM
        with patch.object(agent, "llm") as mock_llm:
            mock_llm.invoke.return_value = Mock(content="Please select a game first...")

            # Test query handling
            result, success = agent.handle_query("user123", "how to unlock something?")

            # Verify game context was checked
            mock_input_flow.get_user_game.assert_called_with("user123")

            # Should still return a response
            assert success is True
            assert "game" in result.lower() or "select" in result.lower()

    def test_error_handling_in_agents(self):
        """Test that agents handle errors gracefully."""
        # Create minimal mocks
        mock_input_flow = Mock()
        mock_progress = Mock()
        mock_knowledge_base = Mock()

        # Setup mock to raise exception
        mock_knowledge_base.search_game_knowledge.side_effect = Exception(
            "Database error"
        )

        # Create agent
        agent = ProgressionAgent(
            game_input_flow=mock_input_flow,
            user_progress=mock_progress,
            knowledge_base=mock_knowledge_base,
        )

        # Test query handling
        result, success = agent.handle_query("user123", "help me progress")

        # Should handle error gracefully
        assert success is False
        assert "error" in result.lower()

    def test_content_type_filtering(self):
        """Test that agents request appropriate content types."""
        # Create minimal mocks
        mock_input_flow = Mock()
        mock_progress = Mock()
        mock_knowledge_base = Mock()

        # Setup mock responses
        mock_input_flow.get_user_game.return_value = {
            "game_name": "Test Game",
            "prompt": "Unlockables content",
        }
        mock_progress.get_progress.return_value = "early_game"
        mock_knowledge_base.search_game_knowledge.return_value = []

        # Test different agent types
        agents = [
            (UnlockablesAgent, ["unlockables", "guides", "collectibles"]),
            (ProgressionAgent, ["progression", "walkthroughs", "strategies"]),
            (LoreAgent, ["lore", "story", "characters", "worldbuilding"]),
        ]

        for agent_class, expected_content_types in agents:
            # Create agent
            agent = agent_class(
                game_input_flow=mock_input_flow,
                user_progress=mock_progress,
                knowledge_base=mock_knowledge_base,
            )

            # Mock the LLM
            with patch.object(agent, "llm") as mock_llm:
                mock_llm.invoke.return_value = Mock(content="Test response...")

                # Test query handling
                result, success = agent.handle_query("user123", "test query")

                # Verify knowledge was searched with correct content types
                call_args = mock_knowledge_base.search_game_knowledge.call_args
                content_types = call_args[1]["content_types"]

                assert set(content_types) == set(expected_content_types)


class TestGameRouterIntegration:
    """Integration tests for the game router."""

    def test_router_with_no_game_selected(self):
        """Test router behavior when no game is selected."""
        # Create minimal mock
        mock_input_flow = Mock()
        mock_input_flow.get_user_game.return_value = None

        # Create router
        with patch("src.game_router.ChatOpenAI") as mock_llm_class:
            mock_llm_class.return_value = Mock()

            from src.game_router import GameRouterAgent

            router = GameRouterAgent(game_input_flow=mock_input_flow)

            # Test routing
            result = router.route_query("user123", "help me with games")

            # Should return default agent
            assert result.agent == "progression"
            assert "no game selected" in result.reasoning.lower()

    def test_router_with_game_selected(self):
        """Test router behavior when game is selected."""
        # Create minimal mock
        mock_input_flow = Mock()
        mock_input_flow.get_user_game.return_value = {
            "game_name": "The Legend of Zelda",
            "prompt": "Help with game",
        }

        # Create router
        with patch("src.game_router.ChatOpenAI") as mock_llm_class:
            mock_llm_instance = Mock()
            mock_llm_class.return_value = mock_llm_instance

            # Mock structured output
            mock_decision = Mock()
            mock_decision.agent = "lore"
            mock_decision.reasoning = "User asking about game story"
            mock_decision.confidence = 0.9
            mock_llm_instance.with_structured_output.return_value = Mock()
            mock_llm_instance.with_structured_output.return_value.invoke.return_value = mock_decision

            from src.game_router import GameRouterAgent

            router = GameRouterAgent(game_input_flow=mock_input_flow)

            # Test routing
            result = router.route_query("user123", "tell me about zelda's story")

            # Verify routing decision
            assert result.agent == "lore"
            assert result.reasoning == "User asking about game story"

    def test_different_query_types_routing(self):
        """Test that different query types are routed correctly."""
        test_cases = [
            ("how to unlock master sword", "unlockables"),
            ("best way to level up", "progression"),
            ("history of hyrule kingdom", "lore"),
            ("find all collectibles", "unlockables"),
            ("stuck on this boss", "progression"),
            ("who is ganondorf", "lore"),
        ]

        # Create minimal mock
        mock_input_flow = Mock()
        mock_input_flow.get_user_game.return_value = {
            "game_name": "The Legend of Zelda",
            "prompt": "Game help",
        }

        # Create router
        with patch("src.game_router.ChatOpenAI") as mock_llm_class:
            mock_llm_instance = Mock()
            mock_llm_class.return_value = mock_llm_instance

            from src.game_router import GameRouterAgent

            router = GameRouterAgent(game_input_flow=mock_input_flow)

            for query, expected_agent in test_cases:
                # Mock structured output
                mock_decision = Mock()
                mock_decision.agent = expected_agent
                mock_decision.reasoning = f"Query matches {expected_agent} domain"
                mock_decision.confidence = 0.8

                mock_llm_instance.with_structured_output.return_value = Mock()
                mock_llm_instance.with_structured_output.return_value.invoke.return_value = mock_decision

                # Test routing
                result = router.route_query("user123", query)

                # Verify routing decision
                assert result.agent == expected_agent


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
