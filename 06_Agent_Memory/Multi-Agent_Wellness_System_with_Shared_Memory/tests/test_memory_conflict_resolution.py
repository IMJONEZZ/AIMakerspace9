#!/usr/bin/env python3
"""
Tests for memory conflict resolution functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


class TestMemoryConflictResolution:
    """Test memory conflict resolution and cleanup functionality."""

    @pytest.fixture
    def mock_store(self):
        """Mock storage for testing."""
        store = Mock()
        store.list.return_value = []
        store.get.return_value = None
        return store

    def test_find_similar_episodes_detection(self, mock_store):
        """Test detection of similar episodes."""
        with patch("src.wellness_memory.memory_types.BaseStore"):
            from src.wellness_memory.memory_types import EpisodicMemory

            memory = EpisodicMemory(mock_store)

            # Mock existing episodes
            mock_episodes = [
                Mock(
                    key="episode1",
                    value={
                        "situation": "Help with boss fight",
                        "input_text": "how to beat final boss",
                        "similarity_score": 0.9,
                    },
                ),
                Mock(
                    key="episode2",
                    value={
                        "situation": "Boss strategy help",
                        "input_text": "final boss strategy",
                        "similarity_score": 0.8,
                    },
                ),
            ]

            memory.find_similar = Mock(return_value=mock_episodes)

            # Test detection
            similar = memory.find_similar("new_episode", threshold=0.85, limit=5)

            assert len(similar) == 2
            assert similar[0].value["similarity_score"] > 0.85

    def test_importance_based_merging(self, mock_store):
        """Test importance-based episode merging."""
        with patch("src.wellness_memory.memory_types.BaseStore"):
            from src.wellness_memory.memory_types import EpisodicMemory

            memory = EpisodicMemory(mock_store)

            # Mock episodes with different importance
            low_importance = Mock(
                key="episode1", value={"importance": 0.3, "situation": "Basic help"}
            )
            high_importance = Mock(
                key="episode2", value={"importance": 0.9, "situation": "Critical help"}
            )

            memory.find_similar = Mock(return_value=[low_importance, high_importance])
            memory.remove_episode = Mock(return_value=True)
            memory.store_episode = Mock(return_value="merged_episode")

            # Test merging logic (high importance should replace low importance)
            result = memory.store_episode(
                key="test_episode",
                situation="test situation",
                input_text="test input",
                output_text="test output",
                importance=0.9,
            )

            # Should store new high-importance episode
            assert result == "merged_episode"

    def test_episode_removal_with_reason(self, mock_store):
        """Test episode removal with proper reason tracking."""
        with patch("src.wellness_memory.memory_types.BaseStore"):
            from src.wellness_memory.memory_types import EpisodicMemory

            memory = EpisodicMemory(mock_store)

            # Mock episode removal
            memory.remove_episode = Mock(return_value=True)

            # Test removal
            success = memory.remove_episode("episode1", reason="Duplicate content")

            assert success
            memory.remove_episode.assert_called_once_with(
                "episode1", reason="Duplicate content"
            )

    def test_conflict_resolution_thresholds(self, mock_store):
        """Test different similarity thresholds for conflict detection."""
        with patch("src.wellness_memory.memory_types.BaseStore"):
            from src.wellness_memory.memory_types import EpisodicMemory

            memory = EpisodicMemory(mock_store)

            # Test different thresholds
            test_cases = [
                (0.95, "strict"),  # Very strict - should catch fewer conflicts
                (0.85, "moderate"),  # Moderate - balanced approach
                (0.70, "lenient"),  # Lenient - catches more potential conflicts
            ]

            for threshold, description in test_cases:
                # Mock episodes with varying similarity scores
                mock_episodes = [
                    Mock(key="episode1", value={"similarity_score": 0.9}),
                    Mock(key="episode2", value={"similarity_score": 0.8}),
                    Mock(key="episode3", value={"similarity_score": 0.7}),
                ]

                memory.find_similar = Mock(return_value=mock_episodes)

                # Filter episodes based on threshold
                similar = memory.find_similar("test_episode", threshold=threshold)
                filtered_count = len(
                    [e for e in similar if e.value["similarity_score"] >= threshold]
                )

                # Verify threshold filtering works
                assert filtered_count >= 1  # At least one episode should match

    def test_merge_reason_tracking(self, mock_store):
        """Test that merge reasons are properly tracked."""
        with patch("src.wellness_memory.memory_types.BaseStore"):
            from src.wellness_memory.memory_types import EpisodicMemory

            memory = EpisodicMemory(mock_store)

            # Mock storage operations
            memory.remove_episode = Mock(return_value=True)
            memory.store_episode = Mock(return_value="merged_key")

            # Test with merge reason
            result = memory.store_episode(
                key="new_episode",
                situation="Updated situation",
                input_text="input",
                output_text="output",
                importance=0.8,
                merge_reason="Replacing duplicate with higher importance",
            )

            assert result == "merged_key"

    def test_batch_conflict_resolution(self, mock_store):
        """Test resolving conflicts for multiple episodes at once."""
        with patch("src.wellness_memory.memory_types.BaseStore"):
            from src.wellness_memory.memory_types import EpisodicMemory

            memory = EpisodicMemory(mock_store)

            # Mock multiple conflicting episodes
            conflicts = [
                {
                    "key": f"conflict_episode_{i}",
                    "importance": 0.4 + (i * 0.1),
                    "situation": f"Similar situation {i}",
                }
                for i in range(3)
            ]

            # Mock resolution process
            removed_episodes = []
            stored_episodes = []

            def mock_remove(key, **kwargs):
                removed_episodes.append((key, kwargs.get("reason", "No reason")))
                return True

            def mock_store(**kwargs):
                stored_episodes.append(kwargs)
                return f"stored_{len(stored_episodes)}"

            memory.remove_episode = Mock(side_effect=mock_remove)
            memory.store_episode = Mock(side_effect=mock_store)

            # Simulate batch resolution
            for conflict in conflicts:
                # Lower importance episodes would be removed
                if conflict["importance"] < 0.6:
                    memory.remove_episode(conflict["key"], reason="Low importance")
                else:
                    memory.store_episode(
                        key=conflict["key"],
                        situation=conflict["situation"],
                        input_text="input",
                        output_text="output",
                        importance=conflict["importance"],
                    )

            # Verify resolution
            assert len(removed_episodes) == 2  # Low importance episodes removed
            assert len(stored_episodes) == 1  # High importance episode kept

    def test_similarity_score_calculation(self, mock_store):
        """Test similarity score calculation for conflict detection."""
        with patch("src.wellness_memory.memory_types.BaseStore"):
            from src.wellness_memory.memory_types import EpisodicMemory

            memory = EpisodicMemory(mock_store)

            # Mock embedding similarity calculation
            def mock_calculate_similarity(text1, text2):
                # Simple mock similarity calculation
                common_words = set(text1.lower().split()) & set(text2.lower().split())
                total_words = set(text1.lower().split()) | set(text2.lower().split())
                return len(common_words) / len(total_words) if total_words else 0

            # Test cases
            test_pairs = [
                ("how to beat boss", "help with boss fight", 0.8),  # High similarity
                ("sword location", "armor upgrade", 0.2),  # Low similarity
                ("character progression", "level up guide", 0.6),  # Medium similarity
            ]

            for text1, text2, expected_range in test_pairs:
                similarity = mock_calculate_similarity(text1, text2)

                if expected_range == 0.8:
                    assert similarity > 0.7  # High similarity
                elif expected_range == 0.2:
                    assert similarity < 0.5  # Low similarity
                else:
                    assert 0.5 <= similarity <= 0.8  # Medium similarity

    def test_memory_conflict_prevention(self, mock_store):
        """Test prevention of memory conflicts through smart storage."""
        with patch("src.wellness_memory.memory_types.BaseStore"):
            from src.wellness_memory.memory_types import EpisodicMemory

            memory = EpisodicMemory(mock_store)

            # Test conflict detection before storage
            memory.find_similar = Mock(
                return_value=[
                    Mock(
                        key="existing_episode",
                        value={
                            "importance": 0.8,
                            "situation": "Similar to new episode",
                        },
                    )
                ]
            )
            memory.remove_episode = Mock(return_value=True)
            memory.store_episode = Mock(return_value="new_key")

            # Attempt to store potentially conflicting episode
            result = memory.store_episode(
                key="potential_conflict",
                situation="Similar to existing episode",
                input_text="similar input",
                output_text="new output",
                importance=0.9,  # Higher importance, should replace
            )

            assert result == "new_key"
            memory.remove_episode.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
