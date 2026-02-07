"""
Context tools for AI Life Coach.

This module provides LangChain tools that enable agents to manage workspace
context files including user profiles, assessments, plans, progress tracking,
and curated resources. All tools use the FilesystemBackend for persistent
file storage in the workspace directory.

Tools:
- save_assessment: Save user wellness assessments as JSON files
- get_active_plan: Retrieve a user's current active plan (Markdown)
- save_weekly_progress: Save weekly progress summaries as JSON
- list_user_assessments: List all assessments for a user
- read_assessment: Read a specific assessment by date
- save_curated_resource: Save curated resources (articles, links) for user reference

Directory Structure:
    workspace/
    ├── user_profile/{user_id}/profile.json
    ├── assessments/{user_id}/{YYYY-MM-DD}_assessment.json
    ├── plans/{user_id}/{plan_name}.md
    ├── progress/{user_id}/week_{n}_summary.json
    └── resources/curated_articles/
"""

from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, List, Optional
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
# Context Tool Factory
# ==============================================================================


def create_context_tools(backend=None) -> tuple:
    """
    Create context tools with shared FilesystemBackend instance.

    These tools enable agents to persist and retrieve context information
    across sessions, providing a form of long-term memory through the filesystem.

    Args:
        backend: Optional FilesystemBackend instance. If None, uses get_backend()

    Returns:
        Tuple of context tools (save_assessment, get_active_plan,
                               save_weekly_progress, list_user_assessments,
                               read_assessment, save_curated_resource)

    Example:
        >>> from src.config import config
        >>> config.initialize_environment()
        >>> tools = create_context_tools()
        >>> result = save_assessment("user_123", {"energy": 5, "stress_level": 3})
    """
    if backend is None:
        backend = get_backend()

    # Get the workspace directory path from backend
    workspace_path = Path(backend.root_dir) if hasattr(backend, "root_dir") else Path("workspace")

    @tool
    def save_assessment(user_id: str, assessment_data: Dict[str, Any]) -> str:
        """Save a user's wellness assessment as a JSON file.

        This tool stores wellness assessments with timestamps, enabling
        tracking of user progress across multiple sessions. Assessments are
        stored as JSON files in the assessments/{user_id}/ directory.

        Args:
            user_id: The user's unique identifier (must be non-empty string)
            assessment_data: Dictionary containing assessment information:
                - energy_level (int, 1-10): Self-reported energy level
                - stress_level (int, 1-10): Current stress level
                - sleep_quality (str: poor/fair/good/excellent): Sleep quality rating
                - mood (str): Current mood state
                - physical_activity (int, 1-10): Activity level
                - nutrition_score (int, 1-10): Nutrition quality rating
                - notes (str, optional): Additional qualitative feedback

        Returns:
            Confirmation message with file path and timestamp.
            If an error occurs, returns a helpful error message.

        Raises:
            ValueError: If user_id is empty or assessment_data is invalid

        Example:
            >>> save_assessment("user_123", {
            ...     "energy_level": 7,
            ...     "stress_level": 4,
            ...     "sleep_quality": "good",
            ...     "mood": "positive"
            ... })
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not assessment_data or not isinstance(assessment_data, dict):
            return "Error: assessment_data must be a non-empty dictionary"

        try:
            # Generate timestamp for filename
            today = date.today()
            timestamp_str = datetime.now().isoformat()

            # Prepare assessment data
            assessment_record = {
                "user_id": user_id,
                "date": today.isoformat(),
                "timestamp": timestamp_str,
                **assessment_data,
            }

            # Convert to JSON string with proper formatting
            json_content = json.dumps(assessment_record, indent=2)

            # Write to file using backend
            path = f"assessments/{user_id}/{today}_assessment.json"

            # Use backend's write_file if available, otherwise use direct file writing
            if hasattr(backend, "write_file"):
                result = backend.write_file(path, json_content)
            else:
                # Fallback: Write directly to filesystem
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)
                result = f"File written to {path}"

            return (
                f"Assessment saved for user '{user_id}' on {today}.\n"
                f"Path: {path}\n"
                f"Timestamp: {timestamp_str}"
            )

        except Exception as e:
            return f"Error saving assessment for user '{user_id}': {str(e)}"

    @tool
    def get_active_plan(user_id: str) -> str:
        """Retrieve a user's current active plan from the plans directory.

        This tool searches for and retrieves the most recent plan file
        (.md) in the plans/{user_id}/ directory. Plans are stored as
        Markdown for readability and easy editing.

        Args:
            user_id: The user's unique identifier (must be non-empty string)

        Returns:
            Plan content as formatted text. If no plan file exists,
            returns a helpful message indicating no active plan.
            If multiple plans exist, retrieves the most recently modified one.

        Raises:
            ValueError: If user_id is empty

        Example:
            >>> get_active_plan("user_123")
            'Active Plan for user_123:\\n## 90-Day Wellness Challenge\\n...'
        """
        # Validate input
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        try:
            # Search for plan files in the user's plans directory
            plans_dir = workspace_path / "plans" / user_id

            if not plans_dir.exists():
                return f"No plan directory found for user '{user_id}'. Create a plan first."

            # Find all .md files
            plan_files = list(plans_dir.glob("*.md"))

            if not plan_files:
                return f"No plan files found for user '{user_id}'. Create a plan first."

            # Get the most recently modified file
            latest_plan = max(plan_files, key=lambda f: f.stat().st_mtime)

            # Read the plan content
            if hasattr(backend, "read_file"):
                rel_path = f"plans/{user_id}/{latest_plan.name}"
                content = backend.read_file(rel_path)
            else:
                content = latest_plan.read_text()

            # Format the response
            modified_time = datetime.fromtimestamp(latest_plan.stat().st_mtime)
            return (
                f"Active Plan for user '{user_id}':\n"
                f"File: {latest_plan.name}\n"
                f"Last Modified: {modified_time.strftime('%Y-%m-%d %H:%M')}\n"
                f"{'=' * 60}\n\n{content}"
            )

        except Exception as e:
            return f"Error retrieving plan for user '{user_id}': {str(e)}"

    @tool
    def save_weekly_progress(user_id: str, week_data: Dict[str, Any]) -> str:
        """Save a weekly progress summary as a JSON file.

        This tool stores structured weekly progress data, enabling agents
        to track user progress over time and generate insights. Progress
        summaries are stored in the progress/{user_id}/ directory.

        Args:
            user_id: The user's unique identifier (must be non-empty string)
            week_data: Dictionary containing weekly progress information:
                - week_number (int, required): Week number in the program
                - completion_rate (float, 0-1): Percentage of planned tasks completed
                - achievements (list[str]): List of accomplishments for the week
                - challenges (list[str]): List of difficulties encountered
                - average_mood (str): Average mood for the week
                - energy_trend (str: improving/stable/declining): Energy level trend
                - notes (str, optional): Additional qualitative summary

        Returns:
            Confirmation message with file path and week number.
            If an error occurs, returns a helpful error message.

        Raises:
            ValueError: If user_id is empty or week_data lacks required fields

        Example:
            >>> save_weekly_progress("user_123", {
            ...     "week_number": 1,
            ...     "completion_rate": 0.85,
            ...     "achievements": ["Started morning routine", "Exercised 3 times"]
            ... })
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not week_data or not isinstance(week_data, dict):
            return "Error: week_data must be a non-empty dictionary"

        # Validate required fields
        if "week_number" not in week_data:
            return "Error: week_data must contain 'week_number' field"

        try:
            # Prepare progress data
            timestamp_str = datetime.now().isoformat()

            progress_record = {"user_id": user_id, "timestamp": timestamp_str, **week_data}

            # Convert to JSON string with proper formatting
            json_content = json.dumps(progress_record, indent=2)

            # Write to file using backend
            week_num = week_data["week_number"]
            path = f"progress/{user_id}/week_{week_num}_summary.json"

            # Use backend's write_file if available, otherwise use direct file writing
            if hasattr(backend, "write_file"):
                result = backend.write_file(path, json_content)
            else:
                # Fallback: Write directly to filesystem
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(json_content)
                result = f"File written to {path}"

            return (
                f"Weekly progress saved for user '{user_id}'.\n"
                f"Week: {week_num}\n"
                f"Path: {path}\n"
                f"Timestamp: {timestamp_str}"
            )

        except Exception as e:
            return f"Error saving weekly progress for user '{user_id}': {str(e)}"

    @tool
    def list_user_assessments(user_id: str) -> str:
        """List all assessments for a specific user.

        This tool retrieves and lists metadata for all assessment files
        associated with a user, providing an overview of their assessment history.

        Args:
            user_id: The user's unique identifier (must be non-empty string)

        Returns:
            Formatted list of assessments with dates and key metrics.
            If no assessments found, returns a helpful message.

        Raises:
            ValueError: If user_id is empty

        Example:
            >>> list_user_assessments("user_123")
            'Assessments for user_123:\\n- 2026-02-05: Energy=7, Stress=4\\n...'
        """
        # Validate input
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"

        try:
            # Search for assessment files in the user's assessments directory
            assessments_dir = workspace_path / "assessments" / user_id

            if not assessments_dir.exists():
                return f"No assessment directory found for user '{user_id}'."

            # Find all JSON files
            assessment_files = sorted(assessments_dir.glob("*_assessment.json"))

            if not assessment_files:
                return f"No assessments found for user '{user_id}'."

            # Build formatted list
            parts = [
                f"Assessments for user '{user_id}':",
                f"Total: {len(assessment_files)} assessments\n",
            ]

            for file_path in assessment_files:
                # Parse date from filename
                date_str = file_path.stem.replace("_assessment", "")

                # Read and parse the assessment data
                try:
                    if hasattr(backend, "read_file"):
                        rel_path = f"assessments/{user_id}/{file_path.name}"
                        content_str = backend.read_file(rel_path)
                    else:
                        content_str = file_path.read_text()

                    data = json.loads(content_str)

                    # Extract key metrics
                    energy_level = data.get("energy_level", "N/A")
                    stress_level = data.get("stress_level", "N/A")
                    mood = data.get("mood", "N/A")

                    parts.append(
                        f"  - {date_str}: Energy={energy_level}, Stress={stress_level}, Mood={mood}"
                    )

                except Exception as parse_error:
                    parts.append(f"  - {date_str}: [Error reading file: {parse_error}]")

            return "\n".join(parts)

        except Exception as e:
            return f"Error listing assessments for user '{user_id}': {str(e)}"

    @tool
    def read_assessment(user_id: str, assessment_date: str) -> str:
        """Read a specific assessment by date.

        This tool retrieves the full content of an assessment file for
        a given user and date, providing detailed information about that
        particular wellness check-in.

        Args:
            user_id: The user's unique identifier (must be non-empty string)
            assessment_date: Date of the assessment in YYYY-MM-DD format

        Returns:
            Full assessment content as formatted text. If not found,
            returns a helpful message indicating the file doesn't exist.

        Raises:
            ValueError: If user_id is empty or date format is invalid

        Example:
            >>> read_assessment("user_123", "2026-02-05")
        """
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            return "Error: user_id must be a non-empty string"
        if not assessment_date or not isinstance(assessment_date, str):
            return "Error: assessment_date must be a string in YYYY-MM-DD format"

        try:
            # Validate date format
            datetime.strptime(assessment_date, "%Y-%m-%d")
        except ValueError:
            return "Error: assessment_date must be in YYYY-MM-DD format"

        try:
            # Build file path
            path = f"assessments/{user_id}/{assessment_date}_assessment.json"

            # Read the file
            if hasattr(backend, "read_file"):
                content_str = backend.read_file(path)
            else:
                file_path = workspace_path / path
                if not file_path.exists():
                    return f"No assessment found for user '{user_id}' on date '{assessment_date}'."
                content_str = file_path.read_text()

            # Parse and format the data
            data = json.loads(content_str)

            parts = [f"Assessment for user '{user_id}' on {assessment_date}:", "=" * 60]

            # Format all fields nicely
            for key, value in sorted(data.items()):
                if isinstance(value, dict):
                    parts.append(f"\n{key.upper()}:")
                    for sub_key, sub_value in sorted(value.items()):
                        parts.append(f"  {sub_key}: {sub_value}")
                elif isinstance(value, list):
                    parts.append(f"\n{key.upper()}:")
                    for item in value:
                        parts.append(f"  - {item}")
                else:
                    parts.append(f"{key}: {value}")

            return "\n".join(parts)

        except FileNotFoundError:
            return f"No assessment found for user '{user_id}' on date '{assessment_date}'."
        except Exception as e:
            return f"Error reading assessment for user '{user_id}': {str(e)}"

    @tool
    def save_curated_resource(
        title: str, category: str, content: str, user_id: Optional[str] = None
    ) -> str:
        """Save a curated resource (article, guide, tip) for user reference.

        This tool stores curated resources such as articles, guides,
        or tips that can be referenced during coaching sessions.
        Resources are organized by category for easy retrieval.

        Args:
            title: Title of the resource (must be non-empty string)
            category: Category for organization (e.g., "exercise", "nutrition",
                     "stress_management", "career_tips")
            content: Content of the resource (article text, guide, tips)
            user_id: Optional user ID. If provided, saves to user-specific
                     resources. Otherwise, saves to general curated_articles.

        Returns:
            Confirmation message with file path and resource details.
            If an error occurs, returns a helpful error message.

        Raises:
            ValueError: If title or content is empty

        Example:
            >>> save_curated_resource(
            ...     "Morning Routine Guide",
            ...     "wellness_tips",
            ...     "Start your day with 10 minutes of meditation..."
            ... )
        """
        # Validate inputs
        if not title or not isinstance(title, str):
            return "Error: title must be a non-empty string"
        if not category or not isinstance(category, str):
            return "Error: category must be a non-empty string"
        if not content or not isinstance(content, str):
            return "Error: content must be a non-empty string"

        try:
            # Sanitize title for filename
            safe_title = "".join(
                c if c.isalnum() or c in (" ", "-", "_") else "_" for c in title
            ).strip()
            safe_title = safe_title.replace(" ", "_")

            # Generate timestamp
            timestamp_str = datetime.now().isoformat()
            date_str = date.today().isoformat()

            # Prepare resource data
            if user_id:
                path = f"resources/{user_id}/{category}/{date_str}_{safe_title}.md"
            else:
                path = f"resources/curated_articles/{category}/{date_str}_{safe_title}.md"

            # Format as Markdown
            markdown_content = f"""# {title}

**Category**: {category}
**Saved**: {timestamp_str}

---

{content}
"""

            # Write to file using backend
            if hasattr(backend, "write_file"):
                result = backend.write_file(path, markdown_content)
            else:
                # Fallback: Write directly to filesystem
                file_path = workspace_path / path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(markdown_content)
                result = f"File written to {path}"

            target = f"user '{user_id}'" if user_id else "general resources"
            return (
                f"Resource saved to {target}.\nTitle: {title}\nCategory: {category}\nPath: {path}"
            )

        except Exception as e:
            return f"Error saving resource '{title}': {str(e)}"

    print("Context tools created successfully!")
    return (
        save_assessment,
        get_active_plan,
        save_weekly_progress,
        list_user_assessments,
        read_assessment,
        save_curated_resource,
    )


# Export tools at module level for convenience
__all__ = [
    "create_context_tools",
]
