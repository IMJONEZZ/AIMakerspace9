"""
Configuration module for AI Life Coach.

Handles environment variables, model initialization, and system-wide settings.
"""

import os
from pathlib import Path
from typing import Any, Optional

# Deep Agents imports
from deepagents.backends import FilesystemBackend

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
WORKSPACE_DIR = PROJECT_ROOT / "workspace"
SKILLS_DIR = PROJECT_ROOT / "skills"


def get_env_var(key: str, default: Optional[str] = None) -> str:
    """
    Get environment variable with optional default.

    Args:
        key: Environment variable name
        default: Default value if not found

    Returns:
        Environment variable value or default
    """
    return os.getenv(key, default or "")


class ModelConfig:
    """Configuration for language model settings."""

    def __init__(self):
        # Local LLM endpoint configuration (default)
        self.use_local_endpoint = get_env_var("USE_LOCAL_ENDPOINT", "true").lower() == "true"
        self.local_endpoint = get_env_var("LOCAL_ENDPOINT", "http://192.168.1.79:8080/v1")
        self.local_model = get_env_var("LOCAL_MODEL", "glm-4.7")

        # OpenAI configuration (for cloud models)
        self.openai_api_key = get_env_var("OPENAI_API_KEY", "")
        self.openai_model = get_env_var("OPENAI_MODEL", "gpt-4o-mini")

        # Anthropic configuration (for Claude)
        self.anthropic_api_key = get_env_var("ANTHROPIC_API_KEY", "")
        self.anthropic_model = get_env_var("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

    def get_model_config(self) -> str:
        """
        Get the model configuration string for LangChain.

        Returns:
            Model provider and model name
        """
        if self.use_local_endpoint:
            # Set up local endpoint environment variables
            os.environ["OPENAI_API_BASE"] = self.local_endpoint
            os.environ["OPENAI_API_KEY"] = "not-needed"
            return f"openai:{self.local_model}"
        elif self.openai_api_key:
            os.environ["OPENAI_API_KEY"] = self.openai_api_key
            return f"openai:{self.openai_model}"
        elif self.anthropic_api_key:
            os.environ["ANTHROPIC_API_KEY"] = self.anthropic_api_key
            return f"anthropic:{self.anthropic_model}"
        else:
            raise ValueError(
                "No API key configured. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env"
            )


class MemoryConfig:
    """Configuration for memory and storage settings."""

    def __init__(self):
        # Memory store type (in-memory for development, postgres for production)
        self.store_type = get_env_var("MEMORY_STORE_TYPE", "in_memory")

        # Database configuration for persistent storage
        self.db_uri = get_env_var("DATABASE_URI", "sqlite:///ai_life_coach.db")

        # Workspace directory for context files
        self.workspace_dir = Path(get_env_var("WORKSPACE_DIR", str(WORKSPACE_DIR)))

        # Memory store instance (will be initialized in initialize_environment)
        self.store: Optional[Any] = None  # Will hold InMemoryStore or PostgresStore


class SystemConfig:
    """Overall system configuration."""

    def __init__(self):
        self.model = ModelConfig()
        self.memory = MemoryConfig()

        # System behavior settings
        self.debug_mode = get_env_var("DEBUG_MODE", "false").lower() == "true"
        self.max_subagent_depth = int(get_env_var("MAX_SUBAGENT_DEPTH", "3"))
        self.enable_human_approval = get_env_var("ENABLE_HUMAN_APPROVAL", "false").lower() == "true"

        # Backend storage (will be initialized in initialize_environment)
        self.backend = None

    def initialize_environment(self):
        """
        Set up environment variables for LangChain and Deep Agents.
        Also initializes the FilesystemBackend for workspace operations
        and InMemoryStore for long-term memory.
        """
        # Configure model endpoint
        self.model.get_model_config()

        # LangSmith for tracing (optional)
        langchain_api_key = get_env_var("LANGCHAIN_API_KEY", "")
        if langchain_api_key:
            os.environ["LANGCHAIN_API_KEY"] = langchain_api_key
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_PROJECT"] = get_env_var("LANGCHAIN_PROJECT", "ai-life-coach")

        # Create workspace directories if they don't exist
        self.memory.workspace_dir.mkdir(parents=True, exist_ok=True)
        (self.memory.workspace_dir / "user_profile").mkdir(exist_ok=True)
        (self.memory.workspace_dir / "assessments").mkdir(exist_ok=True)
        (self.memory.workspace_dir / "plans").mkdir(exist_ok=True)
        (self.memory.workspace_dir / "progress").mkdir(exist_ok=True)
        (self.memory.workspace_dir / "resources").mkdir(exist_ok=True)

        # Initialize FilesystemBackend for workspace operations
        # virtual_mode=True is required to sandbox file operations to root_dir
        self.backend = FilesystemBackend(
            root_dir=str(self.memory.workspace_dir),
            virtual_mode=True,
        )

        # Initialize InMemoryStore for long-term memory
        from langgraph.store.memory import InMemoryStore

        self.memory.store = InMemoryStore()


# Global configuration instance
config = SystemConfig()


def get_backend():
    """
    Get the initialized FilesystemBackend.

    Returns:
        FilesystemBackend: The configured backend for workspace operations

    Raises:
        RuntimeError: If environment has not been initialized
    """
    if config.backend is None:
        raise RuntimeError("Backend not initialized. Call config.initialize_environment() first.")
    return config.backend


def get_memory_store():
    """
    Get the initialized memory store.

    Returns:
        InMemoryStore: The configured store for long-term memory

    Raises:
        RuntimeError: If environment has not been initialized
    """
    if config.memory.store is None:
        raise RuntimeError(
            "Memory store not initialized. Call config.initialize_environment() first."
        )
    return config.memory.store
