"""
Core Shared Memory Infrastructure

This module provides the central memory management system for the multi-agent
wellness application, including:
- InMemoryStore initialization with semantic search capabilities
- User profile management utilities
- Knowledge base loading and indexing
- Episode storage and retrieval
"""

import os
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path

from langgraph.store.memory import InMemoryStore
from langgraph.store.base import BaseStore
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .memory_namespaces import (
    get_user_profile_namespace,
    get_wellness_knowledge_namespace,
    get_agent_instructions_namespace,
    get_agent_episodes_namespace,
    AGENT_EXERCISE,
    AGENT_NUTRITION,
    AGENT_SLEEP,
)


class MemoryManager:
    """Central memory management system for multi-agent wellness application."""

    def __init__(
        self,
        embeddings_model: Optional[str] = None,
        embedding_dim: int = 1536,
        data_path: str = "data",
    ):
        """
        Initialize the memory manager.

        Args:
            embeddings_model: Model name for embeddings (uses local endpoint by default)
            embedding_dim: Dimension of embedding vectors
            data_path: Path to data directory containing HealthWellnessGuide.txt
        """
        self.data_path = Path(data_path)

        # Initialize embeddings model (using local endpoint)
        if embeddings_model is None:
            embeddings_model = "text-embedding-nomic-embed-text-v2-moe"

        self.embeddings = OpenAIEmbeddings(
            model=embeddings_model,
            base_url=os.environ.get("OPENAI_BASE_URL", "http://192.168.1.79:8080/v1"),
            check_embedding_ctx_length=False,
        )

        # Initialize store with semantic search
        self.store: InMemoryStore = InMemoryStore(
            index={"embed": self.embeddings, "dims": embedding_dim}
        )

        # Checkpoint store for short-term memory
        from langgraph.checkpoint.memory import MemorySaver

        self.checkpointer = MemorySaver()

        # Knowledge base loaded flag
        self._knowledge_loaded = False

    def load_knowledge_base(self, file_path: Optional[str] = None) -> int:
        """
        Load wellness knowledge base from text file into semantic memory.

        Args:
            file_path: Path to the wellness guide. Defaults to data/HealthWellnessGuide.txt

        Returns:
            Number of chunks loaded
        """
        if file_path is None:
            file_path = str(self.data_path / "HealthWellnessGuide.txt")

        if not Path(file_path).exists():
            raise FileNotFoundError(f"Wellness guide not found at {file_path}")

        # Load and chunk the document
        loader = TextLoader(file_path)
        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, chunk_overlap=100
        )
        chunks = text_splitter.split_documents(documents)

        # Store chunks in semantic memory
        namespace = get_wellness_knowledge_namespace()
        for i, chunk in enumerate(chunks):
            self.store.put(
                namespace,
                f"chunk_{i}",
                {"text": chunk.page_content, "source": str(file_path)},
            )

        self._knowledge_loaded = True
        return len(chunks)

    def search_knowledge_base(self, query: str, limit: int = 3) -> List[Any]:
        """
        Search the wellness knowledge base semantically.

        Args:
            query: Query string
            limit: Maximum number of results to return

        Returns:
            List of search results with text and scores
        """
        if not self._knowledge_loaded:
            raise RuntimeError(
                "Knowledge base not loaded. Call load_knowledge_base() first."
            )

        namespace = get_wellness_knowledge_namespace()
        results = self.store.search(namespace, query=query, limit=limit)
        return list(results)

    def store_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> None:
        """
        Store/update user profile information.

        Args:
            user_id: Unique user identifier
            profile_data: Dictionary containing profile fields (name, goals, conditions, etc.)
        """
        namespace = get_user_profile_namespace(user_id)
        for key, value in profile_data.items():
            self.store.put(namespace, key, {"value": value})

    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve complete user profile.

        Args:
            user_id: Unique user identifier

        Returns:
            Dictionary of profile data
        """
        namespace = get_user_profile_namespace(user_id)
        items = list(self.store.search(namespace))
        return {item.key: item.value.get("value") for item in items}

    def store_episode(
        self,
        agent_name: str,
        episode_id: str,
        situation: str,
        input_text: str,
        output_text: str,
        feedback: Optional[str] = None,
    ) -> None:
        """
        Store a successful consultation episode.

        Args:
            agent_name: Name of the agent (e.g., AGENT_EXERCISE)
            episode_id: Unique identifier for this episode
            situation: Description of the consultation situation
            input_text: User's input/question
            output_text: Agent's response
            feedback: Optional user feedback on the interaction
        """
        namespace = get_agent_episodes_namespace(agent_name)
        episode_data = {
            "text": situation,  # For semantic search
            "situation": situation,
            "input": input_text,
            "output": output_text,
        }
        if feedback:
            episode_data["feedback"] = feedback

        self.store.put(namespace, episode_id, episode_data)

    def get_agent_episodes(
        self,
        agent_name: str,
        query: Optional[str] = None,
        limit: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve episodes for an agent.

        Args:
            agent_name: Name of the agent
            query: Optional query for semantic search. If None, returns all episodes.
            limit: Maximum number of results

        Returns:
            List of episode data dictionaries
        """
        namespace = get_agent_episodes_namespace(agent_name)

        if query:
            results = self.store.search(namespace, query=query, limit=limit)
        else:
            results = list(self.store.search(namespace))

        return [item.value for item in results]

    def get_cross_agent_episodes(
        self,
        query: str,
        exclude_agent: Optional[str] = None,
        limit_per_agent: int = 1,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Retrieve episodes from all agents for cross-agent learning.

        Args:
            query: Query string for semantic search
            exclude_agent: Agent to exclude from results (e.g., current agent)
            limit_per_agent: Max episodes per agent

        Returns:
            Dictionary mapping agent names to their relevant episodes
        """
        agents = [AGENT_EXERCISE, AGENT_NUTRITION, AGENT_SLEEP]
        if exclude_agent:
            agents = [a for a in agents if a != exclude_agent]

        results = {}
        for agent in agents:
            try:
                episodes = self.get_agent_episodes(
                    agent, query=query, limit=limit_per_agent
                )
                if episodes:
                    results[agent] = episodes
            except Exception:
                pass

        return results

    def store_agent_instructions(
        self,
        agent_name: str,
        instructions: str,
        version: int = 1,
    ) -> None:
        """
        Store/update agent instructions (procedural memory).

        Args:
            agent_name: Name of the agent
            instructions: Instructions text
            version: Version number for tracking updates
        """
        namespace = get_agent_instructions_namespace(agent_name)
        self.store.put(
            namespace,
            "wellness_assistant",
            {"instructions": instructions, "version": version},
        )

    def get_agent_instructions(self, agent_name: str) -> Tuple[Optional[str], int]:
        """
        Retrieve agent instructions.

        Args:
            agent_name: Name of the agent

        Returns:
            Tuple of (instructions_text, version_number)
        """
        namespace = get_agent_instructions_namespace(agent_name)
        try:
            item = self.store.get(namespace, "wellness_assistant")
            if item is not None:
                return (item.value["instructions"], item.value["version"])
        except Exception:
            pass
        return (None, 0)

    def get_store(self) -> BaseStore:
        """Get the underlying InMemoryStore instance."""
        return self.store

    def get_checkpointer(self):
        """Get the checkpointer for short-term memory."""
        return self.checkpointer

    def list_all_memories(self) -> Dict[str, int]:
        """
        Get overview of all stored memories for dashboard/debugging.

        Returns:
            Dictionary with memory statistics
        """
        stats = {
            "user_profiles": 0,
            "knowledge_chunks": 0,
            "exercise_episodes": 0,
            "nutrition_episodes": 0,
            "sleep_episodes": 0,
        }

        # Count knowledge chunks
        try:
            stats["knowledge_chunks"] = len(
                list(self.store.search(get_wellness_knowledge_namespace()))
            )
        except Exception:
            pass

        # Count episodes per agent
        for agent in [AGENT_EXERCISE, AGENT_NUTRITION, AGENT_SLEEP]:
            try:
                episodes = len(
                    list(self.store.search(get_agent_episodes_namespace(agent)))
                )
                stats[f"{agent}_episodes"] = episodes
            except Exception:
                pass

        # Count user profiles (prefix-based estimate)
        all_items = list(self.store.search(()))
        profile_count = sum(
            1
            for item in all_items
            if len(item.namespace) >= 2 and item.namespace[1] == "profile"
        )
        stats["user_profiles"] = profile_count

        return stats


def create_llm() -> ChatOpenAI:
    """
    Create a standard LLM instance for the wellness agents.

    Returns:
        ChatOpenAI instance configured for local endpoint
    """
    return ChatOpenAI(
        model=os.environ.get("OPENAI_MODEL", "openai/gpt-oss-120b"),
        base_url=os.environ.get("OPENAI_BASE_URL", "http://192.168.1.79:8080/v1/"),
        temperature=0,
    )
