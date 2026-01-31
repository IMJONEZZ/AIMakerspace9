"""
Cross-Agent Learning System

This module enables agents to learn from each other's successful episodes,
implementing the cross-agent learning pattern where:
- Agents can READ from all agents' episode namespaces
- Agents only WRITE to their own episode namespace
- This enables knowledge transfer while maintaining agent identity

Key Features:
- Episode storage and retrieval with semantic search
- Cross-agent episode discovery
- Episode ranking by relevance
- Episode summarization for context building
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from .memory_manager import MemoryManager, create_llm
from .memory_namespaces import (
    AGENT_EXERCISE,
    AGENT_NUTRITION,
    AGENT_SLEEP,
    get_agent_episodes_namespace,
)


class EpisodeManager:
    """Manages episode storage and retrieval for a single agent."""

    def __init__(self, memory_manager: MemoryManager, agent_name: str):
        """Initialize episode manager for a specific agent.

        Args:
            memory_manager: Shared memory manager
            agent_name: Name of the agent (e.g., AGENT_EXERCISE)
        """
        self.memory = memory_manager
        self.agent_name = agent_name

    def store_episode(
        self,
        situation: str,
        input_text: str,
        output_text: str,
        feedback: Optional[str] = None,
        success_score: float = 1.0,
    ) -> str:
        """Store a successful consultation episode.

        Args:
            situation: Description of the consultation context
            input_text: User's question or request
            output_text: Agent's response
            feedback: Optional user feedback on the interaction
            success_score: Success score (0.0 to 1.0)

        Returns:
            Episode ID
        """
        timestamp = datetime.now().isoformat()
        episode_id = f"episode_{timestamp.replace(':', '-')}"

        self.memory.store_episode(
            agent_name=self.agent_name,
            episode_id=episode_id,
            situation=situation,
            input_text=input_text,
            output_text=output_text,
            feedback=feedback,
        )

        # Also store success score
        namespace = get_agent_episodes_namespace(self.agent_name)
        try:
            episode_data = self.memory.store.get(namespace, episode_id).value
            episode_data["success_score"] = success_score
            episode_data["timestamp"] = timestamp
            self.memory.store.put(namespace, episode_id, episode_data)
        except Exception:
            pass

        return episode_id

    def get_relevant_episodes(
        self,
        query: str,
        limit: int = 3,
        min_success_score: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """Retrieve episodes relevant to a query.

        Args:
            query: Query string for semantic search
            limit: Maximum number of episodes to return
            min_success_score: Minimum success score threshold

        Returns:
            List of episode dictionaries sorted by relevance
        """
        episodes = self.memory.get_agent_episodes(
            self.agent_name, query=query, limit=limit * 2
        )

        # Filter by success score and sort
        filtered = [
            ep for ep in episodes if ep.get("success_score", 1.0) >= min_success_score
        ]

        return filtered[:limit]

    def get_all_episodes(self) -> List[Dict[str, Any]]:
        """Get all episodes for this agent.

        Returns:
            List of all episode dictionaries
        """
        return self.memory.get_agent_episodes(self.agent_name, query=None)


class CrossAgentLearner:
    """Enables cross-agent learning by allowing agents to read each other's episodes."""

    def __init__(self, memory_manager: MemoryManager):
        """Initialize cross-agent learner.

        Args:
            memory_manager: Shared memory manager
        """
        self.memory = memory_manager
        self.llm = create_llm()
        self.agents = [AGENT_EXERCISE, AGENT_NUTRITION, AGENT_SLEEP]

    def find_cross_agent_episodes(
        self,
        query: str,
        current_agent: Optional[str] = None,
        limit_per_agent: int = 2,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Find relevant episodes from other agents.

        Args:
            query: Query string for semantic search
            current_agent: Agent making the query (will be excluded)
            limit_per_agent: Max episodes per agent

        Returns:
            Dictionary mapping agent names to their relevant episodes
        """
        return self.memory.get_cross_agent_episodes(
            query=query,
            exclude_agent=current_agent,
            limit_per_agent=limit_per_agent,
        )

    def summarize_cross_agent_insights(
        self,
        query: str,
        current_agent: Optional[str] = None,
    ) -> str:
        """Generate a summary of insights from cross-agent episodes.

        Args:
            query: Query string
            current_agent: Current agent making the request

        Returns:
            Summary of relevant insights from other agents
        """
        cross_agent_episodes = self.find_cross_agent_episodes(query, current_agent)

        if not cross_agent_episodes:
            return "No relevant episodes found from other agents."

        # Build context string
        insights = []
        for agent_name, episodes in cross_agent_episodes.items():
            if not episodes:
                continue

            insights.append(f"\nFrom {agent_name}:")
            for i, ep in enumerate(episodes[:2]):  # Limit to 2 per agent
                insights.append(f"  {i + 1}. Situation: {ep.get('situation', 'N/A')}")
                insights.append(f"     Input: {ep.get('input', 'N/A')[:100]}...")
                insights.append(f"     Output: {ep.get('output', 'N/A')[:100]}...")

        # Use LLM to summarize
        summary_prompt = f"""You are analyzing cross-agent learning insights for a wellness query.

Query: {query}

Here are relevant episodes from other agents:
{"".join(insights)}

Summarize the key insights and patterns these episodes reveal that could help answer this query.
Focus on actionable advice and successful approaches. Keep it concise (3-5 sentences)."""

        try:
            response = self.llm.invoke([HumanMessage(content=summary_prompt)])
            return response.content
        except Exception as e:
            # Fallback to concatenation if LLM fails
            return f"Cross-agent insights available from {list(cross_agent_episodes.keys())}."

    def get_episode_examples(
        self,
        query: str,
        current_agent: Optional[str] = None,
    ) -> List[str]:
        """Get formatted few-shot examples from cross-agent episodes.

        Args:
            query: Query string
            current_agent: Current agent

        Returns:
            List of formatted example strings for few-shot learning
        """
        cross_agent_episodes = self.find_cross_agent_episodes(query, current_agent)

        examples = []
        for agent_name, episodes in cross_agent_episodes.items():
            for ep in episodes[:2]:  # Top 2 per agent
                example = f"""Example from {agent_name}:
User: {ep.get("input", "")}
Response: {ep.get("output", "")}"""
                examples.append(example)

        return examples

    def rank_episodes_by_relevance(
        self,
        query: str,
        episodes: List[Dict[str, Any]],
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Rank episodes by relevance to query.

        Args:
            query: Query string
            episodes: List of episode dictionaries

        Returns:
            List of (episode, score) tuples sorted by relevance
        """
        ranked = []

        for ep in episodes:
            # Combine situation and input for relevance scoring
            text_to_match = f"{ep.get('situation', '')} {ep.get('input', '')}"

            # Simple keyword-based scoring (could use semantic similarity instead)
            query_words = set(query.lower().split())
            text_words = set(text_to_match.lower().split())

            # Jaccard similarity
            intersection = query_words & text_words
            union = query_words | text_words
            similarity = len(intersection) / len(union) if union else 0.0

            # Boost by success score
            success_boost = ep.get("success_score", 1.0) * 0.3

            final_score = similarity + success_boost
            ranked.append((ep, final_score))

        # Sort by score descending
        ranked.sort(key=lambda x: x[1], reverse=True)

        return ranked

    def transfer_knowledge(
        self,
        from_agent: str,
        to_agent: str,
        query: str,
    ) -> Optional[Dict[str, Any]]:
        """Transfer a relevant episode from one agent to another.

        Args:
            from_agent: Source agent
            to_agent: Destination agent
            query: Query context

        Returns:
            Transferred episode or None if no suitable episode found
        """
        from_episodes = self.memory.get_agent_episodes(from_agent, query=query, limit=1)

        if not from_episodes:
            return None

        best_episode = from_episodes[0]

        # Store as a transferred episode in the destination agent's namespace
        timestamp = datetime.now().isoformat()
        episode_id = f"transferred_{from_agent}_{timestamp.replace(':', '-')}"

        transferred_episode = best_episode.copy()
        transferred_episode["transferred_from"] = from_agent
        transferred_episode["transferred_at"] = timestamp

        namespace = get_agent_episodes_namespace(to_agent)
        self.memory.store.put(namespace, episode_id, transferred_episode)

        return transferred_episode


class EpisodeTracker:
    """Tracks episode statistics and learning progress."""

    def __init__(self, memory_manager: MemoryManager):
        """Initialize episode tracker.

        Args:
            memory_manager: Shared memory manager
        """
        self.memory = memory_manager

    def get_episode_stats(self) -> Dict[str, Dict[str, int]]:
        """Get statistics about episodes across all agents.

        Returns:
            Dictionary with episode counts per agent
        """
        stats = {}

        for agent in [AGENT_EXERCISE, AGENT_NUTRITION, AGENT_SLEEP]:
            try:
                episodes = self.memory.get_agent_episodes(agent, query=None)
                stats[agent] = {
                    "total": len(episodes),
                    "successful": sum(
                        1 for ep in episodes if ep.get("success_score", 1.0) >= 0.7
                    ),
                    "average_success": sum(
                        ep.get("success_score", 1.0) for ep in episodes
                    )
                    / len(episodes)
                    if episodes
                    else 0.0,
                }
            except Exception:
                stats[agent] = {"total": 0, "successful": 0, "average_success": 0.0}

        return stats

    def get_learning_coverage(self) -> Dict[str, List[str]]:
        """Analyze what topics agents have learned about.

        Returns:
            Dictionary mapping agents to lists of their topic keywords
        """
        coverage = {}

        for agent in [AGENT_EXERCISE, AGENT_NUTRITION, AGENT_SLEEP]:
            try:
                episodes = self.memory.get_agent_episodes(agent, query=None)

                keywords = set()
                for ep in episodes:
                    words = (
                        ep.get("situation", "").lower().split()
                        + ep.get("input", "").lower().split()
                    )
                    keywords.update(words[:5])  # First few words

                coverage[agent] = list(keywords)[:10]
            except Exception:
                coverage[agent] = []

        return coverage


def create_episode_manager(
    memory_manager: MemoryManager, agent_name: str
) -> EpisodeManager:
    """Factory function to create an episode manager.

    Args:
        memory_manager: Shared memory manager
        agent_name: Name of the agent

    Returns:
        EpisodeManager instance
    """
    return EpisodeManager(memory_manager, agent_name)


def create_cross_agent_learner(memory_manager: MemoryManager) -> CrossAgentLearner:
    """Factory function to create a cross-agent learner.

    Args:
        memory_manager: Shared memory manager

    Returns:
        CrossAgentLearner instance
    """
    return CrossAgentLearner(memory_manager)
