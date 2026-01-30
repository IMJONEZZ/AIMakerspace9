"""Memory type implementations for the wellness agent.

This module provides classes for working with each of the 5 memory types
from the CoALA (Cognitive Architectures for Language Agents) framework.
"""

from typing import Any, Optional
from dataclasses import dataclass
from langgraph.store.base import BaseStore
from langchain_core.messages import BaseMessage, trim_messages
from langchain_openai import ChatOpenAI


@dataclass
class ShortTermMemory:
    """Short-term memory manages conversation context within a thread.

    Short-term memory is automatically handled by LangGraph's checkpointer.
    This class provides utilities for working with the message history.

    Attributes:
        messages: The list of messages in the current conversation.
    """

    messages: list[BaseMessage]

    def get_recent(self, n: int = 10) -> list[BaseMessage]:
        """Get the n most recent messages.

        Args:
            n: Number of recent messages to return.

        Returns:
            List of the n most recent messages.
        """
        return self.messages[-n:] if len(self.messages) > n else self.messages

    def trim(
        self,
        max_tokens: int = 4000,
        llm: Optional[ChatOpenAI] = None,
        include_system: bool = True,
    ) -> list[BaseMessage]:
        """Trim messages to fit within a token limit.

        Args:
            max_tokens: Maximum number of tokens to keep.
            llm: The LLM to use for token counting.
            include_system: Whether to always keep system messages.

        Returns:
            Trimmed list of messages.
        """
        if llm is None:
            llm = ChatOpenAI(model="gpt-4o-mini")

        trimmer = trim_messages(
            max_tokens=max_tokens,
            strategy="last",
            token_counter=llm,
            include_system=include_system,
            allow_partial=False,
        )
        return trimmer.invoke(self.messages)


class LongTermMemory:
    """Long-term memory stores user information across sessions.

    Long-term memory persists across different conversation threads,
    allowing the agent to remember user preferences, goals, and history.
    """

    def __init__(self, store: BaseStore, user_id: str):
        """Initialize long-term memory for a user.

        Args:
            store: The memory store to use.
            user_id: The unique identifier for the user.
        """
        self.store = store
        self.user_id = user_id
        self.profile_namespace = (user_id, "profile")
        self.preferences_namespace = (user_id, "preferences")

    def get_profile(self) -> dict[str, Any]:
        """Get the user's wellness profile.

        Returns:
            Dictionary containing the user's profile data.
        """
        items = list(self.store.search(self.profile_namespace))
        return {item.key: item.value for item in items}

    def set_profile(self, key: str, value: dict[str, Any]) -> None:
        """Set a profile attribute for the user.

        Args:
            key: The profile attribute key (e.g., "goals", "conditions").
            value: The value to store.
        """
        self.store.put(self.profile_namespace, key, value)

    def get_preferences(self) -> dict[str, Any]:
        """Get the user's preferences.

        Returns:
            Dictionary containing the user's preferences.
        """
        items = list(self.store.search(self.preferences_namespace))
        return {item.key: item.value for item in items}

    def set_preference(self, key: str, value: dict[str, Any]) -> None:
        """Set a preference for the user.

        Args:
            key: The preference key (e.g., "communication_style").
            value: The value to store.
        """
        self.store.put(self.preferences_namespace, key, value)


class SemanticMemory:
    """Semantic memory stores and retrieves facts by meaning.

    Semantic memory uses embeddings to find relevant information
    based on semantic similarity rather than exact matches.
    """

    def __init__(self, store: BaseStore, namespace: tuple[str, ...]):
        """Initialize semantic memory.

        Args:
            store: The memory store with embedding support.
            namespace: The namespace for storing facts.
        """
        self.store = store
        self.namespace = namespace

    def store_fact(self, key: str, text: str, metadata: Optional[dict] = None) -> None:
        """Store a fact in semantic memory.

        Args:
            key: Unique identifier for the fact.
            text: The text content of the fact (used for embedding).
            metadata: Optional additional metadata.
        """
        value = {"text": text}
        if metadata:
            value.update(metadata)
        self.store.put(self.namespace, key, value)

    def search(self, query: str, limit: int = 3) -> list[dict[str, Any]]:
        """Search for facts related to a query.

        Args:
            query: The search query.
            limit: Maximum number of results to return.

        Returns:
            List of relevant facts with their similarity scores.
        """
        results = self.store.search(self.namespace, query=query, limit=limit)
        return [
            {
                "key": r.key,
                "text": r.value.get("text", ""),
                "score": r.score,
                **{k: v for k, v in r.value.items() if k != "text"},
            }
            for r in results
        ]


class EpisodicMemory:
    """Episodic memory stores past experiences for few-shot learning.

    Episodic memory enables the agent to learn from past successful
    interactions and use them as examples for future responses.
    """

    def __init__(self, store: BaseStore, namespace: tuple[str, ...] = ("agent", "episodes")):
        """Initialize episodic memory.

        Args:
            store: The memory store with embedding support.
            namespace: The namespace for storing episodes.
        """
        self.store = store
        self.namespace = namespace

    def store_episode(
        self,
        key: str,
        situation: str,
        input_text: str,
        output_text: str,
        feedback: Optional[str] = None,
    ) -> None:
        """Store a successful interaction as an episode.

        Args:
            key: Unique identifier for the episode.
            situation: Description of the situation (used for semantic search).
            input_text: The user's input.
            output_text: The agent's successful response.
            feedback: Optional feedback from the user.
        """
        self.store.put(
            self.namespace,
            key,
            {
                "text": situation,  # Used for semantic search
                "situation": situation,
                "input": input_text,
                "output": output_text,
                "feedback": feedback,
            }
        )

    def find_similar(self, query: str, limit: int = 2) -> list[dict[str, Any]]:
        """Find episodes similar to the current situation.

        Args:
            query: The current user query or situation description.
            limit: Maximum number of episodes to return.

        Returns:
            List of similar episodes with their details.
        """
        results = self.store.search(self.namespace, query=query, limit=limit)
        return [
            {
                "situation": r.value.get("situation", ""),
                "input": r.value.get("input", ""),
                "output": r.value.get("output", ""),
                "feedback": r.value.get("feedback", ""),
                "score": r.score,
            }
            for r in results
        ]

    def format_as_few_shot(self, episodes: list[dict[str, Any]]) -> str:
        """Format episodes as few-shot examples for prompts.

        Args:
            episodes: List of episodes to format.

        Returns:
            Formatted string suitable for inclusion in prompts.
        """
        if not episodes:
            return "No similar past interactions found."

        examples = []
        for i, ep in enumerate(episodes, 1):
            example = f"""Example {i}:
Situation: {ep['situation']}
User: {ep['input']}
Assistant: {ep['output']}"""
            if ep.get("feedback"):
                example += f"\nFeedback: {ep['feedback']}"
            examples.append(example)

        return "\n\n".join(examples)


class ProceduralMemory:
    """Procedural memory stores and updates agent instructions.

    Procedural memory enables self-improvement by allowing the agent
    to update its own instructions based on feedback.
    """

    def __init__(
        self,
        store: BaseStore,
        namespace: tuple[str, ...] = ("agent", "instructions"),
        key: str = "wellness_assistant",
    ):
        """Initialize procedural memory.

        Args:
            store: The memory store.
            namespace: The namespace for storing instructions.
            key: The key for the agent's instructions.
        """
        self.store = store
        self.namespace = namespace
        self.key = key

    def get_instructions(self) -> tuple[str, int]:
        """Get the current instructions.

        Returns:
            Tuple of (instructions_text, version_number).
        """
        item = self.store.get(self.namespace, self.key)
        if item is None:
            return "", 0
        return item.value.get("instructions", ""), item.value.get("version", 0)

    def update_instructions(self, new_instructions: str) -> int:
        """Update the instructions.

        Args:
            new_instructions: The new instructions text.

        Returns:
            The new version number.
        """
        _, current_version = self.get_instructions()
        new_version = current_version + 1

        self.store.put(
            self.namespace,
            self.key,
            {
                "instructions": new_instructions,
                "version": new_version,
            }
        )
        return new_version

    def reflect_and_update(
        self,
        feedback: str,
        llm: Optional[ChatOpenAI] = None,
    ) -> tuple[str, int]:
        """Reflect on feedback and update instructions.

        Args:
            feedback: User feedback about the agent's performance.
            llm: The LLM to use for reflection.

        Returns:
            Tuple of (new_instructions, new_version).
        """
        if llm is None:
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

        current_instructions, _ = self.get_instructions()

        reflection_prompt = f"""You are improving an AI assistant's instructions based on user feedback.

Current Instructions:
{current_instructions}

User Feedback:
{feedback}

Based on this feedback, provide improved instructions. Keep the same general format but incorporate the feedback.
Only output the new instructions, nothing else."""

        response = llm.invoke(reflection_prompt)
        new_instructions = response.content

        new_version = self.update_instructions(new_instructions)
        return new_instructions, new_version
