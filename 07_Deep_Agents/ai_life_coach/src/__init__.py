"""
AI Life Coach - A Deep Agent system for comprehensive life guidance.

This package provides a multi-agent coaching system with:
- Life Coach Coordinator (main orchestrator)
- Career Specialist
- Relationship Specialist
- Finance Specialist
- Wellness Specialist

Built on LangChain Deep Agents framework with:
- Advanced planning with todo lists and dependencies
- Context management via filesystem backend
- Long-term memory across sessions
- Progressive capability disclosure via skills

Author: AI Life Coach Project
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "AI Life Coach Project"

# Export main components
from src.main import create_life_coach

__all__ = ["create_life_coach", "__version__"]
