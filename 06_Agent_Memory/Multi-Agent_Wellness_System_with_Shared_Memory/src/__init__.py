"""Multi-Agent Wellness System with Shared Memory."""

from .memory_manager import MemoryManager, create_llm
from .memory_namespaces import (
    AGENT_EXERCISE,
    AGENT_NUTRITION,
    AGENT_SLEEP,
    get_user_profile_namespace,
    get_wellness_knowledge_namespace,
    get_agent_instructions_namespace,
    get_agent_episodes_namespace,
)
from .router import RouterAgent, create_router_agent
from .specialist_agents import (
    ExerciseAgent,
    NutritionAgent,
    SleepAgent,
    create_exercise_agent,
    create_nutrition_agent,
    create_sleep_agent,
)
from .cross_agent_learning import (
    EpisodeManager,
    CrossAgentLearner,
    EpisodeTracker,
    create_episode_manager,
    create_cross_agent_learner,
)
from .wellness_system import WellnessSystem, create_wellness_system

__all__ = [
    "MemoryManager",
    "create_llm",
    "AGENT_EXERCISE",
    "AGENT_NUTRITION",
    "AGENT_SLEEP",
    "get_user_profile_namespace",
    "get_wellness_knowledge_namespace",
    "get_agent_instructions_namespace",
    "get_agent_episodes_namespace",
    "RouterAgent",
    "create_router_agent",
    "ExerciseAgent",
    "NutritionAgent",
    "SleepAgent",
    "create_exercise_agent",
    "create_nutrition_agent",
    "create_sleep_agent",
    "EpisodeManager",
    "CrossAgentLearner",
    "EpisodeTracker",
    "create_episode_manager",
    "create_cross_agent_learner",
    "WellnessSystem",
    "create_wellness_system",
]
