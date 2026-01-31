"""
Specialist Agents for Multi-Agent Wellness System

This module implements the three specialist agents:
- ExerciseAgent: Handles fitness, workouts, and physical activity
- NutritionAgent: Handles diet, meal planning, and healthy eating
- SleepAgent: Handles sleep quality, insomnia, and rest

All agents share a common base class that provides:
- Memory access (profile, knowledge, own episodes)
- Cross-agent learning from other agents' episodes
- Episode storage for future few-shot learning
"""

from typing import Annotated, TypedDict, Optional, List

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from .memory_manager import MemoryManager, create_llm
from .cross_agent_learning import (
    EpisodeManager,
    CrossAgentLearner,
    create_episode_manager,
    create_cross_agent_learner,
)
from .memory_namespaces import (
    AGENT_EXERCISE,
    AGENT_NUTRITION,
    AGENT_SLEEP,
)


class SpecialistAgentState(TypedDict):
    """State for specialist agent graphs."""

    messages: Annotated[list, add_messages]
    user_id: str
    response_generated: bool


class BaseSpecialistAgent:
    """Base class for all specialist wellness agents."""

    def __init__(
        self,
        memory_manager: MemoryManager,
        agent_name: str,
        system_prompt: str,
    ):
        """Initialize base specialist agent.

        Args:
            memory_manager: Shared memory manager
            agent_name: Name of the agent (e.g., AGENT_EXERCISE)
            system_prompt: System prompt for this specialist
        """
        self.memory = memory_manager
        self.agent_name = agent_name
        self.llm = create_llm()
        self.system_prompt = system_prompt

        # Episode and cross-agent learning managers
        self.episode_manager = create_episode_manager(memory_manager, agent_name)
        self.cross_agent_learner = create_cross_agent_learner(memory_manager)

        # Build the graph
        self.graph = self._build_graph()

    def _build_context_from_memory(self, user_id: str, query: str) -> str:
        """Build context from memory for the agent.

        Args:
            user_id: User identifier
            query: Current query

        Returns:
            Context string with relevant memories
        """
        context_parts = []

        # 1. User profile
        try:
            profile = self.memory.get_user_profile(user_id)
            if profile:
                context_parts.append("User Profile:")
                for key, value in profile.items():
                    if isinstance(value, list):
                        context_parts.append(
                            f"- {key}: {', '.join(str(v) for v in value)}"
                        )
                    else:
                        context_parts.append(f"- {key}: {value}")
                context_parts.append("")
        except Exception:
            pass

        # 2. Own episodes (few-shot learning)
        try:
            own_episodes = self.episode_manager.get_relevant_episodes(query, limit=2)
            if own_episodes:
                context_parts.append("Previous Successful Interactions:")
                for i, ep in enumerate(own_episodes):
                    context_parts.append(
                        f"{i + 1}. Situation: {ep.get('situation', 'N/A')}"
                    )
                    context_parts.append(f"   User: {ep.get('input', 'N/A')[:80]}...")
                    context_parts.append(
                        f"   Response: {ep.get('output', 'N/A')[:80]}..."
                    )
                context_parts.append("")
        except Exception:
            pass

        # 3. Wellness knowledge base
        try:
            knowledge_results = self.memory.search_knowledge_base(query, limit=2)
            if knowledge_results:
                context_parts.append("Relevant Knowledge:")
                for i, result in enumerate(knowledge_results):
                    text = result.value.get("text", "")[:200]
                    context_parts.append(f"{i + 1}. {text}...")
                context_parts.append("")
        except Exception:
            pass

        # 4. Cross-agent insights
        try:
            cross_agent_insights = (
                self.cross_agent_learner.summarize_cross_agent_insights(
                    query, current_agent=self.agent_name
                )
            )
            if (
                cross_agent_insights
                and "No relevant episodes" not in cross_agent_insights
            ):
                context_parts.append("Insights from Other Specialists:")
                context_parts.append(cross_agent_insights)
                context_parts.append("")
        except Exception:
            pass

        return "\n".join(context_parts)

    def _agent_node(self, state: SpecialistAgentState) -> dict:
        """Node that processes the query and generates a response.

        Args:
            state: Current agent state

        Returns:
            Updated state with response
        """
        user_id = state["user_id"]

        # Get the latest user message
        user_query = ""
        for msg in reversed(state["messages"]):
            if isinstance(msg, HumanMessage):
                user_query = msg.content
                break

        # Build context from memory
        memory_context = self._build_context_from_memory(user_id, user_query)

        # Build full system prompt
        full_system_prompt = f"""{self.system_prompt}

{memory_context if memory_context else "No additional context available."}

Use this information to provide personalized and well-informed advice."""

        # Generate response
        messages = [
            SystemMessage(content=full_system_prompt),
            *state["messages"],
        ]

        response = self.llm.invoke(messages)

        print(f"[{self.agent_name}] Generated response for user: {user_id}")

        return {
            "messages": [response],
            "response_generated": True,
        }

    def _build_graph(self):
        """Build the agent's LangGraph.

        Returns:
            Compiled graph
        """
        builder = StateGraph(SpecialistAgentState)
        builder.add_node("agent", self._agent_node)
        builder.add_edge(START, "agent")
        builder.add_edge("agent", END)

        return builder.compile(
            checkpointer=self.memory.get_checkpointer(), store=self.memory.get_store()
        )

    def handle_query(
        self,
        user_id: str,
        query: str,
        thread_id: Optional[str] = None,
    ) -> tuple[AIMessage, bool]:
        """Handle a user query.

        Args:
            user_id: User identifier
            query: User's question or request
            thread_id: Thread ID for conversation tracking

        Returns:
            Tuple of (response_message, success)
        """
        if thread_id is None:
            thread_id = f"{self.agent_name}_{user_id}"

        config = {"configurable": {"thread_id": thread_id}}

        try:
            result = self.graph.invoke(
                {
                    "messages": [HumanMessage(content=query)],
                    "user_id": user_id,
                },
                config,
            )

            response = result["messages"][-1]

            # Store episode for future learning
            self.episode_manager.store_episode(
                situation=f"User query about wellness topic",
                input_text=query,
                output_text=response.content,
            )

            return response, True

        except Exception as e:
            error_msg = AIMessage(content=f"Sorry, I encountered an error: {str(e)}")
            return error_msg, False


class ExerciseAgent(BaseSpecialistAgent):
    """Exercise Specialist Agent - handles fitness and physical activity."""

    def __init__(self, memory_manager: MemoryManager):
        """Initialize exercise agent."""
        system_prompt = """You are an Exercise Specialist helping users with fitness, workouts, and physical activity.

Your expertise includes:
- Exercise routines for different fitness levels
- Workout planning and progression
- Injury-appropriate exercises
- Physical activity recommendations
- Recovery and stretching

Always consider:
- User's current fitness level (if known)
- Any injuries or physical limitations
- Goals (weight loss, muscle gain, general fitness)
- Available equipment and time

Be encouraging but realistic. Prioritize safety over intensity."""
        super().__init__(memory_manager, AGENT_EXERCISE, system_prompt)


class NutritionAgent(BaseSpecialistAgent):
    """Nutrition Specialist Agent - handles diet and healthy eating."""

    def __init__(self, memory_manager: MemoryManager):
        """Initialize nutrition agent."""
        system_prompt = """You are a Nutrition Specialist helping users with diet, meal planning, and healthy eating.

Your expertise includes:
- Balanced nutrition principles
- Meal planning for different goals (weight loss, muscle gain, general health)
- Dietary restrictions and allergies
- Healthy food choices and substitutions
- Hydration recommendations

Always consider:
- User's dietary restrictions or allergies (if known)
- Goals and preferences
- Budget constraints (if mentioned)
- Cultural food preferences

Be non-judgmental and focus on sustainable, healthy choices rather than restrictive diets."""
        super().__init__(memory_manager, AGENT_NUTRITION, system_prompt)


class SleepAgent(BaseSpecialistAgent):
    """Sleep Specialist Agent - handles sleep quality and rest."""

    def __init__(self, memory_manager: MemoryManager):
        """Initialize sleep agent."""
        system_prompt = """You are a Sleep Specialist helping users with sleep quality, insomnia, and rest optimization.

Your expertise includes:
- Sleep hygiene best practices
- Insomnia management strategies
- Sleep schedule optimization
- Rest and recovery techniques
- Dealing with sleep disruptions

Always consider:
- User's current sleep patterns (if mentioned)
- Stress levels and lifestyle factors
- Sleep environment challenges
- Medical conditions that affect sleep

Be empathetic and offer practical, evidence-based solutions."""
        super().__init__(memory_manager, AGENT_SLEEP, system_prompt)


def create_exercise_agent(memory_manager: MemoryManager) -> ExerciseAgent:
    """Factory function to create an exercise agent.

    Args:
        memory_manager: Shared memory manager

    Returns:
        ExerciseAgent instance
    """
    return ExerciseAgent(memory_manager)


def create_nutrition_agent(memory_manager: MemoryManager) -> NutritionAgent:
    """Factory function to create a nutrition agent.

    Args:
        memory_manager: Shared memory manager

    Returns:
        NutritionAgent instance
    """
    return NutritionAgent(memory_manager)


def create_sleep_agent(memory_manager: MemoryManager) -> SleepAgent:
    """Factory function to create a sleep agent.

    Args:
        memory_manager: Shared memory manager

    Returns:
        SleepAgent instance
    """
    return SleepAgent(memory_manager)
