"""
Resource Curation System for AI Life Coach.

This module implements a comprehensive resource curation and recommendation system that:
1. Manages curated learning resources with rich metadata
2. Implements tagging and categorization for discoverability
3. Provides personalized recommendations based on user goals and preferences
4. Tracks resource ratings and reviews
5. Monitors user progress through resources (not started, in progress, completed)

Based on research in:
- Content curation best practices (aggregation, distillation, elevation)
- Personalized learning resource recommendation algorithms
- Tag-based recommendation systems
- User preference learning and collaborative filtering

Resource Types Supported:
- Articles/Blog posts
- Books
- Videos/Courses
- Exercises/Worksheets
- Tools/Apps

Metadata Schema:
- title: Resource title
- type: Resource type (article, book, video, exercise, tool)
- category: Primary category (career, relationship, finance, wellness)
- tags: List of descriptive tags
- difficulty: Difficulty level (beginner, intermediate, advanced)
- estimated_time: Estimated time to consume (minutes)
- author/creator: Source attribution
- url: Link to resource (optional)
- description: Brief summary
- rating: Average user rating (1-5)
- review_count: Number of reviews
"""

from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
import json

# Import LangChain components
try:
    from langchain_core.tools import tool
except ImportError:
    # Fallback for development environments without full LangChain
    def tool(func):
        """Fallback decorator when langchain_core is not available."""
        func.is_tool = True  # type: ignore
        return func


# Import backend configuration
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import get_backend


# ==============================================================================
# Resource Metadata Schema
# ==============================================================================


class ResourceType(str, Enum):
    """Enumeration of supported resource types."""

    ARTICLE = "article"
    BOOK = "book"
    VIDEO = "video"
    EXERCISE = "exercise"
    TOOL = "tool"


class ResourceCategory(str, Enum):
    """Enumeration of resource categories aligned with life domains."""

    CAREER = "career"
    RELATIONSHIP = "relationship"
    FINANCE = "finance"
    WELLNESS = "wellness"
    GENERAL = "general"


class DifficultyLevel(str, Enum):
    """Enumeration of difficulty levels."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class ProgressStatus(str, Enum):
    """Enumeration of resource progress statuses."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


# Predefined tag taxonomy for consistency
TAG_TAXONOMY = {
    "career": [
        "skill_development",
        "networking",
        "resume",
        "interview_prep",
        "leadership",
        "career_change",
        "promotion",
        "work_life_balance",
        "productivity",
        "time_management",
        "negotiation",
        "personal_branding",
    ],
    "relationship": [
        "communication",
        "conflict_resolution",
        "boundary_setting",
        "trust_building",
        "emotional_intelligence",
        "dating",
        "marriage",
        "family",
        "friendship",
        "social_skills",
        "empathy",
        "active_listening",
    ],
    "finance": [
        "budgeting",
        "saving",
        "investing",
        "debt_management",
        "retirement_planning",
        "emergency_fund",
        "financial_literacy",
        "tax_planning",
        "wealth_building",
        "frugality",
        "side_hustle",
        "financial_independence",
    ],
    "wellness": [
        "nutrition",
        "exercise",
        "sleep",
        "stress_management",
        "mental_health",
        "mindfulness",
        "meditation",
        "habit_formation",
        "self_care",
        "energy_management",
        "workout",
        "healthy_eating",
        "burnout_prevention",
    ],
    "general": [
        "goal_setting",
        "motivation",
        "productivity",
        "learning",
        "self_improvement",
        "mindset",
        "confidence",
        "resilience",
        "growth_mindset",
    ],
}


# Recommendation weights for scoring algorithm
RECOMMENDATION_WEIGHTS = {
    "goal_alignment": 0.35,  # 35% - How well resource matches user goals
    "category_match": 0.20,  # 20% - Matches user's focus domain
    "difficulty_match": 0.15,  # 15% - Appropriate difficulty level
    "rating": 0.15,  # 15% - Resource quality rating
    "time_fit": 0.10,  # 10% - Fits user's available time
    "diversity": 0.05,  # 5% - Ensures variety in recommendations
}


# ==============================================================================
# Resource Data Models
# ==============================================================================


class Resource:
    """
    Represents a curated learning resource with comprehensive metadata.
    """

    def __init__(
        self,
        resource_id: Optional[str] = None,
        title: str = "",
        resource_type: str = "article",
        category: str = "general",
        tags: Optional[List[str]] = None,
        difficulty: str = "beginner",
        estimated_time: int = 15,
        author: str = "",
        url: str = "",
        description: str = "",
        rating: float = 0.0,
        review_count: int = 0,
        created_at: Optional[str] = None,
    ):
        self.resource_id = (
            resource_id
            or f"res_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hash(title) % 10000:04d}"
        )
        self.title = title
        self.resource_type = resource_type
        self.category = category
        self.tags = tags or []
        self.difficulty = difficulty
        self.estimated_time = estimated_time
        self.author = author
        self.url = url
        self.description = description
        self.rating = rating
        self.review_count = review_count
        self.created_at = created_at or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert resource to dictionary for storage."""
        return {
            "resource_id": self.resource_id,
            "title": self.title,
            "resource_type": self.resource_type,
            "category": self.category,
            "tags": self.tags,
            "difficulty": self.difficulty,
            "estimated_time": self.estimated_time,
            "author": self.author,
            "url": self.url,
            "description": self.description,
            "rating": self.rating,
            "review_count": self.review_count,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Resource":
        """Create resource from dictionary."""
        return cls(
            resource_id=data.get("resource_id"),
            title=data.get("title", ""),
            resource_type=data.get("resource_type", "article"),
            category=data.get("category", "general"),
            tags=data.get("tags", []),
            difficulty=data.get("difficulty", "beginner"),
            estimated_time=data.get("estimated_time", 15),
            author=data.get("author", ""),
            url=data.get("url", ""),
            description=data.get("description", ""),
            rating=data.get("rating", 0.0),
            review_count=data.get("review_count", 0),
            created_at=data.get("created_at"),
        )


class UserResourceProgress:
    """
    Tracks a user's progress and interaction with a specific resource.
    """

    def __init__(
        self,
        user_id: str,
        resource_id: str,
        status: str = "not_started",
        user_rating: Optional[int] = None,
        user_review: str = "",
        progress_percentage: int = 0,
        started_at: Optional[str] = None,
        completed_at: Optional[str] = None,
        notes: str = "",
    ):
        self.user_id = user_id
        self.resource_id = resource_id
        self.status = status
        self.user_rating = user_rating
        self.user_review = user_review
        self.progress_percentage = progress_percentage
        self.started_at = started_at
        self.completed_at = completed_at
        self.notes = notes

    def to_dict(self) -> Dict[str, Any]:
        """Convert progress to dictionary for storage."""
        return {
            "user_id": self.user_id,
            "resource_id": self.resource_id,
            "status": self.status,
            "user_rating": self.user_rating,
            "user_review": self.user_review,
            "progress_percentage": self.progress_percentage,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserResourceProgress":
        """Create progress from dictionary."""
        return cls(
            user_id=data.get("user_id", ""),
            resource_id=data.get("resource_id", ""),
            status=data.get("status", "not_started"),
            user_rating=data.get("user_rating"),
            user_review=data.get("user_review", ""),
            progress_percentage=data.get("progress_percentage", 0),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
            notes=data.get("notes", ""),
        )


class ResourceReview:
    """
    Represents a user review of a resource.
    """

    def __init__(
        self,
        user_id: str,
        resource_id: str,
        rating: int,
        review: str = "",
        would_recommend: bool = True,
        helpful_count: int = 0,
        created_at: Optional[str] = None,
    ):
        self.user_id = user_id
        self.resource_id = resource_id
        self.rating = rating
        self.review = review
        self.would_recommend = would_recommend
        self.helpful_count = helpful_count
        self.created_at = created_at or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert review to dictionary for storage."""
        return {
            "user_id": self.user_id,
            "resource_id": self.resource_id,
            "rating": self.rating,
            "review": self.review,
            "would_recommend": self.would_recommend,
            "helpful_count": self.helpful_count,
            "created_at": self.created_at,
        }


# ==============================================================================
# Helper Functions
# ==============================================================================


def sanitize_filename(text: str) -> str:
    """
    Sanitize text for use in filenames.

    Args:
        text: Text to sanitize

    Returns:
        Sanitized filename-safe string
    """
    safe = "".join(c if c.isalnum() or c in (" ", "-", "_") else "_" for c in text)
    return safe.replace(" ", "_").lower()[:50]


def calculate_goal_alignment_score(resource: Resource, user_goals: List[Dict[str, Any]]) -> float:
    """
    Calculate how well a resource aligns with user goals.

    Uses tag matching and category alignment to determine relevance.

    Args:
        resource: Resource to evaluate
        user_goals: List of user's goals

    Returns:
        Alignment score between 0.0 and 1.0
    """
    if not user_goals:
        return 0.5  # Neutral score if no goals

    alignment_scores = []

    for goal in user_goals:
        goal_domain = goal.get("domain", "general")
        goal_title = goal.get("title", "").lower()
        goal_description = goal.get("description", "").lower()

        score = 0.0

        # Category match
        if resource.category == goal_domain:
            score += 0.4

        # Tag overlap with goal keywords
        goal_text = f"{goal_title} {goal_description}"
        matching_tags = [tag for tag in resource.tags if tag.lower() in goal_text]
        score += len(matching_tags) * 0.15

        # Title/description keyword match
        resource_text = f"{resource.title} {resource.description}".lower()
        goal_words = set(goal_text.split())
        resource_words = set(resource_text.split())
        word_overlap = len(goal_words & resource_words)
        score += min(word_overlap * 0.05, 0.3)

        alignment_scores.append(min(score, 1.0))

    return max(alignment_scores) if alignment_scores else 0.5


def calculate_difficulty_match_score(resource: Resource, user_level: str = "intermediate") -> float:
    """
    Calculate how well resource difficulty matches user level.

    Args:
        resource: Resource to evaluate
        user_level: User's preferred difficulty level

    Returns:
        Match score between 0.0 and 1.0
    """
    difficulty_levels = ["beginner", "intermediate", "advanced"]

    resource_idx = (
        difficulty_levels.index(resource.difficulty)
        if resource.difficulty in difficulty_levels
        else 1
    )
    user_idx = difficulty_levels.index(user_level) if user_level in difficulty_levels else 1

    diff = abs(resource_idx - user_idx)

    if diff == 0:
        return 1.0
    elif diff == 1:
        return 0.7
    else:
        return 0.4


def calculate_time_fit_score(resource: Resource, available_time: int = 30) -> float:
    """
    Calculate how well resource fits user's available time.

    Args:
        resource: Resource to evaluate
        available_time: User's available time in minutes

    Returns:
        Fit score between 0.0 and 1.0
    """
    if available_time <= 0:
        return 0.5

    # Perfect fit if resource time equals available time
    if resource.estimated_time <= available_time:
        return 1.0

    # Penalty for resources that exceed available time
    excess_ratio = resource.estimated_time / available_time
    return max(0.0, 1.0 - (excess_ratio - 1.0) * 0.5)


def calculate_recommendation_score(
    resource: Resource,
    user_goals: List[Dict[str, Any]],
    focus_category: str = "general",
    user_difficulty: str = "intermediate",
    available_time: int = 30,
    exclude_ids: Optional[List[str]] = None,
) -> float:
    """
    Calculate comprehensive recommendation score for a resource.

    Uses weighted factors to determine how well a resource matches user needs.

    Args:
        resource: Resource to score
        user_goals: User's goals for alignment calculation
        focus_category: User's current focus domain
        user_difficulty: User's preferred difficulty level
        available_time: User's available time in minutes
        exclude_ids: Resource IDs to exclude from recommendations

    Returns:
        Recommendation score between 0.0 and 1.0
    """
    # Skip excluded resources
    if exclude_ids and resource.resource_id in exclude_ids:
        return 0.0

    # Calculate component scores
    goal_alignment = calculate_goal_alignment_score(resource, user_goals)
    category_match = 1.0 if resource.category == focus_category else 0.3
    difficulty_match = calculate_difficulty_match_score(resource, user_difficulty)
    rating_score = resource.rating / 5.0 if resource.rating > 0 else 0.5
    time_fit = calculate_time_fit_score(resource, available_time)

    # Calculate weighted total
    total_score = (
        goal_alignment * RECOMMENDATION_WEIGHTS["goal_alignment"]
        + category_match * RECOMMENDATION_WEIGHTS["category_match"]
        + difficulty_match * RECOMMENDATION_WEIGHTS["difficulty_match"]
        + rating_score * RECOMMENDATION_WEIGHTS["rating"]
        + time_fit * RECOMMENDATION_WEIGHTS["time_fit"]
    )

    return round(total_score, 3)


def load_resource_catalog(backend: Any) -> Dict[str, Resource]:
    """
    Load all resources from the catalog.

    Args:
        backend: FilesystemBackend instance

    Returns:
        Dictionary of resource_id -> Resource
    """
    catalog_path = "resources/catalog.json"
    catalog = {}

    try:
        if hasattr(backend, "read_file"):
            content = backend.read_file(catalog_path)
        else:
            workspace_path = (
                Path(backend.root_dir) if hasattr(backend, "root_dir") else Path("workspace")
            )
            file_path = workspace_path / catalog_path
            if not file_path.exists():
                return catalog
            content = file_path.read_text()

        data = json.loads(content)
        for res_data in data.get("resources", []):
            resource = Resource.from_dict(res_data)
            catalog[resource.resource_id] = resource

    except Exception:
        pass  # Return empty catalog if file doesn't exist

    return catalog


def save_resource_catalog(backend: Any, catalog: Dict[str, Resource]) -> None:
    """
    Save resource catalog to storage.

    Args:
        backend: FilesystemBackend instance
        catalog: Dictionary of resource_id -> Resource
    """
    catalog_path = "resources/catalog.json"
    workspace_path = Path(backend.root_dir) if hasattr(backend, "root_dir") else Path("workspace")

    data = {
        "last_updated": datetime.now().isoformat(),
        "resource_count": len(catalog),
        "resources": [r.to_dict() for r in catalog.values()],
    }

    json_content = json.dumps(data, indent=2)

    if hasattr(backend, "write_file"):
        backend.write_file(catalog_path, json_content)
    else:
        file_path = workspace_path / catalog_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(json_content)


def load_user_resource_progress(user_id: str, backend: Any) -> Dict[str, UserResourceProgress]:
    """
    Load a user's resource progress data.

    Args:
        user_id: User identifier
        backend: FilesystemBackend instance

    Returns:
        Dictionary of resource_id -> UserResourceProgress
    """
    progress_path = f"resources/user_progress/{user_id}.json"
    progress = {}

    try:
        if hasattr(backend, "read_file"):
            content = backend.read_file(progress_path)
        else:
            workspace_path = (
                Path(backend.root_dir) if hasattr(backend, "root_dir") else Path("workspace")
            )
            file_path = workspace_path / progress_path
            if not file_path.exists():
                return progress
            content = file_path.read_text()

        data = json.loads(content)
        for prog_data in data.get("progress", []):
            prog = UserResourceProgress.from_dict(prog_data)
            progress[prog.resource_id] = prog

    except Exception:
        pass  # Return empty progress if file doesn't exist

    return progress


def save_user_resource_progress(
    user_id: str, backend: Any, progress: Dict[str, UserResourceProgress]
) -> None:
    """
    Save a user's resource progress data.

    Args:
        user_id: User identifier
        backend: FilesystemBackend instance
        progress: Dictionary of resource_id -> UserResourceProgress
    """
    progress_path = f"resources/user_progress/{user_id}.json"
    workspace_path = Path(backend.root_dir) if hasattr(backend, "root_dir") else Path("workspace")

    data = {
        "user_id": user_id,
        "last_updated": datetime.now().isoformat(),
        "progress_count": len(progress),
        "progress": [p.to_dict() for p in progress.values()],
    }

    json_content = json.dumps(data, indent=2)

    if hasattr(backend, "write_file"):
        backend.write_file(progress_path, json_content)
    else:
        file_path = workspace_path / progress_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(json_content)


def load_user_reviews(backend: Any) -> Dict[str, List[ResourceReview]]:
    """
    Load all resource reviews.

    Args:
        backend: FilesystemBackend instance

    Returns:
        Dictionary of resource_id -> List of ResourceReview
    """
    reviews_path = "resources/reviews.json"
    reviews = {}

    try:
        if hasattr(backend, "read_file"):
            content = backend.read_file(reviews_path)
        else:
            workspace_path = (
                Path(backend.root_dir) if hasattr(backend, "root_dir") else Path("workspace")
            )
            file_path = workspace_path / reviews_path
            if not file_path.exists():
                return reviews
            content = file_path.read_text()

        data = json.loads(content)
        for review_data in data.get("reviews", []):
            review = ResourceReview(**review_data)
            if review.resource_id not in reviews:
                reviews[review.resource_id] = []
            reviews[review.resource_id].append(review)

    except Exception:
        pass  # Return empty reviews if file doesn't exist

    return reviews


def save_user_reviews(backend: Any, reviews: Dict[str, List[ResourceReview]]) -> None:
    """
    Save resource reviews.

    Args:
        backend: FilesystemBackend instance
        reviews: Dictionary of resource_id -> List of ResourceReview
    """
    reviews_path = "resources/reviews.json"
    workspace_path = Path(backend.root_dir) if hasattr(backend, "root_dir") else Path("workspace")

    all_reviews = []
    for review_list in reviews.values():
        all_reviews.extend([r.to_dict() for r in review_list])

    data = {
        "last_updated": datetime.now().isoformat(),
        "review_count": len(all_reviews),
        "reviews": all_reviews,
    }

    json_content = json.dumps(data, indent=2)

    if hasattr(backend, "write_file"):
        backend.write_file(reviews_path, json_content)
    else:
        file_path = workspace_path / reviews_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(json_content)


def update_resource_rating(resource: Resource, reviews: List[ResourceReview]) -> None:
    """
    Update resource rating based on reviews.

    Args:
        resource: Resource to update
        reviews: List of reviews for the resource
    """
    if not reviews:
        resource.rating = 0.0
        resource.review_count = 0
        return

    ratings = [r.rating for r in reviews]
    resource.rating = round(sum(ratings) / len(ratings), 2)
    resource.review_count = len(ratings)


# ==============================================================================
# Resource Curation Tools Factory
# ==============================================================================


def create_resource_tools(backend=None):
    """
    Create resource curation tools with shared backend instance.

    These tools enable the AI Life Coach to:
    - Add and manage curated resources with rich metadata
    - Search and filter resources by tags, category, difficulty
    - Get personalized recommendations based on user goals
    - Rate and review resources
    - Track user progress through resources

    Based on content curation best practices and personalized learning research.

    Args:
        backend: Optional FilesystemBackend instance. If None, uses get_backend()

    Returns:
        Tuple of resource tools:
        - add_resource: Add a new resource to the catalog
        - search_resources: Search resources by filters
        - get_recommendations: Get personalized resource recommendations
        - rate_resource: Rate and review a resource
        - track_resource_progress: Update progress on a resource
        - get_resource_details: Get detailed info about a resource
        - get_user_resource_stats: Get user's resource consumption stats
        - get_available_tags: Get available tags for a category

    Example:
        >>> from src.config import config
        >>> config.initialize_environment()
        >>> tools = create_resource_tools()
        >>> result = add_resource(
        ...     title="Atomic Habits Summary",
        ...     resource_type="article",
        ...     category="wellness",
        ...     tags=["habit_formation", "productivity"],
        ...     difficulty="beginner",
        ...     estimated_time=20
        ... )
    """
    if backend is None:
        backend = get_backend()

    # Get the workspace directory path from backend
    workspace_path = Path(backend.root_dir) if hasattr(backend, "root_dir") else Path("workspace")

    @tool
    def add_resource(
        title: str,
        resource_type: str,
        category: str,
        description: str,
        tags: Optional[List[str]] = None,
        difficulty: str = "beginner",
        estimated_time: int = 15,
        author: str = "",
        url: str = "",
    ) -> str:
        """Add a new curated resource to the catalog.

        This tool adds resources with comprehensive metadata for personalized
        recommendations. Resources can be articles, books, videos, exercises,
        or tools across all life domains.

        Args:
            title: Resource title (required)
            resource_type: Type - 'article', 'book', 'video', 'exercise', 'tool'
            category: Domain - 'career', 'relationship', 'finance', 'wellness', 'general'
            description: Brief description/summary of the resource
            tags: List of descriptive tags (e.g., ['productivity', 'time_management'])
            difficulty: Level - 'beginner', 'intermediate', 'advanced'
            estimated_time: Time to consume in minutes
            author: Author/creator name
            url: Link to the resource (if applicable)

        Returns:
            Confirmation with resource ID and saved details.

        Example:
            >>> add_resource(
            ...     title="The 7 Habits of Highly Effective People - Summary",
            ...     resource_type="article",
            ...     category="career",
            ...     description="Comprehensive summary of Covey's 7 habits framework",
            ...     tags=["productivity", "leadership", "personal_development"],
            ...     difficulty="intermediate",
            ...     estimated_time=25,
            ...     author="Stephen Covey (summary)",
            ...     url="https://example.com/7-habits-summary"
            ... )
        """
        # Validate inputs
        if not title or not isinstance(title, str):
            return "Error: title must be a non-empty string"
        if resource_type not in [t.value for t in ResourceType]:
            return (
                f"Error: resource_type must be one of: {', '.join([t.value for t in ResourceType])}"
            )
        if category not in [c.value for c in ResourceCategory]:
            return (
                f"Error: category must be one of: {', '.join([c.value for c in ResourceCategory])}"
            )
        if difficulty not in [d.value for d in DifficultyLevel]:
            return (
                f"Error: difficulty must be one of: {', '.join([d.value for d in DifficultyLevel])}"
            )

        try:
            # Load existing catalog
            catalog = load_resource_catalog(backend)

            # Create new resource
            resource = Resource(
                title=title,
                resource_type=resource_type,
                category=category,
                description=description,
                tags=tags or [],
                difficulty=difficulty,
                estimated_time=estimated_time,
                author=author,
                url=url,
            )

            # Add to catalog
            catalog[resource.resource_id] = resource

            # Save catalog
            save_resource_catalog(backend, catalog)

            # Format response
            lines = [
                f"Resource Added Successfully!",
                "=" * 60,
                f"",
                f"ID: {resource.resource_id}",
                f"Title: {title}",
                f"Type: {resource_type}",
                f"Category: {category}",
                f"Difficulty: {difficulty}",
                f"Estimated Time: {estimated_time} minutes",
            ]

            if tags:
                lines.append(f"Tags: {', '.join(tags)}")
            if author:
                lines.append(f"Author: {author}")
            if url:
                lines.append(f"URL: {url}")

            lines.append(f"\nDescription: {description[:150]}...")
            lines.append(f"\nTotal resources in catalog: {len(catalog)}")

            return "\n".join(lines)

        except Exception as e:
            return f"Error adding resource: {str(e)}"

    @tool
    def search_resources(
        query: str = "",
        category: Optional[str] = None,
        resource_type: Optional[str] = None,
        difficulty: Optional[str] = None,
        tags: Optional[List[str]] = None,
        max_time: Optional[int] = None,
        min_rating: Optional[float] = None,
        limit: int = 10,
    ) -> str:
        """Search resources using filters and keywords.

        This tool enables discovery of resources by applying multiple filters
        including category, type, difficulty, tags, and time constraints.

        Args:
            query: Free-text search in title and description
            category: Filter by domain (career, relationship, finance, wellness, general)
            resource_type: Filter by type (article, book, video, exercise, tool)
            difficulty: Filter by level (beginner, intermediate, advanced)
            tags: Filter by tags (list of tag strings)
            max_time: Maximum estimated time in minutes
            min_rating: Minimum rating threshold (0-5)
            limit: Maximum results to return (default: 10)

        Returns:
            List of matching resources with details.

        Example:
            >>> search_resources(
            ...     category="wellness",
            ...     difficulty="beginner",
            ...     tags=["stress_management"],
            ...     max_time=20
            ... )
        """
        try:
            # Load catalog
            catalog = load_resource_catalog(backend)

            if not catalog:
                return "No resources in catalog. Add resources first with add_resource()."

            # Filter resources
            matches = []
            for resource in catalog.values():
                # Category filter
                if category and resource.category != category:
                    continue

                # Type filter
                if resource_type and resource.resource_type != resource_type:
                    continue

                # Difficulty filter
                if difficulty and resource.difficulty != difficulty:
                    continue

                # Tags filter
                if tags:
                    resource_tags = set(t.lower() for t in resource.tags)
                    search_tags = set(t.lower() for t in tags)
                    if not search_tags & resource_tags:  # No overlap
                        continue

                # Max time filter
                if max_time and resource.estimated_time > max_time:
                    continue

                # Min rating filter
                if min_rating and resource.rating < min_rating:
                    continue

                # Text query filter
                if query:
                    query_lower = query.lower()
                    searchable_text = (
                        f"{resource.title} {resource.description} {' '.join(resource.tags)}".lower()
                    )
                    if query_lower not in searchable_text:
                        continue

                matches.append(resource)

            # Sort by rating (highest first), then by title
            matches.sort(key=lambda r: (-r.rating if r.rating > 0 else -1, r.title))

            # Limit results
            matches = matches[:limit]

            # Format response
            lines = [
                f"Resource Search Results",
                "=" * 60,
                f"",
                f"Filters applied:",
            ]

            if query:
                lines.append(f"  Query: '{query}'")
            if category:
                lines.append(f"  Category: {category}")
            if resource_type:
                lines.append(f"  Type: {resource_type}")
            if difficulty:
                lines.append(f"  Difficulty: {difficulty}")
            if tags:
                lines.append(f"  Tags: {', '.join(tags)}")
            if max_time:
                lines.append(f"  Max Time: {max_time} min")
            if min_rating:
                lines.append(f"  Min Rating: {min_rating}/5")

            lines.append(f"\nFound {len(matches)} resource(s):\n")

            if not matches:
                lines.append("No resources match your criteria. Try adjusting filters.")
            else:
                for i, resource in enumerate(matches, 1):
                    rating_str = (
                        f"{'★' * int(resource.rating)}{'☆' * (5 - int(resource.rating))} ({resource.rating})"
                        if resource.rating > 0
                        else "No ratings yet"
                    )
                    lines.append(f"{i}. {resource.title}")
                    lines.append(f"   ID: {resource.resource_id}")
                    lines.append(
                        f"   Type: {resource.resource_type} | Category: {resource.category}"
                    )
                    lines.append(
                        f"   Difficulty: {resource.difficulty} | Time: {resource.estimated_time} min"
                    )
                    lines.append(f"   Rating: {rating_str} ({resource.review_count} reviews)")
                    if resource.tags:
                        lines.append(f"   Tags: {', '.join(resource.tags[:5])}")
                    lines.append("")

            return "\n".join(lines)

        except Exception as e:
            return f"Error searching resources: {str(e)}"

    @tool
    def get_recommendations(
        user_id: str,
        user_goals: Optional[List[Dict[str, Any]]] = None,
        focus_category: str = "general",
        difficulty: str = "intermediate",
        available_time: int = 30,
        resource_type: Optional[str] = None,
        count: int = 5,
    ) -> str:
        """Get personalized resource recommendations based on user goals.

        This tool uses a multi-factor recommendation algorithm that considers:
        - Goal alignment (35%): How well resource matches user's goals
        - Category match (20%): Alignment with focus domain
        - Difficulty match (15%): Appropriate difficulty level
        - Resource rating (15%): Quality based on community ratings
        - Time fit (10%): Fits within available time
        - Diversity (5%): Ensures variety in recommendations

        Args:
            user_id: User's unique identifier
            user_goals: List of user's goals for alignment scoring
            focus_category: Domain to focus on (career, relationship, finance, wellness)
            difficulty: Preferred difficulty level (beginner, intermediate, advanced)
            available_time: Available time in minutes (default: 30)
            resource_type: Optional filter by resource type
            count: Number of recommendations to return (default: 5)

        Returns:
            Personalized recommendations ranked by relevance score.

        Example:
            >>> get_recommendations(
            ...     user_id="user_123",
            ...     user_goals=[
            ...         {"domain": "wellness", "title": "Improve sleep quality"}
            ...     ],
            ...     focus_category="wellness",
            ...     difficulty="beginner",
            ...     available_time=20
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        try:
            # Load catalog
            catalog = load_resource_catalog(backend)

            if not catalog:
                return "No resources available. Add resources to the catalog first."

            # Load user's progress to exclude completed resources
            user_progress = load_user_resource_progress(user_id, backend)
            completed_ids = [
                res_id for res_id, prog in user_progress.items() if prog.status == "completed"
            ]

            # Calculate scores for all resources
            scored_resources = []
            for resource in catalog.values():
                # Type filter
                if resource_type and resource.resource_type != resource_type:
                    continue

                score = calculate_recommendation_score(
                    resource=resource,
                    user_goals=user_goals or [],
                    focus_category=focus_category,
                    user_difficulty=difficulty,
                    available_time=available_time,
                    exclude_ids=completed_ids,
                )

                if score > 0:
                    scored_resources.append((resource, score))

            # Sort by score (highest first)
            scored_resources.sort(key=lambda x: x[1], reverse=True)

            # Get top recommendations
            top_recommendations = scored_resources[:count]

            # Format response
            lines = [
                f"Personalized Resource Recommendations for {user_id}",
                "=" * 60,
                f"",
                f"Focus: {focus_category} | Difficulty: {difficulty} | Time: {available_time} min",
                f"Goals considered: {len(user_goals) if user_goals else 0}",
                f"Completed resources excluded: {len(completed_ids)}",
                f"",
            ]

            if not top_recommendations:
                lines.append(
                    "No recommendations found. Try adjusting your preferences or adding more resources."
                )
            else:
                lines.append(f"Top {len(top_recommendations)} Recommendations:\n")

                for i, (resource, score) in enumerate(top_recommendations, 1):
                    # Get user's progress on this resource
                    prog = user_progress.get(resource.resource_id)
                    status_emoji = (
                        "✓"
                        if prog and prog.status == "completed"
                        else "○"
                        if prog and prog.status == "in_progress"
                        else "•"
                    )

                    rating_str = (
                        f"{'★' * int(resource.rating)}{'☆' * (5 - int(resource.rating))}"
                        if resource.rating > 0
                        else "☆☆☆☆☆"
                    )

                    lines.append(f"{status_emoji} {i}. {resource.title}")
                    lines.append(f"   ID: {resource.resource_id}")
                    lines.append(f"   Match Score: {score * 100:.1f}%")
                    lines.append(
                        f"   Type: {resource.resource_type} | Time: {resource.estimated_time} min | {rating_str}"
                    )
                    lines.append(
                        f"   Tags: {', '.join(resource.tags[:4]) if resource.tags else 'None'}"
                    )

                    if prog:
                        lines.append(f"   Your Status: {prog.status.replace('_', ' ').title()}")

                    lines.append("")

            return "\n".join(lines)

        except Exception as e:
            return f"Error generating recommendations: {str(e)}"

    @tool
    def rate_resource(
        user_id: str,
        resource_id: str,
        rating: int,
        review: str = "",
        would_recommend: bool = True,
    ) -> str:
        """Rate and review a resource.

        This tool allows users to provide feedback on resources, which:
        - Updates the resource's average rating
        - Helps improve recommendations for the user and others
        - Provides qualitative feedback through reviews

        Args:
            user_id: User's unique identifier
            resource_id: Resource ID to rate
            rating: Rating from 1-5 (5 = excellent)
            review: Optional text review
            would_recommend: Whether user would recommend to others

        Returns:
            Confirmation with updated rating and review details.

        Example:
            >>> rate_resource(
            ...     user_id="user_123",
            ...     resource_id="res_20240201093012_1234",
            ...     rating=5,
            ...     review="Excellent resource! Really helped with my morning routine.",
            ...     would_recommend=True
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not resource_id or not isinstance(resource_id, str):
            return "Error: resource_id must be a non-empty string"
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            return "Error: rating must be an integer between 1 and 5"

        try:
            # Load catalog
            catalog = load_resource_catalog(backend)

            if resource_id not in catalog:
                return f"Resource '{resource_id}' not found in catalog."

            resource = catalog[resource_id]

            # Load existing reviews
            reviews = load_user_reviews(backend)

            # Create new review
            review_obj = ResourceReview(
                user_id=user_id,
                resource_id=resource_id,
                rating=rating,
                review=review,
                would_recommend=would_recommend,
            )

            # Add/update review
            if resource_id not in reviews:
                reviews[resource_id] = []

            # Check if user already reviewed this resource
            existing_idx = None
            for idx, r in enumerate(reviews[resource_id]):
                if r.user_id == user_id:
                    existing_idx = idx
                    break

            if existing_idx is not None:
                reviews[resource_id][existing_idx] = review_obj
            else:
                reviews[resource_id].append(review_obj)

            # Save reviews
            save_user_reviews(backend, reviews)

            # Update resource rating
            update_resource_rating(resource, reviews[resource_id])

            # Save updated catalog
            save_resource_catalog(backend, catalog)

            # Update user's resource progress
            user_progress = load_user_resource_progress(user_id, backend)
            if resource_id not in user_progress:
                user_progress[resource_id] = UserResourceProgress(
                    user_id=user_id,
                    resource_id=resource_id,
                )

            user_progress[resource_id].user_rating = rating
            user_progress[resource_id].user_review = review
            save_user_resource_progress(user_id, backend, user_progress)

            # Format response
            stars = "★" * rating + "☆" * (5 - rating)
            lines = [
                f"Resource Rating Submitted",
                "=" * 60,
                f"",
                f"Resource: {resource.title}",
                f"Your Rating: {stars} ({rating}/5)",
                f"Would Recommend: {'Yes' if would_recommend else 'No'}",
            ]

            if review:
                lines.append(f"Review: {review[:200]}...")

            lines.append(f"\nResource now has {resource.review_count} review(s)")
            lines.append(f"Average Rating: {resource.rating}/5")

            return "\n".join(lines)

        except Exception as e:
            return f"Error rating resource: {str(e)}"

    @tool
    def track_resource_progress(
        user_id: str,
        resource_id: str,
        status: str,
        progress_percentage: Optional[int] = None,
        notes: str = "",
    ) -> str:
        """Update progress tracking for a resource.

        This tool tracks user progress through resources:
        - not_started: Haven't begun yet
        - in_progress: Currently working through it
        - completed: Finished the resource

        Progress tracking helps personalize future recommendations and
        provides insights into learning patterns.

        Args:
            user_id: User's unique identifier
            resource_id: Resource ID to track
            status: Progress status - 'not_started', 'in_progress', 'completed'
            progress_percentage: Optional completion percentage (0-100)
            notes: Optional notes about progress

        Returns:
            Confirmation with progress details and next steps.

        Example:
            >>> track_resource_progress(
            ...     user_id="user_123",
            ...     resource_id="res_20240201093012_1234",
            ...     status="completed",
            ...     progress_percentage=100,
            ...     notes="Really helpful, especially section 3 on habit stacking"
            ... )
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not resource_id or not isinstance(resource_id, str):
            return "Error: resource_id must be a non-empty string"
        if status not in [s.value for s in ProgressStatus]:
            return f"Error: status must be one of: {', '.join([s.value for s in ProgressStatus])}"

        try:
            # Load catalog
            catalog = load_resource_catalog(backend)

            if resource_id not in catalog:
                return f"Resource '{resource_id}' not found in catalog."

            resource = catalog[resource_id]

            # Load user's progress
            user_progress = load_user_resource_progress(user_id, backend)

            # Create or update progress
            if resource_id not in user_progress:
                user_progress[resource_id] = UserResourceProgress(
                    user_id=user_id,
                    resource_id=resource_id,
                )

            prog = user_progress[resource_id]

            # Update status
            prog.status = status

            # Update timestamps
            if status == "in_progress" and not prog.started_at:
                prog.started_at = datetime.now().isoformat()
            elif status == "completed":
                if not prog.started_at:
                    prog.started_at = datetime.now().isoformat()
                prog.completed_at = datetime.now().isoformat()
                progress_percentage = 100

            # Update progress percentage
            if progress_percentage is not None:
                prog.progress_percentage = max(0, min(100, progress_percentage))

            # Update notes
            if notes:
                prog.notes = notes

            # Save progress
            save_user_resource_progress(user_id, backend, user_progress)

            # Format response
            status_emoji = {
                "not_started": "○",
                "in_progress": "◐",
                "completed": "✓",
            }.get(status, "•")

            lines = [
                f"Progress Updated",
                "=" * 60,
                f"",
                f"Resource: {resource.title}",
                f"Status: {status_emoji} {status.replace('_', ' ').title()}",
            ]

            if prog.progress_percentage > 0:
                bar_length = 20
                filled = int(bar_length * prog.progress_percentage / 100)
                bar = "█" * filled + "░" * (bar_length - filled)
                lines.append(f"Progress: [{bar}] {prog.progress_percentage}%")

            if prog.started_at:
                lines.append(f"Started: {prog.started_at[:10]}")
            if prog.completed_at:
                lines.append(f"Completed: {prog.completed_at[:10]}")

            if notes:
                lines.append(f"Notes: {notes}")

            # Suggest next steps
            lines.append(f"\n{'=' * 60}")
            if status == "completed":
                lines.append("🎉 Great job completing this resource!")
                lines.append("Consider rating it to help others discover quality content.")
            elif status == "in_progress":
                lines.append("💪 Keep going! Consistency is key to learning.")
            else:
                lines.append("📚 Ready to start? Set aside dedicated time for focused learning.")

            return "\n".join(lines)

        except Exception as e:
            return f"Error tracking progress: {str(e)}"

    @tool
    def get_resource_details(resource_id: str) -> str:
        """Get detailed information about a specific resource.

        This tool retrieves comprehensive details about a resource including
        its metadata, ratings, and reviews.

        Args:
            resource_id: Resource ID to look up

        Returns:
            Detailed resource information including reviews.

        Example:
            >>> get_resource_details("res_20240201093012_1234")
        """
        if not resource_id or not isinstance(resource_id, str):
            return "Error: resource_id must be a non-empty string"

        try:
            # Load catalog
            catalog = load_resource_catalog(backend)

            if resource_id not in catalog:
                return f"Resource '{resource_id}' not found in catalog."

            resource = catalog[resource_id]

            # Load reviews
            reviews = load_user_reviews(backend)
            resource_reviews = reviews.get(resource_id, [])

            # Format response
            rating_str = (
                f"{'★' * int(resource.rating)}{'☆' * (5 - int(resource.rating))} ({resource.rating}/5 from {resource.review_count} reviews)"
                if resource.rating > 0
                else "No ratings yet"
            )

            lines = [
                f"Resource Details",
                "=" * 60,
                f"",
                f"Title: {resource.title}",
                f"ID: {resource.resource_id}",
                f"",
                f"Type: {resource.resource_type}",
                f"Category: {resource.category}",
                f"Difficulty: {resource.difficulty}",
                f"Estimated Time: {resource.estimated_time} minutes",
                f"",
                f"Rating: {rating_str}",
            ]

            if resource.author:
                lines.append(f"Author: {resource.author}")
            if resource.url:
                lines.append(f"URL: {resource.url}")
            if resource.tags:
                lines.append(f"Tags: {', '.join(resource.tags)}")

            lines.append(f"\nDescription:")
            lines.append(resource.description)

            if resource_reviews:
                lines.append(f"\n{'=' * 60}")
                lines.append(f"Reviews ({len(resource_reviews)}):")
                lines.append("=" * 60)

                for review in resource_reviews[:5]:  # Show top 5
                    review_stars = "★" * review.rating + "☆" * (5 - review.rating)
                    lines.append(f"\n{review_stars} - User {review.user_id[:8]}...")
                    if review.review:
                        lines.append(f'  "{review.review[:150]}..."')
                    lines.append(f"  Would recommend: {'Yes' if review.would_recommend else 'No'}")

            return "\n".join(lines)

        except Exception as e:
            return f"Error getting resource details: {str(e)}"

    @tool
    def get_user_resource_stats(user_id: str) -> str:
        """Get resource consumption statistics for a user.

        This tool provides insights into a user's learning patterns:
        - Total resources consumed
        - Breakdown by category and type
        - Average ratings given
        - Time spent learning
        - Completion rates

        Args:
            user_id: User's unique identifier

        Returns:
            Comprehensive resource consumption statistics.

        Example:
            >>> get_user_resource_stats("user_123")
        """
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        try:
            # Load user's progress
            user_progress = load_user_resource_progress(user_id, backend)

            if not user_progress:
                return (
                    f"No resource activity found for user '{user_id}'. Start exploring resources!"
                )

            # Load catalog for resource details
            catalog = load_resource_catalog(backend)

            # Calculate statistics
            total_resources = len(user_progress)
            completed = sum(1 for p in user_progress.values() if p.status == "completed")
            in_progress = sum(1 for p in user_progress.values() if p.status == "in_progress")
            not_started = sum(1 for p in user_progress.values() if p.status == "not_started")

            # Category breakdown
            category_counts = {}
            type_counts = {}
            total_time = 0
            ratings_given = []

            for res_id, prog in user_progress.items():
                if res_id in catalog:
                    resource = catalog[res_id]
                    category_counts[resource.category] = (
                        category_counts.get(resource.category, 0) + 1
                    )
                    type_counts[resource.resource_type] = (
                        type_counts.get(resource.resource_type, 0) + 1
                    )

                    if prog.status == "completed":
                        total_time += resource.estimated_time

                if prog.user_rating:
                    ratings_given.append(prog.user_rating)

            # Format response
            completion_rate = (completed / total_resources * 100) if total_resources > 0 else 0
            avg_rating = sum(ratings_given) / len(ratings_given) if ratings_given else 0

            lines = [
                f"Resource Consumption Statistics for {user_id}",
                "=" * 60,
                f"",
                f"Total Resources: {total_resources}",
                f"Completed: {completed} ({completion_rate:.1f}%)",
                f"In Progress: {in_progress}",
                f"Not Started: {not_started}",
                f"",
                f"Total Learning Time: {total_time} minutes ({total_time // 60} hours)",
            ]

            if ratings_given:
                lines.append(
                    f"Average Rating Given: {avg_rating:.1f}/5 ({len(ratings_given)} ratings)"
                )

            lines.append(f"\nBy Category:")
            for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
                lines.append(f"  {cat.capitalize()}: {count}")

            lines.append(f"\nBy Resource Type:")
            for res_type, count in sorted(type_counts.items(), key=lambda x: -x[1]):
                lines.append(f"  {res_type.capitalize()}: {count}")

            # Provide insights
            lines.append(f"\n{'=' * 60}")
            if completion_rate >= 70:
                lines.append("🌟 Excellent completion rate! You're a dedicated learner.")
            elif completion_rate >= 40:
                lines.append(
                    "📚 Good progress! Try to complete resources before starting new ones."
                )
            else:
                lines.append(
                    "💡 Tip: Focus on completing in-progress resources before exploring new ones."
                )

            return "\n".join(lines)

        except Exception as e:
            return f"Error getting user stats: {str(e)}"

    @tool
    def get_available_tags(category: str = "general") -> str:
        """Get available tags for a specific category.

        This tool returns the predefined tag taxonomy to help with
        consistent resource tagging.

        Args:
            category: Category to get tags for (career, relationship, finance, wellness, general)

        Returns:
            List of available tags for the category.

        Example:
            >>> get_available_tags("wellness")
        """
        if category not in TAG_TAXONOMY:
            return f"Error: category must be one of: {', '.join(TAG_TAXONOMY.keys())}"

        tags = TAG_TAXONOMY[category]

        lines = [
            f"Available Tags for {category.capitalize()}",
            "=" * 60,
            f"",
            f"Total tags: {len(tags)}\n",
        ]

        for i, tag in enumerate(tags, 1):
            lines.append(f"  {i}. {tag}")

        lines.append(f"\nUse these tags when adding resources for consistent categorization.")

        return "\n".join(lines)

    print("Resource curation tools created successfully!")
    return (
        add_resource,
        search_resources,
        get_recommendations,
        rate_resource,
        track_resource_progress,
        get_resource_details,
        get_user_resource_stats,
        get_available_tags,
    )


# Export tools at module level for convenience
__all__ = [
    "create_resource_tools",
    "Resource",
    "UserResourceProgress",
    "ResourceReview",
    "ResourceType",
    "ResourceCategory",
    "DifficultyLevel",
    "ProgressStatus",
    "TAG_TAXONOMY",
]
