"""
Router Agent for Multi-Agent Wellness System

The Router Agent analyzes user queries and routes them to the appropriate
specialist agent based on:
- Query content (exercise, nutrition, sleep related)
- User profile context (goals, conditions, preferences)
"""

import os
from typing import Annotated, TypedDict, Literal
from enum import Enum

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from pydantic import BaseModel

from .memory_manager import MemoryManager, create_llm


class AgentType(str, Enum):
    """Types of specialist agents."""

    EXERCISE = "exercise"
    NUTRITION = "nutrition"
    SLEEP = "sleep"


class RouterDecision(BaseModel):
    """Structured output for router decision."""

    agent: Literal["exercise", "nutrition", "sleep"]
    reasoning: str
    confidence: float


class RouterState(TypedDict):
    """State for the router graph."""

    messages: Annotated[list, add_messages]
    user_id: str
    routing_decision: RouterDecision


class RouterAgent:
    """Router Agent for query routing and agent selection."""

    def __init__(self, memory_manager: MemoryManager):
        """Initialize the router agent.

        Args:
            memory_manager: Shared memory manager instance
        """
        self.memory = memory_manager
        self.llm = create_llm()
        self.graph = self._build_graph()

    def _build_router_prompt(self, user_profile: dict) -> str:
        """Build system prompt for routing with user context.

        Args:
            user_profile: User's profile dictionary

        Returns:
            System prompt string
        """
        base_prompt = """You are a Wellness Router that determines which specialist agent should handle a user's query.

Available Specialists:
- exercise_agent: Handles fitness, workouts, physical activity, movement questions
- nutrition_agent: Handles diet, meal planning, healthy eating, food questions
- sleep_agent: Handles sleep quality, insomnia, rest, recovery questions

Consider the user's profile and choose the most relevant specialist.
If multiple topics are present, prioritize based on:
1. User's primary goals
2. Recent conditions or injuries
3. Query emphasis

Respond with structured output containing:
- agent: Which specialist to route to ("exercise", "nutrition", or "sleep")
- reasoning: Brief explanation of your decision
- confidence: Your confidence level (0.0 to 1.0)"""

        if user_profile:
            profile_context = "\n\nUser Profile:\n"
            for key, value in user_profile.items():
                if isinstance(value, list):
                    profile_context += f"- {key}: {', '.join(str(v) for v in value)}\n"
                else:
                    profile_context += f"- {key}: {value}\n"
            base_prompt += profile_context

        return base_prompt

    def _router_node(self, state: RouterState) -> dict:
        """Node that makes routing decision.

        Args:
            state: Current router state

        Returns:
            Updated state with routing decision
        """
        user_id = state["user_id"]

        # Get user profile for context
        try:
            user_profile = self.memory.get_user_profile(user_id)
        except Exception:
            user_profile = {}

        # Get the latest user message
        user_query = ""
        for msg in reversed(state["messages"]):
            if isinstance(msg, HumanMessage):
                user_query = msg.content
                break

        # Build prompt with context
        system_prompt = self._build_router_prompt(user_profile)

        # Create structured output LLM
        router_llm = self.llm.with_structured_output(RouterDecision)

        # Make routing decision
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_query),
        ]

        decision = router_llm.invoke(messages)

        print(f"[Router] Routing to: {decision.agent}")
        print(f"[Router] Reasoning: {decision.reasoning}")
        print(f"[Router] Confidence: {decision.confidence:.2f}")

        return {"routing_decision": decision}

    def _build_graph(self):
        """Build the router graph.

        Returns:
            Compiled LangGraph
        """
        builder = StateGraph(RouterState)
        builder.add_node("router", self._router_node)
        builder.add_edge(START, "router")
        builder.add_edge("router", END)

        return builder.compile(
            checkpointer=self.memory.get_checkpointer(), store=self.memory.get_store()
        )

    def route_query(
        self,
        user_id: str,
        query: str,
        thread_id: str = "default_thread",
    ) -> RouterDecision:
        """
        Route a user query to the appropriate specialist agent.

        Args:
            user_id: User identifier
            query: User's question or request
            thread_id: Thread ID for conversation tracking

        Returns:
            RouterDecision with selected agent and reasoning
        """
        config = {"configurable": {"thread_id": thread_id}}

        result = self.graph.invoke(
            {
                "messages": [HumanMessage(content=query)],
                "user_id": user_id,
            },
            config,
        )

        return result["routing_decision"]

    def batch_route(self, queries: list[str], user_id: str) -> list[RouterDecision]:
        """
        Route multiple queries in batch.

        Args:
            queries: List of user queries
            user_id: User identifier

        Returns:
            List of routing decisions
        """
        results = []
        for i, query in enumerate(queries):
            thread_id = f"batch_{user_id}_{i}"
            decision = self.route_query(user_id, query, thread_id)
            results.append(decision)

        return results


def create_router_agent(memory_manager: MemoryManager) -> RouterAgent:
    """
    Factory function to create a router agent.

    Args:
        memory_manager: Shared memory manager instance

    Returns:
        Configured RouterAgent instance
    """
    return RouterAgent(memory_manager)
