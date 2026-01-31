"""
Memory Namespace Strategy for Multi-Agent Wellness System

This module defines the memory namespace patterns used throughout the system.

NAMESPACE PATTERNS:
===================

Shared Namespaces (All Agents Can Access):
-----------------------------------------
1. User Profile: (user_id, "profile")
   - Stores user demographics, goals, conditions
   - Example: ("user_123", "profile", "name") = {"value": "Sarah"}

2. Wellness Knowledge: ("wellness", "knowledge")
   - Stores semantic knowledge base
   - Example: ("wellness", "knowledge", "chunk_5") = {"text": "...", "embedding": [...]}

Per-Agent Namespaces (Agent-Specific):
------------------------------------
3. Agent Instructions: (agent_name, "instructions")
   - Stores agent's current instructions
   - Example: ("exercise_agent", "instructions") = {"instructions": "...", "version": 1}

4. Agent Episodes: (agent_name, "episodes")
   - Stores successful consultation episodes
   - Example: ("exercise_agent", "episodes", "episode_1") = {"situation": "...", "input": "...", "output": "..."}

CROSS-AGENT LEARNING:
=====================
Agents can READ from other agents' episode namespaces but only WRITE to their own.
This enables learning while maintaining agent identity.

ACCESS CONTROL:
==============
- Read access: All agents can read shared namespaces
- Write access: Agents write to (user_id, "profile"), their own instructions and episodes
- Cross-agent read: Agents can read other agents' episodes (read-only)
"""

from typing import Tuple, List

# Namespace constants
USER_PROFILE_PREFIX = "profile"
WELLNESS_KNOWLEDGE_PREFIX = "wellness_knowledge"

# Agent names
AGENT_EXERCISE = "exercise_agent"
AGENT_NUTRITION = "nutrition_agent"
AGENT_SLEEP = "sleep_agent"

# Memory types
MEMORY_INSTRUCTIONS = "instructions"
MEMORY_EPISODES = "episodes"


def get_user_profile_namespace(user_id: str) -> Tuple[str, ...]:
    """Get namespace for user profile."""
    return (user_id, USER_PROFILE_PREFIX)


def get_wellness_knowledge_namespace() -> Tuple[str, ...]:
    """Get namespace for wellness knowledge base."""
    return ("wellness", WELLNESS_KNOWLEDGE_PREFIX)


def get_agent_instructions_namespace(agent_name: str) -> Tuple[str, ...]:
    """Get namespace for agent instructions."""
    return (agent_name, MEMORY_INSTRUCTIONS)


def get_agent_episodes_namespace(agent_name: str) -> Tuple[str, ...]:
    """Get namespace for agent episodes."""
    return (agent_name, MEMORY_EPISODES)


def get_all_shared_namespaces(user_id: str) -> List[Tuple[str, ...]]:
    """Get all shared namespaces accessible by all agents."""
    return [
        get_user_profile_namespace(user_id),
        get_wellness_knowledge_namespace(),
    ]


def get_all_agent_namespaces(agent_name: str) -> List[Tuple[str, ...]]:
    """Get all namespaces for a specific agent."""
    return [
        get_agent_instructions_namespace(agent_name),
        get_agent_episodes_namespace(agent_name),
    ]


def get_cross_agent_read_namespaces(target_agent: str) -> List[Tuple[str, ...]]:
    """
    Get namespaces an agent can read from other agents.
    Includes shared namespaces plus all episode namespaces (for cross-agent learning).
    """
    return [
        get_agent_episodes_namespace(AGENT_EXERCISE),
        get_agent_episodes_namespace(AGENT_NUTRITION),
        get_agent_episodes_namespace(AGENT_SLEEP),
    ]


# Namespace access control rules
NAMESPACE_ACCESS_RULES = {
    # Read permissions
    "read": {
        ("user_*", USER_PROFILE_PREFIX): ["all"],
        ("wellness", WELLNESS_KNOWLEDGE_PREFIX): ["all"],
        (AGENT_EXERCISE, MEMORY_EPISODES): ["all"],  # Cross-agent learning
        (AGENT_NUTRITION, MEMORY_EPISODES): ["all"],  # Cross-agent learning
        (AGENT_SLEEP, MEMORY_EPISODES): ["all"],  # Cross-agent learning
    },
    # Write permissions
    "write": {
        (AGENT_EXERCISE, MEMORY_INSTRUCTIONS): [AGENT_EXERCISE],
        (AGENT_EXERCISE, MEMORY_EPISODES): [AGENT_EXERCISE],
        (AGENT_NUTRITION, MEMORY_INSTRUCTIONS): [AGENT_NUTRITION],
        (AGENT_NUTRITION, MEMORY_EPISODES): [AGENT_NUTRITION],
        (AGENT_SLEEP, MEMORY_INSTRUCTIONS): [AGENT_SLEEP],
        (AGENT_SLEEP, MEMORY_EPISODES): [AGENT_SLEEP],
    },
}
