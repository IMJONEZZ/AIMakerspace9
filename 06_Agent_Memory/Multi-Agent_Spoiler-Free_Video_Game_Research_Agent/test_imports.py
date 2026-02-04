#!/usr/bin/env python3
"""
Simple test of the real system components
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))


def test_imports():
    """Test all required imports."""
    print("Testing imports...")

    try:
        from game_router import GameRouterAgent

        print("✓ GameRouterAgent imported")
    except Exception as e:
        print(f"✗ GameRouterAgent failed: {e}")

    try:
        from game_specialist_agents import UnlockablesAgent, ProgressionAgent, LoreAgent

        print("✓ Specialist agents imported")
    except Exception as e:
        print(f"✗ Specialist agents failed: {e}")

    try:
        from game_input_flow import GameInputFlow

        print("✓ GameInputFlow imported")
    except Exception as e:
        print(f"✗ GameInputFlow failed: {e}")

    try:
        from user_game_progress import UserGameProgress

        print("✓ UserGameProgress imported")
    except Exception as e:
        print(f"✗ UserGameProgress failed: {e}")

    try:
        from game_knowledge_base import GameKnowledgeBase

        print("✓ GameKnowledgeBase imported")
    except Exception as e:
        print(f"✗ GameKnowledgeBase failed: {e}")

    try:
        from game_story_research_agent import GameStoryResearchAgent

        print("✓ GameStoryResearchAgent imported")
    except Exception as e:
        print(f"✗ GameStoryResearchAgent failed: {e}")


if __name__ == "__main__":
    test_imports()
