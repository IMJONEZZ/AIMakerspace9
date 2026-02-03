"""Test memory cleanup functionality."""

import pytest
from unittest.mock import Mock
from src.wellness_memory.memory_types import EpisodicMemory
from langgraph.store.base import BaseStore


class TestMemoryCleanup:
    """Test memory cleanup features."""

    def test_cleanup_by_importance_threshold(self):
        """Test cleanup removes low importance episodes."""
        mock_store = Mock(spec=BaseStore)

        # Mock episodes with varying importance
        mock_episodes = [
            Mock(
                key="high_importance",
                value={"importance": 0.8, "timestamp": "2024-01-01T10:00:00"},
            ),
            Mock(
                key="medium_importance",
                value={"importance": 0.5, "timestamp": "2024-01-01T10:00:00"},
            ),
            Mock(
                key="low_importance",
                value={"importance": 0.1, "timestamp": "2024-01-01T10:00:00"},
            ),
        ]
        mock_store.search.return_value = mock_episodes

        memory = EpisodicMemory(mock_store)

        # Run cleanup with importance threshold of 0.3
        result = memory.cleanup_episodes(importance_threshold=0.3)

        # Should remove low importance episode
        assert result["status"] == "success"
        assert result["kept_count"] == 2  # high and medium importance
        assert result["removed_count"] == 1  # low importance episode
        assert "low_importance" in result["removal_reasons"]

    def test_cleanup_by_age(self):
        """Test cleanup removes old episodes."""
        mock_store = Mock(spec=BaseStore)

        # Mock episodes with different ages
        from datetime import datetime, timedelta

        old_date = (datetime.now() - timedelta(days=40)).isoformat()
        recent_date = (datetime.now() - timedelta(days=10)).isoformat()

        mock_episodes = [
            Mock(key="old_episode", value={"importance": 0.7, "timestamp": old_date}),
            Mock(
                key="recent_episode",
                value={"importance": 0.7, "timestamp": recent_date},
            ),
        ]
        mock_store.search.return_value = mock_episodes

        memory = EpisodicMemory(mock_store)

        # Run cleanup with 30-day age limit
        result = memory.cleanup_episodes(age_days=30)

        # Should remove old episode
        assert result["status"] == "success"
        assert result["kept_count"] == 1
        assert result["removed_count"] == 1
        assert "old_age" in result["removal_reasons"]

    def test_cleanup_max_episodes_limit(self):
        """Test cleanup respects maximum episode limit."""
        mock_store = Mock(spec=BaseStore)

        # Mock many episodes
        mock_episodes = [
            Mock(
                key=f"episode_{i}",
                value={
                    "importance": 0.5 + (i * 0.1),
                    "timestamp": "2024-01-01T10:00:00",
                },
            )
            for i in range(5)  # 5 episodes
        ]
        mock_store.search.return_value = mock_episodes

        memory = EpisodicMemory(mock_store)

        # Run cleanup with max_episodes=3
        result = memory.cleanup_episodes(max_episodes=3)

        # Should keep only top 3 by importance
        assert result["status"] == "success"
        assert result["kept_count"] == 3
        assert result["removed_count"] == 2
        assert "max_episodes_limit" in result["removal_reasons"]

    def test_cleanup_dry_run(self):
        """Test cleanup dry run doesn't actually remove episodes."""
        mock_store = Mock(spec=BaseStore)

        mock_episodes = [
            Mock(
                key="test_episode",
                value={"importance": 0.1, "timestamp": "2024-01-01T10:00:00"},
            ),
        ]
        mock_store.search.return_value = mock_episodes

        memory = EpisodicMemory(mock_store)

        # Run cleanup with dry_run=True
        result = memory.cleanup_episodes(dry_run=True)

        # Should report removal but not actually delete
        assert result["status"] == "success"
        assert result["dry_run"] is True
        assert result["removed_count"] == 0  # No actual deletions in dry run
        assert result["episodes_marked_for_removal"] == 1

    def test_cleanup_statistics(self):
        """Test cleanup statistics calculation."""
        mock_store = Mock(spec=BaseStore)

        # Mock episodes for statistics
        from datetime import datetime, timedelta

        old_date = (datetime.now() - timedelta(days=40)).isoformat()
        new_date = (datetime.now() - timedelta(days=5)).isoformat()

        mock_episodes = [
            Mock(
                key="old_low", value={"importance": 0.1, "timestamp": old_date}
            ),  # Old and low importance
            Mock(
                key="recent_high", value={"importance": 0.9, "timestamp": new_date}
            ),  # Recent and high importance
            Mock(
                key="recent_medium", value={"importance": 0.5, "timestamp": new_date}
            ),  # Recent and medium importance
        ]
        mock_store.search.return_value = mock_episodes

        memory = EpisodicMemory(mock_store)

        # Get statistics
        stats = memory.get_cleanup_statistics()

        # Should calculate correct statistics
        assert stats["status"] == "success"
        assert stats["total_episodes"] == 3
        assert stats["low_importance_count"] == 1  # old_low
        assert stats["old_episode_count"] == 1  # old_low
        assert stats["reclaimable_episodes"] == 2  # old_low (counted once)
        assert stats["average_importance"] == (0.1 + 0.9 + 0.5) / 3

    def test_combined_cleanup_criteria(self):
        """Test cleanup with multiple criteria combined."""
        mock_store = Mock(spec=BaseStore)

        # Mock episodes with various characteristics
        from datetime import datetime, timedelta

        very_old_date = (datetime.now() - timedelta(days=50)).isoformat()
        old_date = (datetime.now() - timedelta(days=40)).isoformat()
        recent_date = (datetime.now() - timedelta(days=10)).isoformat()

        mock_episodes = [
            Mock(
                key="very_old_low",
                value={"importance": 0.1, "timestamp": very_old_date},
            ),  # Very old and low importance
            Mock(
                key="old_low", value={"importance": 0.2, "timestamp": old_date}
            ),  # Old and low importance
            Mock(
                key="old_high", value={"importance": 0.8, "timestamp": old_date}
            ),  # Old but high importance
            Mock(
                key="recent_low", value={"importance": 0.1, "timestamp": recent_date}
            ),  # Recent but low importance
            Mock(
                key="recent_high", value={"importance": 0.9, "timestamp": recent_date}
            ),  # Recent and high importance
        ]
        mock_store.search.return_value = mock_episodes

        memory = EpisodicMemory(mock_store)

        # Run cleanup with multiple criteria
        result = memory.cleanup_episodes(
            importance_threshold=0.3,  # Remove importance < 0.3
            age_days=30,  # Remove older than 30 days
            max_episodes=3,  # Keep only top 3
        )

        # Should remove based on all criteria
        assert result["status"] == "success"
        assert result["kept_count"] == 1  # Only recent_high
        assert (
            result["removed_count"] == 4
        )  # very_old_low, old_low, recent_low, old_high

        # Check removal reasons
        reasons = result["removal_reasons"]
        assert "low_importance" in reasons
        assert "old_age" in reasons

    def test_cleanup_error_handling(self):
        """Test cleanup error handling."""
        mock_store = Mock(spec=BaseStore)
        mock_store.search.side_effect = Exception("Database error")

        memory = EpisodicMemory(mock_store)

        # Should handle errors gracefully
        result = memory.cleanup_episodes()
        assert result["status"] == "error"
        assert "message" in result

    def test_cleanup_empty_memory(self):
        """Test cleanup with empty episodic memory."""
        mock_store = Mock(spec=BaseStore)
        mock_store.search.return_value = []

        memory = EpisodicMemory(mock_store)

        # Run cleanup on empty memory
        result = memory.cleanup_episodes()

        # Should handle empty memory gracefully
        assert result["status"] == "success"
        assert result["removed_count"] == 0
        assert result["kept_count"] == 0

    def test_removal_reasons_summary(self):
        """Test removal reasons are summarized correctly."""
        mock_store = Mock(spec=BaseStore)

        # Mock episodes for different reasons
        mock_episodes = [
            Mock(key="test1", value={"importance": 0.1, "timestamp": "2024-01-01"}),
            Mock(key="test2", value={"importance": 0.2, "timestamp": "2024-01-01"}),
            Mock(key="test3", value={"importance": 0.15, "timestamp": "2024-01-01"}),
        ]
        mock_store.search.return_value = mock_episodes

        memory = EpisodicMemory(mock_store)

        # Run cleanup with low threshold to trigger removals
        result = memory.cleanup_episodes(importance_threshold=0.3)

        # Should summarize reasons correctly
        reasons = result["removal_reasons"]
        assert reasons["low_importance"] == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
