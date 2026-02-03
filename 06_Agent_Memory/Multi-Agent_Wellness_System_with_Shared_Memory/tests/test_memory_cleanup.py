#!/usr/bin/env python3
"""
Tests for memory cleanup and maintenance functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from datetime import datetime, timedelta

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


class TestMemoryCleanup:
    """Test memory cleanup and maintenance functionality."""

    @pytest.fixture
    def mock_store(self):
        """Mock storage for testing."""
        store = Mock()
        store.list.return_value = []
        store.get.return_value = None
        return store

    def test_cleanup_by_importance_threshold(self, mock_store):
        """Test cleanup based on importance threshold."""
        with patch("src.wellness_memory.memory_types.BaseStore"):
            from src.wellness_memory.memory_types import EpisodicMemory

            memory = EpisodicMemory(mock_store)

            # Mock episodes with varied importance
            episodes = [
                Mock(
                    key=f"episode_{i}",
                    value={
                        "importance": 0.1 * (i + 1),
                        "timestamp": datetime.now().isoformat(),
                    },
                )
                for i in range(10)  # Importance from 0.1 to 1.0
            ]

            memory.search = Mock(return_value=episodes)
            memory.remove_episode = Mock(return_value=True)

            # Test cleanup with importance threshold
            cleanup_result = memory.cleanup_episodes(
                importance_threshold=0.5,  # Remove episodes with importance < 0.5
                dry_run=False,
            )

            # Should have removed 4 episodes (0.1, 0.2, 0.3, 0.4)
            assert cleanup_result["removed_count"] == 4
            assert cleanup_result["kept_count"] == 6
            assert cleanup_result["criterion"] == "importance_threshold"

    def test_cleanup_by_age(self, mock_store):
        """Test cleanup based on episode age."""
        with patch("src.wellness_memory.memory_types.BaseStore"):
            from src.wellness_memory.memory_types import EpisodicMemory

            memory = EpisodicMemory(mock_store)

            # Mock episodes with different ages
            now = datetime.now()
            episodes = [
                Mock(
                    key=f"episode_{i}",
                    value={
                        "importance": 0.8,
                        "timestamp": (now - timedelta(days=i * 10)).isoformat(),
                    },
                )
                for i in range(10)  # Ages from 0 to 90 days
            ]

            memory.search = Mock(return_value=episodes)
            memory.remove_episode = Mock(return_value=True)

            # Test cleanup with age threshold (remove episodes older than 30 days)
            cleanup_result = memory.cleanup_episodes(max_age_days=30, dry_run=False)

            # Should have removed episodes older than 30 days (episodes 4, 5, 6, 7, 8, 9)
            assert cleanup_result["removed_count"] == 6
            assert cleanup_result["kept_count"] == 4
            assert cleanup_result["criterion"] == "age"

    def test_cleanup_by_maximum_count(self, mock_store):
        """Test cleanup to maintain maximum episode count."""
        with patch("src.wellness_memory.memory_types.BaseStore"):
            from src.wellness_memory.memory_types import EpisodicMemory

            memory = EpisodicMemory(mock_store)

            # Mock episodes (more than maximum allowed)
            episodes = [
                Mock(
                    key=f"episode_{i}",
                    value={
                        "importance": 0.5
                        + (i * 0.01),  # Slightly increasing importance
                        "timestamp": datetime.now().isoformat(),
                    },
                )
                for i in range(15)  # 15 episodes
            ]

            memory.search = Mock(return_value=episodes)
            memory.remove_episode = Mock(return_value=True)

            # Test cleanup with maximum count
            cleanup_result = memory.cleanup_episodes(
                max_episodes=10,  # Keep only 10 episodes
                dry_run=False,
            )

            # Should have removed 5 episodes (least important ones)
            assert cleanup_result["removed_count"] == 5
            assert cleanup_result["kept_count"] == 10
            assert cleanup_result["criterion"] == "max_count"

    def test_dry_run_cleanup(self, mock_store):
        """Test cleanup in dry-run mode (no actual removal)."""
        with patch("src.wellness_memory.memory_types.BaseStore"):
            from src.wellness_memory.memory_types import EpisodicMemory

            memory = EpisodicMemory(mock_store)

            # Mock episodes
            episodes = [
                Mock(
                    key=f"episode_{i}",
                    value={
                        "importance": 0.1 * (i + 1),
                        "timestamp": datetime.now().isoformat(),
                    },
                )
                for i in range(5)
            ]

            memory.search = Mock(return_value=episodes)

            # Test dry-run cleanup
            cleanup_result = memory.cleanup_episodes(
                importance_threshold=0.5, dry_run=True
            )

            # Should report what would be removed but not actually remove anything
            assert (
                cleanup_result["removed_count"] == 2
            )  # Would remove episodes 0.1, 0.2
            assert (
                cleanup_result["kept_count"] == 3
            )  # Would keep episodes 0.3, 0.4, 0.5
            assert cleanup_result["dry_run"] == True

    def test_combined_cleanup_criteria(self, mock_store):
        """Test cleanup with multiple criteria combined."""
        with patch("src.wellness_memory.memory_types.BaseStore"):
            from src.wellness_memory.memory_types import EpisodicMemory

            memory = EpisodicMemory(mock_store)

            # Mock episodes with varied characteristics
            now = datetime.now()
            episodes = [
                Mock(
                    key=f"episode_{i}",
                    value={
                        "importance": 0.1 * (i + 1),
                        "timestamp": (now - timedelta(days=i * 15)).isoformat(),
                    },
                )
                for i in range(10)  # 10 episodes with different importance and age
            ]

            memory.search = Mock(return_value=episodes)
            memory.remove_episode = Mock(return_value=True)

            # Test cleanup with combined criteria
            cleanup_result = memory.cleanup_episodes(
                importance_threshold=0.4,  # Remove low importance (< 0.4)
                max_age_days=45,  # Remove old episodes (> 45 days)
                dry_run=False,
            )

            # Should remove episodes that meet ANY of the criteria
            # Episodes 0, 1, 2 (importance < 0.4) + episodes 4, 5, 6, 7, 8, 9 (age > 45 days)
            # But some overlap, so need to check unique removals
            assert (
                cleanup_result["removed_count"] >= 3
            )  # At least the 3 low importance ones
            assert cleanup_result["criterion"] == "combined"

    def test_cleanup_statistics_reporting(self, mock_store):
        """Test detailed cleanup statistics reporting."""
        with patch("src.wellness_memory.memory_types.BaseStore"):
            from src.wellness_memory.memory_types import EpisodicMemory

            memory = EpisodicMemory(mock_store)

            # Mock episodes
            episodes = [
                Mock(
                    key=f"episode_{i}",
                    value={
                        "importance": 0.1 + (i * 0.1),
                        "timestamp": datetime.now().isoformat(),
                    },
                )
                for i in range(10)
            ]

            memory.search = Mock(return_value=episodes)
            memory.remove_episode = Mock(return_value=True)

            # Perform cleanup
            cleanup_result = memory.cleanup_episodes(
                importance_threshold=0.5, dry_run=False
            )

            # Verify statistics
            assert "removed_count" in cleanup_result
            assert "kept_count" in cleanup_result
            assert "criterion" in cleanup_result
            assert "removal_reasons" in cleanup_result
            assert "total_importance_removed" in cleanup_result
            assert "total_importance_kept" in cleanup_result

    def test_cleanup_reason_summarization(self, mock_store):
        """Test summarization of cleanup reasons."""
        with patch("src.wellness_memory.memory_types.BaseStore"):
            from src.wellness_memory.memory_types import EpisodicMemory

            memory = EpisodicMemory(mock_store)

            # Mock episodes with different characteristics for removal
            episodes = [
                Mock(
                    key="low_importance",
                    value={"importance": 0.2, "timestamp": datetime.now().isoformat()},
                ),
                Mock(
                    key="old_episode",
                    value={
                        "importance": 0.8,
                        "timestamp": (datetime.now() - timedelta(days=100)).isoformat(),
                    },
                ),
                Mock(
                    key="keep_episode",
                    value={"importance": 0.9, "timestamp": datetime.now().isoformat()},
                ),
            ]

            memory.search = Mock(return_value=episodes)
            memory.remove_episode = Mock(return_value=True)

            # Perform cleanup
            cleanup_result = memory.cleanup_episodes(
                importance_threshold=0.5, max_age_days=30, dry_run=False
            )

            # Check removal reasons
            reasons = cleanup_result["removal_reasons"]
            assert any("importance" in reason.lower() for reason in reasons)
            assert any("age" in reason.lower() for reason in reasons)

    def test_get_cleanup_statistics(self, mock_store):
        """Test getting cleanup statistics without performing cleanup."""
        with patch("src.wellness_memory.memory_types.BaseStore"):
            from src.wellness_memory.memory_types import EpisodicMemory

            memory = EpisodicMemory(mock_store)

            # Mock episodes with varied characteristics
            now = datetime.now()
            episodes = [
                Mock(
                    key=f"episode_{i}",
                    value={
                        "importance": 0.1 + (i * 0.15),
                        "timestamp": (now - timedelta(days=i * 10)).isoformat(),
                    },
                )
                for i in range(8)
            ]

            memory.search = Mock(return_value=episodes)

            # Get cleanup statistics
            stats = memory.get_cleanup_statistics()

            # Verify statistics
            assert "total_episodes" in stats
            assert "average_importance" in stats
            assert "oldest_episode_age_days" in stats
            assert "newest_episode_age_days" in stats
            assert "potential_removals" in stats

            # Check potential removals for different thresholds
            potential = stats["potential_removals"]
            assert "by_importance" in potential
            assert "by_age" in potential
            assert "by_count" in potential

    def test_scheduled_cleanup(self, mock_store):
        """Test scheduled cleanup execution."""
        with patch("src.wellness_memory.memory_types.BaseStore"):
            from src.wellness_memory.memory_types import EpisodicMemory

            memory = EpisodicMemory(mock_store)

            # Mock episodes and cleanup
            episodes = [
                Mock(
                    key=f"episode_{i}",
                    value={
                        "importance": 0.1 * (i + 1),
                        "timestamp": datetime.now().isoformat(),
                    },
                )
                for i in range(20)
            ]

            memory.search = Mock(return_value=episodes)
            memory.remove_episode = Mock(return_value=True)
            memory.get_cleanup_statistics = Mock(
                return_value={
                    "total_episodes": 20,
                    "average_importance": 0.55,
                    "potential_removals": {
                        "by_importance": 8,
                        "by_age": 5,
                        "by_count": 10,
                    },
                }
            )

            # Test scheduled cleanup with automatic thresholds
            cleanup_result = memory.scheduled_cleanup(
                auto_thresholds=True, dry_run=False
            )

            # Should perform cleanup based on automatic thresholds
            assert "removed_count" in cleanup_result
            assert cleanup_result["scheduled"] == True
            assert cleanup_result["auto_thresholds"] == True

    def test_cleanup_preservation_rules(self, mock_store):
        """Test cleanup with preservation rules (never remove certain episodes)."""
        with patch("src.wellness_memory.memory_types.BaseStore"):
            from src.wellness_memory.memory_types import EpisodicMemory

            memory = EpisodicMemory(mock_store)

            # Mock episodes with preservation flags
            episodes = [
                Mock(
                    key="preserve_this",
                    value={
                        "importance": 0.1,  # Low importance but preserved
                        "timestamp": datetime.now().isoformat(),
                        "preserve": True,
                    },
                ),
                Mock(
                    key="normal_episode",
                    value={
                        "importance": 0.1,  # Low importance, not preserved
                        "timestamp": datetime.now().isoformat(),
                        "preserve": False,
                    },
                ),
                Mock(
                    key="high_importance",
                    value={
                        "importance": 0.9,  # High importance
                        "timestamp": datetime.now().isoformat(),
                        "preserve": False,
                    },
                ),
            ]

            memory.search = Mock(return_value=episodes)
            memory.remove_episode = Mock(return_value=True)

            # Test cleanup with preservation
            cleanup_result = memory.cleanup_episodes(
                importance_threshold=0.5,
                preserve_flagged=True,  # Don't remove episodes with preserve=True
                dry_run=False,
            )

            # Should only remove the normal low-importance episode
            assert cleanup_result["removed_count"] == 1
            assert cleanup_result["preserved_count"] == 1  # The preserve=True episode

    def test_cleanup_batch_processing(self, mock_store):
        """Test cleanup with batch processing for large datasets."""
        with patch("src.wellness_memory.memory_types.BaseStore"):
            from src.wellness_memory.memory_types import EpisodicMemory

            memory = EpisodicMemory(mock_store)

            # Mock large number of episodes
            episodes = [
                Mock(
                    key=f"episode_{i}",
                    value={
                        "importance": 0.1 + (i * 0.001),
                        "timestamp": datetime.now().isoformat(),
                    },
                )
                for i in range(1000)  # 1000 episodes
            ]

            memory.search = Mock(return_value=episodes)
            memory.remove_episode = Mock(return_value=True)

            # Test batch cleanup
            cleanup_result = memory.cleanup_episodes(
                importance_threshold=0.5,
                batch_size=100,  # Process in batches of 100
                dry_run=False,
            )

            # Should handle large dataset efficiently
            assert cleanup_result["removed_count"] >= 400  # Approximately half
            assert cleanup_result["batch_processed"] == True
            assert "batches_processed" in cleanup_result

    def test_cleanup_error_handling(self, mock_store):
        """Test cleanup error handling and recovery."""
        with patch("src.wellness_memory.memory_types.BaseStore"):
            from src.wellness_memory.memory_types import EpisodicMemory

            memory = EpisodicMemory(mock_store)

            # Mock episodes with one that causes an error on removal
            episodes = [
                Mock(key="good_episode_1", value={"importance": 0.1}),
                Mock(key="bad_episode", value={"importance": 0.2}),
                Mock(key="good_episode_2", value={"importance": 0.3}),
            ]

            memory.search = Mock(return_value=episodes)

            # Mock removal that fails for bad_episode
            def mock_remove(key, **kwargs):
                if key == "bad_episode":
                    raise Exception("Removal failed")
                return True

            memory.remove_episode = Mock(side_effect=mock_remove)

            # Test cleanup with error handling
            cleanup_result = memory.cleanup_episodes(
                importance_threshold=0.5, dry_run=False, continue_on_error=True
            )

            # Should handle errors gracefully
            assert cleanup_result["removed_count"] == 2  # Only successful removals
            assert cleanup_result["errors_count"] == 1  # One error
            assert "error_details" in cleanup_result
            assert "bad_episode" in str(cleanup_result["error_details"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
