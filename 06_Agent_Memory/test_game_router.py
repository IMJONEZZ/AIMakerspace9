"""
Tests for Game Router Agent module.
"""

import pytest
from unittest.mock import Mock, patch

from src.game_router import (
    GameRouterAgent,
    create_game_router_agent,
    RouterDecision,
)


class TestGameRouterAgent:
    """Test game router agent functionality."""

    def test_router_initialization(self):
        """Test that router initializes correctly."""
        mock_flow = Mock()

        router = GameRouterAgent(mock_flow)

        assert router.game_input_flow == mock_flow
        assert router.graph is not None

    def test_build_router_prompt_no_game(self):
        """Test building prompt without game context."""
        from src.game_router import GameRouterAgent

        router = GameRouterAgent.__new__(GameRouterAgent)

        prompt = router._build_router_prompt(None)

        assert "unlockables" in prompt
        assert "progression" in prompt
        assert "lore" in prompt
        assert "Selected Game:" not in prompt

    def test_build_router_prompt_with_game(self):
        """Test building prompt with game context."""
        from src.game_router import GameRouterAgent

        router = GameRouterAgent.__new__(GameRouterAgent)

        game_context = {
            "game_name": "Elden Ring",
            "prompt": "Help me find all the legendary weapons",
        }

        prompt = router._build_router_prompt(game_context)

        assert "Elden Ring" in prompt
        assert "Help me find all the legendary weapons" in prompt

    @patch("langchain_openai.ChatOpenAI")
    def test_route_query_no_game_selected(self, mock_llm_class):
        """Test routing when no game is selected."""
        mock_flow = Mock()
        mock_flow.get_user_game.return_value = None

        router = GameRouterAgent(mock_flow)

        decision = router.route_query("user1", "test query")

        assert isinstance(decision, RouterDecision)
        assert decision.agent == "progression"
        assert "No game selected" in decision.reasoning

    @patch("langchain_openai.ChatOpenAI")
    def test_route_query_with_game(self, mock_llm_class):
        """Test routing with a selected game."""
        mock_flow = Mock()
        mock_flow.get_user_game.return_value = {
            "game_name": "Elden Ring",
            "prompt": "",
        }

        mock_llm_instance = Mock()
        mock_decision = RouterDecision(
            agent="unlockables",
            reasoning="User is asking about unlocking items",
            confidence=0.9,
        )
        mock_llm_instance.with_structured_output.return_value.invoke.return_value = (
            mock_decision
        )
        mock_llm_class.return_value = mock_llm_instance

        router = GameRouterAgent(mock_flow)

        decision = router.route_query("user1", "how do I unlock the sword")

        assert isinstance(decision, RouterDecision)
        assert decision.agent == "unlockables"

    @patch("langchain_openai.ChatOpenAI")
    def test_route_query_progression(self, mock_llm_class):
        """Test routing progression query."""
        mock_flow = Mock()
        mock_flow.get_user_game.return_value = {"game_name": "Zelda", "prompt": ""}

        mock_llm_instance = Mock()
        mock_decision = RouterDecision(
            agent="progression",
            reasoning="User is asking about solving a puzzle",
            confidence=0.95,
        )
        mock_llm_instance.with_structured_output.return_value.invoke.return_value = (
            mock_decision
        )
        mock_llm_class.return_value = mock_llm_instance

        router = GameRouterAgent(mock_flow)

        decision = router.route_query("user1", "how do I solve this temple puzzle")

        assert decision.agent == "progression"

    @patch("langchain_openai.ChatOpenAI")
    def test_route_query_lore(self, mock_llm_class):
        """Test routing lore query."""
        mock_flow = Mock()
        mock_flow.get_user_game.return_value = {"game_name": "Dark Souls", "prompt": ""}

        mock_llm_instance = Mock()
        mock_decision = RouterDecision(
            agent="lore",
            reasoning="User is asking about character backstory",
            confidence=0.92,
        )
        mock_llm_instance.with_structured_output.return_value.invoke.return_value = (
            mock_decision
        )
        mock_llm_class.return_value = mock_llm_instance

        router = GameRouterAgent(mock_flow)

        decision = router.route_query("user1", "who is Gwyn really")

        assert decision.agent == "lore"


class TestRouterDecision:
    """Test RouterDecision model."""

    def test_router_decision_creation(self):
        """Test creating a router decision."""
        decision = RouterDecision(
            agent="unlockables",
            reasoning="Query is about unlocking items",
            confidence=0.9,
        )

        assert decision.agent == "unlockables"
        assert decision.reasoning == "Query is about unlocking items"
        assert decision.confidence == 0.9

    def test_router_decision_valid_agents(self):
        """Test that only valid agent names are used."""
        valid_agents = ["unlockables", "progression", "lore"]

        for agent in valid_agents:
            decision = RouterDecision(
                agent=agent, reasoning=f"Routing to {agent}", confidence=0.8
            )
            assert decision.agent == agent


class TestFactoryFunction:
    """Test factory function."""

    def test_create_game_router_agent(self):
        """Test creating router via factory."""
        mock_flow = Mock()

        router = create_game_router_agent(mock_flow)

        assert isinstance(router, GameRouterAgent)
        assert router.game_input_flow == mock_flow


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
