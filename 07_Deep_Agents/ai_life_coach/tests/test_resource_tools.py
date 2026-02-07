"""
Test suite for Resource Curation System tools.

This module provides comprehensive tests for the resource curation system,
including:
- Resource catalog management (add, search)
- Recommendation engine with multi-factor scoring
- Resource rating and review system
- Progress tracking (not started, in progress, completed)
- Tag taxonomy and categorization
"""

import pytest
from pathlib import Path

# Import resource tools and helper functions
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.resource_tools import (
    Resource,
    UserResourceProgress,
    ResourceReview,
    TAG_TAXONOMY,
    sanitize_filename,
    calculate_goal_alignment_score,
    calculate_difficulty_match_score,
    calculate_time_fit_score,
    calculate_recommendation_score,
    update_resource_rating,
)


# ==============================================================================
# Data Model Tests
# ==============================================================================


def test_resource_creation():
    """Test Resource data model creation."""
    resource = Resource(
        title="Test Resource",
        resource_type="article",
        category="wellness",
        description="A test resource",
        tags=["stress_management", "mindfulness"],
        difficulty="beginner",
        estimated_time=20,
    )

    assert resource.title == "Test Resource"
    assert resource.resource_type == "article"
    assert resource.category == "wellness"
    assert resource.difficulty == "beginner"
    assert resource.estimated_time == 20
    assert len(resource.tags) == 2
    assert resource.resource_id.startswith("res_")


def test_resource_to_dict():
    """Test Resource serialization to dictionary."""
    resource = Resource(
        title="Test",
        resource_type="book",
        category="career",
        description="Test book",
    )

    data = resource.to_dict()

    assert data["title"] == "Test"
    assert data["resource_type"] == "book"
    assert data["category"] == "career"
    assert "resource_id" in data
    assert "created_at" in data


def test_resource_from_dict():
    """Test Resource deserialization from dictionary."""
    data = {
        "resource_id": "res_123",
        "title": "Test Resource",
        "resource_type": "video",
        "category": "finance",
        "tags": ["budgeting", "saving"],
        "difficulty": "intermediate",
        "estimated_time": 30,
        "author": "Test Author",
        "url": "https://example.com",
        "description": "Test description",
        "rating": 4.5,
        "review_count": 10,
        "created_at": "2024-01-01T00:00:00",
    }

    resource = Resource.from_dict(data)

    assert resource.resource_id == "res_123"
    assert resource.title == "Test Resource"
    assert resource.rating == 4.5
    assert resource.review_count == 10


def test_user_resource_progress():
    """Test UserResourceProgress data model."""
    progress = UserResourceProgress(
        user_id="user_123",
        resource_id="res_456",
        status="in_progress",
        progress_percentage=50,
    )

    assert progress.user_id == "user_123"
    assert progress.status == "in_progress"
    assert progress.progress_percentage == 50

    # Test serialization
    data = progress.to_dict()
    assert data["status"] == "in_progress"

    # Test deserialization
    restored = UserResourceProgress.from_dict(data)
    assert restored.user_id == "user_123"


# ==============================================================================
# Helper Function Tests
# ==============================================================================


def test_sanitize_filename():
    """Test filename sanitization."""
    # Test normal text
    assert sanitize_filename("Hello World") == "hello_world"

    # Test special characters
    assert sanitize_filename("Test@File#Name!") == "test_file_name_"

    # Test truncation (50 char limit)
    long_name = "A" * 60
    assert len(sanitize_filename(long_name)) == 50


def test_calculate_goal_alignment_score():
    """Test goal alignment scoring."""
    resource = Resource(
        title="Stress Management Techniques",
        resource_type="article",
        category="wellness",
        description="Learn to manage stress effectively",
        tags=["stress_management", "mindfulness", "wellness"],
    )

    # Test with matching goal
    goals = [
        {
            "domain": "wellness",
            "title": "Reduce stress",
            "description": "Manage daily stress better",
        }
    ]
    score = calculate_goal_alignment_score(resource, goals)
    assert 0.4 <= score <= 1.0  # Should have good alignment

    # Test with no goals
    score = calculate_goal_alignment_score(resource, [])
    assert score == 0.5  # Neutral score

    # Test with non-matching goal
    goals = [{"domain": "finance", "title": "Save money", "description": "Build savings"}]
    score = calculate_goal_alignment_score(resource, goals)
    assert score < 0.4  # Lower alignment


def test_calculate_difficulty_match_score():
    """Test difficulty match scoring."""
    resource = Resource(
        title="Test",
        resource_type="article",
        category="general",
        description="Test",
        difficulty="intermediate",
    )

    # Perfect match
    assert calculate_difficulty_match_score(resource, "intermediate") == 1.0

    # One level difference
    assert calculate_difficulty_match_score(resource, "beginner") == 0.7
    assert calculate_difficulty_match_score(resource, "advanced") == 0.7

    # Two level difference
    beginner_resource = Resource(
        title="Test",
        resource_type="article",
        category="general",
        description="Test",
        difficulty="beginner",
    )
    assert calculate_difficulty_match_score(beginner_resource, "advanced") == 0.4


def test_calculate_time_fit_score():
    """Test time fit scoring."""
    resource = Resource(
        title="Test",
        resource_type="article",
        category="general",
        description="Test",
        estimated_time=30,
    )

    # Perfect fit
    assert calculate_time_fit_score(resource, 30) == 1.0

    # Resource fits within available time
    assert calculate_time_fit_score(resource, 60) == 1.0

    # Resource exceeds available time
    assert calculate_time_fit_score(resource, 20) < 1.0
    assert calculate_time_fit_score(resource, 20) > 0.0

    # Resource significantly exceeds available time
    assert calculate_time_fit_score(resource, 10) == 0.0


def test_calculate_recommendation_score():
    """Test comprehensive recommendation scoring."""
    resource = Resource(
        title="Productivity Tips",
        resource_type="article",
        category="career",
        description="Boost your productivity",
        tags=["productivity", "time_management"],
        difficulty="intermediate",
        estimated_time=20,
        rating=4.5,
    )

    goals = [{"domain": "career", "title": "Improve productivity", "description": "Get more done"}]

    score = calculate_recommendation_score(
        resource=resource,
        user_goals=goals,
        focus_category="career",
        user_difficulty="intermediate",
        available_time=30,
    )

    assert 0.5 <= score <= 1.0  # Should have good score

    # Test with excluded resource
    score = calculate_recommendation_score(
        resource=resource,
        user_goals=goals,
        exclude_ids=[resource.resource_id],
    )
    assert score == 0.0


def test_update_resource_rating():
    """Test resource rating update."""
    resource = Resource(
        title="Test",
        resource_type="article",
        category="general",
        description="Test",
    )

    # No reviews
    update_resource_rating(resource, [])
    assert resource.rating == 0.0
    assert resource.review_count == 0

    # With reviews
    reviews = [
        ResourceReview(user_id="u1", resource_id="r1", rating=5),
        ResourceReview(user_id="u2", resource_id="r1", rating=4),
        ResourceReview(user_id="u3", resource_id="r1", rating=3),
    ]

    update_resource_rating(resource, reviews)
    assert resource.rating == 4.0  # Average of 5, 4, 3
    assert resource.review_count == 3


# ==============================================================================
# Tag Taxonomy Tests
# ==============================================================================


def test_tag_taxonomy_structure():
    """Test that tag taxonomy has expected structure."""
    assert "career" in TAG_TAXONOMY
    assert "wellness" in TAG_TAXONOMY
    assert "relationship" in TAG_TAXONOMY
    assert "finance" in TAG_TAXONOMY
    assert "general" in TAG_TAXONOMY

    # Check that each category has tags
    for category, tags in TAG_TAXONOMY.items():
        assert len(tags) > 0
        assert all(isinstance(tag, str) for tag in tags)


# ==============================================================================
# Tool Integration Tests
# ==============================================================================


@pytest.fixture
def backend():
    """Create a mock backend for testing."""

    class MockBackend:
        def __init__(self):
            self.root_dir = Path("workspace")
            self.files = {}

        def write_file(self, path, content):
            self.files[path] = content
            full_path = self.root_dir / path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)

        def read_file(self, path):
            if path in self.files:
                return self.files[path]
            full_path = self.root_dir / path
            if full_path.exists():
                return full_path.read_text()
            raise FileNotFoundError(f"File not found: {path}")

    mock_backend = MockBackend()

    # Initialize config
    try:
        from src.config import config

        config.initialize_environment()
    except Exception:
        pass

    yield mock_backend


@pytest.fixture
def resource_tools(backend):
    """Create resource tools with mock backend."""
    from src.tools.resource_tools import create_resource_tools

    return create_resource_tools(backend)


def test_add_resource_basic(backend, resource_tools):
    """Test basic resource addition."""
    add_resource = resource_tools[0]

    result = add_resource.invoke(
        {
            "title": "Test Resource Article",
            "resource_type": "article",
            "category": "wellness",
            "description": "A comprehensive article about wellness",
            "tags": ["stress_management", "mindfulness"],
            "difficulty": "beginner",
            "estimated_time": 20,
            "author": "Test Author",
            "url": "https://example.com/article",
        }
    )

    assert "Resource Added Successfully" in result
    assert "Test Resource Article" in result
    assert "article" in result
    assert "wellness" in result

    # Verify file was created
    catalog_path = "resources/catalog.json"
    assert backend.read_file(catalog_path) is not None


def test_add_resource_validation(backend, resource_tools):
    """Test resource input validation."""
    add_resource = resource_tools[0]

    # Test invalid resource type
    result = add_resource.invoke(
        {
            "title": "Test",
            "resource_type": "invalid_type",
            "category": "wellness",
            "description": "Test",
        }
    )
    assert "Error" in result

    # Test invalid category
    result = add_resource.invoke(
        {
            "title": "Test",
            "resource_type": "article",
            "category": "invalid_category",
            "description": "Test",
        }
    )
    assert "Error" in result


def test_search_resources(backend, resource_tools):
    """Test resource search functionality."""
    add_resource = resource_tools[0]
    search_resources = resource_tools[1]

    # Add test resources
    add_resource.invoke(
        {
            "title": "Productivity Hacks",
            "resource_type": "article",
            "category": "career",
            "description": "Boost your productivity",
            "tags": ["productivity", "time_management"],
            "difficulty": "beginner",
            "estimated_time": 15,
        }
    )

    add_resource.invoke(
        {
            "title": "Stress Management Guide",
            "resource_type": "book",
            "category": "wellness",
            "description": "Comprehensive stress management",
            "tags": ["stress_management", "mindfulness"],
            "difficulty": "intermediate",
            "estimated_time": 120,
        }
    )

    # Test category filter
    result = search_resources.invoke(
        {
            "category": "career",
        }
    )
    assert "Productivity Hacks" in result
    assert "Stress Management Guide" not in result

    # Test tag filter
    result = search_resources.invoke(
        {
            "tags": ["stress_management"],
        }
    )
    assert "Stress Management Guide" in result


def test_get_recommendations(backend, resource_tools):
    """Test recommendation engine."""
    add_resource = resource_tools[0]
    get_recommendations = resource_tools[2]

    # Add test resources
    add_resource.invoke(
        {
            "title": "Career Growth Strategies",
            "resource_type": "article",
            "category": "career",
            "description": "How to grow your career",
            "tags": ["career", "leadership"],
            "difficulty": "intermediate",
            "estimated_time": 25,
            "rating": 4.5,
        }
    )

    # Get recommendations
    result = get_recommendations.invoke(
        {
            "user_id": "test_user_1",
            "user_goals": [
                {"domain": "career", "title": "Advance my career", "description": "Get promoted"}
            ],
            "focus_category": "career",
            "difficulty": "intermediate",
            "available_time": 30,
            "count": 5,
        }
    )

    assert "Personalized Resource Recommendations" in result
    assert "Career Growth Strategies" in result


def test_rate_resource(backend, resource_tools):
    """Test resource rating."""
    add_resource = resource_tools[0]
    rate_resource = resource_tools[3]

    # Add a resource first
    add_result = add_resource.invoke(
        {
            "title": "Test Resource for Rating",
            "resource_type": "article",
            "category": "wellness",
            "description": "Test resource",
        }
    )

    # Extract resource ID from result
    import re

    match = re.search(r"ID: (res_\d+_\d+)", add_result)
    assert match is not None
    resource_id = match.group(1)

    # Rate the resource
    result = rate_resource.invoke(
        {
            "user_id": "test_user",
            "resource_id": resource_id,
            "rating": 5,
            "review": "Excellent resource! Very helpful.",
            "would_recommend": True,
        }
    )

    assert "Resource Rating Submitted" in result
    assert "★" in result


def test_track_resource_progress(backend, resource_tools):
    """Test progress tracking."""
    add_resource = resource_tools[0]
    track_progress = resource_tools[4]

    # Add a resource
    add_result = add_resource.invoke(
        {
            "title": "Progress Test Resource",
            "resource_type": "book",
            "category": "finance",
            "description": "Test resource for progress",
            "estimated_time": 60,
        }
    )

    # Extract resource ID
    import re

    match = re.search(r"ID: (res_\d+_\d+)", add_result)
    resource_id = match.group(1)

    # Start progress
    result = track_progress.invoke(
        {
            "user_id": "test_user",
            "resource_id": resource_id,
            "status": "in_progress",
            "progress_percentage": 25,
            "notes": "Reading chapter 2",
        }
    )

    assert "Progress Updated" in result
    assert "In Progress" in result
    assert "25%" in result

    # Complete progress
    result = track_progress.invoke(
        {
            "user_id": "test_user",
            "resource_id": resource_id,
            "status": "completed",
            "notes": "Finished!",
        }
    )

    assert "Completed" in result
    assert "100%" in result


def test_get_resource_details(backend, resource_tools):
    """Test getting resource details."""
    add_resource = resource_tools[0]
    get_details = resource_tools[5]

    # Add a resource
    add_result = add_resource.invoke(
        {
            "title": "Detailed Test Resource",
            "resource_type": "article",
            "category": "relationship",
            "description": "This is a detailed description.",
            "tags": ["communication", "trust_building"],
            "difficulty": "advanced",
            "estimated_time": 45,
            "author": "Dr. Test",
        }
    )

    # Extract resource ID
    import re

    match = re.search(r"ID: (res_\d+_\d+)", add_result)
    resource_id = match.group(1)

    # Get details
    result = get_details.invoke(
        {
            "resource_id": resource_id,
        }
    )

    assert "Resource Details" in result
    assert "Detailed Test Resource" in result
    assert "relationship" in result
    assert "advanced" in result


def test_get_user_resource_stats(backend, resource_tools):
    """Test user resource statistics."""
    add_resource = resource_tools[0]
    track_progress = resource_tools[4]
    get_stats = resource_tools[6]

    # Add resources
    add_result1 = add_resource.invoke(
        {
            "title": "Stats Test Resource 1",
            "resource_type": "article",
            "category": "wellness",
            "description": "Test",
            "estimated_time": 20,
        }
    )

    add_result2 = add_resource.invoke(
        {
            "title": "Stats Test Resource 2",
            "resource_type": "video",
            "category": "career",
            "description": "Test",
            "estimated_time": 30,
        }
    )

    # Extract IDs
    import re

    match1 = re.search(r"ID: (res_\d+_\d+)", add_result1)
    match2 = re.search(r"ID: (res_\d+_\d+)", add_result2)
    resource_id1 = match1.group(1)
    resource_id2 = match2.group(1)

    # Track progress for user
    track_progress.invoke(
        {
            "user_id": "stats_user",
            "resource_id": resource_id1,
            "status": "completed",
        }
    )

    track_progress.invoke(
        {
            "user_id": "stats_user",
            "resource_id": resource_id2,
            "status": "in_progress",
            "progress_percentage": 50,
        }
    )

    # Get stats
    result = get_stats.invoke(
        {
            "user_id": "stats_user",
        }
    )

    assert "Resource Consumption Statistics" in result
    assert "Total Resources:" in result
    assert "Completed:" in result


def test_get_available_tags(backend, resource_tools):
    """Test getting available tags."""
    get_tags = resource_tools[7]

    result = get_tags.invoke(
        {
            "category": "wellness",
        }
    )

    assert "Available Tags for Wellness" in result
    assert "stress_management" in result or "nutrition" in result

    # Test invalid category
    result = get_tags.invoke(
        {
            "category": "invalid",
        }
    )
    assert "Error" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
