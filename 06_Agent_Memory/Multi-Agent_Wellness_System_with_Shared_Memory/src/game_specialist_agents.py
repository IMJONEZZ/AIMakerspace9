"""
Game Specialist Agents

This module implements specialist agents for video game assistance:
- UnlockablesAgent: Helps unlock weapons, tools, items, quests
- ProgressionAgent: Helps with game progression (leveling up, puzzles)
- LoreAgent: Handles story and world-building questions

All agents use:
- GameInputFlow to access the selected game
- UserGameProgress for progress-aware spoiler control
- GameKnowledgeBase for retrieving walkthrough/lore information
"""

from typing import Optional, List

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from .game_input_flow import GameInputFlow
from .user_game_progress import UserGameProgress, PROGRESS_MARKERS
from .game_knowledge_base import GameKnowledgeBase


class BaseGameSpecialistAgent:
    """Base class for all game specialist agents."""

    def __init__(
        self,
        agent_name: str,
        system_prompt: str,
        game_input_flow: GameInputFlow,
        user_progress: UserGameProgress,
        knowledge_base: GameKnowledgeBase,
    ):
        """Initialize base game specialist agent.

        Args:
            agent_name: Name of the agent
            system_prompt: System prompt for this specialist
            game_input_flow: Game input flow manager
            user_progress: User progress tracker
            knowledge_base: Game knowledge base
        """
        self.agent_name = agent_name
        self.system_prompt = system_prompt
        self.game_input_flow = game_input_flow
        self.user_progress = user_progress
        self.knowledge_base = knowledge_base

    def _get_game_context(self, user_id: str) -> Optional[dict]:
        """Get the selected game for a user.

        Args:
            user_id: User identifier

        Returns:
            Dictionary with game_name and prompt, or None if no game selected
        """
        return self.game_input_flow.get_user_game(user_id)

    def _get_user_progress(self, user_id: str, game_name: str) -> Optional[str]:
        """Get user's progress in a game.

        Args:
            user_id: User identifier
            game_name: Name of the game

        Returns:
            Progress marker, or None if not found
        """
        return self.user_progress.get_progress(user_id, game_name)

    def _search_knowledge_base(
        self,
        query: str,
        game_name: str,
        progress_marker: Optional[str] = None,
        content_types: Optional[List[str]] = None,
    ) -> List[dict]:
        """Search the knowledge base with spoiler-aware filtering.

        Args:
            query: Search query
            game_name: Name of the game
            progress_marker: User's current progress marker for spoiler control
            content_types: Optional filter for content types

        Returns:
            List of search results
        """
        if progress_marker is None:
            progress_marker = "intro/tutorial"

        return self.knowledge_base.search_game_knowledge(
            query=query,
            game_name=game_name,
            avoid_spoilers=True,
            user_progress_marker=progress_marker,
            content_types=content_types,
            limit=3,
        )

    def handle_query(self, user_id: str, query: str) -> tuple[str, bool]:
        """Handle a user query.

        Args:
            user_id: User identifier
            query: User's question or request

        Returns:
            Tuple of (response_text, success)
        """
        try:
            game_context = self._get_game_context(user_id)

            if not game_context:
                return (
                    "I don't have a selected game to help with. Please select a game first.",
                    False,
                )

            game_name = game_context["game_name"]
            progress_marker = self._get_user_progress(user_id, game_name)

            if not progress_marker:
                progress_marker = "intro/tutorial"

            search_results = self._search_knowledge_base(
                query, game_name, progress_marker
            )

            context_parts = [f"Game: {game_name}"]
            context_parts.append(f"Your Progress: {progress_marker}")
            context_parts.append("")

            if search_results:
                context_parts.append("Relevant Information from Knowledge Base:")
                for i, result in enumerate(search_results):
                    text = result.get("text", "")[:300]
                    context_parts.append(f"{i + 1}. {text}...")
                context_parts.append("")
            else:
                context_parts.append("No relevant information found in knowledge base.")
                context_parts.append("")

            full_system_prompt = f"""{self.system_prompt}

{"".join(context_parts)}

Use this information to provide helpful, spoiler-free assistance."""

            from langchain_openai import ChatOpenAI

            llm = ChatOpenAI(
                model="glm-4.7",
                base_url="http://192.168.1.79:8080/v1",
                api_key="dummy",
            )

            messages = [
                SystemMessage(content=full_system_prompt),
                HumanMessage(content=query),
            ]

            response = llm.invoke(messages)
            print(f"[{self.agent_name}] Generated response for user: {user_id}")

            return response.content, True

        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            print(f"[{self.agent_name}] Error: {e}")
            return error_msg, False


class UnlockablesAgent(BaseGameSpecialistAgent):
    """Unlockables Specialist Agent - helps unlock weapons, tools, items, quests."""

    def __init__(
        self,
        game_input_flow: GameInputFlow,
        user_progress: UserGameProgress,
        knowledge_base: GameKnowledgeBase,
    ):
        """Initialize unlockables agent."""
        system_prompt = """You are an Unlockables Specialist helping players discover how to unlock weapons, tools, items, quests, and other unlockable content in video games.

Your expertise includes:
- Finding unlock conditions for weapons and gear
- Locating hidden items and secrets
- Completing prerequisites for quests
- Unlocking new areas or abilities
- Discovering optional content

CRITICAL SPOILER RULES:
- NEVER reveal information beyond the user's current progress marker
- If a weapon/item unlocks AFTER their progress, suggest they focus on current content instead
- Don't mention endgame or post-game unlockables to early/mid-game players
- Be vague about story-related unlocks (e.g., "you'll unlock this naturally as you progress")

Always consider:
- User's current progress in the game
- Whether unlockables are accessible at their stage
- Alternative options if something is locked behind progress

Be helpful but respect spoiler boundaries. If you can't provide specific help due to spoilers, explain why and offer general guidance."""

        super().__init__(
            agent_name="UnlockablesAgent",
            system_prompt=system_prompt,
            game_input_flow=game_input_flow,
            user_progress=user_progress,
            knowledge_base=knowledge_base,
        )


class ProgressionAgent(BaseGameSpecialistAgent):
    """Progression Specialist Agent - helps with game progression and puzzles."""

    def __init__(
        self,
        game_input_flow: GameInputFlow,
        user_progress: UserGameProgress,
        knowledge_base: GameKnowledgeBase,
    ):
        """Initialize progression agent."""
        system_prompt = """You are a Progression Specialist helping players advance through video games, solve puzzles, and overcome challenges.

Your expertise includes:
- Leveling up and character progression
- Solving puzzles and riddles
- Navigating maps and finding objectives
- Overcoming difficult bosses or encounters
- Understanding game mechanics and systems

CRITICAL SPOILER RULES:
- NEVER reveal story events or plot points beyond the user's progress
- Don't mention later areas, characters, or twists they haven't reached
- Avoid spoilers about boss identities or story revelations
- If help requires revealing future content, provide general guidance instead

Always consider:
- User's current progress in the game
- Whether mechanics are available at their stage
- Difficulty level and provide appropriate hints (not full solutions unless asked)
- Alternative approaches to challenges

Be patient and helpful. Provide graduated hints: start gentle, get more specific if they're struggling."""

        super().__init__(
            agent_name="ProgressionAgent",
            system_prompt=system_prompt,
            game_input_flow=game_input_flow,
            user_progress=user_progress,
            knowledge_base=knowledge_base,
        )


class LoreAgent(BaseGameSpecialistAgent):
    """Lore Specialist Agent - handles story, world-building, and character questions."""

    def __init__(
        self,
        game_input_flow: GameInputFlow,
        user_progress: UserGameProgress,
        knowledge_base: GameKnowledgeBase,
    ):
        """Initialize lore agent."""
        system_prompt = """You are a Lore Specialist helping players understand the story, world-building, and character backgrounds in video games.

Your expertise includes:
- Game lore and mythology
- Character backgrounds and motivations
- World history and geography
- Story themes and symbolism
- Connections between different story elements

CRITICAL SPOILER RULES:
- NEVER reveal story events, plot twists, or endings beyond the user's progress
- Don't mention character fates or future developments
- Avoid spoiling emotional story beats or revelations
- If explaining lore would reveal future plot points, keep it vague and focus on established facts

Always consider:
- User's current progress in the game
- What they've already experienced vs. what lies ahead
- The difference between "established lore" (already revealed) and "future plot points"
- When to say "this will be explained later" instead of spoiling

Be engaging and enrich their understanding of the world they're exploring. Deepen appreciation without spoiling surprises."""

        super().__init__(
            agent_name="LoreAgent",
            system_prompt=system_prompt,
            game_input_flow=game_input_flow,
            user_progress=user_progress,
            knowledge_base=knowledge_base,
        )


def create_unlockables_agent(
    game_input_flow: GameInputFlow,
    user_progress: UserGameProgress,
    knowledge_base: GameKnowledgeBase,
) -> UnlockablesAgent:
    """Factory function to create an unlockables agent.

    Args:
        game_input_flow: Game input flow manager
        user_progress: User progress tracker
        knowledge_base: Game knowledge base

    Returns:
        UnlockablesAgent instance
    """
    return UnlockablesAgent(game_input_flow, user_progress, knowledge_base)


def create_progression_agent(
    game_input_flow: GameInputFlow,
    user_progress: UserGameProgress,
    knowledge_base: GameKnowledgeBase,
) -> ProgressionAgent:
    """Factory function to create a progression agent.

    Args:
        game_input_flow: Game input flow manager
        user_progress: User progress tracker
        knowledge_base: Game knowledge base

    Returns:
        ProgressionAgent instance
    """
    return ProgressionAgent(game_input_flow, user_progress, knowledge_base)


def create_lore_agent(
    game_input_flow: GameInputFlow,
    user_progress: UserGameProgress,
    knowledge_base: GameKnowledgeBase,
) -> LoreAgent:
    """Factory function to create a lore agent.

    Args:
        game_input_flow: Game input flow manager
        user_progress: User progress tracker
        knowledge_base: Game knowledge base

    Returns:
        LoreAgent instance
    """
    return LoreAgent(game_input_flow, user_progress, knowledge_base)


__all__ = [
    "UnlockablesAgent",
    "ProgressionAgent",
    "LoreAgent",
    "create_unlockables_agent",
    "create_progression_agent",
    "create_lore_agent",
]
