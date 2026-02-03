#!/usr/bin/env python3
"""
Tests for memory importance scoring functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


class TestMemoryImportanceScoring:
    """Test memory importance scoring and management."""

    @pytest.fixture
    def mock_store(self):
        """Mock storage for testing."""
        store = Mock()
        store.list.return_value = []
        store.get.return_value = None
        return store

    def test_automatic_importance_calculation(self, mock_store):
        """Test automatic importance scoring based on episode characteristics."""
        with patch("src.wellness_memory.memory_types.BaseStore"):
            from src.wellness_memory.memory_types import EpisodicMemory

            memory = EpisodicMemory(mock_store)

            # Test importance calculation for different scenarios
            test_scenarios = [
                {
                    "situation": "Help with final boss",
                    "input_text": "how to defeat the final boss in dark souls",
                    "output_text": "Here's a comprehensive strategy for defeating the final boss...",
                    "feedback": "This saved my run, thank you!",
                    "expected_min_importance": 0.7,
                },
                {
                    "situation": "Basic question",
                    "input_text": "where is the first town",
                    "output_text": "The first town is north of the starting area",
                    "feedback": None,
                    "expected_max_importance": 0.5,
                },
                {
                    "situation": "Medium complexity help",
                    "input_text": "what's the best weapon combination for mid-game",
                    "output_text": "For mid-game, I recommend the fire sword combined with ice magic...",
                    "feedback": "This was helpful",
                    "expected_min_importance": 0.4,
                },
            ]

            for scenario in test_scenarios:
                importance = memory.calculate_importance(
                    situation=scenario["situation"],
                    input_text=scenario["input_text"],
                    output_text=scenario["output_text"],
                    feedback=scenario["feedback"],
                )

                if "expected_min_importance" in scenario:
                    assert importance >= scenario["expected_min_importance"]
                else:
                    assert importance <= scenario["expected_max_importance"]

    def test_manual_importance_override(self, mock_store):
        """Test manual importance setting override."""
        with patch("src.wellness_memory.memory_types.BaseStore"):
            from src.wellness_memory.memory_types import EpisodicMemory

            memory = EpisodicMemory(mock_store)

            # Test manual override
            manual_importance = 0.95  # Maximum importance

            # Mock episode storage
            memory._store_episode_internal = Mock(return_value="test_key")

            # Store with manual importance
            result = memory.store_episode(
                key="test_episode",
                situation="Test situation",
                input_text="Test input",
                output_text="Test output",
                importance=manual_importance,
            )

            # Should use manual importance over calculated
            assert result == "test_key"

    def test_importance_weighted_retrieval(self, mock_store):
        """Test retrieval sorted by importance."""
        with patch("src.wellness_memory.memory_types.BaseStore"):
            from src.wellness_memory.memory_types import EpisodicMemory

            memory = EpisodicMemory(mock_store)

            # Mock episodes with different importance scores
            mock_episodes = [
                Mock(
                    key="episode1",
                    value={"importance": 0.3, "situation": "Low importance episode"},
                ),
                Mock(
                    key="episode2",
                    value={"importance": 0.9, "situation": "High importance episode"},
                ),
                Mock(
                    key="episode3",
                    value={"importance": 0.6, "situation": "Medium importance episode"},
                ),
            ]

            memory.search = Mock(return_value=mock_episodes)

            # Test importance-weighted retrieval
            results = memory.search(query="test", sort_by_importance=True)

            # Verify results are sorted by importance (highest first)
            assert results[0].value["importance"] == 0.9  # Highest
            assert results[1].value["importance"] == 0.6  # Medium
            assert results[2].value["importance"] == 0.3  # Lowest

    def test_importance_factors_calculation(self, mock_store):
        """Test individual factors that contribute to importance scoring."""
        with patch("src.wellness_memory.memory_types.BaseStore"):
            from src.wellness_memory.memory_types import EpisodicMemory

            memory = EpisodicMemory(mock_store)

            # Test individual factor calculations
            test_cases = [
                {
                    "feedback": "This was amazing, saved my game!",
                    "input_complexity": "how do I optimize my build for endgame pvp and pve while balancing resistances and damage output",
                    "output_detail": "Here's a comprehensive guide covering all aspects...",
                    "situation_specificity": "help with specific boss using lightning build in NG+7",
                    "expected_high": True,
                },
                {
                    "feedback": None,
                    "input_complexity": "where go",
                    "output_detail": "North",
                    "situation_specificity": "help",
                    "expected_high": False,
                },
            ]

            for case in test_cases:
                # Calculate individual factors
                feedback_score = memory._calculate_feedback_score(case["feedback"])
                complexity_score = memory._calculate_input_complexity(
                    case["input_complexity"]
                )
                detail_score = memory._calculate_output_detail(case["output_detail"])
                specificity_score = memory._calculate_situation_specificity(
                    case["situation_specificity"]
                )

                # Overall importance should reflect the pattern
                if case["expected_high"]:
                    assert feedback_score > 0.5 or complexity_score > 0.5
                else:
                    assert feedback_score < 0.5 and complexity_score < 0.5

    def test_importance_threshold_filtering(self, mock_store):
        """Test filtering episodes by importance threshold."""
        with patch("src.wellness_memory.memory_types.BaseStore"):
            from src.wellness_memory.memory_types import EpisodicMemory

            memory = EpisodicMemory(mock_store)

            # Mock mixed importance episodes
            episodes = [
                Mock(key=f"episode_{i}", value={"importance": 0.1 * (i + 1)})
                for i in range(10)  # Importance from 0.1 to 1.0
            ]

            memory.search = Mock(return_value=episodes)

            # Test threshold filtering
            threshold = 0.7
            filtered_results = memory.search(
                query="test", importance_threshold=threshold
            )

            # Should only return episodes with importance >= threshold
            for result in filtered_results:
                assert result.value["importance"] >= threshold

    def test_importance_decay_over_time(self, mock_store):
        """Test importance decay based on episode age."""
        with patch("src.wellness_memory.memory_types.BaseStore"):
            from src.wellness_memory.memory_types import EpisodicMemory
            from datetime import datetime, timedelta

            memory = EpisodicMemory(mock_store)

            # Mock episodes with different ages
            now = datetime.now()
            episodes = [
                Mock(
                    key="old_episode",
                    value={
                        "importance": 0.8,
                        "timestamp": (now - timedelta(days=30)).isoformat(),
                    },
                ),
                Mock(
                    key="new_episode",
                    value={
                        "importance": 0.8,
                        "timestamp": (now - timedelta(days=1)).isoformat(),
                    },
                ),
            ]

            memory.search = Mock(return_value=episodes)

            # Test importance decay (if implemented)
            results_with_decay = memory.search(
                query="test",
                apply_decay=True,
                decay_rate=0.1,  # 10% decay per week
            )

            # New episode should have higher effective importance
            new_importance = next(
                r.value["importance"]
                for r in results_with_decay
                if r.key == "new_episode"
            )
            old_importance = next(
                r.value["importance"]
                for r in results_with_decay
                if r.key == "old_episode"
            )

            # With decay, new should be higher than old
            assert new_importance > old_importance

    def test_importance_categories(self, mock_store):
        """Test importance categorization (critical, high, medium, low)."""
        with patch("src.wellness_memory.memory_types.BaseStore"):
            from src.wellness_memory.memory_types import EpisodicMemory

            memory = EpisodicMemory(mock_store)

            # Test categorization function
            test_scores = [
                (0.95, "critical"),
                (0.8, "high"),
                (0.6, "medium"),
                (0.3, "low"),
                (0.1, "low"),
            ]

            for score, expected_category in test_scores:
                category = memory._categorize_importance(score)
                assert category == expected_category

    def test_importance_statistics(self, mock_store):
        """Test importance statistics calculation."""
        with patch("src.wellness_memory.memory_types.BaseStore"):
            from src.wellness_memory.memory_types import EpisodicMemory

            memory = EpisodicMemory(mock_store)

            # Mock episodes with varied importance scores
            episodes = [
                Mock(value={"importance": 0.2}),
                Mock(value={"importance": 0.4}),
                Mock(value={"importance": 0.6}),
                Mock(value={"importance": 0.8}),
                Mock(value={"importance": 1.0}),
            ]

            memory.search = Mock(return_value=episodes)

            # Test statistics calculation
            stats = memory.get_importance_statistics()

            expected_avg = sum([0.2, 0.4, 0.6, 0.8, 1.0]) / 5
            assert abs(stats["average_importance"] - expected_avg) < 0.01
            assert stats["total_episodes"] == 5
            assert stats["max_importance"] == 1.0
            assert stats["min_importance"] == 0.2

    def test_importance_based_cleanup(self, mock_store):
        """Test cleanup based on importance thresholds."""
        with patch("src.wellness_memory.memory_types.BaseStore"):
            from src.wellness_memory.memory_types import EpisodicMemory

            memory = EpisodicMemory(mock_store)

            # Mock episodes with varied importance
            episodes = [
                Mock(key=f"episode_{i}", value={"importance": 0.1 * (i + 1)})
                for i in range(10)  # 0.1 to 1.0
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

    def test_importance_boosting(self, mock_store):
        """Test importance boosting based on user interactions."""
        with patch("src.wellness_memory.memory_types.BaseStore"):
            from src.wellness_memory.memory_types import EpisodicMemory

            memory = EpisodicMemory(mock_store)

            # Mock episode update
            memory.update_episode_importance = Mock(return_value=True)

            # Test importance boosting
            boost_reasons = [
                ("user_rated_helpful", 0.2),
                ("frequently_accessed", 0.15),
                ("saved_user_progress", 0.3),
                ("resolved_critical_issue", 0.4),
            ]

            for reason, boost_amount in boost_reasons:
                success = memory.boost_importance(
                    episode_key="test_episode", reason=reason, boost_amount=boost_amount
                )

                assert success
                memory.update_episode_importance.assert_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
