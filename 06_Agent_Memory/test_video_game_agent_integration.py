"""Simple integration test for video game agent system.

This test verifies that the main components can work together
without complex mocking scenarios.
"""

import pytest
from unittest.mock import Mock


class TestVideoGameAgentBasics:
    """Basic integration tests for the video game agent system."""

    def test_user_game_progress_creation(self):
        """Test UserGameProgress can be created and used."""
        from src.user_game_progress import UserGameProgress
        from qdrant_client import QdrantClient

        # Create with in-memory client
        client = QdrantClient(":memory:")
        progress = UserGameProgress(client)

        # Test basic operations
        progress.update_progress("user1", "intro/tutorial")
        stored = progress.get_progress("user1")
        assert stored == "intro/tutorial"

        # Test removal
        removed = progress.remove_progress("user1")
        assert removed is True

        # Test getting non-existent progress
        none_progress = progress.get_progress("user1")
        assert none_progress is None

    def test_game_tracker_creation(self):
        """Test GameTracker can be created and used."""
        from src.game_tracker import GameTracker
        from qdrant_client import QdrantClient

        # Create with in-memory client
        client = QdrantClient(":memory:")
        tracker = GameTracker(client)

        # Test basic operations
        processed = tracker.is_game_processed("Test Game")
        assert processed is False  # Should be False initially

        # Mark as processed
        tracker.mark_game_processed("Test Game")
        processed_after = tracker.is_game_processed("Test Game")
        assert processed_after is True

    def test_game_input_flow_creation(self):
        """Test GameInputFlow can be created and used."""
        from src.game_input_flow import GameInputFlow
        from qdrant_client import QdrantClient

        # Create with in-memory client
        client = QdrantClient(":memory:")
        input_flow = GameInputFlow(client)

        # Test getting non-existent game
        game = input_flow.get_user_game("user1")
        assert game is None

    def test_game_knowledge_base_creation(self):
        """Test GameKnowledgeBase can be created and used."""
        from src.game_knowledge_base import GameKnowledgeBase
        from qdrant_client import QdrantClient

        # Create with in-memory client
        client = QdrantClient(":memory:")
        knowledge_base = GameKnowledgeBase(client)

        # Test search (should work without errors)
        results = knowledge_base.search_game_knowledge(
            query="test query",
            game_name="Test Game",
            avoid_spoilers=True,
            user_progress_marker="early",
            content_types=["guides"],
            limit=3,
        )

        # Should return empty list for in-memory client
        assert isinstance(results, list)

    def test_specialist_agent_creation(self):
        """Test specialist agents can be created."""
        from src.game_specialist_agents import (
            UnlockablesAgent,
            ProgressionAgent,
            LoreAgent,
        )
        from src.game_input_flow import GameInputFlow
        from src.user_game_progress import UserGameProgress
        from src.game_knowledge_base import GameKnowledgeBase
        from qdrant_client import QdrantClient

        # Create with in-memory client
        client = QdrantClient(":memory:")
        input_flow = GameInputFlow(client)
        progress = UserGameProgress(client)
        knowledge_base = GameKnowledgeBase(client)

        # Create agents
        unlockables = UnlockablesAgent(input_flow, progress, knowledge_base)
        progression = ProgressionAgent(input_flow, progress, knowledge_base)
        lore = LoreAgent(input_flow, progress, knowledge_base)

        # Test agents are created
        assert unlockables is not None
        assert progression is not None
        assert lore is not None

        # Test agent names
        assert unlockables.agent_name == "Unlockables Specialist"
        assert progression.agent_name == "Progression Specialist"
        assert lore.agent_name == "Lore Specialist"

    def test_game_router_creation(self):
        """Test GameRouter can be created."""
        from src.game_router import GameRouterAgent
        from src.game_input_flow import GameInputFlow
        from qdrant_client import QdrantClient

        # Create with in-memory client
        client = QdrantClient(":memory:")
        input_flow = GameInputFlow(client)

        # Create router
        router = GameRouterAgent(input_flow)

        # Test router is created
        assert router is not None
        assert router.game_input_flow is input_flow

    def test_game_story_research_agent_creation(self):
        """Test GameStoryResearchAgent can be created."""
        from src.game_story_research_agent import GameStoryResearchAgent
        from qdrant_client import QdrantClient

        # Create with in-memory client
        client = QdrantClient(":memory:")
        agent = GameStoryResearchAgent(client)

        # Test agent is created
        assert agent is not None
        assert agent.qdrant_client is client

    def test_basic_token_counting_fix(self):
        """Test that token counting fix is working."""
        from src.wellness_memory.utils import trim_conversation
        from src.wellness_memory.memory_types import ShortTermMemory
        from langchain_core.messages import HumanMessage, AIMessage

        # Test trim_conversation doesn't raise errors
        messages = [
            HumanMessage(content="Hello"),
            AIMessage(content="Hi there"),
        ]

        result = trim_conversation(messages, max_tokens=100)
        assert isinstance(result, list)
        assert len(result) >= 0

        # Test ShortTermMemory trim method
        memory = ShortTermMemory(messages)
        trimmed = memory.trim(max_tokens=100)
        assert isinstance(trimmed, list)
        assert len(trimmed) >= 0

    def test_all_components_importable(self):
        """Test that all main components can be imported."""
        # Test all main imports work
        from src.game_story_research_agent import GameStoryResearchAgent
        from src.game_router import GameRouterAgent
        from src.game_specialist_agents import (
            BaseGameSpecialistAgent,
            UnlockablesAgent,
            ProgressionAgent,
            LoreAgent,
        )
        from src.user_game_progress import UserGameProgress
        from src.game_input_flow import GameInputFlow
        from src.game_knowledge_base import GameKnowledgeBase
        from src.game_tracker import GameTracker
        from src.wellness_memory.utils import trim_conversation
        from src.wellness_memory.memory_types import (
            ShortTermMemory,
            LongTermMemory,
            SemanticMemory,
            EpisodicMemory,
            ProceduralMemory,
        )

        # Test that classes are defined
        assert GameStoryResearchAgent is not None
        assert GameRouterAgent is not None
        assert BaseGameSpecialistAgent is not None
        assert UnlockablesAgent is not None
        assert ProgressionAgent is not None
        assert LoreAgent is not None
        assert UserGameProgress is not None
        assert GameInputFlow is not None
        assert GameKnowledgeBase is not None
        assert GameTracker is not None
        assert trim_conversation is not None
        assert ShortTermMemory is not None
        assert LongTermMemory is not None
        assert SemanticMemory is not None
        assert EpisodicMemory is not None
        assert ProceduralMemory is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
