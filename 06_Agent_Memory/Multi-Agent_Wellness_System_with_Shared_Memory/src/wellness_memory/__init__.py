"""Wellness Memory Agent Package.

This package implements a memory-enabled wellness assistant using LangGraph.
It demonstrates all 5 memory types from the CoALA framework:
- Short-term: Conversation history within a thread
- Long-term: User preferences stored across sessions
- Semantic: Facts retrieved by meaning
- Episodic: Learning from past experiences
- Procedural: Self-improving instructions
"""

from wellness_memory.agents import wellness_graph, create_wellness_agent
from wellness_memory.stores import create_memory_store, create_checkpointer
from wellness_memory.memory_types import (
    ShortTermMemory,
    LongTermMemory,
    SemanticMemory,
    EpisodicMemory,
    ProceduralMemory,
)
from wellness_memory.utils import trim_conversation, summarize_conversation

__all__ = [
    "wellness_graph",
    "create_wellness_agent",
    "create_memory_store",
    "create_checkpointer",
    "ShortTermMemory",
    "LongTermMemory",
    "SemanticMemory",
    "EpisodicMemory",
    "ProceduralMemory",
    "trim_conversation",
    "summarize_conversation",
]
