"""Test memory importance scoring functionality."""

import pytest
from unittest.mock import Mock
from src.wellness_memory.memory_types import EpisodicMemory
from langgraph.store.base import BaseStore


class TestMemoryImportanceScoring:
    """Test memory importance scoring features."""

    def test_automatic_importance_calculation(self):
        """Test that importance is calculated automatically when not provided."""
        mock_store = Mock(spec=BaseStore)
        mock_store.search.return_value = []  # No conflicts

        memory = EpisodicMemory(mock_store)

        # Store episode without explicit importance
        resolved_key = memory.store_episode(
            key="test_episode",
            situation="User asks for detailed exercise advice",
            input="Can you give me a comprehensive workout plan for weight loss?",
            output="Here's a detailed 4-week workout plan with cardio and strength training...",
            feedback="This is excellent, very helpful!",
        )

        # Check that importance was calculated
        call_args = mock_store.put.call_args
        stored_data = call_args[0][2]
        assert "importance" in stored_data
        assert (
            stored_data["importance"] > 0.5
        )  # Should be higher due to positive feedback

    def test_feedback_based_importance(self):
        """Test importance calculation based on user feedback."""
        mock_store = Mock(spec=BaseStore)
        mock_store.search.return_value = []

        memory = EpisodicMemory(mock_store)

        # Test positive feedback
        memory.store_episode(
            key="positive_feedback",
            situation="Test situation",
            input="Test input",
            output="Test output",
            feedback="This was excellent!",
        )

        call_args = mock_store.put.call_args
        stored_data = call_args[0][2]
        positive_importance = stored_data["importance"]

        # Reset mock for next test
        mock_store.reset_mock()
        mock_store.search.return_value = []

        # Test negative feedback
        memory.store_episode(
            key="negative_feedback",
            situation="Test situation",
            input="Test input",
            output="Test output",
            feedback="This was unhelpful",
        )

        call_args = mock_store.put.call_args
        stored_data = call_args[0][2]
        negative_importance = stored_data["importance"]

        # Positive feedback should result in higher importance
        assert positive_importance > negative_importance

    def test_importance_weighting_factors(self):
        """Test that different factors affect importance scoring."""
        from src.wellness_memory.memory_types import EpisodicMemory

        # Test different scenarios
        test_cases = [
            {
                "name": "short_simple",
                "situation": "Simple question",
                "input": "Hi",
                "output": "Hello",
                "feedback": None,
                "expected_min_importance": 0.4,  # Should be lower
            },
            {
                "name": "detailed_positive",
                "situation": "Complex detailed question about specific topic",
                "input": "Can you provide a comprehensive analysis of machine learning algorithms including detailed explanations of neural networks, decision trees, and ensemble methods?",
                "output": "Here's a comprehensive overview of machine learning algorithms...",
                "feedback": "This was perfect, exactly what I needed!",
                "expected_min_importance": 0.8,  # Should be higher
            },
        ]

        for case in test_cases:
            mock_store = Mock(spec=BaseStore)
            mock_store.search.return_value = []

            memory = EpisodicMemory(mock_store)

            memory.store_episode(
                key=case["name"],
                situation=case["situation"],
                input=case["input"],
                output=case["output"],
                feedback=case["feedback"],
            )

            call_args = mock_store.put.call_args
            stored_data = call_args[0][2]
            actual_importance = stored_data["importance"]

            assert actual_importance >= case["expected_min_importance"], (
                f"{case['name']} should have importance >= {case['expected_min_importance']}"
            )

    def test_importance_based_retrieval(self):
        """Test that retrieval is sorted by importance."""
        mock_store = Mock(spec=BaseStore)

        # Mock search results with different importance scores
        mock_store.search.return_value = [
            Mock(
                key="low_importance",
                value={
                    "situation": "Low importance episode",
                    "importance": 0.2,
                    "output": "Simple response",
                },
                score=0.8,
            ),
            Mock(
                key="high_importance",
                value={
                    "situation": "High importance episode",
                    "importance": 0.9,
                    "output": "Detailed response",
                },
                score=0.7,
            ),
        ]

        memory = EpisodicMemory(mock_store)
        results = memory.find_similar("test query")

        # Should return high importance episode first
        assert len(results) == 2
        assert results[0]["importance"] == 0.9
        assert results[1]["importance"] == 0.2

    def test_manual_importance_override(self):
        """Test that manually provided importance overrides calculation."""
        mock_store = Mock(spec=BaseStore)
        mock_store.search.return_value = []

        memory = EpisodicMemory(mock_store)

        # Store with manual importance
        memory.store_episode(
            key="manual_importance",
            situation="Test situation",
            input="Test input",
            output="Test output",
            importance=0.95,  # High manual importance
        )

        call_args = mock_store.put.call_args
        stored_data = call_args[0][2]

        # Should use manual importance
        assert stored_data["importance"] == 0.95

    def test_timestamp_inclusion(self):
        """Test that timestamps are included in episodes."""
        mock_store = Mock(spec=BaseStore)
        mock_store.search.return_value = []

        memory = EpisodicMemory(mock_store)

        memory.store_episode(
            key="timestamp_test",
            situation="Test situation",
            input="Test input",
            output="Test output",
        )

        call_args = mock_store.put.call_args
        stored_data = call_args[0][2]

        # Should include timestamp
        assert "timestamp" in stored_data
        assert stored_data["timestamp"] != ""

    def test_importance_bounds(self):
        """Test that importance scores stay within valid bounds."""
        mock_store = Mock(spec=BaseStore)
        mock_store.search.return_value = []

        memory = EpisodicMemory(mock_store)

        # Store with extremely positive feedback
        memory.store_episode(
            key="bounds_test",
            situation="Test situation",
            input="Test input",
            output="Test output",
            feedback="This was absolutely perfect excellent amazing helpful wonderful!",
        )

        call_args = mock_store.put.call_args
        stored_data = call_args[0][2]

        # Should be capped at 1.0
        assert stored_data["importance"] <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
