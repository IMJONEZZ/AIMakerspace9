"""Memory store configurations for the wellness agent.

This module provides factory functions for creating memory stores
used by the wellness agent for different memory types.
"""

from typing import Optional
from langchain_openai import OpenAIEmbeddings
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore


def create_checkpointer() -> MemorySaver:
    """Create a checkpointer for short-term memory.

    The checkpointer saves graph state at each step, enabling:
    - Conversation history within a thread
    - State inspection and debugging
    - Time-travel debugging in LangGraph Studio

    Returns:
        MemorySaver: An in-memory checkpointer for development.

    Note:
        For production, consider using PostgresSaver or other
        persistent checkpointers.
    """
    return MemorySaver()


def create_memory_store(
    with_embeddings: bool = True,
    embedding_model: Optional[str] = "text-embedding-3-small",
    embedding_dims: int = 1536,
) -> InMemoryStore:
    """Create a memory store for long-term, semantic, episodic, and procedural memory.

    Args:
        with_embeddings: Whether to enable semantic search with embeddings.
        embedding_model: The OpenAI embedding model to use.
        embedding_dims: The dimension of the embedding vectors.

    Returns:
        InMemoryStore: A store configured for the specified memory types.

    Note:
        For production, consider using PostgresStore or other
        persistent stores.
    """
    if with_embeddings:
        embeddings = OpenAIEmbeddings(model=embedding_model)
        return InMemoryStore(
            index={
                "embed": embeddings,
                "dims": embedding_dims,
            }
        )
    else:
        return InMemoryStore()


def initialize_wellness_store(store: InMemoryStore) -> None:
    """Initialize the store with default wellness data.

    This function sets up:
    - Default procedural instructions for the wellness agent
    - Sample wellness knowledge for semantic memory

    Args:
        store: The memory store to initialize.
    """
    # Initialize procedural memory with default instructions
    default_instructions = """You are a Personal Wellness Assistant. Follow these guidelines:

1. Be empathetic and supportive in all interactions
2. Always consider the user's wellness profile when giving advice
3. Provide evidence-based wellness information
4. Encourage healthy habits without being preachy
5. Refer users to healthcare professionals for medical concerns

When responding:
- Use the user's name if known
- Reference their wellness goals when relevant
- Build on previous conversations when possible
- Keep responses focused and actionable"""

    store.put(
        ("agent", "instructions"),
        "wellness_assistant",
        {
            "instructions": default_instructions,
            "version": 1,
        }
    )

    # Initialize sample episodic memories
    sample_episodes = [
        {
            "situation": "User asked about starting an exercise routine with joint pain",
            "input": "I want to start exercising but my knees hurt. What should I do?",
            "output": "For knee-friendly exercise, I'd recommend starting with low-impact activities like swimming, cycling, or using an elliptical machine. These options minimize stress on your joints while still providing excellent cardiovascular benefits. Always start slowly and listen to your body. If pain persists, please consult a healthcare provider.",
            "feedback": "User found this helpful and appreciated the specific alternatives",
        },
        {
            "situation": "User struggling with sleep quality",
            "input": "I can't fall asleep at night. I've tried everything.",
            "output": "Sleep difficulties can be frustrating. Let's focus on sleep hygiene basics: 1) Keep a consistent sleep schedule, even on weekends. 2) Create a relaxing bedtime routine - try reading or gentle stretching. 3) Make your bedroom cool, dark, and quiet. 4) Avoid screens for 1-2 hours before bed. Which of these would you like to start with?",
            "feedback": "User appreciated the structured approach and actionable steps",
        },
    ]

    for i, episode in enumerate(sample_episodes):
        store.put(
            ("agent", "episodes"),
            f"episode_{i}",
            {
                "text": episode["situation"],  # Used for semantic search
                **episode,
            }
        )


# Namespace conventions for the wellness agent
NAMESPACES = {
    # User-specific namespaces (parameterized by user_id)
    "profile": lambda user_id: (user_id, "profile"),
    "preferences": lambda user_id: (user_id, "preferences"),
    "facts": lambda user_id: (user_id, "facts"),
    "wellness_history": lambda user_id: (user_id, "wellness_history"),

    # Shared namespaces
    "knowledge": ("wellness", "knowledge"),
    "instructions": ("agent", "instructions"),
    "episodes": ("agent", "episodes"),
}
