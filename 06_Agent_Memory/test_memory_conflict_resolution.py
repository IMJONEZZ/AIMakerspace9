"""Test memory conflict resolution functionality."""

import pytest
from unittest.mock import Mock
from src.wellness_memory.memory_types import EpisodicMemory
from langgraph.store.base import BaseStore


class TestMemoryConflictResolution:
    """Test memory conflict resolution features."""

    def test_conflict_detection_and_resolution(self):
        """Test that conflicts are detected and resolved properly."""
        # Create mock store
        mock_store = Mock(spec=BaseStore)

        # Mock search to return similar episode
        mock_store.search.return_value = [
            Mock(
                key="existing_episode",
                value={
                    "situation": "User asks about exercise advice",
                    "input": "How should I exercise?",
                    "output": "Start with light cardio...",
                    "importance": 0.7,
                    "timestamp": "2024-01-01T10:00:00",
                },
                score=0.9,  # High similarity
            )
        ]

        # Create episodic memory
        memory = EpisodicMemory(mock_store)

        # Store new episode with high similarity
        resolved_key = memory.store_episode(
            key="new_episode",
            situation="User asks about exercise advice",
            input="How should I exercise?",
            output="Try cardio and strength training...",
            importance=0.8,  # Higher importance than existing
        )

        # Should create merged episode
        assert "merged" in resolved_key
        mock_store.put.assert_called()

        # Verify search was called for conflict detection
        mock_store.search.assert_called()

    def test_importance_based_resolution(self):
        """Test that higher importance episodes replace lower ones."""
        mock_store = Mock(spec=BaseStore)

        # Mock search with lower importance existing episode
        mock_store.search.return_value = [
            Mock(
                key="existing_episode",
                value={
                    "situation": "Similar situation",
                    "importance": 0.3,  # Lower importance
                },
                score=0.9,
            )
        ]

        memory = EpisodicMemory(mock_store)

        # Store higher importance episode
        resolved_key = memory.store_episode(
            key="high_importance_episode",
            situation="Similar situation",
            input="Test input",
            output="Test output",
            importance=0.9,  # Higher importance
        )

        # Should merge with higher importance winning
        assert "merged" in resolved_key

        # Check the merged episode data
        call_args = mock_store.put.call_args
        merged_data = call_args[0][2]  # namespace, key, value
        assert merged_data["importance"] == 0.9
        assert merged_data["merge_reason"] == "Higher importance"

    def test_no_conflict_storage(self):
        """Test that episodes without conflicts are stored normally."""
        mock_store = Mock(spec=BaseStore)

        # Mock search with no similar episodes
        mock_store.search.return_value = []

        memory = EpisodicMemory(mock_store)

        # Store episode with no conflicts
        resolved_key = memory.store_episode(
            key="unique_episode",
            situation="Unique situation",
            input="Unique input",
            output="Unique output",
        )

        # Should use original key
        assert resolved_key == "unique_episode"

        # Should store without merging
        call_args = mock_store.put.call_args
        stored_data = call_args[0][2]
        assert "merge_reason" not in stored_data

    def test_timestamp_addition(self):
        """Test that timestamps are added to episodes."""
        mock_store = Mock(spec=BaseStore)
        mock_store.search.return_value = []

        memory = EpisodicMemory(mock_store)

        # Store episode
        memory.store_episode(
            key="timestamp_test",
            situation="Test situation",
            input="Test input",
            output="Test output",
        )

        # Check timestamp was added
        call_args = mock_store.put.call_args
        stored_data = call_args[0][2]
        assert "timestamp" in stored_data
        assert stored_data["timestamp"] != ""

    def test_importance_scoring_in_retrieval(self):
        """Test that importance scores are included in retrieval results."""
        mock_store = Mock(spec=BaseStore)

        # Mock search results
        mock_store.search.return_value = [
            Mock(
                key="episode1",
                value={
                    "situation": "Test situation 1",
                    "input": "Input 1",
                    "output": "Output 1",
                    "importance": 0.8,
                    "timestamp": "2024-01-01T10:00:00",
                },
                score=0.9,
            )
        ]

        memory = EpisodicMemory(mock_store)

        # Find similar episodes
        results = memory.find_similar("test query")

        # Should include importance in results
        assert len(results) == 1
        assert "importance" in results[0]
        assert results[0]["importance"] == 0.8
        assert "timestamp" in results[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
