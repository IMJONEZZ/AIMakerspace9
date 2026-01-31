"""
Multi-Agent Wellness System - Main Entry Point

This module integrates all components of the multi-agent wellness system:
- Memory Manager (shared memory infrastructure)
- Router Agent (query routing)
- Specialist Agents (Exercise, Nutrition, Sleep)
- Cross-Agent Learning

Usage:
    from src.wellness_system import WellnessSystem

    system = WellnessSystem()
    response = system.handle_query("user_123", "I want to lose weight but I have a knee injury")
"""

from typing import Optional, Dict, Any

from .memory_manager import MemoryManager
from .router import RouterAgent, create_router_agent
from .specialist_agents import (
    ExerciseAgent,
    NutritionAgent,
    SleepAgent,
    create_exercise_agent,
    create_nutrition_agent,
    create_sleep_agent,
)
from .cross_agent_learning import EpisodeTracker


class WellnessSystem:
    """Main wellness system integrating all components."""

    def __init__(self, data_path: str = "data"):
        """Initialize the wellness system.

        Args:
            data_path: Path to data directory containing HealthWellnessGuide.txt
        """
        # Initialize memory manager
        self.memory = MemoryManager(data_path=data_path)

        # Load knowledge base
        print("Loading wellness knowledge base...")
        self.memory.load_knowledge_base()
        print(f"Knowledge base loaded successfully!")

        # Initialize agents
        self.router = create_router_agent(self.memory)
        self.exercise_agent = create_exercise_agent(self.memory)
        self.nutrition_agent = create_nutrition_agent(self.memory)
        self.sleep_agent = create_sleep_agent(self.memory)

        # Episode tracker for statistics
        self.tracker = EpisodeTracker(self.memory)

        # Agent mapping
        self.agent_map = {
            "exercise": self.exercise_agent,
            "nutrition": self.nutrition_agent,
            "sleep": self.sleep_agent,
        }

    def handle_query(
        self,
        user_id: str,
        query: str,
        thread_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Handle a user query through the full multi-agent pipeline.

        Args:
            user_id: User identifier
            query: User's question or request
            thread_id: Optional thread ID for conversation tracking

        Returns:
            Dictionary with response and metadata
        """
        # Step 1: Route the query
        routing_decision = self.router.route_query(user_id, query)

        # Step 2: Get the appropriate specialist agent
        agent = self.agent_map.get(routing_decision.decision)
        if not agent:
            raise ValueError(f"Unknown agent: {routing_decision.decision}")

        # Step 3: Handle the query with the specialist
        response, success = agent.handle_query(user_id, query, thread_id)

        return {
            "response": response.content,
            "agent_used": routing_decision.decision,
            "routing_reasoning": routing_decision.reasoning,
            "confidence": routing_decision.confidence,
            "success": success,
        }

    def multi_turn_conversation(
        self,
        user_id: str,
        queries: list[str],
    ) -> list[Dict[str, Any]]:
        """
        Handle a multi-turn conversation.

        Args:
            user_id: User identifier
            queries: List of questions in order

        Returns:
            List of responses for each query
        """
        responses = []
        thread_id = f"conversation_{user_id}"

        for i, query in enumerate(queries):
            print(f"\n--- Turn {i + 1} ---")
            print(f"User: {query}")

            result = self.handle_query(user_id, query, thread_id)

            print(f"Agent: {result['agent_used']}")
            print(f"Response: {result['response'][:200]}...")

            responses.append(result)

        return responses

    def get_system_stats(self) -> Dict[str, Any]:
        """Get statistics about the system's memory and learning.

        Returns:
            Dictionary with system statistics
        """
        memory_stats = self.memory.list_all_memories()
        episode_stats = self.tracker.get_episode_stats()
        learning_coverage = self.tracker.get_learning_coverage()

        return {
            "memory": memory_stats,
            "episodes": episode_stats,
            "coverage": learning_coverage,
        }

    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get a user's profile.

        Args:
            user_id: User identifier

        Returns:
            Dictionary with user profile data
        """
        return self.memory.get_user_profile(user_id)

    def set_user_profile(
        self,
        user_id: str,
        profile_data: Dict[str, Any],
    ) -> None:
        """Set/update a user's profile.

        Args:
            user_id: User identifier
            profile_data: Dictionary of profile fields to set/update
        """
        self.memory.store_user_profile(user_id, profile_data)

    def demo_cross_agent_learning(self) -> Dict[str, Any]:
        """
        Demonstrate cross-agent learning by showing how agents benefit from each other's episodes.

        Returns:
            Dictionary with demonstration results
        """
        print("\n=== Cross-Agent Learning Demo ===\n")

        # Create a test user with a knee injury
        test_user = "demo_user_1"
        self.set_user_profile(
            test_user,
            {
                "name": "Demo User",
                "goals": ["lose weight"],
                "conditions": ["knee injury"],
            },
        )

        # Step 1: Exercise agent handles a query about exercise with knee injury
        print("Step 1: Querying Exercise Agent...")
        response1 = self.handle_query(
            test_user,
            "I want to lose weight but I have a knee injury. What exercises can I do?",
        )
        print(f"Exercise Agent Response: {response1['response'][:150]}...")

        # Step 2: Query nutrition agent - it should be aware of the knee injury context
        print("\nStep 2: Querying Nutrition Agent...")
        response2 = self.handle_query(
            test_user,
            "What should I eat to support my weight loss goals?",
        )
        print(f"Nutrition Agent Response: {response2['response'][:150]}...")

        # Step 3: Check episode statistics
        stats = self.get_system_stats()

        return {
            "exercise_response": response1,
            "nutrition_response": response2,
            "stats": stats,
        }


def create_wellness_system(data_path: str = "data") -> WellnessSystem:
    """
    Factory function to create a wellness system.

    Args:
        data_path: Path to data directory

    Returns:
        WellnessSystem instance
    """
    return WellnessSystem(data_path)
