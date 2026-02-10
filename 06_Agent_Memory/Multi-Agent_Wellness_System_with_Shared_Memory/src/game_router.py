"""
Game Router Agent

The Game Router analyzes user queries and routes them to the appropriate
game specialist agent based on:
- Query content (unlockables, progression/progression, lore)
- User's selected game and progress
"""

from typing import Annotated, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel

from .game_input_flow import GameInputFlow


class AgentType(str):
    """Types of game specialist agents."""

    UNLOCKABLES = "unlockables"
    PROGRESSION = "progression"
    LORE = "lore"


class RouterDecision(BaseModel):
    """Structured output for router decision."""

    agent: str
    reasoning: str
    confidence: float


class RouterState(TypedDict):
    """State for the router graph."""

    messages: Annotated[list, add_messages]
    user_id: str
    routing_decision: RouterDecision


class GameRouterAgent:
    """Game Router for query routing and game specialist agent selection."""

    def __init__(self, game_input_flow: GameInputFlow):
        """Initialize the game router agent.

        Args:
            game_input_flow: Game input flow manager
        """
        self.game_input_flow = game_input_flow
        self.graph = self._build_graph()

    def _build_router_prompt(self, game_context: dict) -> str:
        """Build system prompt for routing with game context.

        Args:
            game_context: User's selected game dictionary

        Returns:
            System prompt string
        """
        base_prompt = """You are a Game Router that determines which game specialist agent should handle a user's query.

Available Specialists:
- unlockables_agent: Handles questions about unlocking weapons, tools, items, quests, and other discoverable content
  Examples: "how do I unlock the sword", "where can I find the key", "any secret items in this area"

- progression_agent: Handles questions about advancing through the game, solving puzzles, overcoming challenges
  Examples: "how do I solve this puzzle", "stuck on boss fight", "where do I go next"

- lore_agent: Handles questions about story, world-building, character backgrounds, and game mythology
  Examples: "who is this character", "what's the history of this place", "why did that happen"

Consider:
1. The user's current progress in the game (avoid spoilers)
2. What information they're asking for
3. Which specialist would be most helpful

Respond with structured output containing:
- agent: Which specialist to route to ("unlockables", "progression", or "lore")
- reasoning: Brief explanation of your decision
- confidence: Your confidence level (0.0 to 1.0)"""

        if game_context:
            game_name = game_context.get("game_name", "Unknown")
            base_prompt += f"\n\nSelected Game: {game_name}"
            if game_context.get("prompt"):
                base_prompt += f"\nUser's stated goal: {game_context['prompt']}"

        return base_prompt

    def _router_node(self, state: RouterState) -> dict:
        """Node that makes routing decision.

        Args:
            state: Current router state

        Returns:
            Updated state with routing decision
        """
        user_id = state["user_id"]

        game_context = self.game_input_flow.get_user_game(user_id)

        if not game_context:
            decision = RouterDecision(
                agent="progression",
                reasoning="No game selected - defaulting to progression agent for general guidance",
                confidence=0.5,
            )
        else:
            from langchain_openai import ChatOpenAI

            llm = ChatOpenAI(
                model="openai/gpt-oss-120b",
                base_url="http://192.168.1.79:8080/v1",
            )

            router_llm = llm.with_structured_output(RouterDecision)

            user_query = ""
            for msg in reversed(state["messages"]):
                if isinstance(msg, HumanMessage):
                    user_query = msg.content
                    break

            system_prompt = self._build_router_prompt(game_context)

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_query),
            ]

            decision = router_llm.invoke(messages)

        print(f"[GameRouter] Routing to: {decision.agent}")
        print(f"[GameRouter] Reasoning: {decision.reasoning}")
        print(f"[GameRouter] Confidence: {decision.confidence:.2f}")

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

        return builder.compile()

    def route_query(
        self,
        user_id: str,
        query: str,
    ) -> RouterDecision:
        """
        Route a user query to the appropriate game specialist agent.

        Args:
            user_id: User identifier
            query: User's question or request

        Returns:
            RouterDecision with selected agent and reasoning
        """
        result = self.graph.invoke(
            {
                "messages": [HumanMessage(content=query)],
                "user_id": user_id,
            },
        )

        return result["routing_decision"]


def create_game_router_agent(game_input_flow: GameInputFlow) -> GameRouterAgent:
    """
    Factory function to create a game router agent.

    Args:
        game_input_flow: Game input flow manager

    Returns:
        Configured GameRouterAgent instance
    """
    return GameRouterAgent(game_input_flow)


__all__ = ["GameRouterAgent", "create_game_router_agent", "RouterDecision"]
