"""
Memory management module for AI Life Coach.

This module provides comprehensive namespace strategy and utilities for managing
long-term memory using LangGraph's InMemoryStore. It defines data models,
namespace constants, and CRUD operations for all memory types.

Memory Architecture:
- User-specific namespaces: profile, goals, progress, preferences
- Shared namespace: coaching patterns (anonymized across users)
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

# Import LangGraph Store components
try:
    from langgraph.store.memory import InMemoryStore
    from langgraph.store.base import BaseStore
except ImportError:
    # For development/testing without full LangGraph installation
    InMemoryStore = None  # type: ignore
    BaseStore = Any  # type: ignore


# ==============================================================================
# Namespace Constants
# ==============================================================================


def get_profile_namespace(user_id: str) -> Tuple[str, str]:
    """Get the profile namespace for a user."""
    return (user_id, "profile")


def get_goals_namespace(user_id: str) -> Tuple[str, str]:
    """Get the goals namespace for a user."""
    return (user_id, "goals")


def get_progress_namespace(user_id: str) -> Tuple[str, str]:
    """Get the progress namespace for a user."""
    return (user_id, "progress")


def get_preferences_namespace(user_id: str) -> Tuple[str, str]:
    """Get the preferences namespace for a user."""
    return (user_id, "preferences")


def get_coaching_patterns_namespace() -> Tuple[str, str]:
    """Get the shared coaching patterns namespace (cross-user)."""
    return ("coaching", "patterns")


# ==============================================================================
# Data Models
# ==============================================================================


class UserProfile:
    """User profile data including demographics, values, and life situation."""

    def __init__(
        self,
        user_id: str,
        name: Optional[str] = None,
        age: Optional[int] = None,
        occupation: Optional[str] = None,
        relationship_status: Optional[str] = None,
        values: Optional[List[str]] = None,
        life_situation: Optional[Dict[str, Any]] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
    ):
        self.user_id = user_id
        self.name = name or ""
        self.age = age
        self.occupation = occupation or ""
        self.relationship_status = relationship_status or ""
        self.values = values or []
        self.life_situation = life_situation or {}
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary for storage."""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "age": self.age,
            "occupation": self.occupation,
            "relationship_status": self.relationship_status,
            "values": self.values,
            "life_situation": self.life_situation,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserProfile":
        """Create profile from dictionary."""
        return cls(
            user_id=data.get("user_id", ""),
            name=data.get("name"),
            age=data.get("age"),
            occupation=data.get("occupation"),
            relationship_status=data.get("relationship_status"),
            values=data.get("values", []),
            life_situation=data.get("life_situation", {}),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )


class Goal:
    """User goal with metadata for tracking and dependencies."""

    def __init__(
        self,
        goal_id: Optional[str] = None,
        title: str = "",
        description: str = "",
        domain: str = "general",  # career, relationship, finance, wellness
        priority: int = 3,  # 1-5 (5 = highest)
        status: str = "pending",  # pending, in_progress, completed, cancelled
        timeframe: str = "medium",  # short, medium, long
        deadline: Optional[str] = None,
        dependencies: Optional[List[str]] = None,  # IDs of prerequisite goals
        created_at: Optional[str] = None,
    ):
        self.goal_id = goal_id or str(uuid4())
        self.title = title
        self.description = description
        self.domain = domain
        self.priority = priority
        self.status = status
        self.timeframe = timeframe
        self.deadline = deadline
        self.dependencies = dependencies or []
        self.created_at = created_at or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert goal to dictionary for storage."""
        return {
            "goal_id": self.goal_id,
            "title": self.title,
            "description": self.description,
            "domain": self.domain,
            "priority": self.priority,
            "status": self.status,
            "timeframe": self.timeframe,
            "deadline": self.deadline,
            "dependencies": self.dependencies,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Goal":
        """Create goal from dictionary."""
        return cls(
            goal_id=data.get("goal_id"),
            title=data.get("title", ""),
            description=data.get("description", ""),
            domain=data.get("domain", "general"),
            priority=data.get("priority", 3),
            status=data.get("status", "pending"),
            timeframe=data.get("timeframe", "medium"),
            deadline=data.get("deadline"),
            dependencies=data.get("dependencies", []),
            created_at=data.get("created_at"),
        )


class Milestone:
    """Achievement or milestone in user's journey."""

    def __init__(
        self,
        title: str = "",
        description: str = "",
        domain: str = "general",
        achieved_at: Optional[str] = None,
        significance: str = "normal",  # minor, normal, major
        milestone_id: Optional[str] = None,
    ):
        self.milestone_id = milestone_id or str(uuid4())
        self.title = title
        self.description = description
        self.domain = domain
        self.achieved_at = achieved_at or datetime.now().isoformat()
        self.significance = significance

    def to_dict(self) -> Dict[str, Any]:
        """Convert milestone to dictionary for storage."""
        return {
            "milestone_id": self.milestone_id,
            "title": self.title,
            "description": self.description,
            "domain": self.domain,
            "achieved_at": self.achieved_at,
            "significance": self.significance,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Milestone":
        """Create milestone from dictionary."""
        return cls(
            title=data.get("title", ""),
            description=data.get("description", ""),
            domain=data.get("domain", "general"),
            achieved_at=data.get("achieved_at"),
            significance=data.get("significance", "normal"),
            milestone_id=data.get("milestone_id"),  # Preserve original ID
        )


class Setback:
    """Setback or challenge user has overcome."""

    def __init__(
        self,
        description: str = "",
        domain: str = "general",
        occurred_at: Optional[str] = None,
        resolved: bool = False,
        resolution_notes: str = "",
        setback_id: Optional[str] = None,
    ):
        self.setback_id = setback_id or str(uuid4())
        self.description = description
        self.domain = domain
        self.occurred_at = occurred_at or datetime.now().isoformat()
        self.resolved = resolved
        self.resolution_notes = resolution_notes

    def to_dict(self) -> Dict[str, Any]:
        """Convert setback to dictionary for storage."""
        return {
            "setback_id": self.setback_id,
            "description": self.description,
            "domain": self.domain,
            "occurred_at": self.occurred_at,
            "resolved": self.resolved,
            "resolution_notes": self.resolution_notes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Setback":
        """Create setback from dictionary."""
        return cls(
            description=data.get("description", ""),
            domain=data.get("domain", "general"),
            occurred_at=data.get("occurred_at"),
            resolved=data.get("resolved", False),
            resolution_notes=data.get("resolution_notes", ""),
            setback_id=data.get("setback_id"),  # Preserve original ID
        )


class UserPreferences:
    """User preferences for communication and coaching style."""

    def __init__(
        self,
        user_id: str = "",
        communication_style: str = "balanced",  # concise, balanced, detailed
        coaching_approach: str = "supportive",  # direct, supportive, collaborative
        preferred_checkin_frequency: str = "weekly",  # daily, weekly, bi_weekly
        preferred_response_length: str = "medium",  # short, medium, long
        custom_preferences: Optional[Dict[str, Any]] = None,
    ):
        self.user_id = user_id
        self.communication_style = communication_style
        self.coaching_approach = coaching_approach
        self.preferred_checkin_frequency = preferred_checkin_frequency
        self.preferred_response_length = preferred_response_length
        self.custom_preferences = custom_preferences or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert preferences to dictionary for storage."""
        return {
            "user_id": self.user_id,
            "communication_style": self.communication_style,
            "coaching_approach": self.coaching_approach,
            "preferred_checkin_frequency": self.preferred_checkin_frequency,
            "preferred_response_length": self.preferred_response_length,
            "custom_preferences": self.custom_preferences,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserPreferences":
        """Create preferences from dictionary."""
        return cls(
            user_id=data.get("user_id", ""),
            communication_style=data.get("communication_style", "balanced"),
            coaching_approach=data.get("coaching_approach", "supportive"),
            preferred_checkin_frequency=data.get("preferred_checkin_frequency", "weekly"),
            preferred_response_length=data.get("preferred_response_length", "medium"),
            custom_preferences=data.get("custom_preferences", {}),
        )


class CoachingPattern:
    """Anonymized coaching pattern learned across users."""

    def __init__(
        self,
        pattern_id: Optional[str] = None,
        title: str = "",
        description: str = "",
        category: str = "general",  # strategy, insight, challenge
        effectiveness_score: Optional[float] = None,  # 0-1 based on outcomes
        usage_count: int = 0,
        related_domains: Optional[List[str]] = None,
    ):
        self.pattern_id = pattern_id or str(uuid4())
        self.title = title
        self.description = description
        self.category = category
        self.effectiveness_score = effectiveness_score
        self.usage_count = usage_count
        self.related_domains = related_domains or []

    def to_dict(self) -> Dict[str, Any]:
        """Convert pattern to dictionary for storage."""
        return {
            "pattern_id": self.pattern_id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "effectiveness_score": self.effectiveness_score,
            "usage_count": self.usage_count,
            "related_domains": self.related_domains,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CoachingPattern":
        """Create pattern from dictionary."""
        return cls(
            pattern_id=data.get("pattern_id"),
            title=data.get("title", ""),
            description=data.get("description", ""),
            category=data.get("category", "general"),
            effectiveness_score=data.get("effectiveness_score"),
            usage_count=data.get("usage_count", 0),
            related_domains=data.get("related_domains", []),
        )


# ==============================================================================
# Memory Manager
# ==============================================================================


class MemoryManager:
    """
    High-level memory manager for AI Life Coach.

    Provides convenient CRUD operations for all memory namespaces.
    Handles error cases like missing users/data gracefully.
    """

    def __init__(self, store: Any):
        """
        Initialize the memory manager with a LangGraph Store.

        Args:
            store: An instance of InMemoryStore or PostgresStore

        Raises:
            ValueError: If store is not provided
        """
        if store is None:
            raise ValueError(
                "Store cannot be None. Initialize with InMemoryStore or PostgresStore."
            )
        self.store = store

    # ==================== Profile Operations ====================

    def save_profile(self, profile: UserProfile) -> None:
        """
        Save or update a user's complete profile.

        Args:
            profile: UserProfile object to save
        """
        namespace = get_profile_namespace(profile.user_id)
        profile.updated_at = datetime.now().isoformat()
        self.store.put(namespace, "profile_data", profile.to_dict())

    def get_profile(self, user_id: str) -> Optional[UserProfile]:
        """
        Retrieve a user's profile.

        Args:
            user_id: User's unique identifier

        Returns:
            UserProfile object or None if not found
        """
        namespace = get_profile_namespace(user_id)
        try:
            item = self.store.get(namespace, "profile_data")
            if item and item.value:
                return UserProfile.from_dict(item.value)
        except Exception:
            # Profile not found or access error
            pass
        return None

    def profile_exists(self, user_id: str) -> bool:
        """
        Check if a user has an existing profile.

        Args:
            user_id: User's unique identifier

        Returns:
            True if profile exists, False otherwise
        """
        return self.get_profile(user_id) is not None

    # ==================== Goal Operations ====================

    def save_goal(self, user_id: str, goal: Goal) -> None:
        """
        Save or update a single goal.

        Args:
            user_id: User's unique identifier
            goal: Goal object to save

        Raises:
            ValueError: If user_id is empty
        """
        if not user_id:
            raise ValueError("user_id cannot be empty")

        namespace = get_goals_namespace(user_id)
        self.store.put(namespace, goal.goal_id, goal.to_dict())

    def get_goal(self, user_id: str, goal_id: str) -> Optional[Goal]:
        """
        Retrieve a specific goal.

        Args:
            user_id: User's unique identifier
            goal_id: Goal's unique identifier

        Returns:
            Goal object or None if not found
        """
        namespace = get_goals_namespace(user_id)
        try:
            item = self.store.get(namespace, goal_id)
            if item and item.value:
                return Goal.from_dict(item.value)
        except Exception:
            pass
        return None

    def get_goals(self, user_id: str) -> List[Goal]:
        """
        Retrieve all goals for a user.

        Args:
            user_id: User's unique identifier

        Returns:
            List of Goal objects (empty list if no goals found)
        """
        namespace = get_goals_namespace(user_id)
        goals: List[Goal] = []
        try:
            items = list(self.store.search(namespace))
            goals = [Goal.from_dict(item.value) for item in items if item.value]
        except Exception:
            pass
        return goals

    def get_goals_by_domain(self, user_id: str, domain: str) -> List[Goal]:
        """
        Retrieve goals filtered by domain.

        Args:
            user_id: User's unique identifier
            domain: Domain to filter by (career, relationship, finance, wellness)

        Returns:
            List of Goal objects filtered by domain
        """
        goals = self.get_goals(user_id)
        return [goal for goal in goals if goal.domain == domain]

    def delete_goal(self, user_id: str, goal_id: str) -> bool:
        """
        Delete a specific goal.

        Args:
            user_id: User's unique identifier
            goal_id: Goal's unique identifier

        Returns:
            True if deleted, False otherwise
        """
        namespace = get_goals_namespace(user_id)
        try:
            self.store.delete(namespace, goal_id)
            return True
        except Exception:
            return False

    # ==================== Progress Operations ====================

    def add_milestone(self, user_id: str, milestone: Milestone) -> None:
        """
        Add a milestone to user's progress record.

        Args:
            user_id: User's unique identifier
            milestone: Milestone object to add

        Raises:
            ValueError: If user_id is empty
        """
        if not user_id:
            raise ValueError("user_id cannot be empty")

        namespace = get_progress_namespace(user_id)
        # Use milestone ID as key
        self.store.put(namespace, f"milestone_{milestone.milestone_id}", milestone.to_dict())

    def add_setback(self, user_id: str, setback: Setback) -> None:
        """
        Add a setback to user's progress record.

        Args:
            user_id: User's unique identifier
            setback: Setback object to add

        Raises:
            ValueError: If user_id is empty
        """
        if not user_id:
            raise ValueError("user_id cannot be empty")

        namespace = get_progress_namespace(user_id)
        self.store.put(namespace, f"setback_{setback.setback_id}", setback.to_dict())

    def get_milestones(self, user_id: str) -> List[Milestone]:
        """
        Retrieve all milestones for a user.

        Args:
            user_id: User's unique identifier

        Returns:
            List of Milestone objects (empty list if none found)
        """
        namespace = get_progress_namespace(user_id)
        milestones: List[Milestone] = []
        try:
            items = list(self.store.search(namespace))
            for item in items:
                if item.value and isinstance(item.key, str) and item.key.startswith("milestone_"):
                    milestones.append(Milestone.from_dict(item.value))
        except Exception:
            pass
        return sorted(milestones, key=lambda m: m.achieved_at or "")

    def get_setbacks(self, user_id: str) -> List[Setback]:
        """
        Retrieve all setbacks for a user.

        Args:
            user_id: User's unique identifier

        Returns:
            List of Setback objects (empty list if none found)
        """
        namespace = get_progress_namespace(user_id)
        setbacks: List[Setback] = []
        try:
            items = list(self.store.search(namespace))
            for item in items:
                if item.value and isinstance(item.key, str) and item.key.startswith("setback_"):
                    setbacks.append(Setback.from_dict(item.value))
        except Exception:
            pass
        return sorted(setbacks, key=lambda s: s.occurred_at or "")

    # ==================== Preferences Operations ====================

    def save_preferences(self, preferences: UserPreferences) -> None:
        """
        Save or update user's coaching preferences.

        Args:
            preferences: UserPreferences object to save

        Raises:
            ValueError: If user_id is empty
        """
        if not preferences.user_id:
            raise ValueError("user_id cannot be empty")

        namespace = get_preferences_namespace(preferences.user_id)
        self.store.put(namespace, "preferences_data", preferences.to_dict())

    def get_preferences(self, user_id: str) -> Optional[UserPreferences]:
        """
        Retrieve a user's preferences.

        Args:
            user_id: User's unique identifier

        Returns:
            UserPreferences object or None if not found
        """
        namespace = get_preferences_namespace(user_id)
        try:
            item = self.store.get(namespace, "preferences_data")
            if item and item.value:
                prefs_dict = item.value
                prefs_dict["user_id"] = user_id  # Ensure user_id is set
                return UserPreferences.from_dict(prefs_dict)
        except Exception:
            pass
        return None

    def update_preference_key(self, user_id: str, key: str, value: Any) -> None:
        """
        Update a single preference field.

        Args:
            user_id: User's unique identifier
            key: Preference field name (e.g., "communication_style")
            value: New value for the preference

        Raises:
            ValueError: If user_id is empty
        """
        if not user_id:
            raise ValueError("user_id cannot be empty")

        preferences = self.get_preferences(user_id) or UserPreferences(user_id=user_id)

        # Update if key exists in preferences
        if hasattr(preferences, key):
            setattr(preferences, key, value)
        elif preferences.custom_preferences is not None:
            preferences.custom_preferences[key] = value
        else:
            preferences.custom_preferences = {key: value}

        self.save_preferences(preferences)

    # ==================== Coaching Patterns Operations ====================

    def save_pattern(self, pattern: CoachingPattern) -> None:
        """
        Save or update a coaching pattern (shared across users).

        Args:
            pattern: CoachingPattern object to save

        Note:
            Patterns are stored in shared namespace and should be anonymized.
        """
        namespace = get_coaching_patterns_namespace()
        self.store.put(namespace, pattern.pattern_id, pattern.to_dict())

    def get_pattern(self, pattern_id: str) -> Optional[CoachingPattern]:
        """
        Retrieve a specific coaching pattern.

        Args:
            pattern_id: Pattern's unique identifier

        Returns:
            CoachingPattern object or None if not found
        """
        namespace = get_coaching_patterns_namespace()
        try:
            item = self.store.get(namespace, pattern_id)
            if item and item.value:
                return CoachingPattern.from_dict(item.value)
        except Exception:
            pass
        return None

    def get_patterns(self) -> List[CoachingPattern]:
        """
        Retrieve all coaching patterns.

        Returns:
            List of CoachingPattern objects (empty list if none found)
        """
        namespace = get_coaching_patterns_namespace()
        patterns: List[CoachingPattern] = []
        try:
            items = list(self.store.search(namespace))
            patterns = [CoachingPattern.from_dict(item.value) for item in items if item.value]
        except Exception:
            pass
        return sorted(patterns, key=lambda p: p.usage_count or 0, reverse=True)

    def get_patterns_by_domain(self, domain: str) -> List[CoachingPattern]:
        """
        Retrieve patterns filtered by related domains.

        Args:
            domain: Domain to filter by (career, relationship, finance, wellness)

        Returns:
            List of CoachingPattern objects filtered by domain
        """
        patterns = self.get_patterns()
        return [p for p in patterns if domain in (p.related_domains or [])]

    def increment_pattern_usage(self, pattern_id: str) -> None:
        """
        Increment the usage count for a pattern.

        Args:
            pattern_id: Pattern's unique identifier
        """
        pattern = self.get_pattern(pattern_id)
        if pattern:
            pattern.usage_count += 1
            self.save_pattern(pattern)

    # ==================== Utility Operations ====================

    def get_user_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Get a comprehensive summary of all data for a user.

        Args:
            user_id: User's unique identifier

        Returns:
            Dictionary containing summary of all user data
        """
        return {
            "profile": self.get_profile(user_id),
            "goals": self.get_goals(user_id),
            "milestones": self.get_milestones(user_id),
            "setbacks": self.get_setbacks(user_id),
            "preferences": self.get_preferences(user_id),
        }

    def delete_user_data(self, user_id: str) -> bool:
        """
        Delete all data for a user (GDPR compliance).

        Args:
            user_id: User's unique identifier

        Returns:
            True if deletion successful, False otherwise
        """
        try:
            # Delete from each user-specific namespace
            namespaces = [
                get_profile_namespace(user_id),
                get_goals_namespace(user_id),
                get_progress_namespace(user_id),
                get_preferences_namespace(user_id),
            ]

            for namespace in namespaces:
                try:
                    items = list(self.store.search(namespace))
                    for item in items:
                        self.store.delete(namespace, item.key)
                except Exception:
                    continue

            return True
        except Exception:
            return False


# ==============================================================================
# Factory Functions
# ==============================================================================


def create_memory_store(store_type: str = "in_memory") -> Any:
    """
    Create a memory store instance.

    Args:
        store_type: Type of store to create ("in_memory" or "postgres")

    Returns:
        Initialized BaseStore instance

    Raises:
        ValueError: If store_type is invalid or InMemoryStore not available
        NotImplementedError: For postgres store (not yet implemented)
    """
    if InMemoryStore is None:
        raise ValueError("LangGraph Store not available. Install with: pip install langgraph")

    if store_type == "in_memory":
        return InMemoryStore()
    elif store_type == "postgres":
        raise NotImplementedError(
            "PostgresStore not yet implemented. Use store_type='in_memory' for development."
        )
    else:
        raise ValueError(f"Invalid store_type: {store_type}. Use 'in_memory' or 'postgres'.")


def create_memory_manager(store: Optional[Any] = None) -> MemoryManager:
    """
    Create a memory manager instance.

    Args:
        store: Optional pre-initialized store. If None, creates InMemoryStore.

    Returns:
        Initialized MemoryManager instance

    Raises:
        ValueError: If store cannot be created
    """
    if store is None:
        store = create_memory_store()
    return MemoryManager(store)
