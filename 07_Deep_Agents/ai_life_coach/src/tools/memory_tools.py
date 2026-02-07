"""
Memory tools for AI Life Coach.

This module provides LangChain tools that allow agents to interact with
the long-term memory system. Each tool uses the @tool decorator and follows
best practices for validation, error handling, and user-friendly output.

Tools:
- get_user_profile: Retrieve a user's wellness profile
- save_user_preference: Save a user preference to memory
- update_milestone: Add or update a milestone in progress tracking
- get_progress_history: Retrieve filtered progress history for a user
"""

from datetime import datetime
from typing import Any, Optional

# Import LangChain components
try:
    from langchain_core.tools import tool
except ImportError:
    # Fallback for development environments without full LangChain
    def tool(func):
        """Fallback decorator when langchain_core is not available."""
        func.is_tool = True  # type: ignore
        return func


# Import LangGraph Store components
try:
    from langgraph.store.base import BaseStore
except ImportError:
    BaseStore = Any  # type: ignore

# Import memory module components
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from memory import MemoryManager


# ==============================================================================
# Memory Tool Factory
# ==============================================================================


def create_memory_tools(store: Optional[Any] = None) -> tuple:
    """
    Create memory tools with a shared MemoryManager instance.

    Args:
        store: Optional LangGraph Store instance. If None, creates InMemoryStore.

    Returns:
        Tuple of memory tools (get_user_profile, save_user_preference,
                               update_milestone, get_progress_history)

    Raises:
        ValueError: If store cannot be created
    """
    # Create memory manager with the provided or default store
    memory_manager = MemoryManager(store)

    # Define tools that share the same memory manager
    @tool
    def get_user_profile(user_id: str) -> str:
        """Retrieve a user's wellness profile from long-term memory.

        This tool fetches the complete user profile including demographics,
        values, occupation, relationship status, and life situation.

        Args:
            user_id: The user's unique identifier (must be non-empty string)

        Returns:
            User profile as formatted text string. If profile not found,
            returns a helpful message indicating no profile exists.

        Raises:
            ValueError: If user_id is empty or not a string

        Example:
            >>> result = get_user_profile("user_123")
            >>> print(result)
            Profile for user_123:
              name: Alex Johnson
              age: 35
              occupation: Software Engineer
        """
        # Validate input
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        try:
            # Retrieve profile from memory
            profile = memory_manager.get_profile(user_id)

            if not profile:
                return f"No profile found for user '{user_id}'. Would you like to create a profile?"

            # Format profile data as readable text
            parts = [f"Profile for '{user_id}':"]

            if profile.name:
                parts.append(f"  name: {profile.name}")
            if profile.age is not None:
                parts.append(f"  age: {profile.age}")
            if profile.occupation:
                parts.append(f"  occupation: {profile.occupation}")
            if profile.relationship_status:
                parts.append(f"  relationship_status: {profile.relationship_status}")
            if profile.values:
                parts.append(f"  values: {', '.join(profile.values)}")
            if profile.life_situation:
                parts.append(f"  life_situation: {profile.life_situation}")
            if profile.created_at:
                parts.append(f"  created_at: {profile.created_at}")
            if profile.updated_at:
                parts.append(f"  updated_at: {profile.updated_at}")

            return "\n".join(parts)

        except Exception as e:
            # Handle any unexpected errors gracefully
            return f"Error retrieving profile for user '{user_id}': {str(e)}"

    @tool
    def save_user_preference(user_id: str, key: str, value: str) -> str:
        """Save a user preference to long-term memory.

        This tool stores individual preference settings for coaching style,
        communication preferences, and other user-specific configurations.

        Args:
            user_id: The user's unique identifier (must be non-empty string)
            key: The preference key/field name (e.g., "communication_style",
                 "coaching_approach", "preferred_checkin_frequency")
            value: The preference value to store

        Returns:
            Confirmation message indicating the preference was saved.
            If an error occurs, returns a helpful error message.

        Raises:
            ValueError: If user_id or key is empty

        Example:
            >>> save_user_preference("user_123", "communication_style", "concise")
            'Saved preference communication_style for user user_123'
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not key or not isinstance(key, str):
            return "Error: key must be a non-empty string"
        if value is None:
            return "Error: value cannot be None"

        try:
            # Update the specific preference key
            memory_manager.update_preference_key(user_id, key, value)

            return f"Saved preference '{key}' for user '{user_id}'"

        except ValueError as ve:
            # Handle validation errors
            return f"Validation error: {str(ve)}"
        except Exception as e:
            # Handle unexpected errors
            return f"Error saving preference for user '{user_id}': {str(e)}"

    @tool
    def update_milestone(user_id: str, milestone_data: dict) -> str:
        """Add or update a milestone in the user's progress tracking.

        This tool records achievements and milestones across different domains
        (career, relationship, finance, wellness) to track user progress.

        Args:
            user_id: The user's unique identifier (must be non-empty string)
            milestone_data: Dictionary containing milestone information:
                - title (str): Title of the milestone
                - description (str, optional): Detailed description
                - domain (str, optional): Domain category (default: "general")
                - achieved_at (str, optional): ISO timestamp (default: now)
                - significance (str, optional): "minor", "normal", or "major"
                - milestone_id (str, optional): Existing ID to update

        Returns:
            Confirmation message indicating the milestone was saved.
            If an error occurs, returns a helpful error message.

        Raises:
            ValueError: If user_id is empty or milestone_data is invalid

        Example:
            >>> update_milestone("user_123", {
            ...     "title": "Got promotion",
            ...     "domain": "career",
            ...     "significance": "major"
            ... })
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not milestone_data or not isinstance(milestone_data, dict):
            return "Error: milestone_data must be a non-empty dictionary"

        # Validate required fields
        if "title" not in milestone_data or not milestone_data["title"]:
            return "Error: milestone_data must contain a non-empty 'title' field"

        try:
            # Import Milestone model
            from memory import Milestone

            # Create milestone object with validation
            milestone = Milestone(
                title=milestone_data["title"],
                description=milestone_data.get("description", ""),
                domain=milestone_data.get("domain", "general"),
                achieved_at=milestone_data.get("achieved_at") or datetime.now().isoformat(),
                significance=milestone_data.get("significance", "normal"),
                milestone_id=milestone_data.get("milestone_id"),
            )

            # Save to memory
            memory_manager.add_milestone(user_id, milestone)

            return (
                f"Milestone '{milestone.title}' saved for user '{user_id}' "
                f"(domain: {milestone.domain}, significance: {milestone.significance})"
            )

        except ValueError as ve:
            # Handle validation errors
            return f"Validation error: {str(ve)}"
        except Exception as e:
            # Handle unexpected errors
            return f"Error updating milestone for user '{user_id}': {str(e)}"

    @tool
    def get_progress_history(user_id: str, timeframe: Optional[str] = None) -> str:
        """Retrieve filtered progress history for a user.

        This tool retrieves milestones and setbacks from the user's progress
        record, optionally filtered by timeframe or domain.

        Args:
            user_id: The user's unique identifier (must be non-empty string)
            timeframe: Optional filter for time period:
                - "all": Return all progress (default)
                - "recent": Last 30 days
                - "month": Current month
                - "year": Current year

        Returns:
            Formatted progress history as text string. If no progress found,
            returns a helpful message indicating no milestones exist.

        Raises:
            ValueError: If user_id is empty

        Example:
            >>> get_progress_history("user_123", "recent")
            'Progress history for user_123 (recent):\n  Milestones:...'
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        try:
            # Retrieve milestones and setbacks
            milestones = memory_manager.get_milestones(user_id)
            setbacks = memory_manager.get_setbacks(user_id)

            # Apply timeframe filtering if specified
            now = datetime.now()
            filtered_milestones = []
            filtered_setbacks = []

            if timeframe == "recent":
                # Last 30 days
                cutoff_date = now.replace(day=max(1, now.day - 30)).isoformat()
            elif timeframe == "month":
                # Current month
                cutoff_date = now.replace(day=1).isoformat()
            elif timeframe == "year":
                # Current year
                cutoff_date = now.replace(month=1, day=1).isoformat()
            else:
                # All time - no filtering
                cutoff_date = None

            for milestone in milestones:
                if cutoff_date is None or (
                    milestone.achieved_at and milestone.achieved_at >= cutoff_date
                ):
                    filtered_milestones.append(milestone)

            for setback in setbacks:
                if cutoff_date is None or (
                    setback.occurred_at and setback.occurred_at >= cutoff_date
                ):
                    filtered_setbacks.append(setback)

            # Check if any progress exists
            if not filtered_milestones and not filtered_setbacks:
                timeframe_desc = f" ({timeframe})" if timeframe else ""
                return (
                    f"No progress history found for user '{user_id}'{timeframe_desc}. "
                    "Track milestones and setbacks to build your progress record."
                )

            # Format progress history
            parts = [f"Progress history for user '{user_id}'"]
            if timeframe:
                parts.append(f" ({timeframe})")
            parts.append(":")

            # Add milestones section
            if filtered_milestones:
                parts.append(f"\n  Milestones ({len(filtered_milestones)}):")
                for milestone in filtered_milestones:
                    parts.append(f"    - {milestone.title}")
                    if milestone.description:
                        parts.append(f"      Description: {milestone.description}")
                    if milestone.domain != "general":
                        parts.append(f"      Domain: {milestone.domain}")
                    if milestone.significance != "normal":
                        parts.append(f"      Significance: {milestone.significance}")
                    if milestone.achieved_at:
                        parts.append(f"      Achieved: {milestone.achieved_at}")

            # Add setbacks section
            if filtered_setbacks:
                parts.append(f"\n  Setbacks ({len(filtered_setbacks)}):")
                for setback in filtered_setbacks:
                    parts.append(f"    - {setback.description}")
                    if setback.domain != "general":
                        parts.append(f"      Domain: {setback.domain}")
                    if setback.occurred_at:
                        parts.append(f"      Occurred: {setback.occurred_at}")
                    if setback.resolved:
                        parts.append(f"      Status: Resolved")
                    elif setback.resolution_notes:
                        parts.append(f"      Resolution Notes: {setback.resolution_notes}")

            return "\n".join(parts)

        except Exception as e:
            # Handle unexpected errors gracefully
            return f"Error retrieving progress history for user '{user_id}': {str(e)}"

    print("Memory tools created successfully!")
    return get_user_profile, save_user_preference, update_milestone, get_progress_history


# Export tools at module level for convenience
__all__ = [
    "create_memory_tools",
]
