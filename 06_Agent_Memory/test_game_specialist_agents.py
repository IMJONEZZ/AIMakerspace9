"""
Tests for Game Specialist Agents module.
"""

import pytest
from unittest.mock import Mock, patch

from src.game_specialist_agents import (
    UnlockablesAgent,
    ProgressionAgent,
    LoreAgent,
    create_unlockables_agent,
    create_progression_agent,
    create_lore_agent,
)


class TestBaseGameSpecialistAgent:
    """Test base game specialist agent functionality."""

    def test_get_game_context_no_selection(self):
        """Test getting context when no game is selected."""
        mock_flow = Mock()
        mock_flow.get_user_game.return_value = None

        from src.game_specialist_agents import BaseGameSpecialistAgent

        agent = BaseGameSpecialistAgent(
            agent_name="TestAgent",
            system_prompt="You are a test agent.",
            game_input_flow=mock_flow,
            user_progress=Mock(),
            knowledge_base=Mock(),
        )

        context = agent._get_game_context("user1")
        assert context is None
        mock_flow.get_user_game.assert_called_once_with("user1")

    def test_get_game_context_with_selection(self):
        """Test getting context when a game is selected."""
        mock_flow = Mock()
        mock_flow.get_user_game.return_value = {
            "game_name": "Elden Ring",
            "prompt": "Help me with Elden Ring",
        }

        from src.game_specialist_agents import BaseGameSpecialistAgent

        agent = BaseGameSpecialistAgent(
            agent_name="TestAgent",
            system_prompt="You are a test agent.",
            game_input_flow=mock_flow,
            user_progress=Mock(),
            knowledge_base=Mock(),
        )

        context = agent._get_game_context("user1")
        assert context["game_name"] == "Elden Ring"
        assert context["prompt"] == "Help me with Elden Ring"

    def test_get_user_progress(self):
        """Test getting user progress."""
        mock_progress = Mock()
        mock_progress.get_progress.return_value = "mid_game"

        from src.game_specialist_agents import BaseGameSpecialistAgent

        agent = BaseGameSpecialistAgent(
            agent_name="TestAgent",
            system_prompt="You are a test agent.",
            game_input_flow=Mock(),
            user_progress=mock_progress,
            knowledge_base=Mock(),
        )

        progress = agent._get_user_progress("user1", "Elden Ring")
        assert progress == "mid_game"
        mock_progress.get_progress.assert_called_once_with("user1", "Elden Ring")

    def test_get_user_progress_none(self):
        """Test getting user progress when none exists."""
        mock_progress = Mock()
        mock_progress.get_progress.return_value = None

        from src.game_specialist_agents import BaseGameSpecialistAgent

        agent = BaseGameSpecialistAgent(
            agent_name="TestAgent",
            system_prompt="You are a test agent.",
            game_input_flow=Mock(),
            user_progress=mock_progress,
            knowledge_base=Mock(),
        )

        progress = agent._get_user_progress("user1", "Elden Ring")
        assert progress is None

    def test_search_game_knowledge_knowledge_base(self):
        """Test search_game_knowledgeing knowledge base."""
        mock_kb = Mock()
        mock_kb.search_game_knowledge.return_value = [
            {"text": "Weapon found in early game area", "score": 0.9}
        ]

        from src.game_specialist_agents import BaseGameSpecialistAgent

        agent = BaseGameSpecialistAgent(
            agent_name="TestAgent",
            system_prompt="You are a test agent.",
            game_input_flow=Mock(),
            user_progress=Mock(),
            knowledge_base=mock_kb,
        )

        results = agent._search_knowledge_base(
            "how to find sword", "Elden Ring", "early_game"
        )

        assert len(results) == 1
        mock_kb.search_game_knowledge.assert_called_once()


class TestUnlockablesAgent:
    """Test Unlockables Agent."""

    def test_agent_initialization(self):
        """Test that unlockables agent initializes correctly."""
        mock_flow = Mock()
        mock_progress = Mock()
        mock_kb = Mock()

        agent = UnlockablesAgent(mock_flow, mock_progress, mock_kb)

        assert agent.agent_name == "UnlockablesAgent"
        assert "unlock" in agent.system_prompt.lower()
        assert "spoiler" in agent.system_prompt.lower()

    @patch("langchain_openai.ChatOpenAI")
    def test_handle_query_no_game_selected(self, mock_llm_class):
        """Test handling query when no game is selected."""
        mock_flow = Mock()
        mock_flow.get_user_game.return_value = None

        agent = UnlockablesAgent(mock_flow, Mock(), Mock())

        response, success = agent.handle_query("user1", "how to unlock sword")

        assert success is False
        assert "select a game first" in response.lower()

    @patch("langchain_openai.ChatOpenAI")
    def test_handle_query_with_game(self, mock_llm_class):
        """Test handling query with a selected game."""
        mock_flow = Mock()
        mock_flow.get_user_game.return_value = {
            "game_name": "Elden Ring",
            "prompt": "",
        }

        mock_progress = Mock()
        mock_progress.get_progress.return_value = "early_game"

        mock_kb = Mock()
        mock_kb.search_game_knowledge.return_value = [
            {"text": "Sword found in Limgrave", "score": 0.9}
        ]

        mock_response = Mock()
        mock_response.content = "You can find the sword in Limgrave"
        mock_llm_instance = Mock()
        mock_llm_instance.invoke.return_value = mock_response
        mock_llm_class.return_value = mock_llm_instance

        agent = UnlockablesAgent(mock_flow, mock_progress, mock_kb)

        response, success = agent.handle_query("user1", "how to unlock sword")

        assert success is True
        assert response == "You can find the sword in Limgrave"
        mock_kb.search_game_knowledge.assert_called_once()


class TestProgressionAgent:
    """Test Progression Agent."""

    def test_agent_initialization(self):
        """Test that progression agent initializes correctly."""
        mock_flow = Mock()
        mock_progress = Mock()
        mock_kb = Mock()

        agent = ProgressionAgent(mock_flow, mock_progress, mock_kb)

        assert agent.agent_name == "ProgressionAgent"
        assert "progression" in agent.system_prompt.lower()
        assert "puzzle" in agent.system_prompt.lower()

    @patch("langchain_openai.ChatOpenAI")
    def test_handle_query_puzzle_help(self, mock_llm_class):
        """Test handling puzzle help query."""
        mock_flow = Mock()
        mock_flow.get_user_game.return_value = {"game_name": "Zelda", "prompt": ""}

        mock_progress = Mock()
        mock_progress.get_progress.return_value = "mid_game"

        mock_kb = Mock()
        mock_kb.search_game_knowledge.return_value = [
            {"text": "Puzzle solution involves pushing blocks", "score": 0.95}
        ]

        mock_response = Mock()
        mock_response.content = "Try pushing the blocks onto the pressure plates"
        mock_llm_instance = Mock()
        mock_llm_instance.invoke.return_value = mock_response
        mock_llm_class.return_value = mock_llm_instance

        agent = ProgressionAgent(mock_flow, mock_progress, mock_kb)

        response, success = agent.handle_query("user1", "stuck on water temple puzzle")

        assert success is True
        assert "Try pushing" in response


class TestLoreAgent:
    """Test Lore Agent."""

    def test_agent_initialization(self):
        """Test that lore agent initializes correctly."""
        mock_flow = Mock()
        mock_progress = Mock()
        mock_kb = Mock()

        agent = LoreAgent(mock_flow, mock_progress, mock_kb)

        assert agent.agent_name == "LoreAgent"
        assert "lore" in agent.system_prompt.lower()
        assert "story" in agent.system_prompt.lower()

    @patch("langchain_openai.ChatOpenAI")
    def test_handle_query_lore_question(self, mock_llm_class):
        """Test handling lore question."""
        mock_flow = Mock()
        mock_flow.get_user_game.return_value = {
            "game_name": "Elden Ring",
            "prompt": "",
        }

        mock_progress = Mock()
        mock_progress.get_progress.return_value = "early_game"

        mock_kb = Mock()
        mock_kb.search_game_knowledge.return_value = [
            {
                "text": "The Lands Between were ruled by Queen Marika the Eternal",
                "score": 0.98,
            }
        ]

        mock_response = Mock()
        mock_response.content = "Queen Marika ruled the Lands Between"
        mock_llm_instance = Mock()
        mock_llm_instance.invoke.return_value = mock_response
        mock_llm_class.return_value = mock_llm_instance

        agent = LoreAgent(mock_flow, mock_progress, mock_kb)

        response, success = agent.handle_query("user1", "who ruled the lands between")

        assert success is True
        assert "Queen Marika" in response


class TestFactoryFunctions:
    """Test factory functions."""

    def test_create_unlockables_agent(self):
        """Test creating unlockables agent via factory."""
        mock_flow = Mock()
        mock_progress = Mock()
        mock_kb = Mock()

        agent = create_unlockables_agent(mock_flow, mock_progress, mock_kb)

        assert isinstance(agent, UnlockablesAgent)
        assert agent.game_input_flow == mock_flow
        assert agent.user_progress == mock_progress
        assert agent.knowledge_base == mock_kb

    def test_create_progression_agent(self):
        """Test creating progression agent via factory."""
        mock_flow = Mock()
        mock_progress = Mock()
        mock_kb = Mock()

        agent = create_progression_agent(mock_flow, mock_progress, mock_kb)

        assert isinstance(agent, ProgressionAgent)
        assert agent.game_input_flow == mock_flow
        assert agent.user_progress == mock_progress
        assert agent.knowledge_base == mock_kb

    def test_create_lore_agent(self):
        """Test creating lore agent via factory."""
        mock_flow = Mock()
        mock_progress = Mock()
        mock_kb = Mock()

        agent = create_lore_agent(mock_flow, mock_progress, mock_kb)

        assert isinstance(agent, LoreAgent)
        assert agent.game_input_flow == mock_flow
        assert agent.user_progress == mock_progress
        assert agent.knowledge_base == mock_kb


class TestSpoilerControl:
    """Test spoiler control in agents."""

    @patch("langchain_openai.ChatOpenAI")
    def test_spoiler_filtering_applied(self, mock_llm_class):
        """Test that spoiler filtering is applied to knowledge base search_game_knowledge."""
        mock_flow = Mock()
        mock_flow.get_user_game.return_value = {"game_name": "Game", "prompt": ""}

        mock_progress = Mock()
        mock_progress.get_progress.return_value = "early_game"

        mock_kb = Mock()
        mock_kb.search_game_knowledge.return_value = []

        mock_response = Mock()
        mock_response.content = "Response"
        mock_llm_instance = Mock()
        mock_llm_instance.invoke.return_value = mock_response
        mock_llm_class.return_value = mock_llm_instance

        agent = UnlockablesAgent(mock_flow, mock_progress, mock_kb)
        agent.handle_query("user1", "test query")

        call_args = mock_kb.search_game_knowledge.call_args
        assert call_args is not None
        kwargs = call_args.kwargs if hasattr(call_args, "kwargs") else call_args[1]
        assert kwargs["avoid_spoilers"] is True
        assert kwargs["user_progress_marker"] == "early_game"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
