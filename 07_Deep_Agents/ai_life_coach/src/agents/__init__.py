"""
Agents for AI Life Coach.

This module provides access to the coordinator agent and four domain specialist subagents:
- Coordinator: Orchestrates all specialists, integrates cross-domain insights
- Career Specialist: Professional development and career guidance
- Relationship Specialist: Interpersonal relationships and communication
- Finance Specialist: Personal finance and financial planning
- Wellness Specialist: Holistic health and wellbeing

Example:
    >>> from src.agents import (
    ...     get_coordinator_prompt,
    ...     get_all_specialists,
    ...     get_career_specialist
    ... )
    >>>
    >>> # Get coordinator system prompt
    >>> coordinator_prompt = get_coordinator_prompt()
    >>>
    >>> # Get all specialists at once
    >>> career, rel, fin, well = get_all_specialists()
    >>>
    >>> # Or get a specific specialist
    >>> career = get_career_specialist(tools=memory_tools + context_tools)
"""

from src.agents.coordinator import get_coordinator_prompt
from src.agents.specialists import (
    get_all_specialists,
    get_career_specialist,
    get_relationship_specialist,
    get_finance_specialist,
    get_wellness_specialist,
)

__all__ = [
    "get_coordinator_prompt",
    "get_all_specialists",
    "get_career_specialist",
    "get_relationship_specialist",
    "get_finance_specialist",
    "get_wellness_specialist",
]
