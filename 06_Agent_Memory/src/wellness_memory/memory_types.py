"""Memory type implementations for the wellness agent.

This module provides classes for working with each of the 5 memory types
from the CoALA (Cognitive Architectures for Language Agents) framework.
"""

from typing import Any, Optional
from dataclasses import dataclass
from langgraph.store.base import BaseStore
from langchain_core.messages import BaseMessage, trim_messages
from langchain_core.messages.utils import count_tokens_approximately
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
            token_counter=count_tokens_approximately,
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

    def __init__(
        self, store: BaseStore, namespace: tuple[str, ...] = ("agent", "episodes")
    ):
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
        importance: Optional[float] = None,
        resolve_conflicts: bool = True,
        auto_calculate_importance: bool = True,
    ) -> str:
        """Store a successful interaction as an episode.

        Args:
            key: Unique identifier for the episode.
            situation: Description of the situation (used for semantic search).
            input_text: The user's input.
            output_text: The agent's successful response.
            feedback: Optional feedback from the user.
            importance: Optional importance score (0.0-1.0).
            resolve_conflicts: Whether to detect and resolve conflicts.

        Returns:
            The actual key used for storage (may be modified for conflict resolution).
        """
        calculated_importance = importance
        if auto_calculate_importance and importance is None:
            calculated_importance = self._calculate_importance(situation, input_text, output_text, feedback)
        
        episode_data = {
            "text": situation,  # Used for semantic search
            "situation": situation,
            "input": input_text,
            "output": output_text,
            "feedback": feedback,
            "importance": calculated_importance or 0.5,  # Default importance
            "timestamp": self._get_timestamp(),
        }

        if resolve_conflicts:
            resolved_key = self._resolve_conflicts(key, episode_data)
        else:
            resolved_key = key

        self.store.put(self.namespace, resolved_key, episode_data)
        return resolved_key

    def _calculate_importance(
        self, situation: str, input_text: str, output_text: str, feedback: Optional[str]
    ) -> float:
        """Calculate importance score based on content analysis.
        
        Args:
            situation: The situation description.
            input_text: User's input.
            output_text: Agent's output.
            feedback: User feedback (if available).
            
        Returns:
            Importance score from 0.0 to 1.0.
        """
        importance = 0.5  # Base importance
        
        # Factor 1: User feedback (highest weight)
        if feedback:
            feedback_lower = feedback.lower()
            if any(word in feedback_lower for word in ["excellent", "perfect", "helpful", "great"]):
                importance += 0.3
            elif any(word in feedback_lower for word in ["good", "useful", "thanks"]):
                importance += 0.2
            elif any(word in feedback_lower for word in ["okay", "fine", "average"]):
                importance += 0.1
            elif any(word in feedback_lower for word in ["bad", "unhelpful", "wrong"]):
                importance -= 0.2
                
        # Factor 2: Input complexity (medium weight)
        input_complexity = min(len(input_text.split()) / 20.0, 1.0)  # Normalize to 0-1
        importance += input_complexity * 0.2
        
        # Factor 3: Output detail level (medium weight)
        output_detail = min(len(output_text.split()) / 30.0, 1.0)  # Normalize to 0-1
        importance += output_detail * 0.15
        
        # Factor 4: Situation specificity (low weight)
        situation_specificity = min(len(situation.split()) / 15.0, 1.0)  # Normalize to 0-1
        importance += situation_specificity * 0.1
        
        # Ensure within bounds
        return max(0.0, min(1.0, importance))

    def _get_timestamp(self) -> str:
        """Get current timestamp for episode storage."""
        from datetime import datetime
        return datetime.now().isoformat()

    def _resolve_conflicts(self, key: str, episode_data: dict[str, Any]) -> str:
        """Detect and resolve conflicts with existing episodes.
        
        Args:
            key: Proposed episode key.
            episode_data: Episode data to store.
            
        Returns:
            Resolved key (may be modified to avoid conflicts).
        """
        # Search for similar existing episodes
        similar_episodes = self.find_similar(episode_data["situation"], limit=3)
        
        if not similar_episodes:
            return key
            
        # Check for conflicts (very similar situations)
        for similar in similar_episodes:
            similarity_score = similar.get("score", 0.0)
            if similarity_score > 0.85:  # High similarity threshold
                return self._merge_episodes(key, episode_data, similar)
                
        return key

    def _merge_episodes(self, new_key: str, new_episode: dict[str, Any], existing_episode: dict[str, Any]) -> str:
        """Merge conflicting episodes based on importance and recency.
        
        Args:
            new_key: Key for the new episode.
            new_episode: New episode data.
            existing_episode: Existing episode data.
            
        Returns:
            Key for the merged episode.
        """
        # Compare importance scores
        new_importance = new_episode.get("importance", 0.5)
        existing_importance = existing_episode.get("importance", 0.5)
        
        # If new episode is more important, replace the existing one
        if new_importance > existing_importance:
            merged_key = f"{new_key}_merged"
            merged_episode = new_episode.copy()
            merged_episode["merged_from"] = existing_episode.get("situation", "")
            merged_episode["merge_reason"] = "Higher importance"
        else:
            # If existing is more important, keep it but update with new feedback if provided
            merged_key = f"{existing_episode.get('situation', 'unknown')}_updated"
            merged_episode = existing_episode.copy()
            if new_episode.get("feedback"):
                merged_episode["feedback"] = new_episode["feedback"]
                merged_episode["merge_reason"] = "Updated with new feedback"
            else:
                merged_episode["merge_reason"] = "Kept existing (higher importance)"
        
        # Store merged episode
        self.store.put(self.namespace, merged_key, merged_episode)
        
        # Remove the less important episode if they're different
        if new_importance > existing_importance:
            self._remove_episode_by_key(existing_episode.get("situation", ""))
        elif new_importance < existing_importance:
            self._remove_episode_by_key(new_key)
            
        return merged_key

    def _remove_episode_by_key(self, key: str) -> bool:
        """Remove an episode by its key.
        
        Args:
            key: Episode key to remove.
            
        Returns:
            True if removed, False if not found.
        """
        try:
            self.store.delete(self.namespace, key)
            return True
        except Exception:
            return False

    def cleanup_episodes(
        self,
        importance_threshold: float = 0.2,
        age_days: int = 30,
        max_episodes: int = 1000,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        """Clean up old or low-importance episodes.
        
        Args:
            importance_threshold: Remove episodes below this importance score.
            age_days: Remove episodes older than this many days.
            max_episodes: Keep only the most recent N episodes.
            dry_run: If True, report what would be removed without actually removing.
            
        Returns:
            Dictionary with cleanup statistics.
        """
        from datetime import datetime, timedelta
        
        # Get all episodes
        try:
            all_items = list(self.store.search(self.namespace, limit=10000))
        except Exception:
            return {
                "status": "error",
                "message": "Failed to retrieve episodes for cleanup",
                "removed_count": 0,
                "kept_count": 0,
            }
        
        cutoff_date = datetime.now() - timedelta(days=age_days)
        
        episodes_to_remove = []
        episodes_to_keep = []
        
        for item in all_items:
            episode_data = item.value
            should_remove = False
            remove_reason = []
            
            # Check importance threshold
            if episode_data.get("importance", 0.5) < importance_threshold:
                should_remove = True
                remove_reason.append("low_importance")
            
            # Check age
            timestamp_str = episode_data.get("timestamp", "")
            if timestamp_str:
                try:
                    episode_date = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    if episode_date < cutoff_date:
                        should_remove = True
                        remove_reason.append("old_age")
                except ValueError:
                    pass  # Invalid timestamp format
            
            # Check max episodes limit (sort by importance and recency)
            # This will be handled after filtering
            
            if should_remove:
                episodes_to_remove.append({
                    "key": item.key,
                    "reason": remove_reason,
                    "importance": episode_data.get("importance", 0.5),
                    "timestamp": timestamp_str,
                })
            else:
                episodes_to_keep.append(item)
        
        # Apply max_episodes limit to kept episodes
        if len(episodes_to_keep) > max_episodes:
            # Sort by importance first, then timestamp (newest first)
            episodes_to_keep.sort(key=lambda x: (
                x.value.get("importance", 0.5),
                x.value.get("timestamp", "")
            ), reverse=True)
            
            excess_episodes = episodes_to_keep[max_episodes:]
            episodes_to_keep = episodes_to_keep[:max_episodes]
            
            # Mark excess for removal
            for item in excess_episodes:
                episodes_to_remove.append({
                    "key": item.key,
                    "reason": ["max_episodes_limit"],
                    "importance": item.value.get("importance", 0.5),
                    "timestamp": item.value.get("timestamp", ""),
                })
        
        # Remove episodes if not dry run
        removed_count = 0
        if not dry_run:
            for item_to_remove in episodes_to_remove:
                try:
                    self.store.delete(self.namespace, item_to_remove["key"])
                    removed_count += 1
                except Exception:
                    pass  # Count as failed removal
        
        return {
            "status": "success",
            "removed_count": removed_count,
            "kept_count": len(episodes_to_keep),
            "total_before": len(all_items),
            "episodes_marked_for_removal": len(episodes_to_remove),
            "removal_reasons": self._summarize_removal_reasons(episodes_to_remove),
            "dry_run": dry_run,
        }

    def _summarize_removal_reasons(self, episodes_to_remove: list[dict[str, Any]]) -> dict[str, int]:
        """Summarize reasons for episode removal."""
        reasons = {}
        for episode in episodes_to_remove:
            for reason in episode.get("reason", []):
                reasons[reason] = reasons.get(reason, 0) + 1
        return reasons

    def get_cleanup_statistics(self) -> dict[str, Any]:
        """Get statistics about the current state of episodic memory.
        
        Returns:
            Dictionary with memory statistics.
        """
        try:
            all_items = list(self.store.search(self.namespace, limit=10000))
        except Exception:
            return {
                "status": "error",
                "message": "Failed to retrieve episodes for statistics",
            }
        
        if not all_items:
            return {
                "status": "success",
                "total_episodes": 0,
                "average_importance": 0.0,
                "oldest_episode": None,
                "newest_episode": None,
                "low_importance_count": 0,
                "old_episode_count": 0,
            }
        
        from datetime import datetime, timedelta
        
        # Calculate statistics
        importances = [item.value.get("importance", 0.5) for item in all_items]
        timestamps = []
        low_importance_count = 0
        old_episode_count = 0
        cutoff_date = datetime.now() - timedelta(days=30)
        
        for item in all_items:
            episode_data = item.value
            
            # Count low importance episodes
            if episode_data.get("importance", 0.5) < 0.3:
                low_importance_count += 1
            
            # Count old episodes
            timestamp_str = episode_data.get("timestamp", "")
            if timestamp_str:
                try:
                    episode_date = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    if episode_date < cutoff_date:
                        old_episode_count += 1
                    timestamps.append(episode_date)
                except ValueError:
                    pass
        
        return {
            "status": "success",
            "total_episodes": len(all_items),
            "average_importance": sum(importances) / len(importances) if importances else 0.0,
            "oldest_episode": min(timestamps) if timestamps else None,
            "newest_episode": max(timestamps) if timestamps else None,
            "low_importance_count": low_importance_count,
            "old_episode_count": old_episode_count,
            "reclaimable_episodes": low_importance_count + old_episode_count,
        }

    def find_similar(self, query: str, limit: int = 2) -> list[dict[str, Any]]:
        """Find episodes similar to the current situation.

        Args:
            query: The current user query or situation description.
            limit: Maximum number of episodes to return.

        Returns:
            List of similar episodes with their details.
        """
        results = self.store.search(self.namespace, query=query, limit=limit)
        # Sort by importance first, then score
        sorted_results = sorted(results, key=lambda x: (
            x.value.get("importance", 0.5),
            x.score
        ), reverse=True)
        
        return [
            {
                "situation": r.value.get("situation", ""),
                "input": r.value.get("input", ""),
                "output": r.value.get("output", ""),
                "feedback": r.value.get("feedback", ""),
                "importance": r.value.get("importance", 0.5),
                "timestamp": r.value.get("timestamp", ""),
                "score": r.score,
            }
            for r in sorted_results
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
Situation: {ep["situation"]}
User: {ep["input"]}
Assistant: {ep["output"]}"""
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
            },
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
        new_instructions = str(response.content)

        new_version = self.update_instructions(new_instructions)
        return new_instructions, new_version
